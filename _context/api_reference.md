# API 對照表

## 一、資料來源 API

### RSS Feeds（免費，無需 API Key）
| 來源 | Feed URL | 類型 | 更新頻率 |
|------|---------|------|---------|
| TechCrunch | `https://techcrunch.com/feed/` | 科技新聞 | 即時 |
| VentureBeat | `https://venturebeat.com/feed/` | AI 創投新聞 | 即時 |
| The Verge | `https://www.theverge.com/rss/index.xml` | 科技媒體 | 即時 |
| AI News | `https://www.artificialintelligence-news.com/feed/` | AI 專門媒體 | 每日 |

### Serper API（Google 新聞搜尋）
| 欄位 | 值 |
|------|---|
| Endpoint | `https://google.serper.dev/news` |
| 方法 | `POST` |
| Header | `X-API-KEY: <SERPER_API_KEY>` |
| 英文查詢 | `{ "q": "AI tools 2026", "gl": "us", "num": 10 }` |
| 中文查詢 | `{ "q": "AI 工具 2026", "gl": "tw", "hl": "zh-TW", "num": 10 }` |
| 費率 | 免費 2,500 次/月 |

### Perplexity API（即時熱門話題）
| 欄位 | 值 |
|------|---|
| Endpoint | `https://api.perplexity.ai/chat/completions` |
| 方法 | `POST` |
| Header | `Authorization: Bearer <PPLX_API_KEY>` |
| Model | `sonar` |
| 用途 | Prompt 中要求搜尋今日 AI 熱門話題 Top 5 |

### Hacker News API（免費，無需 Key）
| 欄位 | 值 |
|------|---|
| Top Stories | `https://hacker-news.firebaseio.com/v0/topstories.json` |
| 單篇詳情 | `https://hacker-news.firebaseio.com/v0/item/{id}.json` |
| 搜尋（Algolia） | `https://hn.algolia.com/api/v1/search?query=AI&tags=story&numericFilters=created_at_i>{timestamp}` |

---

## 二、AI 模型 API

### Gemini 2.0 Flash（聚類去重）
| 欄位 | 值 |
|------|---|
| Endpoint | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent` |
| 方法 | `POST` |
| Header | `x-goog-api-key: <GEMINI_API_KEY>` |
| 定價 | 輸入 $0.10/1M tokens · 輸出 $0.40/1M tokens |

### Claude Sonnet（評分 + 文案）
| 欄位 | 值 |
|------|---|
| Endpoint | `https://api.anthropic.com/v1/messages` |
| 方法 | `POST` |
| Headers | `x-api-key: <ANTHROPIC_API_KEY>`, `anthropic-version: 2023-06-01` |
| Model | `claude-sonnet-4-6` |
| 定價 | 輸入 $3/1M tokens · 輸出 $15/1M tokens |

### GPT-4o（策略分析）
| 欄位 | 值 |
|------|---|
| Endpoint | `https://api.openai.com/v1/chat/completions` |
| 方法 | `POST` |
| Header | `Authorization: Bearer <OPENAI_API_KEY>` |
| Model | `gpt-4o` |
| 定價 | 輸入 $2.50/1M tokens · 輸出 $10/1M tokens |

---

## 三、Threads Graph API（數據追蹤）

| 欄位 | 值 |
|------|---|
| Base URL | `https://graph.threads.net/v1.0` |
| App ID | `2047745122833004` |
| App 名稱 | `threads-tracker` |
| OAuth | 需要 Long-lived Token（60 天有效） |

### 常用 Endpoints

| 操作 | Method | URL |
|------|--------|-----|
| 取得我的資料 | `GET` | `/me?fields=id,username,threads_profile_picture_url&access_token={TOKEN}` |
| 取得近期貼文 | `GET` | `/me/threads?fields=id,text,timestamp,media_type&access_token={TOKEN}` |
| 單篇貼文數據 | `GET` | `/{post_id}/insights?metric=views,likes,replies,reposts,quotes&access_token={TOKEN}` |

### 抓取資料欄位
| 指標 | API 欄位 | 說明 |
|------|---------|------|
| 觀看數 | `views` | 貼文被看到的次數 |
| 按讚數 | `likes` | 按讚次數 |
| 回覆數 | `replies` | 留言數 |
| 轉發數 | `reposts` | 轉發次數 |
| 引用數 | `quotes` | 引用次數 |
| 互動率 | 自行計算 | `(likes + replies + reposts + quotes) / views × 100` |

---

## 四、環境變數清單

```env
# === 資料來源 ===
SERPER_API_KEY=
PPLX_API_KEY=

# === AI 模型 ===
GEMINI_API_KEY=
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# === Threads ===
THREADS_APP_ID=2047745122833004
THREADS_ACCESS_TOKEN=
THREADS_USER_ID=

# === 可選 ===
NOTEBOOKLM_API_KEY=
```
