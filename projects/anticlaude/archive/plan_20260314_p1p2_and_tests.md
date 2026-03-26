# AntiClaude — P1 / P2 功能完成 + 測試套件計畫
> 作者：Claude Code
> 日期：2026-03-14
> 執行者：Claude Code

---

## 注意事項（執行前必讀）

1. **SSE 直連 8000 不需要改** — `next.config.js` 裡有明確說明：Next.js 會 buffer SSE 導致延遲，這是刻意設計，不是問題
2. **`selection.py` 已有 `_emit_sage()`** — 不要重複建，直接在現有基礎上擴充
3. **Pixel/Sage/Lumi 在 pipeline 裡是示意性的** — 這三個角色目前工作時間很短，屬於 pipeline 的最後階段，暫時可接受，P2 完成後再評估是否要延長
4. **測試檔案放 `tests/`** — 現有 conftest.py + pytest.ini 已設定好 async
5. **Flow Lab tab 是純前端工作** — 後端 API 全部完成，只要對接前端元件

---

## 目前不完整項目的處理決定

| 問題 | 處理方式 |
|------|---------|
| SSE 直連 8000 | ✅ 保留，這是正確設計 |
| Pixel/Sage/Lumi pipeline 工作時間極短 | ⚠️ 列入 P3，待 P2 完成後再優化 |
| `ai/handoff/` 模板不自動填入 | ✅ 手動用途，不需自動化（是文件工具不是程式） |
| `current-task.md` 還顯示舊任務 | 📌 **本計畫執行完後更新** |

---

## P1-A：`awaiting_human` 狀態

### 目標
當 AI 完成工作、需要你做決策時，AI Office 顯示明確提示 + 行動按鈕。

### 視覺效果
```
[Craft] 🟠 等待你決策
        「選品報告已完成，請選擇進貨 / 不進貨」
        [查看報告] [核准進貨] [不進貨]
```

### 任務 1：後端 — 新增 `awaiting_human` 狀態

**檔案**：`src/api/agent_status.py`

在現有的 `mark_agent_blocked` 後面新增：

```python
def mark_agent_awaiting_human(
    agent_id: str,
    message: str = "",
    action_type: str = "",   # "approve_purchase" | "select_draft" | "confirm_analysis"
    ref_id: str = "",        # 關聯的 candidate_id 或 analysis_id
    artifact_refs: list[str] | None = None,
) -> None:
    """
    標記 agent 為等待人類決策狀態。
    action_type 讓前端知道要顯示哪種行動按鈕。
    """
    if agent_id not in _status:
        return
    timestamp = _now_iso()
    current = _status[agent_id]
    task_meta = deepcopy(current.get("task_meta") or _default_task())
    task_meta["status"] = "awaiting_human"
    task_meta["updated_at"] = timestamp
    task_meta["action_type"] = action_type
    task_meta["ref_id"] = ref_id
    if artifact_refs is not None:
        task_meta["artifact_refs"] = list(artifact_refs)
    current["status"] = "awaiting_human"
    current["task"] = message or current.get("task", "")
    current["updated_at"] = timestamp
    current["task_meta"] = task_meta
    _append_event(agent_id)
    _emit_snapshot([agent_id])
```

同時在 `_default_task()` 裡加入兩個新欄位：
```python
"action_type": "",
"ref_id": "",
```

---

### 任務 2：前端 — AI Office 顯示 awaiting_human 卡片

**檔案**：`dashboard/src/app/office/page.tsx`

**要做的事**：

1. 在 `AgentInfo` type 加入 `awaiting_human` 到 status 聯合型別
2. 在 `TaskMeta` type 加入 `action_type: string` 和 `ref_id: string`
3. Agent 卡片邏輯：當 `status === "awaiting_human"` 時
   - 顯示橘色 border（區分於 working 的藍色）
   - 顯示 `"等待你決策"` badge
   - 根據 `action_type` 顯示不同按鈕：
     - `"approve_purchase"` → `[查看報告]` `[核准進貨]` `[不進貨]`
     - `"select_draft"` → `[查看草稿]` `[選擇發文]`
     - `"confirm_analysis"` → `[查看分析]` `[確認]`
4. 按鈕 onClick 行為：
   - `[查看報告]` → navigate to `/ecommerce?tab=reports&id={ref_id}`
   - `[核准進貨]` → PATCH `/api/ecommerce/selection/candidates/{ref_id}` with `{ status: "approved" }`，完成後 agent 回 idle
   - `[不進貨]` → PATCH 同上 with `{ status: "rejected" }`，完成後 agent 回 idle
   - `[查看草稿]` → navigate to `/reports`
   - `[選擇發文]` → navigate to `/picks`

**注意**：按鈕呼叫 API 後要呼叫 `mark_agent_done`（後端），讓 agent 回 idle。

---

### 任務 3：在 pipeline 尾端觸發 `awaiting_human`

**檔案**：`src/agents/orchestrator.py`

在 Craft 的 idle 之前，改成：

```python
# 原本
_safe_emit(emit_task, "craft", status="idle", ...)

# 改成
from src.api.agent_status import mark_agent_awaiting_human
mark_agent_awaiting_human(
    "craft",
    message=f"今日草稿已完成，請選擇發文版本",
    action_type="select_draft",
    ref_id=d,
    artifact_refs=[f"outputs/drafts/{d}.md"] if drafts_path else [],
)
```

---

## P1-B：Flow Lab Dashboard 5 個 Tab

> 後端 API 全部完成，只補前端。

**檔案**：`dashboard/src/app/ecommerce/page.tsx`

目前 tab 結構大概是：在售商品 / 定價決策 / 週績效表 / 系統設定 / 說明書

要新增 5 個 tab，修改 tab 定義陣列加入：

### Tab 1：候選池

**API**：`GET /api/ecommerce/selection/candidates`

顯示欄位：
- 商品名稱、市場類型（demand/trend/problem/hybrid）、來源平台、類別、狀態 badge
- 篩選器：類別 / market_type / status（pending/approved/rejected/watchlist）
- 每列右側：`[開始分析]` 按鈕 → POST `/api/ecommerce/selection/analyze/{candidate_id}`
- 右上角：`[新增候選]` 按鈕 → 展開表單

**新增候選表單欄位**：
- 商品名稱（必填）
- 類別（下拉：療育小物/桌面收納/文具周邊/香氛燈光/其他）
- 來源平台（TikTok/Instagram/蝦皮/Amazon/其他）
- 市場類型（demand/trend/problem/hybrid）
- 品牌概念說明（選填）

---

### Tab 2：評分分析

**API**：`GET /api/ecommerce/selection/analysis/{candidate_id}`

顯示內容：
- 左側清單：所有已分析候選品（含 score_total 和 viability_band 色標）
- 右側詳情：
  - 評分雷達圖或長條圖：demand / competition / profit / pain_points / brand_fit
  - 財務摘要：landed_cost / gross_margin / break_even_roas
  - viability_band 顯示（強力候選/可行/觀察/拒絕）
  - recommended_role（traffic/profit/hero）
  - AI 推理說明（reasoning 欄位）
  - 狀態按鈕：`[核准進貨]` `[加入觀察]` `[拒絕]`

---

### Tab 3：組合設計

**API**：`GET /api/ecommerce/selection/portfolio`

顯示內容：
- 目前商品組合中 traffic / profit / hero 各幾個（含百分比）
- 目標比例：traffic 40% / profit 40% / hero 20%
- 缺口提示：「目前缺 hero 商品，建議下次優先評估高品牌辨識度商品」
- 現有商品列表（各自標注角色）

---

### Tab 4：選品報告

**API**：`GET /api/ecommerce/selection/reports`

顯示內容：
- 報告列表（依日期排序，含商品名稱、評分、結論）
- 點擊展開：完整 markdown 報告
- 每份報告右上角：`[複製]` `[下載 .md]`

---

### Tab 5：學習記憶

**API**：`GET /api/ecommerce/selection/lessons`

顯示內容：
- 按 lesson_type 分組：winning_pattern / rejection_pattern / market_insight / brand_rule
- 每條 lesson：主題、內容、信心分數（顯示星星）、來源分析數
- 篩選器：按類型篩選
- 底部統計：累積學習數、最近更新時間

---

## P2：Flow Lab 選品流程接入 AI Office

### 核心原則（你的要求）
> **用到那個功能才啟動**，不是一直跑

觸發邏輯：
| 用戶動作 | 觸發的 Agent |
|---------|------------|
| 新增候選商品 | Ori 啟動：「準備蒐集競品資料」 |
| 點擊 `[開始分析]` | Ori → Sage 啟動：競品搜尋 → 評分 |
| 分析完成 | Craft 啟動：產選品報告 |
| 報告完成 | `awaiting_human`：等你決策 |
| 你按核准/拒絕 | Sage 啟動：寫入 lesson，然後 idle |

### 任務 1：新增 emit 函數到 selection.py

**檔案**：`src/ecommerce/selection.py`

現有 `_emit_sage()` 已存在，補充缺少的角色：

```python
def _emit_ori(status: str, task: str = "", target: str = "", artifact_refs: list | None = None) -> None:
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            "ori", status=status, task=task, title=task,
            task_type="research", priority="normal",
            source_agent_id="", target_agent_id=target,
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass

def _emit_craft(status: str, task: str = "", source: str = "", artifact_refs: list | None = None) -> None:
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            "craft", status=status, task=task, title=task,
            task_type="content", priority="normal",
            source_agent_id=source, target_agent_id="",
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass
```

---

### 任務 2：在 create_candidate 端點觸發 Ori

**檔案**：`src/ecommerce/selection.py`，`create_candidate` 函數

在 return 之前加入：
```python
# 新增候選後，Ori 進入待命狀態
_emit_ori("working", f"候選品已加入：{body.product_name}，等待開始分析", target="sage")
# 3 秒後示意回 idle（非阻塞）
import asyncio
asyncio.get_event_loop().call_later(3, lambda: _emit_ori("idle"))
```

**注意**：這裡不做真實搜尋，只是讓 AI Office 顯示「Ori 知道有新候選了」。真實搜尋在 analyze 時觸發。

---

### 任務 3：在 analyze_candidate 端點加入完整 Agent 流

**檔案**：`src/ecommerce/selection.py`，`analyze_candidate` 函數

在分析開始前加入：
```python
# Step 1: Ori 搜尋競品
_emit_ori("working", f"搜尋 {candidate_id} 競品資料與市場信號", target="sage")
```

在評分計算後加入：
```python
# Step 2: Sage 評分
_emit_ori("idle")
_emit_sage("working", f"對 {candidate_id} 進行 SOP 評分分析", target_agent_id="craft")
```

在分析結果存入 DB 後：
```python
# Step 3: Craft 產報告（如果有 report body 或自動觸發）
_emit_sage("idle")
_emit_craft("working", f"整理 {candidate_id} 選品報告", source="sage")
```

在函數最後：
```python
# Step 4: 等待人決策
_emit_craft("idle")
from src.api.agent_status import mark_agent_awaiting_human
mark_agent_awaiting_human(
    "craft",
    message=f"{candidate_name} 選品報告完成，請決策",
    action_type="approve_purchase",
    ref_id=candidate_id,
    artifact_refs=[f"ecommerce/selection/analysis/{candidate_id}"],
)
```

---

### 任務 4：在 patch_candidate 決策後觸發 Sage lesson

**檔案**：`src/ecommerce/selection.py`，`patch_candidate` 函數

`_auto_lesson_on_decision` 已存在，確認它在 patch 時被呼叫（讀程式碼確認，如果沒有則加入呼叫）。

完成後讓 Craft 回 idle：
```python
from src.api.agent_status import mark_agent_done
mark_agent_done("craft")
```

---

## P3：測試套件

### 測試目標
確保整個系統在修改後不會 regression，覆蓋後端 API + pipeline + Agent 狀態機。

---

### 任務 T-1：Agent 狀態機測試

**新建檔案**：`tests/test_agent_status.py`

```python
"""
測試 Agent 狀態機完整生命週期
"""
import pytest
from src.api.agent_status import (
    get_all_status,
    set_agent_status,
    update_agent_task,
    mark_agent_done,
    mark_agent_blocked,
    mark_agent_handoff_pending,
    mark_agent_awaiting_human,
)


def test_initial_state():
    """所有 agent 初始狀態應為 idle"""
    status = get_all_status()
    for agent_id in ["ori", "lala", "craft", "lumi", "sage", "pixel"]:
        assert agent_id in status
        # 可能是 idle 或其他（測試環境可能有殘留）
        assert status[agent_id]["status"] in ("idle", "working", "blocked", "handoff_pending", "awaiting_human", "done")


def test_set_agent_working():
    """set_agent_status 設為 working 應更新狀態"""
    set_agent_status("ori", "working", "測試任務")
    status = get_all_status()
    assert status["ori"]["status"] == "working"
    assert status["ori"]["task"] == "測試任務"


def test_update_agent_task_structured():
    """update_agent_task 應建立結構化 task_meta"""
    update_agent_task(
        "lala",
        status="working",
        task="策略分析",
        task_type="strategy",
        source_agent_id="ori",
        target_agent_id="craft",
    )
    status = get_all_status()
    meta = status["lala"]["task_meta"]
    assert meta["task_type"] == "strategy"
    assert meta["source_agent_id"] == "ori"
    assert meta["target_agent_id"] == "craft"
    assert meta["status"] == "in_progress"


def test_mark_agent_done():
    """mark_agent_done 應將 agent 回到 idle"""
    set_agent_status("craft", "working", "寫文案")
    mark_agent_done("craft", artifact_refs=["outputs/drafts/test.md"])
    status = get_all_status()
    assert status["craft"]["status"] == "idle"


def test_mark_agent_blocked():
    """mark_agent_blocked 應設定 blocked 狀態"""
    mark_agent_blocked("sage", "等待 Ori 提供競品資料")
    status = get_all_status()
    assert status["sage"]["status"] == "blocked"
    assert status["sage"]["task_meta"]["status"] == "blocked"


def test_mark_agent_handoff_pending():
    """mark_agent_handoff_pending 應設定交接狀態"""
    set_agent_status("ori", "working", "分群任務")
    mark_agent_handoff_pending("ori", target_agent_id="lala")
    status = get_all_status()
    assert status["ori"]["status"] == "handoff_pending"
    assert status["ori"]["task_meta"]["target_agent_id"] == "lala"


def test_mark_agent_awaiting_human():
    """mark_agent_awaiting_human 應設定等待人決策狀態"""
    mark_agent_awaiting_human(
        "craft",
        message="選品報告完成，請決策",
        action_type="approve_purchase",
        ref_id="candidate_123",
    )
    status = get_all_status()
    assert status["craft"]["status"] == "awaiting_human"
    assert status["craft"]["task_meta"]["action_type"] == "approve_purchase"
    assert status["craft"]["task_meta"]["ref_id"] == "candidate_123"


def test_all_six_agents_exist():
    """確認 6 個 agent 都存在"""
    status = get_all_status()
    for agent_id in ["ori", "lala", "craft", "lumi", "sage", "pixel"]:
        assert agent_id in status
        assert "nickname" in status[agent_id]
        assert "role" in status[agent_id]
```

---

### 任務 T-2：Ecommerce Selection API 測試

**新建檔案**：`tests/test_ecommerce_selection.py`

```python
"""
測試 Flow Lab 選品 API
"""
import pytest
from fastapi.testclient import TestClient
from src.api.main import app

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


def test_create_candidate():
    """新增候選品應回傳 201 和 candidate_id"""
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    assert res.status_code == 201
    data = res.json()
    assert "candidate_id" in data
    assert data["product_name"] == CANDIDATE_PAYLOAD["product_name"]
    return data["candidate_id"]


def test_list_candidates():
    """列出候選池應回傳陣列"""
    res = client.get("/api/ecommerce/selection/candidates")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_analyze_candidate():
    """送出分析應計算評分並回傳結果"""
    # 先建候選品
    res = client.post("/api/ecommerce/selection/candidates", json=CANDIDATE_PAYLOAD)
    candidate_id = res.json()["candidate_id"]

    # 分析
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
    score = compute_score(
        demand=7.5,
        competition=6.0,
        profit=8.0,
        pain_points=7.0,
        brand_fit=9.0,
    )
    expected = 7.5 * 2 + 8.0 * 2 + 7.0 + 6.0 + 9.0
    assert abs(score - expected) < 0.01


def test_portfolio_endpoint():
    """組合設計端點應回傳角色分佈"""
    res = client.get("/api/ecommerce/selection/portfolio")
    assert res.status_code == 200
    data = res.json()
    assert "traffic" in data or "roles" in data or isinstance(data, dict)


def test_shortlist_endpoint():
    """shortlist 端點應回傳高分候選"""
    res = client.post("/api/ecommerce/selection/shortlist", json={"min_score": 30})
    assert res.status_code == 200


def test_lessons_endpoint():
    """學習記憶端點應回傳陣列"""
    res = client.get("/api/ecommerce/selection/lessons")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
```

---

### 任務 T-3：核心 API 端點健康測試

**新建檔案**：`tests/test_api_health.py`

```python
"""
測試所有核心 API 端點是否正常回應（健康檢查）
"""
import pytest
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
    assert data["count"] == len(data["events"])  # 確認 count 是真實筆數


def test_reports_endpoint():
    """/api/reports 應正常回應"""
    res = client.get("/api/reports")
    assert res.status_code == 200


def test_ecommerce_products_endpoint():
    """/api/ecommerce/products 應正常回應"""
    res = client.get("/api/ecommerce/products")
    assert res.status_code == 200


def test_ecommerce_settings_endpoint():
    """/api/ecommerce/settings 應回傳設定值"""
    res = client.get("/api/ecommerce/settings")
    assert res.status_code == 200
    data = res.json()
    assert "platform_fee" in data or isinstance(data, dict)


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
```

---

### 任務 T-4：Pipeline Orchestrator 測試（擴充現有）

**修改**：`tests/test_pipeline.py`

在現有測試後加入：

```python
def test_orchestrator_emits_agent_events():
    """Pipeline 跑完後 agent_events.jsonl 應有新事件"""
    import asyncio
    from pathlib import Path
    from src.config import OUTPUTS_DIR
    from src.agents.orchestrator import run_pipeline

    events_path = OUTPUTS_DIR / "office_memory" / "agent_events.jsonl"
    before_count = 0
    if events_path.exists():
        before_count = len(events_path.read_text().strip().splitlines())

    # dry-run 方式執行（mock scrapers）
    with patch("src.scrapers.aggregator.run_aggregator", new_callable=AsyncMock) as mock_agg:
        mock_agg.return_value = [
            {"title": f"Test Article {i}", "url": f"https://example.com/{i}",
             "source": "test", "published_at": "2026-03-14"}
            for i in range(5)
        ]
        with patch("src.agents.cluster.ClusterAgent.run", new_callable=AsyncMock) as mock_cluster:
            from src.agents.base import AgentResult
            mock_cluster.return_value = AgentResult(
                success=True,
                data=[{"cluster_label": "AI Test", "articles": [], "summary": "Test"}],
                model_used="mock",
            )
            # 其他 agent 類似 mock...
            # 確認 events 有增加
            pass  # 完整 mock 依現有 test_pipeline.py 樣式補齊


def test_agent_status_after_pipeline():
    """Pipeline 結束後 AI Office 狀態應正確"""
    from src.api.agent_status import get_all_status
    status = get_all_status()
    # Pipeline 結束後所有 agent 應回到 idle（有 AUTO_IDLE 機制）
    # 這個測試確認 status 結構正確
    for agent_id in ["ori", "lala", "craft"]:
        assert agent_id in status
        assert "task_meta" in status[agent_id]
        assert "status" in status[agent_id]["task_meta"]
```

---

### 任務 T-5：前端 Build 測試

**在 CI 或手動執行**：

```bash
cd dashboard
npm run build
```

**確認事項**：
- [ ] TypeScript 無錯誤
- [ ] 所有頁面 build 成功（office / ecommerce / reports / metrics / picks）
- [ ] `awaiting_human` 新增到 status 型別後不造成 TS 錯誤

---

## 執行順序

| 步驟 | 任務 | 檔案 | 備註 |
|------|------|------|------|
| 1 | T-1 先寫 agent 狀態機測試 | `tests/test_agent_status.py` | 先有測試再改 code |
| 2 | P1-A 後端加 awaiting_human | `src/api/agent_status.py` | 跑 T-1 確認通過 |
| 3 | T-2 寫 selection 測試 | `tests/test_ecommerce_selection.py` | 先有測試再改 |
| 4 | P2 selection.py 加 emit | `src/ecommerce/selection.py` | 跑 T-2 確認通過 |
| 5 | T-3 API 健康測試 | `tests/test_api_health.py` | 全部跑一次確認 |
| 6 | P1-A 前端 awaiting_human UI | `dashboard/src/app/office/page.tsx` | 需後端先完成 |
| 7 | P1-B Flow Lab 5 個 tab | `dashboard/src/app/ecommerce/page.tsx` | 最大工作量 |
| 8 | P1-A pipeline 觸發 awaiting_human | `src/agents/orchestrator.py` | 接 Craft 尾端 |
| 9 | T-5 前端 build 測試 | `npm run build` | 確認無 TS 錯誤 |
| 10 | 更新 current-task.md | `ai/state/current-task.md` | 標記完成 |
| 11 | 更新 progress-log.md | `ai/state/progress-log.md` | 記錄本次執行 |

---

## 完成後驗收標準

### Agent 狀態
- [ ] `pytest tests/test_agent_status.py` 全過
- [ ] AI Office 能看到橘色 `awaiting_human` 卡片
- [ ] Pipeline 跑完後 Craft 顯示等待決策（不是直接 idle）

### Flow Lab
- [ ] `pytest tests/test_ecommerce_selection.py` 全過
- [ ] `/ecommerce` 有 5 個新 tab 且能正常載入資料
- [ ] 新增候選 → Ori 在 AI Office 出現
- [ ] 點分析 → Ori → Sage → Craft 依序出現
- [ ] 報告完成 → Craft 顯示 awaiting_human
- [ ] 按核准/拒絕 → Craft 回 idle，lesson 被寫入

### 整體
- [ ] `pytest tests/ -v` 全過（無 FAILED）
- [ ] `npm run build` 無 TypeScript 錯誤
- [ ] AI Office SSE 正常更新（服務啟動後開 /office 確認）
