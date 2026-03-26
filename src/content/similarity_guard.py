"""
Similarity Guard — 防止連續發相似主題

使用 Jaccard 詞重疊率（不依賴外部 NLP 套件），
搭配時間冷卻期（lookback_days）過濾近期貼文。
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class SimilarityResult:
    is_too_similar: bool
    max_similarity: float   # 0.0 ~ 1.0
    similar_to: str         # 最相似貼文的摘要（前 60 字）
    reasons: list[str] = field(default_factory=list)


def _jaccard(text_a: str, text_b: str) -> float:
    """Jaccard 詞重疊率（以空格分詞，不含 stopwords）"""
    tokens_a = set(text_a.lower().split())
    tokens_b = set(text_b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


def check_similarity(
    new_topic: dict,
    recent_posts: list[dict],
    lookback_days: int = 7,
    threshold: float = 0.35,
) -> SimilarityResult:
    """
    檢查新主題是否與近期貼文過於相似。

    Args:
        new_topic:     含 cluster_label, merged_summary
        recent_posts:  近期貼文 list，每筆含 text/content/hook 及 posted_at/created_at
        lookback_days: 回看天數（預設 7 天）
        threshold:     Jaccard 門檻（>= threshold → 視為相似，預設 0.35）

    Returns:
        SimilarityResult
    """
    label = new_topic.get("cluster_label", "")
    summary = new_topic.get("merged_summary", "")
    new_text = f"{label} {summary}"

    cutoff = datetime.now() - timedelta(days=lookback_days)

    max_sim = 0.0
    most_similar = ""
    reasons: list[str] = []

    for post in recent_posts:
        # 日期過濾
        raw_date = post.get("posted_at") or post.get("created_at") or ""
        if raw_date:
            try:
                if datetime.fromisoformat(raw_date[:19]) < cutoff:
                    continue
            except ValueError:
                pass

        post_text = (
            post.get("text")
            or post.get("content")
            or post.get("hook")
            or ""
        )
        sim = _jaccard(new_text, post_text)
        if sim > max_sim:
            max_sim = sim
            most_similar = post_text[:60] + "…" if len(post_text) > 60 else post_text

    is_too_similar = max_sim >= threshold
    if is_too_similar:
        reasons.append(
            f"與近 {lookback_days} 天貼文詞彙重疊率 {max_sim:.0%}（門檻 {threshold:.0%}）"
        )
        reasons.append(f"最相似貼文：{most_similar}")

    return SimilarityResult(
        is_too_similar=is_too_similar,
        max_similarity=round(max_sim, 3),
        similar_to=most_similar,
        reasons=reasons,
    )
