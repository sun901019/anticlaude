"""
測試 RSS 抓取器
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta
import time


def _make_entry(title="Test AI Article", url="https://example.com", hours_ago=1):
    published = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    t = published.timetuple()
    entry = MagicMock()
    entry.title = title
    entry.link = url
    entry.published_parsed = t[:9]
    entry.summary = "<p>Test summary content</p>"
    entry.description = ""
    return entry


def _make_feed(entries, bozo=False):
    feed = MagicMock()
    feed.entries = entries
    feed.bozo = bozo
    return feed


@pytest.mark.asyncio
async def test_fetch_rss_returns_items():
    from src.scrapers.rss_scraper import fetch_rss

    mock_feed = _make_feed([_make_entry(), _make_entry(hours_ago=2)])
    with patch("feedparser.parse", return_value=mock_feed):
        result = await fetch_rss("techcrunch", "https://techcrunch.com/feed/")

    assert len(result) == 2
    assert result[0]["source"] == "techcrunch"
    assert result[0]["language"] == "en"


@pytest.mark.asyncio
async def test_fetch_rss_filters_old_articles():
    from src.scrapers.rss_scraper import fetch_rss

    mock_feed = _make_feed([
        _make_entry(hours_ago=5),    # 新的 → 保留
        _make_entry(hours_ago=30),   # 舊的 → 過濾
    ])
    with patch("feedparser.parse", return_value=mock_feed):
        result = await fetch_rss("ainews", "https://example.com/feed")

    assert len(result) == 1


@pytest.mark.asyncio
async def test_fetch_rss_handles_404():
    from src.scrapers.rss_scraper import fetch_rss

    with patch("feedparser.parse", side_effect=Exception("Connection error")):
        result = await fetch_rss("theverge", "https://example.com/404")

    assert result == []


@pytest.mark.asyncio
async def test_fetch_rss_strips_html_from_summary():
    from src.scrapers.rss_scraper import fetch_rss, _parse_entry

    entry = _make_entry()
    entry.summary = "<p>This is <strong>bold</strong> and <em>italic</em></p>"
    result = _parse_entry(entry, "test")
    assert "<p>" not in result["summary"]
    assert "bold" in result["summary"]


@pytest.mark.asyncio
async def test_fetch_all_rss_gathers_all_sources():
    from src.scrapers.rss_scraper import fetch_all_rss

    mock_feed = _make_feed([_make_entry()])
    with patch("feedparser.parse", return_value=mock_feed):
        results = await fetch_all_rss()

    assert len(results) == 4  # 4 個 feed，各 1 則
