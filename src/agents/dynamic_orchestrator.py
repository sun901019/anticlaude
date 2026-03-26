"""
Dynamic Orchestrator — Phase 4
接收任意 task_type + context，路由至對應 agent 並執行。

設計原則：
- 純新增，完全不修改 orchestrator.py（固定 pipeline 不受影響）
- 路由規則從 Registry Reader 讀取（programmatic，非硬編碼）
- 每個 task_type 對應一個 handler function
- 不存在的 task_type → 回傳 unsupported 訊息而非拋出異常

使用方式：
    from src.agents.dynamic_orchestrator import run_task
    result = await run_task("content_research", {})
    result = await run_task("draft_generation", {"date_str": "2026-03-16"})
"""
import asyncio
from typing import Any

from src.registry.reader import resolve_agent, list_task_types
from src.ai.skill_loader import load_composite_skill, format_skill_block
from src.ai.skill_routing import get_skill_route
from src.utils.logger import get_logger

log = get_logger("dynamic_orchestrator")


# ── Task Handlers ─────────────────────────────────────────────────────────────
# 每個 handler 接收 context dict，回傳 {"success": bool, "data": ..., "agent": ...}

async def _handle_content_research(ctx: dict) -> dict:
    """Ori — 蒐集今日 AI 熱門文章（呼叫現有 aggregator）"""
    date_str = ctx.get("date_str")
    from src.scrapers.aggregator import run_aggregator
    articles = await run_aggregator(date_str)
    return {
        "success": True,
        "agent": "ori",
        "data": {"articles_count": len(articles), "articles": articles[:5]},  # 回傳前 5 筆預覽
    }


async def _handle_market_analysis(ctx: dict) -> dict:
    """Ori — 市場分析（搜尋 + 競品結構化）"""
    product_name = ctx.get("product_name", "")
    category = ctx.get("category", "")
    if not product_name:
        return {"success": False, "agent": "ori", "error": "需要提供 product_name"}
    from src.ai.competitor_analyzer import research_competitor
    result = research_competitor(product_name, category)
    return {"success": bool(result), "agent": "ori", "data": result}


async def _handle_topic_strategy(ctx: dict) -> dict:
    """Lala — 從已評分主題選 Top 3（先做 Orio 評分再選）"""
    scored = ctx.get("scored_topics", [])
    if not scored:
        return {"success": False, "agent": "lala", "error": "需要提供 scored_topics"}

    # Orio enrichment: add orio_score to each topic before GPT strategy picks Top 3
    try:
        from src.content.orio_scorer import score_topic
        for topic in scored:
            if "orio_score" not in topic:
                s = score_topic(topic)
                topic["orio_score"] = {
                    "topic_fit":    s.topic_fit_score,
                    "persona_fit":  s.persona_fit_score,
                    "source_trust": s.source_trust_score,
                    "composite":    s.composite_score,
                    "passed":       s.passed,
                    "reasons":      s.reasons,
                }
        log.info(f"[OrioScorer] enriched {len(scored)} topics in topic_strategy")
    except Exception as e:
        log.warning(f"[OrioScorer] enrichment failed (non-fatal): {e}")

    from src.ai.gpt_strategist import select_top3
    result = await select_top3(scored)
    return {"success": True, "agent": "lala", "data": result}


async def _handle_draft_generation(ctx: dict) -> dict:
    """Craft — 為 top3 主題生成草稿（含 GEO 驗證 + A/B 比較）"""
    top3 = ctx.get("top3", [])
    scored = ctx.get("scored_topics", [])
    date_str = ctx.get("date_str")
    run_id = ctx.get("run_id", "")
    task_id = ctx.get("task_id", "")
    geo_skill = ctx.get("_geo_skill", "")
    if not top3:
        return {"success": False, "agent": "craft", "error": "需要提供 top3 主題"}
    from src.ai.claude_writer import write_drafts
    path, drafts = await write_drafts(top3, scored, date_str, extra_skill=geo_skill)

    # GEO hard gate: validate drafts and flag non-compliant ones
    geo_report: dict = {}
    try:
        from src.content.geo_validator import validate_drafts_batch
        geo_report = validate_drafts_batch(drafts)
        if not geo_report["all_passed"]:
            failed = [r for r in geo_report["results"] if not r["passed"]]
            log.warning(
                f"[GEO Gate] {len(failed)}/{geo_report['total']} drafts failed GEO check. "
                f"Violations: {[v for r in failed for v in r['violations'][:2]]}"
            )
    except Exception as e:
        log.warning(f"[GEO Gate] validation skipped (non-fatal): {e}")

    # A/B comparison: compare first two drafts if available
    ab_result: dict = {}
    try:
        if len(drafts) >= 2:
            from src.content.ab_tester import compare_drafts
            ab = compare_drafts(drafts[0], drafts[1])
            ab_result = {
                "winner_idx": ab.winner_idx,
                "winner_score": ab.winner_score,
                "scores": ab.scores,
                "summary": ab.summary,
            }
            log.info(f"[A/B] {ab.summary}")
    except Exception as e:
        log.warning(f"[A/B] comparison skipped (non-fatal): {e}")

    # Phase 4: Memory Fabric — record artifact
    try:
        from src.workflows.runner import record_artifact
        record_artifact(
            producer="craft",
            artifact_type="draft",
            run_id=run_id,
            task_id=task_id,
            file_path=str(path),
            metadata={
                "drafts_count": len(drafts),
                "date_str": date_str or "",
                "geo_applied": bool(geo_skill),
                "geo_passed": geo_report.get("all_passed"),
                "ab_winner": ab_result.get("winner_idx"),
            },
        )
        log.info(f"[MemoryFabric] draft artifact 已記錄：{path}")
    except Exception as e:
        log.warning(f"[MemoryFabric] draft artifact 記錄失敗（不影響輸出）：{e}")

    return {
        "success": True,
        "agent": "craft",
        "data": {
            "drafts_path": path,
            "drafts_count": len(drafts),
            "geo_validation": geo_report,
            "ab_result": ab_result,
        },
    }


async def _handle_data_analysis(ctx: dict) -> dict:
    """Sage — 讀取近期貼文數據，產出分析摘要"""
    days = ctx.get("days", 30)
    from src.db.connection import db
    try:
        with db() as conn:
            rows = conn.execute(
                """SELECT post_type, AVG(engagement_rate) as avg_eng, COUNT(*) as n
                   FROM posts WHERE posted_at >= date('now', ?)
                   GROUP BY post_type ORDER BY avg_eng DESC""",
                (f"-{days} days",)
            ).fetchall()
        return {
            "success": True,
            "agent": "sage",
            "data": {
                "period_days": days,
                "by_type": [dict(r) for r in rows],
            },
        }
    except Exception as e:
        return {"success": False, "agent": "sage", "error": str(e)}


async def _handle_seo_analysis(ctx: dict) -> dict:
    """Sage — SEO / GEO 分析（placeholder，等外部工具接入）"""
    brand_url = ctx.get("brand_url", "")
    return {
        "success": True,
        "agent": "sage",
        "data": {
            "message": f"SEO 分析已排程（brand_url={brand_url}）。",
            "note": "需要接入 geo-seo-claude 工具後完整執行，目前回傳 placeholder。",
        },
    }


async def _handle_product_evaluation(ctx: dict) -> dict:
    """Sage — 選品評分"""
    candidate_id = ctx.get("candidate_id", "")
    if not candidate_id:
        return {"success": False, "agent": "sage", "error": "需要提供 candidate_id"}
    from src.db.connection import db
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM ecommerce_selection_analyses WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1",
                (candidate_id,)
            ).fetchone()
        return {
            "success": bool(row),
            "agent": "sage",
            "data": dict(row) if row else {"message": "找不到評分記錄"},
        }
    except Exception as e:
        return {"success": False, "agent": "sage", "error": str(e)}


async def _handle_copywriting(ctx: dict) -> dict:
    """Craft — 電商/廣告文案生成（單主題）"""
    topic = ctx.get("topic", "")
    product = ctx.get("product", "")
    style = ctx.get("style", "threads")
    run_id = ctx.get("run_id", "")
    task_id = ctx.get("task_id", "")

    subject = topic or product
    if not subject:
        return {"success": False, "agent": "craft", "error": "需要提供 topic 或 product 作為文案主題"}

    try:
        from src.ai.claude_writer import write_drafts
        top3 = [{"cluster_label": subject, "style": style}]
        path, drafts = await write_drafts(top3, [], date_str=None, extra_skill=ctx.get("_geo_skill", ""))
        try:
            from src.workflows.runner import record_artifact
            record_artifact(
                producer="craft",
                artifact_type="draft",
                run_id=run_id,
                task_id=task_id,
                file_path=str(path),
                metadata={"topic": subject, "style": style, "source": "copywriting", "geo_applied": bool(ctx.get("_geo_skill", ""))},
            )
        except Exception as ae:
            log.warning(f"[MemoryFabric] copywriting artifact 記錄失敗：{ae}")
        return {
            "success": True,
            "agent": "craft",
            "data": {"drafts_path": str(path), "drafts_count": len(drafts), "topic": subject},
        }
    except Exception as e:
        return {"success": False, "agent": "craft", "error": str(e)}


async def _handle_competitor_analysis(ctx: dict) -> dict:
    """Ori — 競品分析"""
    product_name = ctx.get("product_name", ctx.get("query", ""))
    category = ctx.get("category", "")
    if not product_name:
        return {"success": False, "agent": "ori", "error": "需要提供 product_name 或 query"}
    from src.ai.competitor_analyzer import research_competitor
    result = research_competitor(product_name, category)
    return {"success": bool(result), "agent": "ori", "data": result}


async def _handle_audience_analysis(ctx: dict) -> dict:
    """Lala — 受眾分析（placeholder，等外部工具接入）"""
    topic = ctx.get("topic", ctx.get("query", ""))
    return {
        "success": True,
        "agent": "lala",
        "data": {
            "topic": topic,
            "message": "受眾分析已排程。需要接入受眾洞察工具後完整執行，目前回傳 placeholder。",
        },
    }


async def _handle_content_planning(ctx: dict) -> dict:
    """Lala — 內容規劃（placeholder）"""
    return {
        "success": True,
        "agent": "lala",
        "data": {"message": "內容規劃已排程。目前回傳 placeholder，等待策略模組整合。"},
    }


async def _handle_system_debugging(ctx: dict) -> dict:
    """Lumi — 系統除錯（placeholder）"""
    issue = ctx.get("issue", ctx.get("query", ""))
    return {
        "success": True,
        "agent": "lumi",
        "data": {"issue": issue, "message": "系統除錯任務已記錄。請至 CEO Console 描述具體問題。"},
    }


async def _handle_backend_development(ctx: dict) -> dict:
    """Lumi — 後端開發（placeholder）"""
    return {
        "success": True,
        "agent": "lumi",
        "data": {"message": "後端開發任務已記錄。請至 CEO Console 描述需求。"},
    }


async def _handle_ui_implementation(ctx: dict) -> dict:
    """Lumi — 前端實作（placeholder）"""
    return {
        "success": True,
        "agent": "lumi",
        "data": {"message": "前端實作任務已記錄。請至 CEO Console 描述需求。"},
    }


async def _handle_design_evaluation(ctx: dict) -> dict:
    """Pixel — 設計評估（placeholder）"""
    return {
        "success": True,
        "agent": "pixel",
        "data": {"message": "設計評估任務已記錄。請至 CEO Console 描述評估對象。"},
    }


async def _handle_ux_review(ctx: dict) -> dict:
    """Pixel — UX 審查（placeholder）"""
    return {
        "success": True,
        "agent": "pixel",
        "data": {"message": "UX 審查任務已記錄。請至 CEO Console 描述審查範圍。"},
    }


async def _handle_unsupported(task_type: str) -> dict:
    supported = list_task_types()
    return {
        "success": False,
        "agent": "none",
        "error": f"不支援的 task_type：{task_type}",
        "supported_task_types": supported,
    }


# ── Handler Registry ──────────────────────────────────────────────────────────

HANDLERS: dict[str, Any] = {
    # ── Core pipeline tasks ───────────────────────────────────────────────────
    "content_research":    _handle_content_research,
    "market_analysis":     _handle_market_analysis,
    "competitor_analysis": _handle_competitor_analysis,
    "audience_analysis":   _handle_audience_analysis,
    "content_planning":    _handle_content_planning,
    "topic_strategy":      _handle_topic_strategy,
    "draft_generation":    _handle_draft_generation,
    "copywriting":         _handle_copywriting,
    "data_analysis":       _handle_data_analysis,
    "seo_analysis":        _handle_seo_analysis,
    "product_evaluation":  _handle_product_evaluation,
    # ── Engineering / design tasks (placeholder handlers) ─────────────────────
    "system_debugging":    _handle_system_debugging,
    "backend_development": _handle_backend_development,
    "ui_implementation":   _handle_ui_implementation,
    "design_evaluation":   _handle_design_evaluation,
    "ux_review":           _handle_ux_review,
}


# ── 主函數 ────────────────────────────────────────────────────────────────────

async def run_task(task_type: str, context: dict | None = None) -> dict:
    """
    動態執行任意 task_type。

    Args:
        task_type: 任務類型（對應 project_routing_map.md）
        context:   任務所需的輸入參數

    Returns:
        {"success": bool, "agent": str, "data": ..., "task_type": str}
    """
    ctx = dict(context or {})
    handler = HANDLERS.get(task_type)

    agent_id = resolve_agent(task_type) or "none"
    log.info(f"[DynamicOrchestrator] task={task_type} → agent={agent_id}")

    # Skill auto-inject: load all required skills for this task_type
    route = get_skill_route(task_type)
    if route:
        loaded: dict[str, str] = {}
        for skill_name in route.required_skills:
            content = load_composite_skill(skill_name)
            if content:
                loaded[skill_name] = content
        if loaded:
            ctx["_skills"] = loaded
            log.info(f"[SkillRoute] 已注入 {list(loaded)} → task={task_type}")
        # Backward-compat: keep _geo_skill key for draft_generation handler
        geo = loaded.get("geo_optimization_engine", "")
        if geo:
            ctx["_geo_skill"] = geo

    if handler is None:
        result = await _handle_unsupported(task_type)
    else:
        try:
            result = await handler(ctx)
        except Exception as e:
            log.error(f"[DynamicOrchestrator] task={task_type} 執行失敗：{e}")
            result = {"success": False, "agent": agent_id, "error": str(e)}

    result["task_type"] = task_type
    return result


def get_supported_tasks() -> dict[str, str]:
    """回傳所有支援的 task_type 及對應 agent"""
    from src.registry.reader import get_routing_map
    rmap = get_routing_map()
    return {t: rmap.get(t, "none") for t in HANDLERS}
