"""
X (Twitter) API v2 Publisher
==============================
Publishes tweets via X API v2 POST /2/tweets.
Uses OAuth 1.0a (user-context) via requests-oauthlib.

Required config:
  X_API_KEY, X_API_KEY_SECRET
  X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET
"""
import asyncio
from functools import partial
from typing import Optional

import httpx
from requests_oauthlib import OAuth1

from src.utils.logger import get_logger

log = get_logger("publishers.x_client")

X_API_BASE = "https://api.twitter.com"
_TWEET_ENDPOINT = f"{X_API_BASE}/2/tweets"


def _oauth1(api_key: str, api_secret: str, access_token: str, access_token_secret: str) -> OAuth1:
    return OAuth1(api_key, api_secret, access_token, access_token_secret)


async def post_tweet(
    text: str,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
    reply_to_id: Optional[str] = None,
) -> dict:
    """
    POST /2/tweets — publishes a tweet and returns the API response dict.
    Raises httpx.HTTPStatusError on non-2xx responses.
    """
    body: dict = {"text": text}
    if reply_to_id:
        body["reply"] = {"in_reply_to_tweet_id": reply_to_id}

    auth = _oauth1(api_key, api_secret, access_token, access_token_secret)

    # requests-oauthlib is sync; run in thread pool to avoid blocking event loop
    import requests
    fn = partial(
        requests.post,
        _TWEET_ENDPOINT,
        json=body,
        auth=auth,
        timeout=30,
    )
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, fn)
    resp.raise_for_status()
    log.info(f"[XClient] tweet posted: status={resp.status_code}")
    return resp.json()


async def delete_tweet(
    tweet_id: str,
    api_key: str,
    api_secret: str,
    access_token: str,
    access_token_secret: str,
) -> dict:
    """
    DELETE /2/tweets/:id — removes a tweet.
    """
    import requests
    auth = _oauth1(api_key, api_secret, access_token, access_token_secret)
    url = f"{_TWEET_ENDPOINT}/{tweet_id}"
    fn = partial(requests.delete, url, auth=auth, timeout=30)
    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, fn)
    resp.raise_for_status()
    log.info(f"[XClient] tweet deleted: id={tweet_id} status={resp.status_code}")
    return resp.json()
