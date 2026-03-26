"""
Workflow Runner
================
Create and manage workflow runs and their tasks.

This is the primary interface for any agent or API endpoint that wants to
track work as a structured workflow. It does NOT execute agent logic —
it only manages state transitions and events.

Usage:
    from src.workflows.runner import create_run, start_task, complete_task, fail_task

    run = create_run("daily_content_pipeline", domain="media", context={"date": "2026-03-19"})
    task = start_task(run.id, agent="ori", task_type="content_research")
    complete_task(task.id, output={"articles_count": 12})
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.workflows.models import WorkflowRun, WorkflowTask, Artifact, Domain
from src.workflows.checkpoint_store import (
    save_run, get_run, update_run_status,
    save_task, update_task_status,
    save_artifact,
)
from src.workflows.events import emit
from src.utils.logger import get_logger

log = get_logger("workflows.runner")


# ── Run lifecycle ──────────────────────────────────────────────────────────────

def create_run(
    name: str,
    domain: Domain = "media",
    context: dict[str, Any] | None = None,
) -> WorkflowRun:
    """Create and persist a new workflow run (status=running)."""
    run = WorkflowRun(name=name, domain=domain, status="running", context=context or {})
    save_run(run)
    emit("run_started", run_id=run.id, payload={"name": name, "domain": domain})
    log.info(f"Run started: {run.id} | {name}")
    return run


def complete_run(run_id: str) -> None:
    update_run_status(run_id, "completed")
    emit("run_completed", run_id=run_id)
    log.info(f"Run completed: {run_id}")


def fail_run(run_id: str, error: str) -> None:
    update_run_status(run_id, "failed", error=error)
    emit("run_failed", run_id=run_id, payload={"error": error})
    log.error(f"Run failed: {run_id} | {error}")


def pause_run(run_id: str) -> None:
    update_run_status(run_id, "paused")
    emit("run_paused", run_id=run_id)


def resume_run(run_id: str) -> None:
    update_run_status(run_id, "running")
    emit("run_resumed", run_id=run_id)


# ── Task lifecycle ─────────────────────────────────────────────────────────────

def start_task(
    run_id: str,
    agent: str,
    task_type: str,
    input: dict[str, Any] | None = None,
) -> WorkflowTask:
    """Create and persist a task in running state."""
    task = WorkflowTask(
        run_id=run_id, agent=agent, task_type=task_type,
        status="running", input=input or {},
    )
    save_task(task)
    emit("task_started", run_id=run_id, task_id=task.id,
         payload={"agent": agent, "task_type": task_type})
    log.info(f"Task started: {task.id} | {agent}/{task_type}")
    return task


def complete_task(task_id: str, output: dict[str, Any] | None = None) -> None:
    update_task_status(task_id, "completed", output=output)
    # We need run_id for the event — fetch task
    from src.workflows.checkpoint_store import get_tasks_for_run
    emit("task_completed", run_id=_get_run_id(task_id),
         task_id=task_id, payload={"output_keys": list((output or {}).keys())})
    log.info(f"Task completed: {task_id}")


def fail_task(task_id: str, error: str) -> None:
    update_task_status(task_id, "failed", error=error)
    emit("task_failed", run_id=_get_run_id(task_id),
         task_id=task_id, payload={"error": error})
    log.error(f"Task failed: {task_id} | {error}")


def await_approval(task_id: str) -> None:
    """Transition task to awaiting_approval state (runner pauses here)."""
    update_task_status(task_id, "awaiting_approval")
    log.info(f"Task awaiting approval: {task_id}")


# ── Artifact helpers ───────────────────────────────────────────────────────────

def record_artifact(
    producer: str,
    artifact_type: str,
    run_id: str | None = None,
    task_id: str | None = None,
    file_path: str | None = None,
    db_ref: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Artifact:
    """Save an artifact and emit an artifact_saved event."""
    artifact = Artifact(
        run_id=run_id, task_id=task_id,
        artifact_type=artifact_type,
        producer=producer,
        file_path=file_path, db_ref=db_ref,
        metadata=metadata or {},
        created_at=datetime.now(timezone.utc),
    )
    save_artifact(artifact)
    if run_id:
        emit("artifact_saved", run_id=run_id, task_id=task_id,
             payload={"artifact_id": artifact.id, "type": artifact_type, "producer": producer})
    log.info(f"Artifact saved: {artifact.id} | {artifact_type} by {producer}")
    return artifact


# ── Internal helpers ───────────────────────────────────────────────────────────

def _get_run_id(task_id: str) -> str:
    """Look up run_id from DB. Returns 'unknown' if not found."""
    from src.db.connection import db as _db
    try:
        with _db() as conn:
            row = conn.execute(
                "SELECT run_id FROM workflow_tasks WHERE id=?", (task_id,)
            ).fetchone()
        return row["run_id"] if row else "unknown"
    except Exception:
        return "unknown"
