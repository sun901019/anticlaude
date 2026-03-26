"""Async Serper search client — thin wrapper around the Serper REST API."""
import httpx
from src.config import settings
from src.utils.logger import get_logger

log = get_logger("serper_client")

SERPER_URL = "https://google.serper.dev/search"
_TIMEOUT = 20.0


async def search(query: str, gl: str = "tw", hl: str = "zh-TW", num: int = 8) -> list[dict]:
    """
    Run a Serper search and return a list of organic result dicts.
    Each dict has: title, snippet, link.
    Returns [] if API key is missing or the request fails.
    """
    if not settings.serper_api_key:
        log.debug("Serper API key not set, skipping search")
        return []
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                SERPER_URL,
                headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
                json={"q": query, "gl": gl, "hl": hl, "num": num},
            )
            resp.raise_for_status()
            data = resp.json()
        return [
            {"title": r.get("title", ""), "snippet": r.get("snippet", ""), "link": r.get("link", "")}
            for r in data.get("organic", [])
        ]
    except Exception as e:
        log.warning(f"Serper search failed ({query[:40]}): {e}")
        return []
