# AITOS Evolution Execution Plan
> 建立日期：2026-03-19
> 依據：README_spec_index_20260318 + 四份核心文件
> 執行者：Claude Code（Lumi 角色）
> 追蹤：每次完成後更新「進度追蹤」區段

---

## 核心決策（不可動搖）

1. **不重寫成 Node.js 編排器** — 保留 FastAPI/Python 控制層
2. **先建工作流骨架** — run/task/event/artifact/approval 五個原語
3. **研究身份與發布身份分離** — scraping 不走主帳號
4. **Flow Lab 核心定位是「決策系統」** — 不只是電商賣貨
5. **品質系統化** — 內容/UI 品質要變成可執行規則，不只靠 prompt

---

## 執行路線圖（8 個 Phase）

### Phase 1 — 穩固工程基礎
**目標**：讓現有系統達到可以繼續加蓋的穩固狀態
**優先度**：必須先做，其他 phase 都依賴這個

| 任務 | 狀態 | 說明 |
|------|------|------|
| 1.1 確認 dashboard build 乾淨 | `[ ]` | 檢查 ecommerce/page.tsx:556 fix 是否有效 |
| 1.2 掃描並修復 encoding 亂碼 | `[ ]` | ai/state/、projects/、src/ 目錄全掃 |
| 1.3 確認 pytest 全 pass | `[ ]` | 88 passed → 應維持或提升 |
| 1.4 記錄架構與程式碼的落差 | `[ ]` | 標記哪些 doc 說的和程式碼不符 |

**優化建議**：
- build 確認後要在 CI 方向考慮加 pre-commit hook，避免回歸
- encoding 掃描可寫成一個腳本 `scripts/check_encoding.py` 供後續定期執行

---

### Phase 2 — 工作流骨架（最關鍵）
**目標**：建立 run/task/event/artifact/approval 五個原語
**說明**：沒有這個，報告、審核、checkpoint/resume 都是空話

#### 2.1 設計 Schema 合約（Pydantic）

```python
# src/workflows/models.py 目標結構

class WorkflowRun:
    id: str           # uuid
    name: str         # e.g. "daily_content_pipeline"
    domain: str       # "media" | "flowlab" | "trading"
    status: str       # "pending" | "running" | "paused" | "completed" | "failed"
    started_at: datetime
    completed_at: datetime | None
    context: dict     # 輸入參數

class WorkflowTask:
    id: str
    run_id: str
    agent: str        # "ori" | "lala" | "craft" | "sage" | "lumi"
    task_type: str
    status: str       # "pending" | "running" | "completed" | "failed" | "awaiting_approval"
    input: dict
    output: dict | None
    error: str | None
    started_at: datetime
    completed_at: datetime | None

class WorkflowEvent:
    id: str
    run_id: str
    task_id: str | None
    event_type: str   # "started" | "completed" | "failed" | "approval_requested" | "resumed"
    payload: dict
    timestamp: datetime

class Artifact:
    id: str
    run_id: str
    task_id: str
    artifact_type: str  # "draft" | "analysis" | "report" | "product_spec" | "screenshot"
    producer: str       # agent name
    file_path: str | None
    db_ref: str | None
    metadata: dict
    created_at: datetime

class ApprovalRequest:
    id: str
    run_id: str
    task_id: str
    action: str       # "publish_post" | "promote_product" | "execute_trade_analysis"
    risk_level: str   # "low" | "medium" | "high"
    evidence: dict    # 給 CEO 看的摘要
    status: str       # "pending" | "approved" | "rejected"
    decided_at: datetime | None
    decision_note: str | None
```

| 任務 | 狀態 | 說明 |
|------|------|------|
| 2.1 建立 src/workflows/models.py | `[ ]` | Pydantic v2 schema |
| 2.2 建立 src/workflows/runner.py | `[ ]` | 執行 run + task 的主控邏輯 |
| 2.3 建立 src/workflows/events.py | `[ ]` | 事件發布 + 訂閱 |
| 2.4 建立 src/workflows/approval.py | `[ ]` | 審核閘門邏輯 |
| 2.5 建立 src/workflows/checkpoint_store.py | `[ ]` | SQLite 持久化 |
| 2.6 DB migration：新增 5 張表 | `[ ]` | workflow_runs, workflow_tasks, workflow_events, artifacts, approval_requests |
| 2.7 基本 API 端點：GET /api/workflows/runs | `[ ]` | 列出最近執行記錄 |
| 2.8 基本 API 端點：GET /api/workflows/runs/{id} | `[ ]` | 單一 run 詳情 + task 樹 |
| 2.9 基本 API 端點：GET /api/approvals/pending | `[ ]` | 待審核清單 |
| 2.10 基本 API 端點：POST /api/approvals/{id}/decide | `[ ]` | 審核決策 |

**優化建議**：
- 用 SQLite JSON1 extension 存 context/evidence 欄位，不要過早正規化
- approval_requests 要有 TTL 概念，避免舊審核堆積
- events 表未來可以直接當 SSE 的 source

---

### Phase 3 — main.py 拆分
**目標**：把超載的 main.py 分成有邊界的 route 模組
**說明**：現在全擠在一個檔案，維護成本高、merge conflict 風險大

| 任務 | 狀態 | 說明 |
|------|------|------|
| 3.1 建立 src/api/routes/ 目錄結構 | `[ ]` | 空目錄 + __init__.py |
| 3.2 抽出 health.py | `[ ]` | /api/health |
| 3.3 抽出 chat.py | `[ ]` | /api/chat |
| 3.4 抽出 content.py | `[ ]` | /api/pipeline、/api/content/* |
| 3.5 抽出 ecommerce.py | `[ ]` | /api/ecommerce/* |
| 3.6 抽出 review.py | `[ ]` | /api/review-queue/* |
| 3.7 抽出 workflows.py | `[ ]` | /api/workflows/*、/api/approvals/* |
| 3.8 main.py 只保留 app 組裝 + 排程 | `[ ]` | include_router 清單 |
| 3.9 確認所有 pytest + build 仍通過 | `[ ]` | 回歸測試 |

**優化建議**：
- 每個 router 用 `APIRouter(prefix="/api/...", tags=["..."])`
- 可以同步替各 router 加 Response 型別標注，提升 OpenAPI 文件品質

---

### Phase 4 — Memory Fabric 正規化
**目標**：每個產出物都有 id/type/producer/path/timestamp/linked-run 元資料

| 任務 | 狀態 | 說明 |
|------|------|------|
| 4.1 現有輸出物清單盤點 | `[x]` | drafts/、reports/、logs/ — 由 artifacts DB 表管理 |
| 4.2 在 Phase 2 的 artifacts 表寫入草稿產出 | `[x]` | claude_writer.py extra_skill param + dynamic_orchestrator record_artifact ✅ |
| 4.3 在 artifacts 表寫入選品報告產出 | `[x]` | selection.py 兩個報告 INSERT 後各加 record_artifact ✅ |
| 4.4 在 artifacts 表寫入週報產出 | `[x]` | weekly_report.py save 後加 record_artifact ✅ |
| 4.5 前端 Artifact Panel | `[ ]` | AI Office 加「產出物」側欄 |

**優化建議**：
- file_path 存相對路徑（相對於 ANTICLAUDE_ROOT），避免 Windows/Linux 路徑問題
- 未來清理舊 artifact 時只需 scan artifacts 表，不用走 filesystem

---

### Phase 5 — 內容智慧升級（Content Intelligence）
**目標**：建立 src/content/ 策略層，讓內容品質系統化而非只靠 prompt

| 任務 | 狀態 | 說明 |
|------|------|------|
| 5.1 GEO 自動注入（dynamic_orchestrator.py） | `[x]` | GEO_AUTO_INJECT_TASKS + run_task 注入 geo_optimization_engine skill ✅ |
| 5.2 建立 src/content/ 目錄 | `[x]` | src/content/__init__.py ✅ |
| 5.3 format_selector.py | `[x]` | short/long/thread 自動選擇 ✅ |
| 5.4 topic_fit.py | `[x]` | 品牌適配 Gate + 封鎖關鍵字 + 加扣分訊號 ✅ |
| 5.5 similarity_guard.py | `[x]` | Jaccard 詞重疊 + 冷卻期過濾 ✅ |
| 5.6 engagement_plan.py | `[x]` | 三時段建議 + first_reply 5分鐘 + 第一小時行動清單 ✅ |
| 5.7 把 content/ 模組接入 claude_writer.py | `[x]` | format_selector + topic_fit 接入，format_block 注入 prompt ✅ |

**優化建議**：
- similarity_guard 可用 sentence-transformers 做語意相似度（而非只比較關鍵字）
- format_selector 應依 Threads 演算法研究結論（threads_algorithm_field_research）驅動

---

### Phase 6 — Flow Lab 視覺工作流
**目標**：CEO 上傳 1688/Taobao 截圖 → AI 自動提取 → 產 Shopee + Threads 草稿
**說明**：這是最快交付真實商業價值、風險最低的 Flow Lab 升級路徑

| 任務 | 狀態 | 說明 |
|------|------|------|
| 6.1 POST /api/flowlab/screenshot-analyze | `[x]` | src/api/routes/flowlab.py ✅ |
| 6.2 screenshot_analyzer.py | `[x]` | Claude Vision 提取 + Shopee + Threads 三合一 ✅ |
| 6.3 Artifact 寫入（raw extraction） | `[x]` | record_artifact type=screenshot_extraction ✅ |
| 6.4 接 Craft 產 Shopee 文案 | `[x]` | SHOPEE_DRAFT_PROMPT + GEO keywords ✅ |
| 6.5 接 Craft 產 Threads 貼文草稿 | `[x]` | THREADS_DRAFT_PROMPT + first_reply seed ✅ |
| 6.6 任務狀態設為 awaiting_approval | `[x]` | approval_request + mark_agent_awaiting_human ✅ |
| 6.7 前端上傳 UI（Flow Lab 頁） | `[ ]` | 拖拉上傳 + 分析進度 + 審核卡片（Phase 7 前端工作）|

**優化建議**：
- 截圖分析支援多張圖（競品比較場景）
- 提取結果以結構化 JSON 存 DB，供後續選品評分使用

---

### Phase 7 — Graph-Capable 工作流
**目標**：支援 checkpoint/resume、審核閘、多 agent 討論
**說明**：基於 Phase 2 的 workflow skeleton，此時加 graph 邏輯才乾淨

| 任務 | 狀態 | 說明 |
|------|------|------|
| 7.1 把每日內容 pipeline 改成 graph-style | `[ ]` | 每個步驟是獨立 node，可 retry |
| 7.2 審核閘：發布前 await approval | `[ ]` | 連接 approval_requests |
| 7.3 CEO Console 加「深度分析」模式 | `[ ]` | Mode C: Deliberation Graph |
| 7.4 前端 workflow timeline UI | `[ ]` | AI Office 顯示 run → task 樹狀圖 |

**優化建議**：
- 不要用 LangGraph 框架（增加依賴複雜度），用純 Python 狀態機實作即可
- graph 只用在有「人類審核中繼點」的工作流

---

### Phase 8 — 外部 Adapter 接入
**目標**：安全連接 X、Figma 等外部系統

| 任務 | 狀態 | 說明 |
|------|------|------|
| 8.1 src/adapters/ 目錄 + 基礎合約 | `[ ]` | 每個 adapter 要有 risk_level、timeout、approval_required |
| 8.2 X 發布 adapter | `[ ]` | 待 X token |
| 8.3 Figma API adapter | `[ ]` | 待 Figma token |
| 8.4 chrome-cdp adapter（監督模式） | `[ ]` | 只限人工觸發 |

---

### Phase 9 — Trading Domain（長期）
**目標**：研究 + 日誌 + 回測，不做即時下單

| 任務 | 狀態 | 說明 |
|------|------|------|
| 9.1 src/trading/ 目錄骨架 | `[ ]` | data_ingest / market_structure / setup_detector / journal / playbook |
| 9.2 Trading Desk 前端頁面 | `[ ]` | /trading |

---

## 進度追蹤（每次執行後更新）

| 日期 | Phase | 完成任務 | 說明 | 下次從這裡繼續 |
|------|-------|---------|------|--------------|
| 2026-03-19 | 建立 | — | aitos_execution_plan_20260319.md 建立 | Phase 1.1 |
| 2026-03-19 | Phase 1 | 1.1 1.2 1.3 1.4 全完成 | build ✅ 16/16、encoding ✅ 0個亂碼、pytest ✅ 88 passed、架構落差已記錄 | Phase 2 |
| 2026-03-19 | Phase 2 | 2.1-2.10 全完成 | models/runner/events/approval/checkpoint_store ✅、5 張 DB 表 ✅、4 個 API 端點 ✅、pytest 100 passed | Phase 3 |
| 2026-03-19 | Phase 3 | 3.1-3.9 全完成 | main.py 1526→164行、7個 route 模組 + state.py、pytest 100 passed | Phase 4 |
| 2026-03-19 | Phase 4 | 4.2 完成 | claude_writer.py extra_skill param ✅、dynamic_orchestrator _handle_draft_generation → record_artifact ✅ | Phase 5 |
| 2026-03-19 | Phase 5 | 5.1-5.5 完成 | GEO auto-inject in run_task ✅、src/content/ 三模組建立 ✅、pytest 117 passed、skills v2.0 升級 ✅ | Phase 5.6-5.7 |
| 2026-03-19 | Phase 4+5+6 | 全面推進 | Phase 4.3-4.4（selection+weekly record_artifact）✅、Phase 5.6 engagement_plan.py ✅、Phase 5.7（format_selector+topic_fit → claude_writer）✅、Phase 6.1-6.6（screenshot_analyzer + flowlab route + DB table）✅、pytest 128 passed | **Phase 4.5 Artifact Panel（前端）、Phase 6.7 截圖上傳 UI** |

### Phase 1 架構落差記錄（1.4）
- `main.py`：**1460 行**，超載嚴重，Phase 3 拆分緊迫
- 不存在的目錄（Phase 2-8 要建的）：`src/workflows/`、`src/content/`、`src/adapters/`、`src/api/routes/`、`src/trading/`
- 所有 Phase 方向與 spec 文件一致，無落差

---

## 優化觀察紀錄（邊做邊補）

### 架構優化
- （執行中發現時補充）

### 效能優化
- （執行中發現時補充）

### 安全建議
- （執行中發現時補充）

---

## 快速參考：下次對話直接繼續

1. 讀這份文件
2. 找「進度追蹤」表最後一行的「下次從這裡繼續」
3. 直接執行，不需重新規劃

---

*文件版本：v1.0 — 2026-03-19*
*下次更新：每完成一個任務後*
