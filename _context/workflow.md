# 工作流程 — 每日 / 每週手動觸發

> 所有流程透過 Next.js 儀表板上的按鈕手動觸發。打開 → 按一下 → 等結果。

## 每日流程（手動觸發）

```
🔘 按「抓取素材」─── 資料抓取 ─────────────────────────
          │
          ├─ RSS 訂閱：TechCrunch, VentureBeat, The Verge, AI News
          ├─ Serper API：Google 新聞（EN + ZH 各 10 筆）
          ├─ Perplexity API：即時熱門 AI 話題 Top 5
          └─ Hacker News API：前一天 Top 20 AI 相關討論
          │
          ▼
🔘 按「AI 分析」─── Gemini 深度分析 ──────────────────────
          │
          └─ Gemini 2.0 Flash（大 Context Window，一次吃全部素材）
                ① 聚類去重：合併同主題不同來源
                ② 深度分析：歸納關鍵觀點、影響、潛在角度
                ③ 輸出：15-20 則精華主題
          │
          ▼
     ─── Claude 評分 + 文案 ─────────────────────────────
          │
          ├─ Claude Sonnet → 受眾匹配度評分 1-10
          │     輸入：精華主題 + about_me.md
          │
          └─ Claude Sonnet → 繁中文案（每個主題 2 版本）
                輸入：Top 3 主題 + about_me.md 語氣規範
                輸出：可直接複製貼上的 Threads 貼文
          │
          ▼
     ─── GPT 策略建議 ───────────────────────────────────
          │
          └─ GPT-4o → 結合 Threads 數據選 Top 3 + 理由
          │
          ▼
🔘 按「抓 Threads 數據」─── 數據追蹤 ───────────────────
          │
          └─ Threads Graph API
                抓取：所有貼文的觀看 / 按讚 / 回覆 / 轉發 / 引用
                寫入：outputs/threads_metrics/YYYY-MM-DD.json
```

## 每週流程（手動觸發「生成週報」按鈕）

```
🔘 按「生成週報」───────────────────────────────────────
  │
  ├─ 整合 7 天的 daily_reports + threads_metrics
  │
  └─ GPT-4o 生成週報
        ├─ 本週最佳 / 最差貼文分析
        ├─ 觀眾偏好趨勢
        └─ 下週內容策略建議
        │
        ▼
  輸出：outputs/weekly_reports/week_YYYY-WW.md
```

## AI 模型分工原則

| 模型 | 角色 | 為什麼用它 | 成本考量 |
|------|------|-----------|---------|
| Gemini 2.0 Flash | **分析引擎** | 大 Context Window，聚類+去重+深度分析一次搞定 | 最便宜 |
| Claude Sonnet | 內容創作者 | 最懂繁中語感，Hook 最自然 | 中等，用在刀口 |
| GPT-4o | 策略顧問 | 結構性分析強，大局觀 | 中等 |
| Perplexity | 新聞雷達 | 即時搜尋，最新消息 | API 計次 |

## 操作方式
1. **打開儀表板**：`cd dashboard && npm run dev` → http://localhost:3000
2. **按「🚀 一鍵全部跑」**：系統跑完抓取 → 分析 → 文案，約 2-3 分鐘
3. **看今日總覽**：Top 3 主題 + 6 篇文案，選一版 → 一鍵複製 → 貼到 Threads
4. **按「📊 抓 Threads 數據」**：抓最新貼文數據
5. **週末按「📋 生成週報」**：看下週策略建議
