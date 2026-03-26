"""
Figma Operator API Routes
==========================
Proxy endpoints for the Figma read-only integration.
All routes require FIGMA_API_TOKEN to be set in .env.

Endpoints:
  GET /api/figma/ping              — connectivity check
  GET /api/figma/file              — file metadata (name, pages, last modified)
  GET /api/figma/nodes             — fetch specific nodes by ID
  GET /api/figma/comments          — list file comments
  GET /api/figma/images            — render nodes as image URLs
  GET /api/figma/components        — list published components in a file
"""
from fastapi import APIRouter, HTTPException, Query
from src.config import settings
from src.utils.logger import get_logger
import src.integrations.figma_client as figma_client  # module-level for test patching

router = APIRouter()
log = get_logger("api.figma")


def _require_token() -> str:
    token = settings.figma_api_token
    if not token:
        raise HTTPException(
            status_code=400,
            detail="FIGMA_API_TOKEN 未設定。請在 .env 加入 FIGMA_API_TOKEN=<your-token>",
        )
    return token


@router.get("/api/figma/ping")
async def figma_ping():
    """Test Figma API connectivity. Returns ok=False if token not set."""
    token = settings.figma_api_token
    if not token:
        return {"ok": False, "error": "FIGMA_API_TOKEN 未設定", "connected": False}
    try:
        connected = await figma_client.ping(token)
        return {"ok": connected, "connected": connected}
    except Exception as e:
        log.warning(f"[Figma] ping error: {e}")
        return {"ok": False, "connected": False, "error": str(e)}


@router.get("/api/figma/file")
async def figma_file(file_key: str = Query(..., description="Figma file key from URL")):
    """
    Return file metadata: name, last modified, pages list, component count.
    Does NOT return the full node tree (too large).
    """
    token = _require_token()
    try:
        data = await figma_client.get_file(file_key, token)
        doc = data.get("document", {})
        pages = [
            {"id": ch.get("id"), "name": ch.get("name")}
            for ch in doc.get("children", [])
            if ch.get("type") == "CANVAS"
        ]
        return {
            "ok": True,
            "name": data.get("name"),
            "last_modified": data.get("lastModified"),
            "version": data.get("version"),
            "file_key": file_key,
            "pages": pages,
            "page_count": len(pages),
        }
    except Exception as e:
        log.warning(f"[Figma] get_file error: {e}")
        raise HTTPException(status_code=502, detail=f"Figma API error: {str(e)[:200]}")


@router.get("/api/figma/nodes")
async def figma_nodes(
    file_key: str = Query(...),
    ids: str = Query(..., description="Comma-separated node IDs"),
):
    """Fetch specific nodes by ID. ids=1:2,1:3 (Figma node ID format)."""
    token = _require_token()
    node_list = [n.strip() for n in ids.split(",") if n.strip()]
    if not node_list:
        raise HTTPException(status_code=400, detail="ids parameter is empty")
    try:
        data = await figma_client.get_file_nodes(file_key, node_list, token)
        nodes = data.get("nodes", {})
        simplified = {}
        for node_id, node_data in nodes.items():
            doc = node_data.get("document", {})
            simplified[node_id] = {
                "id": doc.get("id"),
                "name": doc.get("name"),
                "type": doc.get("type"),
                "visible": doc.get("visible", True),
            }
        return {"ok": True, "file_key": file_key, "nodes": simplified, "count": len(simplified)}
    except Exception as e:
        log.warning(f"[Figma] get_file_nodes error: {e}")
        raise HTTPException(status_code=502, detail=f"Figma API error: {str(e)[:200]}")


@router.get("/api/figma/comments")
async def figma_comments(file_key: str = Query(...)):
    """List all comments on a Figma file."""
    token = _require_token()
    try:
        comments = await figma_client.get_comments(file_key, token)
        simplified = [
            {
                "id": c.get("id"),
                "message": c.get("message", ""),
                "user": c.get("user", {}).get("name"),
                "created_at": c.get("created_at"),
                "resolved_at": c.get("resolved_at"),
            }
            for c in comments
        ]
        return {"ok": True, "file_key": file_key, "comments": simplified, "count": len(simplified)}
    except Exception as e:
        log.warning(f"[Figma] get_comments error: {e}")
        raise HTTPException(status_code=502, detail=f"Figma API error: {str(e)[:200]}")


@router.get("/api/figma/images")
async def figma_images(
    file_key: str = Query(...),
    ids: str = Query(..., description="Comma-separated node IDs to render"),
    fmt: str = Query("png", description="Output format: png | jpg | svg | pdf"),
    scale: float = Query(1.0, ge=0.5, le=4.0, description="Render scale (0.5–4.0)"),
):
    """Render Figma nodes as image URLs (valid ~30 days)."""
    token = _require_token()
    node_list = [n.strip() for n in ids.split(",") if n.strip()]
    if not node_list:
        raise HTTPException(status_code=400, detail="ids parameter is empty")
    try:
        data = await figma_client.get_file_images(file_key, node_list, token, fmt=fmt, scale=scale)
        return {
            "ok": True,
            "file_key": file_key,
            "format": fmt,
            "scale": scale,
            "images": data.get("images", {}),
            "err": data.get("err"),
        }
    except Exception as e:
        log.warning(f"[Figma] get_file_images error: {e}")
        raise HTTPException(status_code=502, detail=f"Figma API error: {str(e)[:200]}")


@router.get("/api/figma/components")
async def figma_components(file_key: str = Query(...)):
    """List top-level components/frames from all pages of a file."""
    token = _require_token()
    try:
        data = await figma_client.get_file(file_key, token)
        doc = data.get("document", {})
        components = []
        for page in doc.get("children", []):
            if page.get("type") != "CANVAS":
                continue
            page_name = page.get("name", "")
            for child in page.get("children", []):
                components.append({
                    "id": child.get("id"),
                    "name": child.get("name"),
                    "type": child.get("type"),
                    "page": page_name,
                })
        return {
            "ok": True,
            "file_key": file_key,
            "components": components[:50],  # cap at 50 for response size
            "total": len(components),
        }
    except Exception as e:
        log.warning(f"[Figma] components error: {e}")
        raise HTTPException(status_code=502, detail=f"Figma API error: {str(e)[:200]}")
