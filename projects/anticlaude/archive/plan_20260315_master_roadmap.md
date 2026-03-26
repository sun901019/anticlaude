# AntiClaude — 主路線圖（Master Roadmap）
> 作者：Claude Code
> 日期：2026-03-15
> 狀態：每次完成升級後在此更新 ✅

---

## 系統現況

```
已完成
├── AI Agency 6 層框架（CLAUDE.md v2.0）        ✅
├── 6 個 Agent 資訊隔離規則                     ✅
├── ai/ 目錄結構（context / state / handoff / skills）  ✅
├── awaiting_human 狀態（agent_status.py）      ✅
├── AI Office 決策卡片（橘色 UI + 按鈕）         ✅
├── Flow Lab Dashboard 5 tabs                  ✅
├── 事件驅動 Agent 啟動（orchestrator.py）       ✅
├── 測試套件 49/50（1 個過時斷言待修）            ✅
├── 每日摘要自動產出                             ✅
├── Ori 真正搜競品（competitor_analyzer.py）    ✅ Phase 3A
├── Sage 自動評分（sage_scorer.py）             ✅ Phase 3A
├── Craft 自動產報告（craft_reporter.py）       ✅ Phase 3A
├── POST /auto-analyze/{id} 串接全流程          ✅ Phase 3A
└── 全 API 確認正常（6/6 PASS）                 ✅

待執行
├── Fix-1：test_serper.py 過時斷言                      ✅ 完成
├── Phase 3B：升級 D / E / F                           ✅ 完成
├── Phase 3C：升級 G（LINE Notify）                    ✅ 完成（需 LINE_NOTIFY_TOKEN）
├── Phase 3C：升級 H（雲端部署）                        ⏸ 用戶決定跳過
└── 技術債（start.ps1 / stop.ps1 / CLAUDE.md）         ✅ 完成
```

---

## Fix-1：修正 test_serper.py 過時斷言

**負責**：Codex（單檔修改，5 分鐘）
**檔案**：`tests/test_serper.py` 第 22 行

```python
# 改前
assert len(results) == 4  # 2 queries × 2 results

# 改後
assert len(results) > 0  # query 數量可能變動，只確認有結果
```

**原因**：Serper 現在跑 5 個 query，舊測試寫死 2 query × 2 = 4。

---

## Phase 3B — 閉環智能化

> 前提：Phase 3A 已完成 ✅

### 升級 D：Threads 數據自動排程

**目標**：每天固定時間自動抓 Threads 數據，不需人工介入。

**實作位置**：`src/pipeline.py` 或新建 `src/scheduler.py`

**實作方式**：
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(run_threads_tracker, "cron", hour=2, minute=0)   # 每天凌晨 2 點
scheduler.add_job(run_daily_pipeline, "cron", hour=7, minute=0)    # 每天早上 7 點

scheduler.start()
```

**注意**：
- Windows 環境下 APScheduler 需用 `AsyncIOScheduler`，避免 `BlockingScheduler` 阻塞
- `uvicorn` startup event 中啟動 scheduler（`app.add_event_handler("startup", ...)`）
- 測試方式：改成 1 分鐘後觸發，驗證後改回正式時間

**完成標準**：
- [ ] scheduler 在 uvicorn 啟動時自動啟動
- [ ] 每天凌晨 2 點觸發 `run_threads_tracker`
- [ ] 每天早上 7 點觸發 `run_daily_pipeline`
- [ ] AI Office 顯示排程觸發事件

---

### 升級 E：Threads 數據影響選題

**目標**：Lala 選題時自動讀取近期高互動模式，注入 prompt。

**實作位置**：`src/agents/strategy.py`（Lala 的策略 agent）

**新增邏輯**：
```python
# 在 StrategyAgent 組裝 prompt 前加入
from src.db.queries import get_top_performing_topics
insights = get_top_performing_topics(days=14, top_n=5)

if insights:
    insight_text = "\n".join([
        f"- {i['topic_type']}：平均互動率 {i['avg_engagement']}%"
        for i in insights
    ])
    prompt += f"\n\n近期高互動主題模式（請優先選擇類似方向）：\n{insight_text}"
```

**需要確認**：
- `src/db/queries.py` 是否有 `get_top_performing_topics()` 函數（若無則新建）
- `audience_insights` 表欄位確認（topic_type / avg_engagement / recorded_at）

**完成標準**：
- [ ] `get_top_performing_topics(days, top_n)` 函數可用
- [ ] Lala 選題時 prompt 自動帶入近 14 天高互動主題
- [ ] 沒有 insights 時優雅降級（空清單不報錯）

---

### 升級 F：選品決策自動學習

**目標**：累積 10 條 lesson 後，Sage 自動整合成「選品規則更新」，影響 Ori 下次搜尋。

**實作位置**：`src/ecommerce/selection.py`，`_auto_lesson_on_decision` 函數末尾

**新增觸發邏輯**：
```python
lesson_count = conn.execute(
    "SELECT COUNT(*) FROM ecommerce_selection_lessons"
).fetchone()[0]

if lesson_count > 0 and lesson_count % 10 == 0:
    _trigger_sage_rule_synthesis(lesson_count)
```

**新建函數 `_trigger_sage_rule_synthesis()`**：
1. 讀取所有 lesson（`ecommerce_selection_lessons` 表）
2. 用 Claude Sonnet 整合成 3-5 條選品規則
3. 寫入 `ai/context/flowlab-selection-rules.md`
4. Ori 下次分析時讀取此檔作為 context

**Claude Prompt 骨架**：
```
你是 Flow Lab 選品策略師（Sage）。
以下是過去 {n} 筆選品決策的經驗教訓：
{lessons}

請整合成 3-5 條具體的選品規則（格式：規則 / 適用情境 / 成功條件）。
輸出格式：Markdown，適合注入 Ori 的 research prompt。
```

**完成標準**：
- [ ] `_trigger_sage_rule_synthesis()` 函數建立
- [ ] 每累積 10 筆 lesson 自動觸發一次
- [ ] 規則寫入 `ai/context/flowlab-selection-rules.md`
- [ ] `competitor_analyzer.py` 在搜尋前讀取此規則檔（若存在）

---

## Phase 3C — 對外擴展

> 前提：Phase 3B 穩定運行後再做

### 升級 G：LINE 通知系統

**目標**：重要事件主動推播，不用一直盯 dashboard。

**觸發條件**：
- 文案草稿完成（Craft awaiting_human select_draft）
- 選品報告完成（Craft awaiting_human approve_purchase）
- 週報已生成
- Pipeline 跑失敗（Exception 觸發）

**實作位置**：`src/utils/notify.py`（新建）

```python
# src/utils/notify.py
import os
import httpx

async def send_line_notify(message: str) -> None:
    token = os.getenv("LINE_NOTIFY_TOKEN")
    if not token:
        return  # 沒設定 token 就靜默跳過
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {token}"},
            data={"message": message},
        )
```

**接入點**：
- `src/api/agent_status.py` → `mark_agent_awaiting_human()` 末尾呼叫
- `src/agents/orchestrator.py` → pipeline 失敗 except 區塊

**環境變數**：`.env` 加入 `LINE_NOTIFY_TOKEN=xxx`

**完成標準**：
- [ ] `src/utils/notify.py` 建立
- [ ] awaiting_human 觸發時發送 LINE 通知
- [ ] 沒有 LINE_NOTIFY_TOKEN 時靜默跳過（不報錯）

---

### 升級 H：雲端部署

**目標**：24/7 自動運行，手機也能看 dashboard。

**建議方案**：

| 元件 | 平台 | 費用 |
|------|------|------|
| 後端 FastAPI | Railway 或 Render | 免費方案可用 |
| 前端 Next.js | Vercel | 免費 |
| 資料庫 SQLite | Turso（SQLite 雲端版） | 免費方案可用 |
| n8n | Railway 自架 | 自架免費 |

**部署前檢查清單**：
- [ ] 所有 `localhost:8000` hardcode 改為環境變數 `NEXT_PUBLIC_API_BASE`
- [ ] `.env.example` 建立（不含真實 key）
- [ ] `requirements.txt` 確認完整
- [ ] SQLite → Turso 遷移腳本
- [ ] next.config.js rewrite rule 確認（SSE 路由）
- [ ] `flowlab-selection/` 舊目錄加 `DEPRECATED.md`

---

## 技術債清理（隨時可做）

| 項目 | 說明 | 優先 |
|------|------|------|
| google.genai 遷移 | `google.generativeai` 已廢棄，遷移到 `google.genai` | 低（目前正常） |
| flowlab-selection/ 廢棄標記 | 加 DEPRECATED.md | 低 |
| API 路徑統一 | 前端混用 relative / absolute | 中（部署前必做）|
| ai_office_vision.md 同步 | 標記已完成項目 | 低 |

---

## 執行優先順序

```
立即（Codex，5 分鐘）
└── Fix-1：test_serper.py 斷言修正

Phase 3B（本週）
├── 升級 D：Threads 自動排程
├── 升級 E：Threads 數據 → 選題
└── 升級 F：選品決策 → 學習規則

Phase 3C（下週）
├── 升級 G：LINE 通知
└── 升級 H：雲端部署（含技術債清理）
```

---

## 給 Claude Code 的執行備註

1. 每完成一個升級，在本文件對應的 `完成標準` 打 `[x]`
2. 同步更新 `ai/state/progress-log.md`（本輪做了什麼）
3. 同步更新 `ai/state/current-task.md`（現在在哪個任務）
4. 升級 D（排程）測試時先用 1 分鐘觸發驗證，確認後改回正式時間
5. 升級 F 完成後，確認 `competitor_analyzer.py` 有讀取 `flowlab-selection-rules.md`
6. Phase 3C 前，先完成「API 路徑統一」技術債
