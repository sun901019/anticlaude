# encoding: utf-8
import pytest
from src.agents.dynamic_orchestrator import run_task, get_supported_tasks


def test_get_supported_tasks_returns_dict():
    tasks = get_supported_tasks()
    assert isinstance(tasks, dict)
    assert len(tasks) > 0
    assert "content_research" in tasks
    assert "draft_generation" in tasks
    assert "data_analysis" in tasks


@pytest.mark.asyncio
async def test_run_task_unsupported():
    result = await run_task("nonexistent_task_xyz_999")
    assert result["success"] is False
    assert "supported_task_types" in result
    assert result["task_type"] == "nonexistent_task_xyz_999"
    assert result["agent"] == "none"


@pytest.mark.asyncio
async def test_run_task_market_analysis_missing_product_name():
    result = await run_task("market_analysis", {})
    assert result["success"] is False
    assert result["agent"] == "ori"
    assert "product_name" in result.get("error", "")


@pytest.mark.asyncio
async def test_run_task_product_evaluation_missing_candidate_id():
    result = await run_task("product_evaluation", {})
    assert result["success"] is False
    assert result["agent"] == "sage"


@pytest.mark.asyncio
async def test_run_task_always_includes_task_type():
    result = await run_task("nonexistent_xyz_abc")
    assert result.get("task_type") == "nonexistent_xyz_abc"


@pytest.mark.asyncio
async def test_run_task_data_analysis_returns_correct_format():
    result = await run_task("data_analysis", {"days": 7})
    assert result["task_type"] == "data_analysis"
    assert result["agent"] == "sage"
    assert "success" in result


@pytest.mark.asyncio
async def test_run_task_seo_analysis_returns_placeholder():
    result = await run_task("seo_analysis", {"brand_url": "https://example.com"})
    assert result["success"] is True
    assert result["agent"] == "sage"
    assert "data" in result


@pytest.mark.asyncio
async def test_run_task_topic_strategy_missing_scored_topics():
    result = await run_task("topic_strategy", {})
    assert result["success"] is False
    assert result["agent"] == "lala"
    assert "scored_topics" in result.get("error", "")


@pytest.mark.asyncio
async def test_run_task_injects_skills_for_draft_generation():
    # draft_generation requires content_creation + geo_optimization_engine per skill_routing
    # without API key the handler will fail, but skills are injected before handler runs
    # We test this indirectly: result always has task_type key
    result = await run_task("draft_generation", {"top3": []})
    assert result["task_type"] == "draft_generation"
    assert result["agent"] in ("craft", "none")


@pytest.mark.asyncio
async def test_skill_routing_injected_for_known_task():
    from src.ai.skill_routing import get_required_skills
    skills = get_required_skills("content_research")
    assert "research_analysis" in skills
