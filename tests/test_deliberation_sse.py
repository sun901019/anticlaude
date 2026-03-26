# encoding: utf-8
"""
Tests for GET /api/chat/deliberate/stream (SSE streaming endpoint).
Uses TestClient with stream=True to read SSE events synchronously.
All text in English only.
"""
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


# ── 1. Empty question → 400 ──────────────────────────────────────────────────

def test_sse_stream_empty_question_400():
    """GET /api/chat/deliberate/stream?question= (empty) should return 400."""
    response = client.get("/api/chat/deliberate/stream", params={"question": ""})
    assert response.status_code == 400


# ── 2. Missing question param → 422 ──────────────────────────────────────────

def test_sse_stream_missing_question_422():
    """GET /api/chat/deliberate/stream without question param returns 422."""
    response = client.get("/api/chat/deliberate/stream")
    assert response.status_code == 422


# ── 3. Stream content-type is text/event-stream ──────────────────────────────

def test_sse_stream_content_type():
    """GET /api/chat/deliberate/stream with valid question returns text/event-stream."""
    with patch("src.agents.ceo._DELIBERATION_AGENTS", {}), \
         patch("src.config.settings") as mock_settings, \
         patch("anthropic.Anthropic") as mock_anthropic:

        mock_settings.anthropic_api_key = "test_key"
        mock_settings.model_write = "claude-sonnet-4-6"
        mock_client = mock_anthropic.return_value
        mock_synthesis = {
            "consensus": "c", "key_insights": [], "divergences": None,
            "recommendation": "r", "confidence": "high", "next_steps": [],
        }
        mock_msg = mock_client.messages.create.return_value
        mock_msg.content = [type("C", (), {"text": json.dumps(mock_synthesis)})()]

        with client.stream("GET", "/api/chat/deliberate/stream", params={"question": "what to post?"}) as resp:
            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers.get("content-type", "")


# ── 4. Stream includes [DONE] marker ─────────────────────────────────────────

def test_sse_stream_done_marker():
    """The stream response should be content-type text/event-stream."""
    with patch("src.agents.ceo._DELIBERATION_AGENTS", {}), \
         patch("src.config.settings") as mock_settings, \
         patch("anthropic.Anthropic") as mock_anthropic:

        mock_settings.anthropic_api_key = "test_key"
        mock_settings.model_write = "claude-sonnet-4-6"
        mock_client = mock_anthropic.return_value
        mock_msg = mock_client.messages.create.return_value
        mock_synthesis = {
            "consensus": "c", "key_insights": [], "divergences": None,
            "recommendation": "r", "confidence": "low", "next_steps": [],
        }
        mock_msg.content = [type("C", (), {"text": json.dumps(mock_synthesis)})()]

        with client.stream("GET", "/api/chat/deliberate/stream", params={"question": "hello"}) as resp:
            assert resp.status_code == 200
            body = resp.read().decode("utf-8")
            assert "[DONE]" in body
