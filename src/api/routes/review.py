"""
Review Queue Routes
  GET   /api/review-queue
  POST  /api/review-queue
  PATCH /api/review-queue/{item_id}

Approval Model — Semantic Contract
-----------------------------------
review_items     → Operator-facing curated inbox.
                   Only high-risk actions that require Sun's manual decision:
                   publish_post, promote_product, approve_purchase,
                   approve_screenshot, approve_video_analysis.
                   This is what the /review page and sidebar badge count.

approval_requests → Workflow-internal gate.
                    Created by the graph runner at every approval step.
                    Some are auto-approved; only curated ones surface in review_items.
                    Source of truth for workflow state — do NOT use for UI counts.

Bridge:
  When a review_item was created from an approval gate, its context JSON contains
  {"approval_id": "..."}.  PATCH /api/review-queue/{id} syncs the decision back
  to the approval_request table so the graph runner can proceed or fail correctly.
"""
import json
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from src.db.connection import db
from src.utils.logger import get_logger

router = APIRouter()
log = get_logger("api.review")


class ReviewItemCreate(BaseModel):
    item_type: str
    question: str
    context: str | None = None
    options_json: str | None = None
    recommended: str | None = None
    reason: str | None = None
    related_agents: str | None = None
    deadline: str | None = None
    default_action: str | None = None
    created_by: str | None = None


class ReviewDecision(BaseModel):
    status: str          # approved | rejected | deferred
    decision_by: str | None = None
    decision_note: str | None = None
    platforms: list[str] = ["x", "threads"]  # which platforms to publish to on approval
    draft_id: int | None = None              # specific draft to publish (overrides auto-pick)


@router.get("/api/review-queue/stats")
async def review_queue_stats():
    """快速統計各狀態的審核項目數量。供 TopNav badge 和 morning report 使用。"""
    try:
        with db() as conn:
            rows = conn.execute(
                "SELECT status, COUNT(*) as n FROM review_items GROUP BY status"
            ).fetchall()
        counts = {r["status"]: r["n"] for r in rows}
        return {
            "pending": counts.get("pending", 0),
            "approved": counts.get("approved", 0),
            "rejected": counts.get("rejected", 0),
            "deferred": counts.get("deferred", 0),
            "total": sum(counts.values()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/review-queue")
async def get_review_queue(status: str | None = None, limit: int = 50):
    """取得待審核項目列表"""
    try:
        with db() as conn:
            if status:
                rows = conn.execute(
                    "SELECT * FROM review_items WHERE status=? ORDER BY created_at DESC LIMIT ?",
                    (status, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM review_items ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                ).fetchall()
        return {"items": [dict(r) for r in rows], "total": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/review-queue")
async def create_review_item(item: ReviewItemCreate):
    """建立新的審核項目（由 agent 呼叫）"""
    try:
        with db() as conn:
            cur = conn.execute(
                """INSERT INTO review_items
                   (item_type, question, context, options_json, recommended, reason,
                    related_agents, deadline, default_action, created_by)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (item.item_type, item.question, item.context, item.options_json,
                 item.recommended, item.reason, item.related_agents,
                 item.deadline, item.default_action, item.created_by),
            )
        return {"ok": True, "id": cur.lastrowid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _trigger_x_publish(approval_id: str, text: str) -> None:
    """Background task: publish to X only."""
    try:
        from src.adapters.x_adapter import XPublishAdapter
        result = await XPublishAdapter().execute({"action": "post", "text": text, "dry_run": False})
        if result.ok:
            log.info(f"X publish OK for approval {approval_id}: {result.data}")
        else:
            log.warning(f"X publish failed for approval {approval_id}: {result.error}")
    except Exception as e:
        log.warning(f"X publish error (non-fatal): {e}")


async def _trigger_threads_publish(approval_id: str, text: str) -> None:
    """Background task: publish to Threads only."""
    try:
        from src.tracker.threads_client import publish_post as threads_publish
        result = await threads_publish(text)
        if result.get("ok"):
            log.info(f"Threads publish OK for approval {approval_id}: post_id={result.get('threads_post_id')}")
        else:
            log.warning(f"Threads publish failed for approval {approval_id}: {result.get('error')}")
    except Exception as e:
        log.warning(f"Threads publish error (non-fatal): {e}")


async def _trigger_dual_publish(approval_id: str, text: str) -> None:
    """Background task: publish to both X and Threads."""
    await _trigger_x_publish(approval_id, text)
    await _trigger_threads_publish(approval_id, text)


async def _resume_pipeline(run_id: str) -> None:
    """Background task: resume graph pipeline after approval gate is cleared."""
    try:
        from src.domains.media.pipeline_graph import run_content_pipeline
        result = await run_content_pipeline(resume_run_id=run_id)
        log.info(f"Pipeline resumed run_id={run_id} ok={result.get('ok')} paused_at={result.get('paused_at')}")
    except Exception as e:
        log.warning(f"Pipeline resume failed for run_id={run_id} (non-fatal): {e}")


@router.patch("/api/review-queue/{item_id}")
async def decide_review_item(item_id: int, decision: ReviewDecision,
                              background_tasks: BackgroundTasks):
    """更新審核項目決策，並同步回對應的 approval_request（若有）。"""
    now = datetime.now(timezone.utc).isoformat()
    try:
        with db() as conn:
            # 1. 取得現有 review_item（需要 context 欄位）
            row = conn.execute(
                "SELECT context FROM review_items WHERE id=?", (item_id,)
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Review item not found")

            # 2. 更新 review_item
            conn.execute(
                """UPDATE review_items
                   SET status=?, decision_by=?, decision_note=?,
                       decision_at=?, updated_at=?
                   WHERE id=?""",
                (decision.status, decision.decision_by, decision.decision_note,
                 now, now, item_id),
            )

            # 3. 若 context 含 approval_id，同步 approval_request
            approval_id: str | None = None
            run_id: str | None = None
            try:
                ctx = json.loads(row["context"] or "{}")
                approval_id = ctx.get("approval_id")
                run_id = ctx.get("run_id")
            except Exception:
                pass

            if approval_id:
                # Map review decision → approval decision
                approval_decision = (
                    "approved" if decision.status == "approved"
                    else "rejected" if decision.status == "rejected"
                    else None   # "deferred" → leave approval_request pending
                )
                if approval_decision:
                    conn.execute(
                        """UPDATE approval_requests
                           SET status=?, decided_at=?, decision_note=?
                           WHERE id=? AND status='pending'""",
                        (approval_decision, now,
                         f"[review_queue sync] {decision.decision_note or ''}",
                         approval_id),
                    )
                    log.info(
                        f"review_item {item_id} → synced approval {approval_id} → {approval_decision}"
                    )

                    # Wire dual publish: approved publish_post → fire X + Threads
                    if approval_decision == "approved" and ctx.get("action") == "publish_post":
                        # 1. Use the specific draft_id if frontend passed one (most reliable)
                        if decision.draft_id:
                            draft_row = conn.execute(
                                "SELECT content FROM drafts WHERE id=?",
                                (decision.draft_id,),
                            ).fetchone()
                        else:
                            draft_row = conn.execute(
                                """SELECT content FROM drafts
                                   WHERE (published_at IS NULL OR published_at = '')
                                   ORDER BY rowid DESC LIMIT 1"""
                            ).fetchone()
                        publish_text = draft_row["content"] if draft_row else None

                        # 2. Fallback to evidence content_preview
                        if not publish_text:
                            apr_row = conn.execute(
                                "SELECT evidence_json FROM approval_requests WHERE id=?",
                                (approval_id,),
                            ).fetchone()
                            if apr_row:
                                evidence = json.loads(apr_row["evidence_json"] or "{}")
                                publish_text = (
                                    evidence.get("content_preview")
                                    or evidence.get("text")
                                    or evidence.get("draft", "")
                                )

                        if publish_text:
                            platforms = set(decision.platforms) if decision.platforms else {"x", "threads"}
                            wants_x = "x" in platforms
                            wants_threads = "threads" in platforms
                            if wants_x and wants_threads:
                                background_tasks.add_task(_trigger_dual_publish, approval_id, publish_text)
                                log.info(f"Dual publish (X + Threads) queued for approval {approval_id}")
                            elif wants_x:
                                background_tasks.add_task(_trigger_x_publish, approval_id, publish_text)
                                log.info(f"X-only publish queued for approval {approval_id}")
                            elif wants_threads:
                                background_tasks.add_task(_trigger_threads_publish, approval_id, publish_text)
                                log.info(f"Threads-only publish queued for approval {approval_id}")
                            else:
                                log.warning(f"publish_post approved but no platforms selected (approval={approval_id}) — nothing published")
                        else:
                            log.warning(
                                f"publish_post approved but no publishable text found "
                                f"(approval={approval_id}) — "
                                f"drafts table had {'no unpublished row' if not draft_row else 'empty content'}, "
                                f"evidence had no content_preview/text/draft field. "
                                f"Nothing was published."
                            )

                    # Resume pipeline so save_outputs node runs after gate is cleared
                    if run_id:
                        background_tasks.add_task(_resume_pipeline, run_id)
                        log.info(f"Pipeline resume queued for run_id={run_id}")

        return {"ok": True, "id": item_id, "status": decision.status,
                "approval_synced": approval_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/review-queue/rejected")
async def purge_rejected_items(older_than_days: int = 0):
    """
    清除已拒絕的審核項目。
    older_than_days=0（預設）清除全部已拒絕；>0 只清除超過 N 天的。
    同步清除對應的 approval_requests（status=rejected）。
    """
    try:
        with db() as conn:
            if older_than_days > 0:
                cutoff = f"datetime('now', '-{older_than_days} days')"
                r1 = conn.execute(
                    f"DELETE FROM review_items WHERE status='rejected' AND created_at < {cutoff}"
                )
                r2 = conn.execute(
                    f"DELETE FROM approval_requests WHERE status='rejected' AND decided_at < {cutoff}"
                )
            else:
                r1 = conn.execute("DELETE FROM review_items WHERE status='rejected'")
                r2 = conn.execute("DELETE FROM approval_requests WHERE status='rejected'")
        return {
            "ok": True,
            "review_items_deleted": r1.rowcount,
            "approval_requests_deleted": r2.rowcount,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/review-queue")
async def cleanup_review_items(status: str):
    """
    Delete review items by status to keep the queue manageable.

    Supported status values:
    - pending   (dismiss all unanswered items — also cancels linked approval_requests)
    - approved
    - rejected
    - deferred
    - decided   (approved + rejected + deferred)
    - all       (everything)
    """
    allowed = {"pending", "approved", "rejected", "deferred", "decided", "all"}
    if status not in allowed:
        raise HTTPException(status_code=400, detail=f"status must be one of {sorted(allowed)}")

    try:
        with db() as conn:
            if status == "all":
                review_cur = conn.execute("DELETE FROM review_items")
                approval_deleted = conn.execute("DELETE FROM approval_requests").rowcount
            elif status == "decided":
                review_cur = conn.execute(
                    "DELETE FROM review_items WHERE status IN ('approved','rejected','deferred')"
                )
                approval_deleted = conn.execute(
                    "DELETE FROM approval_requests WHERE status IN ('approved','rejected')"
                ).rowcount
            elif status == "pending":
                review_cur = conn.execute(
                    "DELETE FROM review_items WHERE status='pending'"
                )
                # Also cancel the linked pending approval_requests so the pipeline
                # doesn't hang waiting for a gate that no longer has a review item.
                approval_deleted = conn.execute(
                    "UPDATE approval_requests SET status='rejected', decision_note='dismissed via review queue cleanup' "
                    "WHERE status='pending'"
                ).rowcount
            else:
                review_cur = conn.execute(
                    "DELETE FROM review_items WHERE status=?",
                    (status,),
                )
                approval_deleted = (
                    conn.execute(
                        "DELETE FROM approval_requests WHERE status=?",
                        (status,),
                    ).rowcount
                    if status in {"approved", "rejected"}
                    else 0
                )
        return {
            "ok": True,
            "status": status,
            "review_items_deleted": review_cur.rowcount,
            "approval_requests_deleted": approval_deleted,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
