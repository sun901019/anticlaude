from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.db.schema import init_db
import src.db.connection as db_connection

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_db(monkeypatch):
    test_db_dir = Path("tests/.tmp")
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db_path = test_db_dir / "test_new_endpoints.db"
    if test_db_path.exists():
        test_db_path.unlink()
    # Override env var (takes priority over DB_PATH in _resolve_db_path)
    monkeypatch.setenv("ANTICLAUDE_DB", str(test_db_path))
    init_db()


def test_auto_flag_returns_flagged_product():
    with db_connection.db() as conn:
        conn.execute(
            """
            INSERT INTO fl_products (sku, name, product_type, status)
            VALUES ('FL-01', 'Low Margin Product', 'general', 'active')
            """
        )
        conn.execute(
            """
            INSERT INTO fl_performance
            (sku, record_date, current_price, sales_7d, revenue_7d, ad_spend_7d, current_stock, roas, gross_profit, gross_margin, next_action)
            VALUES ('FL-01', date('now'), 100, 2, 200, 50, 3, 1.2, 10, 0.05, '')
            """
        )

    res = client.post("/api/ecommerce/auto-flag")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] == 1
    assert len(data["flagged"]) == 1
    assert data["flagged"][0]["sku"] == "FL-01"
    assert data["flagged"][0]["action"]


def test_system_logs_returns_logs_and_date(monkeypatch):
    logs_dir = Path("tests/.tmp/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    (logs_dir / f"{today}.log").write_text(
        "2026-03-16 12:00:00 | ERROR    | api | something failed\n"
        "2026-03-16 12:01:00 | WARNING  | api | something odd\n",
        encoding="utf-8",
    )

    monkeypatch.setattr("src.config.LOGS_DIR", logs_dir)

    res = client.get("/api/system/logs")
    assert res.status_code == 200
    data = res.json()
    assert "logs" in data
    assert "date" in data
    assert isinstance(data["logs"], list)
    assert data["date"] == today


def test_performance_history_has_history_key():
    res = client.get("/api/ecommerce/performance-history")
    assert res.status_code == 200
    data = res.json()
    assert "history" in data
