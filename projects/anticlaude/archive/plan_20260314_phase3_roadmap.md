# AntiClaude — Phase 3 升級路線圖
> 作者：Claude Code
> 日期：2026-03-14
> 前提：P1/P2 已完成（awaiting_human / Flow Lab 5 tabs / 測試套件）

---

## 系統現況總結

```
已完成
├── AI Agency 6 層框架          ✅
├── AI Office 即時狀態          ✅
├── awaiting_human 決策提示     ✅
├── Flow Lab Dashboard 5 tabs  ✅
├── 事件驅動 Agent 啟動         ✅
├── 測試套件 49/50 通過         ✅
└── 每日摘要自動產出            ✅

尚未完成
├── Ori 真正搜尋競品（目前只是示意）
├── Sage 自動評分（目前手動填數字）
├── Craft 自動產選品報告
├── Threads 數據自動閉環
├── 雲端部署
└── 通知系統
```

---

## 待修正（Codex 執行，小改動）

### Fix-1：修正 test_serper.py 過時斷言

**檔案**：`tests/test_serper.py` 第 22 行

```python
# 改前
assert len(results) == 4  # 2 queries × 2 results

# 改後
assert len(results) > 0  # query 數量可能變動，只確認有結果
```

原因：Serper 現在跑 5 個 query，測試還寫著舊的 2 個 query 預期值。

---

## 第一優先：讓 AI 真正工作

> 這是整個 Phase 3 最有價值的升級。
> 做完後「新增候選商品」就真的是 Ori 去網路搜，Sage 自動評分，Craft 自動寫報告。你只需要看結果做決定。

---

### 升級 A：Ori 真正搜尋競品

**現況**：`_emit_ori()` 只是顯示狀態，沒有真正搜尋。

**目標**：點「開始分析」後，Ori 真的用 Serper API 搜尋競品資料。

**實作位置**：`src/ecommerce/selection.py`，`analyze_candidate` 函數

**新增邏輯**：

```python
# 在 _emit_ori("working", ...) 之後，真正搜尋
async def _ori_research_competitor(product_name: str, category: str) -> dict:
    """
    Ori 的競品研究：用 Serper 搜尋蝦皮熱銷 + 負評 + 市場信號
    回傳結構化競品資料供 Sage 評分使用
    """
    from src.scrapers.serper_scraper import fetch_serper

    queries = [
        f"{product_name} 蝦皮 熱銷",
        f"{product_name} 評價 缺點",
        f"{product_name} site:shopee.tw",
    ]

    raw_results = []
    for q in queries:
        results = await fetch_serper(q, language="zh-TW", num=5)
        raw_results.extend(results)

    # 用 Claude 整理成結構化競品分析
    from src.ai.gemini import analyze_competitor_data  # 需新建此函數
    structured = await analyze_competitor_data(product_name, raw_results)
    return structured
```

**需要新建**：`src/ai/` 裡加一個 `analyze_competitor_data()` 函數，用 Gemini Flash（便宜快速）整理競品原始資料成結構化格式。

**輸出格式**：
```python
{
    "competitor_count": 15,
    "price_range": {"min": 199, "max": 899},
    "avg_rating": 4.2,
    "pain_points": ["容易壞", "包裝差", "客服差"],
    "market_type_hint": "problem",
    "demand_signal": "high",
    "raw_summary": "..."
}
```

---

### 升級 B：Sage 自動評分

**現況**：`analyze_candidate` 需要用戶手動填 demand_score / competition_score 等數字。

**目標**：Ori 搜完後，Sage 用 Claude 自動計算各維度分數。

**實作位置**：`src/ecommerce/selection.py`，新增 `auto_analyze_candidate` 端點

```
POST /api/ecommerce/selection/auto-analyze/{candidate_id}
```

流程：
1. Ori 搜尋完成，回傳 competitor_data
2. Sage 把 competitor_data 送給 Claude Sonnet
3. Claude 依照 `ai/skills/product-scoring.md` 的評分標準輸出各維度分數
4. 系統自動填入 `ecommerce_selection_analyses` 表

**Claude Prompt 骨架**：
```
你是 Flow Lab 的選品分析師（Sage）。
品牌定位：辦公室療育，主打桌面療癒商品。

以下是商品「{product_name}」的競品研究資料：
{competitor_data}

請依照以下評分標準輸出 JSON：
- demand_score (1-10)：需求強度
- competition_score (1-10)：競爭健康度（有價格梯次=高分，全部同質=低分）
- profit_score (1-10)：利潤空間（成本×3可達=高分）
- pain_point_score (1-10)：痛點改善機會
- brand_fit_score (1-10)：品牌適配度
- market_type：demand/trend/problem/hybrid
- reasoning：100字內說明
```

---

### 升級 C：Craft 自動產選品報告

**現況**：報告需要手動輸入內容。

**目標**：Sage 評分完成後，Craft 自動用 Claude 產出可讀報告。

**實作位置**：`src/ecommerce/selection.py`，在 `analyze_candidate` 或 `auto_analyze_candidate` 結尾自動觸發

```python
async def _craft_generate_report(candidate_id: str, analysis: dict) -> str:
    """
    Craft 自動產選品報告
    """
    from src.ai.claude import generate_selection_report  # 需新建

    report_md = await generate_selection_report(analysis)

    # 存入 DB
    # POST /api/ecommerce/selection/reports/{analysis_id}
    return report_md
```

**報告格式**：
```markdown
# 選品報告：{product_name}
> 分析日期：{date} ｜ 評分：{score_total}/50 ｜ 建議：{viability_band}

## 一句話結論
{2句話說要不要進}

## 評分細項
| 維度 | 分數 | 說明 |
...

## 主要風險
...

## 差異化機會
{負評裡找到的改善點}

## 財務試算
| 項目 | 數值 |
| 建議進貨價 | NT$ |
| 建議售價 | NT$ |
| 預估毛利率 | % |
```

---

## 第二優先：Threads 閉環真正運轉

### 升級 D：Threads 數據自動排程

**現況**：需要手動按「抓 Threads 數據」按鈕。

**目標**：每天固定時間自動抓，不需要人工介入。

**實作位置**：`src/pipeline.py` 或新建 `src/scheduler.py`

```python
# 使用 APScheduler 或直接在 uvicorn startup 設定
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 每天凌晨 2 點抓 Threads 數據
scheduler.add_job(run_threads_tracker, "cron", hour=2, minute=0)

# 每天早上 7 點跑內容 pipeline
scheduler.add_job(run_daily_pipeline, "cron", hour=7, minute=0)
```

---

### 升級 E：Threads 數據自動影響選題

**現況**：`audience_insights` 表有數據，但 Lala 選題時需要手動參考。

**目標**：Lala 在選題時自動讀取近期高互動模式，注入 prompt。

**實作位置**：`src/agents/strategy.py`（Lala 的策略 agent）

在 StrategyAgent 的 prompt 組裝前加入：
```python
# 讀取近 14 天高互動主題特徵
from src.db.queries import get_top_performing_topics
insights = get_top_performing_topics(days=14, top_n=5)

if insights:
    insight_text = "\n".join([
        f"- {i['topic_type']}：平均互動率 {i['avg_engagement']}%"
        for i in insights
    ])
    prompt += f"\n\n近期高互動主題模式（請優先選擇類似方向）：\n{insight_text}"
```

---

### 升級 F：選品決策自動學習

**現況**：`_auto_lesson_on_decision()` 已存在，但 lesson 沒有反向影響 Ori 的搜尋策略。

**目標**：累積 10 條 lesson 後，Sage 自動整合成「選品規則更新」，存入 `ai/context/` 讓 Ori 下次搜尋時參考。

**實作位置**：`src/ecommerce/selection.py`，`_auto_lesson_on_decision` 函數末尾

```python
# 累積到 10 條時觸發規則整合
lesson_count = conn.execute("SELECT COUNT(*) FROM ecommerce_selection_lessons").fetchone()[0]
if lesson_count % 10 == 0:
    _trigger_sage_rule_synthesis(lesson_count)
```

新建 `_trigger_sage_rule_synthesis()`：
- 讀取所有 lesson
- 用 Claude 整合成 3-5 條選品規則
- 寫入 `ai/context/flowlab-selection-rules.md`
- Ori 下次分析時讀取此檔案

---

## 第三優先：對外擴展

### 升級 G：通知系統

**目標**：重要事件主動通知你，不用一直盯 dashboard。

**觸發條件**：
- 今日文案準備完畢（Craft awaiting_human）
- 選品報告完成（Craft awaiting_human approve_purchase）
- 週報已生成
- 系統跑失敗

**實作方式**（選一）：
- **LINE Notify**（最簡單，台灣最常用）
- **Telegram Bot**
- **Email**（已有 Gmail node 在 n8n 計畫中）

```python
# src/utils/notify.py
async def send_line_notify(message: str) -> None:
    import httpx
    token = os.getenv("LINE_NOTIFY_TOKEN")
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://notify-api.line.me/api/notify",
            headers={"Authorization": f"Bearer {token}"},
            data={"message": message},
        )
```

在 `mark_agent_awaiting_human` 後面加一行呼叫即可。

---

### 升級 H：雲端部署

**現況**：全部本機，關電腦就停了。

**目標**：部署到雲端，24/7 自動跑，手機也能看 dashboard。

**建議方案**：

| 元件 | 平台 | 費用 |
|------|------|------|
| 後端 FastAPI | Railway / Render | 免費方案可用 |
| 前端 Next.js | Vercel | 免費 |
| 資料庫 SQLite | 升級為 Turso（SQLite 雲端版）| 免費方案可用 |
| n8n | Railway 自架 or n8n Cloud | 自架免費 |

**注意**：部署前要把所有 `localhost:8000` hardcode 改成環境變數（`NEXT_PUBLIC_API_BASE`，office/page.tsx 已有實作）。

---

## 執行優先順序

```
現在（本週）
└── Fix-1：修正 test_serper.py ← Codex，5分鐘

Phase 3A（最有感，讓 AI 真正工作）
├── 升級 A：Ori 搜尋競品
├── 升級 B：Sage 自動評分
└── 升級 C：Craft 自動產報告

Phase 3B（閉環智能化）
├── 升級 D：Threads 自動排程
├── 升級 E：Threads 數據影響選題
└── 升級 F：選品決策自動學習

Phase 3C（對外擴展）
├── 升級 G：LINE 通知
└── 升級 H：雲端部署
```

---

## Phase 3A 完成後的操作體驗

```
你：在候選池新增「珪藻土杯墊」

AI Office：
  [Ori]  🔵 搜尋「珪藻土杯墊」蝦皮競品與市場信號...
         （真的在跑 Serper，約 10 秒）
  [Ori]  ✅ 找到 23 筆競品資料 → 交給 Sage

  [Sage] 🔵 分析競品，計算各維度評分...
         （Claude 自動評分，約 15 秒）
  [Sage] ✅ 評分完成：42/50（強力候選）→ 交給 Craft

  [Craft] 🔵 產出選品報告...
  [Craft] 🟠 等待你決策
          「珪藻土杯墊 選品報告完成」
          [查看報告] [核准進貨] [不進貨]

你：點「查看報告」，10 秒內決定要不要進貨
```

---

## 給 Claude Code 的執行備註

1. 升級 A/B/C 有相依性：A 要先完成，B 才能用 A 的資料，C 才能用 B 的結果
2. `src/ai/` 目錄已存在，在裡面加新的 AI 呼叫函數，不要直接寫在 selection.py
3. Gemini Flash 用於 Ori 的競品整理（便宜快），Claude Sonnet 用於 Sage 評分和 Craft 報告（品質高）
4. 所有新 AI 呼叫都要加 try/except，失敗時降級為空結果，不要讓分析流程中斷
5. 升級 D（排程）要注意 Windows 環境下 APScheduler 的 asyncio 相容性
6. 每完成一個升級，更新 `ai/state/progress-log.md`
