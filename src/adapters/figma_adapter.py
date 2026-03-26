"""
Figma API Adapter
==================
Read-only adapter for Figma API v1.
Risk: medium (read-only, no mutations)
Approval: not required
"""
from src.adapters.base import AdapterBase, AdapterResult
from src.config import settings
from src.integrations.figma_client import get_file, get_file_nodes, get_comments, get_file_images, ping


class FigmaAdapter(AdapterBase):
    name = "figma_api"
    risk_level = "medium"
    timeout_seconds = 30
    requires_approval = False
    allowed_agents = ["pixel"]

    async def execute(self, payload: dict) -> AdapterResult:
        """
        payload:
          action: str        — "get_file" | "get_nodes" | "get_comments" | "get_images" | "ping"
          file_key: str      — Figma 文件 key (required for most actions)
          node_ids: list[str]— 節點 ID 清單 (for get_nodes / get_images)
          format: str        — 圖片格式 "png" | "jpg" | "svg" (default "png")
          scale: float       — 輸出縮放比例 (default 1.0)
        """
        token = settings.figma_api_token
        if not token:
            return AdapterResult(ok=False, error="FIGMA_API_TOKEN 未設定")

        action = payload.get("action", "get_nodes")
        file_key = payload.get("file_key", "")
        node_ids = payload.get("node_ids", [])

        if action == "ping":
            ok = await ping(token)
            return AdapterResult(ok=ok, data={"connected": ok})

        if not file_key:
            return AdapterResult(ok=False, error="file_key 不得為空")

        if action == "get_file":
            data = await get_file(file_key, token)
            return AdapterResult(ok=True, data=data)

        if action == "get_nodes":
            if not node_ids:
                return AdapterResult(ok=False, error="node_ids 不得為空")
            data = await get_file_nodes(file_key, node_ids, token)
            return AdapterResult(ok=True, data=data)

        if action == "get_comments":
            data = await get_comments(file_key, token)
            return AdapterResult(ok=True, data={"comments": data})

        if action == "get_images":
            if not node_ids:
                return AdapterResult(ok=False, error="node_ids 不得為空")
            fmt = payload.get("format", "png")
            scale = float(payload.get("scale", 1.0))
            data = await get_file_images(file_key, node_ids, token, fmt=fmt, scale=scale)
            return AdapterResult(ok=True, data=data)

        return AdapterResult(ok=False, error=f"未知 action: {action}")
