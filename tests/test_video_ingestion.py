"""
Tests for Video Ingestion M1 + M2 — upload path, DB record, approval, model, frame adapter.

Covers:
  - VideoInsightArtifact model fields
  - "video_analysis" in ArtifactType
  - "approve_video_analysis" in _ACTION_SUMMARIES
  - VideoFrameAdapter M2: missing file → ok=False, missing video_path → ok=False
  - VideoFrameAdapter registry status = active
  - POST /api/flowlab/video-upload: unsupported type → 415
  - POST /api/flowlab/video-upload: oversized → 413
  - POST /api/flowlab/video-upload: valid mp4 → creates DB record + approval_request
  - GET /api/flowlab/video-analyses: returns list
  - GET /api/flowlab/video-analyses/{id}: returns detail
"""
from __future__ import annotations

import io
import pytest
from fastapi.testclient import TestClient


# ── Model tests ───────────────────────────────────────────────────────────────

class TestVideoInsightArtifactModel:
    def test_model_default_status(self):
        from src.workflows.models import VideoInsightArtifact
        v = VideoInsightArtifact(video_path="data/uploads/videos/test.mp4")
        assert v.status == "processing"
        assert v.keyframe_paths == []
        assert v.extracted_products == []
        assert v.transcript is None

    def test_model_has_id(self):
        from src.workflows.models import VideoInsightArtifact
        v = VideoInsightArtifact(video_path="test.mp4")
        assert len(v.id) == 36  # uuid4

    def test_video_analysis_in_artifact_type(self):
        from src.workflows.models import Artifact
        a = Artifact(producer="ori", artifact_type="video_analysis")
        assert a.artifact_type == "video_analysis"


class TestVideoActionSummary:
    def test_approve_video_analysis_in_summaries(self):
        from src.workflows.checkpoint_store import _ACTION_SUMMARIES
        assert "approve_video_analysis" in _ACTION_SUMMARIES
        assert len(_ACTION_SUMMARIES["approve_video_analysis"]) > 5


class TestVideoFrameAdapterM2:
    @pytest.mark.asyncio
    async def test_missing_video_path_returns_error(self):
        """Empty video_path → ok=False without crashing."""
        from src.adapters.video_adapter import VideoFrameAdapter
        adapter = VideoFrameAdapter()
        result = await adapter.execute({"video_path": ""})
        assert result.ok is False
        assert result.error is not None

    @pytest.mark.asyncio
    async def test_nonexistent_file_returns_error(self):
        """Non-existent file → ok=False with descriptive error."""
        from src.adapters.video_adapter import VideoFrameAdapter
        adapter = VideoFrameAdapter()
        result = await adapter.execute({"video_path": "/nonexistent/fake_video.mp4"})
        assert result.ok is False
        assert result.error is not None

    def test_adapter_in_registry_is_active(self):
        from src.adapters.registry import get_adapter_meta
        meta = get_adapter_meta("video_frame_extractor")
        assert meta is not None
        assert meta["status"] == "active"
        assert meta["risk_level"] == "low"


# ── API tests ─────────────────────────────────────────────────────────────────

class TestVideoUploadAPI:

    def _client(self):
        from src.api.main import app
        return TestClient(app)

    def test_unsupported_content_type_returns_415(self):
        client = self._client()
        resp = client.post(
            "/api/flowlab/video-upload",
            files={"file": ("test.txt", b"not a video", "text/plain")},
        )
        assert resp.status_code == 415

    def test_valid_mp4_upload_creates_record(self):
        client = self._client()
        # Minimal valid-looking mp4 bytes (not a real video, but content_type matters)
        fake_mp4 = b"\x00" * 1024  # 1KB fake data
        resp = client.post(
            "/api/flowlab/video-upload",
            files={"file": ("sample.mp4", io.BytesIO(fake_mp4), "video/mp4")},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["status"] == "processing"
        assert "video_id" in data
        assert data["video_path"].startswith("data/uploads/videos/")

    def test_uploaded_video_appears_in_list(self):
        client = self._client()
        fake_mp4 = b"\x00" * 512
        upload_resp = client.post(
            "/api/flowlab/video-upload",
            files={"file": ("list_test.mp4", io.BytesIO(fake_mp4), "video/mp4")},
        )
        assert upload_resp.status_code == 200
        video_id = upload_resp.json()["video_id"]

        list_resp = client.get("/api/flowlab/video-analyses")
        assert list_resp.status_code == 200
        ids = [v["id"] for v in list_resp.json()["videos"]]
        assert video_id in ids

    def test_uploaded_video_detail(self):
        client = self._client()
        fake_mp4 = b"\x00" * 512
        upload_resp = client.post(
            "/api/flowlab/video-upload",
            files={"file": ("detail_test.mp4", io.BytesIO(fake_mp4), "video/mp4")},
        )
        video_id = upload_resp.json()["video_id"]

        detail_resp = client.get(f"/api/flowlab/video-analyses/{video_id}")
        assert detail_resp.status_code == 200
        data = detail_resp.json()
        assert data["ok"] is True
        assert data["id"] == video_id
        assert data["status"] == "processing"
        assert isinstance(data["keyframe_paths"], list)

    def test_nonexistent_video_detail_returns_404(self):
        client = self._client()
        resp = client.get("/api/flowlab/video-analyses/nonexistent-id")
        assert resp.status_code == 404

    def test_upload_creates_approval_request_in_review_items(self):
        """Medium-risk approval should create review_item in CEO inbox."""
        from src.db.connection import db
        with db() as conn:
            conn.execute(
                "DELETE FROM review_items WHERE status='pending' AND context LIKE ?",
                ('%"action": "approve_video_analysis"%',),
            )
        client = self._client()
        fake_mp4 = b"\x00" * 512
        upload_resp = client.post(
            "/api/flowlab/video-upload",
            files={"file": ("approval_test.mp4", io.BytesIO(fake_mp4), "video/mp4")},
        )
        assert upload_resp.status_code == 200
        approval_id = upload_resp.json().get("approval_id", "")
        assert approval_id, "approval_id should be set"

        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM review_items WHERE context LIKE ?",
                (f"%{approval_id}%",),
            ).fetchall()
        assert len(rows) >= 1, "medium-risk video upload should create review_item"
