from __future__ import annotations

import pytest

from src.social import x_search


class _DummyResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class _DummyClient:
    def __init__(self, recorder: dict):
        self.recorder = recorder

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, headers=None, params=None):
        self.recorder["url"] = url
        self.recorder["headers"] = headers
        self.recorder["params"] = params
        return _DummyResponse({"data": [{"id": "1"}]})


def test_bearer_headers():
    headers = x_search._bearer_headers("abc")
    assert headers == {"Authorization": "Bearer abc"}


@pytest.mark.asyncio
async def test_search_recent_clamps_and_returns_data(monkeypatch):
    recorder: dict = {}
    monkeypatch.setattr(x_search.httpx, "AsyncClient", lambda timeout: _DummyClient(recorder))

    data = await x_search.search_recent("ai tooling", "token", max_results=999)
    assert data == [{"id": "1"}]
    assert recorder["params"]["max_results"] == "100"
    assert recorder["params"]["query"] == "ai tooling"
    assert recorder["headers"]["Authorization"] == "Bearer token"


@pytest.mark.asyncio
async def test_get_user_timeline_clamps_minimum(monkeypatch):
    recorder: dict = {}
    monkeypatch.setattr(x_search.httpx, "AsyncClient", lambda timeout: _DummyClient(recorder))

    data = await x_search.get_user_timeline("42", "token", max_results=1)
    assert data == [{"id": "1"}]
    assert recorder["params"]["max_results"] == "5"
    assert recorder["url"].endswith("/users/42/tweets")


@pytest.mark.asyncio
async def test_ping_returns_false_on_exception(monkeypatch):
    async def _boom(*args, **kwargs):
        raise RuntimeError("no network")

    monkeypatch.setattr(x_search, "search_recent", _boom)
    assert await x_search.ping("token") is False
