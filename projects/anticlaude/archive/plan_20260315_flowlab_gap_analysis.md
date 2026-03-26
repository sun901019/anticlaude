# Flow Lab 差異分析與補強計畫
> 作者：Claude Code
> 日期：2026-03-15
> 依據：用戶提供的 AI Shopee Product Selection System 規格 vs 現有系統

---

## 結論先說

現有系統已具備規格的 **70% 核心功能**，且在某些地方（選品 AI 流程、學習記憶、候選池管理）甚至**超越規格**。
主要缺口集中在**成本結構不完整**和**建議售價計算邏輯尚未統一**。

---

## 現況對照表

| 規格模組 | 現有狀態 | 說明 |
|--------|---------|------|
| 供應商資料（1688）| ✅ 手動輸入 | cost_rmb、supplier 欄位存在 |
| 蝦皮市場分析 | ✅ AI 自動（Serper）| competitor_analyzer.py |
| 成本計算 | ⚠️ 部分 | 缺物流費、包裝費、退貨風險費 |
| 利潤計算 | ⚠️ 部分 | gross_margin 計算未含全成本 |
| 建議售價公式 | ⚠️ 不完整 | 有 calc_suggested_price()，但公式與規格不同 |
| 安全 CPA 計算 | ❌ 缺少 | safe_CPA = 售價 - 全成本，尚未實作 |
| 競爭分析 | ✅ 有 | price_range 有，市場健康度分類尚未顯示 |
| 商品評分模型 | ✅ 已實作 | Sage 5 維度，最高 50 分 |
| 商品角色分類 | ⚠️ 手動設定 | 有 引流/毛利/主力，但未根據毛利率自動分類 |
| 最終選品報告 | ✅ 完整 | Craft 自動產 markdown 報告 |
| AI 自動化流程 | ✅ 超越規格 | Ori→Sage→Craft 全自動，規格列為「未來功能」|
| 學習記憶系統 | ✅ 超越規格 | lessons + rule synthesis，規格沒有此功能 |
| 候選池管理 | ✅ 超越規格 | 候選池 + 審核流程，規格沒有此功能 |

---

## 缺口詳細分析

### 缺口 1：成本結構不完整（高優先）

**規格要求的 8 類成本：**

| 成本類別 | 規格 | 現有系統 | 狀態 |
|--------|------|---------|------|
| 商品成本 | supplier_price | cost_rmb ✅ | 有 |
| 物流費 | weight × shipping_per_kg | ❌ 無 weight 欄位 | 缺 |
| 包裝費 | bubble_wrap + box + brand_pkg | ❌ 無 | 缺 |
| 平台費 | 5%（可設定） | platform_fee ✅ | 有 |
| 金流費 | 2%（可設定） | payment_fee ✅ | 有 |
| 活動費 | campaign_fee（可選）| ❌ fl_settings 無此項 | 缺 |
| 廣告費 | CPA / daily_budget | ad_spend_7d（週費用）✅ | 部分 |
| 折扣費 | coupon_rate × 售價 | ❌ 無 | 缺 |
| 退貨風險費 | (return_rate + damage_rate) × 售價 | ❌ 無 | 缺 |

**影響**：現有 `gross_margin` 只扣了平台費 + 金流費 + 廣告費，沒有扣物流/包裝/風險，導致毛利率偏高估。

---

### 缺口 2：建議售價公式不統一（高優先）

**規格公式：**
```
recommended_price = total_cost × 2.5  （基本）
recommended_price = total_cost × 3.0  （保守）
```

**現有公式（router.py calc_suggested_price）：**
```python
# 售價 = 成本 / (1 - 目標毛利率 - 平台費 - 金流費)
min_price = cost_twd / (1 - target_margin - total_fee)
suggested = round(min_price × 1.1 / 10) * 10
```

**問題**：現有公式更精確（有目標毛利率），規格公式更直覺（乘數）。
**建議**：兩者都保留，讓使用者選擇顯示方式。

---

### 缺口 3：安全 CPA 未計算（高優先）

**規格公式：**
```
safe_CPA = selling_price - total_cost
```
意思是：扣完所有成本後剩下的，才是你能給廣告花的最大值。

**現有**：`ad_spend_7d` 記錄的是實際花費，但沒有計算「最多能花多少」的上限建議。

**影響**：用戶不知道廣告預算上限，容易超支。

---

### 缺口 4：商品角色未自動分類（中優先）

**規格邏輯：**
```
gross_margin < 20%  → 引流款（Traffic）
gross_margin 20-40% → 毛利款（Profit）
gross_margin > 40%  → 主力款（Hero）
```

**現有**：`role` 欄位是手動填的（引流款/毛利款/主力款）。
**應改為**：輸入成本 + 售價後，系統自動建議角色，使用者可覆蓋。

---

### 缺口 5：市場健康度分類（中優先）

**規格邏輯：**
- 健康市場：競品有多個價格區間（99 / 129 / 199 / 299）→ 有差異化空間
- 不健康市場：全部同價（99 / 99 / 99）→ 價格戰

**現有**：`competitor_analyzer.py` 有 `price_range (min/max)` 但沒有「健康度」分類輸出。

**建議輸出欄位新增**：`market_health: "healthy" | "price_war" | "unclear"`

---

## 不需要補的（現有已超越規格）

| 規格寫的「未來功能」 | 現有狀態 |
|-----------------|---------|
| 1688 自動抓資料 | 目前手動，OK（規格也說是 Optional）|
| 蝦皮自動抓資料 | Serper 搜尋替代，OK |
| 負評分析器 | competitor_analyzer.py 已包含 pain_points |
| AI 選品自動化 | ✅ 已完整實作（Ori→Sage→Craft）|
| 資料庫設計 | ✅ 已完整，還更複雜（含選品引擎） |

---

## 補強計畫（按優先順序）

### Phase A：成本結構補完（核心）

**目標**：讓成本計算涵蓋全部 8 類，毛利率準確反映真實利潤。

**需要做的事：**

1. `fl_products` 表新增欄位：
   ```sql
   weight_kg       REAL,          -- 商品重量（物流費計算用）
   packaging_cost  REAL DEFAULT 0, -- 每件包裝費
   return_rate     REAL DEFAULT 0.02, -- 退貨率（預設 2%）
   damage_rate     REAL DEFAULT 0.01  -- 破損率（預設 1%）
   ```

2. `fl_settings` 新增：
   ```
   shipping_per_kg = 40    -- 每公斤物流費（TWD，可調整）
   campaign_fee    = 0.00  -- 蝦皮活動費（0~3%）
   coupon_rate     = 0.00  -- 折價券折扣率
   ```

3. `router.py` 更新 `calc_suggested_price()` 納入全成本：
   ```python
   total_cost = cost_twd + shipping_cost + packaging_cost
               + platform_cost + ads_cost + discount_cost + risk_cost
   ```

4. 新增 `safe_CPA` 計算並顯示在 decision API 回傳結果中。

---

### Phase B：自動角色分類（輔助）

**目標**：輸入成本後系統自動建議商品角色。

**改法**：在 `calc_suggested_price()` 回傳結果加入 `suggested_role`：

```python
if est_gross_margin < 0.20:
    suggested_role = "引流款"
elif est_gross_margin < 0.40:
    suggested_role = "毛利款"
else:
    suggested_role = "主力款"
```

前端「新增商品」表單自動帶入建議角色，使用者可手動覆蓋。

---

### Phase C：市場健康度（錦上添花）

**目標**：在選品報告中顯示「市場健康」或「價格戰」警告。

**改法**：`competitor_analyzer.py` 加入判斷：

```python
price_spread = price_range["max"] - price_range["min"]
price_avg = (price_range["max"] + price_range["min"]) / 2

if price_spread / price_avg > 0.5:
    market_health = "healthy"   # 價差大，有差異化空間
elif price_spread / price_avg > 0.2:
    market_health = "moderate"
else:
    market_health = "price_war" # 價差小，容易打價格戰
```

---

## 實作工作量估計

| 項目 | 複雜度 | 說明 |
|------|--------|------|
| Phase A-1：DB schema 加欄位 | 低 | ALTER TABLE 加欄位 |
| Phase A-2：fl_settings 加設定 | 低 | 新增 3 筆預設值 |
| Phase A-3：calc_suggested_price 重算 | 中 | 納入更多費用參數 |
| Phase A-4：safe_CPA 顯示 | 低 | decision API 加一個計算欄位 |
| Phase A-5：前端顯示更新 | 中 | ecommerce page 顯示全成本明細 |
| Phase B：自動角色建議 | 低 | 計算後加 suggested_role 欄位 |
| Phase C：市場健康度 | 低 | competitor_analyzer.py 加判斷邏輯 |

---

## 給 Claude Code 的執行備註

1. **先做 Phase A** — 成本結構是基礎，其他都依賴它
2. DB schema 加欄位要用 `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`（SQLite 不支援 IF NOT EXISTS，要先 try/except）
3. 前端顯示全成本明細建議做成「展開/收合」UI，預設收合，不要讓介面太複雜
4. `return_rate` 和 `damage_rate` 設好預設值（2% / 1%），讓使用者不填也能計算
5. 每完成一個 Phase，更新 `ai/state/progress-log.md`
