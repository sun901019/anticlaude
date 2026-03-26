"""
AI Office & Morning Report Routes
  GET  /api/agents/status
  POST /api/agents/{agent_id}/status
  GET  /api/agents/stream
  GET  /api/agents/events
  POST /api/agents/demo-handoff
  GET  /api/agents/today-stats
  GET  /api/morning/briefing
  GET  /api/morning-report
"""
import json as _json
from datetime import date, datetime, timedelta

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import src.api.state as state
from src.utils.logger import get_logger

router = APIRouter()
log = get_logger("api.agents")


# ── AI Office ─────────────────────────────────────────────────────────────────

@router.get("/api/agents/status")
async def get_agents_status():
    from src.api.agent_status import get_all_status
    return get_all_status()


class AgentStatusUpdate(BaseModel):
    status: str
    task: str = ""
    title: str = ""
    task_type: str = ""
    priority: str = "normal"
    source_agent_id: str = ""
    target_agent_id: str = ""
    artifact_refs: list[str] = []
    task_id: str = ""
    started_at: str = ""


@router.post("/api/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, body: AgentStatusUpdate):
    from src.api.agent_status import update_agent_task
    update_agent_task(
        agent_id,
        status=body.status, task=body.task, title=body.title,
        task_type=body.task_type, priority=body.priority,
        source_agent_id=body.source_agent_id, target_agent_id=body.target_agent_id,
        artifact_refs=body.artifact_refs, task_id=body.task_id,
        started_at=body.started_at,
    )
    return {"ok": True, "agent": agent_id, "status": body.status}


@router.get("/api/agents/stream")
async def stream_agents_status():
    from src.api.agent_status import sse_generator
    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/api/agents/events")
async def get_agent_events(limit: int = 50, agent_id: str | None = None):
    from src.api.agent_status import get_recent_events
    events = get_recent_events(limit=limit, agent_id=agent_id)
    return {"events": events, "count": len(events)}


@router.post("/api/agents/demo-handoff")
async def demo_agent_handoff():
    from src.api.agent_status import run_demo_handoff
    return {"ok": True, "handoffs": run_demo_handoff()}


@router.get("/api/agents/today-stats")
async def get_today_stats():
    from src.db.connection import db
    from src.config import OUTPUTS_DIR

    today = date.today().isoformat()
    reports_dir = OUTPUTS_DIR / "daily_reports"

    pipeline: dict = {
        "ran_today": False, "ran_at": None, "status": None,
        "topics_found": 0, "top3": [], "drafts_count": 0, "models": {},
    }
    report_path = reports_dir / f"{today}.json"
    if report_path.exists():
        try:
            r = _json.loads(report_path.read_text(encoding="utf-8"))
            pipeline.update({
                "ran_today": True, "status": "success",
                "topics_found": len(r.get("all_topics", [])),
                "top3": [t.get("cluster_label", "") for t in r.get("top3", []) if t],
                "models": r.get("model_log", {}),
                "ran_at": datetime.fromtimestamp(report_path.stat().st_mtime).strftime("%H:%M"),
            })
        except Exception:
            pipeline.update({"ran_today": True, "status": "error"})

    agents_stats: dict = {}
    try:
        with db() as conn:
            ori_count = conn.execute(
                "SELECT COUNT(*) as n FROM articles WHERE date(scraped_at)=?", (today,)
            ).fetchone()["n"]
            agents_stats["ori"] = {
                "signal_count": ori_count,
                "label": f"今日訊號 {ori_count} 篇" if ori_count else "今日尚未抓取",
            }

            lala_top3 = pipeline.get("top3", [])
            agents_stats["lala"] = {
                "top3": lala_top3,
                "label": f"已選 {len(lala_top3)} 個主題" if lala_top3 else "今日尚未選題",
            }

            draft_row = conn.execute(
                "SELECT COUNT(*) as n, MAX(created_at) as last FROM drafts WHERE date(created_at)=?", (today,)
            ).fetchone()
            draft_n, draft_last = draft_row["n"], draft_row["last"]
            latest_hook = None
            if draft_n > 0:
                h = conn.execute(
                    "SELECT hook FROM drafts WHERE date(created_at)=? AND hook IS NOT NULL ORDER BY created_at DESC LIMIT 1",
                    (today,)
                ).fetchone()
                if h and h["hook"]:
                    latest_hook = h["hook"][:30] + "…" if len(h["hook"]) > 30 else h["hook"]
            agents_stats["craft"] = {
                "drafts_count": draft_n,
                "last_at": draft_last[11:16] if draft_last else None,
                "latest_hook": latest_hook,
                "label": f"今日草稿 {draft_n} 篇" if draft_n else "今日尚未生成",
            }
            pipeline["drafts_count"] = draft_n

            ins = conn.execute(
                "SELECT analysis_date, engagement_trend, growth_rate FROM audience_insights ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
            pending = conn.execute(
                "SELECT COUNT(*) as n FROM ecommerce_selection_candidates WHERE selection_status NOT IN ('approved','rejected','rejected_auto')"
            ).fetchone()["n"]
            agents_stats["sage"] = {
                "last_insights_date": ins["analysis_date"] if ins else None,
                "trend": ins["engagement_trend"] if ins else None,
                "growth_rate": ins["growth_rate"] if ins else None,
                "pending_candidates": pending,
                "label": f"待分析商品 {pending} 個" if pending else "候選池已清空",
            }
    except Exception:
        pass

    threads = {"last_sync": None, "trend": None, "growth_rate": None}
    sage = agents_stats.get("sage", {})
    if sage.get("last_insights_date"):
        threads = {
            "last_sync": sage["last_insights_date"],
            "trend": sage["trend"],
            "growth_rate": sage["growth_rate"],
        }

    flowlab = {"pending_candidates": sage.get("pending_candidates", 0)}

    try:
        now = datetime.now()
        nxt = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now.hour >= 8:
            nxt += timedelta(days=1)
        h = int((nxt - now).total_seconds() // 3600)
        m = int(((nxt - now).total_seconds() % 3600) // 60)
        next_label = f"{h}h {m}m 後" if h > 0 else f"{m}m 後"
    except Exception:
        h, m, next_label, nxt = 0, 0, "—", datetime.now()

    return {
        "today": today,
        "pipeline": pipeline,
        "agents": agents_stats,
        "threads": threads,
        "flowlab": flowlab,
        "next_pipeline": {
            "at": nxt.strftime("%Y-%m-%dT%H:%M:00"),
            "hours_until": h,
            "mins_until": m,
            "label": next_label,
        },
    }


# ── Morning Report ────────────────────────────────────────────────────────────

def _build_morning_report() -> dict:
    """Shared logic for both morning endpoints."""
    from src.db.connection import db
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    result: dict = {
        "date": today,
        "pipeline_ran_today": False,
        "pipeline_ran_at": None,
        "topics_today": 0,
        "drafts_today": 0,
        "posts_today": 0,
        "yesterday_best": None,
        "yesterday_avg_engagement": None,
        "next_pipeline_label": "",
        "has_error": bool(state.pipeline_last_error),
        "error_summary": state.pipeline_last_error[:80] if state.pipeline_last_error else "",
        "pending_approvals": 0,
        "pending_review_items": 0,
    }
    if state.pipeline_last_success_at and state.pipeline_last_success_at[:10] == today:
        result["pipeline_ran_today"] = True
        result["pipeline_ran_at"] = state.pipeline_last_success_at
    try:
        with db() as conn:
            result["topics_today"] = conn.execute(
                "SELECT COUNT(*) as n FROM topics WHERE date=?", (today,)
            ).fetchone()["n"]
            result["drafts_today"] = conn.execute(
                "SELECT COUNT(*) as n FROM drafts WHERE date(created_at)=?", (today,)
            ).fetchone()["n"]
            result["posts_today"] = conn.execute(
                "SELECT COUNT(*) as n FROM posts WHERE date(posted_at)=?", (today,)
            ).fetchone()["n"]
            best = conn.execute(
                """SELECT text, views, engagement_rate FROM posts
                   WHERE date(posted_at)=? AND views > 0
                   ORDER BY engagement_rate DESC LIMIT 1""", (yesterday,)
            ).fetchone()
            if best:
                result["yesterday_best"] = {
                    "text": best["text"][:60] + "…" if len(best["text"]) > 60 else best["text"],
                    "views": best["views"],
                    "engagement_rate": best["engagement_rate"],
                }
            avg = conn.execute(
                "SELECT ROUND(AVG(engagement_rate),2) as avg FROM posts WHERE date(posted_at)=?",
                (yesterday,)
            ).fetchone()
            if avg and avg["avg"]:
                result["yesterday_avg_engagement"] = avg["avg"]
            result["pending_approvals"] = conn.execute(
                "SELECT COUNT(*) as n FROM approval_requests WHERE status='pending'"
            ).fetchone()["n"]
            result["pending_review_items"] = conn.execute(
                "SELECT COUNT(*) as n FROM review_items WHERE status='pending'"
            ).fetchone()["n"]
    except Exception:
        pass
    try:
        now = datetime.now()
        nxt = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now.hour >= 8:
            nxt += timedelta(days=1)
        diff = nxt - now
        h = int(diff.total_seconds() // 3600)
        m = int((diff.total_seconds() % 3600) // 60)
        result["next_pipeline_label"] = f"{h}h {m}m 後" if h > 0 else f"{m}m 後"
    except Exception:
        pass
    return result


@router.get("/api/morning/briefing")
async def morning_briefing():
    return _build_morning_report()


@router.get("/api/morning-report")
async def morning_report():
    return _build_morning_report()


# ── Skill Routing ──────────────────────────────────────────────────────────────

@router.get("/api/skills/routing")
async def get_skill_routing():
    """
    Machine-readable task_type → skill routing table.
    Used by Office UI for governance transparency and by orchestrator for skill loading.
    """
    from src.ai.skill_routing import get_task_skill_summary
    from src.ai.skill_loader import _cache
    return {
        "routes": get_task_skill_summary(),
        "cached_skills": sorted(_cache.keys()),
    }
