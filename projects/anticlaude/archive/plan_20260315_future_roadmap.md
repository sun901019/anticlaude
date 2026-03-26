# AntiClaude — 未來優化路線圖
> 作者：Claude Code
> 日期：2026-03-15
> 前提：系統目前健康度優良，核心功能已完整，以下為擴展與精煉方向

---

## 系統現況快照

```
已完成（生產可用）
├── AI Agency 6 層框架                    ✅
├── 內容 Pipeline（Ori→Lala→Craft→Sage） ✅
├── Flow Lab 選品引擎（含 AI 全自動）      ✅
├── AI Office 即時儀表板                  ✅
├── 成本計算器（8 類成本）                 ✅
├── Threads 自動排程 + 數據回饋            ✅
├── 學習記憶 + 規則合成                   ✅
├── LINE 通知系統                         ✅
├── 50 個測試                            ✅
└── 技術債清理                           ✅

部分完成
├── 受眾洞察 → 選題影響（資料有，尚未注入）  ⚠️
├── Agent Timeline 篩選 UI                ⚠️
└── 雲端部署                             ⏸ 暫緩

未開始
├── Threads 自動發文                      📋
├── A/B 測試機制                         📋
├── 蝦皮銷售數據可視化                    📋
└── 競品價格追蹤警示                      📋
```

---

## 第一層：補完現有缺口（最近期，1-2 週）

### Gap-1：受眾洞察 → Lala 選題注入（半完成）

**現況**：`audience_insights` 表有數據，`get_top_performing_topics()` 函數也建好了，
但 Lala 的 `strategy.py` 還沒有在選題時讀取這些數據。

**補法**：
```python
# src/agents/strategy.py，在 prompt 組裝前加入
from src.db.queries import get_top_performing_topics
insights = get_top_performing_topics(days=14, top_n=5)
if insights:
    insight_text = "\n".join([
        f"- {i['topic_type']}：平均互動率 {i['avg_engagement']}%"
        for i in insights
    ])
    prompt += f"\n\n近期高互動主題（優先選擇類似方向）：\n{insight_text}"
```

**效果**：Lala 的選題開始受真實表現數據影響，系統越用越準。

---

### Gap-2：AI Office Timeline 篩選 UI

**現況**：後端 `/api/agents/events?agent_id=ori` 已支援篩選，
但前端的 filter chips 只有全部 / 各 Agent，缺少「任務類型」篩選。

**補法**：office/page.tsx 活動流加上任務類型篩選按鈕（研究 / 策略 / 內容 / 分析）。

---

### Gap-3：成本計算器前端 UI（本計畫已規劃，待執行）

**現況**：後端 `calc_full_cost()` 已完成，但前端 Modal 尚未加入成本細項 UI。

**參考**：`plan_20260315_cost_calculator.md`（已有完整規格）

---

## 第二層：內容自動化升級（近期，2-4 週）

### Content-1：Threads 自動發文

**現況**：系統產文案、你人工複製貼上發出去。

**目標**：Craft 完成文案 → 你在 AI Office 按「發文」→ 系統自動透過 Threads API 發出。

**需要的東西**：
- Threads Graph API 的 `POST /me/threads` 端點（已有 THREADS_ACCESS_TOKEN）
- 前端 AI Office 的 awaiting_human 卡片加「一鍵發文」按鈕
- 後端新增 `POST /api/threads/publish` 端點

**工作量**：中等（API 整合 + 前端按鈕）

---

### Content-2：A/B 測試機制

**現況**：每次 Craft 產 1 篇文案，你選一篇。

**目標**：Craft 對同一主題產 2 個版本（不同 Hook），發文後自動比較互動率，學習哪種風格更好。

**流程**：
```
Craft 產 2 個版本（版本 A: 問題型 Hook / 版本 B: 故事型 Hook）
→ 你選擇先發哪個
→ 7 天後 Tracker 抓回兩者互動率
→ Sage 記錄「這類主題用哪種 Hook 更好」
→ 下次 Craft 自動偏向勝出風格
```

**工作量**：中等（drafts 表加 ab_group 欄位 + 分析邏輯）

---

### Content-3：週報升級 — 可視化版本

**現況**：週報是純文字 markdown。

**目標**：`/reports` 頁面加入圖表顯示：
- 本週互動率趨勢折線圖
- 各主題類型表現長條圖
- Threads 追蹤者成長曲線

**工作量**：前端為主（Recharts 已在 package.json，可直接用）

---

## 第三層：Flow Lab 電商升級（中期，1-2 個月）

### EC-1：蝦皮銷售數據可視化

**現況**：`fl_performance` 有 7 天銷量數據，但沒有圖表。

**目標**：定價決策 Tab 加入：
- 各商品週銷售趨勢折線圖
- 毛利率變化趨勢
- 庫存消耗速度預測（還剩幾天賣完）

---

### EC-2：競品價格追蹤警示

**現況**：Ori 只在候選商品分析時搜一次競品。

**目標**：已在售商品每週自動追蹤競品價格，若市場均價下跌超過 10%，LINE 通知你調整定價策略。

**流程**：
```
每週一凌晨 → Ori 對在售商品跑一次簡化競品搜尋
→ 比較上週 vs 本週市場均價
→ 若跌幅 > 10% → LINE 通知「FL-01 市場均價下降，建議確認定價」
→ 記錄歷史價格趨勢
```

---

### EC-3：商品生命週期管理

**現況**：商品只有 active / archived 兩個狀態。

**目標**：加入智能生命週期建議：
```
新品期（上架 0-30 天）: 監控起量速度
成長期（銷量穩定成長）: 建議加大廣告預算
成熟期（銷量穩定）: 維持現況
衰退期（連 2 週銷量下滑）: 建議出清或重新選品
```

---

### EC-4：Bundle 收益分析

**現況**：組合設計 Tab 可以建 bundle，但沒有實際銷售追蹤。

**目標**：加入 bundle 銷售績效：每週記錄哪些 bundle 有被購買（手動輸入），Sage 分析哪些組合轉換率高。

---

## 第四層：系統架構升級（長期）

### Arch-1：雲端部署（Phase 3C）

> 用戶已決定暫緩，等準備好再做。

**準備清單**：
- [ ] 前端所有 `localhost:8000` 改為 `NEXT_PUBLIC_API_BASE` 環境變數
- [ ] CORS 改為環境變數 `ALLOWED_ORIGINS`
- [ ] SQLite → Turso（SQLite 雲端版，相容現有代碼）
- [ ] 後端部署到 Railway / Render
- [ ] 前端部署到 Vercel
- [ ] n8n 自架到 Railway

---

### Arch-2：全局 Flag 改 asyncio.Lock（技術債）

**現況**：`src/api/main.py` 有 4 個全局 bool flag 控制排程。

```python
_pipeline_running = False   # 目前跑著就不重複觸發
```

**改為**：

```python
_pipeline_lock = asyncio.Lock()
async def _scheduled_pipeline():
    async with _pipeline_lock:
        ...
```

**工作量**：低（純代碼重構，不影響功能）

---

### Arch-3：google.genai 遷移（技術債）

**現況**：使用 `google.generativeai`（已廢棄，會印 warning）。

**改為**：`google.genai`（新版 SDK，API 略有差異但功能相同）

**影響檔案**：`src/ai/competitor_analyzer.py`、`src/ai/gemini_cluster.py`

---

### Arch-4：測試覆蓋率提升

**現況**：50 個測試，主要覆蓋 API health + agent status + ecommerce。

**缺少測試的地方**：
- `src/ai/competitor_analyzer.py`（Ori 搜尋邏輯）
- `src/ai/sage_scorer.py`（Sage 評分邏輯）
- `src/agents/orchestrator.py`（Pipeline 流程）
- 成本計算器 `calc_full_cost()` 公式正確性

---

## 優先執行順序

```
立即（本週）
├── Gap-3：成本計算器前端 UI（規格已完整）
└── Gap-1：受眾洞察 → Lala 注入（改一個函數）

近期（2 週內）
├── Content-1：Threads 自動發文（最有感）
└── Gap-2：AI Office Timeline 任務類型篩選

中期（1 個月）
├── Content-2：A/B 測試機制
├── EC-1：蝦皮銷售數據圖表
├── EC-2：競品價格追蹤警示
└── Content-3：週報圖表版本

長期（2-3 個月）
├── EC-3：商品生命週期管理
├── EC-4：Bundle 收益分析
├── Arch-2：asyncio.Lock 重構
├── Arch-3：google.genai 遷移
└── Arch-4：測試覆蓋率提升

等準備好再做
└── Arch-1：雲端部署
```

---

## 最有感的下一步：Threads 自動發文

目前流程：
```
AI 產文案 → 你複製 → 手動開 Threads → 貼上 → 發文
```

改完後：
```
AI 產文案 → AI Office 顯示「文案就緒」→ 你看一眼滿意 → 按「發文」→ 自動上傳
```

這是你現在唯一需要「人工操作」但完全可以省掉的步驟。

---

## 給 Claude Code 的執行備註

1. 每個項目開始前先建 `plan_YYYYMMDD_項目名.md`
2. Gap 系列（補完現有）優先於全新功能
3. Content-1（自動發文）需要確認 Threads API 的發文權限範圍
4. EC-2（競品追蹤）可以複用 `competitor_analyzer.py`，只需加排程觸發
5. 雲端部署前必須先做 CORS 和 localhost hardcode 清理
