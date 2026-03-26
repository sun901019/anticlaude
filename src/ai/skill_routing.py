"""
Skill Routing — machine-readable task_type → skill mapping.

Replaces the ad-hoc GEO_AUTO_INJECT_TASKS set with a formal per-task routing
table that specifies which composite skills to load, the primary execution
pattern, risk level, and whether a human-review gate is required.

Usage:
    from src.ai.skill_routing import get_required_skills, TASK_SKILL_ROUTES
    skills = get_required_skills("draft_generation")
    # ["content_creation", "geo_optimization_engine"]
"""
from typing import Literal

Pattern = Literal["Generator", "Reviewer", "Tool Wrapper", "Pipeline", "Inversion"]
RiskLevel = Literal["low", "medium", "high"]


class SkillRoute:
    __slots__ = (
        "primary_pattern",
        "required_skills",
        "optional_skills",
        "requires_review",
        "risk_level",
    )

    def __init__(
        self,
        primary_pattern: Pattern,
        required_skills: list[str],
        optional_skills: list[str],
        requires_review: bool,
        risk_level: RiskLevel,
    ):
        self.primary_pattern = primary_pattern
        self.required_skills = required_skills
        self.optional_skills = optional_skills
        self.requires_review = requires_review
        self.risk_level = risk_level

    def to_dict(self) -> dict:
        return {
            "primary_pattern":  self.primary_pattern,
            "required_skills":  self.required_skills,
            "optional_skills":  self.optional_skills,
            "requires_review":  self.requires_review,
            "risk_level":       self.risk_level,
        }


# ── Routing Table ──────────────────────────────────────────────────────────────
# Each key matches a task_type recognized by dynamic_orchestrator.py.
# Skill names must match filenames in _hub/shared/skills/composite/*.md

TASK_SKILL_ROUTES: dict[str, SkillRoute] = {
    "content_research": SkillRoute(
        primary_pattern="Tool Wrapper",
        required_skills=["research_analysis"],
        optional_skills=["geo_optimization_engine"],
        requires_review=False,
        risk_level="low",
    ),
    "market_analysis": SkillRoute(
        primary_pattern="Tool Wrapper",
        required_skills=["research_analysis", "marketing_strategy"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "topic_strategy": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["marketing_strategy", "seo_optimization"],
        optional_skills=["content_creation"],
        requires_review=False,
        risk_level="low",
    ),
    "draft_generation": SkillRoute(
        primary_pattern="Generator",
        required_skills=["content_creation", "geo_optimization_engine"],
        optional_skills=["seo_optimization"],
        requires_review=True,
        risk_level="medium",
    ),
    "copywriting": SkillRoute(
        primary_pattern="Generator",
        required_skills=["content_creation", "geo_optimization_engine"],
        optional_skills=["seo_optimization"],
        requires_review=True,
        risk_level="medium",
    ),
    "data_analysis": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["seo_optimization"],
        optional_skills=["research_analysis"],
        requires_review=False,
        risk_level="low",
    ),
    "seo_analysis": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["seo_optimization", "geo_optimization_engine"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "product_evaluation": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["research_analysis", "marketing_strategy"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "competitor_analysis": SkillRoute(
        primary_pattern="Tool Wrapper",
        required_skills=["research_analysis", "marketing_strategy"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "audience_analysis": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["marketing_strategy"],
        optional_skills=["research_analysis"],
        requires_review=False,
        risk_level="low",
    ),
    "content_planning": SkillRoute(
        primary_pattern="Generator",
        required_skills=["marketing_strategy", "content_creation"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "system_debugging": SkillRoute(
        primary_pattern="Tool Wrapper",
        required_skills=["project_planning"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "backend_development": SkillRoute(
        primary_pattern="Generator",
        required_skills=["project_planning"],
        optional_skills=[],
        requires_review=True,
        risk_level="medium",
    ),
    "ui_implementation": SkillRoute(
        primary_pattern="Generator",
        required_skills=["project_planning", "ux_review"],
        optional_skills=[],
        requires_review=True,
        risk_level="medium",
    ),
    "design_evaluation": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["ux_review"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
    "ux_review": SkillRoute(
        primary_pattern="Reviewer",
        required_skills=["ux_review"],
        optional_skills=[],
        requires_review=False,
        risk_level="low",
    ),
}


# ── Public Helpers ─────────────────────────────────────────────────────────────

def get_skill_route(task_type: str) -> SkillRoute | None:
    """Return the SkillRoute for a task_type, or None if unknown."""
    return TASK_SKILL_ROUTES.get(task_type)


def get_required_skills(task_type: str) -> list[str]:
    """Return the required skill names for a task_type (empty list if unknown)."""
    route = TASK_SKILL_ROUTES.get(task_type)
    return list(route.required_skills) if route else []


def requires_review(task_type: str) -> bool:
    """Return True if this task type requires a human-review approval gate."""
    route = TASK_SKILL_ROUTES.get(task_type)
    return route.requires_review if route else False


def get_task_skill_summary() -> list[dict]:
    """Serializable list of all routes — for API exposure and Office UI."""
    return [
        {"task_type": task_type, **route.to_dict()}
        for task_type, route in TASK_SKILL_ROUTES.items()
    ]
