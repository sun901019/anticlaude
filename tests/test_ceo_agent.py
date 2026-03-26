# encoding: utf-8
import pytest
from unittest.mock import patch
from src.agents.ceo import _fallback, get_routing_map, get_agent_description


def test_fallback_format():
    result = _fallback("test error")
    assert result["agent"] == "none"
    assert result["task_type"] is None
    assert result["response"] == "test error"
    assert result["actions"] == []


def test_routing_map_is_dict():
    rmap = get_routing_map()
    assert isinstance(rmap, dict)
    assert rmap.get("content_research") == "ori"
    assert rmap.get("draft_generation") == "craft"
    assert rmap.get("seo_analysis") == "sage"
    assert rmap.get("ui_implementation") == "lumi"


def test_agent_description_known():
    for agent_id in ("ori", "lala", "craft", "sage", "lumi", "pixel"):
        desc = get_agent_description(agent_id)
        assert len(desc) > 2


def test_agent_description_unknown():
    desc = get_agent_description("unknown_xyz")
    assert desc == "unknown_xyz"


@pytest.mark.asyncio
async def test_process_message_no_api_key():
    from src.agents.ceo import process_message
    with patch("src.agents.ceo.settings") as mock_settings:
        mock_settings.anthropic_api_key = None
        result = await process_message("你好")
        assert result["agent"] == "none"
        assert result["response"] != ""
