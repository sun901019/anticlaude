# Flow Lab 選品引擎 API Contract

Date: 2026-03-14
Executable truth: `src/ecommerce/selection.py`
Mounted at: `/api/ecommerce/selection`

---

## 設計原則

- 現有 `/api/ecommerce/*` 路由**不動**，語意是「已上架 SKU 的運營管理」
- 新路由前綴 `/api/ecommerce/selection/*`，語意是「新品候選的評估 pipeline」
- 兩者 lifecycle 不同：候選品通過評估後才能成為 fl_products 的 active SKU

---

## 候選池（Candidates）

### POST `/api/ecommerce/selection/candidates`
新增候選品（可單筆或批量）

Request:
```json
{
  "product_name": "人體工學頸枕",
  "source_platform": "shopee",
  "source_url": "https://...",
  "category": "辦公室舒適",
  "keywords": ["頸枕", "辦公室", "久坐"],
  "market_type": "problem",
  "discovery_notes": "蝦皮熱賣，1星評論多提到材質硬",
  "created_by_agent": "ori"
}
```

Response:
```json
{ "ok": true, "candidate_id": "cand_abc123" }
```

---

### GET `/api/ecommerce/selection/candidates`
列出候選池，支援篩選

Query params:
- `status`: candidate | shortlisted | approved | rejected | all（預設 all）
- `market_type`: demand | trend | problem | hybrid
- `source_platform`: shopee | tiktok | amazon | ...
- `limit`: 預設 50

Response:
```json
[
  {
    "candidate_id": "cand_abc123",
    "product_name": "人體工學頸枕",
    "market_type": "problem",
    "status": "candidate",
    "selection_status": "evaluating",
    "risk_score": null,
    "created_at": "2026-03-14T10:00:00"
  }
]
```

---

### PATCH `/api/ecommerce/selection/candidates/{candidate_id}`
更新候選品狀態或補充資料

Request:
```json
{
  "status": "shortlisted",
  "market_type": "hybrid",
  "risk_flags": ["fragile"]
}
```

---

### GET `/api/ecommerce/selection/candidates/{candidate_id}`
取得單一候選品完整資料（含最新分析）

---

## 分析（Analyses）

### POST `/api/ecommerce/selection/analyze/{candidate_id}`
提交手動評分，計算加權總分與 viability band

Request:
```json
{
  "demand_score": 8,
  "competition_score": 6,
  "profit_score": 7,
  "pain_point_score": 9,
  "brand_fit_score": 8,
  "market_metrics": {
    "demand_stability": "stable",
    "trend_curve": "growing"
  },
  "competition_metrics": {
    "competitor_count": 45,
    "price_ladder_health": "healthy",
    "price_range": [299, 890]
  },
  "financials": {
    "cost_rmb": 38,
    "exchange_rate": 4.5,
    "platform_fee": 0.05,
    "payment_fee": 0.12,
    "ad_cost_est": 50
  },
  "negative_reviews": [
    {"pain_point": "材質偏硬", "frequency": 23, "opportunity": "加強填充設計"},
    {"pain_point": "顏色單調", "frequency": 11, "opportunity": "擴色系"}
  ],
  "analyzed_by_agent": "sage"
}
```

Response:
```json
{
  "ok": true,
  "analysis_id": 1,
  "score_total": 42,
  "score_breakdown": {
    "demand": 8, "profit": 7, "pain_points": 9,
    "competition": 6, "brand_fit": 8,
    "formula": "8*2 + 7*2 + 9 + 6 + 8 = 47 (weighted)",
    "weighted_total": 42
  },
  "viability_band": "strong",
  "recommended_role": "毛利款",
  "role_confidence": 0.82,
  "landed_cost_twd": 256.5,
  "min_viable_price": 489,
  "target_price": 590
}
```

---

### GET `/api/ecommerce/selection/analysis/{candidate_id}`
取得最新分析結果

---

## 報告（Reports）

### POST `/api/ecommerce/selection/reports/{analysis_id}`
對已分析的候選品生成 Markdown 報告

Response:
```json
{
  "ok": true,
  "report_id": 1,
  "report_title": "人體工學頸枕 選品報告 2026-03-14",
  "preview": "## 選品評估報告..."
}
```

---

### GET `/api/ecommerce/selection/reports`
列出所有報告，可依 candidate_id 篩選

---

### GET `/api/ecommerce/selection/reports/{report_id}`
取得完整報告 Markdown

---

## 組合設計（Portfolio）

### GET `/api/ecommerce/selection/portfolio`
計算目前候選池的 traffic/profit/hero 角色分佈

Response:
```json
{
  "approved_count": 3,
  "role_distribution": {
    "引流款": 1,
    "毛利款": 2,
    "主力款": 0
  },
  "portfolio_target": {"引流款": "40%", "毛利款": "40%", "主力款": "20%"},
  "gap": "缺主力款，建議搜尋高毛利高品牌辨識度商品"
}
```

---

### POST `/api/ecommerce/selection/shortlist`
依評分門檻生成推薦清單

Request:
```json
{ "min_score": 35, "max_count": 10 }
```

---

## 學習記憶（Lessons）

### GET `/api/ecommerce/selection/lessons`
列出學習記憶，可依 lesson_type 篩選

### POST `/api/ecommerce/selection/lessons`
手動新增或 AI 生成 lesson

---

## 評分公式

```
score_total = demand*2 + profit*2 + pain_points + competition + brand_fit
```

viability_band 對照：
- `strong`   → 40-50
- `viable`   → 35-39
- `watchlist`→ 30-34
- `reject`   → < 30

---

## Agent 分工

| Endpoint | 負責 Agent |
|---------|-----------|
| POST /candidates | Ori |
| POST /analyze | Sage |
| POST /reports | Craft |
| GET /portfolio | Lala |
| POST /lessons | Sage |

---

## 未來擴充（Phase 4+）

- `POST /selection/import/shopee` — 蝦皮批量匯入
- `POST /selection/reviews/analyze` — Claude API 負評聚類
- `GET /selection/market-map` — 市場圖譜視覺化
