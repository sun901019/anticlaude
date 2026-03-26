"""
GEO/SEO enforcement gate tests.

Verifies that:
1. draft_generation task type includes geo_optimization_engine in required_skills
2. copywriting task type includes geo_optimization_engine in required_skills
3. All content-producing task types have geo_optimization_engine OR content_creation
4. _handle_draft_generation records artifact metadata with "geo_applied" key
"""
import inspect

import pytest

from src.ai.skill_routing import TASK_SKILL_ROUTES


# Content-producing task types that must enforce GEO or content_creation
CONTENT_TASK_TYPES = {"draft_generation", "copywriting"}


class TestGeoEnforcement:

    def test_geo_skill_loaded_for_draft_generation(self):
        """draft_generation must declare geo_optimization_engine as a required skill."""
        assert "draft_generation" in TASK_SKILL_ROUTES, \
            "TASK_SKILL_ROUTES is missing 'draft_generation'"
        route = TASK_SKILL_ROUTES["draft_generation"]
        assert "geo_optimization_engine" in route.required_skills, (
            f"geo_optimization_engine not found in draft_generation required_skills: "
            f"{route.required_skills}"
        )

    def test_geo_skill_loaded_for_copywriting(self):
        """copywriting must declare geo_optimization_engine as a required skill."""
        assert "copywriting" in TASK_SKILL_ROUTES, \
            "TASK_SKILL_ROUTES is missing 'copywriting'"
        route = TASK_SKILL_ROUTES["copywriting"]
        assert "geo_optimization_engine" in route.required_skills, (
            f"geo_optimization_engine not found in copywriting required_skills: "
            f"{route.required_skills}"
        )

    def test_skill_routing_has_geo_for_all_draft_tasks(self):
        """All content-producing task types must have geo_optimization_engine or content_creation."""
        missing = []
        for task_type in CONTENT_TASK_TYPES:
            assert task_type in TASK_SKILL_ROUTES, \
                f"TASK_SKILL_ROUTES is missing '{task_type}'"
            route = TASK_SKILL_ROUTES[task_type]
            all_skills = set(route.required_skills) | set(route.optional_skills)
            has_geo = "geo_optimization_engine" in all_skills
            has_content_creation = "content_creation" in all_skills
            if not (has_geo or has_content_creation):
                missing.append(task_type)
        assert not missing, (
            f"These content task types lack both geo_optimization_engine and "
            f"content_creation: {missing}"
        )

    def test_geo_artifact_flag_present(self):
        """_handle_draft_generation must include 'geo_applied' in artifact metadata."""
        from src.agents.dynamic_orchestrator import _handle_draft_generation

        # Inspect source to verify "geo_applied" key is present in the metadata dict
        source = inspect.getsource(_handle_draft_generation)
        assert "geo_applied" in source, (
            "_handle_draft_generation does not reference 'geo_applied' in its source; "
            "artifact metadata must include this flag."
        )
