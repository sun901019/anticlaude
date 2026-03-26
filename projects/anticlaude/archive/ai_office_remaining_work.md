# AI Office 待辦與後續規劃

> 目的: 記錄目前 AI Office 尚未完成的工作、建議優先順序、觸發條件與風險。
> 狀態: 持續更新中
> 更新日期: 2026-03-14（plan_20260314_optimization_roadmap 執行後）

## 目前已完成到哪（截至 2026-03-14）

✅ 已完成項目:
- AI Office 頁面（`/office`）6 個 agent 卡片 + SSE 燈號
- agent 結構化 task state（task_id / task_type / priority / source/target / artifact_refs）
- agent 事件記錄到 `outputs/office_memory/agent_events.jsonl`
- 持久化 Timeline（SSE 直連 8000，`NEXT_PUBLIC_API_BASE` 環境變數）
- Handoff 生命週期：`blocked` / `done` / `handoff_pending` helpers（`agent_status.py`）
- Artifact 可點擊：`artifactLink()` helper，路徑 → dashboard 路由
- 真實 Workflow 接入：orchestrator / tracker / feedback 全程 emit
- 每日記憶摘要：`src/office/daily_summary.py`，orchestrator 末尾觸發
- 一鍵啟動：`start.ps1`（Port 衝突偵測 + 後端 + 前端 + 健康確認）
- Lala 高互動主題模式注入：`memory.py` 讀取近 3 期 audience_insights
- Flow Lab 選品學習回路：approved/rejected → Sage auto-lesson，10 條觸發整合提醒

## 目前還沒完成的事

### 1. Threads 受眾數據 → Lala 選題（進階）

現況:
- 基礎注入已完成（strategy_section + 高互動主題模式）
- 但還沒有依受眾分群（年齡/職業/興趣）做差異化選題建議

待做（可選）:
- `audience_insights` 加入分群欄位
- Lala prompt 加入「哪個受眾群最在乎這個主題」維度

### 2. Flow Lab 選品 → Lala 選題整合

現況:
- 選品引擎已完整（5 個 Tab）
- 但 Flow Lab 商品動態（哪個品上架、哪個品在測試）還未注入選題策略

待做（可選）:
- Sage auto-lesson 整合後，將規則注入 Lala content-strategist prompt

### 3. Timeline agent 篩選 UI

現況:
- Timeline 顯示全部事件
- 缺少按 agent 篩選的 chips

待做:
- 前端 Timeline 上方加篩選 chips（Ori/Lala/Craft/全部）
- API 支援 `?agent_id=` 參數（已在 roadmap 但未實作）

## 建議優先順序（下一期）

1. Timeline agent 篩選（低風險、高可見度）
2. Threads 分群選題（需 DB 擴充）
3. Flow Lab 規則 → Lala 整合（待 lesson 累積足夠後）

## 觸發條件設計

### AI Office 什麼時候應該顯示任務

應顯示的條件:
- agent API 被呼叫
- pipeline 開始某個步驟
- 任務轉交到下一個 agent
- 任務完成
- 任務被阻塞

### AI Office 什麼時候應該寫入記憶

應寫入的條件:
- 新任務建立
- 任務狀態改變
- handoff 發生
- artifact 產生
- 任務完成

### 不應亂寫入的情況

不應寫入:
- UI 單純刷新
- 無意義的 polling
- 沒有真正任務變化的重複更新

## 風險

### 1. UI 看起來很完整，但底層流程不一致

如果畫面做太快，卻沒有真的接進 pipeline，AI Office 會變成漂亮但不可信的控制台。

### 2. 記憶只有堆 log，沒有轉成知識

只存 JSONL 不等於 agent 會變聰明。

真正的「越來越聰明」需要:
- 摘要
- 回顧
- 策略回寫
- 可檢索知識

### 3. 多 agent 定義與主程式漂移

如果 `_hub`、`projects/anticlaude/`、`src/` 三邊規格不同步，後面很容易失真。

## 文件同步原則

之後如果要繼續做 AI Office:
- 先更新 `projects/anticlaude/` 下的規格文件
- 再改 API
- 再改前端

至少要同步維護這幾份:
- `ai_office_vision.md`
- `ai_office_handoff_memory.md`
- `ai_office_remaining_work.md`
- `codex_agent_spec.md`

## 建議優先順序

如果之後恢復開發，建議順序:

1. 先修啟動與服務穩定性
2. 再完成持久化 timeline
3. 再補 handoff 狀態
4. 再補 artifact UI
5. 最後全面接真實 workflow 與記憶回顧
