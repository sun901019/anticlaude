# tests/test_orio_scorer_standalone.py
# Tests for src/content/orio_scorer.py
# All entries in English only.

import pytest
from src.content.orio_scorer import score_topic, rank_topics, OrioScore

# ── Sample topics ─────────────────────────────────────────────────────────────

AI_TOPIC = {
    "cluster_label": "AI Agent automation workflow",
    "merged_summary": "Claude AI model development, LLM toolchain integration for productivity",
    "post_type": "tech_trend",
    "source": "arxiv",
}

NEGATIVE_TOPIC = {
    "cluster_label": "celebrity gossip entertainment",
    "merged_summary": "Entertainment news, celebrity drama, fashion and lifestyle",
    "post_type": "lifestyle",
    "source": "unknown",
}

EMPTY_TOPIC = {}


# ── Test 1: score_topic(AI_TOPIC) → composite_score >= 0.45 and passed=True ──

def test_ai_topic_passes_threshold():
    result = score_topic(AI_TOPIC)
    assert isinstance(result, OrioScore)
    assert result.composite_score >= 0.45
    assert result.passed is True


# ── Test 2: score_topic(NEGATIVE_TOPIC) has lower composite than AI_TOPIC ────

def test_negative_topic_lower_composite_than_ai():
    ai_result = score_topic(AI_TOPIC)
    neg_result = score_topic(NEGATIVE_TOPIC)
    assert neg_result.composite_score < ai_result.composite_score


# ── Test 3: score_topic(AI_TOPIC) source_trust_score == 0.95 (arxiv) ─────────

def test_ai_topic_arxiv_source_trust():
    result = score_topic(AI_TOPIC)
    assert result.source_trust_score == 0.95


# ── Test 4: score_topic(EMPTY_TOPIC) does not raise — returns OrioScore ───────

def test_empty_topic_no_exception():
    result = score_topic(EMPTY_TOPIC)
    assert isinstance(result, OrioScore)


# ── Test 5: composite_score is in [0.0, 1.0] for any scored topic ─────────────

def test_composite_score_range():
    for topic in (AI_TOPIC, NEGATIVE_TOPIC, EMPTY_TOPIC):
        result = score_topic(topic)
        assert 0.0 <= result.composite_score <= 1.0, (
            f"composite_score {result.composite_score} out of [0.0, 1.0]"
        )


# ── Test 6: passed == (composite_score >= 0.45) for AI_TOPIC ─────────────────

def test_passed_matches_threshold_for_ai_topic():
    result = score_topic(AI_TOPIC)
    assert result.passed == (result.composite_score >= 0.45)


# ── Test 7: score_topic(AI_TOPIC) reasons list is not empty ──────────────────

def test_ai_topic_reasons_nonempty():
    result = score_topic(AI_TOPIC)
    assert isinstance(result.reasons, list)
    assert len(result.reasons) > 0


# ── Test 8: rank_topics([AI_TOPIC, NEGATIVE_TOPIC]) returns only passed=True ─

def test_rank_topics_only_passed():
    results = rank_topics([AI_TOPIC, NEGATIVE_TOPIC])
    for item in results:
        composite = item["orio_score"]["composite"]
        assert composite >= 0.45, (
            f"Item with composite {composite} should not have passed"
        )


# ── Test 9: rank_topics result is sorted by composite descending ──────────────

def test_rank_topics_sorted_descending():
    results = rank_topics([AI_TOPIC, NEGATIVE_TOPIC])
    composites = [item["orio_score"]["composite"] for item in results]
    assert composites == sorted(composites, reverse=True)


# ── Test 10: rank_topics result topics contain "orio_score" dict with required keys ──

def test_rank_topics_orio_score_keys():
    results = rank_topics([AI_TOPIC])
    assert len(results) >= 1
    orio_score = results[0]["orio_score"]
    for key in ("topic_fit", "persona_fit", "source_trust", "composite", "reasons"):
        assert key in orio_score, f"Missing key in orio_score: {key}"


# ── Test 11: rank_topics([]) returns empty list ───────────────────────────────

def test_rank_topics_empty_input():
    result = rank_topics([])
    assert result == []


# ── Test 12: OrioScore fields all in [0.0, 1.0] ──────────────────────────────

def test_ai_topic_score_fields_in_range():
    result = score_topic(AI_TOPIC)
    for field_name, value in (
        ("topic_fit_score", result.topic_fit_score),
        ("persona_fit_score", result.persona_fit_score),
        ("source_trust_score", result.source_trust_score),
    ):
        assert 0.0 <= value <= 1.0, (
            f"{field_name} = {value} is out of [0.0, 1.0]"
        )
