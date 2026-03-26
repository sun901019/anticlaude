"""
Topic Fit Gate — 過濾不符合品牌定位的主題

品牌定位：台灣科技工作者受眾，聚焦 AI工具 / 職涯 / 個人成長
"""
from dataclasses import dataclass, field


# 品牌核心領域
ALLOWED_DOMAINS = {
    "AI工具", "AI應用", "職涯", "個人成長", "創業", "科技趨勢",
    "生產力", "學習方法", "遠距工作", "工具推薦", "數據", "自動化",
}

# 封鎖關鍵字（出現即直接拒絕）
BLOCKED_KEYWORDS = [
    "政治", "選舉", "統獨", "候選人",
    "業配", "贊助", "合作碼", "推薦碼",
]

# AI 相關關鍵字（加分訊號）
_AI_KEYWORDS = {"ai", "gpt", "claude", "llm", "自動化", "agent", "機器學習", "深度學習"}

# 工程師導向關鍵字（輕微扣分）
_ENGINEER_SIGNALS = {"工程師", "後端", "前端", "演算法", "程式碼", "debug", "deployment"}


@dataclass
class TopicFitResult:
    score: float         # 0.0 ~ 1.0
    passed: bool         # score >= 0.5 → pass
    reasons: list[str] = field(default_factory=list)
    blocked_by: str = ""


def check_topic_fit(topic: dict) -> TopicFitResult:
    """
    檢查主題是否符合品牌定位。

    Args:
        topic: 含 cluster_label, post_type, merged_summary, category(optional)

    Returns:
        TopicFitResult
    """
    label = topic.get("cluster_label", "")
    post_type = topic.get("post_type", "")
    summary = (topic.get("merged_summary") or "").lower()
    category = topic.get("category", "")
    label_lower = label.lower()

    reasons: list[str] = []

    # ── 封鎖檢查（立即拒絕）─────────────────────────────────────────
    for kw in BLOCKED_KEYWORDS:
        if kw in label or kw in summary:
            return TopicFitResult(
                score=0.0, passed=False,
                reasons=[f"含封鎖關鍵字：{kw}"],
                blocked_by=kw,
            )

    score = 0.5  # 基礎分

    # ── 加分訊號 ────────────────────────────────────────────────────
    if post_type in ("趨勢解讀", "觀點分享", "個人經驗", "職涯建議"):
        score += 0.2
        reasons.append(f"貼文類型 {post_type!r} 與品牌高度匹配")

    if any(d in label or d in category for d in ALLOWED_DOMAINS):
        score += 0.2
        reasons.append("主題屬於品牌核心領域")

    if any(kw in label_lower or kw in summary for kw in _AI_KEYWORDS):
        score += 0.1
        reasons.append("含 AI 相關關鍵字，符合主要受眾興趣")

    # ── 扣分訊號 ────────────────────────────────────────────────────
    if any(sig in summary or sig in label_lower for sig in _ENGINEER_SIGNALS):
        score -= 0.15
        reasons.append("偏向工程師受眾，一般科技工作者相關性較低")

    score = round(max(0.0, min(1.0, score)), 2)

    if not reasons:
        reasons.append("無明顯加分或扣分因素，維持基礎分 0.5")

    return TopicFitResult(score=score, passed=score >= 0.5, reasons=reasons)
