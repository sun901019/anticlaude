from __future__ import annotations

import json

from fastapi.testclient import TestClient

from src.api.main import app
from src.db.connection import db
from src.workflows.approval import request_approval
from src.workflows.checkpoint_store import get_approval


client = TestClient(app)


def _get_review_items_for_approval(approval_id: str) -> list[dict]:
    with db() as conn:
        rows = conn.execute(
            "SELECT * FROM review_items WHERE context LIKE ?",
            (f"%{approval_id}%",),
        ).fetchall()
    return [dict(row) for row in rows]


def _clear_pending_review_items_for_action(action: str) -> None:
    with db() as conn:
        conn.execute(
            "DELETE FROM review_items WHERE status='pending' AND context LIKE ?",
            (f'%"action": "{action}"%',),
        )


class TestApprovalBridge:
    def test_select_draft_no_longer_creates_review_item(self):
        approval_id = request_approval(
            action="select_draft",
            risk_level="medium",
            evidence={"test": "select_draft_internal"},
        )
        items = _get_review_items_for_approval(approval_id)
        assert items == []

    def test_publish_post_still_creates_review_item(self):
        _clear_pending_review_items_for_action("publish_post")
        approval_id = request_approval(
            action="publish_post",
            risk_level="high",
            evidence={"test": "bridge_high"},
        )
        items = _get_review_items_for_approval(approval_id)
        assert len(items) >= 1
        ctx = json.loads(items[0]["context"])
        assert ctx["approval_id"] == approval_id

    def test_low_risk_does_not_create_review_item(self):
        approval_id = request_approval(
            action="review_scored_topics",
            risk_level="low",
            evidence={"test": "bridge_low"},
        )
        items = _get_review_items_for_approval(approval_id)
        assert items == []

    def test_review_decision_syncs_to_approval_approved(self):
        _clear_pending_review_items_for_action("approve_screenshot")
        approval_id = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"test": "sync_approved"},
        )
        item_id = _get_review_items_for_approval(approval_id)[0]["id"]

        resp = client.patch(
            f"/api/review-queue/{item_id}",
            json={"status": "approved", "decision_by": "ceo", "decision_note": "looks good"},
        )
        assert resp.status_code == 200
        assert resp.json()["approval_synced"] == approval_id

        approval = get_approval(approval_id)
        assert approval is not None
        assert approval.status == "approved"

    def test_review_decision_syncs_to_approval_rejected(self):
        _clear_pending_review_items_for_action("publish_post")
        approval_id = request_approval(
            action="publish_post",
            risk_level="high",
            evidence={"test": "sync_rejected"},
        )
        item_id = _get_review_items_for_approval(approval_id)[0]["id"]

        resp = client.patch(
            f"/api/review-queue/{item_id}",
            json={"status": "rejected", "decision_by": "ceo"},
        )
        assert resp.status_code == 200

        approval = get_approval(approval_id)
        assert approval is not None
        assert approval.status == "rejected"

    def test_deferred_review_leaves_approval_pending(self):
        _clear_pending_review_items_for_action("approve_video_analysis")
        approval_id = request_approval(
            action="approve_video_analysis",
            risk_level="medium",
            evidence={"test": "sync_deferred"},
        )
        item_id = _get_review_items_for_approval(approval_id)[0]["id"]

        resp = client.patch(
            f"/api/review-queue/{item_id}",
            json={"status": "deferred", "decision_by": "ceo"},
        )
        assert resp.status_code == 200

        approval = get_approval(approval_id)
        assert approval is not None
        assert approval.status == "pending"

    def test_review_item_has_human_readable_question(self):
        _clear_pending_review_items_for_action("approve_screenshot")
        approval_id = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"test": "question_check"},
        )
        items = _get_review_items_for_approval(approval_id)
        assert items
        assert "審核" in items[0]["question"] or "確認" in items[0]["question"]

    def test_cleanup_endpoint_removes_approved_items(self):
        _clear_pending_review_items_for_action("approve_screenshot")
        approval_id = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"test": "cleanup_approved"},
        )
        item_id = _get_review_items_for_approval(approval_id)[0]["id"]
        client.patch(
            f"/api/review-queue/{item_id}",
            json={"status": "approved", "decision_by": "ceo"},
        )

        resp = client.delete("/api/review-queue?status=approved")
        assert resp.status_code == 200
        assert resp.json()["review_items_deleted"] >= 1

    def test_cleanup_endpoint_removes_deferred_items_only_from_review_queue(self):
        _clear_pending_review_items_for_action("approve_video_analysis")
        approval_id = request_approval(
            action="approve_video_analysis",
            risk_level="medium",
            evidence={"test": "cleanup_deferred"},
        )
        item_id = _get_review_items_for_approval(approval_id)[0]["id"]
        client.patch(
            f"/api/review-queue/{item_id}",
            json={"status": "deferred", "decision_by": "ceo"},
        )

        resp = client.delete("/api/review-queue?status=deferred")
        assert resp.status_code == 200
        assert resp.json()["review_items_deleted"] >= 1
        assert resp.json()["approval_requests_deleted"] == 0


class TestApprovalDedup:
    """Dedup and cap-at-5 accumulation guard tests (checklist 1.2)."""

    def test_same_approval_id_does_not_create_duplicate_review_item(self):
        """Triggering the same approval twice must not create a second review_item."""
        _clear_pending_review_items_for_action("publish_post")
        approval_id = request_approval(
            action="publish_post",
            risk_level="high",
            evidence={"test": "dedup_same_approval"},
        )
        # Simulate second trigger with the same approval_id (e.g. workflow retry)
        from src.workflows.approval import _create_inbox_item
        from src.workflows.checkpoint_store import get_approval
        approval = get_approval(approval_id)
        assert approval is not None
        _create_inbox_item(approval)  # second call — should be no-op

        items = _get_review_items_for_approval(approval_id)
        assert len(items) == 1, f"Expected 1 item, got {len(items)}"

    def test_same_action_different_runs_each_get_own_review_item(self):
        """Two different approvals for the same action (different runs) both appear."""
        _clear_pending_review_items_for_action("approve_screenshot")
        id_a = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"test": "dedup_run_a"},
        )
        id_b = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"test": "dedup_run_b"},
        )
        items_a = _get_review_items_for_approval(id_a)
        items_b = _get_review_items_for_approval(id_b)
        assert len(items_a) == 1
        assert len(items_b) == 1
        assert items_a[0]["id"] != items_b[0]["id"]

    def test_cap_at_5_prevents_runaway_accumulation(self):
        """More than 5 pending items for the same action must be silently dropped."""
        _clear_pending_review_items_for_action("publish_post")
        ids = []
        for i in range(7):
            ids.append(request_approval(
                action="publish_post",
                risk_level="high",
                evidence={"test": f"cap_test_{i}"},
            ))

        with db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM review_items WHERE status='pending' AND context LIKE ?",
                ('%"action": "publish_post"%',),
            ).fetchone()[0]
        assert count <= 5, f"Expected ≤5 items, got {count}"
