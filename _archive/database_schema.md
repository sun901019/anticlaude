# 資料庫架構 — SQLite Schema

> 支援閉環系統（Closed-Loop）：數據回饋 → 越來越懂受眾

## 閉環流程

```
                    ┌──────────────────────┐
                    │   ① 抓取素材         │
                    │   RSS / Serper / HN   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   ② Gemini 分析      │◄─── 歷史主題（避免重複）
                    │   聚類 + 去重 + 深度  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
            ┌──────│   ③ Claude 評分      │◄─── 受眾偏好模型 ★
            │      │   受眾匹配度 1-10     │     （從歷史數據學到的）
            │      └──────────┬───────────┘
            │                 │
            │                 ▼
            │      ┌──────────────────────┐
            │      │   ④ GPT 策略         │◄─── 歷史表現數據 ★
            │      │   選 Top 3 + 文案     │     （哪類話題最受歡迎）
            │      └──────────┬───────────┘
            │                 │
            │                 ▼
            │      ┌──────────────────────┐
            │      │   ⑤ 發佈到 Threads   │
            │      │   （手動複製貼上）     │
            │      └──────────┬───────────┘
            │                 │
            │                 ▼
            │      ┌──────────────────────┐
            │      │   ⑥ 抓取表現數據     │
            │      │   觀看/按讚/互動率    │
            │      └──────────┬───────────┘
            │                 │
            │                 ▼
            │      ┌──────────────────────┐
            └─────►│   ⑦ 回饋分析引擎     │ ★ 閉環核心
                   │   更新受眾偏好模型    │
                   │   學習什麼內容有效    │
                   └──────────────────────┘
```

## 資料庫檔案
`data/anticlaude.db`（SQLite）

---

## Tables

### `articles` — 所有抓過的素材（+ 去重基礎）
```sql
CREATE TABLE articles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    url_hash        TEXT UNIQUE NOT NULL,        -- SHA-256(url)，快速去重
    url             TEXT NOT NULL,
    title           TEXT NOT NULL,
    summary         TEXT,
    source          TEXT NOT NULL,               -- techcrunch / serper_en / hackernews...
    language        TEXT DEFAULT 'en',           -- en / zh-TW
    published_at    DATETIME,
    scraped_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    gemini_cluster  TEXT,                        -- 被歸到哪個主題群
    claude_score    REAL,                        -- 受眾匹配度 1-10
    was_used        BOOLEAN DEFAULT 0,           -- 是否被選為 Top 3
    post_type       TEXT                         -- AI工具實測 / 趨勢解讀 / 職涯觀點 / 個人成長
);
CREATE INDEX idx_articles_scraped ON articles(scraped_at);
CREATE INDEX idx_articles_score ON articles(claude_score DESC);
```

### `topics` — 已處理過的主題（語意去重 + 閉環追蹤）
```sql
CREATE TABLE topics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE NOT NULL,               -- 產出日期
    cluster_label   TEXT NOT NULL,               -- 主題名稱
    key_insights    TEXT,                        -- JSON: 關鍵觀點列表
    deep_analysis   TEXT,                        -- Gemini 深度分析
    category        TEXT,                        -- 主題類別
    score           REAL,                        -- Claude 評分
    rank            INTEGER,                     -- 當日排名（1=Top）
    was_posted      BOOLEAN DEFAULT 0,           -- 是否真的發了
    article_ids     TEXT,                        -- JSON: 關聯的 article IDs
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_topics_date ON topics(date);
CREATE INDEX idx_topics_category ON topics(category);
```

### `posts` — Threads 貼文 + 表現數據
```sql
CREATE TABLE posts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    threads_id      TEXT UNIQUE NOT NULL,         -- Threads 貼文 ID
    text            TEXT,                         -- 貼文內容
    posted_at       DATETIME,                    -- 發佈時間
    topic_id        INTEGER REFERENCES topics(id), -- 關聯到哪個主題
    category        TEXT,                        -- 主題類別
    post_type       TEXT,                        -- AI工具實測 / 趨勢解讀...
    -- 表現指標（每次抓取時更新）
    views           INTEGER DEFAULT 0,
    likes           INTEGER DEFAULT 0,
    replies         INTEGER DEFAULT 0,
    reposts         INTEGER DEFAULT 0,
    quotes          INTEGER DEFAULT 0,
    engagement_rate REAL DEFAULT 0,              -- 自動計算
    -- 時間戳
    metrics_updated_at DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_posts_posted ON posts(posted_at);
CREATE INDEX idx_posts_category ON posts(category);
CREATE INDEX idx_posts_engagement ON posts(engagement_rate DESC);
```

### `audience_insights` — 受眾偏好模型（閉環核心 ★）
```sql
CREATE TABLE audience_insights (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_date   DATE NOT NULL,               -- 分析日期
    period_days     INTEGER DEFAULT 30,          -- 分析區間（天）
    -- 主題類別表現
    category_performance TEXT,                   -- JSON: { "AI工具實測": { avg_views, avg_engagement, count } }
    -- 時間規律
    best_posting_day    TEXT,                    -- 最佳發文日（週幾）
    best_posting_hour   INTEGER,                -- 最佳發文時段
    -- 內容模式
    top_performing_hooks TEXT,                   -- JSON: 高互動貼文的 Hook 模式
    avg_optimal_length  INTEGER,                -- 最佳貼文長度
    effective_hashtags   TEXT,                   -- JSON: 高互動率的 hashtag
    -- 趨勢
    growth_rate         REAL,                   -- 觀看數成長率 %
    engagement_trend    TEXT,                    -- up / stable / down
    -- AI 生成的建議
    strategic_summary   TEXT,                    -- GPT 產出的策略摘要
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### `drafts` — 生成過的文案記錄
```sql
CREATE TABLE drafts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            DATE NOT NULL,
    topic_id        INTEGER REFERENCES topics(id),
    version         INTEGER DEFAULT 1,           -- 同主題第幾版
    content         TEXT NOT NULL,               -- 文案全文
    hook            TEXT,                        -- 第一句 Hook
    hashtags        TEXT,                        -- JSON: hashtag 列表
    was_selected    BOOLEAN DEFAULT 0,           -- 是否被選中發佈
    post_id         INTEGER REFERENCES posts(id), -- 發佈後關聯
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 閉環查詢範例

### 「過去 30 天，哪類主題互動率最高？」
```sql
SELECT category,
       COUNT(*) as post_count,
       ROUND(AVG(engagement_rate), 2) as avg_engagement,
       ROUND(AVG(views), 0) as avg_views
FROM posts
WHERE posted_at >= date('now', '-30 days')
GROUP BY category
ORDER BY avg_engagement DESC;
```

### 「週幾發文效果最好？」
```sql
SELECT CASE strftime('%w', posted_at)
         WHEN '0' THEN '週日' WHEN '1' THEN '週一'
         WHEN '2' THEN '週二' WHEN '3' THEN '週三'
         WHEN '4' THEN '週四' WHEN '5' THEN '週五'
         WHEN '6' THEN '週六'
       END as day_of_week,
       ROUND(AVG(engagement_rate), 2) as avg_engagement,
       COUNT(*) as posts
FROM posts
GROUP BY strftime('%w', posted_at)
ORDER BY avg_engagement DESC;
```

### 「這個主題過去 7 天有人發過嗎？」（去重）
```sql
SELECT cluster_label, date, score
FROM topics
WHERE date >= date('now', '-7 days')
  AND cluster_label LIKE '%' || ? || '%';
```

### 「哪種 Hook 開頭互動最高？」
```sql
SELECT d.hook,
       p.engagement_rate,
       p.views
FROM drafts d
JOIN posts p ON d.post_id = p.id
WHERE d.was_selected = 1
ORDER BY p.engagement_rate DESC
LIMIT 10;
```
