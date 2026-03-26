"""
測試所有核心 API 端點是否正常回應（健康檢查）
"""
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_agent_status_endpoint():
    """/api/agents/status 應回傳 6 個 agent"""
    res = client.get("/api/agents/status")
    assert res.status_code == 200
    data = res.json()
    for agent_id in ["ori", "lala", "craft", "lumi", "sage", "pixel"]:
        assert agent_id in data


def test_agent_events_endpoint():
    """/api/agents/events 應回傳正確格式"""
    res = client.get("/api/agents/events?limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "events" in data
    assert "count" in data
    assert data["count"] == len(data["events"])


def test_reports_endpoint():
    """/api/today 應正常回應（每日報告）"""
    res = client.get("/api/today")
    assert res.status_code == 200


def test_ecommerce_products_endpoint():
    """/api/ecommerce/products 應正常回應"""
    res = client.get("/api/ecommerce/products")
    assert res.status_code == 200


def test_ecommerce_settings_endpoint():
    """/api/ecommerce/settings 應正常回應"""
    res = client.get("/api/ecommerce/settings")
    assert res.status_code == 200


def test_ecommerce_selection_candidates():
    """/api/ecommerce/selection/candidates 應正常回應"""
    res = client.get("/api/ecommerce/selection/candidates")
    assert res.status_code == 200


def test_demo_handoff_endpoint():
    """/api/agents/demo-handoff 應觸發成功"""
    res = client.post("/api/agents/demo-handoff")
    assert res.status_code == 200
    data = res.json()
    assert "handoffs" in data


def test_404_on_unknown_route():
    """未知路由應回傳 404"""
    res = client.get("/api/does-not-exist")
    assert res.status_code == 404
