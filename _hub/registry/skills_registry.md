# Skills Registry — Skill 索引

> 所有可用 Skill 的完整清單。
> **最後更新**：2026-03-12（整合後：9 → 6 個 Skills）

---

## 活躍 Skills

| Skill | 檔案 | 說明 | 來源 Repo |
|-------|------|------|----------|
| **writing_guide** | `_hub/shared/skills/writing_guide.md` | Threads 貼文結構 + 去 AI 痕跡（整合 content_creation + text_humanization） | marketingskills + Humanizer-zh |
| **strategy_guide** | `_hub/shared/skills/strategy_guide.md` | 素材評估 + 選題策略 + 受眾成長（整合 research_analysis + marketing_strategy） | awesome-agent-skills + geo-seo-claude + marketingskills |
| **dev_tools** | `_hub/shared/skills/dev_tools.md` | Vizro 視覺化 + HTML 投影片（整合 data_processing + presentation_ui） | vizro + frontend-slides + toonify-mcp |
| **seo_optimization** | `_hub/shared/skills/seo_optimization.md` | GEO + SEO 優化 | geo-seo-claude |
| **project_planning** | `_hub/shared/skills/project_planning.md` | 任務拆解、甘特圖生成 | awesome-agent-skills |
| **coding_agent** | `_hub/shared/skills/coding_agent.md` | 程式碼生成與系統實作 | agency-agents |

---

## Pipeline 中實際使用的 Skill 規則

Skills 規則透過 Prompt Templates 注入（不是 Python import）：

| Prompt 檔案 | 注入的 Skill 規則 |
|------------|----------------|
| `src/ai/prompts/scoring_prompt.txt` | `strategy_guide`：主題比例、多樣性評分、audience_insights |
| `src/ai/prompts/writing_prompt.txt` | `writing_guide`：禁用詞、禁用句式、台灣語氣 |
| `src/ai/prompts/strategy_prompt.txt` | `strategy_guide`：選題多樣性、類型平衡、歷史表現 |

---

## 已歸檔 Skills

已合併，原始檔案在 `_hub/shared/skills/_archive/`：

- `content_creation.md` + `text_humanization.md` → `writing_guide.md`
- `research_analysis.md` + `marketing_strategy.md` → `strategy_guide.md`
- `data_processing.md` + `presentation_ui.md` → `dev_tools.md`

---

## 外部 Repo 對照

| Repo | 本地路徑 | 貢獻給哪個 Skill |
|------|---------|----------------|
| Humanizer-zh（op7418） | `_hub/skills_library/Humanizer-zh/` | `writing_guide` |
| marketingskills | `_hub/skills_library/marketingskills/` | `writing_guide`, `strategy_guide` |
| awesome-agent-skills | `_hub/skills_library/awesome-agent-skills/` | `strategy_guide`, `project_planning` |
| geo-seo-claude | `_hub/skills_library/geo-seo-claude/` | `strategy_guide`, `seo_optimization` |
| agency-agents | `_hub/skills_library/agency-agents/` | `coding_agent`, agents 參考 |
| vizro | `_hub/skills_library/vizro/` | `dev_tools` |
| frontend-slides | `_hub/skills_library/frontend-slides/` | `dev_tools` |
| toonify-mcp | `_hub/skills_library/toonify-mcp/` | `dev_tools` |
| aws-agent-skills-libukai | `_hub/skills_library/aws-agent-skills-libukai/` | 備用（DevOps 場景） |
