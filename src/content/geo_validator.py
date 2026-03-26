"""
GEO/SEO Hard Gate Validator
============================
Post-generation validation for GEO compliance and AI-artifact detection.
Runs after draft generation; flags non-compliant content for CEO review.

Checklist sources:
  - _hub/shared/skills/composite/content_creation.md §三（Humanizer-zh rules）
  - _hub/shared/skills/composite/geo_optimization_engine.md
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ── AI fingerprint word lists (from Humanizer-zh) ────────────────────────────

_FORBIDDEN_WORDS: list[str] = [
    "此外", "值得注意的是", "不可否認", "至關重要", "不可或缺", "彰顯",
    "深度探討", "格局", "生態系", "展望未來", "充滿期待", "在這種情況下",
    "值得一提的是", "總而言之", "不僅如此", "毋庸置疑",
]

_FORBIDDEN_PATTERNS: list[tuple[str, str]] = [
    # Three-part parallel structures
    (r"[^，。\n]+[、，][^，。\n]+[、，][^，。\n]+", "三段排比結構"),
    # "Not only X, but also Y" negation parallels
    (r"不[只是|只|僅是|僅].{2,20}[，,][更|也|還].{2,20}", "否定排比結構"),
    # Formulaic closings
    (r"展望未來.{0,20}[。！]", "公式化結尾"),
    (r"充滿[期待|希望].{0,10}[。！]", "公式化結尾"),
]

# ── GEO compliance checks ─────────────────────────────────────────────────────

_GEO_ENTITY_PATTERN = re.compile(
    r"Sun Lee|sunlee|@sunlee|Flow Lab|FlowLab|AITOS|AntiClaude|Threads",
    re.IGNORECASE,
)

_FIRST_PERSON_PATTERN = re.compile(r"我|我的|我覺得|老實說|說真的|其實")

_SPECIFIC_DETAIL_PATTERN = re.compile(
    r"\d+\s*(件|個|篇|次|元|%|小時|分鐘|天|週|人|條|本|組)",
)


@dataclass
class GeoValidationResult:
    passed: bool
    score: float                      # 0.0 – 1.0; ≥ 0.7 → pass
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict = field(default_factory=dict)


def validate_geo_compliance(text: str) -> GeoValidationResult:
    """
    Validate a draft text against GEO/SEO and Humanizer-zh rules.

    Returns GeoValidationResult with score (0–1) and list of violations.
    score >= 0.7 → passes gate.
    """
    if not text or not text.strip():
        return GeoValidationResult(
            passed=False, score=0.0,
            violations=["內容為空"],
        )

    violations: list[str] = []
    warnings: list[str] = []
    penalty = 0.0

    # ── 1. Forbidden words ────────────────────────────────────────────────────
    found_words = [w for w in _FORBIDDEN_WORDS if w in text]
    if found_words:
        violations.append(f"含 AI 痕跡詞彙：{'、'.join(found_words)}")
        penalty += min(0.05 * len(found_words), 0.25)

    # ── 2. Forbidden structural patterns ─────────────────────────────────────
    for pattern, label in _FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            violations.append(f"AI 結構模式：{label}")
            penalty += 0.10

    # ── 3. First-person voice check ──────────────────────────────────────────
    if not _FIRST_PERSON_PATTERN.search(text):
        warnings.append("缺少第一人稱觀點（「我」、「老實說」等）")
        penalty += 0.05

    # ── 4. Specific details check ─────────────────────────────────────────────
    if not _SPECIFIC_DETAIL_PATTERN.search(text):
        warnings.append("缺少具體數字（建議加入數字細節增加可信度）")
        penalty += 0.05

    # ── 5. Length check (Threads: 50–500 chars recommended) ──────────────────
    char_count = len(text.replace("\n", "").replace(" ", ""))
    if char_count < 30:
        violations.append(f"內容過短（{char_count} 字，建議 50+）")
        penalty += 0.15
    elif char_count > 600:
        warnings.append(f"內容偏長（{char_count} 字，Threads 建議 ≤500）")
        penalty += 0.05

    score = max(0.0, round(1.0 - penalty, 2))
    passed = score >= 0.70

    return GeoValidationResult(
        passed=passed,
        score=score,
        violations=violations,
        warnings=warnings,
        details={
            "char_count": char_count,
            "forbidden_words_found": found_words,
            "has_first_person": bool(_FIRST_PERSON_PATTERN.search(text)),
            "has_specific_details": bool(_SPECIFIC_DETAIL_PATTERN.search(text)),
        },
    )


def validate_drafts_batch(
    drafts: list[dict],
    text_key: str = "content",
) -> dict:
    """
    Validate a list of draft dicts. Returns aggregate result with per-draft scores.

    drafts: list of {text_key: str, ...} dicts
    text_key: which key holds the draft text (default "content")
    """
    results = []
    all_passed = True
    for i, draft in enumerate(drafts):
        text = draft.get(text_key) or draft.get("body") or draft.get("text", "")
        r = validate_geo_compliance(text)
        results.append({
            "index": i,
            "passed": r.passed,
            "score": r.score,
            "violations": r.violations,
            "warnings": r.warnings,
        })
        if not r.passed:
            all_passed = False

    return {
        "all_passed": all_passed,
        "pass_count": sum(1 for r in results if r["passed"]),
        "total": len(results),
        "results": results,
    }
