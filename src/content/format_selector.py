"""
Format Selector — 根據主題特性選擇最適 Threads 發文格式

格式定義：
  short   80-150 字，工具介紹 / 個人經驗 / 時事評論
  long    200-300 字，趨勢解讀 / 觀點分享 / 職涯建議 / 數據分析
  thread  每串 ≤150 字，分多串發布，適合複雜度高的深度主題
"""
from dataclasses import dataclass


@dataclass
class FormatRecommendation:
    format: str        # "short" | "long" | "thread"
    rationale: str
    max_words: int
    use_thread: bool


# post_type → (format, rationale, max_words)
_FORMAT_RULES: dict[str, tuple[str, str, int]] = {
    "趨勢解讀":  ("long",  "趨勢需要背景鋪陳，長版讓讀者理解為什麼這件事重要", 300),
    "工具介紹":  ("short", "工具介紹重點明確，短版提高完讀率", 150),
    "觀點分享":  ("long",  "觀點需要論述支撐，長版建立說服力", 280),
    "數據分析":  ("long",  "數據需要解讀，長版讓數字有意義", 280),
    "個人經驗":  ("short", "個人故事要抓住眼球，短版降低讀者疲勞", 150),
    "職涯建議":  ("long",  "職涯類讀者願意投入時間，長版增加權威感", 300),
    "事件評論":  ("short", "時事評論要快、要準，短版保持時效性", 150),
}

# 若 summary 超過此長度且為深度類型 → 建議分串
_THREAD_SUMMARY_LEN = 500
_THREAD_ELIGIBLE_TYPES = {"趨勢解讀", "觀點分享", "職涯建議"}


def select_format(topic: dict) -> FormatRecommendation:
    """
    根據主題選擇格式。

    Args:
        topic: 含 post_type, merged_summary, cluster_label 的 dict

    Returns:
        FormatRecommendation
    """
    post_type = topic.get("post_type", "趨勢解讀")
    summary = topic.get("merged_summary", "")

    fmt, rationale, max_words = _FORMAT_RULES.get(
        post_type, ("long", "預設長版，適合深度內容", 280)
    )

    use_thread = (
        len(summary) > _THREAD_SUMMARY_LEN
        and post_type in _THREAD_ELIGIBLE_TYPES
    )
    if use_thread:
        fmt = "thread"
        rationale = (
            f"內容複雜（素材 {len(summary)} 字），建議分串以保持每串可讀性"
        )
        max_words = 150  # per-thread-post limit

    return FormatRecommendation(
        format=fmt,
        rationale=rationale,
        max_words=max_words,
        use_thread=use_thread,
    )
