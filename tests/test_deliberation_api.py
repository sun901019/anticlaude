# encoding: utf-8
"""
Tests for POST /api/chat/deliberate endpoint.
All log and comment text is in English only.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Test 1: empty question -> 400
# ---------------------------------------------------------------------------

def test_deliberate_empty_question():
    """POST with an empty question string should return 400."""
    res = client.post("/api/chat/deliberate", json={"question": ""})
    assert res.status_code == 400


# ---------------------------------------------------------------------------
# Test 2: missing question field -> 422
# ---------------------------------------------------------------------------

def test_deliberate_missing_question():
    """POST with no question field at all should return 422 (validation error)."""
    res = client.post("/api/chat/deliberate", json={})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Test 3: successful deliberation returns expected keys -> 200
# ---------------------------------------------------------------------------

def test_deliberate_returns_keys():
    """Mock deliberate() to return a full result; verify 200 and all required keys."""
    mock_result = {
        "consensus": "Agree on strategy X",
        "recommendation": "Proceed with option A",
        "confidence": 0.85,
        "next_steps": ["Step 1", "Step 2"],
        "agent_inputs": {
            "ori": {"status": "ok"},
            "lala": {"status": "ok"},
            "sage": {"status": "ok"},
        },
    }
    with patch(
        "src.agents.ceo.deliberate",
        new_callable=AsyncMock,
    ) as mock_deliberate:
        mock_deliberate.return_value = mock_result
        res = client.post(
            "/api/chat/deliberate",
            json={"question": "What strategy should we use?"},
        )

    assert res.status_code == 200
    data = res.json()
    for key in ("consensus", "recommendation", "confidence", "next_steps", "agent_inputs"):
        assert key in data, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# Test 4: deliberate() raises Exception -> 500
# ---------------------------------------------------------------------------

def test_deliberate_error_propagates():
    """When deliberate() raises an exception the endpoint should return 500."""
    with patch(
        "src.agents.ceo.deliberate",
        new_callable=AsyncMock,
    ) as mock_deliberate:
        mock_deliberate.side_effect = Exception("fail")
        res = client.post(
            "/api/chat/deliberate",
            json={"question": "What should we do?"},
        )

    assert res.status_code == 500


# ---------------------------------------------------------------------------
# Test 5: whitespace-only question -> 400
# ---------------------------------------------------------------------------

def test_deliberate_question_whitespace():
    """POST with a whitespace-only question string should return 400."""
    res = client.post("/api/chat/deliberate", json={"question": "   "})
    assert res.status_code == 400
