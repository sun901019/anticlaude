"""
Graph-Capable Workflow Engine — Phase 7
========================================
Pure Python state machine for checkpoint/resume, retryable nodes, approval gates.

Design principles:
  - No external frameworks (no LangGraph, no Celery) — pure Python
  - GraphNode: dataclass with name, agent, handler, retry_limit, optional approval gate
  - GraphRunner: creates WorkflowRun + WorkflowTask DB records at every step
  - Approval gate: creates approval_request, pauses run, returns immediately
  - Resume: call run(resume_run_id=...) to skip completed nodes and continue

Retry behaviour:
  - retry_limit=1 → single attempt (default)
  - retry_limit=2 → up to 2 attempts with 1-second pause between
  - retry_limit=3 → attempts with exponential back-off: 1s, 2s
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from src.workflows.models import Domain
from src.workflows.runner import (
    create_run, complete_run, fail_run, pause_run, resume_run,
    start_task, complete_task, fail_task,
)
from src.workflows.checkpoint_store import get_run, get_tasks_for_run, list_approvals_for_run
from src.utils.logger import get_logger

log = get_logger("workflows.graph")

NodeHandler = Callable[[dict[str, Any]], Coroutine[Any, Any, dict[str, Any]]]


@dataclass
class GraphNode:
    """A single step in a graph workflow."""
    name: str                                            # unique name; used as task_type in DB
    agent: str                                           # which agent executes this
    handler: NodeHandler                                 # async fn(ctx) -> dict
    retry_limit: int = 1                                 # total attempts (1 = no retry on fail)
    is_approval_gate: bool = False                       # pause run + request human approval
    approval_action: str = ""                            # action name for approval_requests table
    approval_risk: str = "medium"                        # "low" | "medium" | "high"
    depends_on: list[str] = field(default_factory=list)  # node names that must complete first


@dataclass
class GraphResult:
    ok: bool
    run_id: str
    outputs: dict[str, Any]        # node_name → handler return value
    error: str | None = None
    paused_at: str | None = None   # node name if run was paused for approval


class GraphRunner:
    """
    Execute a list of GraphNodes as a structured workflow with full DB tracking.

    Execution flow:
    1. Create (or resume) a WorkflowRun in the DB
    2. Iterate nodes in list order
    3. For each node:
       - Skip if already completed (resume path)
       - Skip if depends_on not met
       - If approval_gate: request_approval → pause_run → return with paused_at
       - Otherwise: start_task → handler(ctx) with retries → complete_task or fail_task
    4. complete_run when all nodes pass; fail_run on fatal node failure

    Resume:
        call run(resume_run_id=...) → fetches completed tasks from DB → skips them
        Outputs and context are restored from completed task output_json.
    """

    def __init__(self, nodes: list[GraphNode], name: str, domain: Domain = "media") -> None:
        self.nodes = nodes
        self.name = name
        self.domain = domain

    async def run(
        self,
        context: dict[str, Any] | None = None,
        resume_run_id: str | None = None,
    ) -> GraphResult:
        ctx = dict(context or {})
        outputs: dict[str, Any] = {}
        completed_nodes: set[str] = set()

        # ── Create or resume WorkflowRun ──────────────────────────────────────
        if resume_run_id:
            existing = get_run(resume_run_id)
            if existing is None:
                return GraphResult(
                    ok=False, run_id=resume_run_id, outputs={},
                    error=f"Run '{resume_run_id}' not found",
                )
            resume_run(resume_run_id)
            run_id = resume_run_id
            # Restore completed-node outputs so downstream ctx is populated
            for t in get_tasks_for_run(run_id):
                if t.status == "completed":
                    completed_nodes.add(t.task_type)
                    if t.output:
                        outputs[t.task_type] = t.output
                        ctx.update(_extract_ctx(t.output))

            # Enforce approval gates on resume.
            # - rejected approval → hard fail (CEO said no; cannot bypass by calling resume again)
            # - approved approval → skip the gate node (already granted)
            # - no decision yet → gate will re-trigger and pause again (normal flow)
            all_approvals = list_approvals_for_run(run_id)
            rejected_actions = {a.action for a in all_approvals if a.status == "rejected"}
            approved_actions = {a.action for a in all_approvals if a.status == "approved"}

            if rejected_actions:
                fail_run(run_id, f"Approval rejected for: {rejected_actions}")
                return GraphResult(
                    ok=False, run_id=run_id, outputs=outputs,
                    error=f"Cannot resume: approval rejected for {rejected_actions}",
                )

            for node in self.nodes:
                if node.is_approval_gate and (node.approval_action or node.name) in approved_actions:
                    completed_nodes.add(node.name)
                    log.info(f"[Graph] Gate '{node.name}' already approved — skipping on resume")

            log.info(f"[Graph] Resuming {run_id} | skipping={completed_nodes}")
        else:
            run_obj = create_run(self.name, domain=self.domain, context=ctx)
            run_id = run_obj.id
            log.info(f"[Graph] New run {run_id} | {self.name}")

        ctx["run_id"] = run_id

        # ── Execute nodes ─────────────────────────────────────────────────────
        for node in self.nodes:
            # Skip nodes already completed (resume path)
            if node.name in completed_nodes:
                log.info(f"[Graph] '{node.name}' already completed — skipping")
                continue

            # Check dependencies
            if node.depends_on:
                missing = [d for d in node.depends_on if d not in completed_nodes]
                if missing:
                    log.warning(f"[Graph] '{node.name}' skipped — unmet deps: {missing}")
                    continue

            # ── Approval gate ─────────────────────────────────────────────────
            if node.is_approval_gate:
                log.info(f"[Graph] Approval gate reached: '{node.name}'")
                try:
                    from src.workflows.approval import request_approval
                    evidence: dict[str, Any] = {
                        "node": node.name,
                        "action": node.approval_action or node.name,
                        "outputs_summary": {k: _summarize(v) for k, v in outputs.items()},
                    }
                    # For publish_post gates: include first draft content so the
                    # review approval trigger can extract text for X/Threads publishing.
                    if node.approval_action == "publish_post":
                        drafts = ctx.get("drafts", [])
                        if drafts and isinstance(drafts, list):
                            first = drafts[0]
                            # drafts[i] = {"label": str, "v1": {"content": str}, "v2": ...}
                            v1 = first.get("v1") or first.get("v2") or {}
                            preview = v1.get("content", "") if isinstance(v1, dict) else ""
                            if not preview:
                                # fallback: any string value in the draft dict
                                for val in first.values():
                                    if isinstance(val, str) and len(val) > 20:
                                        preview = val
                                        break
                            evidence["content_preview"] = preview[:500]
                    approval_id = request_approval(
                        action=node.approval_action or node.name,
                        risk_level=node.approval_risk,  # type: ignore[arg-type]
                        evidence=evidence,
                        run_id=run_id,
                    )
                    pause_run(run_id)
                    try:
                        from src.api.agent_status import mark_agent_awaiting_human
                        mark_agent_awaiting_human(
                            "craft",
                            message=f"等待審核（approval_id={approval_id}）",
                            action_type=node.approval_action or node.name,
                            ref_id=approval_id,
                        )
                    except Exception:
                        pass
                    return GraphResult(
                        ok=True, run_id=run_id, outputs=outputs, paused_at=node.name,
                    )
                except Exception as e:
                    log.error(f"[Graph] Approval gate '{node.name}' error: {e}")
                    fail_run(run_id, str(e))
                    return GraphResult(ok=False, run_id=run_id, outputs=outputs, error=str(e))

            # ── Normal node with retry ────────────────────────────────────────
            node_output: dict[str, Any] | None = None
            last_error = ""

            for attempt in range(max(1, node.retry_limit)):
                task = start_task(
                    run_id, agent=node.agent, task_type=node.name,
                    input={k: v for k, v in ctx.items()
                           if not k.startswith("_") and k not in ("run_id", "task_id")},
                )
                ctx["task_id"] = task.id
                try:
                    node_output = await node.handler(ctx)
                    if isinstance(node_output, dict) and node_output.get("success") is False:
                        raise RuntimeError(node_output.get("error", "handler returned success=False"))
                    complete_task(task.id, output=node_output)
                    log.info(f"[Graph] '{node.name}' OK (attempt {attempt + 1}/{node.retry_limit})")
                    break
                except Exception as e:
                    last_error = str(e)
                    log.warning(f"[Graph] '{node.name}' attempt {attempt + 1} failed: {e}")
                    if attempt + 1 < node.retry_limit:
                        await asyncio.sleep(2 ** attempt)   # back-off: 1s, 2s, 4s…
                    else:
                        fail_task(task.id, last_error)

            if node_output is None or (
                isinstance(node_output, dict) and node_output.get("success") is False
            ):
                fail_run(
                    run_id,
                    f"Node '{node.name}' failed after {node.retry_limit} attempt(s): {last_error}",
                )
                return GraphResult(ok=False, run_id=run_id, outputs=outputs, error=last_error)

            # Propagate into context for downstream nodes
            outputs[node.name] = node_output
            completed_nodes.add(node.name)
            ctx.update(_extract_ctx(node_output))

        complete_run(run_id)
        return GraphResult(ok=True, run_id=run_id, outputs=outputs)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _extract_ctx(output: dict[str, Any]) -> dict[str, Any]:
    """Flatten handler output into shared context for downstream nodes."""
    if not isinstance(output, dict):
        return {}
    skip = {"success", "agent", "task_type", "error"}
    flat = {k: v for k, v in output.items() if k not in skip}
    # If handler wraps result in a "data" sub-dict, merge that too
    if "data" in flat and isinstance(flat["data"], dict):
        flat.update(flat.pop("data"))
    return flat


def _summarize(value: Any, max_len: int = 200) -> str:
    try:
        s = str(value)
        return s[:max_len] + "..." if len(s) > max_len else s
    except Exception:
        return "<unserializable>"
