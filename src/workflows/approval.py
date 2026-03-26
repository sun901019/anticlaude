"""
Workflow Approval Gate
=======================
Create approval requests, check their status, and record decisions.

Approval flow:
    1. Agent calls request_approval(run_id, task_id, action, risk_level, evidence)
    2. CEO sees it in /api/approvals/pending
    3. CEO calls decide_approval(approval_id, "approved"|"rejected", note)
    4. Runner checks get_approval(approval_id).status to resume or cancel

Usage:
    from src.workflows.approval import request_approval, decide

    approval_id = request_approval(
        run_id=run.id,
        task_id=task.id,
        action="publish_post",
        risk_level="medium",
        evidence={"draft_id": 42, "content_preview": "..."},
    )
"""
from __future__ import annotations

import json
from typing import Any

from src.workflows.models import ApprovalRequest, RiskLevel
from src.workflows.checkpoint_store import create_approval, get_approval, decide_approval
from src.workflows.events import emit
from src.db.connection import db
from src.utils.logger import get_logger

log = get_logger("workflows.approval")

# Actions that warrant a mirrored review_item in the legacy CEO inbox.
# Not every approval_request should become a review queue item, otherwise
# internal workflow gates like `select_draft` create noisy backlog entries.
_INBOX_ACTIONS = {
    "publish_post",
    "promote_product",
    "approve_screenshot",
    "approve_video_analysis",
    "approve_purchase",
}

_ACTION_QUESTION: dict[str, str] = {
    "select_draft":         "請審核 AI 草稿，核准後 Pipeline 才會繼續儲存結果",
    "publish_post":         "AI 準備同時發布至 X 和 Threads，請預覽草稿後確認",
    "promote_product":      "AI 建議推廣以下商品，請確認是否進行",
    "review_scored_topics": "AI 已完成主題評分，請確認方向後繼續選題流程",
    "approve_screenshot":      "截圖分析完成，請確認是否產出貼文草稿",
    "approve_video_analysis":  "影片已上傳，請確認是否進行 AI 分析與草稿產出",
    "approve_purchase":        "AI 建議進貨此選品，請確認是否採購",
}


def _create_inbox_item(approval: ApprovalRequest) -> None:
    """Mirror high/medium approval_request into review_items for CEO inbox."""
    if approval.action not in _INBOX_ACTIONS:
        return

    # Dedup: one review_item per approval_id (prevent double-insert on retry).
    # Also cap at 5 pending per action to stop runaway accumulation across many pipeline runs.
    try:
        with db() as conn:
            # Per-approval dedup: bail if this exact approval already has a review_item
            already = conn.execute(
                "SELECT id FROM review_items WHERE context LIKE ? LIMIT 1",
                (f'%{approval.id}%',),
            ).fetchone()
            if already:
                log.info(
                    f"Skipping review_item for approval {approval.id} — already exists (id={already['id']})"
                )
                return
            # Global cap: at most 5 pending per action to avoid inbox flood
            count = conn.execute(
                "SELECT COUNT(*) FROM review_items WHERE status='pending' AND created_by='workflow' "
                "AND context LIKE ?",
                (f'%"action": "{approval.action}"%',),
            ).fetchone()[0]
        if count >= 5:
            log.info(
                f"Skipping review_item for {approval.action} — {count} pending already (cap=5)"
            )
            return
    except Exception as e:
        log.warning(f"Dedup check failed (continuing anyway): {e}")

    question = _ACTION_QUESTION.get(
        approval.action,
        f"AI 發出審核請求：{approval.action}",
    )
    context_json = json.dumps(
        {"approval_id": approval.id, "run_id": approval.run_id, "action": approval.action},
        ensure_ascii=False,
    )
    publish_note = "同時發布至 X 和 Threads" if approval.action == "publish_post" else "允許 Pipeline 繼續執行"
    options_json = json.dumps(
        [
            {"label": "核准", "consequence": publish_note},
            {"label": "拒絕", "consequence": "停止本次 Pipeline Run"},
        ],
        ensure_ascii=False,
    )
    try:
        with db() as conn:
            conn.execute(
                """INSERT INTO review_items
                   (item_type, question, context, options_json, recommended, reason,
                    related_agents, created_by)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    "content",
                    question,
                    context_json,
                    options_json,
                    "核准",
                    f"Risk level: {approval.risk_level}",
                    json.dumps(["craft", "lumi"], ensure_ascii=False),
                    "workflow",
                ),
            )
        log.info(f"Review inbox item created for approval {approval.id}")
    except Exception as e:
        log.warning(f"Failed to create inbox item for approval {approval.id}: {e}")


def request_approval(
    action: str,
    evidence: dict[str, Any],
    risk_level: RiskLevel = "medium",
    run_id: str | None = None,
    task_id: str | None = None,
) -> str:
    """
    Create an approval request and return its ID.
    The caller is responsible for polling get_approval(id).status.
    """
    approval = ApprovalRequest(
        run_id=run_id,
        task_id=task_id,
        action=action,
        risk_level=risk_level,
        evidence=evidence,
    )
    create_approval(approval)
    _create_inbox_item(approval)   # mirror to CEO review inbox for medium/high risk

    if run_id:
        emit(
            "approval_requested",
            run_id=run_id,
            task_id=task_id,
            payload={"approval_id": approval.id, "action": action, "risk_level": risk_level},
        )

    log.info(f"Approval requested: {approval.id} | action={action} | risk={risk_level}")
    return approval.id


def check_approval(approval_id: str) -> str:
    """Return current status: 'pending' | 'approved' | 'rejected'."""
    approval = get_approval(approval_id)
    return approval.status if approval else "not_found"


def decide(approval_id: str, decision: str, note: str | None = None) -> bool:
    """
    Record a CEO decision on an approval request.
    Returns True if the request was found and updated.
    """
    updated = decide_approval(approval_id, decision, note)
    if updated:
        approval = get_approval(approval_id)
        if approval and approval.run_id:
            emit(
                "approval_decided",
                run_id=approval.run_id,
                task_id=approval.task_id,
                payload={"approval_id": approval_id, "decision": decision},
            )
        log.info(f"Approval decided: {approval_id} → {decision}")
    return updated
