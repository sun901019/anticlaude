"""
Threads 數據收集：抓所有貼文 → 查詢 insights → 寫入 JSON
輸出：outputs/threads_metrics/YYYY-MM-DD.json
"""
import asyncio
from datetime import datetime

from src.tracker.threads_client import get_recent_posts, get_post_insights
from src.utils.file_io import save_daily_json
from src.utils.logger import get_logger

log = get_logger("metrics_collector")


def _calc_engagement(views: int, likes: int, replies: int, reposts: int, quotes: int) -> float:
    if views == 0:
        return 0.0
    total = likes + replies + reposts + quotes
    return round(total / views * 100, 2)


def _emit(agent_id: str, status: str, task: str = "", artifact_refs: list | None = None) -> None:
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            agent_id,
            status=status,
            task=task,
            title=task,
            task_type="engineering",
            priority="normal",
            source_agent_id="",
            target_agent_id="sage" if status == "working" else "",
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass


async def collect_metrics(date_str: str | None = None) -> list[dict]:
    """
    抓取所有 Threads 貼文數據並儲存
    """
    d = date_str or datetime.now().strftime("%Y-%m-%d")

    _emit("lumi", "working", "抓取 Threads 貼文互動數據")
    posts = await get_recent_posts(limit=50)
    if not posts:
        log.warning("沒有取得任何貼文，跳過數據收集")
        _emit("lumi", "idle")
        return []

    log.info(f"取得 {len(posts)} 篇貼文，開始查詢 insights...")

    async def _fetch_one(post: dict) -> dict | None:
        post_id = post.get("id", "")
        insights = await get_post_insights(post_id)
        if insights is None:
            return None

        views = insights.get("views", 0)
        likes = insights.get("likes", 0)
        replies = insights.get("replies", 0)
        reposts = insights.get("reposts", 0)
        quotes = insights.get("quotes", 0)

        return {
            "post_id": post_id,
            "text": (post.get("text") or "")[:50],
            "timestamp": post.get("timestamp", ""),
            "media_type": post.get("media_type", ""),
            "views": views,
            "likes": likes,
            "replies": replies,
            "reposts": reposts,
            "quotes": quotes,
            "engagement_rate": _calc_engagement(views, likes, replies, reposts, quotes),
        }

    # 並行查詢所有貼文（限制並發數避免 rate limit）
    semaphore = asyncio.Semaphore(5)

    async def _limited(post):
        async with semaphore:
            return await _fetch_one(post)

    results = await asyncio.gather(*[_limited(p) for p in posts], return_exceptions=True)

    metrics = []
    for r in results:
        if isinstance(r, dict):
            metrics.append(r)
        elif isinstance(r, Exception):
            log.warning(f"取得 insights 時出現例外：{r}")

    log.info(f"成功取得 {len(metrics)} 篇貼文數據")
    save_daily_json("threads_metrics", metrics, d)

    # 同步寫入 SQLite
    try:
        from src.db.schema import init_db
        from src.db.queries import upsert_post
        init_db()
        for m in metrics:
            upsert_post(m)
        log.info(f"已將 {len(metrics)} 篇貼文數據同步到 DB")
    except Exception as e:
        log.warning(f"DB 同步失敗（不影響主流程）：{e}")

    _emit("lumi", "idle", artifact_refs=[f"outputs/threads_metrics/{d}.json"])
    return metrics
