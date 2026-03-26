"""
Approval Matrix — 批准門控正規化
==================================
集中定義哪些 action_type 對應哪個 risk_level，
避免各呼叫方自行決定風險等級造成不一致。

來源：aitos_token_memory_skill_integration_consolidation_20260319.md §5.2
      「公開發文 / 核心修改 / 高風險 adapter / 重要商業決策 → 必須過審核閘」

使用方式：
    from src.workflows.approval_matrix import get_risk_level, requires_human
    risk = get_risk_level("publish_post")    # → "high"
    human = requires_human("publish_post")  # → True
"""
from typing import Literal

RiskLevel = Literal["low", "medium", "high", "critical"]

# action_type → (risk_level, requires_human_approval, is_irreversible, rationale)
# is_irreversible=True means the action has external side-effects that cannot be undone
_MATRIX: dict[str, tuple[RiskLevel, bool, bool, str]] = {
    # ── 內容發布 ────────────────────────────────────────────────────────────────
    "publish_post":            ("high",     True,  True,  "公開發文不可逆，影響品牌形象"),
    "delete_post":             ("high",     True,  True,  "刪除發文不可逆"),
    "schedule_post":           ("medium",   True,  False, "排程發文可取消，但有時效性"),
    "promote_product":         ("high",     True,  True,  "商品推廣發布至受眾，不可逆"),

    # ── 草稿 / 內容生成 ─────────────────────────────────────────────────────────
    "draft_generation":        ("low",      False, False, "內部草稿，不對外，可自動執行"),
    "content_selection":       ("low",      False, False, "選題建議，不強制，可自動執行"),
    "screenshot_analysis":     ("low",      False, False, "無外部副作用，結果進審核池"),

    # ── 商業 / 電商決策 ─────────────────────────────────────────────────────────
    "approve_purchase":        ("high",     True,  True,  "商業採購影響現金流"),
    "reject_candidate":        ("medium",   True,  False, "拒絕選品有時需附理由"),
    "pricing_update":          ("high",     True,  True,  "定價影響毛利率，立即生效"),
    "selection_report":        ("low",      False, False, "選品分析報告，供參考，不執行"),

    # ── 系統 / 架構修改 ─────────────────────────────────────────────────────────
    "system_modification":     ("critical", True,  False, "修改核心 Python 邏輯，需沙盒 + 審核"),
    "skill_update":            ("medium",   True,  False, "更新 AI skill 可能影響生產行為"),
    "prompt_update":           ("medium",   False, False, "修改 prompt，低風險但建議記錄"),
    "schema_migration":        ("critical", True,  True,  "DB Schema 變更不可逆"),

    # ── 外部 Adapter / API ───────────────────────────────────────────────────────
    "external_api_call":       ("high",     True,  False, "呼叫外部系統，有費用或副作用"),
    "x_publish":               ("high",     True,  True,  "X 發文不可逆，高曝光風險"),
    "figma_read":              ("medium",   False, False, "Figma 唯讀，無副作用"),
    "chrome_automation":       ("critical", True,  False, "瀏覽器自動化可能觸發反爬蟲"),

    # ── 研究 / 數據 ─────────────────────────────────────────────────────────────
    "content_research":        ("low",      False, False, "資料蒐集，無外部副作用"),
    "market_analysis":         ("low",      False, False, "市場分析，唯讀"),
    "weekly_report":           ("low",      False, False, "週報生成，內部使用"),

    # ── 截圖分析（FlowLab）──────────────────────────────────────────────────────
    "approve_screenshot_analysis": ("low",  False, False, "確認 AI 提取結果，低風險"),
}


def get_risk_level(action_type: str) -> RiskLevel:
    """取得 action_type 的 risk_level，未定義的 action 預設 medium"""
    entry = _MATRIX.get(action_type)
    return entry[0] if entry else "medium"


def requires_human(action_type: str) -> bool:
    """判斷 action_type 是否需要人工審核"""
    entry = _MATRIX.get(action_type)
    return entry[1] if entry else False


def is_irreversible(action_type: str) -> bool:
    """判斷 action_type 是否不可逆（有外部副作用，核准後無法撤銷）"""
    entry = _MATRIX.get(action_type)
    return entry[2] if entry else False


def get_rationale(action_type: str) -> str:
    """取得風險理由說明"""
    entry = _MATRIX.get(action_type)
    return entry[3] if entry else "未定義的 action_type，預設 medium 風險"


def classify(action_type: str) -> dict:
    """一次取得完整分類資訊"""
    return {
        "action_type": action_type,
        "risk_level": get_risk_level(action_type),
        "requires_human": requires_human(action_type),
        "is_irreversible": is_irreversible(action_type),
        "rationale": get_rationale(action_type),
    }


def list_high_risk_actions() -> list[str]:
    """列出所有 high 或 critical 且需要人工審核的 action"""
    return [
        k for k, v in _MATRIX.items()
        if v[0] in ("high", "critical") and v[1]
    ]
