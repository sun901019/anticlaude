"""
FastAPI 後端 — App Assembly
============================
啟動：uvicorn src.api.main:app --port 8000

This file is intentionally thin:
  - app creation, CORS, lifespan
  - APScheduler setup (references src.api.state for shared globals)
  - include_router for all route modules

Business logic lives in src/api/routes/*.py
"""
import sys

# Force UTF-8 output on Windows (CP950 console causes mojibake in logs)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from src.utils.logger import get_logger
import src.api.state as state

log = get_logger("api")

scheduler = AsyncIOScheduler(timezone="Asia/Taipei")


# ── Scheduler helpers ─────────────────────────────────────────────────────────

def _emit_schedule_event(agent_id: str, task: str) -> None:
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            agent_id, status="working", task=task, title=task,
            task_type="一般", priority="normal",
            source_agent_id="", target_agent_id="",
        )
    except Exception:
        pass


async def _scheduled_pipeline():
    log.info("[排程] 每日 pipeline 開始...")
    _emit_schedule_event("ori", "每日內容 Pipeline 啟動（排程）")
    try:
        from src.domains.media.pipeline_graph import run_content_pipeline
        result = await run_content_pipeline(with_approval_gate=True)
        state.pipeline_last_error = ""
        state.pipeline_last_error_at = ""
        state.pipeline_last_success_at = datetime.now().isoformat()
        try:
            from src.utils.notify import send_line_notify
            paused_at = result.get("paused_at")
            outputs = result.get("outputs_summary", {})
            strategy_out = outputs.get("strategy", {})
            top3 = strategy_out.get("top3", [])
            topics_str = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(top3[:3])) if top3 else "  （無主題資料）"
            if paused_at:
                msg = f"[AntiClaude] 草稿已就緒，等待你審核\n今日主題：\n{topics_str}\n\n請至 /review 審核後發布"
            else:
                msg = f"[AntiClaude] Pipeline 完成\n今日主題：\n{topics_str}"
            await send_line_notify(msg)
        except Exception:
            pass
    except Exception as e:
        state.pipeline_last_error = str(e)
        state.pipeline_last_error_at = datetime.now().isoformat()
        log.error(f"[排程] pipeline 失敗：{e}")
        try:
            from src.utils.notify import send_line_notify
            await send_line_notify(f"[AntiClaude] Pipeline 失敗：{e}")
        except Exception:
            pass


async def _scheduled_tracker():
    log.info("[排程] 每日 Threads 數據抓取 + 競品價格監控...")
    _emit_schedule_event("sage", "每日 Threads 數據抓取（排程）")
    try:
        from src.tracker.metrics_collector import collect_metrics
        await collect_metrics()
    except Exception as e:
        log.error(f"[排程] tracker 失敗：{e}")

    # 競品價格監控：若有降價 >10% 自動 LINE 通知
    try:
        from src.scrapers.competitor_tracker import run_price_check_and_notify
        from src.config import settings
        keywords = getattr(settings, "competitor_keywords", None) or []
        if keywords:
            result = await run_price_check_and_notify(keywords)
            log.info(f"[排程] 競品監控完成：{result}")
        else:
            log.info("[排程] 競品監控跳過：未設定 competitor_keywords")
    except Exception as e:
        log.warning(f"[排程] 競品監控失敗（不影響 tracker）：{e}")


async def _scheduled_weekly():
    log.info("[排程] 每週週報生成...")
    _emit_schedule_event("craft", "每週週報生成（排程）")
    try:
        from src.weekly.weekly_report import generate_weekly_report
        await generate_weekly_report()
    except Exception as e:
        log.error(f"[排程] 週報失敗：{e}")


async def _scheduled_night_shift():
    if state.night_shift_lock.locked():
        log.warning("[排程] 夜班已在執行中，跳過")
        return
    log.info("[排程] 夜班開始...")
    _emit_schedule_event("ori", "夜班自治推進（排程）")
    async with state.night_shift_lock:
        try:
            from src.agents.night_shift import run_night_shift
            state.night_shift_last_result = await run_night_shift()
        except Exception as e:
            log.error(f"[排程] 夜班失敗：{e}")
            state.night_shift_last_result = {"error": str(e), "date": datetime.now().strftime("%Y-%m-%d")}


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(_app: FastAPI):
    scheduler.add_job(_scheduled_pipeline, CronTrigger(hour=8, minute=0),
                      id="daily_pipeline", replace_existing=True)
    scheduler.add_job(_scheduled_tracker, CronTrigger(hour=20, minute=0),
                      id="daily_tracker", replace_existing=True)
    scheduler.add_job(_scheduled_weekly, CronTrigger(day_of_week="mon", hour=9, minute=0),
                      id="weekly_report", replace_existing=True)
    scheduler.add_job(_scheduled_night_shift, CronTrigger(hour=22, minute=0),
                      id="night_shift", replace_existing=True)
    scheduler.start()
    log.info("排程已啟動：pipeline@08:00 / tracker@20:00 / weekly@週一09:00 / night_shift@22:00")
    try:
        from src.api.agent_status import restore_today_state
        restore_today_state()
        log.info("Agent 今日狀態已恢復")
    except Exception as e:
        log.warning(f"Agent 狀態恢復失敗（不影響運作）：{e}")
    yield
    scheduler.shutdown()


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(title="AntiClaude API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

# Existing domain router
from src.ecommerce.router import router as ecommerce_router
app.include_router(ecommerce_router, prefix="/api/ecommerce")

# New modular route files
from src.api.routes.health import router as health_router
from src.api.routes.content import router as content_router
from src.api.routes.ecommerce_extra import router as ecommerce_extra_router
from src.api.routes.agents import router as agents_router
from src.api.routes.review import router as review_router
from src.api.routes.chat import router as chat_router
from src.api.routes.workflows import router as workflows_router
from src.api.routes.flowlab import router as flowlab_router
from src.api.routes.figma import router as figma_router

app.include_router(health_router)
app.include_router(content_router)
app.include_router(ecommerce_extra_router)
app.include_router(agents_router)
app.include_router(review_router)
app.include_router(chat_router)
app.include_router(workflows_router)
app.include_router(flowlab_router)
app.include_router(figma_router)
