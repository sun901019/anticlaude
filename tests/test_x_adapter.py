from __future__ import annotations

import pytest

from src.adapters.x_adapter import XPublishAdapter


@pytest.fixture
def adapter(monkeypatch):
    from src import config

    monkeypatch.setattr(config.settings, "x_api_key", "key")
    monkeypatch.setattr(config.settings, "x_api_key_secret", "secret")
    monkeypatch.setattr(config.settings, "x_access_token", "token")
    monkeypatch.setattr(config.settings, "x_access_token_secret", "token_secret")
    return XPublishAdapter()


@pytest.mark.asyncio
async def test_post_dry_run_validates(adapter):
    result = await adapter.execute({"action": "post", "text": "hello world", "dry_run": True})
    assert result.ok is True
    assert result.data["dry_run"] is True
    assert result.data["char_count"] == 11


@pytest.mark.asyncio
async def test_post_requires_text(adapter):
    result = await adapter.execute({"action": "post", "text": "", "dry_run": True})
    assert result.ok is False
    assert "text" in result.error


@pytest.mark.asyncio
async def test_post_rejects_over_limit(adapter):
    result = await adapter.execute({"action": "post", "text": "x" * 281, "dry_run": True})
    assert result.ok is False
    assert "280" in result.error


@pytest.mark.asyncio
async def test_delete_dry_run_validates(adapter):
    result = await adapter.execute({"action": "delete", "tweet_id": "12345", "dry_run": True})
    assert result.ok is True
    assert result.data["tweet_id"] == "12345"


@pytest.mark.asyncio
async def test_delete_requires_tweet_id(adapter):
    result = await adapter.execute({"action": "delete", "dry_run": True})
    assert result.ok is False
    assert "tweet_id" in result.error


@pytest.mark.asyncio
async def test_unknown_action_rejected(adapter):
    result = await adapter.execute({"action": "retweet", "dry_run": True})
    assert result.ok is False
    assert "action" in result.error.lower()


@pytest.mark.asyncio
async def test_safe_execute_blocks_unapproved_live_post(adapter):
    result = await adapter.safe_execute(
        {"action": "post", "text": "ship it", "dry_run": False},
        agent_id="craft",
        pre_approved=False,
    )
    assert result.ok is False
    assert result.error == "approval_required"
    assert "approval_id" in result.data


@pytest.mark.asyncio
async def test_safe_execute_blocks_wrong_agent(adapter):
    result = await adapter.safe_execute(
        {"action": "post", "text": "hello", "dry_run": True},
        agent_id="ori",
    )
    assert result.ok is False
    assert "craft" in result.error


@pytest.mark.asyncio
async def test_missing_credentials_returns_error(monkeypatch):
    from src import config

    monkeypatch.setattr(config.settings, "x_api_key", None)
    monkeypatch.setattr(config.settings, "x_api_key_secret", None)
    monkeypatch.setattr(config.settings, "x_access_token", None)
    monkeypatch.setattr(config.settings, "x_access_token_secret", None)

    adapter = XPublishAdapter()
    result = await adapter.execute({"action": "post", "text": "hello", "dry_run": True})
    assert result.ok is False
    assert "credential" in result.error.lower() or "api" in result.error.lower()
