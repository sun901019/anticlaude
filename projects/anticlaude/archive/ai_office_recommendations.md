# AI Office 優化方案與進化方向

> 目的: 提供一份完整、可執行、可交付給 Claude Code 的 AI Office 優化方案。
> 更新日期: 2026-03-14
> 使用方式: 本文件可作為後續修正、擴充、重構與驗收的決策基準。

---

## 一、總目標

AI Office 的目標不是做一個「會動的 agent 頁面」。

真正要做的是:

- 讓 AntiClaude 的多 agent 協作可視化
- 讓任務交接有明確結構
- 讓產出物可追蹤
- 讓歷史工作可回放
- 讓 agent 有可累積的記憶基礎
- 讓人類使用者像在管理一個 AI 團隊，而不是在看 log

一句話總結:

**AI Office 要從「展示介面」進化成「AI 團隊操作系統的控制室」。**

---

## 二、目前狀態判斷

目前已經有的基礎:

- agent 卡片頁面
- 即時狀態流概念
- 結構化 task metadata 雛形
- 事件記錄雛形
- demo handoff 能力
- 真實 pipeline 接入方向已經明確
- 文件層已有 vision / handoff / remaining work / review

目前主要問題:

- 啟動方式不穩，導致常常不知道是程式壞還是服務沒起來
- 前端與後端路徑策略不完全一致
- 規格文件與實作有些不同步
- timeline 只有「事件存在」，還不是產品層的「持久化工作時間線」
- 記憶只有 log，還沒有摘要、回顧、學習
- handoff 雖有欄位，還沒有完整生命週期

---

## 三、整體優化方向

建議把 AI Office 的優化拆成 6 條主線，同步推進但有優先順序。

### 主線 A: 啟動與運行穩定性

先解決「最新版根本沒跑起來」的問題。

### 主線 B: 資料契約正式化

讓 agent / task / event / handoff 成為正式資料模型，而不是零散欄位。

### 主線 C: Timeline 產品化

讓活動流從「前端事件列表」進化成「可回放、可篩選、可追蹤」的持久化時間線。

### 主線 D: 真實工作流接入

讓 AI Office 顯示真實流程，而不是只顯示手動或示範資料。

### 主線 E: Artifact 與可操作性

讓每個 agent 的工作成果真的能打開、查看、追溯。

### 主線 F: 記憶與學習層

讓 agent 不只是留下紀錄，而是能形成回顧、摘要與可重用經驗。

---

## 四、優先順序建議

建議開發順序:

1. 先穩定啟動與運行
2. 再固定 AI Office 資料契約
3. 再完成持久化 timeline
4. 再補 handoff 生命週期
5. 再補 artifact 可點擊與輸出追蹤
6. 再把真實 workflow 全面接入
7. 最後再做記憶摘要與學習層

原因:

- 如果服務啟不穩，再好的 UI 和 schema 都會看起來像壞掉
- 如果資料契約不固定，後面 timeline / memory / artifact 都會反覆推倒重來

---

## 五、具體方案

## 方案 1: 啟動穩定方案

### 目標

讓任何人都能穩定啟動 AI Office 的前後端，不再因執行方式不同而誤判系統狀態。

### 建議做法

建立一份專門文件:

- `projects/anticlaude/ai_office_runtime.md`

文件內容至少要有:

- 前端啟動命令
- 後端啟動命令
- 哪些命令在這台環境不要用
- 啟動後的驗證 URL
- 常見錯誤與排查方式

### 建議內容

前端:

```powershell
cd C:\Users\sun90\Anticlaude\dashboard
npm.cmd run dev
```

後端:

```powershell
cd C:\Users\sun90\Anticlaude
python -m uvicorn src.api.main:app --port 8000
```

### 不建議

- 在目前環境使用 `uvicorn ... --reload`
- 在目前 PowerShell 環境直接用 `npm run dev`

### 驗收條件

以下都要可回應:

- `/office`
- `/api/agents/status`
- `/api/agents/stream`
- `/api/agents/events`
- `/api/agents/demo-handoff`

---

## 方案 2: AI Office 資料契約正式化

### 目標

讓所有 agent 狀態、handoff、事件和時間線都建立在同一份明確 schema 上。

### 建議模型

#### AgentTask

```json
{
  "id": "task_001",
  "agent_id": "ori",
  "title": "整理今日 AI 訊號",
  "task_type": "research",
  "status": "in_progress",
  "priority": "high",
  "started_at": "2026-03-14T09:00:00",
  "updated_at": "2026-03-14T09:02:00",
  "source_agent_id": "",
  "target_agent_id": "lala",
  "artifact_refs": [
    "outputs/office_memory/demo_research_packet.md"
  ]
}
```

#### AgentEvent

```json
{
  "id": "event_001",
  "task_id": "task_001",
  "agent_id": "ori",
  "event_type": "task_started",
  "message": "整理今日 AI 訊號",
  "created_at": "2026-03-14T09:02:00",
  "metadata": {
    "target_agent_id": "lala",
    "artifact_refs": []
  }
}
```

#### AgentHandoff

```json
{
  "id": "handoff_001",
  "task_id": "task_001",
  "from_agent_id": "ori",
  "to_agent_id": "lala",
  "status": "pending",
  "created_at": "2026-03-14T09:05:00",
  "accepted_at": ""
}
```

### 狀態列舉建議

Agent / Task 狀態建議固定成:

- `idle`
- `in_progress`
- `blocked`
- `handoff_pending`
- `done`

Handoff 狀態建議:

- `pending`
- `accepted`
- `rejected`
- `completed`

### 驗收條件

- 文件、API、UI 三邊使用同一組欄位
- 新增 agent 或 workflow 時不用再猜欄位名稱

---

## 方案 3: Timeline 產品化方案

### 目標

讓 AI Office 右側活動流變成真正可回放、可篩選、可追蹤的時間線。

### 現況問題

- 事件雖然有寫進 `agent_events.jsonl`
- 但 UI 目前還比較像「事件流」
- 還不是「工作歷史系統」

### 建議能力

至少支援:

- 重新整理頁面後保留近期事件
- 顯示真實事件數量
- 依 agent 篩選
- 依 task 篩選
- 依 task_id 分組
- 顯示前一步 / 當前 / 下一步
- 顯示狀態轉換

### API 建議

`GET /api/agents/events`

建議回傳:

```json
{
  "events": [],
  "count": 12,
  "limit": 50
}
```

不要再用:

- `count = limit`

### UI 建議

右側 timeline 每筆至少顯示:

- 時間
- agent 名稱
- task title
- task type
- handoff 對象
- 狀態
- artifact 數量

### 驗收條件

- 關掉頁面重開後仍可看到近期事件
- 能分辨同一份 task 的不同事件

---

## 方案 4: Handoff 生命週期方案

### 目標

讓 AI Office 真正表現出「交接」，而不是只是顯示下一棒欄位。

### 現況問題

目前有:

- `source_agent_id`
- `target_agent_id`

但還缺:

- 已經交出了沒
- 對方接了沒
- 卡住在哪
- 完成了沒

### 建議流程

以內容產線為例:

1. `ori` 建立 task
2. `ori` 完成研究，handoff -> `lala`
3. `lala` 接受 handoff
4. `lala` 完成策略，handoff -> `craft`
5. `craft` 接受並產出 draft
6. `pixel` 接視覺
7. `sage` 做回顧

### 建議 UI 顯示

task card / timeline 顯示:

- 建立
- 進行中
- 待交接
- 已接收
- 已完成
- 已阻塞

### 驗收條件

- 任務不只知道「下一棒是誰」
- 還知道「下一棒到底接了沒有」

---

## 方案 5: Artifact 與產出追蹤方案

### 目標

讓每個 agent 的工作結果都可打開、查看、驗證。

### 建議 artifact 類型

- daily report JSON
- daily report Markdown
- draft Markdown
- weekly report
- office memory summary
- dashboard route
- file path
- DB record id

### UI 建議

在 agent 卡片或 timeline 中新增:

- `產出`
- `打開`
- `查看草稿`
- `查看報告`

### 驗收條件

- 任一 task 若完成，至少有一個可追的 artifact
- 使用者可以直接從 AI Office 進入該成果

---

## 方案 6: 真實 workflow 接入方案

### 目標

讓 AI Office 反映 AntiClaude 真正工作，而不是 demo。

### 優先接入順序

#### 第一優先

內容主流程:

- `ori`
- `lala`
- `craft`

也就是:

- research
- strategy
- drafting

#### 第二優先

展示與回顧:

- `pixel`
- `sage`

#### 第三優先

工程與系統支持:

- `lumi`

#### 第四優先

其他系統:

- feedback
- tracker
- ecommerce

### 技術建議

最適合的接入點:

- `src/agents/orchestrator.py`

原因:

- 這裡是總控層
- 不用污染底層 AI 模型模組
- 可以在同一個地方發出 workflow 狀態

### 驗收條件

- 跑一次真實 pipeline 時，AI Office 能看到實際任務流
- 不需要手動點 demo 才有內容

---

## 方案 7: 記憶與學習層方案

### 目標

讓 agent 從「留下 log」進化成「留下可學習的工作記憶」。

### 重要原則

**event log != 長期記憶**

要讓 agent 真的越來越聰明，至少需要三層:

#### 第 1 層: 原始事件

例如:

- `agent_events.jsonl`

用途:

- 回放
- 稽核
- timeline

#### 第 2 層: 每日摘要

例如:

- `outputs/office_memory/summary_2026-03-14.md`

內容:

- 今天哪些任務完成
- 哪些 handoff 順利
- 哪些任務卡住
- 哪些 agent 負擔最高

#### 第 3 層: 可回寫知識

例如:

- `projects/anticlaude/office_lessons_learned.md`

內容:

- 常見阻塞
- 最有效交接模式
- 哪類 task 常失敗
- 哪類 artifact 最有用

### 建議先做的最小版本

先不要追求「會自己學」。

先做:

1. 事件寫入
2. 每日摘要
3. 回顧文件

這樣就已經比純 log 強很多。

### 驗收條件

- 每天至少可產出一份 AI Office 工作摘要
- 使用者能從摘要看出團隊工作品質

---

## 六、建議新增文件

如果要把這套系統做紮實，建議新增或維護以下文件:

- `ai_office_runtime.md`
- `ai_office_schema.md`
- `ai_office_workflow_map.md`
- `ai_office_memory_strategy.md`
- `office_lessons_learned.md`

目前已存在且應持續同步:

- `ai_office_vision.md`
- `ai_office_handoff_memory.md`
- `ai_office_remaining_work.md`
- `ai_office_review_2026-03-14.md`
- `codex_agent_spec.md`

---

## 七、驗收清單

### 第一階段驗收

- `/office` 可正常載入
- `/api/agents/status` 可回傳
- `/api/agents/stream` 可連線
- `/api/agents/events` 可回傳真實事件
- `/api/agents/demo-handoff` 可成功觸發

### 第二階段驗收

- timeline 重整後仍保留近期事件
- 每個 task 可看到來源與下一棒
- `blocked / done / handoff_pending` 有實際顯示

### 第三階段驗收

- 真實 pipeline 會驅動 AI Office
- artifact 可點擊
- 每日記憶摘要可自動或半自動產出

---

## 八、給 Claude Code 的實作建議

如果 Claude Code 要接手，建議順序:

1. 不要先追視覺
- 先把啟動穩定、API 契約、timeline 基礎打穩

2. 文件先行
- 每次改 schema / workflow / memory，都要先更新 `projects/anticlaude/` 下的 `.md`

3. 不要讓 demo 和真實流程分家
- demo 可以保留，但真實 workflow 才是主路線

4. 避免前後端各自定義欄位
- API schema 要成為唯一來源

5. 把「能看」和「可信」分開驗收
- 一個畫面會動，不代表它可信
- AI Office 的驗收應該重視真實 workflow 映射與 artifact 可追溯

---

## 九、總結

AI Office 最值得做的，不是把畫面做得更像控制台，而是把它做成真正可信的協作系統。

真正有價值的方向是:

- 啟動穩定
- 契約明確
- timeline 可回放
- handoff 可追蹤
- artifact 可打開
- workflow 反映真實工作
- 記憶能累積成知識

如果這些都做好，AI Office 才會從「有趣的 agent 介面」變成「AntiClaude 的操作核心」。
