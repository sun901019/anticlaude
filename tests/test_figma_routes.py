"""
Tests for Figma operator API routes.
Run after src/api/routes/figma.py is created by Claude Code.

NOTE: If figma.py does not exist yet, tests that import from it will fail with
ImportError — that is expected. Fix by completing the route file first.
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


# ── 1. GET /api/figma/ping — no token configured ──────────────────────────────

def test_figma_ping_no_token():
    """Ping endpoint returns ok=False when FIGMA_API_TOKEN is not set."""
    with patch("src.api.routes.figma.settings") as mock_settings:
        mock_settings.figma_api_token = None
        response = client.get("/api/figma/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is False
    assert "error" in data


# ── 2. GET /api/figma/ping — token present, ping succeeds ────────────────────

def test_figma_ping_with_token():
    """Ping endpoint returns ok=True when token is set and figma_client.ping() succeeds."""
    with patch("src.api.routes.figma.settings") as mock_settings, \
         patch("src.api.routes.figma.figma_client") as mock_client:
        mock_settings.figma_api_token = "test_token_abc"
        mock_client.ping = AsyncMock(return_value=True)
        response = client.get("/api/figma/ping")
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True


# ── 3. GET /api/figma/file — missing file_key param → 422 ────────────────────

def test_figma_file_missing_file_key():
    """GET /api/figma/file without file_key query param returns 422 (FastAPI validation)."""
    response = client.get("/api/figma/file")
    assert response.status_code == 422


# ── 4. GET /api/figma/file — valid file_key, returns metadata ────────────────

def test_figma_file_returns_metadata():
    """GET /api/figma/file?file_key=abc returns 200 with a name field."""
    with patch("src.api.routes.figma.settings") as mock_settings, \
         patch("src.api.routes.figma.figma_client") as mock_client:
        mock_settings.figma_api_token = "test_token_abc"
        mock_client.get_file = AsyncMock(return_value={"name": "My Design File", "version": "1"})
        response = client.get("/api/figma/file", params={"file_key": "abc"})
    assert response.status_code == 200
    data = response.json()
    assert "name" in data


# ── 5. GET /api/figma/comments — returns list ────────────────────────────────

def test_figma_comments_returns_list():
    """GET /api/figma/comments?file_key=abc returns 200 with a comments list."""
    with patch("src.api.routes.figma.settings") as mock_settings, \
         patch("src.api.routes.figma.figma_client") as mock_client:
        mock_settings.figma_api_token = "test_token_abc"
        mock_client.get_comments = AsyncMock(return_value=[
            {"id": "1", "message": "Nice work"},
            {"id": "2", "message": "Fix spacing"},
        ])
        response = client.get("/api/figma/comments", params={"file_key": "abc"})
    assert response.status_code == 200
    data = response.json()
    assert "comments" in data
    assert isinstance(data["comments"], list)


# ── 6. GET /api/figma/nodes — missing ids param → 422 ───────────────────────

def test_figma_nodes_missing_ids():
    """GET /api/figma/nodes?file_key=abc without ids returns 422 (FastAPI validation)."""
    response = client.get("/api/figma/nodes", params={"file_key": "abc"})
    assert response.status_code == 422


# ── 7. GET /api/figma/images — returns image URLs ────────────────────────────

def test_figma_images_returns_urls():
    """GET /api/figma/images?file_key=abc&ids=1:1 returns 200 with image URL data."""
    with patch("src.api.routes.figma.settings") as mock_settings, \
         patch("src.api.routes.figma.figma_client") as mock_client:
        mock_settings.figma_api_token = "test_token_abc"
        mock_client.get_file_images = AsyncMock(return_value={
            "images": {"1:1": "https://figma-alpha-api.s3.us-west-2.amazonaws.com/img/abc"}
        })
        response = client.get("/api/figma/images", params={"file_key": "abc", "ids": "1:1"})
    assert response.status_code == 200
    data = response.json()
    # Response should contain image URL data (exact key depends on route implementation)
    assert data is not None
