"""
X (Twitter) API v2 Search & Analytics
========================================
Read-only search and analytics using Bearer token (app-only auth).

Endpoints:
  GET /2/tweets/search/recent  — recent tweet search (7-day window)
  GET /2/tweets/:id/metrics    — public metrics for a tweet
  GET /2/users/:id/tweets      — user timeline

Required config: X_BEARER_TOKEN
"""
import httpx
from typing import Optional

from src.utils.logger import get_logger

log = get_logger("social.x_search")

X_API_BASE = "https://api.twitter.com/2"
_TIMEOUT = 30.0


def _bearer_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def search_recent(
    query: str,
    token: str,
    max_results: int = 10,
    tweet_fields: Optional[list[str]] = None,
) -> list[dict]:
    """
    GET /2/tweets/search/recent
    Returns tweets matching query from the past 7 days.
    max_results: 10–100 (API constraint)
    """
    fields = tweet_fields or ["public_metrics", "created_at", "author_id"]
    params = {
        "query": query,
        "max_results": str(min(max(max_results, 10), 100)),
        "tweet.fields": ",".join(fields),
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            f"{X_API_BASE}/tweets/search/recent",
            headers=_bearer_headers(token),
            params=params,
        )
    resp.raise_for_status()
    data = resp.json()
    return data.get("data", [])


async def get_tweet_metrics(tweet_id: str, token: str) -> dict:
    """
    GET /2/tweets/:id?tweet.fields=public_metrics,non_public_metrics
    Returns engagement metrics for a single tweet.
    Note: non_public_metrics requires OAuth 1.0a (owner auth), not Bearer.
    """
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            f"{X_API_BASE}/tweets/{tweet_id}",
            headers=_bearer_headers(token),
            params={"tweet.fields": "public_metrics,created_at"},
        )
    resp.raise_for_status()
    return resp.json().get("data", {})


async def get_user_timeline(
    user_id: str,
    token: str,
    max_results: int = 10,
) -> list[dict]:
    """
    GET /2/users/:id/tweets
    Returns recent tweets from a user timeline.
    """
    params = {
        "max_results": str(min(max(max_results, 5), 100)),
        "tweet.fields": "public_metrics,created_at",
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(
            f"{X_API_BASE}/users/{user_id}/tweets",
            headers=_bearer_headers(token),
            params=params,
        )
    resp.raise_for_status()
    return resp.json().get("data", [])


async def ping(token: str) -> bool:
    """Quick connectivity check — GET /2/tweets/search/recent with minimal query."""
    try:
        results = await search_recent("from:twitter", token, max_results=10)
        return True
    except Exception as e:
        log.warning(f"[XSearch] ping failed: {e}")
        return False
