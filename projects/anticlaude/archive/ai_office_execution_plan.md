# AI Office 實作規劃

> 目的: 提供一份可直接交給 Claude Code 執行的 AI Office 實作規劃。
> 更新日期: 2026-03-14

## 核心方向

AI Office 不應該只是「角色會動的頁面」。

目標應該是:
- 角色真的有工作
- 任務真的有交接
- 產出真的可追蹤
- 記憶真的可累積
- 畫面上的動態只是工作狀態的外顯

一句話:

**不要做假的活，要做真的有工作所以看起來活。**

## 總體架構原則

延續現有系統，不另起新平台:

- 後端: `FastAPI`
- 即時更新: `SSE`
- 前端: `Next.js`
- 任務來源: `pipeline / feedback / ecommerce / tracker`
- 規格文件: `projects/anticlaude/*.md`

不建議另外重做成獨立的 `Node.js + Socket.io` 系統，除非未來真的要抽成獨立產品。

## 實作目標

AI Office 要同時完成三件事:

1. 狀態可見
- 誰在工作
- 做什麼
- 做到哪裡

2. 流程可追
- 誰派給誰
- 誰接手
- 誰完成
- 誰卡住

3. 產出可驗
- 有沒有真的產出 draft / report / code / 分析
- 使用者能不能從畫面直接打開成果

## Phase 1: 角色狀態系統

### 目標

讓每個 agent 不只是 `idle / working`，而是有完整工作生命週期。

### 建議狀態

- `idle`
- `working`
- `waiting`
- `blocked`
- `done`

### 前端要求

每個角色卡片根據狀態切換視覺:

- `idle`: 靜止
- `working`: 動作感最強
- `waiting`: 輕微呼吸 / 閃爍
- `blocked`: 警示色或警示圖示
- `done`: 完成感狀態

### 驗收

- 畫面上能一眼分辨每個角色目前處於哪一種工作狀態

## Phase 2: 任務與交接模型

### 目標

建立 AI Office 的正式資料模型。

### 建議資料模型

#### AgentTask

- `id`
- `agent_id`
- `title`
- `task_type`
- `status`
- `priority`
- `started_at`
- `updated_at`
- `source_agent_id`
- `target_agent_id`
- `artifact_refs`

#### AgentEvent

- `id`
- `task_id`
- `agent_id`
- `event_type`
- `message`
- `created_at`
- `metadata`

#### AgentHandoff

- `id`
- `task_id`
- `from_agent_id`
- `to_agent_id`
- `status`
- `created_at`
- `accepted_at`

### 建議 event_type

- `task_started`
- `task_updated`
- `handoff_created`
- `handoff_accepted`
- `task_blocked`
- `task_done`

### 驗收

- 任務不是只顯示一行字
- 而是能看出它的上游、下游與目前狀態

## Phase 3: Timeline 產品化

### 目標

把右側活動流做成真正的持久化時間線。

### 要求

- 事件從後端載入，不只靠前端暫存
- 重新整理頁面後仍存在
- 可顯示最近 N 筆
- 能依 agent 或 task 過濾
- 能用 task_id 把同一份工作串成一條線

### UI 至少要顯示

- 時間
- agent
- task title
- task type
- handoff 對象
- 狀態
- artifact 數量

### 驗收

- 使用者能從 timeline 看懂團隊剛剛做了什麼

## Phase 4: 真實工作流接入

### 目標

讓 AI Office 顯示真實 AntiClaude 工作，而不是 demo。

### 接入優先順序

#### 第一條

內容產線:

- `ori` -> `lala` -> `craft`

也就是:

- research
- strategy
- drafting

#### 第二條

展示與回顧:

- `pixel`
- `sage`

#### 第三條

系統支持:

- `lumi`

#### 第四條

其他流程:

- feedback
- tracker
- ecommerce

### 技術原則

優先從總控層接:

- `src/agents/orchestrator.py`

不要直接把狀態邏輯塞進每個底層 AI 模型模組。

### 驗收

- 跑一次真實 pipeline，AI Office 有實際工作流反應

## Phase 5: Artifact 與成果追蹤

### 目標

讓每個 agent 的產出物可以直接被打開。

### 建議 artifact 類型

- draft
- daily report
- weekly report
- office memory summary
- dashboard route
- file path
- DB row identifier

### UI 要求

角色卡片或 timeline 中可以看到:

- 最近產出
- 產出數量
- 可點擊查看

### 驗收

- 使用者從 AI Office 可以直接打開 agent 的成果

## Phase 6: 記憶與學習

### 目標

讓 agent 不只是留 log，而是逐步形成可回顧知識。

### 三層記憶

#### 第 1 層: 原始事件

- `outputs/office_memory/agent_events.jsonl`

用途:

- timeline
- 稽核
- 回放

#### 第 2 層: 每日摘要

建議新增:

- `outputs/office_memory/summary_YYYY-MM-DD.md`

內容:

- 今天完成了哪些任務
- 哪些交接順利
- 哪些任務卡住
- 哪些角色工作量最高

#### 第 3 層: 經驗回寫

建議新增:

- `projects/anticlaude/office_lessons_learned.md`

內容:

- 常見阻塞
- 常見成功交接模式
- 最有效的 artifact 類型
- 哪類 workflow 最不穩

### 驗收

- AI Office 至少能每日產出一份工作摘要

## 交給 Claude Code 的實作順序

建議 Claude Code 按這個順序做:

1. 先穩定啟動與路徑策略
2. 再固定 schema
3. 再做 timeline
4. 再補 handoff 狀態
5. 再補 artifact UI
6. 再接真實 workflow
7. 最後做記憶摘要

## 不建議的做法

- 先追求華麗動畫，但底層沒有真實工作流
- 前後端各自定義一套 task 欄位
- demo handoff 和真實流程完全分離
- 只有 event log，卻宣稱已經有長期記憶

## 驗收標準

### 最低可用版

- `/office` 可正常載入
- agent 狀態有 5 種以上
- timeline 可顯示持久化事件
- demo handoff 可用

### 第一個可信版本

- 真實 pipeline 能觸發 AI Office
- task / handoff / event schema 一致
- artifact 可追

### 第一個有成長性的版本

- 每日摘要存在
- 常見阻塞與經驗能回寫成知識文件

## 總結

AI Office 的正確進化路線不是:

- 先把角色畫得更可愛
- 再加更多動畫

而是:

- 先讓角色真的有任務
- 再讓任務真的會交接
- 再讓交接真的有產出
- 最後讓這些產出形成可累積記憶

這樣它才會從「AI 員工展示頁」進化成「AntiClaude 的活體控制室」。
