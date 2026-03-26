"""
Hacker News 抓取器：Algolia API
過去 24 小時 AI 相關討論，取 Top 20（依 points）
"""
from datetime import datetime, timezone, timedelta

from src.utils.http_client import get
from src.utils.logger import get_logger

log = get_logger("hn_scraper")

HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search"
HN_ITEM_BASE = "https://news.ycombinator.com/item?id="


async def fetch_hn() -> list[dict]:
    cutoff_ts = int((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())

    params = {
        "query": "AI",
        "tags": "story",
        "numericFilters": f"created_at_i>{cutoff_ts}",
        "hitsPerPage": 50,
    }

    result = await get(HN_SEARCH_URL, params=params)
    if result is None or not isinstance(result, dict):
        log.error("HN API 無回應")
        return []

    hits = result.get("hits", [])

    # 依 points 排序，取 Top 20
    hits.sort(key=lambda x: x.get("points") or 0, reverse=True)
    hits = hits[:20]

    normalized = []
    for hit in hits:
        story_id = hit.get("objectID", "")
        url = hit.get("url") or f"{HN_ITEM_BASE}{story_id}"
        normalized.append({
            "title": hit.get("title", ""),
            "url": url,
            "source": "hackernews",
            "summary": f"HN 討論 · {hit.get('num_comments', 0)} 則留言 · {hit.get('points', 0)} 分",
            "published_at": hit.get("created_at", ""),
            "language": "en",
            "points": hit.get("points", 0),
            "num_comments": hit.get("num_comments", 0),
        })

    log.info(f"HN：抓到 {len(normalized)} 則 AI 相關討論")
    return normalized
