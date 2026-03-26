"""
Tests for src/content/ — Format Selector, Topic Fit Gate, Similarity Guard
"""
import pytest
from src.content.format_selector import select_format, FormatRecommendation
from src.content.topic_fit import check_topic_fit, TopicFitResult
from src.content.similarity_guard import check_similarity, SimilarityResult


# ── Format Selector ───────────────────────────────────────────────────────────

class TestFormatSelector:
    def test_short_for_tool_intro(self):
        topic = {"post_type": "工具介紹", "merged_summary": "簡短介紹"}
        result = select_format(topic)
        assert result.format == "short"
        assert result.max_words == 150
        assert not result.use_thread

    def test_long_for_trend(self):
        topic = {"post_type": "趨勢解讀", "merged_summary": "x" * 100}
        result = select_format(topic)
        assert result.format == "long"
        assert result.max_words == 300

    def test_thread_for_complex_trend(self):
        # summary > 500 chars + eligible type → thread
        topic = {"post_type": "趨勢解讀", "merged_summary": "x" * 600}
        result = select_format(topic)
        assert result.format == "thread"
        assert result.use_thread is True
        assert result.max_words == 150

    def test_no_thread_for_tool_intro_even_long_summary(self):
        topic = {"post_type": "工具介紹", "merged_summary": "x" * 600}
        result = select_format(topic)
        assert result.format == "short"
        assert not result.use_thread

    def test_unknown_post_type_defaults_to_long(self):
        topic = {"post_type": "未知類型", "merged_summary": "x"}
        result = select_format(topic)
        assert result.format == "long"

    def test_returns_dataclass(self):
        result = select_format({"post_type": "觀點分享", "merged_summary": ""})
        assert isinstance(result, FormatRecommendation)


# ── Topic Fit Gate ─────────────────────────────────────────────────────────────

class TestTopicFit:
    def test_ai_topic_passes(self):
        topic = {
            "cluster_label": "GPT-5 最新功能解析",
            "post_type": "趨勢解讀",
            "merged_summary": "openai gpt ai 工具",
        }
        result = check_topic_fit(topic)
        assert result.passed
        assert result.score >= 0.5

    def test_political_topic_blocked(self):
        topic = {
            "cluster_label": "台灣政治選舉分析",
            "post_type": "事件評論",
            "merged_summary": "選舉候選人分析",
        }
        result = check_topic_fit(topic)
        assert not result.passed
        assert result.score == 0.0
        assert result.blocked_by != ""

    def test_sponsored_blocked(self):
        topic = {
            "cluster_label": "推薦碼優惠活動",
            "post_type": "工具介紹",
            "merged_summary": "使用推薦碼享折扣",
        }
        result = check_topic_fit(topic)
        assert not result.passed

    def test_engineer_signal_reduces_score(self):
        topic = {
            "cluster_label": "後端架構設計",
            "post_type": "工具介紹",
            "merged_summary": "工程師後端演算法程式碼",
        }
        result = check_topic_fit(topic)
        # Still may pass depending on score, but score should be lower
        assert result.score <= 0.5

    def test_returns_reasons(self):
        topic = {
            "cluster_label": "AI 生產力工具推薦",
            "post_type": "趨勢解讀",
            "merged_summary": "ai 自動化工具",
        }
        result = check_topic_fit(topic)
        assert isinstance(result, TopicFitResult)
        assert isinstance(result.reasons, list)
        assert len(result.reasons) > 0


# ── Similarity Guard ───────────────────────────────────────────────────────────

class TestSimilarityGuard:
    def _recent_post(self, text: str, days_ago: int = 1) -> dict:
        from datetime import datetime, timedelta
        dt = datetime.now() - timedelta(days=days_ago)
        return {"text": text, "posted_at": dt.isoformat()}

    def test_no_recent_posts_not_similar(self):
        topic = {"cluster_label": "AI 工具", "merged_summary": "gpt 生產力"}
        result = check_similarity(topic, [])
        assert not result.is_too_similar
        assert result.max_similarity == 0.0

    def test_identical_topic_flagged(self):
        topic = {"cluster_label": "AI 工具 gpt", "merged_summary": "生產力 自動化"}
        post_text = "AI 工具 gpt 生產力 自動化"  # high overlap
        recent = [self._recent_post(post_text, days_ago=2)]
        result = check_similarity(topic, recent, threshold=0.35)
        assert result.is_too_similar
        assert result.max_similarity > 0.35

    def test_old_post_ignored(self):
        topic = {"cluster_label": "AI 工具 gpt", "merged_summary": "生產力 自動化"}
        post_text = "AI 工具 gpt 生產力 自動化"
        recent = [self._recent_post(post_text, days_ago=10)]  # beyond lookback_days=7
        result = check_similarity(topic, recent, lookback_days=7)
        assert not result.is_too_similar

    def test_different_topic_not_flagged(self):
        topic = {"cluster_label": "職涯轉換建議", "merged_summary": "換工作 薪資 職涯"}
        post_text = "Flow Lab 香氛站 人因工程 桌面美學"
        recent = [self._recent_post(post_text)]
        result = check_similarity(topic, recent)
        assert not result.is_too_similar

    def test_returns_reasons_when_similar(self):
        topic = {"cluster_label": "ai gpt 生產力 自動化", "merged_summary": "工具推薦 自動化"}
        post_text = "ai gpt 生產力 自動化 工具推薦"
        recent = [self._recent_post(post_text)]
        result = check_similarity(topic, recent, threshold=0.2)
        if result.is_too_similar:
            assert len(result.reasons) > 0

    def test_returns_dataclass(self):
        result = check_similarity({}, [])
        assert isinstance(result, SimilarityResult)
