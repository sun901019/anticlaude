# Changelog — Phase 4：Agent 充實 + Codex 整合 + 架構治理

> 記錄 Antigravity 在 Phase 4 規劃的異動，以及 Claude Code 執行結果。
> **執行日期**：2026-03-13

---

## 異動摘要

### Component 1: 5 個骨架 Agent 充實化 ✅

| Agent 檔案 | 異動內容 | 狀態 |
|-----------|---------|------|
| `market_research_agent.md` | 加入角色定義、5維度評估、台灣角度萃取、輸出格式、Prompt範本；Skills 更新為 `strategy_guide` | ✅ 完成 |
| `marketing_strategy_agent.md` | 加入週選題規劃完整流程、audience_insights 互動邏輯、多樣性規則；Skills 更新為 `strategy_guide` | ✅ 完成 |
| `content_agent.md` | 加入格式判斷邏輯、Threads/投影片/文件 3 種工作流、去AI痕跡後處理；Skills 更新為 `writing_guide` + `dev_tools` | ✅ 完成 |
| `planning_agent.md` | 加入 5問澄清流程、WBS模板、claude_code_*.md 生成格式、AntiClaude 專案WBS模板 | ✅ 完成 |
| `coding_agent.md` | 加入 Claude Code vs Codex 任務路由、AntiClaude 技術規範（FastAPI/Next.js/SQLite）、常用程式碼片段 | ✅ 完成 |

---

### Component 2: Codex 執行引擎整合 ✅

| 檔案 | 異動內容 | 狀態 |
|------|---------|------|
| `CLAUDE.md` | 新增「執行引擎選擇規則」段落（8項任務 vs 引擎對照表）；修正 TopNav 路徑（Sidebar → TopNav） | ✅ 完成 |
| `_hub/shared/tools/codex_integration.md` | 新建：Codex 角色定義、使用時機、Claude Code 分工邊界、任務標注規範 | ✅ 新建 |

---

### Component 3: Registry 更新 ✅

| Registry 檔案 | 異動內容 | 狀態 |
|-------------|---------|------|
| `agents_registry.md` | 更新所有 Agent 使用的 Skills 為合併後名稱；新增 7 個 Agent 的完整狀態表；新增 Agent 選用指南 | ✅ 完成 |
| `capability_map.md` | 新增「執行工具層（更新版）」表格；加入 Claude Code vs Codex 決策樹 | ✅ 完成 |
| `tools_registry.md` | 新增 Codex 為第三個執行工具；更新 Tool 使用規則 | ✅ 完成 |
| `skills_registry.md` | 在 Phase 3 已由 Claude Code 更新（9→6 個 Skills） | ✅ 已是最新 |

---

### Component 4: 一致性修正 ✅

| 項目 | 異動 | 狀態 |
|------|------|------|
| CLAUDE.md 上下文載入表 | `Sidebar.tsx` → `TopNav.tsx`（配合 UI 重構） | ✅ 修正 |
| 5 個 Agent YAML header | `skills` 欄位更新為合併後的 skill 名稱 | ✅ 完成 |

---

## 架構一致性驗證

### Skill 引用驗證
```
CLAUDE.md 路由表 → 對應 capability_map.md ✅
agents_registry.md Skills 欄位 → 對應實際 agent YAML header ✅
Agent YAML header skills → 檔案確實存在於 _hub/shared/skills/ ✅
```

### 現有 Skills（合併後，共 6 個）
```
_hub/shared/skills/writing_guide.md      ← threads-writer, content-agent 使用
_hub/shared/skills/strategy_guide.md     ← content-strategist, market-research-agent, marketing-strategy-agent 使用
_hub/shared/skills/dev_tools.md          ← content-agent, agency-agents 使用
_hub/shared/skills/seo_optimization.md   ← market-research-agent 使用
_hub/shared/skills/project_planning.md   ← planning-agent 使用
_hub/shared/skills/coding_agent.md       ← coding-agent 使用
```

---

## 功能驗證範例

模擬任務：「幫我分析今天有什麼 AI 新聞值得發」

```
路由偵測：「分析」「AI 新聞」「值得」→ 選題/分析類
↓
派遣：content-strategist + market-research-agent
↓
Skill 載入：strategy_guide（5維度評估 + 選題多樣性規則）
↓
上下文：about_me.md（@sunlee._.yabg 受眾定義）
↓
輸出：今日推薦素材 3-5 則 + 台灣切角 + 建議主題類型
```

路由正確 ✅

---

## 下一步（Phase 5 建議）

- [ ] 為 `seo_optimization.md` 和 `project_planning.md` 連接 Pipeline
- [ ] 考慮為 market-research-agent 建立每日自動執行觸發點
- [ ] Codex 實際整合測試（當有 OpenAI API key 後）
