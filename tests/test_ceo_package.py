"""
Tests for CeoDecisionPackage — GET /api/approvals/{id}/package.

Covers:
  - Package has all required fields
  - Risk level and summary propagated correctly
  - Artifact links collected from run
  - 404 for unknown approval_id
  - Unknown action falls back to generic summary
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.workflows.checkpoint_store import build_ceo_package
from src.workflows.models import CeoDecisionPackage


# ── Unit: build_ceo_package ───────────────────────────────────────────────────

class TestBuildCeoPackage:
    def test_returns_none_for_unknown_id(self):
        result = build_ceo_package("nonexistent-approval-id")
        assert result is None

    def test_package_has_required_fields(self, monkeypatch):
        from src.workflows.models import ApprovalRequest

        fake_approval = ApprovalRequest(
            id="app-1", run_id="run-1", task_id=None,
            action="select_draft", risk_level="medium",
            evidence={"outputs_summary": {"draft": "test content"}},
            status="pending",
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_approval",
            lambda approval_id: fake_approval,
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_artifacts_for_run",
            lambda run_id: [],
        )

        pkg = build_ceo_package("app-1")
        assert isinstance(pkg, CeoDecisionPackage)
        assert pkg.approval_id == "app-1"
        assert pkg.run_id == "run-1"
        assert pkg.action == "select_draft"
        assert pkg.risk_level == "medium"
        assert pkg.status == "pending"
        assert pkg.summary  # non-empty
        assert isinstance(pkg.artifact_links, list)
        assert pkg.approve_label
        assert pkg.reject_label

    def test_known_action_returns_meaningful_summary(self, monkeypatch):
        from src.workflows.models import ApprovalRequest

        fake_approval = ApprovalRequest(
            id="app-2", run_id=None, task_id=None,
            action="select_draft", risk_level="medium", status="pending",
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_approval",
            lambda approval_id: fake_approval,
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_artifacts_for_run",
            lambda run_id: [],
        )

        pkg = build_ceo_package("app-2")
        assert "草稿" in pkg.summary or "審核" in pkg.summary

    def test_unknown_action_falls_back_to_generic(self, monkeypatch):
        from src.workflows.models import ApprovalRequest

        fake_approval = ApprovalRequest(
            id="app-3", run_id=None, task_id=None,
            action="some_future_action", risk_level="high", status="pending",
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_approval",
            lambda approval_id: fake_approval,
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_artifacts_for_run",
            lambda run_id: [],
        )

        pkg = build_ceo_package("app-3")
        assert "some_future_action" in pkg.summary

    def test_artifact_links_collected(self, monkeypatch):
        from src.workflows.models import ApprovalRequest, Artifact

        fake_approval = ApprovalRequest(
            id="app-4", run_id="run-4", task_id=None,
            action="publish_post", risk_level="high", status="pending",
        )
        fake_artifacts = [
            Artifact(id="art-1", run_id="run-4", producer="craft", artifact_type="draft"),
            Artifact(id="art-2", run_id="run-4", producer="lumi", artifact_type="report"),
        ]
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_approval",
            lambda approval_id: fake_approval,
        )
        monkeypatch.setattr(
            "src.workflows.checkpoint_store.get_artifacts_for_run",
            lambda run_id: fake_artifacts,
        )

        pkg = build_ceo_package("app-4")
        assert "art-1" in pkg.artifact_links
        assert "art-2" in pkg.artifact_links


# ── API: GET /api/approvals/{id}/package ─────────────────────────────────────

class TestApprovalPackageEndpoint:
    def test_404_for_unknown_id(self):
        from src.api.main import app
        client = TestClient(app)
        resp = client.get("/api/approvals/does-not-exist/package")
        assert resp.status_code == 404

    def test_returns_package_for_real_approval(self):
        """Create an approval via the approval module, then fetch its package."""
        from src.api.main import app
        from src.workflows.approval import request_approval

        approval_id = request_approval(
            action="select_draft",
            risk_level="medium",
            evidence={"test": "evidence"},
        )

        client = TestClient(app)
        resp = client.get(f"/api/approvals/{approval_id}/package")
        assert resp.status_code == 200
        data = resp.json()
        assert data["approval_id"] == approval_id
        assert data["action"] == "select_draft"
        assert data["risk_level"] == "medium"
        assert "summary" in data
        assert isinstance(data["artifact_links"], list)
        assert data["approve_label"]
        assert data["reject_label"]
