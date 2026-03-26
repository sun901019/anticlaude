# 🧠 AntiClaude × AI-OS — 專案全景手冊

> **最後更新**：2026-03-13  
> **系統擁有者**：Sun Lee (@sunlee._.yabg)  
> **專案定位**：個人品牌內容自動化 + AI 能力中台

---

## 一句話介紹

AntiClaude 是一套**全自動的 Threads 內容生產系統**，能自動抓取 AI 新聞、分析篩選、撰寫文案、追蹤數據，形成閉環回饋。在此基礎上，我們搭建了 **AI-OS（AI 作業系統）** 中台架構，整合 9 個開源庫的能力，讓多個 AI Agent 各司其職、協同工作。

---

## 系統架構總覽

```
使用者 (Sun Lee)
    │
    ▼
┌────────────────────────────────────┐
│  Antigravity (規劃 / 決策 / 架構)    │  ← 你正在看的這一層
└──────────┬─────────────────────────┘
           │
    ┌──────┴──────┐
    ▼              ▼
Claude Code     Codex
(主引擎)        (副引擎)
    │              │
    ▼              ▼
┌──────────────────────────────┐
│  AI-OS 中台 (_hub/)           │
│  ├── Agents (7 個專家角色)     │
│  ├── Skills (6 個能力指南)     │
│  └── Tools  (Vizro/MCP/Codex) │
└──────────┬───────────────────┘
           │
           ▼
┌──────────────────────────────┐
│  AntiClaude 業務引擎          │
│  ├── src/    (Python 後端)    │
│  ├── dashboard/ (Next.js 前端)│
│  └── data/   (SQLite 資料庫)  │
└──────────────────────────────┘
```

---

## 📁 目錄結構完整索引

### 🔧 `src/` — Python 後端（核心業務邏輯）

| 模組 | 檔案 | 功能 |
|------|------|------|
| **scrapers/** | `aggregator.py` | 整合所有來源的新聞聚合器 |
| | `rss_scraper.py` | RSS Feed 抓取（TechCrunch 等） |
| | `serper_scraper.py` | Google Serper API 搜尋結果抓取 |
| | `hn_scraper.py` | Hacker News 熱門文章抓取 |
| | `perplexity_scraper.py` | Perplexity AI 搜尋結果抓取 |
| **ai/** | `claude_cluster.py` | Claude 聚類分析（文章分組） |
| | `claude_scorer.py` | Claude 評分（5 維度素材評估） |
| | `claude_writer.py` | Claude 文案生成（含品質驗證） |
| | `gemini_cluster.py` | Gemini 備援聚類 |
| | `gpt_strategist.py` | GPT 選題策略（多樣性控制） |
| | `prompts/` | 各 AI 模型的 System Prompt 模板 |
| **agents/** | `orchestrator.py` | Agent 流程編排器 |
| | `debate.py` | 多 Agent 辯論機制 |
| | `judge.py` | 辯論裁判 |
| | `base.py` | Agent 基礎類別 |
| | `cluster.py` / `score.py` / `strategy.py` / `writer.py` | 各職能 Agent 定義 |
| **db/** | `schema.py` | 資料庫結構定義（6 張表） |
| | `queries.py` | 資料庫查詢封裝 |
| | `connection.py` | SQLite 連線管理 |
| **api/** | `main.py` | FastAPI 伺服器（14+ 個 endpoint） |
| **feedback/** | `analysis_engine.py` | 受眾洞察分析引擎 |
| | `memory.py` | 歷史記憶與學習系統 |
| **tracker/** | `metrics_collector.py` | Threads 互動數據收集 |
| | `threads_client.py` | Threads API 客戶端 |
| **weekly/** | `weekly_report.py` | 週報自動生成 |
| **utils/** | `file_io.py` | 檔案讀寫工具 |
| | `http_client.py` | HTTP 請求封裝 |
| | `logger.py` | 日誌系統 |
| **根目錄** | `pipeline.py` | 🔥 主流程引擎（串接所有模組） |
| | `config.py` | 環境變數與設定管理 |

---

### 🖥️ `dashboard/` — Next.js 14 前端儀表板

| 路徑 | 功能 |
|------|------|
| `src/app/page.tsx` | 首頁（總覽儀表板） |
| `src/app/picks/` | 今日精選文章頁 |
| `src/app/metrics/` | Threads 互動數據頁 |
| `src/app/insights/` | 受眾洞察分析頁 |
| `src/app/library/` | 文章庫瀏覽頁 |
| `src/app/reports/` | 週報查看頁 |
| `src/components/TopNav.tsx` | 頂部導航列 |
| `src/components/Sidebar.tsx` | 側邊選單 |
| `src/lib/` | 共用函式庫 |

**技術棧**：Next.js 14 App Router + Tailwind CSS + recharts 圖表

---

### 🗄️ `data/` — SQLite 資料庫

資料庫：`anticlaude.db`（229 KB）

| 資料表 | 用途 |
|--------|------|
| `articles` | 抓取的原始文章 |
| `posts` | Threads 貼文記錄 |
| `post_stats` | 每篇貼文的互動數據 |
| `audience_insights` | 受眾洞察分析結果 |
| `daily_picks` | 每日精選文章 |
| `pipeline_runs` | Pipeline 執行紀錄 |

---

### 📤 `outputs/` — 系統產出

| 資料夾 | 內容 |
|--------|------|
| `daily_reports/` | 每日 Pipeline 執行報告（JSON） |
| `drafts/` | AI 生成的文案草稿 |
| `threads_metrics/` | Threads 平台互動數據快照 |
| `weekly_reports/` | 週報總結 |

---

### 🧪 `tests/` — 自動化測試

| 測試檔 | 覆蓋範圍 |
|--------|---------|
| `test_pipeline.py` | Pipeline 主流程 |
| `test_rss.py` | RSS 抓取功能 |
| `test_serper.py` | Serper API |
| `test_threads.py` | Threads 資料追蹤 |
| `test_utils.py` | 工具函式 |

執行：`pytest tests/ -v`

---

### 📝 `_context/` — AI 記憶檔案

| 檔案 | 說明 |
|------|------|
| `about_me.md` | 品牌定位、受眾畫像、主題比例 |
| `workflow.md` | Pipeline 工作流程詳述 |
| `api_reference.md` | 所有 API 端點參考文件 |

---

### 🧠 `_hub/` — AI-OS 中台（能力調度系統）

這是整個 AI 作業系統的核心。

#### `_hub/shared/skills/` — 6 個能力指南

| Skill 檔案 | 用途 | 提煉自 |
|-----------|------|--------|
| `writing_guide.md` | Threads 貼文完整寫作指南 + 去 AI 痕跡 | marketingskills + Humanizer-zh |
| `strategy_guide.md` | 選題策略 + 素材分析 + 受眾成長 | awesome-agent-skills + geo-seo + marketingskills |
| `dev_tools.md` | Vizro 視覺化 + HTML 投影片 + toonify-mcp | vizro + frontend-slides + toonify-mcp |
| `coding_agent.md` | 程式碼開發技術規範 | agency-agents |
| `seo_optimization.md` | GEO + 傳統 SEO 優化 | geo-seo-claude + marketingskills |
| `project_planning.md` | 任務拆解與規劃 | awesome-agent-skills |

#### `_hub/shared/agents/` — 7 個 AI Agent

| Agent 檔案 | 呼叫名稱 | 職能 | 完成度 |
|-----------|---------|------|:---:|
| `threads-writer.md` | Threads Writer | 繁中 Threads 文案生成 | ✅ 完整 |
| `content-strategist.md` | Content Strategist | 內容選題與策略規劃 | ✅ 完整 |
| `market_research_agent.md` | Market Research | 市場調研、競品分析 | 🔲 骨架 |
| `marketing_strategy_agent.md` | Marketing Strategy | 行銷策略規劃 | 🔲 骨架 |
| `content_agent.md` | Content Agent | 多格式內容生產 | 🔲 骨架 |
| `planning_agent.md` | Planning Agent | 專案規劃、任務拆解 | 🔲 骨架 |
| `coding_agent.md` | Coding Agent | 程式碼生成與重構 | 🔲 骨架 |

另外引用 `agency-agents/` 外部庫的 50+ 專業角色（UI Designer、Backend Architect、Growth Hacker 等）。

#### `_hub/shared/tools/` — 工具定義

| 工具 | 用途 |
|------|------|
| `data_processing_tool.md` | 數據清理與格式化 |
| `visualization_tool.md` | Vizro 互動式儀表板 |
| `codex_integration.md` | Codex 執行引擎路由規則 |
| `toonify-mcp/` | Token 壓縮 MCP 服務 |

#### `_hub/registry/` — 能力索引

| 索引檔 | 功能 |
|--------|------|
| `skills_registry.md` | 所有 Skill 的總目錄 |
| `agents_registry.md` | 所有 Agent 的總目錄 |
| `tools_registry.md` | 所有 Tool 的總目錄 |
| `capability_map.md` | 🗺️ 任務 → Agent → Skill 路由表 |

#### `_hub/skills_library/` — 9 個原始 GitHub Repo（未修改）

| Repo 名稱 | 提供能力 |
|-----------|---------|
| `agency-agents` | 50+ AI 專業角色定義 |
| `frontend-slides` | HTML 投影片製作 |
| `toonify-mcp` | 圖片卡通化 / Token 壓縮 |
| `awesome-agent-skills` | Agent Skills 技能庫 |
| `aws-agent-skills-libukai` | Agent Skills 技能庫（另一版本） |
| `geo-seo-claude` | AI 搜尋可見度 (GEO) 優化 |
| `marketingskills` | 行銷技能提示詞 |
| `Humanizer-zh` | 中文去 AI 痕跡 |
| `vizro` | McKinsey 開源互動式儀表板 |

#### 其他 `_hub/` 檔案

| 檔案 | 說明 |
|------|------|
| `START_HERE.md` | AI-OS 快速入門 |
| `anticlaude-intro.html` | 系統介紹 HTML 投影片 |
| `extract_skills.py` | 技能掃描腳本 |
| `extracted_capabilities.md` | 507 個原始 skill 掃描報告 |

---

### 📂 其他根目錄檔案

| 檔案 | 說明 |
|------|------|
| `CLAUDE.md` | Claude Code 自動派遣規則（Agent 路由表 + 上下文載入 + 執行引擎選擇） |
| `START_HERE.md` | 系統入門指南 |
| `README.md` | 專案 README |
| `.env` | API Key 與環境變數 |
| `requirements.txt` | Python 依賴套件 |
| `pytest.ini` | 測試設定 |

---

## 🔄 Pipeline 自動化流程

```
🌐 新聞抓取        → aggregator.py（RSS + Serper + HN + Perplexity）
    ↓
🧠 聚類分組        → claude_cluster.py（將相似文章分群）
    ↓
⭐ 素材評分        → claude_scorer.py（5 維度：相關性/新鮮度/實用性/話題性/獨特性）
    ↓
📋 策略選題        → gpt_strategist.py（注入主題比例 + 多樣性規則）
    ↓
✍️ 文案生成        → claude_writer.py（注入 writing_guide 規則 + 品質驗證）
    ↓
📊 數據追蹤        → metrics_collector.py → audience_insights → 閉環回饋
```

---

## 👥 Agent 自動派遣（CLAUDE.md 路由）

| 你說什麼 | 系統匹配的 Agent | 使用的 Skill |
|---------|:---:|------|
| 「選題」「今天發什麼」 | Content Strategist | `strategy_guide` |
| 「寫文案」「寫貼文」 | Threads Writer | `writing_guide` |
| 「改 UI」「調整畫面」 | UI Designer | `dev_tools` |
| 「寫 API」「改後端」 | Backend Architect | `coding_agent` |
| 「SEO」「關鍵字」 | Market Research | `seo_optimization` |
| 「做簡報」「投影片」 | Content Agent | `dev_tools` |
| 「部署」「Docker」 | DevOps Automator | `coding_agent` |

---

## ⚙️ 執行引擎

| 引擎 | 適用任務 |
|------|---------|
| **Claude Code** | 跨檔案重構、新功能、Pipeline 修改、架構設計 |
| **Codex** | 單檔 bug fix、生成測試、CSS 微調、Docstring |
| **Antigravity** | 系統規劃、Agent 設計、決策仲裁 |

---

## 🚀 常用指令速查

```bash
# 後端 API
uvicorn src.api.main:app --reload --port 8000

# 前端儀表板
cd dashboard && npm run dev

# 執行 Pipeline
python src/pipeline.py           # 正式執行
python src/pipeline.py --dry-run # 測試模式

# 測試
pytest tests/ -v

# 資料庫初始化
python -m src.db.schema
```

---

## 📌 關鍵數字

| 項目 | 數量 |
|------|:---:|
| Python 後端模組 | 8 個 |
| Python 檔案 | 25+ |
| API Endpoints | 14+ |
| 前端頁面 | 6 個 |
| AI Agent | 7 個自建 + 50 外部 |
| Composite Skills | 6 個 |
| 外部 Repo | 9 個 |
| 自動化測試 | 5 個檔案 |
| 資料庫表 | 6 張 |
