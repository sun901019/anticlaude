"""
Engagement Plan — 第一小時互動策略

根據 Threads 演算法研究（threads_algorithm_field_research_integration_20260317）：
- 發文後 60 分鐘內演算法決定第二波推播
- First-reply 在 5 分鐘內偽造高互動信號
- 台灣科技受眾三個高峰：通勤 07:30-08:30、午休 12:00-13:00、夜間 21:00-22:30
"""
from dataclasses import dataclass, field


@dataclass
class EngagementPlan:
    best_slots: list[str]          # 建議發文時段（如 "07:30–08:30"）
    first_reply_within: int        # 建議 first_reply 發送時限（分鐘）
    first_reply_tip: str           # first_reply 寫作提示
    first_hour_actions: list[str]  # 第一小時行動清單
    rationale: str


# 台灣科技受眾三大高峰時段
_PEAK_SLOTS = {
    "morning": ("07:30", "08:30"),
    "lunch":   ("12:00", "13:00"),
    "evening": ("21:00", "22:30"),
}

# post_type → 推薦時段（順序代表優先度）
_TYPE_SLOT_MAP: dict[str, list[str]] = {
    "趨勢解讀": ["morning", "evening"],
    "工具介紹": ["lunch",   "morning"],
    "觀點分享": ["evening", "morning"],
    "數據分析": ["morning", "lunch"],
    "個人經驗": ["evening", "morning"],
    "職涯建議": ["morning", "evening"],
    "事件評論": ["morning"],          # 時事必須快
}

# format → first_reply 寫作提示
_REPLY_TIP: dict[str, str] = {
    "short":  "補充一個 short 版沒放進去的具體細節，或問讀者遇過類似情況嗎",
    "thread": "在第一串下留言預告後續串的內容，讓等待的讀者知道還有更多",
    "long":   "問一個開放式問題，讓讀者有回應的入口（例：你覺得這個在台灣適用嗎？）",
}


def build_engagement_plan(topic: dict, format_type: str = "long") -> EngagementPlan:
    """
    為主題建立第一小時互動計畫。

    Args:
        topic:       含 post_type, cluster_label 的主題 dict
        format_type: "short" | "long" | "thread"

    Returns:
        EngagementPlan
    """
    post_type = topic.get("post_type", "趨勢解讀")

    slot_keys = _TYPE_SLOT_MAP.get(post_type, ["morning", "evening"])
    best_slots = [f"{_PEAK_SLOTS[k][0]}–{_PEAK_SLOTS[k][1]}" for k in slot_keys]

    first_reply_within = 5
    first_reply_tip = _REPLY_TIP.get(format_type, _REPLY_TIP["long"])

    actions = [
        f"發文後 {first_reply_within} 分鐘內發 first_reply（見草稿 first_reply 欄位）",
        "發文後 15 分鐘：回覆所有留言（哪怕只有 1 則）",
        "發文後 30 分鐘：觀察 views/likes 比例（> 5% 代表演算法已開始推）",
        "發文後 60 分鐘：若互動率 < 2%，考慮刪除後改在另一時段重發",
    ]
    if format_type == "thread":
        actions.insert(1, "分串貼文：主串發出後每隔 2 分鐘追加後續串，不要一次全貼")

    rationale = (
        f"Threads 演算法在發文後 60 分鐘內決定是否進行第二波推播。"
        f"「{post_type}」類主題的台灣科技受眾在 {' / '.join(best_slots)} 最活躍。"
        f"First-reply 在 {first_reply_within} 分鐘內能提升初始互動信號，觸發更廣泛推播。"
    )

    return EngagementPlan(
        best_slots=best_slots,
        first_reply_within=first_reply_within,
        first_reply_tip=first_reply_tip,
        first_hour_actions=actions,
        rationale=rationale,
    )
