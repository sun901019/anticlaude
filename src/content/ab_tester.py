"""A/B Draft Comparison — scores two draft variants and picks the better one."""
import re
from dataclasses import dataclass


@dataclass
class ABTestResult:
    winner_idx: int
    winner_score: float
    scores: list
    summary: str


def _score_draft(draft: dict) -> float:
    text = " ".join(str(draft.get(k, "")) for k in ("version_a", "version_b", "hook", "body", "content")).strip()
    if not text:
        return 0.0
    score = 5.0
    length = len(text)
    if 80 <= length <= 200:
        score += 1.0
    elif length > 400:
        score -= 1.0
    if re.search(r'[？?]', text[:80]):
        score += 0.5
    if re.search(r'\d+', text[:80]):
        score += 0.5
    score += 0.2 * sum(1 for s in ["是", "因為", "根據", "研究", "數據", "結論"] if s in text)
    if re.search(r'[\U0001F300-\U0001FFFF]', text):
        score += 0.3
    return min(score, 10.0)


def compare_drafts(draft_a: dict, draft_b: dict) -> ABTestResult:
    score_a = _score_draft(draft_a)
    score_b = _score_draft(draft_b)
    winner_idx = 0 if score_a >= score_b else 1
    return ABTestResult(
        winner_idx=winner_idx,
        winner_score=max(score_a, score_b),
        scores=[score_a, score_b],
        summary=f"版本{'A' if winner_idx == 0 else 'B'} 勝出（{score_a:.1f} vs {score_b:.1f}）",
    )
