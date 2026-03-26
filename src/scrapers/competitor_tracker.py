"""
Competitor price tracker — LINE alert on price drops.

Flow:
  1. For each keyword, search Shopee via Serper to extract current price.
  2. Load previous price from DB (competitor_price_history table).
  3. Compute change_pct = (current - previous) / previous * 100.
  4. Store current price in DB as the new baseline.
  5. If any keyword dropped > DROP_THRESHOLD_PCT, send a LINE Notify message.
"""
import json
import re
from datetime import datetime, timezone

from src.db.connection import db
from src.utils.logger import get_logger

log = get_logger("competitor_tracker")

DROP_THRESHOLD_PCT = -10.0  # alert when price falls more than 10%


def _ensure_table() -> None:
    """Create competitor_price_history table if it doesn't exist."""
    with db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS competitor_price_history (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword    TEXT NOT NULL,
                price      REAL NOT NULL,
                checked_at TEXT NOT NULL
            )"""
        )


def _load_previous_price(keyword: str) -> float | None:
    """Return the most recent stored price for this keyword, or None."""
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT price FROM competitor_price_history WHERE keyword=? ORDER BY checked_at DESC LIMIT 1",
                (keyword,),
            ).fetchone()
        return float(row["price"]) if row else None
    except Exception as e:
        log.warning(f"Could not load previous price for '{keyword}': {e}")
        return None


def _store_price(keyword: str, price: float) -> None:
    """Persist current price as the new baseline."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with db() as conn:
            conn.execute(
                "INSERT INTO competitor_price_history (keyword, price, checked_at) VALUES (?,?,?)",
                (keyword, price, now),
            )
    except Exception as e:
        log.warning(f"Could not store price for '{keyword}': {e}")


def _extract_price(hits: list[dict]) -> float | None:
    """Parse the first NT$ price from Serper search results."""
    for hit in hits:
        text = f"{hit.get('title', '')} {hit.get('snippet', '')}"
        m = re.search(r'NT?\$?\s*([\d,]+)', text)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                continue
    return None


async def check_competitor_prices(product_keywords: list[str]) -> list[dict]:
    """
    Search current prices for each keyword.
    Returns list of dicts: {keyword, found_price, previous_price, change_pct, source_url}
    """
    from src.scrapers.serper_client import search as serper_search

    _ensure_table()
    results = []

    for keyword in product_keywords:
        try:
            hits = await serper_search(f"{keyword} 價格 shopee")
            current_price = _extract_price(hits)
            previous_price = _load_previous_price(keyword)
            source_url = hits[0].get("link", "") if hits else ""

            # Compute change_pct only when we have both prices
            if current_price is not None and previous_price is not None and previous_price > 0:
                change_pct = (current_price - previous_price) / previous_price * 100.0
            else:
                change_pct = 0.0

            # Store current as new baseline
            if current_price is not None:
                _store_price(keyword, current_price)

            results.append({
                "keyword": keyword,
                "found_price": current_price,
                "previous_price": previous_price,
                "change_pct": change_pct,
                "source_url": source_url,
            })
        except Exception as e:
            log.warning(f"Price check failed for '{keyword}': {e}")
            results.append({
                "keyword": keyword,
                "found_price": None,
                "previous_price": None,
                "change_pct": 0.0,
                "source_url": "",
            })

    return results


async def run_price_check_and_notify(keywords: list[str]) -> dict:
    """Check prices and send LINE alert if any dropped more than DROP_THRESHOLD_PCT."""
    if not keywords:
        return {"checked": 0, "alerts_sent": 0, "results": []}

    results = await check_competitor_prices(keywords)
    alerts_sent = 0

    drops = [r for r in results if r["change_pct"] < DROP_THRESHOLD_PCT]
    if drops:
        lines = [f"• {r['keyword']}: {r['change_pct']:.1f}% (NT${r['found_price']:.0f})" for r in drops]
        msg = "🔔 競品降價提醒\n" + "\n".join(lines)
        try:
            from src.utils.notify import send_line_notify
            await send_line_notify(msg)
            alerts_sent = len(drops)
            log.info(f"LINE alert sent for {len(drops)} price drops")
        except Exception as e:
            log.warning(f"LINE notify failed: {e}")

    return {
        "checked": len(results),
        "alerts_sent": alerts_sent,
        "results": results,
    }
