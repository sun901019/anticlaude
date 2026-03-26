# AntiClaude — 系統架構
> 更新日期：2026-03-21

## 技術棧

| 層 | 技術 | 路徑 | Port |
|----|------|------|------|
| 後端 API | Python FastAPI | `src/api/main.py` | 8000 |
| 前端 | Next.js 14 App Router | `dashboard/` | 3000 |
| 資料庫 | SQLite | `data/anticlaude.db` | — |
| AI 模型 | Claude Sonnet 4.6 (主力) / Gemini Flash / GPT-4o | `src/ai/` | — |
| 排程 | APScheduler（內建，無 n8n） | `src/api/main.py` | — |

## src/ 模組地圖

```
src/
├── api/
│   ├── main.py              # FastAPI 入口 + APScheduler (08:00 pipeline / 20:00 tracker / 22:00 night shift)
│   ├── state.py             # 共享全域狀態
│   └── routes/
│       ├── chat.py          # POST /api/chat + deliberate + SSE stream
│       ├── content.py       # pipeline trigger / drafts / topics / weekly
│       ├── review.py        # review_items CRUD + X publish trigger
│       ├── figma.py         # Figma read-only API
│       ├── flowlab.py       # screenshot analyze / video upload
│       ├── workflows.py     # WorkflowRun / ApprovalRequest API
│       ├── agents.py        # agent status / morning report
│       ├── ecommerce_extra.py # auto-flag / performance-history / alerts
│       └── health.py        # /health /api/health

├── agents/
│   ├── ceo.py               # CEO intent router + multi-agent deliberation
│   ├── orchestrator.py      # run_pipeline (legacy linear, still used)
│   ├── dynamic_orchestrator.py # task-type handler dispatch
│   ├── night_shift.py       # 22:00 nightly summary + LINE notify
│   ├── debate.py + judge.py # debate-style content evaluation
│   ├── writer/score/strategy/cluster.py  # thin wrappers over domains/media/

├── ai/
│   ├── claude_writer.py     # shim → src/domains/media/writer.py
│   ├── claude_scorer.py     # shim → src/domains/media/scorer.py
│   ├── gpt_strategist.py    # shim → src/domains/media/strategist.py
│   ├── claude_cluster.py    # Claude-based clustering (Gemini deprecated)
│   ├── competitor_analyzer.py  # Serper + Gemini Flash structured research
│   ├── craft_reporter.py    # selection report generation
│   ├── skill_loader.py      # composite skill .md loader (lru_cache)
│   └── skill_routing.py     # task_type → required_skills mapping

├── adapters/
│   ├── base.py              # AdapterBase + approval gate enforcement
│   ├── x_adapter.py         # X publish (OAuth 1.0a, dry_run=True default)
│   ├── line_adapter.py      # LINE Notify push
│   ├── figma_adapter.py     # Figma read (token extraction deferred)
│   ├── video_adapter.py     # ffmpeg frame extraction (M2, needs ffmpeg binary)
│   ├── chrome_cdp_adapter.py # Playwright CDP (guarded, not exposed in UI)
│   └── registry.py          # adapter metadata / maturity status

├── content/                 # Content intelligence layer (pure Python, no DB deps)
│   ├── geo_validator.py     # GEO hard gate (forbidden words, AI pattern detect)
│   ├── ab_tester.py         # A/B draft comparison
│   ├── topic_fit.py         # topic-audience alignment scorer
│   ├── format_selector.py   # optimal format selection
│   ├── similarity_guard.py  # recent-topic dedup
│   ├── orio_scorer.py       # Ori-style content scoring
│   └── engagement_plan.py   # engagement strategy planner

├── domains/
│   ├── media/
│   │   ├── pipeline_graph.py  # CANONICAL daily content pipeline (GraphRunner)
│   │   ├── writer.py          # Claude draft generation
│   │   ├── scorer.py          # topic scoring with feedback memory
│   │   └── strategist.py      # GPT-4o topic strategy
│   └── flow_lab/
│       ├── selection.py       # ecommerce candidate scoring + analysis
│       └── screenshot_analyzer.py  # image → product extraction

├── workflows/
│   ├── graph.py             # GraphRunner: node execution, approval gates, resume
│   ├── runner.py            # WorkflowRun / Task CRUD
│   ├── approval.py          # ApprovalRequest + _create_inbox_item (CEO mirror)
│   ├── approval_matrix.py   # action → risk_level / requires_human matrix
│   ├── models.py            # WorkflowRun / Task / ApprovalRequest dataclasses
│   ├── events.py            # emit() workflow event log
│   ├── checkpoint_store.py  # build_ceo_package() / resume helpers
│   └── pipeline_graph.py    # shim → domains/media/pipeline_graph.py

├── scrapers/
│   ├── aggregator.py        # multi-source content aggregation
│   ├── rss_scraper.py       # RSS feed
│   ├── serper_scraper.py    # sync Serper (used by aggregator)
│   ├── serper_client.py     # async Serper (used by competitor_tracker)
│   ├── perplexity_scraper.py # Perplexity research
│   ├── hn_scraper.py        # Hacker News
│   └── competitor_tracker.py # price history DB + change_pct + LINE alert

├── db/
│   ├── schema.py            # init_db() — all table DDL
│   ├── queries.py           # save_drafts / save_topics / get_recent_topic_labels
│   └── connection.py        # db() context manager

├── feedback/
│   ├── memory.py            # get_rich_memory_context() — engagement history for prompts
│   └── analysis_engine.py   # run_feedback_analysis() — post-publish metrics ingestion

├── integrations/
│   └── figma_client.py      # async Figma REST client (read-only)

├── publishers/
│   └── x_client.py          # post_tweet / delete_tweet via X API v2 OAuth 1.0a

├── social/
│   └── x_search.py          # X API v2 search / analytics (Bearer token)

├── tracker/
│   ├── threads_client.py    # Threads publish_post()
│   └── metrics_collector.py # engagement metrics collection

├── weekly/
│   └── weekly_report.py     # weekly summary generation

├── office/
│   └── daily_summary.py     # generate_daily_summary() for AI Office

├── registry/
│   └── reader.py            # capability registry reader (lru_cache)

├── utils/
│   ├── notify.py            # send_line_notify()
│   ├── logger.py            # get_logger()
│   ├── file_io.py           # save_daily_md()
│   └── http_client.py       # shared httpx helpers

└── ecommerce/               # shim layer
    ├── router.py            # ecommerce API routes (main router)
    ├── selection.py         # shim → domains/flow_lab/selection.py
    └── seed_from_excel.py   # one-time data seed script
```

## dashboard/ 頁面地圖

```
dashboard/src/app/
├── page.tsx           # 今日總覽（trigger pipeline / draft list）
├── chat/              # CEO Console + Brain 多智能體審議 (SSE streaming)
├── morning/           # 晨報 + 夜班摘要
├── review/            # 審核佇列（Domain Tab: 全部/自媒體/電商）
├── office/            # AI Office（agent status + approval center + deliberation）
├── ecommerce/         # 電商管理（dashboard / products / performance + mini review panel）
├── flowlab/           # Flow Lab 視覺選品（screenshot + video + mini review panel）
├── figma/             # Figma 整合（stats / components / comments / images）
├── calendar/          # 內容日曆
├── picks/             # 精選清單
├── library/           # 素材庫
├── metrics/           # 績效中心
├── insights/          # 受眾洞察
├── reports/           # 週報
└── system/            # 系統日誌
```

## 審核模型語意

```
review_items       = CEO 操作員 inbox（高風險手動決策入口）
                     → /review 頁顯示
                     → Sidebar + TopNav badge 計數來源
                     → 批准 publish_post → 自動觸發 X 發文

approval_requests  = Workflow 內部閘門（GraphRunner 用）
                     → /office Approval Center 顯示
                     → 不重複計入 badge
                     → 高風險動作會 mirror 到 review_items
```

## 每日自動化排程

| 時間 | 任務 |
|------|------|
| 08:00 | 內容 pipeline（research → cluster → score → strategy → draft → CEO inbox） |
| 20:00 | 競品價格追蹤（COMPETITOR_KEYWORDS_RAW env var 須設定） |
| 22:00 | Night Shift（數據快照 + LINE 夜班通知） |

## 外部整合成熟度

| 整合 | 狀態 | 說明 |
|------|------|------|
| LINE Notify | ✅ 生產可用 | token 須設定在 env |
| X Publish | 🟡 已接通 | credentials 已設定，live 模式 |
| Figma Read | ✅ 生產可用 | file key 須設定在 env |
| Video M1 (screenshot) | ✅ 生產可用 | Flow Lab 截圖分析 |
| Video M2/M3 | ⏸ 延後 | ffmpeg 須安裝 |
| Browser/CDP | ⏸ 受控 | 有 adapter，不在 UI 露出 |
| Serper Search | ✅ | sync + async 兩個 client |
