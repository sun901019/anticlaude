# encoding: utf-8
"""Tests for src/content/geo_validator.py — 9 tests."""
import pytest
from src.content.geo_validator import validate_geo_compliance, validate_drafts_batch


class TestGeoValidator:

    def test_empty_text_fails(self):
        """Empty string must fail with score 0.0."""
        result = validate_geo_compliance("")
        assert result.passed is False
        assert result.score == 0.0

    def test_clean_content_passes(self):
        """Human-sounding content with first-person and specific details should pass."""
        text = (
            "我發現一個方法讓你每週節省 4 小時的整理時間。"
            "說真的，這不是什麼魔法，是 30 件商品賣掉後學到的。"
        )
        result = validate_geo_compliance(text)
        assert result.passed is True
        assert result.score >= 0.7

    def test_forbidden_words_detected(self):
        """Text containing forbidden AI-fingerprint words must generate violations."""
        text = (
            "此外，值得注意的是這個策略至關重要，我們必須認真考慮。"
            "說真的，賣出 10 件後我才明白這件事的重要性。"
        )
        result = validate_geo_compliance(text)
        assert len(result.violations) > 0
        # Check that forbidden words are flagged
        violation_text = " ".join(result.violations)
        assert "此外" in violation_text or "至關重要" in violation_text

    def test_forbidden_words_lower_score(self):
        """Text stuffed with many forbidden words should score below 0.7."""
        text = (
            "此外值得注意的是，不可否認這至關重要，不可或缺。"
            "彰顯深度探討格局，生態系展望未來充滿期待，在這種情況下"
            "值得一提的是總而言之，不僅如此毋庸置疑。"
            "我覺得這樣做很好，賣出 20 件後的心得是這樣的。"
        )
        result = validate_geo_compliance(text)
        assert result.score < 0.7

    def test_too_short_fails(self):
        """Content with too few characters and additional penalties must fail the gate."""
        # "abc" is 3 chars (< 30) → penalty 0.15 for length
        # no first-person → penalty 0.05
        # no specific details → penalty 0.05
        # forbidden words present → penalty >= 0.05
        # total >= 0.30 → score <= 0.70, but we need <0.70 so add more forbidden words
        text = "此外值得注意的是不可否認"  # 12 chars, has 3 forbidden words
        result = validate_geo_compliance(text)
        assert result.passed is False

    def test_has_first_person_boosts_score(self):
        """Content with first-person voice should have has_first_person == True."""
        text = "我覺得這個方法很實用，試了之後賣出 15 件，效果超乎預期。"
        result = validate_geo_compliance(text)
        assert result.details["has_first_person"] is True
        # No first_person warning should be in warnings
        assert not any("第一人稱" in w for w in result.warnings)

    def test_specific_details_detected(self):
        """Content mentioning numeric details should set has_specific_details to True."""
        text = "老實說，賣出 30 件之後我才真正搞懂選品的邏輯，這是真實心得。"
        result = validate_geo_compliance(text)
        assert result.details["has_specific_details"] is True

    def test_validate_drafts_batch_all_pass(self):
        """Two clean drafts should both pass and all_passed == True."""
        draft_a = {"content": "我發現每週只要 3 小時，就能整理好 50 件商品的庫存。說真的很值得。"}
        draft_b = {"content": "老實說，賣出 20 件後我才明白定價的重要性，這是我的真實心得。"}
        result = validate_drafts_batch([draft_a, draft_b])
        assert result["all_passed"] is True
        assert result["pass_count"] == 2
        assert result["total"] == 2

    def test_validate_drafts_batch_mixed(self):
        """One clean draft + one with many forbidden words → all_passed == False."""
        clean = {"content": "我覺得這個方法真的有效，試過之後賣出 25 件，數字不騙人。"}
        bad = {
            "content": (
                "此外值得注意的是不可否認這至關重要不可或缺彰顯深度探討格局"
                "生態系展望未來充滿期待在這種情況下值得一提的是總而言之"
            )
        }
        result = validate_drafts_batch([clean, bad])
        assert result["all_passed"] is False
        assert result["total"] == 2
