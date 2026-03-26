"""
RSS 抓取器：TechCrunch, VentureBeat, The Verge, AI News
只抓最近 24 小時，輸出統一格式
"""
import asyncio
import feedparser
from datetime import datetime, timezone, timedelta
from typing import Any

from src.utils.logger import get_logger

log = get_logger("rss_scraper")

RSS_FEEDS = {
    "techcrunch": "https://techcrunch.com/feed/",
    "venturebeat": "https://venturebeat.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "ainews": "https://www.artificialintelligence-news.com/feed/",
}

CUTOFF_HOURS = 24


def _parse_entry(entry: Any, source: str) -> dict | None:
    """將 feedparser entry 轉換為統一格式"""
    # 取得發布時間
    published = None
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            try:
                published = datetime(*t[:6], tzinfo=timezone.utc)
                break
            except Exception:
                pass

    # 過濾超過 24 小時的文章
    if published:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
        if published < cutoff:
            return None

    # 取得摘要（優先 summary，其次 description）
    summary = ""
    for field in ("summary", "description"):
        raw = getattr(entry, field, "")
        if raw:
            # 移除 HTML tags（簡單處理）
            import re
            summary = re.sub(r"<[^>]+>", "", raw).strip()[:300]
            break

    return {
        "title": getattr(entry, "title", ""),
        "url": getattr(entry, "link", ""),
        "source": source,
        "summary": summary,
        "published_at": published.isoformat() if published else "",
        "language": "en",
    }


async def fetch_rss(source: str, url: str) -> list[dict]:
    """抓取單一 RSS feed（在 executor 中執行，避免阻塞）"""
    loop = asyncio.get_event_loop()
    try:
        feed = await loop.run_in_executor(None, feedparser.parse, url)
    except Exception as e:
        log.warning(f"RSS {source} 抓取失敗：{e}")
        return []

    if feed.bozo and not feed.entries:
        log.warning(f"RSS {source} 解析警告（bozo），跳過")
        return []

    results = []
    for entry in feed.entries:
        item = _parse_entry(entry, source)
        if item:
            results.append(item)

    log.info(f"RSS {source}：抓到 {len(results)} 則（24h 內）")
    return results


async def fetch_all_rss() -> list[dict]:
    """並行抓取所有 RSS，任一失敗不中斷其他"""
    tasks = [fetch_rss(source, url) for source, url in RSS_FEEDS.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_items = []
    for source, result in zip(RSS_FEEDS.keys(), results):
        if isinstance(result, Exception):
            log.error(f"RSS {source} 例外：{result}")
        elif isinstance(result, list):
            all_items.extend(result)

    return all_items
