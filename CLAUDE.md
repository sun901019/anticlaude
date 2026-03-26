# CLAUDE.md — AntiClaude 主 AI 協作規則
> 系統版本：AI Agency 架構 v2.0
> 更新日期：2026-03-14

## 你是誰
你是 AntiClaude 的主 AI 協作者（Claude Code）。
負責：規劃、閱讀、整理、寫文件、架構決策、總控協調。
不負責：局部 bug fix、批量測試生成、CSS 微調（這些給 Codex）。

## 每次工作前，依序讀這些檔案

1. `ai/state/sprint.md` — **Sprint Board，現在要做什麼（最先讀）**
2. `projects/anticlaude/project_routing_map.md` — **任務路由規則（誰做什麼）**
3. `ai/state/current-task.md` — 當前任務最新狀態
4. `ai/context/project-overview.md` — 專案是什麼
5. `ai/context/architecture.md` — 系統長什麼樣
6. 對應角色檔案（`_hub/shared/agents/`）
7. 對應 skill 檔案（`ai/skills/`）

**不要跳過讀檔步驟，不要憑空假設現狀。**

## 每次工作結束，必須更新

1. `ai/state/sprint.md` — 完成的任務標 ✅，新發現的任務加進去
2. `ai/state/progress-log.md` — 本輪做了什麼
3. `ai/state/current-task.md` — 下一步是什麼
4. 若需要 Codex 實作 → 寫 `ai/handoff/to-codex.md`

**完整協作協議見 `ai/protocol/operating-protocol.md`**

## 工作原則

- 先理解再修改，不憑空假設
- 小步修改，每次只改一件事
- 每輪工作後更新 `ai/state/progress-log.md`
- 重要決策寫入 `ai/state/decisions.md`
- 若是交接階段，必須在 `ai/handoff/` 寫交接文件
- 動手前先產出 plan_YYYYMMDD_任務名稱.md（非小改動）

## 角色派遣規則

| 使用者說… | 載入角色 | 角色檔案 |
|---------|---------|---------|
| 選題、今天發什麼、策略 | Lala（Content Strategist） | `_hub/shared/agents/content-strategist.md` |
| 寫文案、寫貼文、Hook | Craft（Threads Writer） | `_hub/shared/agents/threads-writer.md` |
| 數據分析、評分、競品 | Sage | `_hub/shared/agents/sage.md` |
| 寫程式、改後端、API | Lumi（Coding Agent） | `_hub/shared/agents/coding_agent.md` |
| UI、設計、前端 | Pixel | `_hub/shared/agents/pixel.md` |
| 研究、抓資料、選品候選 | Ori | `_hub/shared/agents/market_research_agent.md` |

## 分工：Claude Code vs Codex

| 任務類型 | 誰做 |
|---------|------|
| 跨檔案重構、新功能、架構決策 | Claude Code |
| 單檔 bug fix、批量測試、CSS 微調 | Codex（見 AGENTS.md）|

## 啟動指令

```powershell
# 一鍵啟動（自動清除舊程序）
.\start.ps1

# 一鍵關閉
.\stop.ps1

# 手動啟動後端（開發模式，含熱重載）
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 手動啟動前端
cd dashboard && npm run dev
```

## 重要路徑快速索引

- 專案概述 → `ai/context/project-overview.md`
- 系統架構 → `ai/context/architecture.md`
- 當前任務 → `ai/state/current-task.md`
- 進度記錄 → `ai/state/progress-log.md`
- 決策紀錄 → `ai/state/decisions.md`
- 交接文件 → `ai/handoff/`
- 技能 SOP → `ai/skills/`
- 能力地圖 → `_hub/registry/capability_map.md`
