from __future__ import annotations

import pytest

from src.utils import notify


class _DummyResponse:
    def __init__(self, status_code=200, text="ok"):
        self.status_code = status_code
        self.text = text


class _DummyClient:
    def __init__(self, recorder: dict, response: _DummyResponse | None = None):
        self.recorder = recorder
        self.response = response or _DummyResponse()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, headers=None, json=None):
        self.recorder["url"] = url
        self.recorder["headers"] = headers
        self.recorder["json"] = json
        return self.response


@pytest.mark.asyncio
async def test_send_line_notify_noop_without_env(monkeypatch):
    called = {"value": False}

    class _ShouldNotRun:
        async def __aenter__(self):
            called["value"] = True
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(notify.settings, "line_channel_access_token", None)
    monkeypatch.setattr(notify.settings, "line_user_id", None)
    monkeypatch.setattr(notify.httpx, "AsyncClient", lambda timeout: _ShouldNotRun())

    await notify.send_line_notify("hello")
    assert called["value"] is False


@pytest.mark.asyncio
async def test_send_line_notify_posts_expected_payload(monkeypatch):
    recorder: dict = {}
    monkeypatch.setattr(notify.settings, "line_channel_access_token", "line-token")
    monkeypatch.setattr(notify.settings, "line_user_id", "user-123")
    monkeypatch.setattr(notify.httpx, "AsyncClient", lambda timeout: _DummyClient(recorder))

    await notify.send_line_notify("hello line")

    assert recorder["url"] == notify.LINE_PUSH_URL
    assert recorder["headers"]["Authorization"] == "Bearer line-token"
    assert recorder["json"]["to"] == "user-123"
    assert recorder["json"]["messages"][0]["text"] == "hello line"
