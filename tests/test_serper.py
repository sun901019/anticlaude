"""
測試 Serper 搜尋抓取器
"""
import pytest
from unittest.mock import patch, AsyncMock

MOCK_RESPONSE = {
    "news": [
        {"title": "AI news 1", "link": "https://example.com/1", "snippet": "Summary 1", "date": "2026-03-10"},
        {"title": "AI news 2", "link": "https://example.com/2", "snippet": "Summary 2", "date": "2026-03-10"},
    ]
}


@pytest.mark.asyncio
async def test_fetch_serper_returns_items(monkeypatch):
    monkeypatch.setattr("src.config.settings.serper_api_key", "fake-key")
    with patch("src.scrapers.serper_scraper.post", AsyncMock(return_value=MOCK_RESPONSE)):
        from src.scrapers.serper_scraper import fetch_serper
        results = await fetch_serper()

    assert len(results) > 0  # query 數量可能變動，只確認有結果
    sources = {r["source"] for r in results}
    assert "serper_en" in sources
    assert "serper_zh" in sources


@pytest.mark.asyncio
async def test_fetch_serper_skips_without_key(monkeypatch):
    monkeypatch.setattr("src.config.settings.serper_api_key", None)
    from src.scrapers.serper_scraper import fetch_serper
    results = await fetch_serper()
    assert results == []


@pytest.mark.asyncio
async def test_fetch_serper_handles_api_error(monkeypatch):
    monkeypatch.setattr("src.config.settings.serper_api_key", "fake-key")
    with patch("src.scrapers.serper_scraper.post", AsyncMock(return_value=None)):
        from src.scrapers.serper_scraper import fetch_serper
        results = await fetch_serper()
    assert results == []


@pytest.mark.asyncio
async def test_serper_output_format(monkeypatch):
    monkeypatch.setattr("src.config.settings.serper_api_key", "fake-key")
    with patch("src.scrapers.serper_scraper.post", AsyncMock(return_value=MOCK_RESPONSE)):
        from src.scrapers.serper_scraper import fetch_serper
        results = await fetch_serper()

    for r in results:
        assert "title" in r
        assert "url" in r
        assert "source" in r
        assert "summary" in r
        assert "published_at" in r
        assert "language" in r
