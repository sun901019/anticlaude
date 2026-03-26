"""
Workflow Event Emitter
=======================
Thin wrapper: emit typed events to the workflow_events table.

Usage:
    from src.workflows.events import emit
    emit("task_completed", run_id=run.id, task_id=task.id, payload={"result": "ok"})
"""
from __future__ import annotations

from typing import Any

from src.workflows.models import WorkflowEvent, EventType
from src.workflows.checkpoint_store import emit_event
from src.utils.logger import get_logger

log = get_logger("workflows.events")


def emit(
    event_type: EventType,
    run_id: str,
    task_id: str | None = None,
    payload: dict[str, Any] | None = None,
) -> WorkflowEvent:
    """Create and persist a workflow event."""
    event = WorkflowEvent(
        run_id=run_id,
        task_id=task_id,
        event_type=event_type,
        payload=payload or {},
    )
    try:
        emit_event(event)
    except Exception as exc:
        log.warning(f"Event emit failed ({event_type}): {exc}")
    return event
