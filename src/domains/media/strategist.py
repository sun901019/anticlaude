"""
Canonical location: src/domains/media/strategist.py
(Migrated from src/ai/gpt_strategist.py)

GPT-4o：結合 Threads 數據，選 Top 3 主題 + 策略建議
"""
import json
from pathlib import Path
from openai import OpenAI

from src.config import settings
from src.utils.file_io import load_daily_json, list_recent_dates
from src.utils.logger import get_logger
from src.ai.skill_loader import format_skill_block

log = get_logger("domains.media.strategist")

PROMPT_PATH = Path(__file__).parents[3] / "src" / "ai" / "prompts" / "strategy_prompt.txt"
MODEL = settings.model_strategy


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _load_recent_metrics(days: int = 7) -> list[dict]:
    """讀取最近 N 天的 Threads 數據"""
    dates = list_recent_dates("threads_metrics", days)
    metrics = []
    for d in dates:
        data = load_daily_json("threads_metrics", d)
        if data:
            metrics.extend(data if isinstance(data, list) else [data])
    return metrics


def _parse_response(text: str) -> dict:
    import re
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    log.error("無法解析 GPT 策略回應")
    return {"top3": [], "weekly_insight": ""}


async def select_top3(scored_topics: list[dict]) -> dict:
    """
    選 Top 3 主題，結合近 7 天 Threads 數據
    回傳 {"top3": [...], "weekly_insight": "..."}
    """
    if not settings.openai_api_key:
        log.warning("OPENAI_API_KEY 未設定，使用分數前 3 名作為 Top 3")
        top3 = scored_topics[:3]
        return {
            "top3": [
                {
                    "cluster_label": t["cluster_label"],
                    "rank": i + 1,
                    "strategy_reason": f"評分 {t.get('score', 0)} 分",
                    "post_type": t.get("post_type", "趨勢解讀"),
                }
                for i, t in enumerate(top3)
            ],
            "weekly_insight": "（GPT 策略分析未啟用）",
        }

    client = OpenAI(api_key=settings.openai_api_key)

    metrics = _load_recent_metrics()
    prompt_template = _load_prompt()

    # 注入受眾記憶（各類型歷史表現 + 策略建議）
    from src.feedback.memory import get_rich_memory_context
    memory = get_rich_memory_context()
    category_perf_text = memory.get("strategy_section", "（尚無數據）") if memory.get("has_data") else "（尚無數據）"
    if memory.get("has_data"):
        log.info("StrategyAgent：已注入受眾記憶（類型互動排行 + 策略建議）")

    # 最近 7 天已發的類型（避免重複）
    recent_types_text = "（尚無紀錄）"
    if metrics:
        recent_types = list({m.get("post_type", "") for m in metrics if m.get("post_type")})
        recent_types_text = "、".join(recent_types) if recent_types else "（尚無紀錄）"

    # 注入 Composite Skill：marketing_strategy（選題框架 + 內容策略）
    skill_block = format_skill_block("marketing_strategy", "Marketing Strategy Skill")

    prompt = prompt_template.format(
        scored_topics_json=json.dumps(scored_topics, ensure_ascii=False),
        threads_metrics_json=json.dumps(metrics, ensure_ascii=False) if metrics else "[]（尚無數據）",
        category_performance=category_perf_text,
        recent_post_types=recent_types_text,
    ) + skill_block

    log.info(f"送出 {len(scored_topics)} 則評分主題給 GPT 選 Top 3...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )
        raw_text = response.choices[0].message.content
        result = _parse_response(raw_text)
        log.info(f"GPT 策略完成，Top 3：{[t['cluster_label'] for t in result.get('top3', [])]}")
        return result
    except Exception as e:
        log.error(f"GPT API 失敗：{e}")
        return {"top3": scored_topics[:3], "weekly_insight": ""}
