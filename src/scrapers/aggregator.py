"""
抓取整合器：並行呼叫所有 scraper，合併輸出
儲存至 uploads/raw_feed_YYYY-MM-DD.json
"""
import asyncio
from datetime import datetime

from src.scrapers.rss_scraper import fetch_all_rss
from src.scrapers.serper_scraper import fetch_serper
from src.scrapers.perplexity_scraper import fetch_perplexity
from src.scrapers.hn_scraper import fetch_hn
from src.utils.file_io import save_raw_feed
from src.utils.logger import get_logger

log = get_logger("aggregator")


async def run_aggregator(date_str: str | None = None) -> list[dict]:
    """
    並行執行所有 scraper，合併結果存檔，回傳完整列表。
    任一來源失敗不影響其他。
    """
    log.info("開始並行抓取所有來源...")
    start = datetime.now()

    results = await asyncio.gather(
        fetch_all_rss(),
        fetch_serper(),
        fetch_perplexity(),
        fetch_hn(),
        return_exceptions=True,
    )

    source_names = ["rss", "serper", "perplexity", "hackernews"]
    all_items = []

    for name, result in zip(source_names, results):
        if isinstance(result, Exception):
            log.error(f"{name} 發生例外：{result}")
        elif isinstance(result, list):
            log.info(f"{name}：{len(result)} 則")
            all_items.extend(result)

    elapsed = (datetime.now() - start).total_seconds()
    log.info(f"抓取完成｜共 {len(all_items)} 則｜耗時 {elapsed:.1f}s")

    # 去重：先 filter（找出新素材），再 save（寫入 DB 標記已看過）
    try:
        from src.db.schema import init_db
        from src.db.queries import save_articles, filter_new_articles
        init_db()
        new_items = filter_new_articles(all_items)
        save_articles(new_items)
    except Exception as e:
        log.warning(f"DB 去重失敗（使用全量）：{e}")
        new_items = all_items

    # 存原始檔（全量備份）
    save_raw_feed(all_items, date_str)

    return new_items
