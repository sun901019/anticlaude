"""
初始化 SQLite 資料庫 Schema
執行：python -m src.db.schema
"""
from src.db.connection import db
from src.utils.logger import get_logger

log = get_logger("db.schema")

DDL = """
CREATE TABLE IF NOT EXISTS articles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash        TEXT UNIQUE NOT NULL,
    url             TEXT NOT NULL,
    title           TEXT NOT NULL,
    summary         TEXT,
    source          TEXT NOT NULL,
    language        TEXT DEFAULT 'en',
    published_at    DATETIME,
    scraped_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    gemini_cluster  TEXT,
    claude_score    REAL,
    was_used        BOOLEAN DEFAULT 0,
    post_type       TEXT
);
CREATE INDEX IF NOT EXISTS idx_articles_scraped ON articles(scraped_at);
CREATE INDEX IF NOT EXISTS idx_articles_score   ON articles(claude_score DESC);

CREATE TABLE IF NOT EXISTS topics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE NOT NULL,
    cluster_label   TEXT NOT NULL,
    key_insights    TEXT,
    deep_analysis   TEXT,
    category        TEXT,
    score           REAL,
    dimensions      TEXT,
    rank            INTEGER,
    was_posted      BOOLEAN DEFAULT 0,
    article_ids     TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_topics_date     ON topics(date);
CREATE INDEX IF NOT EXISTS idx_topics_category ON topics(category);
CREATE INDEX IF NOT EXISTS idx_topics_label    ON topics(cluster_label);

CREATE TABLE IF NOT EXISTS posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    threads_id      TEXT UNIQUE NOT NULL,
    text            TEXT,
    posted_at       DATETIME,
    topic_id        INTEGER REFERENCES topics(id),
    category        TEXT,
    post_type       TEXT,
    views           INTEGER DEFAULT 0,
    likes           INTEGER DEFAULT 0,
    replies         INTEGER DEFAULT 0,
    reposts         INTEGER DEFAULT 0,
    quotes          INTEGER DEFAULT 0,
    engagement_rate REAL DEFAULT 0,
    metrics_updated_at DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_posts_posted     ON posts(posted_at);
CREATE INDEX IF NOT EXISTS idx_posts_category   ON posts(category);
CREATE INDEX IF NOT EXISTS idx_posts_engagement ON posts(engagement_rate DESC);

CREATE TABLE IF NOT EXISTS drafts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE NOT NULL,
    topic_id        INTEGER REFERENCES topics(id),
    version         INTEGER DEFAULT 1,
    style           TEXT,
    content         TEXT NOT NULL,
    hook            TEXT,
    hashtags        TEXT,
    was_selected    BOOLEAN DEFAULT 0,
    post_id         INTEGER REFERENCES posts(id),
    published_at    DATETIME,                          -- Threads 發文時間
    threads_post_id TEXT,                             -- Threads 回傳的貼文 ID
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audience_insights (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_date   DATE NOT NULL,
    period_days     INTEGER DEFAULT 30,
    category_performance TEXT,
    best_posting_day    TEXT,
    best_posting_hour   INTEGER,
    top_performing_hooks TEXT,
    avg_optimal_length  INTEGER,
    effective_hashtags  TEXT,
    growth_rate         REAL,
    engagement_trend    TEXT,
    strategic_summary   TEXT,
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_cache (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash    TEXT UNIQUE NOT NULL,
    url         TEXT NOT NULL,
    title       TEXT,
    analysis    TEXT,       -- Ori 的分析結論
    tags        TEXT,       -- JSON array（主題標籤）
    relevance   REAL,       -- 相關度評分（1-10）
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_research_analyzed ON research_cache(analyzed_at);

CREATE TABLE IF NOT EXISTS investment_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    log_date        DATE NOT NULL,
    market          TEXT NOT NULL,  -- US / crypto / TW
    ticker          TEXT,           -- 個股/幣種代碼（選填）
    signal          TEXT,           -- 訊號描述（一句話）
    analysis        TEXT,           -- Sage 的完整分析
    outcome         TEXT,           -- 事後結果（空 = 待觀察）
    was_correct     BOOLEAN,        -- 分析正確？（空 = 待驗證）
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_investment_date   ON investment_log(log_date);
CREATE INDEX IF NOT EXISTS idx_investment_market ON investment_log(market);

-- ===== Flow Lab 電商模組 =====

CREATE TABLE IF NOT EXISTS fl_products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    product_type    TEXT,
    scene           TEXT,
    keyword         TEXT,
    role            TEXT,               -- 引流款 | 毛利款 | 主力款（人工確認後的正式角色）
    role_confirmed  INTEGER DEFAULT 0,  -- 0=AI建議未確認, 1=人工已確認
    market_price_low  REAL,
    market_price_high REAL,
    supplier        TEXT,
    cost_rmb        REAL,               -- 1688 商品本身單價，不含任何運費（人民幣）
    head_freight_rmb REAL DEFAULT 0,    -- 中國→台灣頭程運費，按件攤算（人民幣）
    cost_twd        REAL,               -- 自動計算：(cost_rmb + head_freight_rmb) × 匯率
    target_price    REAL,
    freight_type    TEXT DEFAULT 'sea_fast',  -- air / sea_fast / sea_regular
    is_special_goods INTEGER DEFAULT 0,        -- 1=特貨（帶電/磁/液體）
    ccb_plan        TEXT DEFAULT 'none',       -- none / ccb5 / ccb10
    is_promo_day    INTEGER DEFAULT 0,         -- 1=促銷日建檔
    fulfillment_days INTEGER DEFAULT 1,        -- 備貨天數（>2天觸發 +3% 罰款）
    procurement_mode TEXT DEFAULT 'standard_1688', -- standard_1688 / qql_agent
    length_cm       REAL,                      -- 尺寸（QQL 體積重計算用）
    width_cm        REAL,
    height_cm       REAL,
    status          TEXT DEFAULT 'active',
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fl_products_sku  ON fl_products(sku);
CREATE INDEX IF NOT EXISTS idx_fl_products_role ON fl_products(role);

CREATE TABLE IF NOT EXISTS fl_inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT NOT NULL REFERENCES fl_products(sku),
    purchase_date   DATE,
    cost_rmb        REAL NOT NULL,
    exchange_rate   REAL DEFAULT 4.5,
    cost_twd        REAL,
    quantity        INTEGER NOT NULL,
    lead_days       INTEGER,
    supplier        TEXT,
    batch_note      TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fl_inventory_sku  ON fl_inventory(sku);
CREATE INDEX IF NOT EXISTS idx_fl_inventory_date ON fl_inventory(purchase_date);

CREATE TABLE IF NOT EXISTS fl_performance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT NOT NULL REFERENCES fl_products(sku),
    record_date     DATE NOT NULL,
    current_price   REAL,
    sales_7d        INTEGER DEFAULT 0,
    revenue_7d      REAL DEFAULT 0,
    ad_spend_7d     REAL DEFAULT 0,
    current_stock   INTEGER DEFAULT 0,
    roas            REAL,
    gross_profit    REAL,
    gross_margin    REAL,
    next_action     TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fl_perf_sku  ON fl_performance(sku);
CREATE INDEX IF NOT EXISTS idx_fl_perf_date ON fl_performance(record_date);

CREATE TABLE IF NOT EXISTS fl_settings (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL,
    label           TEXT,
    unit            TEXT,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fl_decisions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT,
    product_name    TEXT NOT NULL,
    analysis_date   DATE NOT NULL,
    financials      TEXT,
    recommended_role TEXT,
    decision_status TEXT DEFAULT '待決定',
    sage_analysis   TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fl_decisions_date   ON fl_decisions(analysis_date);
CREATE INDEX IF NOT EXISTS idx_fl_decisions_status ON fl_decisions(decision_status);

CREATE TABLE IF NOT EXISTS fl_product_relations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT NOT NULL REFERENCES fl_products(sku),
    related_sku     TEXT,               -- 若是已上架商品填 sku
    related_name    TEXT,               -- 若是未上架商品填名稱
    relation_type   TEXT NOT NULL,      -- bundle | cross_sell | upsell | scene_partner
    scene           TEXT,               -- 共同場景：辦公室午休 / 桌面整潔 / ...
    is_bundle_candidate INTEGER DEFAULT 0,
    notes           TEXT,
    bundle_status   TEXT DEFAULT 'draft',  -- draft | testing | active | rejected
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_fl_relations_sku  ON fl_product_relations(sku);
CREATE INDEX IF NOT EXISTS idx_fl_relations_type ON fl_product_relations(relation_type);

-- ===== Flow Lab 選品引擎（Product Intelligence System）=====
-- 語意說明：
--   fl_decisions               → 已上架 SKU 的定價/補貨決策
--   ecommerce_selection_*      → 新品候選的評估、分析、記憶（不同 lifecycle）

CREATE TABLE IF NOT EXISTS ecommerce_selection_candidates (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id        TEXT UNIQUE NOT NULL,   -- 自生成 UUID
    product_name        TEXT NOT NULL,
    market_type         TEXT,                   -- demand | trend | problem | hybrid
    market_confidence   REAL,                   -- 0-1
    source_platform     TEXT,                   -- tiktok | shopee | taobao | amazon | instagram | manual
    source_url          TEXT,
    category            TEXT,
    keywords_json       TEXT,                   -- JSON array
    risk_flags_json     TEXT,                   -- JSON array: fragile/ip/complex_electronics/...
    risk_score          REAL,
    status              TEXT DEFAULT 'candidate', -- candidate | shortlisted | approved | rejected
    selection_status    TEXT DEFAULT 'evaluating', -- evaluating | viable | rejected | watchlist
    launch_status       TEXT DEFAULT 'not_ready',  -- not_ready | ready | launched
    discovery_notes     TEXT,
    created_by_agent    TEXT DEFAULT 'ori',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sel_cand_status    ON ecommerce_selection_candidates(status);
CREATE INDEX IF NOT EXISTS idx_sel_cand_market    ON ecommerce_selection_candidates(market_type);
CREATE INDEX IF NOT EXISTS idx_sel_cand_platform  ON ecommerce_selection_candidates(source_platform);

CREATE TABLE IF NOT EXISTS ecommerce_selection_analyses (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id            TEXT NOT NULL REFERENCES ecommerce_selection_candidates(candidate_id),
    analysis_date           DATE NOT NULL,
    -- 各維度評分 (1-10)
    demand_score            REAL,
    competition_score       REAL,
    profit_score            REAL,
    pain_point_score        REAL,
    brand_fit_score         REAL,
    -- 加權總分：demand*2 + profit*2 + pain_points + competition + brand_fit
    score_total             REAL,
    score_breakdown_json    TEXT,   -- {"demand":8,"profit":7,...,"formula":"..."}
    viability_band          TEXT,   -- strong | viable | watchlist | reject
    -- 市場 / 競品 / 財務明細
    market_metrics_json     TEXT,   -- demand_stability, trend_curve, ...
    competition_metrics_json TEXT,  -- competitor_count, price_ladder_health, ...
    negative_reviews_json   TEXT,   -- [{pain_point, frequency, opportunity}]
    financials_json         TEXT,   -- landed_cost, min_price, target_price, gross_margin, break_even_roas
    -- 角色建議
    recommended_role        TEXT,   -- 引流款 | 毛利款 | 主力款
    role_confidence         REAL,
    role_reasoning          TEXT,
    -- 決策
    next_steps_json         TEXT,   -- {"recommendation":"建議進樣","confidence":"高","reasons":[...],"next_steps":[...],"warnings":[...]}
    decision_status         TEXT DEFAULT '待評估', -- 待評估 | 通過 | 拒絕 | 觀察
    reasoning               TEXT,
    analyzed_by_agent       TEXT DEFAULT 'sage',
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sel_anal_candidate ON ecommerce_selection_analyses(candidate_id);
CREATE INDEX IF NOT EXISTS idx_sel_anal_date      ON ecommerce_selection_analyses(analysis_date);
CREATE INDEX IF NOT EXISTS idx_sel_anal_score     ON ecommerce_selection_analyses(score_total DESC);

CREATE TABLE IF NOT EXISTS ecommerce_selection_reports (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id         INTEGER REFERENCES ecommerce_selection_analyses(id),
    candidate_id        TEXT REFERENCES ecommerce_selection_candidates(candidate_id),
    report_title        TEXT NOT NULL,
    report_markdown     TEXT,
    summary_json        TEXT,   -- {"score":42,"role":"毛利款","top_pain_points":[...],...}
    created_by_agent    TEXT DEFAULT 'craft',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sel_report_candidate ON ecommerce_selection_reports(candidate_id);

CREATE TABLE IF NOT EXISTS ecommerce_selection_lessons (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    theme                   TEXT NOT NULL,          -- 重複出現的主題
    lesson_type             TEXT NOT NULL,          -- rejection_pattern | winning_pattern | margin_rule | brand_rule
    lesson_text             TEXT NOT NULL,
    source_analysis_ids_json TEXT,                  -- JSON array of analysis ids
    confidence              REAL DEFAULT 0.5,       -- 0-1
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sel_lesson_type  ON ecommerce_selection_lessons(lesson_type);
CREATE INDEX IF NOT EXISTS idx_sel_lesson_theme ON ecommerce_selection_lessons(theme);

CREATE TABLE IF NOT EXISTS ecommerce_selection_bundles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    bundle_name         TEXT NOT NULL,
    scene               TEXT,                   -- 使用情境：辦公舒適 / 睡眠改善 / ...
    description         TEXT,
    candidate_ids_json  TEXT NOT NULL,           -- JSON array of candidate_ids
    product_names_json  TEXT,                    -- JSON array（顯示用）
    role_composition    TEXT,                    -- 引流+毛利 / 引流+主力 / 毛利+主力
    base_price_sum      REAL,                    -- 各品單售總和
    bundle_price        REAL,                    -- 組合包建議售價
    discount_pct        REAL,                    -- 折扣比例 0-1
    estimated_margin    REAL,                    -- 組合包預估毛利率
    margin_vs_separate  REAL,                    -- 對比分開銷售的毛利率差
    suggestion_reason   TEXT,                    -- AI 推薦理由
    status              TEXT DEFAULT 'suggested', -- suggested | approved | rejected
    created_by_agent    TEXT DEFAULT 'lala',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sel_bundle_scene  ON ecommerce_selection_bundles(scene);
CREATE INDEX IF NOT EXISTS idx_sel_bundle_status ON ecommerce_selection_bundles(status);

-- ===== Review Queue =====

-- ===== Workflow Runtime（Phase 2）=====

CREATE TABLE IF NOT EXISTS workflow_runs (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    domain          TEXT NOT NULL DEFAULT 'media',
    status          TEXT NOT NULL DEFAULT 'pending',
    context_json    TEXT,
    started_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME,
    error           TEXT
);
CREATE INDEX IF NOT EXISTS idx_wf_runs_status ON workflow_runs(status);
CREATE INDEX IF NOT EXISTS idx_wf_runs_domain ON workflow_runs(domain);
CREATE INDEX IF NOT EXISTS idx_wf_runs_started ON workflow_runs(started_at DESC);

CREATE TABLE IF NOT EXISTS workflow_tasks (
    id              TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES workflow_runs(id),
    agent           TEXT NOT NULL,
    task_type       TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    input_json      TEXT,
    output_json     TEXT,
    error           TEXT,
    started_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at    DATETIME
);
CREATE INDEX IF NOT EXISTS idx_wf_tasks_run    ON workflow_tasks(run_id);
CREATE INDEX IF NOT EXISTS idx_wf_tasks_status ON workflow_tasks(status);
CREATE INDEX IF NOT EXISTS idx_wf_tasks_agent  ON workflow_tasks(agent);

CREATE TABLE IF NOT EXISTS workflow_events (
    id              TEXT PRIMARY KEY,
    run_id          TEXT NOT NULL,
    task_id         TEXT,
    event_type      TEXT NOT NULL,
    payload_json    TEXT,
    timestamp       DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wf_events_run  ON workflow_events(run_id);
CREATE INDEX IF NOT EXISTS idx_wf_events_type ON workflow_events(event_type);
CREATE INDEX IF NOT EXISTS idx_wf_events_time ON workflow_events(timestamp DESC);

CREATE TABLE IF NOT EXISTS artifacts (
    id              TEXT PRIMARY KEY,
    run_id          TEXT,
    task_id         TEXT,
    artifact_type   TEXT NOT NULL,
    producer        TEXT NOT NULL,
    file_path       TEXT,
    db_ref          TEXT,
    metadata_json   TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_artifacts_run    ON artifacts(run_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type   ON artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_producer ON artifacts(producer);
CREATE INDEX IF NOT EXISTS idx_artifacts_created ON artifacts(created_at DESC);

CREATE TABLE IF NOT EXISTS approval_requests (
    id              TEXT PRIMARY KEY,
    run_id          TEXT,
    task_id         TEXT,
    action          TEXT NOT NULL,
    risk_level      TEXT DEFAULT 'medium',
    evidence_json   TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    decided_at      DATETIME,
    decision_note   TEXT
);
CREATE INDEX IF NOT EXISTS idx_approvals_status  ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approvals_run     ON approval_requests(run_id);
CREATE INDEX IF NOT EXISTS idx_approvals_risk    ON approval_requests(risk_level);

-- ===== Flow Lab Screenshot Analysis =====

CREATE TABLE IF NOT EXISTS flowlab_screenshot_analyses (
    id              TEXT PRIMARY KEY,
    image_path      TEXT,
    extraction_json TEXT NOT NULL,
    shopee_draft    TEXT,
    threads_draft   TEXT,
    approval_id     TEXT,
    artifact_id     TEXT,
    status          TEXT NOT NULL DEFAULT 'pending',
    context         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_flowlab_screenshots_status  ON flowlab_screenshot_analyses(status);
CREATE INDEX IF NOT EXISTS idx_flowlab_screenshots_created ON flowlab_screenshot_analyses(created_at DESC);

-- ===== Flow Lab Video Analysis (M1) =====

CREATE TABLE IF NOT EXISTS flowlab_video_analyses (
    id                  TEXT PRIMARY KEY,
    video_path          TEXT NOT NULL,          -- relative path: data/uploads/videos/{uuid}.{ext}
    original_filename   TEXT,
    duration_secs       REAL,                   -- filled after frame extraction
    keyframe_paths_json TEXT,                   -- JSON array of extracted frame paths
    transcript          TEXT,                   -- filled by transcription step (optional)
    extracted_products  TEXT,                   -- JSON array of {name, price_hint, platform_hint}
    threads_draft       TEXT,                   -- AI-generated Threads post
    approval_id         TEXT,
    artifact_id         TEXT,
    status              TEXT NOT NULL DEFAULT 'processing',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_flowlab_videos_status  ON flowlab_video_analyses(status);
CREATE INDEX IF NOT EXISTS idx_flowlab_videos_created ON flowlab_video_analyses(created_at DESC);

-- ===== Review Queue =====

CREATE TABLE IF NOT EXISTS review_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_type       TEXT NOT NULL,      -- content | product | architecture | strategy | integration
    question        TEXT NOT NULL,
    context         TEXT,
    options_json    TEXT,               -- JSON array of {label, consequence}
    recommended     TEXT,
    reason          TEXT,
    related_agents  TEXT,               -- JSON array of agent ids
    deadline        DATE,
    default_action  TEXT,
    status          TEXT DEFAULT 'pending',  -- pending | approved | rejected | deferred
    decision_by     TEXT,
    decision_at     DATETIME,
    decision_note   TEXT,
    created_by      TEXT,               -- agent id that created this item
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_review_status     ON review_items(status);
CREATE INDEX IF NOT EXISTS idx_review_type       ON review_items(item_type);
CREATE INDEX IF NOT EXISTS idx_review_created    ON review_items(created_at);
CREATE INDEX IF NOT EXISTS idx_review_created_by ON review_items(created_by);
CREATE INDEX IF NOT EXISTS idx_review_status_by  ON review_items(status, created_by);

CREATE TABLE IF NOT EXISTS notification_dispatches (
    signature       TEXT PRIMARY KEY,
    channel         TEXT NOT NULL,
    event_type      TEXT,
    ref_id          TEXT,
    payload_json    TEXT,
    last_sent_at    TEXT NOT NULL,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notification_dispatches_channel ON notification_dispatches(channel);
CREATE INDEX IF NOT EXISTS idx_notification_dispatches_sent_at ON notification_dispatches(last_sent_at);
"""


def init_db():
    with db() as conn:
        conn.executescript(DDL)
        # migrations for existing databases
        try:
            conn.execute("ALTER TABLE fl_product_relations ADD COLUMN bundle_status TEXT DEFAULT 'draft'")
        except Exception:
            pass
    log.info("DB schema 初始化完成")


if __name__ == "__main__":
    init_db()
    print("✓ anticlaude.db 初始化完成")
