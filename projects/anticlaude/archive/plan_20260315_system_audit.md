# AntiClaude 系統審計報告
> 作者：Claude Code
> 日期：2026-03-15
> 方法：完整 codebase 掃描（50+ 檔案，6,873 行程式碼）

---

## 總體評分：75% 完成度

核心功能紮實，但有幾個「看起來有，其實是空殼」的模組需要注意。

---

## 一、空殼模組（以為有，其實沒用）

### ❌ 最嚴重：Threads 追蹤功能失效

**現象**：你的 Threads 互動率數據可能從未真正拿到過。

| 檔案 | 狀態 |
|------|------|
| `src/tracker/threads_client.py` | 引用不存在的模組 → import 直接失敗 |
| `src/tracker/metrics_collector.py` | `get_recent_posts()` / `get_post_insights()` 沒有真正實作 |
| Token 驗證 | 未實作 |

**影響**：
- Tracker 排程每天 20:00 跑，但拿回來的是空資料
- audience_insights（受眾洞察）沒有真實互動數據
- Sage / Lala 的學習記憶是基於假數據

**修法**：需要真正實作 Threads Graph API 串接

---

### ❌ competitor_analyzer.py — 存在但完全沒接入

**現象**：`src/ai/competitor_analyzer.py` 有 4.3K 程式碼，但沒有任何地方呼叫它。

- 沒有 API endpoint
- 沒有在選品流程中觸發
- Sage 評分時沒有競品數據注入

**影響**：選品分析缺少真實競品比較

---

### ❌ sage_scorer.py / craft_reporter.py — 都是死代碼

兩個檔案存在但從未被呼叫：
- `src/ai/sage_scorer.py`：投資訊號分析，從未觸發
- `src/ai/craft_reporter.py`：選品報告生成，從未觸發
- `investment_log` DB 表存在但從未寫入

---

### ❌ research_cache 表 — 設計了沒用

`research_cache` 在 schema 中存在，但：
- 沒有任何地方寫入
- 沒有任何地方讀取
- 沒有快取失效策略

---

## 二、部分完成（有但不完整）

### ⚠️ Debate Flow（辯論模式）

**現況**：後端 debate.py / judge.py 功能完整，但：
- 前端沒有切換開關
- 無法從 AI Office 啟用
- judge / debate agent 失敗後沒有錯誤恢復

---

### ⚠️ 前端 metrics 頁面

`dashboard/src/app/metrics/page.tsx` 存在但未完整實作：
- 後端 `/api/stats/posts` 只有基本數據
- 應有：日/週/月 ROI、商品績效、趨勢圖
- 目前幾乎是空頁面

---

### ⚠️ 選品 Bundle 功能

`fl_candidates_bundles` 表存在，bundle 建立邏輯存在，但：
- Portfolio 組合演算法未完整測試
- bundle 銷售追蹤未實作

---

## 三、完全缺少的功能

| 功能 | 影響 |
|------|------|
| Threads 自動發文 | 目前需手動複製貼上 |
| A/B 測試框架 | 無法比較兩個版本效果 |
| 草稿預覽 Modal（Threads 格式） | 看不到實際發文樣子 |
| 大量操作（Bulk Actions）| 每次只能改一件商品 |
| 受眾洞察注入 Lala 選題 | 策略選題沒用到真實數據 |
| AI Office Timeline 任務類型篩選 | 活動流沒有過濾器 |
| 競品價格追蹤警示 | 在售商品無自動監控 |
| 週報視覺化（圖表版） | 純文字 markdown |
| 商品生命週期管理 | 只有 active/archived 兩狀態 |

---

## 四、可優化項目

### 高優先（效能）

| 優化點 | 預期改善 | 位置 |
|--------|---------|------|
| Threads 批次 API 呼叫加 `return_exceptions=True` | 快 30-40% | `metrics_collector.py:80` |
| Prompt 快取（目前每次從磁碟讀） | 每次省 10-50ms | 所有 AI 模組 |
| Scraper 逾時機制（單個來源逾時不影響整體）| Pipeline 可靠度提升 | `aggregator.py:26` |
| DB 查詢快取（7 天話題查詢）| 省 2-3ms/次 | `queries.py:64` |

### 中優先（代碼品質）

| 問題 | 位置 |
|------|------|
| `_parse_response()` 重複 6 次 → 應統一到 `src/utils/llm_utils.py` | claude_cluster/scorer/strategist |
| SSE subscriber 在客戶端斷線後沒有清除 → 記憶體洩漏 | `agent_status.py` |
| 全局 `bool` flag 應改為 `asyncio.Lock()` | `src/api/main.py` |
| `google.generativeai` 廢棄警告 → 改 `google.genai` | `competitor_analyzer.py`, `gemini_cluster.py` |

### 低優先（UX）

- Dark mode 切換按鈕（CSS 變數已準備好）
- 草稿預覽 Modal（Threads 文字格式 + 字數）
- 商品批次操作（多選 + 批次調價）
- 匯出 CSV（商品/報告）

---

## 五、優先執行順序

### 立即要做（有破洞）

```
P0 — Threads 追蹤修復
├── 查清楚 threads_client.py import 錯誤的根本原因
├── 實作真正的 get_recent_posts() / get_post_insights()
└── 確認 THREADS_ACCESS_TOKEN 在 .env 且有效
```

### 近期（1-2 週）

```
P1 — 受眾洞察 → Lala 注入 (Gap-1)
P1 — competitor_analyzer 接入選品流程
P1 — Threads 自動發文 (Content-1)
P2 — AI Office Timeline 任務類型篩選 (Gap-2)
```

### 中期（1 個月）

```
P3 — A/B 測試機制
P3 — 週報視覺化
P3 — 競品價格追蹤警示
P3 — metrics 頁面完整實作
```

### 技術債（不急）

```
P4 — asyncio.Lock 取代 bool flag
P4 — google.genai 遷移
P4 — _parse_response 統一
P4 — SSE subscriber 清除
```

---

## 六、給 Claude Code 的執行備註

1. **P0 Threads 追蹤修復**前，先 `cat src/tracker/threads_client.py` 看清楚 import 結構
2. `competitor_analyzer.py` 要接入 `selection.py` 的 `auto-analyze` 流程，在 Sage 評分前執行
3. `sage_scorer.py` / `craft_reporter.py` 要確認是否還有用，或直接清除（死代碼）
4. 每個 P0/P1 項目開始前建對應 `plan_YYYYMMDD_xxx.md`
