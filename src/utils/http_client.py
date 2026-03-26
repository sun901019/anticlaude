"""
async httpx 封裝：支援 retry（3次）+ timeout（30s）
"""
import asyncio
import httpx
from typing import Any

from src.utils.logger import get_logger

log = get_logger("http_client")

_TIMEOUT = httpx.Timeout(30.0)
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0  # seconds


async def get(url: str, headers: dict | None = None, params: dict | None = None) -> dict | list | str | None:
    """GET 請求，自動 retry"""
    async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.get(url, headers=headers, params=params)
                resp.raise_for_status()
                # 嘗試 JSON，否則回傳文字
                try:
                    return resp.json()
                except Exception:
                    return resp.text
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                log.warning(f"GET {url} 第 {attempt} 次失敗：{e}")
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY * attempt)
    log.error(f"GET {url} 超過最大重試次數")
    return None


async def post(url: str, headers: dict | None = None, json: Any = None) -> dict | None:
    """POST 請求，自動 retry"""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                resp = await client.post(url, headers=headers, json=json)
                resp.raise_for_status()
                return resp.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as e:
                log.warning(f"POST {url} 第 {attempt} 次失敗：{e}")
                if attempt < _MAX_RETRIES:
                    await asyncio.sleep(_RETRY_DELAY * attempt)
    log.error(f"POST {url} 超過最大重試次數")
    return None
