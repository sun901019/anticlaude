"""Tests for serper_client.search() — 3 test cases covering key guard, parse, and error handling."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


# ── 1. Returns empty list when API key is missing ────────────────────────────

@pytest.mark.asyncio
async def test_search_returns_empty_when_no_key(monkeypatch):
    """search() should return [] immediately when serper_api_key is None or empty."""
    monkeypatch.setattr("src.config.settings.serper_api_key", None)
    from src.scrapers.serper_client import search
    result = await search("test query")
    assert result == [], f"Expected [], got {result}"


# ── 2. Parses organic results correctly ──────────────────────────────────────

@pytest.mark.asyncio
async def test_search_parses_organic_results(monkeypatch):
    """search() should return a list of dicts with title/snippet/link from 'organic' key."""
    monkeypatch.setattr("src.config.settings.serper_api_key", "fake-api-key")

    fake_json = {"organic": [{"title": "T", "snippet": "S", "link": "L"}]}

    mock_response = MagicMock()
    mock_response.json.return_value = fake_json
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        from src.scrapers import serper_client
        # Force re-evaluation with the patched client
        result = await serper_client.search("test query")

    expected = [{"title": "T", "snippet": "S", "link": "L"}]
    assert result == expected, f"Expected {expected}, got {result}"


# ── 3. Returns empty list on HTTP / network exception ────────────────────────

@pytest.mark.asyncio
async def test_search_returns_empty_on_error(monkeypatch):
    """search() should return [] if any exception is raised during the HTTP call."""
    monkeypatch.setattr("src.config.settings.serper_api_key", "fake-api-key")

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=Exception("network failure"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("httpx.AsyncClient", return_value=mock_client):
        from src.scrapers import serper_client
        result = await serper_client.search("test query")

    assert result == [], f"Expected [] on error, got {result}"
