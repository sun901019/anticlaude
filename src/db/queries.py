"""
常用 DB 查詢：文章去重、主題歷史、貼文數據
"""
import hashlib
import json
from datetime import datetime, date
from typing import Any

from src.db.connection import db
from src.utils.logger import get_logger

log = get_logger("db.queries")


# ── 文章去重 ──────────────────────────────────────────────────────────────────

def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def filter_new_articles(articles: list[dict], dedup_days: int = 3) -> list[dict]:
    """過濾掉最近 dedup_days 天內已抓過的文章（by url_hash），只回傳新的"""
    if not articles:
        return []
    hashes = [url_hash(a["url"]) for a in articles]
    with db() as conn:
        rows = conn.execute(
            f"SELECT url_hash FROM articles"
            f" WHERE url_hash IN ({','.join('?'*len(hashes))})"
            f" AND scraped_at >= datetime('now', '-{dedup_days} days')",
            hashes
        ).fetchall()
    seen = {r["url_hash"] for r in rows}
    new = [a for a, h in zip(articles, hashes) if h not in seen]
    log.info(f"去重（近{dedup_days}天）：{len(articles)} → {len(new)} 篇新素材")
    return new


def save_articles(articles: list[dict]):
    """批次寫入 articles 表（忽略已存在）"""
    if not articles:
        return
    with db() as conn:
        conn.executemany(
            """INSERT OR IGNORE INTO articles
               (url_hash, url, title, summary, source, language, published_at)
               VALUES (?,?,?,?,?,?,?)""",
            [
                (
                    url_hash(a["url"]),
                    a["url"],
                    a.get("title", ""),
                    a.get("summary", ""),
                    a.get("source", ""),
                    a.get("language", "en"),
                    a.get("published_at"),
                )
                for a in articles
            ],
        )
    log.info(f"已寫入 {len(articles)} 篇文章到 DB")


# ── 主題歷史（語意去重）────────────────────────────────────────────────────────

def get_recent_topic_labels(days: int = 7) -> list[str]:
    """回傳最近 N 天發過的主題名稱，供聚類去重使用"""
    with db() as conn:
        rows = conn.execute(
            "SELECT cluster_label FROM topics WHERE date >= date('now', ?)",
            (f"-{days} days",)
        ).fetchall()
    return [r["cluster_label"] for r in rows]


def save_topics(topics: list[dict], date_str: str) -> dict[str, int]:
    """將評分後的主題寫入 DB，回傳 cluster_label → topic_id 的 mapping"""
    id_map: dict[str, int] = {}
    with db() as conn:
        for t in topics:
            cursor = conn.execute(
                """INSERT INTO topics
                   (date, cluster_label, category, score, dimensions, rank, article_ids, deep_analysis)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    date_str,
                    t["cluster_label"],
                    t.get("post_type", ""),
                    t.get("score", 0),
                    json.dumps(t.get("dimensions"), ensure_ascii=False) if t.get("dimensions") else None,
                    t.get("rank"),
                    json.dumps(t.get("articles", []), ensure_ascii=False),
                    t.get("merged_summary", ""),
                )
            )
            id_map[t["cluster_label"]] = cursor.lastrowid
    log.info(f"已寫入 {len(topics)} 個主題到 DB")
    return id_map


def save_drafts(drafts: list[dict], topic_id_map: dict[str, int], date_str: str):
    """將文案草稿寫入 DB"""
    with db() as conn:
        for draft in drafts:
            label = draft.get("cluster_label", "")
            topic_id = topic_id_map.get(label)
            hook = draft.get("hook", "")
            for ver, style in [("version_a", "資訊型"), ("version_b", "故事型")]:
                v = draft.get(ver, {})
                content = v.get("content", "")
                if not content:
                    continue
                import re
                tags = re.findall(r"#\S+", content)
                conn.execute(
                    """INSERT INTO drafts (date, topic_id, style, content, hook, hashtags)
                       VALUES (?,?,?,?,?,?)""",
                    (date_str, topic_id, v.get("style", style), content, hook,
                     json.dumps(tags, ensure_ascii=False))
                )
    log.info(f"已寫入 {len(drafts)*2} 篇草稿到 DB")


# ── 貼文數據 ───────────────────────────────────────────────────────────────────

def _normalize_timestamp(ts: str | None) -> str | None:
    """把 Threads API 回傳的 ISO 8601 時區格式轉成 SQLite 可解析的格式。
    e.g. '2026-03-08T17:08:41+0000' → '2026-03-08T17:08:41'
    """
    if not ts:
        return ts
    # 移除 +HHMM / +HH:MM / Z 時區後綴
    for sep in ("+", "Z"):
        if sep in ts:
            ts = ts.split(sep)[0]
            break
    return ts


def upsert_post(post: dict):
    """新增或更新貼文數據（by threads_id）"""
    eng = 0.0
    if post.get("views", 0) > 0:
        eng = round(
            (post.get("likes", 0) + post.get("replies", 0) +
             post.get("reposts", 0) + post.get("quotes", 0)) / post["views"] * 100, 2
        )
    posted_at = _normalize_timestamp(post.get("timestamp"))
    category = post.get("category", "")
    with db() as conn:
        conn.execute(
            """INSERT INTO posts (threads_id, text, posted_at, category, views, likes, replies, reposts, quotes, engagement_rate, metrics_updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,CURRENT_TIMESTAMP)
               ON CONFLICT(threads_id) DO UPDATE SET
                 views=excluded.views, likes=excluded.likes,
                 replies=excluded.replies, reposts=excluded.reposts,
                 quotes=excluded.quotes, engagement_rate=excluded.engagement_rate,
                 posted_at=COALESCE(excluded.posted_at, posts.posted_at),
                 category=COALESCE(NULLIF(excluded.category,''), posts.category),
                 metrics_updated_at=CURRENT_TIMESTAMP""",
            (
                post["post_id"], post.get("text", ""), posted_at, category,
                post.get("views", 0), post.get("likes", 0),
                post.get("replies", 0), post.get("reposts", 0),
                post.get("quotes", 0), eng,
            )
        )


def get_post_stats(days: int = 30) -> dict:
    """統計貼文表現，供回饋引擎使用"""
    with db() as conn:
        rows = conn.execute(
            """SELECT category, post_type,
                      COUNT(*) as count,
                      ROUND(AVG(views),0) as avg_views,
                      ROUND(AVG(engagement_rate),2) as avg_engagement
               FROM posts
               WHERE posted_at >= date('now', ?)
               GROUP BY category ORDER BY avg_engagement DESC""",
            (f"-{days} days",)
        ).fetchall()
    return {"rows": [dict(r) for r in rows]}


def get_top_performing_topics(days: int = 14, top_n: int = 5) -> list[dict]:
    """近 N 天高互動主題類型排行（供 Lala 選題注入）"""
    try:
        with db() as conn:
            rows = conn.execute(
                """SELECT category as topic_type,
                          ROUND(AVG(engagement_rate), 2) as avg_engagement,
                          COUNT(*) as post_count
                   FROM posts
                   WHERE posted_at >= date('now', ?)
                     AND engagement_rate IS NOT NULL
                   GROUP BY category
                   ORDER BY avg_engagement DESC
                   LIMIT ?""",
                (f"-{days} days", top_n)
            ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        return []


def get_top_hooks(limit: int = 10) -> list[dict]:
    """高互動率的 Hook 列表"""
    with db() as conn:
        rows = conn.execute(
            """SELECT d.hook, p.engagement_rate, p.views
               FROM drafts d JOIN posts p ON d.post_id = p.id
               WHERE d.was_selected = 1 AND d.hook IS NOT NULL
               ORDER BY p.engagement_rate DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
