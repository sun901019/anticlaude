# AITOS v2 完整升級規劃
> 作者：Claude Code
> 日期：2026-03-17
> 依據：用戶提供的 AITOS 5 層架構願景 + GEO 技能包需求 + LangGraph 升級討論
> 原則：最小侵入、現有系統不中斷、分階段升級

---

## 一、系統現況快照（2026-03-17）

```
目前完成度：約 78%（Phase 1-5 全部落地）

✅ 已完成
├── 6 個 AI Agent（Ori/Lala/Craft/Sage/Lumi/Pixel）
├── CEO Agent（意圖偵測 + 15 種任務路由 + 視覺輸入）
├── Dynamic Orchestrator（7 種任務類型）
├── 4 個 Composite Skills 注入（Craft/Lala/Sage/Ori）
├── 10 頁儀表板（含 CEO Console、晨報、夜班）
├── 50+ API endpoints
├── 排程自動化（08:00/20:00/22:00/週一）
├── Review Queue + 決策流程
└── 88 個測試通過

📋 尚未完成
├── LangGraph 多步驟狀態機
├── GEO 技能包（本輪新增）
├── A/B 測試機制
├── 競品價格追蹤
├── 電商數據圖表
└── 雲端部署
```

---

## 二、關於 LangGraph 與現有 DB 的問題

### Q：LangGraph Checkpoint 會不會跟現有 SQLite 衝突？

**答：完全不會衝突，而且會讓系統更強。**

#### 現有 SQLite 表結構
```
articles / topics / posts / drafts
fl_products / fl_performance
audience_insights / ecommerce_selection_*
review_items / agent_events
```

#### LangGraph Checkpoint 新增的表
```
checkpoints          ← 記錄每個任務圖的最新狀態
checkpoint_blobs     ← 儲存 State 物件的二進制快照
checkpoint_writes    ← 記錄每個節點的輸出（可 replay）
checkpoint_migrations ← 版本控制
```

**兩者完全不同名稱，零衝突。** 可以用同一個 SQLite 檔案，或另開一個 `langgraph.db`（建議分開，更清晰）。

#### 升級後的能力對比

| 能力 | 現在 | 加入 LangGraph 後 |
|------|------|-----------------|
| 任務執行 | 呼叫一次函數，跑完就結束 | 多步驟圖，有狀態，可暫停恢復 |
| 失敗處理 | 直接報錯 | 自動 retry，或暫停等人確認 |
| 多 Agent 協作 | CEO 路由到一個 Agent | Ori→Lala→Craft→Sage 自動接力 |
| 中途暫停 | 無法 | 任意節點 `interrupt()` 等你確認 |
| 任務記憶 | 無（API 無狀態） | Checkpoint 存進 DB，可繼續 |
| 除錯 | 看 log | 每個節點的輸入/輸出都可查詢 |

---

## 三、AITOS v2 目標架構（5 層）

### 用戶提供的願景 vs 現有技術棧對應

```
【Layer 1】頂樓：董事長辦公室（前端單一入口）
  願景：極簡 Apple 風格控制台，輸入框 + 狀態燈號 + 簽呈信箱
  現況：Next.js 儀表板（CEO Console 已存在，/review 已存在）
  差距：首頁改版為「以 CEO Console 為核心」的極簡入口

【Layer 2】4F：營運中樞（Orchestrator）
  願景：Node.js + LangGraph.js + node-cron，處理意圖解析/模型路由/流程控制
  現況：Python FastAPI + APScheduler + 現有 orchestrator.py
  ⚠️ 架構決策點（見下方）

【Layer 3】3F：專業員工辦公區（Agent Roster）
  願景：各 Agent 帶 System Prompt + 綁定特定 LLM
  現況：✅ 6 個 Agent 完整定義，Composite Skills 已注入
  差距：幾乎沒有差距，已達標

【Layer 4】2F：重型機具（Execution Engine）
  願景：Claude Code CLI、Figma MCP、Perplexity API
  現況：Claude API ✅、Perplexity Scraper ✅、Figma MCP ❌（待 token）
  差距：Figma MCP 未設定

【Layer 5】1F：檔案室（Workspace & File System）
  願景：.md + .json 非同步交接
  現況：✅ ai/handoff/ + ai/state/ 系統完整運作
  差距：已達標
```

---

## 四、關鍵架構決策：Python LangGraph vs Node.js LangGraph.js

這是 v2 升級最重要的選擇點。

### 選項 A：保留 Python，加入 Python LangGraph（推薦）

```
優點：
- 現有 50+ API endpoints、全部業務邏輯完整保留
- 無需重寫任何後端代碼
- Python langgraph 與 FastAPI 完美整合
- 學習成本低（只新增 langgraph 套件）

做法：
新增 src/agents/pipeline_graph.py（LangGraph 圖）
保留 orchestrator.py（固定 Pipeline 仍可用）
CEO Agent 可選擇觸發「LangGraph 多步驟模式」或「單一任務模式」
```

### 選項 B：新增 Node.js 編排層（未來願景，工作量大）

```
優點：
- 完全符合用戶描述的 5 層架構願景
- LangGraph.js 生態更活躍（JS 社群較大）
- child_process 直接控制 Claude Code CLI

缺點：
- 需要建立 Python ↔ Node.js 通訊橋（HTTP API 或 Redis）
- 現有 50+ Python endpoints 都要遷移或橋接
- 工作量約 3-4 週，風險高

時機：考慮在雲端部署時一起做（重架構時機）
```

### 建議：先做選項 A（3 天），記錄架構決策，雲端部署時再評估 B

---

## 五、執行路線圖（依優先度）

### Phase A：GEO + 動態技能綁定（本週，1-2 天）✅ 已完成一半

**已完成：**
- `_hub/shared/skills/composite/geo_optimization_engine.md` ✅

**待完成：**
- `src/agents/dynamic_orchestrator.py`：加入 GEO_TASKS 自動注入邏輯
- `src/ai/claude_writer.py`：在 draft_generation 任務時自動載入 GEO skill
- CEO Console 的快速指令：加入「GEO 內容」選項

---

### Phase B：LangGraph 多步驟 Pipeline（本月，3-5 天）

**目標：** 讓 CEO 可以觸發多步驟任務鏈

**新增檔案：**
```
src/agents/pipeline_graph.py    ← LangGraph 圖定義
src/agents/graph_state.py       ← TypedDict State 定義
```

**圖定義：**
```python
# 基本內容 Pipeline 圖
State: {
  "topic": str,
  "research_result": dict,
  "strategy": dict,
  "draft": str,
  "score": float,
  "revision_count": int,
  "status": str
}

節點：
  start → ori_research → lala_strategy → craft_write → sage_score
                                                            ↓
                                              score >= 70 → send_to_review
                                              score < 70, count < 2 → craft_write（重寫）
                                              score < 70, count >= 2 → human_review（強制送審）
```

**DB 新增（不影響現有表）：**
```sql
-- langgraph.db（獨立檔案）
-- LangGraph 自動建立以下表：
checkpoints / checkpoint_blobs / checkpoint_writes
```

**API 新增：**
```
POST /api/pipeline/graph          ← 觸發 LangGraph Pipeline
GET  /api/pipeline/graph/{run_id} ← 查詢執行狀態（含每個節點結果）
POST /api/pipeline/graph/{run_id}/resume ← 人工確認後繼續
```

---

### Phase C：CEO 啟動多步驟任務（下月）

**目標：** 你在 CEO Console 說「幫我找個選品主題寫貼文」→ 自動跑完整鏈

**改動：**
- `src/agents/ceo.py`：新增 `MULTI_STEP_TASKS`，觸發 LangGraph 圖而非單一 Agent
- 前端：多步驟任務顯示進度條（每個節點完成一格變亮）

**你的未來工作流：**
```
你（只需要做這些）：
1. 打開 CEO Console
2. 說「幫我分析這個競品，然後選一個主題，寫一篇 Threads 貼文」
3. 等通知（LINE 或 /morning 頁）
4. 在 /review 看結果、點「核准」
5. 自動發出

你不需要：選 Agent、看流程、複製貼上、手動觸發 Pipeline
```

---

### Phase D：持久化 + Night Shift 升級（2-3 個月後）

**目標：** Night Shift 真正意義上的自治推進

**能力：**
- 22:00 Night Shift 開始一個長任務圖
- 如果任務跑到需要人確認，暫停（`interrupt()`）存入 Checkpoint
- 早上你打開 CEO Console，看到「昨晚 Ori 完成了市調，等你確認選題方向」
- 你點確認，任務繼續從 Lala 開始

---

### Phase E：雲端部署 + 架構重新評估（3+ 個月）

**這個時候再決定是否引入 Node.js 編排層**

準備清單：
- [ ] SQLite → Turso（SQLite 雲端版）
- [ ] 後端 → Railway / Render
- [ ] 前端 → Vercel
- [ ] LangGraph DB → 同 Turso 或 Redis
- [ ] 評估 Python FastAPI + LangGraph vs Node.js 重架構

---

## 六、GEO 技能包整合到系統的方式

### 動態技能綁定機制

```python
# src/agents/dynamic_orchestrator.py 修改點

GEO_AUTO_INJECT_TASKS = [
    "draft_generation",   # Craft 寫貼文
    "copywriting",        # Craft 寫文案
    "content_research",   # Craft 相關研究
]

async def run_task(task_type: str, context: dict) -> dict:
    # 自動注入 GEO skill
    if task_type in GEO_AUTO_INJECT_TASKS:
        from src.ai.skill_loader import load_composite_skill
        geo_skill = load_composite_skill("geo_optimization_engine")
        context["geo_skill"] = geo_skill
    ...
```

### 三個使用情境

**情境 1：Threads 貼文（快樂程式鴨）**
CEO 收到「寫一篇關於 AI Agent 狀態持久化的貼文」
→ 自動注入 GEO Engine + 模板 A（技術權威貼文）
→ Craft 產出含技術術語 + GEO Slot + Key Takeaways 的貼文

**情境 2：電商文案（Flow Lab）**
CEO 收到「寫木質香氛機的商品文案」
→ 自動注入 GEO Engine + 模板 B（電商解決方案）
→ Craft 產出含人因工程術語 + Trust Signals 的 GEO 文案

**情境 3：交易複盤**
CEO 收到「複盤今天的 SMC 交易」
→ 自動注入 GEO Engine + 模板 C（SMC 分析）
→ Craft 產出含 ICT 術語 + 可引用的結構化分析

---

## 七、前端入口升級（Layer 1 改版）

### 現況
`/chat` 是 CEO Console，功能完整，但首頁（`/`）是草稿發文頁。

### 目標
首頁改版為「極簡指揮中心」：

```
首頁（/）
├── 頂部：系統狀態（3 個燈號：Pipeline / Night Shift / Review Queue）
├── 中央：CEO Console 輸入框（和 /chat 一樣的對話入口）
├── 右側：今日摘要（晨報關鍵數字）
└── 底部快捷：「查看草稿」「Review Queue (N 件待審)」「昨晚夜班報告」
```

這樣你打開系統的第一個畫面就是「輸入框 + 狀態概覽」，
真正做到「所有事都從對話開始」。

---

## 八、未來理想工作流（完成後）

```
你每天的操作：

早上（5 分鐘）
1. 打開系統 → 看首頁狀態
2. /morning 頁看晨報：「昨晚 Ori 做了市調，Craft 寫了 2 篇草稿，
   Review Queue 有 3 件待審，Flow Lab 有 1 個競品均價下降 12%」
3. 去 /review 點核准 or 修改 → 自動發出

中途（隨時，30 秒）
- 在 CEO Console 說「Flow Lab 的木質香氛機寫一篇 GEO 文案」
- 5 分鐘後收到 LINE：「Craft 完成，待你審核」

晚上（自動）
- 22:00 Night Shift 自動啟動
- 跑 content_research + data_analysis
- 早上看夜班摘要
```

---

## 九、執行決策清單

| 決策 | 選擇 | 原因 |
|------|------|------|
| LangGraph：Python vs JS | Python（Phase B）→ 評估 JS（Phase E）| 現有後端全是 Python，遷移成本高 |
| LangGraph DB：合用 vs 分開 | 分開（langgraph.db）| 避免混淆，方便備份 |
| 首頁改版時機 | Phase C 之後 | 需要 LangGraph 穩定才有意義 |
| Figma MCP | 等 token 到再做 | 依賴外部資源 |
| 雲端部署 | Phase E（3+ 個月）| 等功能穩定後統一搬 |

---

*建立日期：2026-03-17*
*關聯文件：plan_20260315_future_roadmap.md、ai_os_gap_analysis_20260316.md*
*下一步：Phase A — dynamic_orchestrator.py 加入 GEO 自動注入*
