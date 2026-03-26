"""
Daily Content Pipeline — Graph Definition
==========================================
Defines the daily content pipeline and deliberation pipeline using Phase 7 GraphRunner.

Standard pipeline (with_approval_gate=True):
  1. content_research  (ori)   — aggregate AI articles        [retry=2]
  2. cluster           (ori)   — cluster into topics          [retry=2]
  3. score             (lala)  — score/rank clusters
  4. strategy          (lala)  — pick top3
  5. draft_generation  (craft) — write Threads drafts         [retry=2]
  6. draft_approval    [GATE]  — CEO approves before saving
  7. save_outputs      (lumi)  — persist to DB + daily summary

Deliberation pipeline (deliberation=True):
  Same as above, but adds a score_review gate after step 3.
  CEO can then inject context (via chat) before strategy picks topics.

Usage:
    from src.workflows.pipeline_graph import run_content_pipeline
    result = await run_content_pipeline(date_str="2026-03-19")
    result = await run_content_pipeline(deliberation=True)
    result = await run_content_pipeline(resume_run_id="<uuid>")
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from src.workflows.graph import GraphNode, GraphRunner, GraphResult
from src.utils.logger import get_logger

log = get_logger("domains.media.pipeline_graph")


# ── Node Handlers ─────────────────────────────────────────────────────────────

async def _node_content_research(ctx: dict) -> dict:
    date_str = ctx.get("date_str") or datetime.now().strftime("%Y-%m-%d")
    from src.scrapers.aggregator import run_aggregator
    articles = await run_aggregator(date_str)
    if not articles:
        return {"success": False, "error": "No articles collected"}
    return {"success": True, "agent": "ori", "articles": articles, "articles_count": len(articles)}


async def _node_cluster(ctx: dict) -> dict:
    articles = ctx.get("articles", [])
    if not articles:
        return {"success": False, "error": "No articles in context"}
    from src.agents.cluster import ClusterAgent
    try:
        from src.db.queries import get_recent_topic_labels
        recent_labels = get_recent_topic_labels(days=7)
    except Exception:
        recent_labels = []
    result = await ClusterAgent().run(articles, recent_labels=recent_labels)
    if not result.success:
        return {"success": False, "error": result.error}
    return {"success": True, "agent": "ori", "clusters": result.data, "clusters_count": len(result.data)}


async def _node_score(ctx: dict) -> dict:
    clusters = ctx.get("clusters", [])
    if not clusters:
        return {"success": False, "error": "No clusters in context"}
    from src.agents.score import ScoreAgent
    result = await ScoreAgent().run(clusters)
    if not result.success:
        return {"success": False, "error": result.error}
    scored = result.data
    # Enrich each topic with Orio three-score model (topic_fit × persona_fit × source_trust)
    # Non-fatal: if orio_scorer fails, pass original scored list through
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
    except Exception as e:
        log.warning(f"[PipelineGraph] orio_scorer enrichment failed (non-fatal): {e}")
    return {"success": True, "agent": "lala", "scored_topics": scored}


async def _node_strategy(ctx: dict) -> dict:
    scored = ctx.get("scored_topics", [])
    if not scored:
        return {"success": False, "error": "No scored_topics in context"}
    from src.agents.strategy import StrategyAgent
    result = await StrategyAgent().run(scored)
    if not result.success:
        return {"success": False, "error": result.error}
    data = result.data
    return {
        "success": True, "agent": "lala",
        "top3": data.get("top3", []),
        "weekly_insight": data.get("weekly_insight", ""),
    }


async def _node_draft_generation(ctx: dict) -> dict:
    top3 = ctx.get("top3", [])
    scored = ctx.get("scored_topics", [])
    date_str = ctx.get("date_str") or datetime.now().strftime("%Y-%m-%d")
    run_id = ctx.get("run_id", "")
    task_id = ctx.get("task_id", "")
    if not top3:
        return {"success": False, "error": "No top3 in context"}
    # GEO auto-inject
    from src.ai.skill_loader import load_composite_skill
    geo_skill = load_composite_skill("geo_optimization_engine") or ""
    from src.ai.claude_writer import write_drafts
    path, drafts = await write_drafts(top3, scored, date_str, extra_skill=geo_skill)
    try:
        from src.workflows.runner import record_artifact
        record_artifact(
            producer="craft", artifact_type="draft",
            run_id=run_id, task_id=task_id,
            file_path=str(path),
            metadata={"drafts_count": len(drafts), "date_str": date_str, "geo_applied": bool(geo_skill)},
        )
    except Exception as e:
        log.warning(f"[PipelineGraph] artifact record failed (non-fatal): {e}")
    return {
        "success": True, "agent": "craft",
        "drafts_path": str(path), "drafts_count": len(drafts), "drafts": drafts,
    }


async def _node_save_outputs(ctx: dict) -> dict:
    date_str = ctx.get("date_str") or datetime.now().strftime("%Y-%m-%d")
    top3 = ctx.get("top3", [])
    scored = ctx.get("scored_topics", [])
    drafts = ctx.get("drafts", [])
    try:
        from src.db.queries import save_drafts, save_topics
        from src.db.schema import init_db
        init_db()
        ranked = [
            dict(t, rank=(i + 1) if t["cluster_label"] in {x["cluster_label"] for x in top3} else None)
            for i, t in enumerate(scored)
        ]
        topic_id_map = save_topics(ranked, date_str)
        if drafts:
            save_drafts(drafts, topic_id_map, date_str)
    except Exception as e:
        log.warning(f"[PipelineGraph] DB save failed (non-fatal): {e}")
    try:
        from src.utils.file_io import save_daily_json
        weekly_insight = ctx.get("weekly_insight", "")
        debate_summary = ctx.get("debate_summary", "")
        topic_map = {t["cluster_label"]: t for t in scored}
        draft_map = {d_item.get("cluster_label", ""): d_item for d_item in drafts}
        structured = {
            "date": date_str,
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
        }
        save_daily_json("daily_reports", structured, date_str)
    except Exception as e:
        log.warning(f"[PipelineGraph] daily_reports JSON save failed (non-fatal): {e}")
    try:
        from src.office.daily_summary import generate_daily_summary
        generate_daily_summary(date_str)
    except Exception as e:
        log.warning(f"[PipelineGraph] daily summary failed (non-fatal): {e}")
    return {"success": True, "agent": "lumi", "date": date_str}


async def _noop(ctx: dict) -> dict:
    """Placeholder handler for approval gate nodes — never called by GraphRunner."""
    return {"success": True}


# ── Pipeline Builder ──────────────────────────────────────────────────────────

def build_content_pipeline(
    with_approval_gate: bool = True,
    deliberation: bool = False,
) -> GraphRunner:
    """
    Build the daily content pipeline graph.

    Args:
        with_approval_gate: Insert a human-approval pause before save_outputs.
        deliberation: Insert an extra human pause after scoring so CEO can
                      inject context before strategy selects topics.
    """
    nodes: list[GraphNode] = [
        GraphNode(
            name="content_research", agent="ori",
            handler=_node_content_research, retry_limit=2,
        ),
        GraphNode(
            name="cluster", agent="ori",
            handler=_node_cluster, retry_limit=2,
            depends_on=["content_research"],
        ),
        GraphNode(
            name="score", agent="lala",
            handler=_node_score,
            depends_on=["cluster"],
        ),
    ]

    # Deliberation gate: pause after scoring so CEO can review topic candidates
    if deliberation:
        nodes.append(GraphNode(
            name="score_review",
            agent="human",
            handler=_noop,
            is_approval_gate=True,
            approval_action="review_scored_topics",
            approval_risk="low",
            depends_on=["score"],
        ))

    nodes += [
        GraphNode(
            name="strategy", agent="lala",
            handler=_node_strategy,
            depends_on=["score"],
        ),
        GraphNode(
            name="draft_generation", agent="craft",
            handler=_node_draft_generation, retry_limit=2,
            depends_on=["strategy"],
        ),
    ]

    if with_approval_gate:
        nodes.append(GraphNode(
            name="draft_approval",
            agent="human",
            handler=_noop,
            is_approval_gate=True,
            approval_action="publish_post",   # surfaces in /review CEO inbox; triggers X on approve
            approval_risk="high",
            depends_on=["draft_generation"],
        ))

    save_deps = ["draft_generation", "draft_approval"] if with_approval_gate else ["draft_generation"]
    nodes.append(GraphNode(
        name="save_outputs", agent="lumi",
        handler=_node_save_outputs,
        depends_on=save_deps,
    ))

    return GraphRunner(nodes=nodes, name="daily_content_pipeline", domain="media")


# ── Public Entry Points ───────────────────────────────────────────────────────

async def run_content_pipeline(
    date_str: str | None = None,
    with_approval_gate: bool = True,
    deliberation: bool = False,
    resume_run_id: str | None = None,
) -> dict[str, Any]:
    """
    Run the daily content pipeline as a graph workflow.

    Args:
        date_str:           Target date (defaults to today).
        with_approval_gate: Pause before save_outputs for CEO draft approval.
        deliberation:       Extra pause after scoring (CEO Deliberation Mode).
        resume_run_id:      If set, resumes a previously paused run.

    Returns:
        {
          "ok": bool,
          "run_id": str,
          "paused_at": str | None,   # node name if paused
          "error": str | None,
          "outputs_summary": dict,   # node_name → lightweight output
        }
    """
    context = {"date_str": date_str or datetime.now().strftime("%Y-%m-%d")}
    runner = build_content_pipeline(
        with_approval_gate=with_approval_gate,
        deliberation=deliberation,
    )
    result: GraphResult = await runner.run(context=context, resume_run_id=resume_run_id)
    return {
        "ok": result.ok,
        "run_id": result.run_id,
        "paused_at": result.paused_at,
        "error": result.error,
        "outputs_summary": {
            node_name: {k: v for k, v in data.items()
                        if k not in ("drafts", "articles", "clusters")}
            for node_name, data in result.outputs.items()
            if isinstance(data, dict)
        },
    }
