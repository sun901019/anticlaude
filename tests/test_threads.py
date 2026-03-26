"""
測試 Threads API 整合
"""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_get_me_returns_none_without_token(monkeypatch):
    monkeypatch.setattr("src.config.settings.threads_access_token", None)
    from src.tracker.threads_client import get_me
    result = await get_me()
    assert result is None


@pytest.mark.asyncio
async def test_get_me_detects_expired_token(monkeypatch):
    monkeypatch.setattr("src.config.settings.threads_access_token", "expired-token")
    expired_response = {"error": {"code": 190, "message": "Token expired"}}
    with patch("src.tracker.threads_client.get", AsyncMock(return_value=expired_response)):
        from src.tracker.threads_client import get_me
        result = await get_me()
    assert result is None


@pytest.mark.asyncio
async def test_get_recent_posts_returns_list(monkeypatch):
    monkeypatch.setattr("src.config.settings.threads_access_token", "valid-token")
    monkeypatch.setattr("src.config.settings.threads_user_id", "12345")
    mock_response = {
        "data": [
            {"id": "post1", "text": "Hello world", "timestamp": "2026-03-09T12:00:00Z", "media_type": "TEXT"},
            {"id": "post2", "text": "AI tools", "timestamp": "2026-03-08T12:00:00Z", "media_type": "TEXT"},
        ]
    }
    with patch("src.tracker.threads_client.get", AsyncMock(return_value=mock_response)):
        from src.tracker.threads_client import get_recent_posts
        result = await get_recent_posts()
    assert len(result) == 2
    assert result[0]["id"] == "post1"


@pytest.mark.asyncio
async def test_engagement_rate_calculation():
    from src.tracker.metrics_collector import _calc_engagement
    rate = _calc_engagement(views=1000, likes=30, replies=5, reposts=2, quotes=1)
    assert rate == 3.8


@pytest.mark.asyncio
async def test_engagement_rate_zero_views():
    from src.tracker.metrics_collector import _calc_engagement
    rate = _calc_engagement(views=0, likes=5, replies=0, reposts=0, quotes=0)
    assert rate == 0.0
