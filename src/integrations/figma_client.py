"""
Figma API Client — read-only
=============================
Uses Personal Access Token (FIGMA_API_TOKEN) with X-Figma-Token header.
All operations are read-only (file_content:read scope).

Rate limits: 60 req/min per token (Figma REST v1 default).
"""
import httpx
from src.utils.logger import get_logger

log = get_logger("integrations.figma")

FIGMA_BASE = "https://api.figma.com/v1"
_TIMEOUT = 30.0


def _headers(token: str) -> dict:
    return {"X-Figma-Token": token}


async def get_file(file_key: str, token: str) -> dict:
    """
    GET /v1/files/:file_key
    Returns full Figma document tree (can be large).
    """
    url = f"{FIGMA_BASE}/files/{file_key}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, headers=_headers(token))
    resp.raise_for_status()
    return resp.json()


async def get_file_nodes(file_key: str, node_ids: list[str], token: str) -> dict:
    """
    GET /v1/files/:file_key/nodes?ids=...
    Returns specific nodes from a Figma document.
    """
    ids_param = ",".join(node_ids)
    url = f"{FIGMA_BASE}/files/{file_key}/nodes"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, headers=_headers(token), params={"ids": ids_param})
    resp.raise_for_status()
    return resp.json()


async def get_comments(file_key: str, token: str) -> list[dict]:
    """
    GET /v1/files/:file_key/comments
    Returns all comments on a Figma file.
    """
    url = f"{FIGMA_BASE}/files/{file_key}/comments"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.get(url, headers=_headers(token))
    resp.raise_for_status()
    data = resp.json()
    return data.get("comments", [])


async def get_file_images(file_key: str, node_ids: list[str], token: str,
                          fmt: str = "png", scale: float = 1.0) -> dict:
    """
    GET /v1/images/:file_key?ids=...&format=png
    Renders nodes as images and returns URLs (valid ~30 days).
    """
    url = f"{FIGMA_BASE}/images/{file_key}"
    params = {"ids": ",".join(node_ids), "format": fmt, "scale": str(scale)}
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(url, headers=_headers(token), params=params)
    resp.raise_for_status()
    return resp.json()


async def ping(token: str) -> bool:
    """Quick connectivity check — tries /v1/me endpoint."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{FIGMA_BASE}/me", headers=_headers(token))
        return resp.status_code == 200
    except Exception as e:
        log.warning(f"[FigmaClient] ping failed: {e}")
        return False
