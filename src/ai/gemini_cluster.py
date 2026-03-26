"""
Gemini 2.0 Flash：主題聚類 + 去重
輸入：50-80 則素材 → 輸出：15-20 則精華主題
使用新版 google-genai SDK

NOTE: 目前 pipeline_graph.py 預設使用 claude_cluster（Claude Sonnet）。
      此模組保留為備用聚類引擎，可在 _node_cluster 中切換使用。
"""
import json
from pathlib import Path

from google import genai

from src.config import settings
from src.utils.logger import get_logger

log = get_logger("gemini_cluster")

PROMPT_PATH = Path(__file__).parent / "prompts" / "cluster_prompt.txt"
MODEL_NAME = "gemini-2.5-flash"
MAX_ARTICLES = 60   # 避免免費額度 token 上限
MAX_RETRIES = 1     # quota 失敗立即 fallback 到 Claude，不浪費等待時間


def _load_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "請將以下文章聚類成 15-20 個主題，每個主題給一個簡短標籤和代表性摘要，用 JSON 回答。"


def cluster_articles(articles: list[dict]) -> list[dict]:
    """
    使用 Gemini Flash 聚類文章。
    articles: list of {title, summary, url, source}
    回傳: list of {cluster_label, representative_title, articles: [...]}
    """
    if not settings.gemini_api_key:
        log.warning("GEMINI_API_KEY 未設定，跳過 Gemini 聚類")
        return []

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt_template = _load_prompt()
    trimmed = articles[:MAX_ARTICLES]

    snippets = "\n".join(
        f"[{i+1}] {a.get('title', '')}：{a.get('summary', '')[:150]}"
        for i, a in enumerate(trimmed)
    )
    prompt = f"{prompt_template}\n\n---\n{snippets}\n---\n\n請只輸出 JSON，不要其他說明。"

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
            )
            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            clusters = json.loads(raw)
            if isinstance(clusters, list):
                log.info(f"[GeminiCluster] 聚類完成：{len(clusters)} 個主題")
                return clusters
            log.warning(f"[GeminiCluster] 非預期格式：{type(clusters)}")
            return []
        except Exception as e:
            log.warning(f"[GeminiCluster] attempt {attempt+1} 失敗：{e}")
            if attempt >= MAX_RETRIES:
                return []

    return []
