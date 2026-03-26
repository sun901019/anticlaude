# Project Routing Map
> 建立日期：2026-03-16
> 依據：architecture_load_audit_2026-03-14.md 建議 #1
> 目的：明確定義「任務類型 → 負責 agent → 技能 → 輸出」的完整路由

---

## 任務路由總表

| 任務類型 | 負責 Agent | 所需技能 | 輸入來源 | 輸出產物 | 交接給 |
|---------|-----------|---------|---------|---------|-------|
| `content_research` | Ori | research_analysis | Perplexity API / web | `articles` DB 表 | Lala |
| `market_analysis` | Ori | research_analysis | 外部 API | research report .md | Sage |
| `competitor_analysis` | Ori | research_analysis | web | competitor report | Lala / Sage |
| `topic_strategy` | Lala | marketing_strategy | articles + audience data | top3 topics JSON | Craft |
| `audience_analysis` | Lala | marketing_strategy | `posts` DB 表 | audience insights | Lala (self) |
| `draft_generation` | Craft | content_creation | topics JSON | `drafts` DB 表 | Sage / Human |
| `copywriting` | Craft | content_creation + humanizer | brief | draft text | Human review |
| `seo_analysis` | Sage | seo_optimization | brand URL / content | GEO analysis report | Lala |
| `data_analysis` | Sage | research_analysis | `posts` / `fl_performance` | analytics report | Human |
| `product_evaluation` | Sage | research_analysis | `fl_products` | score + recommendation | Human |
| `ui_implementation` | Lumi | project_planning | design spec / task | code PR | Human |
| `backend_development` | Lumi | project_planning | API spec | code PR | Human |
| `system_debugging` | Lumi | project_planning | error log | bug fix | Human |
| `ux_review` | Pixel | ux_review | page screenshots / code | review report | Lumi |
| `design_evaluation` | Pixel | ux_review | UI mockup | feedback list | Lumi |

---

## 固定 Pipeline 路由（每日 08:00）

```
Ori（content_research）
  ↓ articles 數據
Lala（topic_strategy）
  ↓ top3 topics
Craft（draft_generation）
  ↓ drafts
Sage（product_evaluation，並行）
  ↓ 評分結果
Human（review & publish）
```

---

## 衝突解決規則

當多個文件對同一任務/角色有不同說法時：

1. `projects/anticlaude/` 操作文件（本文件所在）**最高優先**
2. `src/` 實際執行程式碼
3. `_hub/registry/agents_registry.md`
4. `_hub/shared/agents/` 角色定義
5. `_context/` 廣泛背景

**原則：最新的 `projects/anticlaude/` 文件 > 其他一切。**

---

## Source-of-Truth 層級定義

| 層級 | 位置 | 用途 |
|------|------|------|
| 能力庫 | `_hub/` | 所有可用能力的定義（不自動啟用） |
| 專案操作層 | `projects/anticlaude/` | 此專案實際使用的規則（**本層優先**）|
| 執行層 | `src/` + `dashboard/` | 實際運行的程式碼 |
| 產物層 | `data/` + `outputs/` | 執行的真實證據 |

---

## 載入順序（AI Agent 工作前必讀）

```
1. ai/state/sprint.md         ← 現在要做什麼（最先讀）
2. projects/anticlaude/project_routing_map.md  ← 本文件（路由規則）
3. ai/context/architecture.md ← 系統架構
4. 對應 agent 文件（_hub/shared/agents/）
5. 對應 composite skill（_hub/shared/skills/composite/）
```

---
*最後更新：2026-03-16*
*關聯文件：architecture_load_audit_2026-03-14.md*
