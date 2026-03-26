"""
Tests for X publish trigger wired in PATCH /api/review-queue/{item_id}.

Covers:
- Approved publish_post approval triggers _trigger_dual_publish via BackgroundTasks
- Rejected publish_post does NOT trigger
- Non-publish_post action does NOT trigger
- Missing text in evidence logs warning but does not crash (response still 200)
- _trigger_dual_publish calls XPublishAdapter.execute with correct payload
- _trigger_dual_publish failure (adapter ok=False) does not raise
"""
import asyncio
import json

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.api.main import app
from src.db.connection import db
from src.workflows.approval import request_approval

client = TestClient(app)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _get_review_item_for_approval(approval_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM review_items WHERE context LIKE ?",
            (f"%{approval_id}%",),
        ).fetchall()
    return [dict(r) for r in rows]


def _clear_pending(action: str) -> None:
    with db() as conn:
        conn.execute(
            "DELETE FROM review_items WHERE status='pending' AND context LIKE ?",
            (f'%"action": "{action}"%',),
        )


# ── Test Class ─────────────────────────────────────────────────────────────────

class TestXPublishTrigger:

    def test_publish_post_approval_queues_x_trigger(self):
        """Approving a publish_post review item must call _trigger_dual_publish."""
        _clear_pending("publish_post")
        approval_id = request_approval(
            action="publish_post",
            risk_level="high",
            evidence={"content_preview": "Test tweet content"},
        )
        items = _get_review_item_for_approval(approval_id)
        assert items, "Expected at least one review_item for publish_post approval"
        item_id = items[0]["id"]

        with patch("src.api.routes.review._trigger_dual_publish") as mock_trigger:
            resp = client.patch(
                f"/api/review-queue/{item_id}",
                json={"status": "approved", "decision_by": "ceo"},
            )
            assert resp.status_code == 200, resp.text
            # FastAPI TestClient runs BackgroundTasks synchronously
            mock_trigger.assert_called_once_with(approval_id, "Test tweet content")

    def test_rejected_publish_post_does_not_trigger_x(self):
        """Rejecting a publish_post review item must NOT call _trigger_dual_publish."""
        _clear_pending("publish_post")
        approval_id = request_approval(
            action="publish_post",
            risk_level="high",
            evidence={"content_preview": "Should not publish"},
        )
        items = _get_review_item_for_approval(approval_id)
        assert items, "Expected review_item for publish_post"
        item_id = items[0]["id"]

        with patch("src.api.routes.review._trigger_dual_publish") as mock_trigger:
            resp = client.patch(
                f"/api/review-queue/{item_id}",
                json={"status": "rejected", "decision_by": "ceo"},
            )
            assert resp.status_code == 200, resp.text
            mock_trigger.assert_not_called()

    def test_non_publish_action_does_not_trigger_x(self):
        """Approving a non-publish_post item must NOT call _trigger_dual_publish."""
        _clear_pending("approve_screenshot")
        approval_id = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"test": "no_x"},
        )
        items = _get_review_item_for_approval(approval_id)
        assert items, "Expected review_item for approve_screenshot"
        item_id = items[0]["id"]

        with patch("src.api.routes.review._trigger_dual_publish") as mock_trigger:
            resp = client.patch(
                f"/api/review-queue/{item_id}",
                json={"status": "approved", "decision_by": "ceo"},
            )
            assert resp.status_code == 200, resp.text
            mock_trigger.assert_not_called()

    def test_publish_post_missing_text_logs_warning_not_crash(self):
        """Approving publish_post with no text in evidence logs warning, still returns 200."""
        _clear_pending("publish_post")
        approval_id = request_approval(
            action="publish_post",
            risk_level="high",
            evidence={"some_other_key": "value"},
        )
        items = _get_review_item_for_approval(approval_id)
        assert items, "Expected review_item for publish_post"
        item_id = items[0]["id"]

        # No patch — let the real logic run; no x_text means no background task queued
        resp = client.patch(
            f"/api/review-queue/{item_id}",
            json={"status": "approved", "decision_by": "ceo"},
        )
        # Response must still be 200 (no crash)
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["ok"] is True

    def test_trigger_dual_publish_function_calls_adapter(self):
        """_trigger_dual_publish must call XPublishAdapter.execute with correct payload (X leg)."""
        from src.api.routes.review import _trigger_dual_publish

        mock_result = type("R", (), {"ok": True, "data": {"tweet_id": "999"}, "error": None})()

        # XPublishAdapter is imported lazily inside _trigger_dual_publish;
        # patch it at its source module so the lazy import resolves to the mock.
        with patch("src.adapters.x_adapter.XPublishAdapter") as MockAdapter, \
             patch("src.api.routes.review._trigger_threads_publish", new=AsyncMock()) as mock_threads:
            MockAdapter.return_value.execute = AsyncMock(return_value=mock_result)
            asyncio.run(_trigger_dual_publish("test-approval-id", "Hello world"))
            MockAdapter.return_value.execute.assert_called_once_with(
                {"action": "post", "text": "Hello world", "dry_run": False}
            )
            mock_threads.assert_awaited_once_with("test-approval-id", "Hello world")

    def test_trigger_dual_publish_adapter_failure_does_not_raise(self):
        """_trigger_dual_publish must not raise even when adapter returns ok=False (X leg)."""
        from src.api.routes.review import _trigger_dual_publish

        mock_result = type("R", (), {"ok": False, "data": None, "error": "credentials missing"})()

        # XPublishAdapter is imported lazily; patch at source module.
        with patch("src.adapters.x_adapter.XPublishAdapter") as MockAdapter, \
             patch("src.api.routes.review._trigger_threads_publish", new=AsyncMock()) as mock_threads:
            MockAdapter.return_value.execute = AsyncMock(return_value=mock_result)
            # Must complete without exception
            asyncio.run(_trigger_dual_publish("fail-approval-id", "Some text"))
            MockAdapter.return_value.execute.assert_called_once()
            mock_threads.assert_awaited_once_with("fail-approval-id", "Some text")
