"""
Serper API：Google 新聞搜尋
英文 + 中文各 10 則，輸出統一格式
"""
from src.config import settings
from src.utils.http_client import post
from src.utils.logger import get_logger

log = get_logger("serper_scraper")

SERPER_URL = "https://google.serper.dev/news"

QUERIES = [
    # AI / 科技（英文）
    {"q": "AI technology tools 2026", "gl": "us", "num": 10, "lang": "en", "source_tag": "serper_en"},
    # AI / 科技（中文）
    {"q": "AI 工具 科技 2026", "gl": "tw", "hl": "zh-TW", "num": 10, "lang": "zh-TW", "source_tag": "serper_zh"},
    # 商業 / 創業
    {"q": "startup business trends 2026", "gl": "us", "num": 8, "lang": "en", "source_tag": "serper_biz"},
    # 職場生產力 / 效率工具
    {"q": "productivity tools remote work 2026", "gl": "us", "num": 8, "lang": "en", "source_tag": "serper_work"},
    # 台灣時事 / 社會話題
    {"q": "台灣 科技 職場 創業 新聞", "gl": "tw", "hl": "zh-TW", "num": 8, "lang": "zh-TW", "source_tag": "serper_tw"},
]


def _normalize(item: dict, source_tag: str, lang: str) -> dict:
    return {
        "title": item.get("title", ""),
        "url": item.get("link", ""),
        "source": source_tag,
        "summary": item.get("snippet", ""),
        "published_at": item.get("date", ""),
        "language": "en" if lang == "en" else "zh-TW",
    }


async def fetch_serper() -> list[dict]:
    if not settings.serper_api_key:
        log.warning("SERPER_API_KEY 未設定，跳過 Serper 抓取")
        return []

    headers = {
        "X-API-KEY": settings.serper_api_key,
        "Content-Type": "application/json",
    }

    all_items = []
    for query_cfg in QUERIES:
        source_tag = query_cfg["source_tag"]
        lang = query_cfg["lang"]
        payload = {k: v for k, v in query_cfg.items() if k not in ("source_tag", "lang")}

        result = await post(SERPER_URL, headers=headers, json=payload)
        if result is None:
            log.error(f"Serper {source_tag} 回傳空值")
            all_items.extend([])
            continue

        news = result.get("news", [])
        normalized = [_normalize(item, source_tag, lang) for item in news]
        log.info(f"Serper {source_tag}：抓到 {len(normalized)} 則")
        all_items.extend(normalized)

    return all_items
