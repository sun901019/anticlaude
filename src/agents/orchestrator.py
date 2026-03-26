"""
Orchestrator for the daily AntiClaude pipeline.

This module keeps the existing business flow but also emits structured
AI Office task updates so the office view reflects the real pipeline.
"""

from __future__ import annotations

from datetime import datetime

from src.agents.cluster import ClusterAgent
from src.agents.debate import DebateAgent
from src.agents.judge import JudgeAgent
from src.agents.score import ScoreAgent
from src.agents.strategy import StrategyAgent
from src.agents.writer import WriterAgent
from src.api.agent_status import mark_agent_awaiting_human
from src.utils.file_io import save_daily_json
from src.utils.logger import get_logger

log = get_logger("orchestrator")


def _safe_emit(
    emit,
    agent_id: str,
    *,
    status: str,
    task: str,
    task_type: str,
    source_agent_id: str = "",
    target_agent_id: str = "",
    artifact_refs: list[str] | None = None,
) -> None:
    try:
        emit(
            agent_id,
            status=status,
            task=task,
            title=task,
            task_type=task_type,
            priority="high" if status == "working" else "normal",
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            artifact_refs=artifact_refs or [],
        )
    except TypeError:
        # Fallback for older signature compatibility if needed.
        emit(agent_id, status, task)


async def run_pipeline(date_str: str | None = None, use_debate: bool = False) -> dict:
    """
    Run the full daily agent pipeline.

    Returns:
        {"date", "articles_count", "clusters_count", "top3", "drafts_path", "model_log"}
    """
    d = date_str or datetime.now().strftime("%Y-%m-%d")
    model_log: dict[str, str] = {}

    log.info(f"[Orchestrator] Starting pipeline for {d}")

    try:
        from src.api.agent_status import update_agent_task as emit_task
    except Exception:
        def emit_task(*args, **kwargs) -> None:  # type: ignore
            pass

    from src.scrapers.aggregator import run_aggregator

    _safe_emit(
        emit_task,
        "ori",
        status="working",
        task="蒐集 AI 新聞與研究訊號",
        task_type="research",
        target_agent_id="lala",
    )
    try:
        articles = await run_aggregator(d)
    except Exception as exc:
        _safe_emit(emit_task, "ori", status="idle", task="", task_type="research")
        log.exception(f"Aggregator crashed: {exc}")
        return {}
    if not articles:
        _safe_emit(emit_task, "ori", status="idle", task="", task_type="research")
        log.error("No articles collected; pipeline aborted.")
        return {}

    log.info(f"Collected {len(articles)} articles")

    recent_labels: list[str] = []
    try:
        from src.db.queries import get_recent_topic_labels

        recent_labels = get_recent_topic_labels(days=7)
    except Exception as exc:
        log.warning(f"Failed to load recent topic labels: {exc}")

    _safe_emit(
        emit_task,
        "ori",
        status="working",
        task=f"整理 {len(articles)} 筆研究訊號並進行分群",
        task_type="research",
        target_agent_id="lala",
    )
    try:
        cluster_result = await ClusterAgent().run(articles, recent_labels=recent_labels)
    except Exception as exc:
        _safe_emit(emit_task, "ori", status="idle", task="", task_type="research")
        log.exception(f"ClusterAgent crashed: {exc}")
        return {}
    _safe_emit(emit_task, "ori", status="idle", task="", task_type="research")
    if not cluster_result.success:
        log.error(f"ClusterAgent failed: {cluster_result.error}")
        return {}

    clusters: list[dict] = cluster_result.data
    model_log["cluster"] = cluster_result.model_used

    _safe_emit(
        emit_task,
        "lala",
        status="working",
        task=f"評估 {len(clusters)} 組主題並準備選題",
        task_type="strategy",
        source_agent_id="ori",
        target_agent_id="craft",
    )
    try:
        score_result = await ScoreAgent().run(clusters)
    except Exception as exc:
        _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
        log.exception(f"ScoreAgent crashed: {exc}")
        return {}
    _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
    if not score_result.success:
        log.error(f"ScoreAgent failed: {score_result.error}")
        return {}

    scored: list[dict] = score_result.data
    model_log["score"] = score_result.model_used

    weekly_insight = ""
    debate_summary = ""

    if use_debate:
        log.info("[Orchestrator] Running debate selection flow")
        _safe_emit(
            emit_task,
            "lala",
            status="working",
            task="進行辯論式選題比較",
            task_type="strategy",
            source_agent_id="ori",
            target_agent_id="craft",
        )
        try:
            debate_result = await DebateAgent().run(scored)
        except Exception as exc:
            _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
            log.exception(f"DebateAgent crashed: {exc}")
            return {}
        if not debate_result.success:
            _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
            log.warning(f"DebateAgent failed, falling back to standard strategy flow: {debate_result.error}")
            use_debate = False
        else:
            model_log["debate"] = debate_result.model_used
            _safe_emit(
                emit_task,
                "lala",
                status="working",
                task="整合辯論結果並判定最終選題",
                task_type="strategy",
                source_agent_id="ori",
                target_agent_id="craft",
            )
            try:
                judge_result = await JudgeAgent().run(debate_result.data)
            except Exception as exc:
                _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
                log.exception(f"JudgeAgent crashed: {exc}")
                return {}
            _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
            if not judge_result.success:
                log.warning(f"JudgeAgent failed, falling back to standard strategy flow: {judge_result.error}")
                use_debate = False
            else:
                judged: dict = judge_result.data
                top3 = judged.get("top3", [])
                weekly_insight = judged.get("weekly_insight", "")
                debate_summary = judged.get("debate_summary", "")
                model_log["judge"] = judge_result.model_used

    if not use_debate:
        _safe_emit(
            emit_task,
            "lala",
            status="working",
            task="選出今日內容主題與策略角度",
            task_type="strategy",
            source_agent_id="ori",
            target_agent_id="craft",
        )
        try:
            strategy_result = await StrategyAgent().run(scored)
        except Exception as exc:
            _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
            log.exception(f"StrategyAgent crashed: {exc}")
            return {}
        _safe_emit(emit_task, "lala", status="idle", task="", task_type="strategy")
        if not strategy_result.success:
            log.error(f"StrategyAgent failed: {strategy_result.error}")
            return {}
        strategy: dict = strategy_result.data
        top3 = strategy.get("top3", [])
        weekly_insight = strategy.get("weekly_insight", "")
        model_log["strategy"] = strategy_result.model_used

    _safe_emit(
        emit_task,
        "craft",
        status="working",
        task=f"為 {len(top3)} 個主題撰寫 Threads 草稿",
        task_type="content",
        source_agent_id="lala",
        target_agent_id="pixel",
    )
    try:
        writer_result = await WriterAgent().run(top3, scored, d)
    except Exception as exc:
        _safe_emit(
            emit_task,
            "craft",
            status="idle",
            task="",
            task_type="content",
            source_agent_id="lala",
            target_agent_id="pixel",
        )
        log.exception(f"WriterAgent crashed: {exc}")
        return {}
    if not writer_result.success:
        log.warning(f"WriterAgent failed: {writer_result.error}; continuing without drafts")
        drafts_list = []
        drafts_path = ""
    else:
        drafts_list = writer_result.data["drafts_list"]
        drafts_path = writer_result.data["drafts_path"]
        model_log["write"] = writer_result.model_used
    if drafts_path:
        mark_agent_awaiting_human(
            "craft",
            message=f"草稿已完成（{len(drafts_list)} 篇），請選擇發文內容",
            action_type="select_draft",
            ref_id=d,
            artifact_refs=[f"outputs/drafts/{d}.md"],
        )
    else:
        _safe_emit(
            emit_task,
            "craft",
            status="idle",
            task="",
            task_type="content",
            source_agent_id="lala",
            target_agent_id="pixel",
        )

    topic_map = {topic["cluster_label"]: topic for topic in scored}
    draft_map = {draft.get("cluster_label", ""): draft for draft in drafts_list}
    structured = {
        "date": d,
        "weekly_insight": weekly_insight,
        "debate_summary": debate_summary,
        "top3": [
            {
                **item,
                **topic_map.get(item["cluster_label"], {}),
                "draft": draft_map.get(item["cluster_label"], {}),
            }
            for item in top3
        ],
        "all_topics": scored,
        "model_log": model_log,
    }
    save_daily_json("daily_reports", structured, d)

    _safe_emit(
        emit_task,
        "pixel",
        status="working",
        task="整理 AI Office 與 dashboard 呈現素材",
        task_type="design",
        source_agent_id="craft",
        artifact_refs=[f"outputs/daily_reports/{d}.json"],
    )
    _safe_emit(
        emit_task,
        "pixel",
        status="idle",
        task="",
        task_type="design",
        source_agent_id="craft",
        artifact_refs=[f"outputs/daily_reports/{d}.json"],
    )

    _safe_emit(
        emit_task,
        "sage",
        status="working",
        task="準備後續成效分析與回顧",
        task_type="analysis",
        source_agent_id="craft",
        artifact_refs=[f"outputs/daily_reports/{d}.json"],
    )
    _safe_emit(
        emit_task,
        "sage",
        status="idle",
        task="",
        task_type="analysis",
        source_agent_id="craft",
        artifact_refs=[f"outputs/daily_reports/{d}.json"],
    )

    _safe_emit(
        emit_task,
        "lumi",
        status="working",
        task="部署結果與系統記錄",
        task_type="engineering",
        source_agent_id="sage",
        target_agent_id="",
        artifact_refs=[f"outputs/daily_reports/{d}.json"],
    )
    _safe_emit(
        emit_task,
        "lumi",
        status="idle",
        task="",
        task_type="engineering",
    )

    try:
        from src.db.queries import save_drafts, save_topics
        from src.db.schema import init_db

        init_db()
        ranked = [
            dict(
                topic,
                rank=(index + 1) if topic["cluster_label"] in {item["cluster_label"] for item in top3} else None,
            )
            for index, topic in enumerate(scored)
        ]
        topic_id_map = save_topics(ranked, d)
        if drafts_list:
            save_drafts(drafts_list, topic_id_map, d)
    except Exception as exc:
        log.warning(f"Failed to persist pipeline outputs to DB: {exc}")

    try:
        from src.office.daily_summary import generate_daily_summary
        generate_daily_summary(d)
    except Exception as exc:
        log.warning(f"AI Office 摘要產生失敗（不影響主流程）：{exc}")

    log.info(f"[Orchestrator] Completed pipeline for {d}; models={model_log}")
    return {
        "date": d,
        "articles_count": len(articles),
        "clusters_count": len(clusters),
        "top3": top3,
        "drafts_path": drafts_path,
        "model_log": model_log,
    }
