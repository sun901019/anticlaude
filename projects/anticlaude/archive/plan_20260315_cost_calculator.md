# Flow Lab 成本計算器 — 詳細規格
> 作者：Claude Code
> 日期：2026-03-15
> 目標：讓用戶填入成本後，系統自動計算毛利、建議售價、廣告上限

---

## 你要的感覺

```
填入這些：
  進貨成本  ¥20 RMB
  重量      0.4 kg
  包裝費    NT$15
  目標售價  NT$299

系統自動顯示：
  ┌─────────────────────────────────┐
  │  全成本明細                      │
  │  進貨成本      NT$ 90  （¥20×4.5）│
  │  物流費        NT$ 16  （0.4×40） │
  │  包裝費        NT$ 15             │
  │  平台費 5%     NT$ 15  （售×5%）  │
  │  金流費 2%     NT$  6  （售×2%）  │
  │  退貨風險 2%   NT$  6  （售×2%）  │
  │  ─────────────────────────────  │
  │  總成本        NT$148             │
  │  毛利          NT$151  50.5%     │
  │  ─────────────────────────────  │
  │  角色建議      主力款（>40%）     │
  │  建議售價      NT$370  （成本×2.5）│
  │  廣告上限      NT$151  （毛利以內）│
  └─────────────────────────────────┘
```

---

## 成本結構設計

### 分兩層：全域設定 + 商品個別設定

**全域設定**（系統設定 tab，全商品共用）：

| 設定項 | 預設值 | 說明 |
|--------|--------|------|
| 人民幣匯率 | 4.5 | 已有 |
| 蝦皮平台費 | 5% | 已有 |
| 金流費 | 2% | 已有 |
| 每公斤物流費 | NT$40 | **新增** |
| 活動費 | 0% | **新增**（蝦皮大促時才填）|
| 低庫存警示天數 | 7 | 已有 |

**商品個別設定**（每件商品不同）：

| 欄位 | 必填 | 預設值 | 說明 |
|------|------|--------|------|
| 進貨成本（人民幣）| 必填 | — | 已有 `cost_rmb` |
| 商品重量（kg）| 選填 | 0 | **新增** `weight_kg`，空白 = 物流費 0 |
| 每件包裝費（台幣）| 選填 | 0 | **新增** `packaging_cost`，紙箱+氣泡袋+品牌貼紙 |
| 退貨率 | 選填 | 2% | **新增** `return_rate`，不填用系統預設 |
| 破損率 | 選填 | 1% | **新增** `damage_rate`，不填用系統預設 |
| 折扣率 | 選填 | 0% | **新增** `coupon_rate`，有設折價券才填 |
| 目標售價（台幣）| 選填 | — | 已有 `target_price` |

---

## 計算公式

```
// Step 1：固定成本（不受售價影響）
cost_twd        = cost_rmb × exchange_rate
shipping_cost   = weight_kg × shipping_per_kg
packaging_cost  = packaging_cost（直接填入）
fixed_cost      = cost_twd + shipping_cost + packaging_cost

// Step 2：售價相關費用（受售價影響）
platform_cost   = selling_price × platform_fee        // 5%
payment_cost    = selling_price × payment_fee         // 2%
campaign_cost   = selling_price × campaign_fee        // 0%（大促才填）
discount_cost   = selling_price × coupon_rate         // 0%（有折價券才填）
risk_cost       = selling_price × (return_rate + damage_rate)  // 預設 3%

variable_cost   = platform_cost + payment_cost + campaign_cost + discount_cost + risk_cost

// Step 3：總成本
total_cost      = fixed_cost + variable_cost

// Step 4：利潤
profit          = selling_price - total_cost
gross_margin    = profit / selling_price

// Step 5：建議售價（未填目標售價時自動計算）
recommended_price_conservative = fixed_cost / (1 - 0.07 - 0.40)  // 反推：預留 40% 毛利
recommended_price_multiplier   = fixed_cost × 3.0                 // 簡單乘數法

// Step 6：廣告上限
safe_CPA = selling_price - total_cost   // 毛利就是廣告最大空間
```

---

## UI 規劃

### 位置 1：「新增商品」/ 「編輯商品」Modal 新增成本區塊

**現有欄位（保留）：**
- 進貨成本（RMB）
- 目標售價
- 市場價（低/高）

**新增區塊：「成本細項」（預設收合，點開才顯示）：**

```
▼ 成本細項（選填，預設從系統設定帶入）

  商品重量（kg）  [____]  → 物流費 = 重量 × NT$40/kg
  每件包裝費     [____]  NT$
  退貨率         [____]  %  （預設 2%）
  破損率         [____]  %  （預設 1%）
  折扣率         [____]  %  （有折價券才填）
```

**即時計算預覽（填入後自動更新）：**

```
┌─ 成本預覽 ─────────────────────────────┐
│ 進貨成本   NT$ 90                       │
│ 物流費     NT$ 16                       │
│ 包裝費     NT$ 15                       │
│ 平台費     NT$ 15  （售價 NT$299 × 5%） │
│ 金流費     NT$  6  （售價 NT$299 × 2%） │
│ 風險費     NT$  9  （售價 NT$299 × 3%） │
│ ─────────────────────────────────────  │
│ 總成本     NT$151                       │
│ 毛利       NT$148  49.5% ✅             │
│ 角色建議   主力款                        │
│ 廣告上限   NT$148  （最多能花這些打廣告）│
└─────────────────────────────────────────┘
```

---

### 位置 2：「定價決策」Tab 強化

目前「定價決策」只顯示建議售價。強化後顯示完整成本分解：

```
商品：蒜了鴨   售價：NT$299

┌─ 成本結構 ─────────────────────┐    ┌─ 建議行動 ──────────────────┐
│ 進貨  NT$ 90  ████████  30%   │    │ 建議售價  NT$299  ✅ 在合理範圍│
│ 物流  NT$ 16  ███       5%    │    │ 保守售價  NT$360  （成本×3）  │
│ 包裝  NT$ 15  ███       5%    │    │                               │
│ 平台  NT$ 15  ███       5%    │    │ 廣告上限  NT$148/件            │
│ 金流  NT$  6  █         2%    │    │ 安全 ROAS  2.0 ✅             │
│ 風險  NT$  9  ██        3%    │    │                               │
│ ─────────────────────────    │    │ 商品角色  主力款               │
│ 合計  NT$151       50.5% 毛利  │    │ 角色依據  毛利>40%            │
└────────────────────────────────┘    └──────────────────────────────┘
```

---

### 位置 3：「在售商品」列表加毛利率欄

目前列表只有基本資料。新增 `毛利率` 欄：

```
SKU    名稱       角色    進貨RMB  售價    毛利率   狀態
FL-01  蒜了鴨     主力款  ¥20      NT$299  50.5%   active
FL-02  珪藻土杯墊 毛利款  ¥35      NT$449  38.2%   active
```

毛利率顯示顏色：
- **綠色** > 40%（主力款等級）
- **橘色** 20-40%（毛利款等級）
- **紅色** < 20%（警示）

---

## 資料庫變更

### `fl_products` 表新增欄位

```sql
ALTER TABLE fl_products ADD COLUMN weight_kg      REAL DEFAULT 0;
ALTER TABLE fl_products ADD COLUMN packaging_cost REAL DEFAULT 0;
ALTER TABLE fl_products ADD COLUMN return_rate    REAL DEFAULT 0.02;
ALTER TABLE fl_products ADD COLUMN damage_rate    REAL DEFAULT 0.01;
ALTER TABLE fl_products ADD COLUMN coupon_rate    REAL DEFAULT 0;
```

### `fl_settings` 新增設定項

```python
"shipping_per_kg": ("40",  "每公斤物流費", "NT$/kg"),
"campaign_fee":    ("0",   "蝦皮活動費",   "%"),
"default_return_rate":  ("0.02", "預設退貨率", "%"),
"default_damage_rate":  ("0.01", "預設破損率", "%"),
```

---

## 後端 API 變更

### 1. `calc_suggested_price()` 重寫（router.py）

```python
def calc_full_cost(
    cost_rmb: float,
    selling_price: float,
    settings: dict,
    weight_kg: float = 0,
    packaging_cost: float = 0,
    return_rate: float = None,
    damage_rate: float = None,
    coupon_rate: float = 0,
) -> dict:
    exchange_rate  = settings.get("exchange_rate", 4.5)
    platform_fee   = settings.get("platform_fee", 0.05)
    payment_fee    = settings.get("payment_fee", 0.02)
    campaign_fee   = settings.get("campaign_fee", 0)
    shipping_per_kg = settings.get("shipping_per_kg", 40)
    return_rate    = return_rate if return_rate is not None else settings.get("default_return_rate", 0.02)
    damage_rate    = damage_rate if damage_rate is not None else settings.get("default_damage_rate", 0.01)

    cost_twd      = cost_rmb * exchange_rate
    shipping      = weight_kg * shipping_per_kg
    fixed_cost    = cost_twd + shipping + packaging_cost

    variable_rate = platform_fee + payment_fee + campaign_fee + coupon_rate + return_rate + damage_rate
    variable_cost = selling_price * variable_rate

    total_cost    = fixed_cost + variable_cost
    profit        = selling_price - total_cost
    gross_margin  = profit / selling_price if selling_price else 0

    # 建議售價：反推讓毛利達到 40%（扣固定費後）
    # selling = fixed_cost / (1 - variable_rate - 0.40)
    recommended   = round(fixed_cost / max(1 - variable_rate - 0.40, 0.01) * 1.05 / 10) * 10
    conservative  = round(fixed_cost * 3 / 10) * 10

    # 商品角色建議
    if gross_margin < 0.20:
        suggested_role = "引流款"
    elif gross_margin < 0.40:
        suggested_role = "毛利款"
    else:
        suggested_role = "主力款"

    return {
        "breakdown": {
            "cost_twd": round(cost_twd, 1),
            "shipping_cost": round(shipping, 1),
            "packaging_cost": round(packaging_cost, 1),
            "platform_cost": round(selling_price * platform_fee, 1),
            "payment_cost": round(selling_price * payment_fee, 1),
            "campaign_cost": round(selling_price * campaign_fee, 1),
            "discount_cost": round(selling_price * coupon_rate, 1),
            "risk_cost": round(selling_price * (return_rate + damage_rate), 1),
        },
        "fixed_cost": round(fixed_cost, 1),
        "variable_cost": round(variable_cost, 1),
        "total_cost": round(total_cost, 1),
        "profit": round(profit, 1),
        "gross_margin": round(gross_margin, 4),
        "safe_cpa": round(max(profit, 0), 1),
        "recommended_price": recommended,
        "conservative_price": conservative,
        "suggested_role": suggested_role,
    }
```

### 2. `GET /decision/{sku}` 加入全成本計算

現有 decision API 只算基本毛利，改為呼叫 `calc_full_cost()`，回傳完整明細。

### 3. `GET /products` 列表加 `gross_margin_est`

在商品列表中加入估算毛利率（用 target_price 計算）。

---

## 前端 UI 實作重點

### Modal 新增「成本細項」收合區塊

```tsx
{/* 成本細項（預設收合）*/}
const [showCostDetail, setShowCostDetail] = useState(false);

<button onClick={() => setShowCostDetail(!showCostDetail)}>
  {showCostDetail ? "▲" : "▼"} 成本細項（選填）
</button>

{showCostDetail && (
  <div className="grid grid-cols-2 gap-3">
    <Field label="商品重量（kg）" hint="空白=物流費 0">
      <input type="number" step="0.1" ... />
    </Field>
    <Field label="包裝費（NT$）" hint="紙箱+氣泡袋">
      <input type="number" ... />
    </Field>
    <Field label="退貨率（%）" hint="預設 2%">
      <input type="number" step="0.1" ... />
    </Field>
    <Field label="折扣率（%）" hint="有折價券才填">
      <input type="number" step="0.1" ... />
    </Field>
  </div>
)}
```

### 即時計算 Preview（useEffect 監聽欄位變化）

```tsx
useEffect(() => {
  if (!formData.cost_rmb || !formData.target_price) return;
  // 呼叫 /api/ecommerce/calc-cost（新增輕量計算 endpoint）
  // 或直接在前端用相同公式 JS 即時計算
  const result = calcCostPreview(formData, settings);
  setCostPreview(result);
}, [formData.cost_rmb, formData.target_price, formData.weight_kg, ...]);
```

> 建議用**前端 JS 即時計算**（不需 API roundtrip，UX 更流暢）

---

## 執行步驟（給 Claude Code / Codex）

### Step 1：DB Schema（Codex）
- `fl_products` ADD COLUMN：weight_kg / packaging_cost / return_rate / damage_rate / coupon_rate
- `fl_settings` INSERT：shipping_per_kg / campaign_fee / default_return_rate / default_damage_rate
- 注意：SQLite 不支援 `IF NOT EXISTS`，用 try/except 包

### Step 2：後端計算邏輯（Claude Code）
- 重寫 `calc_suggested_price()` → `calc_full_cost()` 含完整 8 類成本
- 更新 `GET /decision/{sku}` 呼叫新函數，回傳 breakdown
- 更新 `GET /products` 列表加 `gross_margin_est`
- 新增輕量 `POST /calc-cost` endpoint 供前端即時預覽使用

### Step 3：前端 Modal 升級（Claude Code + Pixel）
- 「新增商品」/ 「編輯商品」Modal 加成本細項收合區塊
- 加即時計算 Preview 區塊（前端 JS 計算）
- 「在售商品」列表加毛利率欄（帶顏色）

### Step 4：定價決策 Tab 強化（Claude Code + Pixel）
- 完整成本明細卡片（長條圖 or 文字列表）
- 建議售價 + 保守售價
- 安全廣告上限（safe_CPA）
- 商品角色建議（含依據說明）

### Step 5：系統設定 Tab 加新設定項（Claude Code）
- shipping_per_kg 輸入框
- campaign_fee 輸入框
- default_return_rate / default_damage_rate 輸入框

---

## 完成標準

- [ ] 商品有 weight_kg / packaging_cost / return_rate 欄位可填
- [ ] 填完成本後，Modal 裡即時顯示「總成本 / 毛利率 / 建議售價 / 廣告上限」
- [ ] 在售商品列表顯示毛利率（綠/橘/紅）
- [ ] 定價決策 Tab 顯示完整成本明細
- [ ] 系統設定可調整物流費、活動費等全域參數
- [ ] 不填個別欄位時，自動用系統設定預設值計算

---

## 設計原則

1. **不強制填** — 只填進貨成本就能算，其他欄位有預設值
2. **即時預覽** — 每填一個欄位馬上看到結果變化，不需按儲存
3. **收合不干擾** — 成本細項預設收合，簡單情況不看也沒關係
4. **顏色直覺** — 毛利率綠橘紅，一眼知道這個商品值不值得做
