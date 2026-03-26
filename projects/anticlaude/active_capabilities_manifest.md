# Active Capabilities Manifest
> 建立日期：2026-03-16
> 最後更新：2026-03-16（本輪 Sprint 完成後更新）
> 依據：architecture_load_audit_2026-03-14.md 建議 #2
> 目的：區分「能力庫中可用」vs「專案已啟用」vs「已在程式碼中實作」

---

## 一、Active Agents

| Agent | 狀態 | 定義文件 | 程式整合 | 備註 |
|-------|------|---------|---------|------|
| Ori（研究）| ✅ 完全啟用 | `_hub/shared/agents/market_research_agent.md` | `src/ai/claude_scorer.py`（research_analysis skill 注入）| 每日 pipeline 自動執行 |
| Lala（策略）| ✅ 完全啟用 | `_hub/shared/agents/content-strategist.md` | `src/ai/gpt_strategist.py`（marketing_strategy skill 注入）| 每日 pipeline 自動執行 |
| Craft（內容）| ✅ 完全啟用 | `_hub/shared/agents/threads-writer.md` | `src/ai/claude_writer.py`（content_creation skill 注入）| 每日 pipeline 自動執行 |
| Sage（分析）| ✅ 完全啟用 | `_hub/shared/agents/sage.md` | `src/ai/claude_scorer.py`（seo_optimization skill 注入）| 選品評分 + 主題評分 |
| Lumi（工程）| ✅ 手動啟用 | `_hub/shared/agents/coding_agent.md` | Claude Code / Codex | 開發時呼叫 |
| Pixel（設計）| 🟡 部分啟用 | `_hub/shared/agents/pixel.md` | UX 審核文件 | 無自動化流程 |
| **CEO（協調）**| ✅ 新增啟用 | `projects/anticlaude/project_routing_map.md` | `src/agents/ceo.py`（意圖偵測 + 路由）| POST /api/chat 呼叫 |

---

## 二、Active Skills

### Composite Skills（已建立 + 已注入，2026-03-16）

| Skill | 對應 Agent | 文件 | 程式整合 | 狀態 |
|-------|-----------|------|---------|------|
| content_creation | Craft | `_hub/shared/skills/composite/content_creation.md` | `src/ai/claude_writer.py` | ✅ 已注入 prompt |
| marketing_strategy | Lala | `_hub/shared/skills/composite/marketing_strategy.md` | `src/ai/gpt_strategist.py` | ✅ 已注入 prompt |
| seo_optimization | Sage | `_hub/shared/skills/composite/seo_optimization.md` | `src/ai/claude_scorer.py` | ✅ 已注入 prompt |
| research_analysis | Ori | `_hub/shared/skills/composite/research_analysis.md` | `src/ai/competitor_analyzer.py` + `src/scrapers/perplexity_scraper.py` | ✅ 已注入 |
| ux_review | Pixel | `_hub/shared/skills/composite/ux_review.md` | UX 審核文件 | ⚠️ Pixel 無自動化流程 |
| project_planning | Lumi | `_hub/shared/skills/composite/project_planning.md` | Claude Code / Codex | ⚠️ 手動使用 |

### Skill Loader 基礎設施（2026-03-16 新增）

| 模組 | 位置 | 功能 | 狀態 |
|------|------|------|------|
| skill_loader.py | `src/ai/skill_loader.py` | 統一載入 composite skill .md → 注入 prompt | ✅ 啟用中 |

### 現有 Skills（已在程式碼中使用）

| Skill | 位置 | 程式整合 | 狀態 |
|-------|------|---------|------|
| writing_guide | `_hub/shared/skills/writing_guide.md` | 部分（prompt 內嵌）| ✅ 運作中 |
| seo_optimization（舊）| `_hub/shared/skills/seo_optimization.md` | 未（被 composite 版取代）| ⚠️ 文件存在，已被新版覆蓋 |
| strategy_guide | `_hub/shared/skills/strategy_guide.md` | 未 | 文件存在 |

---

## 三、停用 / 未啟用的能力

| 能力 | 來源 | 原因 | 計畫啟用 |
|------|------|------|---------|
| Humanizer-zh | `_hub/skills_library/Humanizer-zh/` | content_creation composite 已含去 AI 痕跡邏輯，但非 Humanizer 完整整合 | Phase 4 |
| geo-seo-claude | `_hub/skills_library/geo-seo-claude/` | 已提取為 seo_optimization composite，程式注入完成 | ✅ 部分完成 |
| ai-night-shift | `src/agents/night_shift.py` | ✅ Phase 5 完成：22:00 自治推進 | — |
| OpenAI Agents SDK | 外部參考 | 僅作架構參考 | Phase 5 |
| Vizro Dashboard | `_hub/skills_library/vizro/` | 未整合到前端 | 低優先 |
| Figma MCP | 待設定 | 需要 Figma Access Token | Phase 4（待 token）|
| Magic UI | npm package | CEO Console 已建立，視覺升級延後 | Phase 4 |
| Aceternity UI | npm package | CEO Console 已建立，動畫升級延後 | Phase 4 |

---

## 四、整合狀態追蹤（Integration Status）

| 系統領域 | 規格文件 | API 實作 | UI 實作 | 驗證 |
|---------|---------|---------|---------|------|
| Content Pipeline | ✅ | ✅ | ✅ | ✅ |
| AI Office | ✅ | ✅ | ✅ | ✅ |
| Flow Lab（選品）| ✅ | ✅ | ✅ | ⚠️ 部分 |
| Feedback Loop | ✅ | ✅ | ✅ | ⚠️ 數據累積中 |
| Weekly Reports | ✅ | ✅ | ✅ | ✅ |
| Tracker | ✅ | ✅ | ✅ | ✅ |
| CEO Console | ✅ | ✅ POST /api/chat | ✅ /chat | ⚠️ 待測試 |
| Review Queue | ✅ | ✅ GET/POST/PATCH | ✅ /review | ⚠️ 待實際使用 |
| Morning Briefing | ✅ | ✅ /api/morning/briefing | ✅ 首頁 + /morning | ✅ |
| Morning Report Page | ✅ | ✅ /api/morning-report | ✅ /morning | ✅ |
| Composite Skills | ✅ | ✅ skill_loader.py | N/A | ✅ 4/6 已注入（Craft/Lala/Sage/Ori）|
| CEO Agent | ✅ | ✅ src/agents/ceo.py | ✅ /chat | ⚠️ 待測試 |
| Night Shift | ✅ | ✅ /api/night-shift/status + /trigger | ✅ /morning 夜班摘要 | ✅ 7/7 tests |

---

## 五、下一步行動

| 優先度 | 任務 | 負責 | 狀態 |
|--------|------|------|------|
| ✅ 完成 | Review Queue API + 頁面 | Lumi | ✅ 2026-03-16 |
| ✅ 完成 | Composite Skills 注入 agent prompt（3/6）| Lumi | ✅ 2026-03-16 |
| ✅ 完成 | CEO Agent `src/agents/ceo.py` | Lumi | ✅ 2026-03-16 |
| ✅ 完成 | POST /api/chat | Lumi | ✅ 2026-03-16 |
| ✅ 完成 | GET /api/morning-report + /morning 頁面 | Lumi | ✅ 2026-03-16 |
| ✅ 完成 | research_analysis skill 注入 Ori（competitor_analyzer + perplexity_scraper）| Lumi | ✅ 2026-03-16 |
| 中 | Figma MCP 設定（待 token）| Lumi | Phase 4 |
| 中 | Magic UI / Aceternity UI 安裝（CEO Console 視覺升級）| Pixel | Phase 4 |
| 低 | Night Shift Mode | Lumi | Phase 5 |

---
*最後更新：2026-03-16*
*關聯文件：architecture_load_audit_2026-03-14.md、ai_os_gap_analysis_20260316.md、aitos_resource_integration_plan_20260316.md*
