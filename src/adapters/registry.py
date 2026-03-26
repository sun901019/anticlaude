"""
Adapter Registry — 全局適配器登記表
=====================================
記錄每個 adapter 的元資料（不實例化，避免 eager import）。
供工作流 / 審核系統查詢 adapter 的 risk_level 與限制規則。

欄位說明：
  module           Python 模組路徑
  class_name       Adapter 類名
  risk_level       low / medium / high / critical
  requires_approval 是否需人工批准才能執行
  auth_required    是否需要 API token/secret
  allowed_agents   允許使用的 agent 清單（空 = 全部）
  timeout_seconds  最大執行秒數
  status           planned / active / deprecated
  description      功能說明
"""

ADAPTER_REGISTRY: dict[str, dict] = {
    "x_publish": {
        "module": "src.adapters.x_adapter",
        "class_name": "XPublishAdapter",
        "risk_level": "high",
        "requires_approval": True,
        "auth_required": True,
        "allowed_agents": ["craft"],
        "timeout_seconds": 60,
        "status": "active",
        "description": "X（Twitter）發布貼文。使用 OAuth 1.0a，dry_run 預設 True。",
    },
    "figma_api": {
        "module": "src.adapters.figma_adapter",
        "class_name": "FigmaAdapter",
        "risk_level": "medium",
        "requires_approval": False,
        "auth_required": True,
        "allowed_agents": ["pixel"],
        "timeout_seconds": 30,
        "status": "active",
        "description": "Figma API 讀取設計稿節點。唯讀，不寫入。",
    },
    "chrome_cdp": {
        "module": "src.adapters.chrome_cdp_adapter",
        "class_name": "ChromeCDPAdapter",
        "risk_level": "critical",
        "requires_approval": True,
        "auth_required": False,
        "allowed_agents": ["ori", "sage"],
        "timeout_seconds": 60,
        "status": "active",
        "description": "Playwright/CDP 瀏覽器自動化。dry_run 預設 True，寫入操作需審核。",
    },
    "line_notify": {
        "module": "src.adapters.line_adapter",
        "class_name": "LineNotifyAdapter",
        "risk_level": "low",
        "requires_approval": False,
        "auth_required": True,
        "allowed_agents": ["ori", "craft", "sage"],
        "timeout_seconds": 10,
        "status": "active",
        "description": "LINE Notify 推播通知。已在生產環境使用。",
    },
    "anthropic_vision": {
        "module": "src.agents.screenshot_analyzer",
        "class_name": "ScreenshotAnalyzer",
        "risk_level": "low",
        "requires_approval": False,
        "auth_required": True,
        "allowed_agents": ["ori", "craft"],
        "timeout_seconds": 60,
        "status": "active",
        "description": "Claude Vision 截圖分析。用於 FlowLab 選品截圖提取。",
    },
    "video_frame_extractor": {
        "module": "src.adapters.video_adapter",
        "class_name": "VideoFrameAdapter",
        "risk_level": "low",
        "requires_approval": False,
        "auth_required": False,
        "allowed_agents": ["ori", "craft"],
        "timeout_seconds": 120,
        "status": "active",
        "description": "影片關鍵幀提取（ffmpeg M2）。使用 ffmpeg subprocess 提取關鍵幀，輸出 JPEG。",
    },
}


def get_adapter_meta(name: str) -> dict | None:
    """取得 adapter 元資料，不存在回傳 None"""
    return ADAPTER_REGISTRY.get(name)


def list_adapters(status: str | None = None) -> list[dict]:
    """列出所有（或特定 status 的）adapter 元資料"""
    items = [{"name": k, **v} for k, v in ADAPTER_REGISTRY.items()]
    if status:
        items = [i for i in items if i.get("status") == status]
    return items


def get_risk_level(adapter_name: str) -> str:
    """取得 adapter 的 risk_level，預設 medium"""
    meta = ADAPTER_REGISTRY.get(adapter_name, {})
    return meta.get("risk_level", "medium")
