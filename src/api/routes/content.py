"""
Content & Media Routes
  POST /api/pipeline/run
  GET  /api/pipeline/status
  GET  /api/night-shift/status
  POST /api/night-shift/trigger
  POST /api/tracker/run
  GET  /api/tracker/status
  GET  /api/metrics
  GET  /api/library
  GET  /api/library/dates
  POST /api/weekly/run
  GET  /api/weekly/status
  GET  /api/weekly/latest
  GET  /api/weekly/list
  GET  /api/weekly/{week_id}
  POST /api/feedback/run
  GET  /api/feedback/status
  GET  /api/feedback/insights
  GET  /api/picks
  GET  /api/picks/dates
  GET  /api/articles/today
  GET  /api/articles/recent
  GET  /api/stats/monthly-ecommerce
  GET  /api/stats/posts
  POST /api/threads/publish
  GET  /api/threads/drafts
  GET  /api/content/calendar
  GET  /api/content/feedback
  GET  /api/system/logs
"""
import calendar as _cal
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from src.utils.file_io import load_daily_json, load_daily_md, load_raw_feed, list_recent_dates
from src.utils.logger import get_logger
import src.api.state as state

router = APIRouter()
log = get_logger("api.content")


# ── Pipeline ──────────────────────────────────────────────────────────────────

@router.post("/api/pipeline/run")
async def trigger_pipeline(
    background_tasks: BackgroundTasks,
    dry_run: bool = False,
    use_debate: bool = False,
):
    if state.pipeline_lock.locked():
        raise HTTPException(status_code=409, detail="Pipeline 正在執行中")

    async def _run():
        async with state.pipeline_lock:
            try:
                if dry_run:
                    from src.pipeline import run_daily_pipeline
                    await run_daily_pipeline(dry_run=True)
                else:
                    from src.agents.orchestrator import run_pipeline as orch_run
                    await orch_run(use_debate=use_debate)
                state.pipeline_last_error = ""
                state.pipeline_last_error_at = ""
                state.pipeline_last_success_at = datetime.now().isoformat()
            except Exception as e:
                state.pipeline_last_error = str(e)
                state.pipeline_last_error_at = datetime.now().isoformat()
                log.error(f"[手動觸發] pipeline 失敗：{e}")

    background_tasks.add_task(_run)
    return {"status": "started", "dry_run": dry_run, "use_debate": use_debate}


@router.post("/api/pipeline/graph-run")
async def trigger_graph_pipeline(
    background_tasks: BackgroundTasks,
    date: str | None = None,
    approval_gate: bool = True,
    deliberation: bool = False,
):
    """Phase 7: Run the daily pipeline as a graph workflow (checkpoint/resume capable)."""
    if state.pipeline_lock.locked():
        raise HTTPException(status_code=409, detail="Pipeline 正在執行中")

    async def _run():
        async with state.pipeline_lock:
            try:
                from src.workflows.pipeline_graph import run_content_pipeline
                result = await run_content_pipeline(
                    date_str=date,
                    with_approval_gate=approval_gate,
                    deliberation=deliberation,
                )
                state.pipeline_last_success_at = datetime.now().isoformat()
                state.pipeline_last_error = ""
                state.pipeline_last_error_at = ""
                log.info(f"[GraphPipeline] run_id={result.get('run_id')} paused_at={result.get('paused_at')}")
            except Exception as e:
                state.pipeline_last_error = str(e)
                state.pipeline_last_error_at = datetime.now().isoformat()
                log.error(f"[GraphPipeline] 失敗：{e}")

    background_tasks.add_task(_run)
    return {"status": "started", "mode": "graph", "approval_gate": approval_gate, "deliberation": deliberation}


@router.post("/api/pipeline/resume/{run_id}")
async def resume_graph_pipeline(
    run_id: str,
    background_tasks: BackgroundTasks,
):
    """Resume a paused graph workflow run after human approval."""
    if state.pipeline_lock.locked():
        raise HTTPException(status_code=409, detail="Pipeline 正在執行中")

    async def _run():
        async with state.pipeline_lock:
            try:
                from src.workflows.pipeline_graph import run_content_pipeline
                result = await run_content_pipeline(resume_run_id=run_id)
                state.pipeline_last_success_at = datetime.now().isoformat()
                state.pipeline_last_error = ""
                state.pipeline_last_error_at = ""
                log.info(f"[GraphPipeline] Resumed {run_id} → paused_at={result.get('paused_at')}")
            except Exception as e:
                state.pipeline_last_error = str(e)
                state.pipeline_last_error_at = datetime.now().isoformat()
                log.error(f"[GraphPipeline] Resume 失敗：{e}")

    background_tasks.add_task(_run)
    return {"status": "resuming", "run_id": run_id}


@router.get("/api/pipeline/status")
async def pipeline_status():
    return {
        "running": state.pipeline_lock.locked(),
        "last_error": state.pipeline_last_error,
        "last_error_at": state.pipeline_last_error_at,
        "last_success_at": state.pipeline_last_success_at,
    }


# ── Night Shift ───────────────────────────────────────────────────────────────

@router.get("/api/night-shift/status")
async def night_shift_status():
    from src.agents.night_shift import get_last_night_shift
    stored = state.night_shift_last_result or {}
    file_result = get_last_night_shift()
    return {
        "running": state.night_shift_lock.locked(),
        "last_result": stored or file_result,
    }


@router.post("/api/night-shift/trigger")
async def trigger_night_shift(background_tasks: BackgroundTasks):
    if state.night_shift_lock.locked():
        raise HTTPException(status_code=409, detail="夜班正在執行中")

    async def _run():
        async with state.night_shift_lock:
            try:
                from src.agents.night_shift import run_night_shift
                state.night_shift_last_result = await run_night_shift()
            except Exception as e:
                log.error(f"[手動夜班] 失敗：{e}")
                state.night_shift_last_result = {"error": str(e)}

    background_tasks.add_task(_run)
    return {"status": "started"}


# ── Tracker ───────────────────────────────────────────────────────────────────

@router.post("/api/tracker/run")
async def run_tracker(background_tasks: BackgroundTasks):
    if state.tracker_lock.locked():
        raise HTTPException(status_code=409, detail="Tracker 正在執行中")

    async def _run():
        async with state.tracker_lock:
            from src.tracker.metrics_collector import collect_metrics
            await collect_metrics()

    background_tasks.add_task(_run)
    return {"status": "started"}


@router.get("/api/tracker/status")
async def tracker_status():
    return {"running": state.tracker_lock.locked()}


@router.get("/api/metrics")
async def get_metrics(days: int = 30):
    dates = list_recent_dates("threads_metrics", days)
    seen: dict[str, dict] = {}
    for d in sorted(dates):
        data = load_daily_json("threads_metrics", d)
        if data and isinstance(data, list):
            for item in data:
                pid = item.get("post_id")
                if pid:
                    seen[pid] = item
    all_metrics = list(seen.values())
    return {"data": all_metrics, "count": len(all_metrics)}


# ── Library ───────────────────────────────────────────────────────────────────

@router.get("/api/library")
async def get_library(date: str | None = None):
    d = date or datetime.now().strftime("%Y-%m-%d")
    raw = load_raw_feed(d)
    return {"date": d, "articles": raw or [], "count": len(raw) if raw else 0}


@router.get("/api/library/dates")
async def get_library_dates():
    from src.config import RAW_FEED_DIR
    files = sorted(RAW_FEED_DIR.glob("raw_feed_*.json"), reverse=True)
    dates = [f.stem.replace("raw_feed_", "") for f in files]
    return {"dates": dates}


# ── Weekly Report ─────────────────────────────────────────────────────────────

@router.post("/api/weekly/run")
async def run_weekly(background_tasks: BackgroundTasks):
    if state.weekly_lock.locked():
        raise HTTPException(status_code=409, detail="週報生成中")

    async def _run():
        async with state.weekly_lock:
            from src.weekly.weekly_report import generate_weekly_report
            await generate_weekly_report()

    background_tasks.add_task(_run)
    return {"status": "started"}


@router.get("/api/weekly/status")
async def weekly_status():
    return {"running": state.weekly_lock.locked()}


@router.get("/api/weekly/latest")
async def get_latest_weekly():
    from src.config import WEEKLY_REPORTS_DIR
    import os as _os
    files = sorted(WEEKLY_REPORTS_DIR.glob("week_*.md"), reverse=True)
    if not files:
        return {"content": None, "last_generated_at": None}
    mtime = _os.path.getmtime(files[0])
    last_gen = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
    return {"week": files[0].stem, "content": files[0].read_text(encoding="utf-8"), "last_generated_at": last_gen}


@router.get("/api/weekly/list")
async def list_weekly():
    from src.config import WEEKLY_REPORTS_DIR
    files = sorted(WEEKLY_REPORTS_DIR.glob("week_*.md"), reverse=True)
    return {"reports": [f.stem for f in files]}


@router.get("/api/weekly/{week_id}")
async def get_weekly(week_id: str):
    from src.config import WEEKLY_REPORTS_DIR
    path = WEEKLY_REPORTS_DIR / f"{week_id}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="週報不存在")
    return {"week": week_id, "content": path.read_text(encoding="utf-8")}


# ── Feedback Analysis ─────────────────────────────────────────────────────────

@router.post("/api/feedback/run")
async def run_feedback(background_tasks: BackgroundTasks, days: int = 30):
    if state.feedback_lock.locked():
        raise HTTPException(status_code=409, detail="回饋分析正在執行中")

    async def _run():
        async with state.feedback_lock:
            from src.feedback.analysis_engine import run_feedback_analysis
            await run_feedback_analysis(days=days)

    background_tasks.add_task(_run)
    return {"status": "started", "days": days}


@router.get("/api/feedback/status")
async def feedback_status():
    return {"running": state.feedback_lock.locked()}


@router.get("/api/feedback/insights")
async def get_insights():
    from src.feedback.analysis_engine import get_latest_insights
    data = get_latest_insights()
    return {"insights": data}


# ── Picks ─────────────────────────────────────────────────────────────────────

@router.get("/api/picks")
async def get_picks(date: str | None = None):
    d = date or datetime.now().strftime("%Y-%m-%d")
    structured = load_daily_json("daily_reports", d)
    if not structured:
        return {"date": d, "picks": [], "top3_labels": []}
    all_topics = structured.get("all_topics", [])
    picks = sorted(all_topics, key=lambda x: x.get("score", 0), reverse=True)
    top3_labels = [t["cluster_label"] for t in structured.get("top3", [])]
    return {"date": d, "picks": picks, "top3_labels": top3_labels}


@router.get("/api/picks/dates")
async def get_picks_dates():
    from src.config import DAILY_REPORTS_DIR
    files = sorted(DAILY_REPORTS_DIR.glob("*.json"), reverse=True)
    dates = [f.stem for f in files]
    return {"dates": dates}


# ── Articles ──────────────────────────────────────────────────────────────────

@router.get("/api/articles/today")
async def get_today_articles(limit: int = 30):
    try:
        from src.db.connection import db
        with db() as conn:
            rows = conn.execute(
                """SELECT title, url, source, summary, language, published_at, scraped_at
                   FROM articles
                   WHERE date(scraped_at) = date('now')
                   ORDER BY scraped_at DESC LIMIT ?""",
                (limit,)
            ).fetchall()
        return {"date": datetime.now().strftime("%Y-%m-%d"), "articles": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        log.error(f"取得今日素材失敗：{e}")
        return {"date": datetime.now().strftime("%Y-%m-%d"), "articles": [], "count": 0}


@router.get("/api/articles/recent")
async def get_recent_articles(days: int = 3, limit: int = 50):
    try:
        from src.db.connection import db
        with db() as conn:
            rows = conn.execute(
                """SELECT title, url, source, summary, language, published_at, scraped_at
                   FROM articles
                   WHERE date(scraped_at) >= date('now', ?)
                   ORDER BY scraped_at DESC LIMIT ?""",
                (f"-{days} days", limit)
            ).fetchall()
        return {"days": days, "articles": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        log.error(f"取得近期素材失敗：{e}")
        return {"days": days, "articles": [], "count": 0}


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/api/stats/monthly-ecommerce")
async def get_monthly_ecommerce():
    try:
        from src.db.connection import db
        from src.ecommerce.router import calc_full_cost, _get_settings
        cfg = _get_settings()
        with db() as conn:
            products = conn.execute(
                "SELECT * FROM fl_products WHERE status NOT IN ('stopped','archived')"
            ).fetchall()
            perf_rows = conn.execute("""
                SELECT p1.* FROM fl_performance p1
                INNER JOIN (
                    SELECT sku, MAX(record_date) as max_date FROM fl_performance GROUP BY sku
                ) p2 ON p1.sku = p2.sku AND p1.record_date = p2.max_date
            """).fetchall()
            perf_map = {r["sku"]: dict(r) for r in perf_rows}
            inv_rows = conn.execute(
                "SELECT sku, COALESCE(SUM(quantity),0) as total FROM fl_inventory GROUP BY sku"
            ).fetchall()
            inv_map = {r["sku"]: r["total"] for r in inv_rows}

        result = []
        total_revenue = 0
        total_profit = 0
        for p in products:
            pd = dict(p)
            sku = pd["sku"]
            perf = perf_map.get(sku, {})
            stock = inv_map.get(sku, 0)
            sales_7d = perf.get("sales_7d", 0)
            revenue_7d = perf.get("revenue_7d", 0)
            ad_spend_7d = perf.get("ad_spend_7d", 0)
            current_price = perf.get("current_price") or pd.get("target_price") or 0
            daily_sales = sales_7d / 7 if sales_7d else 0
            days_left = round(stock / daily_sales) if daily_sales > 0 else None
            cost_info = {}
            if pd.get("cost_rmb") and current_price:
                cost_info = calc_full_cost(
                    pd["cost_rmb"], current_price, cfg,
                    weight_kg=pd.get("weight_kg") or 0,
                    packaging_cost=pd.get("packaging_cost") or 0,
                    head_freight_rmb=pd.get("head_freight_rmb") or 0,
                )
            gross_margin = cost_info.get("gross_margin", perf.get("gross_margin") or 0)
            safe_cpa = cost_info.get("safe_cpa", 0)
            roas = round(revenue_7d / ad_spend_7d, 2) if ad_spend_7d and ad_spend_7d > 0 else None
            total_revenue += revenue_7d
            total_profit += cost_info.get("profit", 0) * sales_7d if cost_info else 0
            result.append({
                "sku": sku, "name": pd["name"], "role": pd.get("role"),
                "status": pd.get("status"),
                "revenue_7d": round(revenue_7d, 0),
                "sales_7d": sales_7d,
                "ad_spend_7d": round(ad_spend_7d, 0),
                "gross_margin": round(gross_margin, 4),
                "safe_cpa": round(safe_cpa, 0),
                "roas": roas,
                "stock": stock,
                "days_left": days_left,
                "current_price": current_price,
            })
        result.sort(key=lambda x: x["revenue_7d"], reverse=True)
        return {
            "total_revenue_7d": round(total_revenue, 0),
            "total_profit_est": round(total_profit, 0),
            "product_count": len(result),
            "products": result,
        }
    except Exception as e:
        log.error(f"取得電商績效失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats/posts")
async def get_post_stats(days: int = 30):
    try:
        from src.db.schema import init_db
        from src.db.queries import get_post_stats, get_top_hooks
        init_db()
        stats = get_post_stats(days=days)
        hooks = get_top_hooks(limit=10)
        return {"stats": stats, "top_hooks": hooks, "days": days}
    except Exception as e:
        log.error(f"取得貼文統計失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Threads ───────────────────────────────────────────────────────────────────

class ThreadsPublishBody(BaseModel):
    text: str
    draft_id: int | None = None


@router.post("/api/threads/publish")
async def threads_publish(body: ThreadsPublishBody):
    try:
        from src.config import settings
        from src.db.connection import db
        text = body.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="貼文內容不能為空")

        import httpx
        url = f"https://graph.threads.net/v1.0/{settings.threads_user_id}/threads"
        params = {"media_type": "TEXT", "text": text, "access_token": settings.threads_access_token}
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, params=params)
            if r.status_code != 200:
                raise HTTPException(status_code=r.status_code, detail=f"Threads API 錯誤：{r.text}")
            creation_id = r.json().get("id")

        pub_url = f"https://graph.threads.net/v1.0/{settings.threads_user_id}/threads_publish"
        pub_params = {"creation_id": creation_id, "access_token": settings.threads_access_token}
        async with httpx.AsyncClient(timeout=30) as client:
            r2 = await client.post(pub_url, params=pub_params)
            if r2.status_code != 200:
                raise HTTPException(status_code=r2.status_code, detail=f"Threads publish 失敗：{r2.text}")
            post_id = r2.json().get("id")

        published_at = datetime.now().isoformat()
        if body.draft_id:
            with db() as conn:
                conn.execute(
                    "UPDATE drafts SET published_at=?, threads_post_id=? WHERE id=?",
                    (published_at, post_id, body.draft_id),
                )
                conn.execute(
                    "UPDATE drafts SET was_selected=1 WHERE id=? AND was_selected=0",
                    (body.draft_id,),
                )
                draft_row = conn.execute("SELECT * FROM drafts WHERE id=?", (body.draft_id,)).fetchone()
                if draft_row:
                    conn.execute(
                        """INSERT OR IGNORE INTO posts
                           (threads_id, text, posted_at, category, post_type)
                           VALUES (?,?,?,?,?)""",
                        (post_id, text, published_at,
                         draft_row["style"] or "general",
                         draft_row["style"] or "一般"),
                    )
            try:
                from src.api.agent_status import update_agent_task
                update_agent_task(
                    "craft", status="idle", task="",
                    title="草稿已發布，等待下次任務",
                    task_type="一般", priority="normal",
                    source_agent_id="", target_agent_id="",
                )
            except Exception:
                pass

        return {"ok": True, "post_id": post_id, "published_at": published_at}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Threads 發布失敗：{e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/threads/drafts")
async def get_publishable_drafts(limit: int = 5):
    """Return today's unpublished drafts first; fall back to most recent if none today."""
    from datetime import date as _date
    today = _date.today().isoformat()
    try:
        from src.db.connection import db
        with db() as conn:
            rows = conn.execute(
                """SELECT id, date, style, content, hook, hashtags, created_at
                   FROM drafts
                   WHERE (published_at IS NULL OR published_at = '')
                     AND date = ?
                   ORDER BY created_at DESC LIMIT ?""",
                (today, limit)
            ).fetchall()
            if not rows:
                rows = conn.execute(
                    """SELECT id, date, style, content, hook, hashtags, created_at
                       FROM drafts
                       WHERE (published_at IS NULL OR published_at = '')
                       ORDER BY created_at DESC LIMIT ?""",
                    (limit,)
                ).fetchall()
        return {"drafts": [dict(r) for r in rows]}
    except Exception as e:
        log.error(f"取得可發布草稿失敗：{e}")
        return {"drafts": []}


class DraftUpdate(BaseModel):
    content: str


@router.patch("/api/drafts/{draft_id}")
async def update_draft(draft_id: int, body: DraftUpdate):
    """直接編輯草稿內容（人工修改後存回 DB）。"""
    try:
        from src.db.connection import db
        with db() as conn:
            cur = conn.execute(
                "UPDATE drafts SET content=? WHERE id=?",
                (body.content, draft_id),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="Draft not found")
        return {"ok": True, "id": draft_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class DraftRegenerate(BaseModel):
    hint: str = ""   # 使用者補充的關鍵字或方向提示


@router.post("/api/drafts/{draft_id}/regenerate")
async def regenerate_draft(draft_id: int, body: DraftRegenerate = DraftRegenerate()):
    """
    重新生成指定草稿。
    取出原始 topic 資料 → 重新呼叫 write_drafts → 更新 DB 內容。
    body.hint: 使用者可補充關鍵字或方向（e.g. "加入個人故事、強調實用性"）
    """
    try:
        from src.db.connection import db
        with db() as conn:
            row = conn.execute(
                """SELECT d.id, d.style, d.topic_id, d.date,
                          t.cluster_label as topic_label,
                          t.key_insights  as topic_summary,
                          t.category      as post_type
                   FROM drafts d
                   LEFT JOIN topics t ON t.id = d.topic_id
                   WHERE d.id=?""",
                (draft_id,),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Draft not found")

        draft = dict(row)
        topic_label   = draft.get("topic_label") or "未知主題"
        topic_summary = draft.get("topic_summary") or topic_label
        post_type     = draft.get("post_type") or "趨勢解讀"
        style         = draft.get("style") or "資訊型"
        date_str      = draft.get("date")

        if body.hint.strip():
            topic_summary = f"{topic_summary}\n\n【CEO 補充方向】{body.hint.strip()}"

        from src.domains.media.writer import write_drafts
        topic_input = {
            "cluster_label": topic_label,
            "post_type":     post_type,
            "merged_summary": topic_summary,
        }
        _, drafts_out = await write_drafts([topic_input], [], date_str=date_str)

        if not drafts_out:
            raise HTTPException(status_code=500, detail="Writer returned no drafts")

        first = drafts_out[0]
        # Pick version matching the draft's style
        ver = first.get("version_b" if "故事" in style else "version_a") \
              or first.get("version_a") \
              or {}
        new_content = ver.get("content", "") if isinstance(ver, dict) else ""
        if not new_content:
            raise HTTPException(status_code=500, detail="Writer returned empty content")

        with db() as conn:
            conn.execute("UPDATE drafts SET content=? WHERE id=?", (new_content, draft_id))

        return {"ok": True, "id": draft_id, "content": new_content}

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Regenerate draft {draft_id} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Content Calendar & Feedback ───────────────────────────────────────────────

@router.get("/api/content/calendar")
async def get_content_calendar(year: int | None = None, month: int | None = None):
    try:
        from src.db.connection import db
        now = datetime.now()
        y = year or now.year
        m = month or now.month
        _, days_in_month = _cal.monthrange(y, m)
        month_str = f"{y}-{m:02d}"

        with db() as conn:
            published_rows = conn.execute(
                """SELECT date(published_at) as d, COUNT(*) as cnt
                   FROM drafts WHERE published_at IS NOT NULL AND published_at != ''
                   AND strftime('%Y-%m', published_at) = ? GROUP BY d""", (month_str,)
            ).fetchall()
            draft_rows = conn.execute(
                """SELECT date, COUNT(*) as cnt FROM drafts
                   WHERE strftime('%Y-%m', date) = ? GROUP BY date""", (month_str,)
            ).fetchall()

        published_dates = {r["d"] for r in published_rows}
        draft_dates = {r["date"] for r in draft_rows}
        days = {}
        for d in range(1, days_in_month + 1):
            date_str = f"{y}-{m:02d}-{d:02d}"
            if date_str in published_dates:
                days[date_str] = "published"
            elif date_str in draft_dates:
                days[date_str] = "draft"
            else:
                days[date_str] = "empty"
        return {"year": y, "month": m, "days": days}
    except Exception as e:
        log.error(f"取得內容日曆失敗：{e}")
        return {"year": year, "month": month, "days": {}}


@router.get("/api/content/feedback")
async def get_content_feedback(days: int = 90):
    try:
        from src.db.connection import db
        with db() as conn:
            category_rows = conn.execute(
                """SELECT p.category,
                          COUNT(*) as post_count,
                          ROUND(AVG(p.engagement_rate), 4) as avg_engagement,
                          ROUND(AVG(p.likes), 1) as avg_likes,
                          ROUND(AVG(p.views), 0) as avg_views,
                          ROUND(AVG(p.replies), 1) as avg_replies
                   FROM posts p
                   WHERE p.posted_at >= date('now', ?)
                     AND p.category IS NOT NULL AND p.category != ''
                   GROUP BY p.category ORDER BY avg_engagement DESC""",
                (f"-{days} days",)
            ).fetchall()
            daily_rows = conn.execute(
                """SELECT date(posted_at) as d, COUNT(*) as posts,
                          ROUND(AVG(engagement_rate), 4) as avg_eng
                   FROM posts WHERE posted_at >= date('now', ?)
                   GROUP BY d ORDER BY d""",
                (f"-{days} days",)
            ).fetchall()
            top_rows = conn.execute(
                """SELECT threads_id, text, posted_at, category,
                          views, likes, replies, engagement_rate
                   FROM posts WHERE posted_at >= date('now', ?)
                   ORDER BY engagement_rate DESC LIMIT 5""",
                (f"-{days} days",)
            ).fetchall()
        return {
            "days": days,
            "by_category": [dict(r) for r in category_rows],
            "daily_trend": [dict(r) for r in daily_rows],
            "top_posts": [dict(r) for r in top_rows],
        }
    except Exception as e:
        log.error(f"取得內容回饋失敗：{e}")
        return {"days": days, "by_category": [], "daily_trend": [], "top_posts": []}


# ── System Logs ───────────────────────────────────────────────────────────────

@router.get("/api/system/logs")
async def get_system_logs(lines: int = 100, level: str = "ERROR"):
    try:
        from src.config import LOGS_DIR
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = LOGS_DIR / f"{today}.log"
        if not log_file.exists():
            return {"logs": [], "date": today}
        level_upper = level.upper()
        entries = []
        for line in log_file.read_text(encoding="utf-8").splitlines()[-500:]:
            if level_upper == "ALL" or f"| {level_upper}" in line or "| ERROR" in line or "| WARNING" in line:
                entries.append(line)
        return {"logs": entries[-lines:], "date": today, "file": str(log_file)}
    except Exception as e:
        return {"logs": [str(e)], "date": ""}


# ── Competitor Tracker ─────────────────────────────────────────────────────────

@router.post("/api/competitor/price-check")
async def competitor_price_check(body: dict):
    from src.scrapers.competitor_tracker import run_price_check_and_notify
    keywords = body.get("keywords", [])
    return await run_price_check_and_notify(keywords)
