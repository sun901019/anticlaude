"""
Canonical location: src/domains/media/scorer.py
(Migrated from src/ai/claude_scorer.py)

Claude Sonnet：受眾匹配度評分（1-10）+ 貼文類型建議
讀取 _context/about_me.md 作為評分依據
"""
import json
from pathlib import Path

import anthropic

from src.config import settings, ABOUT_ME_PATH
from src.utils.logger import get_logger
from src.ai.skill_loader import format_skill_block

log = get_logger("domains.media.scorer")

PROMPT_PATH = Path(__file__).parents[3] / "src" / "ai" / "prompts" / "scoring_prompt.txt"
MODEL = settings.model_score


def _load_about_me() -> str:
    if ABOUT_ME_PATH.exists():
        return ABOUT_ME_PATH.read_text(encoding="utf-8")
    return "台灣科技圈創作者，受眾為對 AI 有興趣的科技工作者"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _parse_response(text: str) -> list[dict]:
    import re
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
    log.error("無法解析 Claude 評分回應")
    return []


async def score_topics(clusters: list[dict]) -> list[dict]:
    """
    為每個聚類主題評分，回傳帶有 score、post_type、reason 的清單
    """
    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY 未設定，跳過評分步驟")
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    about_me = _load_about_me()
    prompt_template = _load_prompt()
    topics_json = json.dumps(clusters, ensure_ascii=False)

    # 注入受眾記憶（閉環回饋）
    from src.feedback.memory import get_rich_memory_context
    memory = get_rich_memory_context()
    audience_insights_section = memory.get("scorer_section", "")
    if memory.get("has_data"):
        log.info("ScoreAgent：已注入受眾記憶（類型互動表現 + 趨勢）")

    # 注入 Composite Skill：seo_optimization（Sage 評分時的 SEO / GEO 框架）
    skill_block = format_skill_block("seo_optimization", "SEO Optimization Skill")

    prompt = prompt_template.format(
        about_me=about_me,
        count=len(clusters),
        topics_json=topics_json,
        audience_insights_section=audience_insights_section,
    ) + skill_block

    log.info(f"送出 {len(clusters)} 則主題給 Claude 評分...")
    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        raw_text = message.content[0].text
        scores = _parse_response(raw_text)

        # 將評分結果合併回原始 clusters
        score_map = {s["cluster_label"]: s for s in scores}
        enriched = []
        for cluster in clusters:
            label = cluster["cluster_label"]
            score_data = score_map.get(label, {})
            enriched.append({
                **cluster,
                "score": score_data.get("score", 0),
                "post_type": score_data.get("post_type", "趨勢解讀"),
                "score_reason": score_data.get("reason", ""),
                "dimensions": score_data.get("dimensions"),  # 四維度分數
            })

        enriched.sort(key=lambda x: x["score"], reverse=True)
        log.info(f"Claude 評分完成，最高分：{enriched[0]['score'] if enriched else 'N/A'}")
        return enriched
    except Exception as e:
        log.error(f"Claude API 失敗：{e}")
        return []
