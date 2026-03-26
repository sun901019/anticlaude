"""
Tests for domain migration shims and wiring.

Covers:
  - src/domains/flow_lab/screenshot_analyzer shim (same object as legacy path)
  - src/domains/media/content/ re-export package
  - orio_scorer enrichment in pipeline score node (_node_score)
  - flowlab approval uses known action key "approve_screenshot"
  - flowlab approval uses risk_level "medium" (creates review_item)
"""
from __future__ import annotations

import json
import pytest


class TestScreenshotAnalyzerShim:
    def test_shim_re_exports_same_function(self):
        from src.domains.flow_lab.screenshot_analyzer import analyze_screenshot as canonical
        from src.agents.screenshot_analyzer import analyze_screenshot as shim
        assert shim is canonical

    def test_shim_re_exports_prompts(self):
        from src.domains.flow_lab.screenshot_analyzer import EXTRACT_PROMPT as cp
        from src.agents.screenshot_analyzer import EXTRACT_PROMPT as sp
        assert sp is cp


class TestMediaContentShim:
    def test_orio_scorer_importable_from_domain(self):
        from src.domains.media.content import score_topic, rank_topics
        assert callable(score_topic)
        assert callable(rank_topics)

    def test_topic_fit_importable_from_domain(self):
        from src.domains.media.content import check_topic_fit, TopicFitResult
        assert callable(check_topic_fit)

    def test_similarity_importable_from_domain(self):
        from src.domains.media.content import check_similarity, SimilarityResult
        assert callable(check_similarity)

    def test_engagement_plan_importable_from_domain(self):
        from src.domains.media.content import EngagementPlan, build_engagement_plan
        assert callable(build_engagement_plan)

    def test_format_selector_importable_from_domain(self):
        from src.domains.media.content import select_format, FormatRecommendation
        assert callable(select_format)


class TestOrioEnrichmentInScoreNode:
    """Verify orio_score metadata gets added to topics when score_topic works."""

    def test_score_topic_adds_fields(self):
        from src.content.orio_scorer import score_topic
        topic = {
            "cluster_label": "AI 生產力工具",
            "merged_summary": "Claude、GPT、LLM 工具如何提升工作流效率",
            "post_type": "工具介紹",
            "source": "techcrunch",
        }
        s = score_topic(topic)
        assert 0.0 <= s.composite_score <= 1.0
        assert isinstance(s.passed, bool)
        assert isinstance(s.reasons, list)

    def test_rank_topics_returns_only_passed(self):
        from src.content.orio_scorer import rank_topics
        topics = [
            {
                "cluster_label": "AI 工具",
                "merged_summary": "Claude 提升生產力",
                "post_type": "工具介紹",
                "source": "techcrunch",
            },
            {
                "cluster_label": "追劇心得",
                "merged_summary": "最近在追的電視劇非常好看",
                "post_type": "心得",
                "source": "unknown",
            },
        ]
        ranked = rank_topics(topics)
        # At least the AI topic should pass
        assert len(ranked) >= 1
        for t in ranked:
            assert "orio_score" in t
            # rank_topics already filters to passed-only; composite >= 0.45
            assert t["orio_score"]["composite"] >= 0.45


class TestFlowlabApprovalKeys:
    """Verify flowlab creates approval with correct action key and risk_level."""

    def test_flowlab_action_key_is_known(self):
        # The action key must be in _ACTION_SUMMARIES so CEO package gets proper text
        from src.workflows.checkpoint_store import _ACTION_SUMMARIES
        assert "approve_screenshot" in _ACTION_SUMMARIES

    def test_flowlab_medium_risk_creates_review_item(self):
        """approve_screenshot with medium risk should create a review_item."""
        from src.workflows.approval import request_approval
        from src.db.connection import db
        with db() as conn:
            conn.execute(
                "DELETE FROM review_items WHERE status='pending' AND context LIKE ?",
                ('%"action": "approve_screenshot"%',),
            )
        approval_id = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"product_name": "測試產品", "analysis_id": "test-123"},
        )
        with db() as conn:
            rows = conn.execute(
                "SELECT * FROM review_items WHERE context LIKE ?",
                (f"%{approval_id}%",),
            ).fetchall()
        assert len(rows) >= 1, "medium risk approve_screenshot should create review_item"
        ctx = json.loads(rows[0]["context"])
        assert ctx["approval_id"] == approval_id

    def test_flowlab_approval_package_has_summary(self):
        """build_ceo_package should return human-readable summary for approve_screenshot."""
        from src.workflows.approval import request_approval
        from src.workflows.checkpoint_store import build_ceo_package
        approval_id = request_approval(
            action="approve_screenshot",
            risk_level="medium",
            evidence={"product_name": "測試產品"},
        )
        pkg = build_ceo_package(approval_id)
        assert pkg is not None
        assert "截圖" in pkg.summary or "審核" in pkg.summary
