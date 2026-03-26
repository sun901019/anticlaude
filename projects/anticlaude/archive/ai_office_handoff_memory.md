# AI Office 交接與記憶規格

> 目的: 讓 Claude Code、Codex 與其他 agent 對 `AI Office` 的交接流程與記憶層有同一份可讀規格。
> 更新日期: 2026-03-14

## 核心原則

AI Office 不是單純顯示誰在忙。

它要能回答三個問題:
- 這份工作現在在誰手上
- 它是從誰那裡接過來的
- 它完成後要交給誰

## 交接最小資料

每一份任務至少要有:
- `task_id`
- `title`
- `task_type`
- `status`
- `source_agent_id`
- `target_agent_id`
- `started_at`
- `artifact_refs`

## 任務狀態定義

- `idle`: 沒有處理中的任務
- `in_progress`: 正在執行
- `blocked`: 卡住，需要人工或其他 agent 協助
- `done`: 已完成，等待交付或已交付

## 標準交接格式

建議任何 agent 在更新狀態時都盡量補齊以下欄位:

```json
{
  "status": "working",
  "task": "整理今日 AI 新聞訊號",
  "title": "整理今日 AI 新聞訊號",
  "task_type": "research",
  "priority": "normal",
  "source_agent_id": "",
  "target_agent_id": "lala",
  "artifact_refs": [
    "outputs/daily_reports/2026-03-14.json"
  ]
}
```

## 推薦交接鏈

### 內容產線

- `ori` -> 研究與訊號整理
- `lala` -> 選題與策略角度
- `craft` -> 草稿與內容產出
- `pixel` -> 視覺包裝或呈現優化
- `sage` -> 表現回顧與策略調整
- `lumi` -> 工具、流程、自動化支援

### 系統開發線

- `lala` -> 決定要做的產品方向
- `lumi` -> 實作 API / UI / 流程
- `pixel` -> UI 呈現與互動優化
- `sage` -> 效果回顧與數據解釋

## 記憶層

目前的最小記憶層是:

- `outputs/office_memory/agent_events.jsonl`

這份檔案的用途:
- 記錄每次 agent 狀態更新
- 保留 task metadata
- 作為日後 timeline、handoff replay、回顧摘要的基礎

## 重要邊界

這個記憶層目前只是「事件記錄」，還不是「會自動學習的長期記憶」。

也就是說:
- 有記錄
- 但還沒有自動摘要
- 還沒有自動從歷史學到策略
- 還沒有自動把經驗回寫成 agent 知識

如果要讓 agent 真的越來越聰明，後續還要補:
- 事件摘要
- 成敗歸因
- 可檢索記憶
- 定期回顧
- 將回顧寫回 `md` 規格或資料庫

## Claude Code / Codex 協作規則

- 任何涉及 AI Office 新流程的改動，都要同步更新 `projects/anticlaude/` 下的對應 `.md` 文件
- 新增任務型別、交接規則、記憶欄位時，文件先更新，再改程式
- 若畫面、API、文件三者定義不一致，以 `projects/anticlaude/` 的最新規格為準，再回補程式

## 下一步

建議優先順序:

1. 將 `/api/agents/{agent_id}/status` 升級為完整 structured task payload
2. 讓 timeline 可以讀取 `agent_events.jsonl`
3. 新增 `blocked` / `done` 狀態
4. 將真實 pipeline / ecommerce / feedback 事件寫入 AI Office
