"""
Tests for Phase 7 Graph-Capable Workflow Engine.

Covers:
  - GraphNode construction
  - GraphRunner: success path, failure + retry, approval gate, resume
  - pipeline_graph: build_content_pipeline() node structure
"""
from __future__ import annotations

import asyncio
import pytest

from src.workflows.graph import GraphNode, GraphRunner, GraphResult, _extract_ctx, _summarize


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _ok_handler(ctx: dict) -> dict:
    return {"success": True, "agent": "test", "value": ctx.get("input_val", 1)}


async def _fail_handler(ctx: dict) -> dict:
    raise RuntimeError("deliberate failure")


async def _fail_soft_handler(ctx: dict) -> dict:
    return {"success": False, "error": "soft failure"}


_attempt_count: dict[str, int] = {}

async def _flaky_handler(ctx: dict) -> dict:
    """Fails on first attempt, succeeds on second."""
    key = ctx.get("run_id", "test")
    _attempt_count[key] = _attempt_count.get(key, 0) + 1
    if _attempt_count[key] < 2:
        raise RuntimeError("flaky: first attempt")
    return {"success": True, "agent": "test", "recovered": True}


# ── Unit tests ────────────────────────────────────────────────────────────────

class TestExtractCtx:
    def test_basic_extraction(self):
        out = {"success": True, "agent": "ori", "articles": [1, 2], "count": 5}
        ctx = _extract_ctx(out)
        assert "articles" in ctx
        assert "count" in ctx
        assert "success" not in ctx
        assert "agent" not in ctx

    def test_unwraps_data(self):
        out = {"success": True, "data": {"key": "val"}}
        ctx = _extract_ctx(out)
        assert ctx.get("key") == "val"
        assert "data" not in ctx

    def test_non_dict_returns_empty(self):
        assert _extract_ctx("not a dict") == {}   # type: ignore[arg-type]
        assert _extract_ctx(None) == {}           # type: ignore[arg-type]


class TestSummarize:
    def test_short_value(self):
        assert _summarize("hello") == "hello"

    def test_truncates_long_value(self):
        long = "x" * 300
        result = _summarize(long)
        assert len(result) <= 203  # 200 chars + "..."
        assert result.endswith("...")

    def test_handles_non_string(self):
        assert _summarize(42) == "42"
        assert _summarize([1, 2]) == "[1, 2]"


class TestGraphNode:
    def test_defaults(self):
        node = GraphNode(name="test", agent="ori", handler=_ok_handler)
        assert node.retry_limit == 1
        assert node.is_approval_gate is False
        assert node.depends_on == []

    def test_custom_fields(self):
        node = GraphNode(
            name="gate", agent="human", handler=_ok_handler,
            is_approval_gate=True, approval_action="publish", approval_risk="high",
        )
        assert node.is_approval_gate is True
        assert node.approval_risk == "high"


# ── GraphRunner integration tests (use real DB via conftest fixture) ───────────

class TestGraphRunnerSuccess:
    @pytest.mark.asyncio
    async def test_single_node_completes(self):
        nodes = [GraphNode(name="step1", agent="test", handler=_ok_handler)]
        runner = GraphRunner(nodes=nodes, name="test_run", domain="system")
        result = await runner.run(context={"input_val": 7})
        assert isinstance(result, GraphResult)
        assert result.ok is True
        assert result.paused_at is None
        assert result.error is None
        assert "step1" in result.outputs

    @pytest.mark.asyncio
    async def test_output_propagates_to_next_node(self):
        async def _reader(ctx: dict) -> dict:
            return {"success": True, "agent": "test", "got": ctx.get("value")}

        nodes = [
            GraphNode(name="producer", agent="test", handler=_ok_handler),
            GraphNode(name="consumer", agent="test", handler=_reader, depends_on=["producer"]),
        ]
        runner = GraphRunner(nodes=nodes, name="chain_run", domain="system")
        result = await runner.run(context={"input_val": 99})
        assert result.ok is True
        consumer_out = result.outputs.get("consumer", {})
        assert consumer_out.get("got") == 99

    @pytest.mark.asyncio
    async def test_unmet_dependency_skips_node(self):
        nodes = [
            GraphNode(name="step_a", agent="test", handler=_ok_handler),
            GraphNode(name="step_b", agent="test", handler=_ok_handler, depends_on=["missing_step"]),
        ]
        runner = GraphRunner(nodes=nodes, name="dep_run", domain="system")
        result = await runner.run()
        # step_a completes, step_b skipped (dep not met) — run still completes
        assert result.ok is True
        assert "step_a" in result.outputs
        assert "step_b" not in result.outputs


class TestGraphRunnerRetry:
    @pytest.mark.asyncio
    async def test_retry_succeeds_on_second_attempt(self):
        _attempt_count.clear()
        nodes = [GraphNode(name="flaky", agent="test", handler=_flaky_handler, retry_limit=2)]
        runner = GraphRunner(nodes=nodes, name="retry_run", domain="system")
        result = await runner.run()
        assert result.ok is True
        assert result.outputs["flaky"]["recovered"] is True

    @pytest.mark.asyncio
    async def test_exhausted_retries_fails_run(self):
        nodes = [GraphNode(name="always_fail", agent="test", handler=_fail_handler, retry_limit=2)]
        runner = GraphRunner(nodes=nodes, name="fail_run", domain="system")
        result = await runner.run()
        assert result.ok is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_soft_failure_fails_run(self):
        nodes = [GraphNode(name="soft", agent="test", handler=_fail_soft_handler)]
        runner = GraphRunner(nodes=nodes, name="soft_fail_run", domain="system")
        result = await runner.run()
        assert result.ok is False


class TestGraphRunnerApprovalGate:
    @pytest.mark.asyncio
    async def test_approval_gate_pauses_run(self, monkeypatch):
        def fake_request_approval(action, risk_level, evidence, run_id=None, task_id=None):
            return "approval-test-id"

        monkeypatch.setattr("src.workflows.approval.request_approval", fake_request_approval)
        monkeypatch.setattr("src.workflows.runner.pause_run", lambda run_id: None)

        nodes = [
            GraphNode(name="work", agent="test", handler=_ok_handler),
            GraphNode(
                name="gate", agent="human", handler=_ok_handler,
                is_approval_gate=True, approval_action="select_draft",
                depends_on=["work"],
            ),
            GraphNode(name="after_gate", agent="test", handler=_ok_handler, depends_on=["work"]),
        ]
        runner = GraphRunner(nodes=nodes, name="gate_run", domain="system")
        result = await runner.run()
        assert result.paused_at == "gate"
        # "after_gate" should not have run yet
        assert "after_gate" not in result.outputs


# ── Approval-gate bypass fix tests ───────────────────────────────────────────

class TestGraphRunnerResumeApprovalGate:
    """Verify that a resumed run does not re-trigger an already-approved gate."""

    @pytest.mark.asyncio
    async def test_resume_skips_approved_gate(self, monkeypatch):
        """After approval, resuming the run should skip the gate and complete."""
        gate_triggered_count = {"n": 0}

        def fake_request_approval(action, risk_level, evidence, run_id=None, task_id=None):
            gate_triggered_count["n"] += 1
            return f"approval-{gate_triggered_count['n']}"

        monkeypatch.setattr("src.workflows.approval.request_approval", fake_request_approval)
        monkeypatch.setattr("src.workflows.runner.pause_run", lambda run_id: None)
        monkeypatch.setattr("src.workflows.runner.resume_run", lambda run_id: None)

        # Patch list_approvals_for_run to return an approved approval for "select_draft"
        from src.workflows.models import ApprovalRequest
        from datetime import datetime, timezone

        def fake_list_approvals(run_id):
            return [
                ApprovalRequest(
                    id="app-1", run_id=run_id, task_id=None,
                    action="select_draft", risk_level="medium",
                    status="approved", decided_at=datetime.now(timezone.utc),
                )
            ]

        monkeypatch.setattr("src.workflows.graph.list_approvals_for_run", fake_list_approvals)

        # Patch get_run to return a valid run object
        from src.workflows.models import WorkflowRun
        monkeypatch.setattr(
            "src.workflows.graph.get_run",
            lambda run_id: WorkflowRun(id=run_id, name="test", status="paused"),
        )
        # Patch get_tasks_for_run to return one completed task (work node)
        from src.workflows.models import WorkflowTask
        monkeypatch.setattr(
            "src.workflows.graph.get_tasks_for_run",
            lambda run_id: [
                WorkflowTask(
                    id="t1", run_id=run_id, agent="test",
                    task_type="work", status="completed",
                    output={"success": True, "value": 1},
                )
            ],
        )

        # Mock all DB-writing functions so the fake run_id doesn't hit FK constraints
        fake_task = WorkflowTask(id="t-new", run_id="fake-run-id", agent="test",
                                 task_type="after_gate", status="running")
        monkeypatch.setattr("src.workflows.graph.start_task", lambda *a, **kw: fake_task)
        monkeypatch.setattr("src.workflows.graph.complete_task", lambda *a, **kw: None)
        monkeypatch.setattr("src.workflows.graph.complete_run", lambda run_id: None)
        monkeypatch.setattr("src.workflows.graph.fail_run", lambda *a: None)

        nodes = [
            GraphNode(name="work", agent="test", handler=_ok_handler),
            GraphNode(
                name="gate", agent="human", handler=_ok_handler,
                is_approval_gate=True, approval_action="select_draft",
                depends_on=["work"],
            ),
            GraphNode(name="after_gate", agent="test", handler=_ok_handler, depends_on=["work"]),
        ]
        runner = GraphRunner(nodes=nodes, name="resume_run", domain="system")
        result = await runner.run(resume_run_id="fake-run-id")

        # Gate should NOT have been triggered again
        assert gate_triggered_count["n"] == 0, "Gate was re-triggered on resume — bypass bug!"
        # after_gate should have executed
        assert "after_gate" in result.outputs
        assert result.paused_at is None
        assert result.ok is True


# ── Pipeline graph structure tests ────────────────────────────────────────────

class TestPipelineGraphStructure:
    def test_standard_pipeline_has_approval_gate(self):
        from src.workflows.pipeline_graph import build_content_pipeline
        runner = build_content_pipeline(with_approval_gate=True)
        node_names = [n.name for n in runner.nodes]
        assert "draft_approval" in node_names
        assert "save_outputs" in node_names

    def test_pipeline_without_gate(self):
        from src.workflows.pipeline_graph import build_content_pipeline
        runner = build_content_pipeline(with_approval_gate=False)
        node_names = [n.name for n in runner.nodes]
        assert "draft_approval" not in node_names

    def test_deliberation_adds_score_review_gate(self):
        from src.workflows.pipeline_graph import build_content_pipeline
        runner = build_content_pipeline(with_approval_gate=True, deliberation=True)
        node_names = [n.name for n in runner.nodes]
        assert "score_review" in node_names
        gate = next(n for n in runner.nodes if n.name == "score_review")
        assert gate.is_approval_gate is True
        assert gate.approval_risk == "low"

    def test_all_nodes_have_required_fields(self):
        from src.workflows.pipeline_graph import build_content_pipeline
        runner = build_content_pipeline()
        for node in runner.nodes:
            assert node.name, f"Node missing name: {node}"
            assert node.agent, f"Node '{node.name}' missing agent"
            assert callable(node.handler), f"Node '{node.name}' handler not callable"

    def test_save_outputs_depends_on_approval_gate(self):
        from src.workflows.pipeline_graph import build_content_pipeline
        runner_with = build_content_pipeline(with_approval_gate=True)
        save = next(n for n in runner_with.nodes if n.name == "save_outputs")
        assert "draft_approval" in save.depends_on, \
            "save_outputs must wait for draft_approval when gate is enabled"

        runner_without = build_content_pipeline(with_approval_gate=False)
        save_no_gate = next(n for n in runner_without.nodes if n.name == "save_outputs")
        assert "draft_approval" not in save_no_gate.depends_on

    def test_runner_name_and_domain(self):
        from src.workflows.pipeline_graph import build_content_pipeline
        runner = build_content_pipeline()
        assert runner.name == "daily_content_pipeline"
        assert runner.domain == "media"
