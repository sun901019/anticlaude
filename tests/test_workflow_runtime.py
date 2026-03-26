"""
Tests for AITOS Workflow Runtime (Phase 2)
==========================================
Covers: models, checkpoint_store, runner, events, approval
"""
import pytest
from datetime import datetime

from src.workflows.models import (
    WorkflowRun, WorkflowTask, WorkflowEvent, Artifact, ApprovalRequest,
)
from src.workflows.runner import (
    create_run, start_task, complete_task, fail_task,
    complete_run, fail_run, record_artifact,
)
from src.workflows.approval import request_approval, check_approval, decide
from src.workflows.checkpoint_store import (
    get_run, get_tasks_for_run, get_events_for_run,
    get_artifacts_for_run, list_runs, list_pending_approvals,
)


# ── Model unit tests ───────────────────────────────────────────────────────────

def test_workflow_run_defaults():
    run = WorkflowRun(name="test_run", domain="media")
    assert run.status == "running" or run.status == "pending"
    assert run.id
    assert run.context == {}
    assert run.is_terminal() is False


def test_workflow_task_defaults():
    task = WorkflowTask(run_id="abc", agent="ori", task_type="content_research")
    assert task.status == "pending"
    assert task.id
    assert task.is_terminal() is False


def test_artifact_defaults():
    art = Artifact(producer="ori", artifact_type="analysis")
    assert art.id
    assert art.metadata == {}
    assert isinstance(art.created_at, datetime)


def test_approval_defaults():
    ap = ApprovalRequest(action="publish_post")
    assert ap.status == "pending"
    assert ap.id


# ── Integration tests (require DB) ────────────────────────────────────────────

def test_create_and_retrieve_run():
    run = create_run("test_pipeline", domain="media", context={"date": "2026-03-19"})
    assert run.id
    assert run.status == "running"

    fetched = get_run(run.id)
    assert fetched is not None
    assert fetched.name == "test_pipeline"
    assert fetched.context["date"] == "2026-03-19"


def test_task_lifecycle():
    run = create_run("task_lifecycle_test", domain="flowlab")
    task = start_task(run.id, agent="sage", task_type="product_evaluation",
                      input={"candidate_id": "cand-001"})
    assert task.status == "running"

    complete_task(task.id, output={"score": 8.5, "viability": "strong"})

    tasks = get_tasks_for_run(run.id)
    assert len(tasks) == 1
    assert tasks[0].status == "completed"
    assert tasks[0].output["score"] == 8.5


def test_task_failure():
    run = create_run("fail_test", domain="media")
    task = start_task(run.id, agent="ori", task_type="content_research")
    fail_task(task.id, error="API timeout")

    tasks = get_tasks_for_run(run.id)
    assert tasks[0].status == "failed"
    assert tasks[0].error == "API timeout"


def test_events_emitted():
    run = create_run("event_test", domain="media")
    task = start_task(run.id, agent="craft", task_type="draft_generation")
    complete_task(task.id, output={"drafts": 2})
    complete_run(run.id)

    events = get_events_for_run(run.id)
    event_types = [e.event_type for e in events]
    assert "run_started" in event_types
    assert "task_started" in event_types
    assert "task_completed" in event_types
    assert "run_completed" in event_types


def test_artifact_recording():
    run = create_run("artifact_test", domain="flowlab")
    task = start_task(run.id, agent="craft", task_type="draft_generation")

    art = record_artifact(
        producer="craft",
        artifact_type="draft",
        run_id=run.id,
        task_id=task.id,
        file_path="outputs/drafts/2026-03-19.md",
        metadata={"drafts_count": 3},
    )
    assert art.id

    artifacts = get_artifacts_for_run(run.id)
    assert len(artifacts) == 1
    assert artifacts[0].artifact_type == "draft"
    assert artifacts[0].metadata["drafts_count"] == 3


def test_approval_workflow():
    run = create_run("approval_test", domain="media")
    task = start_task(run.id, agent="craft", task_type="draft_generation")

    approval_id = request_approval(
        action="publish_post",
        evidence={"draft_id": 42, "preview": "Hello Threads!"},
        risk_level="low",
        run_id=run.id,
        task_id=task.id,
    )

    assert check_approval(approval_id) == "pending"
    pending = list_pending_approvals()
    assert any(a.id == approval_id for a in pending)

    updated = decide(approval_id, "approved", note="Content looks good")
    assert updated is True
    assert check_approval(approval_id) == "approved"

    # Should no longer be in pending list
    pending_after = list_pending_approvals()
    assert all(a.id != approval_id for a in pending_after)


def test_approval_rejection():
    run = create_run("rejection_test", domain="media")
    approval_id = request_approval(
        action="publish_post",
        evidence={"preview": "Controversial content"},
        risk_level="high",
        run_id=run.id,
    )
    decide(approval_id, "rejected", note="Too risky")
    assert check_approval(approval_id) == "rejected"


def test_list_runs_filter_by_domain():
    run_media = create_run("media_run", domain="media")
    run_fl = create_run("flowlab_run", domain="flowlab")

    media_runs = list_runs(limit=10, domain="media")
    fl_runs = list_runs(limit=10, domain="flowlab")

    assert any(r.id == run_media.id for r in media_runs)
    assert any(r.id == run_fl.id for r in fl_runs)
    assert not any(r.id == run_fl.id for r in media_runs)
