"""Tests for competitor_tracker — 7 test cases covering price extraction, change_pct, and alert logic."""
import sqlite3
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from contextlib import contextmanager


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_in_memory_db():
    """Return a fresh in-memory SQLite connection with row_factory set."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return conn


# ── 1. _ensure_table creates the table ────────────────────────────────────────

def test_ensure_table_creates_table():
    """_ensure_table() must create competitor_price_history in the DB."""
    conn = _make_in_memory_db()

    @contextmanager
    def fake_db():
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    with patch("src.scrapers.competitor_tracker.db", fake_db):
        from src.scrapers.competitor_tracker import _ensure_table
        _ensure_table()

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='competitor_price_history'"
    ).fetchall()
    assert len(tables) == 1, "competitor_price_history table should exist after _ensure_table()"
    conn.close()


# ── 2. _extract_price finds NT$ price ─────────────────────────────────────────

def test_extract_price_finds_nt_price():
    """_extract_price should parse NT$350 from title text and return 350.0."""
    from src.scrapers.competitor_tracker import _extract_price
    hits = [{"title": "Product NT$350", "snippet": ""}]
    result = _extract_price(hits)
    assert result == 350.0, f"Expected 350.0, got {result}"


# ── 3. _extract_price returns None when no price present ──────────────────────

def test_extract_price_returns_none_for_no_price():
    """_extract_price should return None when no NT$ price is found."""
    from src.scrapers.competitor_tracker import _extract_price
    hits = [{"title": "no price here", "snippet": ""}]
    result = _extract_price(hits)
    assert result is None, f"Expected None, got {result}"


# ── 4. change_pct computed correctly ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_change_pct_computed_correctly():
    """change_pct should be approx -10.0 when previous=400 and current=360."""
    fake_hits = [{"title": "NT$360", "snippet": "", "link": "http://example.com"}]

    with patch("src.scrapers.competitor_tracker._load_previous_price", return_value=400.0), \
         patch("src.scrapers.competitor_tracker._store_price"), \
         patch("src.scrapers.competitor_tracker._ensure_table"), \
         patch("src.scrapers.serper_client.search", new_callable=AsyncMock, return_value=fake_hits):

        # Reload to pick up patched serper_client inside the function's local import
        import sys
        import src.scrapers.serper_client as sc_mod
        original_search = sc_mod.search
        sc_mod.search = AsyncMock(return_value=fake_hits)
        try:
            from src.scrapers.competitor_tracker import check_competitor_prices
            results = await check_competitor_prices(["test"])
        finally:
            sc_mod.search = original_search

    assert len(results) == 1
    change_pct = results[0]["change_pct"]
    assert abs(change_pct - (-10.0)) < 0.01, f"Expected change_pct ~-10.0, got {change_pct}"


# ── 5. No alert when change_pct is zero ───────────────────────────────────────

@pytest.mark.asyncio
async def test_no_alert_when_change_pct_zero():
    """run_price_check_and_notify should send 0 alerts when prices are the same."""
    from src.scrapers import competitor_tracker

    mock_results = [
        {"keyword": "item_a", "found_price": 300.0, "previous_price": 300.0,
         "change_pct": 0.0, "source_url": ""}
    ]

    with patch.object(competitor_tracker, "check_competitor_prices", new_callable=AsyncMock) as mock_check:
        mock_check.return_value = mock_results
        result = await competitor_tracker.run_price_check_and_notify(["item_a"])

    assert result["alerts_sent"] == 0, f"Expected 0 alerts, got {result['alerts_sent']}"


# ── 6. Alert sent on big drop (−20%) ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_alert_sent_on_big_drop():
    """send_line_notify must be called when price drops more than 10% (previous=500, current=400 → -20%)."""
    from src.scrapers import competitor_tracker
    import src.utils.notify as notify_mod

    mock_results = [
        {"keyword": "gadget", "found_price": 400.0, "previous_price": 500.0,
         "change_pct": -20.0, "source_url": ""}
    ]

    mock_notify = AsyncMock()
    original_notify = notify_mod.send_line_notify
    notify_mod.send_line_notify = mock_notify

    try:
        with patch.object(competitor_tracker, "check_competitor_prices", new_callable=AsyncMock) as mock_check:
            mock_check.return_value = mock_results
            result = await competitor_tracker.run_price_check_and_notify(["gadget"])
    finally:
        notify_mod.send_line_notify = original_notify

    mock_notify.assert_called_once()
    assert result["alerts_sent"] == 1, f"Expected 1 alert, got {result['alerts_sent']}"


# ── 7. Empty keywords returns zero ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_empty_keywords_returns_zero():
    """run_price_check_and_notify([]) should return checked=0, alerts_sent=0, results=[]."""
    from src.scrapers.competitor_tracker import run_price_check_and_notify
    result = await run_price_check_and_notify([])
    assert result == {"checked": 0, "alerts_sent": 0, "results": []}
