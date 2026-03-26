# encoding: utf-8
"""
Tests for _handle_draft_generation GEO validation + A/B result integration.
4 tests verifying that GEO gate and A/B comparison are wired in correctly.

Patching strategy:
  - write_drafts is imported inside the handler via `from src.ai.claude_writer import write_drafts`
    so we patch it at its source: "src.ai.claude_writer.write_drafts"
  - record_artifact is imported via `from src.workflows.runner import record_artifact`
    so we patch: "src.workflows.runner.record_artifact"
  - validate_drafts_batch is imported via `from src.content.geo_validator import validate_drafts_batch`
    so we patch: "src.content.geo_validator.validate_drafts_batch"
"""
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from src.agents.dynamic_orchestrator import _handle_draft_generation


class TestDraftGenerationGeoAb:

    @pytest.mark.asyncio
    async def test_draft_generation_includes_geo_validation(self):
        """geo_validation key must be present and be a dict with 'all_passed'."""
        fake_draft = {"content": "我發現每週省 4 小時整理時間，賣出 30 件後才懂這件事。說真的。"}
        fake_path = Path("fake.md")

        with patch(
            "src.ai.claude_writer.write_drafts",
            new=AsyncMock(return_value=(fake_path, [fake_draft])),
        ), patch(
            "src.workflows.runner.record_artifact",
            new=MagicMock(),
        ):
            result = await _handle_draft_generation({"top3": [{"cluster_label": "test"}]})

        assert result["success"] is True
        geo = result["data"]["geo_validation"]
        assert isinstance(geo, dict)
        assert "all_passed" in geo

    @pytest.mark.asyncio
    async def test_draft_generation_includes_ab_result_when_two_drafts(self):
        """When two drafts are returned, ab_result must contain winner_idx."""
        draft_a = {"content": "我覺得這個方法很實用，賣出 20 件後才真正懂定價。"}
        draft_b = {"content": "老實說賣出 15 件之後發現選品比行銷更重要，這是我的心得。"}
        fake_path = Path("fake.md")

        with patch(
            "src.ai.claude_writer.write_drafts",
            new=AsyncMock(return_value=(fake_path, [draft_a, draft_b])),
        ), patch(
            "src.workflows.runner.record_artifact",
            new=MagicMock(),
        ):
            result = await _handle_draft_generation({"top3": [{"cluster_label": "test"}]})

        assert result["success"] is True
        ab = result["data"]["ab_result"]
        assert ab  # not empty
        assert "winner_idx" in ab

    @pytest.mark.asyncio
    async def test_draft_generation_ab_result_empty_when_one_draft(self):
        """When only one draft is returned, ab_result must be an empty dict."""
        fake_draft = {"content": "我發現每週 3 小時就能整理好 50 件商品，很值得試試。"}
        fake_path = Path("fake.md")

        with patch(
            "src.ai.claude_writer.write_drafts",
            new=AsyncMock(return_value=(fake_path, [fake_draft])),
        ), patch(
            "src.workflows.runner.record_artifact",
            new=MagicMock(),
        ):
            result = await _handle_draft_generation({"top3": [{"cluster_label": "test"}]})

        assert result["success"] is True
        assert result["data"]["ab_result"] == {}

    @pytest.mark.asyncio
    async def test_geo_failure_does_not_crash_draft_generation(self):
        """A GEO validator exception must not propagate — result must still succeed."""
        fake_draft = {"content": "老實說，賣出 10 件後我才明白這件事。"}
        fake_path = Path("fake.md")

        with patch(
            "src.ai.claude_writer.write_drafts",
            new=AsyncMock(return_value=(fake_path, [fake_draft])),
        ), patch(
            "src.workflows.runner.record_artifact",
            new=MagicMock(),
        ), patch(
            "src.content.geo_validator.validate_drafts_batch",
            side_effect=RuntimeError("GEO validator exploded"),
        ):
            result = await _handle_draft_generation({"top3": [{"cluster_label": "test"}]})

        assert result["success"] is True
