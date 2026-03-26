"""
測試 Flow Lab 選品 API
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.db.connection import db
import src.domains.flow_lab.selection as selection_module
import threading

client = TestClient(app)

CANDIDATE_PAYLOAD = {
    "product_name": "測試桌面植物盆栽",
    "category": "療育小物",
    "source_platform": "TikTok",
    "market_type": "problem",
    "brand_concept": "辦公桌療癒",
}

ANALYSIS_PAYLOAD = {
    "demand_score": 7.5,
    "competition_score": 6.0,
    "profit_score": 8.0,
    "pain_point_score": 7.0,
    "brand_fit_score": 9.0,
    "cost_rmb": 25.0,
    "target_price": 299.0,
    "market_type": "problem",
    "demand_signal_summary": "搜尋量穩定，IG 多人分享",
    "competitive_landscape_notes": "競品多但品質參差",
    "pain_points": [{"pain": "容易掉葉子", "frequency": 8}],
    "improvement_opportunity": "改用耐旱品種",
    "reasoning": "適合品牌定位，利潤空間良好",
    "recommended_role": "profit",
}


def _create_candidate(status=None):
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    assert res.status_code in (200, 201)
    candidate_id = res.json()["candidate_id"]
    if status:
        patched = client.patch(
            f"/api/ecommerce/selection/candidates/{candidate_id}",
            json={"status": status},
        )
        assert patched.status_code == 200
    return candidate_id


def test_create_candidate():
    """新增候選品應回傳 candidate_id"""
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    assert res.status_code in (200, 201)
    data = res.json()
    assert "candidate_id" in data


def test_list_candidates():
    """列出候選池應回傳陣列"""
    res = client.get("/api/ecommerce/selection/candidates")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_analyze_candidate():
    """送出分析應計算評分並回傳結果"""
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    assert res.status_code in (200, 201)
    candidate_id = res.json()["candidate_id"]

    res = client.post(
        f"/api/ecommerce/selection/analyze/{candidate_id}",
        json=ANALYSIS_PAYLOAD,
    )
    assert res.status_code in (200, 201)
    data = res.json()
    assert "score_total" in data
    assert data["score_total"] > 0
    assert "viability_band" in data


def test_score_calculation():
    """評分公式：demand×2 + profit×2 + pain_points + competition + brand_fit"""
    from src.ecommerce.selection import compute_score
    score, band = compute_score(
        demand=7.5,
        competition=6.0,
        profit=8.0,
        pain_point=7.0,
        brand_fit=9.0,
    )
    expected = 7.5 * 2 + 8.0 * 2 + 7.0 + 6.0 + 9.0
    assert abs(score - expected) < 0.01
    assert band in ("strong", "viable", "watchlist", "reject")


def test_portfolio_endpoint():
    """組合設計端點應回傳角色分佈"""
    res = client.get("/api/ecommerce/selection/portfolio")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)


@pytest.mark.skip(reason="Deprecated test fixture assumed fl_products.total_stock; replacement pending schema-aligned rewrite.")
def test_bundles_suggest_endpoint_uses_latest_performance_margin():
    """Bundles suggest should not depend on a non-existent fl_products.gross_margin_est column."""
    with db() as conn:
        conn.execute(
            """
            INSERT INTO fl_products (
                sku, name, role, target_price, total_stock, status, family_id, family_name, variant_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("FL-BDL-001", "Desk Cat A", "引流款", 199, 12, "listed", "FAM-CAT", "躺贏招財貓", "閒樂款"),
        )
        conn.execute(
            """
            INSERT INTO fl_products (
                sku, name, role, target_price, total_stock, status, family_id, family_name, variant_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("FL-BDL-002", "Desk Cat B", "毛利款", 299, 9, "listed", "FAM-CAT", "躺贏招財貓", "招財款"),
        )
        conn.execute(
            """
            INSERT INTO fl_performance (
                sku, record_date, current_price, sales_7d, revenue_7d, ad_spend_7d, current_stock, gross_profit, gross_margin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("FL-BDL-001", "2026-03-22", 199, 7, 1393, 0, 12, 400, 0.28),
        )
        conn.execute(
            """
            INSERT INTO fl_performance (
                sku, record_date, current_price, sales_7d, revenue_7d, ad_spend_7d, current_stock, gross_profit, gross_margin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("FL-BDL-002", "2026-03-22", 299, 5, 1495, 0, 9, 700, 0.46),
        )

    res = client.post("/api/ecommerce/selection/bundles/suggest")
    assert res.status_code == 200
    body = res.json()
    assert "suggestions" in body
    assert isinstance(body["suggestions"], list)


def test_shortlist_endpoint():
    """shortlist 端點應回傳高分候選"""
    res = client.post("/api/ecommerce/selection/shortlist", json={"min_score": 30})
    assert res.status_code == 200


def test_lessons_endpoint():
    """學習記憶端點應回傳陣列"""
    res = client.get("/api/ecommerce/selection/lessons")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_patch_candidate_approved_triggers_lesson():
    """核准候選品後，lessons 表應新增一筆記錄"""
    # 建候選品
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    assert res.status_code in (200, 201)
    candidate_id = res.json()["candidate_id"]

    # 先記錄 lesson 數量
    lessons_before = len(client.get("/api/ecommerce/selection/lessons").json())

    # 核准
    res = client.patch(
        f"/api/ecommerce/selection/candidates/{candidate_id}",
        json={"status": "approved"},
    )
    assert res.status_code == 200

    # lesson 數量應增加
    lessons_after = len(client.get("/api/ecommerce/selection/lessons").json())
    assert lessons_after > lessons_before


def test_patch_candidate_rejected_triggers_lesson():
    """拒絕候選品後，lessons 表應新增一筆記錄"""
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    assert res.status_code in (200, 201)
    candidate_id = res.json()["candidate_id"]

    lessons_before = len(client.get("/api/ecommerce/selection/lessons").json())

    res = client.patch(
        f"/api/ecommerce/selection/candidates/{candidate_id}",
        json={"status": "rejected"},
    )
    assert res.status_code == 200

    lessons_after = len(client.get("/api/ecommerce/selection/lessons").json())
    assert lessons_after > lessons_before


def test_promote_approved_candidate():
    candidate_id = _create_candidate()

    analyzed = client.post(
        f"/api/ecommerce/selection/analyze/{candidate_id}",
        json=ANALYSIS_PAYLOAD,
    )
    assert analyzed.status_code in (200, 201)

    approved = client.patch(
        f"/api/ecommerce/selection/candidates/{candidate_id}",
        json={"status": "approved"},
    )
    assert approved.status_code == 200

    res = client.post(f"/api/ecommerce/selection/candidates/{candidate_id}/promote")
    assert res.status_code == 200
    data = res.json()
    assert data["ok"] is True
    assert data["sku"].startswith("FL-")

    with db() as conn:
        product = conn.execute(
            "SELECT sku, name FROM fl_products WHERE sku=?",
            (data["sku"],),
        ).fetchone()

    assert product is not None
    assert product["name"] == CANDIDATE_PAYLOAD["product_name"]


def test_promote_non_approved_candidate():
    candidate_id = _create_candidate(status="candidate")

    res = client.post(f"/api/ecommerce/selection/candidates/{candidate_id}/promote")
    assert res.status_code == 400
    body = res.json()
    assert "detail" in body


def test_batch_analyze_returns_count(monkeypatch):
    first_id = _create_candidate()
    second_payload = dict(CANDIDATE_PAYLOAD)
    second_payload["product_name"] = "第二個候選品"
    res = client.post("/api/ecommerce/selection/candidates", json=second_payload)
    assert res.status_code in (200, 201)
    second_id = res.json()["candidate_id"]

    calls = []

    def fake_auto_analyze(candidate_id, body):
        calls.append((candidate_id, body.category))
        return {"ok": True}

    class ImmediateThread:
        def __init__(self, target=None, daemon=None):
            self._target = target

        def start(self):
            if self._target:
                self._target()

    monkeypatch.setattr(selection_module, "auto_analyze_candidate", fake_auto_analyze)
    monkeypatch.setattr(threading, "Thread", ImmediateThread)

    batch = client.post("/api/ecommerce/selection/batch-analyze")
    assert batch.status_code == 200
    data = batch.json()
    # count >= 2 because full-suite runs may leave other candidates in DB
    assert data["count"] >= 2
    candidate_names = set(data["candidates"])
    assert CANDIDATE_PAYLOAD["product_name"] in candidate_names
    assert second_payload["product_name"] in candidate_names
    # both our specific candidates must have been analyzed
    assert first_id in {cid for cid, _ in calls}
    assert second_id in {cid for cid, _ in calls}
