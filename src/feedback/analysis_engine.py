"""
Phase 4：閉環回饋分析引擎
讀取 posts + drafts DB → GPT 分析受眾偏好 → 寫入 audience_insights
"""
import json
from datetime import datetime

from src.utils.logger import get_logger

log = get_logger("feedback.engine")

ANALYSIS_PROMPT = """你是 Sun Lee 的 Threads 內容策略分析師。
以下是過去 {days} 天的貼文表現數據：

{stats_json}

請分析並產出受眾偏好報告，用以下 JSON 格式回覆，不要其他說明：
{{
  "category_performance": {{
    "AI工具實測": {{"avg_views": 0, "avg_engagement": 0.0, "count": 0}},
    "趨勢解讀": {{"avg_views": 0, "avg_engagement": 0.0, "count": 0}}
  }},
  "best_posting_day": "週三",
  "best_posting_hour": 21,
  "avg_optimal_length": 220,
  "effective_hashtags": ["#AI工具", "#生產力"],
  "growth_rate": 5.2,
  "engagement_trend": "up",
  "strategic_summary": "3-5句策略建議（繁體中文）"
}}
"""


def _emit(status: str, task: str = "", artifact_refs: list | None = None) -> None:
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            "sage",
            status=status,
            task=task,
            title=task,
            task_type="analysis",
            priority="normal",
            source_agent_id="lumi" if status == "working" else "",
            target_agent_id="",
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass


async def run_feedback_analysis(days: int = 30) -> dict:
    """
    分析過去 N 天的貼文表現，產出受眾偏好洞察並寫入 DB
    """
    _emit("working", f"分析近 {days} 天受眾偏好與貼文表現")
    try:
        from src.db.schema import init_db
        from src.db.queries import get_post_stats, get_top_hooks
        from src.db.connection import db
        init_db()
    except Exception as e:
        log.error(f"DB 連線失敗：{e}")
        _emit("idle")
        return {}

    stats = get_post_stats(days=days)
    hooks = get_top_hooks(limit=5)

    if not stats.get("rows"):
        log.warning("資料不足，無法進行回饋分析（需要有貼文數據）")
        _emit("idle")
        return {"status": "insufficient_data"}

    stats_summary = {
        "period_days": days,
        "total_posts": len(stats["rows"]),
        "by_category": stats["rows"],
        "top_hooks": hooks,
    }

    from src.config import settings
    if not settings.openai_api_key:
        log.warning("OPENAI_API_KEY 未設定，跳過 GPT 回饋分析")
        _emit("idle")
        return {"status": "no_api_key"}

    from openai import OpenAI
    client = OpenAI(api_key=settings.openai_api_key)

    prompt = ANALYSIS_PROMPT.format(
        days=days,
        stats_json=json.dumps(stats_summary, ensure_ascii=False, indent=2),
    )

    log.info(f"GPT 分析 {days} 天受眾數據...")
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
        )
        raw = resp.choices[0].message.content or ""
        import re
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
        insight = json.loads(raw)
    except Exception as e:
        log.error(f"GPT 回饋分析失敗：{e}")
        _emit("idle")
        return {}

    # 寫入 DB
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with db() as conn:
            conn.execute(
                """INSERT INTO audience_insights
                   (analysis_date, period_days, category_performance,
                    best_posting_day, best_posting_hour, top_performing_hooks,
                    avg_optimal_length, effective_hashtags,
                    growth_rate, engagement_trend, strategic_summary)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    today, days,
                    json.dumps(insight.get("category_performance", {}), ensure_ascii=False),
                    insight.get("best_posting_day"),
                    insight.get("best_posting_hour"),
                    json.dumps(insight.get("top_performing_hooks", []), ensure_ascii=False),
                    insight.get("avg_optimal_length"),
                    json.dumps(insight.get("effective_hashtags", []), ensure_ascii=False),
                    insight.get("growth_rate"),
                    insight.get("engagement_trend"),
                    insight.get("strategic_summary"),
                )
            )
        log.info("回饋分析已寫入 DB")
    except Exception as e:
        log.error(f"寫入 audience_insights 失敗：{e}")

    _emit("idle", artifact_refs=[f"outputs/office_memory/summary_{today}.md"])
    return insight


def get_latest_insights() -> dict | None:
    """取得最新的受眾洞察（供 Claude 評分參考）"""
    try:
        from src.db.connection import db
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM audience_insights ORDER BY created_at DESC LIMIT 1"
            ).fetchone()
        if not row:
            return None
        d = dict(row)
        for key in ("category_performance", "top_performing_hooks", "effective_hashtags"):
            if d.get(key):
                try:
                    d[key] = json.loads(d[key])
                except Exception:
                    pass
        return d
    except Exception:
        return None


def get_latest_insights_multi(n: int = 3) -> list[dict]:
    """取得最新 N 筆受眾洞察（供多期趨勢分析，用於高互動主題模式注入）"""
    try:
        from src.db.connection import db
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM audience_insights ORDER BY created_at DESC LIMIT ?", (n,)
            ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            for key in ("category_performance", "top_performing_hooks", "effective_hashtags"):
                if d.get(key):
                    try:
                        d[key] = json.loads(d[key])
                    except Exception:
                        pass
            result.append(d)
        return result
    except Exception:
        return []
