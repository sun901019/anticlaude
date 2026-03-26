# 系統架構文件

## 資料流全景

```
┌─────────────────────────────────────────────────────────┐
│                    資料來源（每日 06:00）                   │
│                                                         │
│  RSS Feeds ──┐                                          │
│  Serper API ─┤── 原始素材 (~50-80 則) ─┐                │
│  Perplexity ─┤                        │                │
│  Hacker News ┘                        │                │
│                                       ▼                │
│                            ┌──────────────────┐        │
│                            │  Gemini Flash    │        │
│                            │  聚類 + 去重     │        │
│                            └────────┬─────────┘        │
│                                     │ ~15-20 則        │
│                                     ▼                  │
│                            ┌──────────────────┐        │
│                            │  Claude Sonnet   │        │
│                            │  評分 + 匹配     │        │
│                            └────────┬─────────┘        │
│                                     │ 帶評分           │
│                                     ▼                  │
│                            ┌──────────────────┐        │
│                            │  GPT-4o          │        │
│                            │  策略建議 Top 3   │        │
│                            └────────┬─────────┘        │
│                                     │                  │
│                          ┌──────────┴──────────┐       │
│                          ▼                     ▼       │
│                 ┌──────────────┐      ┌────────────┐   │
│                 │ Claude Sonnet│      │  每日報告   │   │
│                 │ 文案生成 ×2版│      │ daily_report│   │
│                 └──────┬───────┘      └────────────┘   │
│                        ▼                               │
│                 ┌──────────────┐                        │
│                 │  貼文草稿    │                         │
│                 │  drafts/     │                         │
│                 └──────────────┘                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│               Threads 數據追蹤（每日 09:00）              │
│                                                         │
│  Threads Graph API ──→ 昨日貼文數據 ──→ threads_metrics/ │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 週報生成（每週日 10:00）                   │
│                                                         │
│  7天貼文數據 + 7天素材 ──→ GPT-4o ──→ weekly_reports/    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 模組拆解

### Module 1：資料抓取 `scraper`
- **輸入**：無（定時觸發）
- **處理**：並行抓取 4 個來源，統一格式化
- **輸出**：`uploads/raw_feed_YYYY-MM-DD.json`
- **統一格式**：
```json
{
  "title": "文章標題",
  "url": "原文連結",
  "source": "techcrunch | serper_en | serper_zh | perplexity | hackernews",
  "summary": "摘要（100-200字）",
  "published_at": "2026-03-10T06:00:00Z",
  "language": "en | zh-TW"
}
```

### Module 2：AI 分析 `analyzer`
- **輸入**：`raw_feed_YYYY-MM-DD.json` + `_context/about_me.md`
- **Step 1 (Gemini 2.0 Flash)**：聚類去重 + 深度文章分析（替代 NotebookLM）→ 15-20 則精華
- **Step 2 (Claude Sonnet)**：受眾匹配度評分 1-10 + 貼文類型建議
- **Step 3 (GPT-4o)**：結合近 7 天 Threads 數據，選 Top 3
- **輸出**：`outputs/daily_reports/YYYY-MM-DD.md`

### Module 3：文案生成 `writer`
- **輸入**：Top 3 主題 + `_context/about_me.md`
- **處理**：Claude Sonnet 為每個主題生成 2 版文案
- **輸出**：`outputs/drafts/YYYY-MM-DD.md`
- **文案格式**：含 Hook、正文、CTA、建議 hashtag

### Module 4：Threads 追蹤 `tracker`
- **輸入**：Threads Access Token
- **處理**：抓取所有貼文 → 每篇查詢 insights
- **輸出**：`outputs/threads_metrics/YYYY-MM-DD.json`
- **數據格式**：
```json
{
  "post_id": "123456",
  "text": "貼文內容前 50 字...",
  "timestamp": "2026-03-09T12:00:00Z",
  "views": 1500,
  "likes": 45,
  "replies": 8,
  "reposts": 3,
  "quotes": 1,
  "engagement_rate": 3.8
}
```

### Module 5：週報引擎 `weekly`
- **輸入**：7 天的 daily_reports + threads_metrics
- **處理**：GPT-4o 統整分析
- **輸出**：`outputs/weekly_reports/week_YYYY-WW.md`

### Module 6：儀表板 `dashboard`（Next.js）
- **技術**：Next.js 14 App Router，深色主題，完整精美 UI
- **觸發方式**：手動按鈕（不自動排程）
- **頁面**：
  1. **今日總覽**：Top 3 主題 + 文案草稿 + 一鍵複製 + 手動觸發按鈕
  2. **Threads 數據**：按讚/觀看/互動率折線圖 + 貼文表格
  3. **素材庫**：所有抓到的素材 + 評分排序 + 搜尋
  4. **週報**：最新週報 + 歷史瀏覽 + 生成週報按鈕

## 技術選型

| 需求 | 選擇 | 理由 |
|------|------|------|
| 後端 | Python | AI SDK 生態最完整 |
| 儀表板 | Next.js 14 | 完整好看的 UI，深色主題 |
| 觸發方式 | 手動按鈕 | 儀表板上按就跑，不自動排程 |
| 資料存儲 | JSON/MD 檔案 | 本地優先，不依賴雲端 DB |
| HTTP | httpx (async) | 並行抓取多個來源 |

## 成本估算（每月）

| 服務 | 每日用量 | 月成本估算 |
|------|---------|-----------|
| Gemini Flash | ~3K tokens/天 | ~$0.50 |
| Claude Sonnet | ~5K tokens/天 | ~$3.00 |
| GPT-4o | ~2K tokens/天 | ~$1.50 |
| Perplexity | 1 次/天 | ~$1.00 |
| Serper | 2 次/天 | 免費 (2,500/月) |
| Threads API | 免費 | $0 |
| **合計** | | **~$6/月** |
