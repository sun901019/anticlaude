"""
Workflow Runtime Routes
  GET  /api/workflows/runs
  GET  /api/workflows/runs/{run_id}
  GET  /api/artifacts
  GET  /api/approvals/pending
  POST /api/approvals/{approval_id}/decide
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.utils.logger import get_logger
from src.workflows.checkpoint_store import (
    list_runs, get_run, get_tasks_for_run, get_events_for_run,
    get_artifacts_for_run, list_artifacts, list_pending_approvals,
    build_ceo_package,
)
from src.workflows.approval import decide as decide_approval_gate

router = APIRouter()
log = get_logger("api.workflows")


@router.get("/api/workflows/runs")
async def get_workflow_runs(limit: int = 20, domain: str | None = None):
    """List recent workflow runs (newest first)."""
    runs = list_runs(limit=limit, domain=domain)
    return [r.model_dump() for r in runs]


@router.get("/api/workflows/runs/{run_id}")
async def get_workflow_run_detail(run_id: str):
    """Get a single run with its tasks and events."""
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    tasks = get_tasks_for_run(run_id)
    events = get_events_for_run(run_id)
    artifacts = get_artifacts_for_run(run_id)
    return {
        "run": run.model_dump(),
        "tasks": [t.model_dump() for t in tasks],
        "events": [e.model_dump() for e in events],
        "artifacts": [a.model_dump() for a in artifacts],
    }


@router.get("/api/artifacts")
async def get_artifacts(artifact_type: str | None = None, limit: int = 50):
    """List artifacts, optionally filtered by type."""
    artifacts = list_artifacts(artifact_type=artifact_type, limit=limit)
    return [a.model_dump() for a in artifacts]


@router.get("/api/approvals/pending")
async def get_pending_approvals():
    """List all approval requests waiting for CEO decision."""
    approvals = list_pending_approvals()
    return [a.model_dump() for a in approvals]


class ApprovalDecision(BaseModel):
    decision: str       # "approved" | "rejected"
    note: str | None = None


@router.get("/api/approvals/{approval_id}/package")
async def get_approval_package(approval_id: str):
    """Return standardised CEO decision package for one approval request."""
    pkg = build_ceo_package(approval_id)
    if pkg is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return pkg.model_dump()


@router.post("/api/approvals/{approval_id}/decide")
async def post_approval_decision(approval_id: str, body: ApprovalDecision):
    """CEO approves or rejects an approval request."""
    if body.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="decision must be 'approved' or 'rejected'")
    updated = decide_approval_gate(approval_id, body.decision, body.note)
    if not updated:
        raise HTTPException(status_code=404, detail="Approval not found or already decided")
    return {"approval_id": approval_id, "decision": body.decision}
