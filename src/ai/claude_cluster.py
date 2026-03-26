"""
Claude Sonnet fallback 聚類：當 Gemini 不可用時使用
輸入：原始素材 → 輸出：15-20 則去重主題
"""
import json
from pathlib import Path

import anthropic

from src.config import settings
from src.utils.logger import get_logger

log = get_logger("claude_cluster")

PROMPT_PATH = Path(__file__).parent / "prompts" / "cluster_prompt.txt"
MODEL = settings.model_cluster
MAX_ARTICLES = 50  # Claude 每次送較少節省費用


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _parse_response(text: str) -> list[dict]:
    import re
    # 移除 markdown code block
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\[.*?\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    log.error("無法解析 Claude cluster 回應")
    return []


async def cluster_articles_claude(articles: list[dict], recent_labels: list[str] | None = None) -> list[dict]:
    """Claude fallback 聚類"""
    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY 未設定，跳過 Claude 聚類")
        return []

    batch = articles[:MAX_ARTICLES]
    if len(articles) > MAX_ARTICLES:
        log.info(f"Claude 聚類：只送前 {MAX_ARTICLES} 則")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    recent_hint = ""
    if recent_labels:
        labels_str = "、".join(recent_labels[:10])
        recent_hint = f"\n- **注意**：以下主題過去 7 天已發過，請避免重複：{labels_str}\n"

    prompt_template = _load_prompt()
    articles_json = json.dumps(batch, ensure_ascii=False)
    prompt = prompt_template.format(
        count=len(batch), articles_json=articles_json,
        recent_topics_hint=recent_hint
    )

    log.info(f"送出 {len(batch)} 則素材給 Claude 聚類...")
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=8096,
            messages=[{"role": "user", "content": prompt}],
        )
        clusters = _parse_response(message.content[0].text)
        log.info(f"Claude 聚類完成：{len(clusters)} 個主題")
        return clusters
    except Exception as e:
        log.error(f"Claude 聚類失敗：{e}")
        return []
