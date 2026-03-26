# Agents Registry

> 所有可用 Agent 的索引。Agent 負責協調 Skill，依任務選用正確工具。
> **最後更新**：2026-03-13（6 個核心角色全部建立）

---

## 6 個核心 AI 員工

| 暱稱              | Agent 檔案                               | 職責                             | 記憶來源                 | 狀態           |
| ----------------- | ---------------------------------------- | -------------------------------- | ------------------------ | -------------- |
| **Lala**（策略）  | `shared/agents/content-strategist.md`    | 今日選題、策略規劃               | `audience_insights`      | ✅ 完整版      |
| **Craft**（內容） | `shared/agents/threads-writer.md`        | Threads 文案撰寫                 | `top_hooks`              | ✅ 完整版      |
| **Ori**（研究）   | `shared/agents/market_research_agent.md` | AI 新聞篩選、台灣切角分析        | `research_cache`（待建） | ✅ 完整版      |
| **Lumi**（工程）  | `shared/agents/coding_agent.md`          | 程式碼開發、架構設計             | —                        | ✅ 完整版      |
| **Sage**（投資）  | `shared/agents/sage.md`                  | 美股/加密/台股分析（不建議操作） | `investment_log`（待建） | 🟡 SOUL 已定義 |
| **Pixel**（設計） | `shared/agents/pixel.md`                 | 視覺風格、UI 建議、品牌設計      | `design_prefs`（待建）   | 🟡 SOUL 已定義 |

---

## 輔助 Agents

| Agent                      | 檔案                                        | 主要任務           | 狀態 |
| -------------------------- | ------------------------------------------- | ------------------ | ---- |
| `marketing-strategy-agent` | `shared/agents/marketing_strategy_agent.md` | 週選題規劃         | ✅   |
| `content-agent`            | `shared/agents/content_agent.md`            | 多格式內容生產     | ✅   |
| `planning-agent`           | `shared/agents/planning_agent.md`           | 專案規劃、任務拆解 | ✅   |

---

## Agency-Agents 外部庫（來自 msitarzewski/agency-agents）

位置：`_hub/skills_library/agency-agents/`

涵蓋角色：UI Designer、Frontend Developer、Backend Architect、
Growth Hacker、DevOps Automator、Content Creator、SEO Specialist 等 50+ 個。

使用方式：直接引用原始 repo 中的 agent 定義。

---

## Agent 選用指南

```
任務分類 → 對應 Agent：

「今天發什麼？」         → Lala（content-strategist）
「寫這篇貼文」           → Craft（threads-writer）
「哪個新聞值得做」       → Ori（market-research-agent）
「幫我寫程式 / 看架構」  → Lumi（coding-agent）
「市場今天怎麼了」       → Sage（sage）
「這個畫面怎麼設計」     → Pixel（pixel）
「本週怎麼排？」         → marketing-strategy-agent
「做一份投影片」         → content-agent
「拆解這個功能需求」     → planning-agent
```
