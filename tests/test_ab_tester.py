"""Tests for ABTester — 4 test cases."""
import pytest
from src.content.ab_tester import compare_drafts, ABTestResult


# ── 1. compare_drafts returns ABTestResult with all fields ────────────────────

def test_compare_drafts_returns_ab_test_result():
    draft_a = {"hook": "Hook A", "body": "Some body text here."}
    draft_b = {"hook": "Hook B", "body": "Another body text here."}
    result = compare_drafts(draft_a, draft_b)
    assert isinstance(result, ABTestResult)
    assert hasattr(result, "winner_idx")
    assert hasattr(result, "winner_score")
    assert hasattr(result, "scores")
    assert hasattr(result, "summary")


# ── 2. Better draft (with hook question + number) wins ────────────────────────

def test_better_draft_with_question_and_number_wins():
    """Draft A has a question and a number in the hook → higher score."""
    draft_a = {"hook": "你知道嗎？3個方法讓你省錢！", "body": "根據研究數據顯示這個方法有效。"}
    draft_b = {"hook": "一般介紹", "body": "普通的介紹內容。"}
    result = compare_drafts(draft_a, draft_b)
    assert result.winner_idx == 0
    assert result.scores[0] > result.scores[1]


# ── 3. Empty drafts → scores=[0.0, 0.0], winner_idx=0 ────────────────────────

def test_empty_drafts_returns_zero_scores():
    result = compare_drafts({}, {})
    assert result.scores == [0.0, 0.0]
    assert result.winner_idx == 0


# ── 4. scores list has exactly 2 elements ─────────────────────────────────────

def test_scores_list_has_two_elements():
    draft_a = {"content": "Some content A."}
    draft_b = {"content": "Some content B."}
    result = compare_drafts(draft_a, draft_b)
    assert len(result.scores) == 2
