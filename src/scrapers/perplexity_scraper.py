"""
Perplexity API：抓取今日 AI 熱門話題 Top 5
"""
import json
from datetime import datetime

from src.config import settings
from src.utils.http_client import post
from src.utils.logger import get_logger
from src.ai.skill_loader import load_composite_skill

log = get_logger("perplexity_scraper")

PPLX_URL = "https://api.perplexity.ai/chat/completions"
MODEL = "sonar"

PROMPT = """今天是 {date}。
請搜尋並列出今日最熱門的 AI 話題 Top 5。
每一則請回傳：
1. 標題（繁體中文）
2. 一句話摘要（繁體中文，50字內）
3. 原始來源 URL（如果找得到）

請用以下 JSON 格式回覆，不要有其他文字：
[
  {{
    "title": "...",
    "summary": "...",
    "url": "..."
  }},
  ...
]"""


def _parse_response(content: str) -> list[dict]:
    """從 Perplexity 回覆中解析 JSON"""
    try:
        # 嘗試直接解析
        return json.loads(content)
    except json.JSONDecodeError:
        # 嘗試找出 JSON 區塊
        import re
        match = re.search(r"\[.*?\]", content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    log.error("無法解析 Perplexity 回應")
    return []


async def fetch_perplexity() -> list[dict]:
    if not settings.pplx_api_key:
        log.warning("PPLX_API_KEY 未設定，跳過 Perplexity 抓取")
        return []

    headers = {
        "Authorization": f"Bearer {settings.pplx_api_key}",
        "Content-Type": "application/json",
    }

    today = datetime.now().strftime("%Y-%m-%d")

    # 注入 research_analysis skill 作為 system context（研究品質標準）
    research_skill = load_composite_skill("research_analysis")
    system_content = (
        "你是 Ori，AntiClaude 的研究 Agent。負責蒐集今日 AI 熱門話題，產出有依據、有結論、可直接被後續 agent 使用的研究素材。\n\n"
        + research_skill[:800]  # 取前段核心原則，避免 token 過多
        if research_skill else
        "你是 Ori，AntiClaude 的研究 Agent。"
    )

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": PROMPT.format(date=today)},
        ],
    }

    result = await post(PPLX_URL, headers=headers, json=payload)
    if result is None:
        log.error("Perplexity API 無回應")
        return []

    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
    items = _parse_response(content)

    normalized = []
    for item in items:
        normalized.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "source": "perplexity",
            "summary": item.get("summary", ""),
            "published_at": today,
            "language": "zh-TW",
        })

    log.info(f"Perplexity：取得 {len(normalized)} 則熱門話題")
    return normalized
