# 專案紀錄 — AntiClaude 內容自動化系統

> 最後更新：2026-03-11  
> 工作區：`c:\Users\sun90\Anticlaude`

---

## 📊 專案現況總覽

| 項目 | 狀態 |
|------|------|
| **規劃文件** | ✅ 完成（7 份 .md） |
| **Python 後端** | ✅ 已實作（37 個模組） |
| **FastAPI API** | ✅ 已啟動（14 個 endpoint） |
| **Next.js 儀表板** | 🔧 初始結構已建立 |
| **SQLite 資料庫** | ✅ 5 張表已建立 |
| **Pipeline** | ✅ 可執行（含 dry-run） |
| **Threads 追蹤** | ✅ 已實作 |
| **閉環回饋** | ✅ 已實作 |
| **測試** | ✅ 基礎測試已寫 |

---

## 📁 目前檔案結構

```
Anticlaude/                          (81 files)
│
├── _context/                        ← AI 記憶檔
│   ├── about_me.md                  ← 品牌定位、受眾、語氣
│   ├── workflow.md                  ← 每日/每週流程
│   └── api_reference.md             ← API 對照表
│
├── src/                             ← Python 後端（37 模組）
│   ├── config.py                    ← 環境變數（pydantic-settings）
│   ├── pipeline.py                  ← 每日全流程串接
│   │
│   ├── scrapers/                    ← 資料抓取
│   │   ├── rss_scraper.py           ← TechCrunch/VentureBeat/Verge/AI News
│   │   ├── serper_scraper.py        ← Google 新聞 EN+ZH
│   │   ├── perplexity_scraper.py    ← 即時熱門 AI 話題
│   │   ├── hn_scraper.py            ← Hacker News Top 20
│   │   └── aggregator.py            ← 並行整合
│   │
│   ├── ai/                          ← AI 分析模組
│   │   ├── gemini_cluster.py        ← Gemini 聚類去重
│   │   ├── claude_cluster.py        ← Claude 聚類（備用）
│   │   ├── claude_scorer.py         ← Claude 評分
│   │   ├── claude_writer.py         ← Claude 文案生成
│   │   ├── gpt_strategist.py        ← GPT 策略選題
│   │   └── prompts/                 ← 5 個 Prompt 模板
│   │       ├── cluster_prompt.txt
│   │       ├── scoring_prompt.txt
│   │       ├── writing_prompt.txt
│   │       ├── strategy_prompt.txt
│   │       └── weekly_prompt.txt
│   │
│   ├── db/                          ← SQLite 資料庫層
│   │   ├── connection.py            ← DB 連線管理
│   │   ├── schema.py                ← 5 張表 DDL
│   │   └── queries.py               ← 查詢封裝
│   │
│   ├── tracker/                     ← Threads 追蹤
│   │   ├── threads_client.py        ← Graph API 封裝
│   │   └── metrics_collector.py     ← 數據抓取 + 寫入
│   │
│   ├── feedback/                    ← 閉環回饋引擎
│   │   └── analysis_engine.py       ← GPT 受眾偏好分析
│   │
│   ├── weekly/                      ← 週報生成
│   │   └── weekly_report.py
│   │
│   ├── api/                         ← FastAPI 後端 API
│   │   └── main.py                  ← 14 個 endpoint
│   │
│   └── utils/                       ← 共用工具
│       ├── http_client.py           ← async httpx
│       ├── file_io.py               ← 檔案讀寫
│       └── logger.py                ← 結構化日誌
│
├── dashboard/                       ← Next.js 儀表板
│   ├── src/app/
│   │   ├── layout.tsx               ← 深色主題 root layout
│   │   ├── globals.css              ← 設計系統
│   │   ├── page.tsx                 ← 今日總覽（341 行）
│   │   ├── metrics/page.tsx         ← Threads 數據頁
│   │   ├── library/page.tsx         ← 素材庫
│   │   ├── reports/page.tsx         ← 週報
│   │   └── error.tsx                ← 錯誤邊界
│   ├── src/components/
│   │   └── Sidebar.tsx              ← 側邊欄導航
│   └── src/lib/
│       └── api.ts                   ← API client
│
├── data/
│   └── anticlaude.db                ← SQLite 資料庫
│
├── outputs/                         ← 系統產出
│   ├── daily_reports/2026-03-10.md  ← 每日報告
│   ├── drafts/2026-03-10.md         ← 文案草稿
│   ├── threads_metrics/             ← Threads 數據
│   └── weekly_reports/week_2026-11.md
│
├── uploads/                         ← 原始素材
│   └── raw_feed_2026-03-10.json
│
├── tests/                           ← 測試
│   ├── test_utils.py
│   ├── test_rss.py
│   ├── test_serper.py
│   └── test_threads.py
│
├── logs/                            ← 日誌
│   ├── 2026-03-10.log
│   └── 2026-03-11.log
│
├── projects/                        ← 長期項目（空）
├── skills/                          ← AI skills（空）
│
├── README.md
├── requirements.txt                 ← 12 個 Python 依賴
├── database_schema.md               ← DB schema 文件
├── folder_structure.md
├── system_architecture.md
└── pytest.ini
```

---

## 🔌 已實作的 API Endpoints（FastAPI）

| Method | Endpoint | 功能 |
|--------|----------|------|
| `GET` | `/health` | 健康檢查 |
| `GET` | `/api/today` | 今日總覽 |
| `POST` | `/api/pipeline/run` | 🚀 跑完整 pipeline |
| `GET` | `/api/pipeline/status` | Pipeline 狀態 |
| `POST` | `/api/tracker/run` | 📊 抓 Threads 數據 |
| `GET` | `/api/tracker/status` | Tracker 狀態 |
| `GET` | `/api/metrics` | Threads 指標（DB） |
| `GET` | `/api/library` | 素材庫 |
| `GET` | `/api/library/dates` | 可用日期 |
| `POST` | `/api/weekly/run` | 📋 生成週報 |
| `GET` | `/api/weekly/latest` | 最新週報 |
| `GET` | `/api/weekly/list` | 週報列表 |
| `POST` | `/api/feedback/run` | 🧠 回饋分析 |
| `GET` | `/api/insights` | 受眾洞察 |

---

## 🗄️ 資料庫表（SQLite）

| 表名 | 筆數 | 用途 |
|------|------|------|
| `articles` | → 抓取後累積 | 所有素材 + URL 去重 |
| `topics` | → 每日產出 | 處理後主題 + 評分 |
| `posts` | → Threads 追蹤 | 貼文 + 互動指標 |
| `drafts` | → 每日產出 | 文案記錄 |
| `audience_insights` | → 回饋分析 | 受眾偏好模型 |

---

## 📦 技術棧

| 類別 | 技術 | 版本 |
|------|------|------|
| 後端 | Python | 3.14 |
| API | FastAPI + Uvicorn | 0.111 / 0.30 |
| 儀表板 | Next.js (App Router) | 14 |
| 樣式 | Tailwind CSS | — |
| 資料庫 | SQLite | 內建 |
| AI | Anthropic SDK | 0.28 |
| AI | OpenAI SDK | 1.35 |
| AI | Google GenAI SDK | 1.5 |
| HTTP | httpx | 0.27 |
| RSS | feedparser | 6.0 |

---

## ⏱️ 時間線

| 日期 | 里程碑 |
|------|--------|
| 2026-03-10 | 規劃啟動：資料夾結構 + 所有 .md 文件 |
| 2026-03-10 | 確認決策：Next.js + 手動觸發 + Gemini 分析 |
| 2026-03-10 | 加入閉環系統 + SQLite 資料庫設計 |
| 2026-03-10~11 | 完整後端實作（37 模組）+ FastAPI API |
| 2026-03-11 | 儀表板初始結構 + 第一份 dry-run 產出 |
| 2026-03-11 | 本紀錄撰寫 |
