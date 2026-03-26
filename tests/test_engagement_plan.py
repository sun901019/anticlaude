"""
Tests for src/content/engagement_plan.py
"""
from src.content.engagement_plan import build_engagement_plan, EngagementPlan


class TestEngagementPlan:
    def test_returns_dataclass(self):
        result = build_engagement_plan({"post_type": "趨勢解讀"})
        assert isinstance(result, EngagementPlan)

    def test_morning_trend_slots(self):
        result = build_engagement_plan({"post_type": "趨勢解讀"})
        # 趨勢解讀 → morning + evening
        assert any("07:30" in s for s in result.best_slots)
        assert any("21:00" in s for s in result.best_slots)

    def test_event_only_morning(self):
        result = build_engagement_plan({"post_type": "事件評論"})
        assert len(result.best_slots) == 1
        assert "07:30" in result.best_slots[0]

    def test_first_reply_always_5min(self):
        for pt in ("趨勢解讀", "工具介紹", "個人經驗", "職涯建議"):
            result = build_engagement_plan({"post_type": pt})
            assert result.first_reply_within == 5

    def test_thread_format_actions(self):
        result = build_engagement_plan({"post_type": "趨勢解讀"}, format_type="thread")
        # thread format should include multi-thread instruction
        assert any("分串" in a for a in result.first_hour_actions)

    def test_non_thread_no_multi_thread_action(self):
        result = build_engagement_plan({"post_type": "工具介紹"}, format_type="short")
        assert not any("分串" in a for a in result.first_hour_actions)

    def test_first_reply_tip_differs_by_format(self):
        short_tip = build_engagement_plan({}, format_type="short").first_reply_tip
        long_tip = build_engagement_plan({}, format_type="long").first_reply_tip
        thread_tip = build_engagement_plan({}, format_type="thread").first_reply_tip
        assert short_tip != long_tip
        assert short_tip != thread_tip

    def test_rationale_contains_post_type(self):
        result = build_engagement_plan({"post_type": "職涯建議"})
        assert "職涯建議" in result.rationale

    def test_four_actions_for_non_thread(self):
        result = build_engagement_plan({"post_type": "工具介紹"}, format_type="short")
        assert len(result.first_hour_actions) == 4

    def test_five_actions_for_thread(self):
        result = build_engagement_plan({"post_type": "趨勢解讀"}, format_type="thread")
        assert len(result.first_hour_actions) == 5

    def test_unknown_post_type_defaults(self):
        # Should not raise, default to morning/evening
        result = build_engagement_plan({"post_type": "未知類型"})
        assert len(result.best_slots) >= 1
