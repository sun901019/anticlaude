# 任務：啟動 AI-OS 升級計畫 (Phase 1-5)

> ⚠️ 這份文件是給 **Claude Code** 看的執行指令  
> 由 **Antigravity** 負責架構與提煉，請 **Claude Code** 負責終端操作與資料夾搬遷。

---

## 🎯 你的任務目標
將目前的 AntiClaude 單一專案結構，依據 `C:\Users\sun90\.gemini\antigravity\brain\80551ae4-a942-46fa-b6b9-1e27a513bee5\implementation_plan.md` 的規劃，徹底重構為一個 **標準化 AI-OS 中台架構**。

請依照以下 5 個 Phase 依序執行。**每完成一個 Phase，請向我回報狀態，再進行下一個**。

---

## 🏗️ Phase 1: 基礎架構重建 (這部分請你現在執行)

目前的 `c:\Users\sun90\Anticlaude` 根目錄有許多業務代碼。你需要將它們封裝進 `projects/anticlaude/` 內。

**1. 建立核心目錄結構**
在根目錄下建立：
- `_hub/skills_library/`
- `_hub/registry/`
- `_hub/shared/skills/`
- `_hub/shared/agents/`
- `_hub/shared/tools/`
- `_hub/visualization/vizro/`
- `projects/anticlaude/`

**2. 搬遷現有業務代碼**
將以下現有資料夾與檔案，**移動 (Move)** 到 `projects/anticlaude/`：
- `src/`
- `dashboard/`
- `data/`
- `outputs/`
- `uploads/`
- `tests/`
- `logs/`
- `skills/` (舊的，非 _hub 下的)
- `database_schema.md` (如果還在根目錄)
- `system_architecture.md` (如果還在根目錄)
- `project_record.md` (如果還在根目錄)
- `resource_map.md` (如果還在根目錄)
- `pytest.ini`

*(注意：保留根目錄的 `_context/`, `CLAUDE.md`, `README.md`, `requirements.txt` 不動)*

**3. 建立專案標準結構**
在 `projects/anticlaude/` 內建立一個空的 `project_context.md`。

---

## 📥 Phase 2: 能力庫吞噬 (請在 Phase 1 成功後執行)

請將以下 9 個 Repository clone 到 `_hub/skills_library/` 目錄下：

用指令：
```bash
cd _hub/skills_library
git clone https://github.com/msitarzewski/agency-agents.git
git clone https://github.com/zarazhangrui/frontend-slides.git
git clone https://github.com/PCIRCLE-AI/toonify-mcp.git
git clone https://github.com/heilcheng/awesome-agent-skills.git
git clone https://github.com/libukai/awesome-agent-skills.git aws-agent-skills-libukai
git clone https://github.com/zubair-trabzada/geo-seo-claude.git
git clone https://github.com/coreyhaines31/marketingskills.git
git clone https://github.com/op7418/Humanizer-zh.git
git clone https://github.com/mckinsey/vizro.git
cd ../../
```

---

## 🛑 Phase 3: 等待 Antigravity 提煉 (你只要建檔案就好)

因為要從這 9 個 Repo 中掃描幾百個 MD 檔並「手動融合成 9 大精華技能」，這需要極強的 Context 理解。**這個邏輯萃取工作由 Antigravity 負責**。

**你的任務是幫忙把空檔案建好，並注入基礎模板**：
1. 建立 `_hub/registry/` 裡的 `skills_registry.md`, `agents_registry.md`, `tools_registry.md`, `capability_map.md`
2. 建立 `_hub/shared/skills/` 裡的 9 個 skill 檔案：
   `research_analysis.md`, `marketing_strategy.md`, `content_creation.md`, `seo_optimization.md`, `text_humanization.md`, `presentation_ui.md`, `data_processing.md`, `project_planning.md`, `coding_agent.md`
*(內容留空或只寫 `# [Skill Name]` 標題，後續 Antigravity 會來補寫。)*

---

## 🤖 Phase 4: 代理人與工具編制 (建立空檔案)

跟 Phase 3 一樣，請幫忙建好基礎空檔案，由 Antigravity 負責內容編寫：
1. 建立 `_hub/shared/agents/` 裡的 5 個 agent：
   `market_research_agent.md`, `marketing_strategy_agent.md`, `content_agent.md`, `planning_agent.md`, `coding_agent.md`
2. 建立 `_hub/shared/tools/` 裡的 `data_processing_tool.md`, `visualization_tool.md`
3. 建立 `_hub/visualization/vizro/app.py`，裡面寫一個最基礎的 Vizro Hello World 模板（需 `pip install vizro`）。

---

## 🚀 Phase 5: 執行層與開機更新

最後，請幫我更新根目錄的 `CLAUDE.md` 與 `README.md`，宣告系統已進入 AI-OS 模式，並指引如何啟動 `projects/anticlaude/` 內的專案。並隨意建立一個 `START_HERE.md` 放根目錄。

---
**請先問使用者：**「要我現在開始執行 Phase 1 (搬遷與建目錄) 嗎？」
