"""
Workflow Primitives — Pydantic Models
======================================
run / task / event / artifact / approval

These are the five core state types of AITOS workflow runtime.
All DB read/write goes through checkpoint_store.py using these models.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ── Status literals ────────────────────────────────────────────────────────────

RunStatus = Literal["pending", "running", "paused", "completed", "failed"]
TaskStatus = Literal["pending", "running", "completed", "failed", "awaiting_approval", "skipped"]
ApprovalStatus = Literal["pending", "approved", "rejected"]
RiskLevel = Literal["low", "medium", "high"]
Domain = Literal["media", "flowlab", "trading", "system"]
ArtifactType = Literal[
    "draft", "analysis", "report", "product_spec",
    "screenshot_extraction", "weekly_report", "nightly_summary",
    "selection_report", "video_analysis", "other"
]
VideoAnalysisStatus = Literal["processing", "ready", "approved", "rejected", "failed"]
EventType = Literal[
    "run_started", "run_completed", "run_failed", "run_paused", "run_resumed",
    "task_started", "task_completed", "task_failed", "task_skipped",
    "approval_requested", "approval_decided",
    "artifact_saved",
]


# ── Core Models ────────────────────────────────────────────────────────────────

class WorkflowRun(BaseModel):
    """A top-level workflow execution instance."""
    id: str = Field(default_factory=_new_id)
    name: str                                   # e.g. "daily_content_pipeline"
    domain: Domain = "media"
    status: RunStatus = "pending"
    context: dict[str, Any] = Field(default_factory=dict)  # input params
    started_at: datetime = Field(default_factory=_now)
    completed_at: datetime | None = None
    error: str | None = None

    def is_terminal(self) -> bool:
        return self.status in ("completed", "failed")


class WorkflowTask(BaseModel):
    """A single agent step inside a run."""
    id: str = Field(default_factory=_new_id)
    run_id: str
    agent: str                                  # "ori" | "lala" | "craft" | "sage" | "lumi"
    task_type: str
    status: TaskStatus = "pending"
    input: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime = Field(default_factory=_now)
    completed_at: datetime | None = None

    def is_terminal(self) -> bool:
        return self.status in ("completed", "failed", "skipped")


class WorkflowEvent(BaseModel):
    """An immutable log entry for anything that happened in a run."""
    id: str = Field(default_factory=_new_id)
    run_id: str
    task_id: str | None = None
    event_type: EventType
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=_now)


class Artifact(BaseModel):
    """A file or DB record produced by a task."""
    id: str = Field(default_factory=_new_id)
    run_id: str | None = None
    task_id: str | None = None
    artifact_type: ArtifactType = "other"
    producer: str                               # agent name
    file_path: str | None = None                # relative to ANTICLAUDE_ROOT
    db_ref: str | None = None                   # e.g. "drafts:42"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)


class ApprovalRequest(BaseModel):
    """A human-approval gate that pauses execution until decided."""
    id: str = Field(default_factory=_new_id)
    run_id: str | None = None
    task_id: str | None = None
    action: str                                 # "publish_post" | "promote_product" | ...
    risk_level: RiskLevel = "medium"
    evidence: dict[str, Any] = Field(default_factory=dict)  # summary shown to CEO
    status: ApprovalStatus = "pending"
    decided_at: datetime | None = None
    decision_note: str | None = None


class VideoInsightArtifact(BaseModel):
    """Structured output from a video analysis run (M1 upload + M2 frame analysis).

    Created by POST /api/flowlab/video-upload.
    Processing (frame extraction + draft) is async via VideoAnalysisPipeline.
    """
    id: str = Field(default_factory=_new_id)
    video_path: str                              # relative path under data/uploads/videos/
    original_filename: str = ""
    duration_secs: float | None = None           # filled after frame extraction
    keyframe_paths: list[str] = Field(default_factory=list)  # filled by video_adapter
    transcript: str | None = None                # filled by transcription step (if available)
    extracted_products: list[dict[str, Any]] = Field(default_factory=list)
    threads_draft: str | None = None             # filled by craft agent
    approval_id: str | None = None               # linked approval_request
    artifact_id: str | None = None               # linked workflow artifact
    status: VideoAnalysisStatus = "processing"
    created_at: datetime = Field(default_factory=_now)


class CeoDecisionPackage(BaseModel):
    """Standardised bundle shown to the CEO when an approval gate is reached.

    Built by build_ceo_package() in checkpoint_store.py.
    Consumed by GET /api/approvals/{id}/package and the Office dashboard.
    """
    approval_id: str
    run_id: str | None = None
    action: str                                  # machine action name
    risk_level: RiskLevel = "medium"
    status: ApprovalStatus = "pending"
    summary: str                                 # human-readable one-liner
    evidence: dict[str, Any] = Field(default_factory=dict)
    artifact_links: list[str] = Field(default_factory=list)  # artifact IDs for this run
    reversible: bool = True                                   # False = cannot undo after approve
    approve_label: str = "核准"
    reject_label: str = "拒絕"
    created_at: datetime = Field(default_factory=_now)
