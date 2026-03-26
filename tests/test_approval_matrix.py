# tests/test_approval_matrix.py
# Tests for src/workflows/approval_matrix.py
# All entries in English only.

import pytest
from src.workflows.approval_matrix import (
    get_risk_level,
    requires_human,
    get_rationale,
    classify,
    list_high_risk_actions,
)


# ── Test 1: publish_post → risk_level="high", requires_human=True ───────────

def test_publish_post_risk_level():
    assert get_risk_level("publish_post") == "high"


def test_publish_post_requires_human():
    assert requires_human("publish_post") is True


# ── Test 2: system_modification → risk_level="critical" ─────────────────────

def test_system_modification_risk_level():
    assert get_risk_level("system_modification") == "critical"


# ── Test 3: draft_generation → risk_level="low", requires_human=False ────────

def test_draft_generation_risk_level():
    assert get_risk_level("draft_generation") == "low"


def test_draft_generation_requires_human():
    assert requires_human("draft_generation") is False


# ── Test 4: Unknown action → get_risk_level returns "medium", requires_human False ──

def test_unknown_action_risk_level():
    assert get_risk_level("totally_nonexistent_action_xyz") == "medium"


def test_unknown_action_requires_human():
    assert requires_human("totally_nonexistent_action_xyz") is False


# ── Test 5: get_rationale("publish_post") returns non-empty string ───────────

def test_get_rationale_publish_post_nonempty():
    rationale = get_rationale("publish_post")
    assert isinstance(rationale, str)
    assert len(rationale) > 0


# ── Test 6: get_rationale("totally_unknown") returns non-empty string ────────

def test_get_rationale_unknown_action_nonempty():
    rationale = get_rationale("totally_unknown_action_xyz")
    assert isinstance(rationale, str)
    assert len(rationale) > 0


# ── Test 7: classify("publish_post") returns dict with 4 required keys ───────

def test_classify_publish_post_has_required_keys():
    result = classify("publish_post")
    assert isinstance(result, dict)
    for key in ("action_type", "risk_level", "requires_human", "rationale"):
        assert key in result, f"Missing key: {key}"


# ── Test 8: classify("unknown_action") returns dict with all 4 keys (no KeyError) ──

def test_classify_unknown_action_has_all_keys():
    result = classify("unknown_action_xyz")
    assert isinstance(result, dict)
    for key in ("action_type", "risk_level", "requires_human", "rationale"):
        assert key in result, f"Missing key: {key}"


# ── Test 9: list_high_risk_actions() returns non-empty list ──────────────────

def test_list_high_risk_actions_nonempty():
    result = list_high_risk_actions()
    assert isinstance(result, list)
    assert len(result) > 0


# ── Test 10: Every action in list_high_risk_actions() has risk_level in {"high","critical"} ──

def test_list_high_risk_actions_all_high_or_critical():
    for action in list_high_risk_actions():
        level = get_risk_level(action)
        assert level in {"high", "critical"}, (
            f"Action '{action}' has risk_level='{level}', expected high or critical"
        )


# ── Test 11: Every action in list_high_risk_actions() has requires_human == True ──

def test_list_high_risk_actions_all_require_human():
    for action in list_high_risk_actions():
        assert requires_human(action) is True, (
            f"Action '{action}' does not require human approval"
        )


# ── Test 12: "chrome_automation" is in list_high_risk_actions() ──────────────

def test_chrome_automation_in_high_risk():
    assert "chrome_automation" in list_high_risk_actions()


# ── Test 13: "content_research" is NOT in list_high_risk_actions() ───────────

def test_content_research_not_in_high_risk():
    assert "content_research" not in list_high_risk_actions()


# ── Test 14: schema_migration → risk_level="critical" ────────────────────────

def test_schema_migration_risk_level():
    assert get_risk_level("schema_migration") == "critical"
