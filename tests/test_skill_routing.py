"""Tests for src/ai/skill_routing.py — machine-readable task_type → skill mapping."""
import pytest

from src.ai.skill_routing import (
    TASK_SKILL_ROUTES,
    get_skill_route,
    get_required_skills,
    requires_review,
    get_task_skill_summary,
)

KNOWN_TASK_TYPES = list(TASK_SKILL_ROUTES.keys())
VALID_PATTERNS = {"Generator", "Reviewer", "Tool Wrapper", "Pipeline", "Inversion"}
VALID_RISK_LEVELS = {"low", "medium", "high"}


def test_all_task_types_have_routes():
    assert len(TASK_SKILL_ROUTES) >= 7


def test_route_fields_valid():
    for task_type, route in TASK_SKILL_ROUTES.items():
        assert route.primary_pattern in VALID_PATTERNS, f"{task_type}: bad pattern"
        assert route.risk_level in VALID_RISK_LEVELS, f"{task_type}: bad risk_level"
        assert isinstance(route.required_skills, list), f"{task_type}: required_skills not list"
        assert isinstance(route.optional_skills, list), f"{task_type}: optional_skills not list"
        assert isinstance(route.requires_review, bool), f"{task_type}: requires_review not bool"


def test_required_skills_nonempty_for_all():
    for task_type, route in TASK_SKILL_ROUTES.items():
        assert len(route.required_skills) > 0, f"{task_type}: must have at least one required skill"


def test_get_skill_route_known():
    route = get_skill_route("draft_generation")
    assert route is not None
    assert route.primary_pattern == "Generator"
    assert "content_creation" in route.required_skills
    assert "geo_optimization_engine" in route.required_skills


def test_get_skill_route_unknown():
    assert get_skill_route("nonexistent_task") is None


def test_get_required_skills():
    skills = get_required_skills("draft_generation")
    assert "content_creation" in skills
    assert "geo_optimization_engine" in skills


def test_get_required_skills_unknown_returns_empty():
    assert get_required_skills("totally_unknown") == []


def test_requires_review_draft_generation():
    assert requires_review("draft_generation") is True


def test_requires_review_content_research():
    assert requires_review("content_research") is False


def test_requires_review_unknown():
    assert requires_review("nonexistent") is False


def test_summary_returns_all_routes():
    summary = get_task_skill_summary()
    assert isinstance(summary, list)
    assert len(summary) == len(TASK_SKILL_ROUTES)
    task_types = {s["task_type"] for s in summary}
    assert task_types == set(TASK_SKILL_ROUTES.keys())


def test_summary_entries_serializable():
    summary = get_task_skill_summary()
    for entry in summary:
        assert "task_type" in entry
        assert "primary_pattern" in entry
        assert "required_skills" in entry
        assert "risk_level" in entry
        assert "requires_review" in entry


def test_high_risk_tasks_require_review():
    for task_type, route in TASK_SKILL_ROUTES.items():
        if route.risk_level == "high":
            assert route.requires_review, f"{task_type}: high-risk must require_review"


def test_copywriting_same_skills_as_draft_generation():
    copy_route = get_skill_route("copywriting")
    draft_route = get_skill_route("draft_generation")
    assert copy_route is not None and draft_route is not None
    assert set(copy_route.required_skills) == set(draft_route.required_skills)
