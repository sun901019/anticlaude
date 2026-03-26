# Composite Skills Registry
> 建立日期：2026-03-16
> 說明：此 registry 登記所有從外部 repo 提取並整合的 composite skill 定義文件
> 位置：`_hub/shared/skills/composite/`

---

## 已建立的 Composite Skills

| Skill 文件 | 主要 Agent | 用途 | 來源 Repo |
|-----------|----------|------|---------|
| `content_creation.md` | Craft | Threads 文案 + AI 痕跡去除 + 電商文案 | marketingskills, Humanizer-zh |
| `marketing_strategy.md` | Lala | 選題策略 + 內容漏斗 + 受眾分析 | agency-agents, marketingskills |
| `seo_optimization.md` | Sage | GEO/SEO 分析 + E-E-A-T 評估 | geo-seo-claude |
| `research_analysis.md` | Ori | 競品研究 + 市場分析 + 選品調查 | agency-agents |
| `ux_review.md` | Pixel | UI/UX 審核 + Dashboard 設計原則 | agency-agents (design) |
| `project_planning.md` | 全體 (主要 Lumi) | 任務拆解 + 交接格式 + Sprint 原則 | agency-agents (strategy) |

---

## 與現有 Skills 的關係

| 現有 Skill | 對應 Composite Skill | 關係 |
|-----------|---------------------|------|
| `writing_guide.md` | `content_creation.md` | **補充**（現有保留，composite 加強） |
| `strategy_guide.md` | `marketing_strategy.md` | **補充** |
| `seo_optimization.md` | `seo_optimization.md`（composite）| **強化**（加入 GEO 維度） |
| `dev_tools.md` | `project_planning.md` | **補充** |

---

## 尚未提取的 Skills（待後續 Phase）

| 來源 Repo | 可提取內容 | 計畫 Phase |
|---------|---------|-----------|
| `marketingskills/skills/social-content/` | 社群內容策略深化 | Phase 2 |
| `marketingskills/skills/paid-ads/` | 廣告投放策略 | Phase 3 |
| `awesome-agent-skills/` | 通用技能（中文版）| Phase 2 |
| `agency-agents/sales/` | 電商銷售策略 | Phase 3 |

---

## 使用方式

Agent 在需要特定能力時，在 system prompt 或工作前讀取對應的 composite skill 文件。

範例（Craft 準備寫文案時）：
```
讀取：_hub/shared/skills/composite/content_creation.md
應用：按照其中的 Threads 貼文結構框架 + 去除 AI 痕跡 checklist
```

---

*最後更新：2026-03-16*
