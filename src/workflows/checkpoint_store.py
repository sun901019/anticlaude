"""
Workflow Checkpoint Store
==========================
SQLite persistence for all five workflow primitives.
All JSON encoding/decoding happens here — callers always work with model objects.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from src.db.connection import db
from src.workflows.models import (
    WorkflowRun, WorkflowTask, WorkflowEvent, Artifact, ApprovalRequest,
    CeoDecisionPackage,
)
from src.workflows.approval_matrix import is_irreversible as _action_is_irreversible
from src.utils.logger import get_logger

log = get_logger("workflows.store")

_DT_FMT = "%Y-%m-%dT%H:%M:%S.%f"


def _dt(val: Any) -> datetime | None:
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    try:
        return datetime.strptime(val, _DT_FMT)
    except ValueError:
        return datetime.fromisoformat(str(val))


def _j(val: Any) -> str | None:
    return json.dumps(val, ensure_ascii=False) if val is not None else None


def _pj(val: str | None) -> dict | None:
    return json.loads(val) if val else {}


# ── WorkflowRun ───────────────────────────────────────────────────────────────

def save_run(run: WorkflowRun) -> None:
    with db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO workflow_runs
               (id, name, domain, status, context_json, started_at, completed_at, error)
               VALUES (?,?,?,?,?,?,?,?)""",
            (run.id, run.name, run.domain, run.status,
             _j(run.context),
             run.started_at.strftime(_DT_FMT),
             run.completed_at.strftime(_DT_FMT) if run.completed_at else None,
             run.error),
        )


def get_run(run_id: str) -> WorkflowRun | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM workflow_runs WHERE id=?", (run_id,)
        ).fetchone()
    if not row:
        return None
    return WorkflowRun(
        id=row["id"], name=row["name"], domain=row["domain"],
        status=row["status"],
        context=_pj(row["context_json"]),
        started_at=_dt(row["started_at"]),
        completed_at=_dt(row["completed_at"]),
        error=row["error"],
    )


def list_runs(limit: int = 20, domain: str | None = None) -> list[WorkflowRun]:
    with db() as conn:
        if domain:
            rows = conn.execute(
                "SELECT * FROM workflow_runs WHERE domain=? ORDER BY started_at DESC LIMIT ?",
                (domain, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM workflow_runs ORDER BY started_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [
        WorkflowRun(
            id=r["id"], name=r["name"], domain=r["domain"], status=r["status"],
            context=_pj(r["context_json"]),
            started_at=_dt(r["started_at"]), completed_at=_dt(r["completed_at"]),
            error=r["error"],
        )
        for r in rows
    ]


def update_run_status(run_id: str, status: str, error: str | None = None) -> None:
    completed_at = datetime.now(timezone.utc).strftime(_DT_FMT) if status in ("completed", "failed") else None
    with db() as conn:
        conn.execute(
            "UPDATE workflow_runs SET status=?, completed_at=?, error=? WHERE id=?",
            (status, completed_at, error, run_id),
        )


# ── WorkflowTask ──────────────────────────────────────────────────────────────

def save_task(task: WorkflowTask) -> None:
    with db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO workflow_tasks
               (id, run_id, agent, task_type, status,
                input_json, output_json, error, started_at, completed_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (task.id, task.run_id, task.agent, task.task_type, task.status,
             _j(task.input), _j(task.output), task.error,
             task.started_at.strftime(_DT_FMT),
             task.completed_at.strftime(_DT_FMT) if task.completed_at else None),
        )


def get_tasks_for_run(run_id: str) -> list[WorkflowTask]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM workflow_tasks WHERE run_id=? ORDER BY started_at", (run_id,)
        ).fetchall()
    return [
        WorkflowTask(
            id=r["id"], run_id=r["run_id"], agent=r["agent"],
            task_type=r["task_type"], status=r["status"],
            input=_pj(r["input_json"]), output=_pj(r["output_json"]),
            error=r["error"],
            started_at=_dt(r["started_at"]), completed_at=_dt(r["completed_at"]),
        )
        for r in rows
    ]


def update_task_status(
    task_id: str, status: str,
    output: dict | None = None, error: str | None = None,
) -> None:
    completed_at = datetime.now(timezone.utc).strftime(_DT_FMT) if status in ("completed", "failed", "skipped") else None
    with db() as conn:
        conn.execute(
            """UPDATE workflow_tasks
               SET status=?, output_json=?, error=?, completed_at=?
               WHERE id=?""",
            (status, _j(output), error, completed_at, task_id),
        )


# ── WorkflowEvent ─────────────────────────────────────────────────────────────

def emit_event(event: WorkflowEvent) -> None:
    with db() as conn:
        conn.execute(
            """INSERT INTO workflow_events
               (id, run_id, task_id, event_type, payload_json, timestamp)
               VALUES (?,?,?,?,?,?)""",
            (event.id, event.run_id, event.task_id, event.event_type,
             _j(event.payload), event.timestamp.strftime(_DT_FMT)),
        )


def get_events_for_run(run_id: str) -> list[WorkflowEvent]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM workflow_events WHERE run_id=? ORDER BY timestamp", (run_id,)
        ).fetchall()
    return [
        WorkflowEvent(
            id=r["id"], run_id=r["run_id"], task_id=r["task_id"],
            event_type=r["event_type"], payload=_pj(r["payload_json"]),
            timestamp=_dt(r["timestamp"]),
        )
        for r in rows
    ]


# ── Artifact ──────────────────────────────────────────────────────────────────

def save_artifact(artifact: Artifact) -> None:
    with db() as conn:
        conn.execute(
            """INSERT OR REPLACE INTO artifacts
               (id, run_id, task_id, artifact_type, producer,
                file_path, db_ref, metadata_json, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (artifact.id, artifact.run_id, artifact.task_id,
             artifact.artifact_type, artifact.producer,
             artifact.file_path, artifact.db_ref,
             _j(artifact.metadata),
             artifact.created_at.strftime(_DT_FMT)),
        )


def get_artifacts_for_run(run_id: str) -> list[Artifact]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM artifacts WHERE run_id=? ORDER BY created_at", (run_id,)
        ).fetchall()
    return [
        Artifact(
            id=r["id"], run_id=r["run_id"], task_id=r["task_id"],
            artifact_type=r["artifact_type"], producer=r["producer"],
            file_path=r["file_path"], db_ref=r["db_ref"],
            metadata=_pj(r["metadata_json"]),
            created_at=_dt(r["created_at"]),
        )
        for r in rows
    ]


def list_artifacts(artifact_type: str | None = None, limit: int = 50) -> list[Artifact]:
    with db() as conn:
        if artifact_type:
            rows = conn.execute(
                "SELECT * FROM artifacts WHERE artifact_type=? ORDER BY created_at DESC LIMIT ?",
                (artifact_type, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM artifacts ORDER BY created_at DESC LIMIT ?", (limit,)
            ).fetchall()
    return [
        Artifact(
            id=r["id"], run_id=r["run_id"], task_id=r["task_id"],
            artifact_type=r["artifact_type"], producer=r["producer"],
            file_path=r["file_path"], db_ref=r["db_ref"],
            metadata=_pj(r["metadata_json"]),
            created_at=_dt(r["created_at"]),
        )
        for r in rows
    ]


# ── ApprovalRequest ───────────────────────────────────────────────────────────

def create_approval(approval: ApprovalRequest) -> None:
    with db() as conn:
        conn.execute(
            """INSERT INTO approval_requests
               (id, run_id, task_id, action, risk_level,
                evidence_json, status, decided_at, decision_note)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (approval.id, approval.run_id, approval.task_id,
             approval.action, approval.risk_level,
             _j(approval.evidence), approval.status,
             approval.decided_at.strftime(_DT_FMT) if approval.decided_at else None,
             approval.decision_note),
        )


def get_approval(approval_id: str) -> ApprovalRequest | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM approval_requests WHERE id=?", (approval_id,)
        ).fetchone()
    if not row:
        return None
    return ApprovalRequest(
        id=row["id"], run_id=row["run_id"], task_id=row["task_id"],
        action=row["action"], risk_level=row["risk_level"],
        evidence=_pj(row["evidence_json"]), status=row["status"],
        decided_at=_dt(row["decided_at"]), decision_note=row["decision_note"],
    )


def list_approvals_for_run(run_id: str) -> list[ApprovalRequest]:
    """Return all approval requests for a given run (any status)."""
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM approval_requests WHERE run_id=? ORDER BY rowid",
            (run_id,),
        ).fetchall()
    return [
        ApprovalRequest(
            id=r["id"], run_id=r["run_id"], task_id=r["task_id"],
            action=r["action"], risk_level=r["risk_level"],
            evidence=_pj(r["evidence_json"]), status=r["status"],
            decided_at=_dt(r["decided_at"]), decision_note=r["decision_note"],
        )
        for r in rows
    ]


def list_pending_approvals() -> list[ApprovalRequest]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM approval_requests WHERE status='pending' ORDER BY rowid DESC"
        ).fetchall()
    return [
        ApprovalRequest(
            id=r["id"], run_id=r["run_id"], task_id=r["task_id"],
            action=r["action"], risk_level=r["risk_level"],
            evidence=_pj(r["evidence_json"]), status=r["status"],
            decided_at=_dt(r["decided_at"]), decision_note=r["decision_note"],
        )
        for r in rows
    ]


def decide_approval(approval_id: str, decision: str, note: str | None = None) -> bool:
    """decision: 'approved' | 'rejected'. Returns True if found and updated."""
    decided_at = datetime.now(timezone.utc).strftime(_DT_FMT)
    with db() as conn:
        cur = conn.execute(
            """UPDATE approval_requests
               SET status=?, decided_at=?, decision_note=?
               WHERE id=? AND status='pending'""",
            (decision, decided_at, note, approval_id),
        )
    return cur.rowcount > 0


# ── CEO Decision Package ───────────────────────────────────────────────────────

_ACTION_SUMMARIES: dict[str, str] = {
    "select_draft":           "請審核 AI 草稿，選擇是否核准發布",
    "publish_post":           "請審核貼文，確認是否發布至 Threads",
    "promote_product":        "請審核商品推廣建議，確認是否執行",
    "review_scored_topics":   "請審核 AI 評分結果，確認選題方向",
    "approve_screenshot":     "請審核截圖分析結果，確認是否產出草稿",
    "approve_video_analysis": "請審核上傳影片，確認是否進行 AI 分析與草稿產出",
}

_RISK_LABELS: dict[str, str] = {
    "low":    "低風險",
    "medium": "中風險",
    "high":   "高風險",
}

# Reversibility is derived from approval_matrix — single source of truth


def build_ceo_package(approval_id: str) -> CeoDecisionPackage | None:
    """Build a standardised CEO decision package from an approval_request + its run artifacts.

    Returns None if the approval_request is not found.
    """
    approval = get_approval(approval_id)
    if approval is None:
        return None

    # Collect artifact IDs for the same run (if any)
    artifact_links: list[str] = []
    if approval.run_id:
        artifacts = get_artifacts_for_run(approval.run_id)
        artifact_links = [a.id for a in artifacts]

    summary = _ACTION_SUMMARIES.get(
        approval.action,
        f"請審核動作：{approval.action}（{_RISK_LABELS.get(approval.risk_level, approval.risk_level)}）",
    )

    return CeoDecisionPackage(
        approval_id=approval.id,
        run_id=approval.run_id,
        action=approval.action,
        risk_level=approval.risk_level,
        status=approval.status,
        summary=summary,
        evidence=approval.evidence,
        artifact_links=artifact_links,
        reversible=not _action_is_irreversible(approval.action),
    )
