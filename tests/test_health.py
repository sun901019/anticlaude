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
    test_db_path = test_db_dir / "test_health.db"
    if test_db_path.exists():
        test_db_path.unlink()
    monkeypatch.setattr(db_connection, "DB_PATH", test_db_path)
    init_db()


def test_api_health_returns_ok():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "timestamp" in data


def test_ecommerce_alerts_returns_empty_list_on_empty_db():
    res = client.get("/api/ecommerce/alerts")
    assert res.status_code == 200
    data = res.json()
    assert data == {"alerts": [], "count": 0}


def test_ecommerce_performance_history_has_history_key():
    res = client.get("/api/ecommerce/performance-history")
    assert res.status_code == 200
    data = res.json()
    assert "history" in data
    assert isinstance(data["history"], list)
