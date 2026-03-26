# Flow Lab 選品系統智能升級計畫
> 作者：Claude Code
> 日期：2026-03-15
> 依據：用戶提供的選品框架（Harry 邏輯）× 現有系統差距分析

---

## 核心問題診斷

你的系統目前最大的問題不是缺功能，是**數據定義不清 + 判斷邏輯太淺**。

| 問題 | 現況 | 應該是 |
|------|------|--------|
| 欄位定義 | cost_rmb 不知道含不含頭程運費 | 每欄一句說明，填的人不用猜 |
| 商品角色 | 只看毛利率 → 自動貼標 | 4 因素判斷 + AI 建議 + 人工確認 |
| 商品狀態 | active / archived 兩種 | 10 階段生命週期 |
| 差評記錄 | 一個 text 欄位 | 結構化（改善難度/風險等級）|
| 關聯商品 | scene 文字欄位 | 可連帶商品清單 + 場景標籤 |
| 下一步建議 | 無 | AI 輸出「建議進樣 / 原因 / 步驟」|

---

## Part 1：欄位定義標準（最先解決）

### 問題根源

同一個欄位，不同時間填入的理解不同，導致所有毛利計算偏差。

### 各欄位定義（明確版）

#### 成本類（固定成本）

| 欄位 | 定義 | 填入範例 |
|------|------|--------|
| `cost_rmb` | **1688 商品本身單價，不含任何運費** | 38.5 |
| `head_freight_rmb` ⬅️新增 | **中國境內集運費 + 頭程國際運費（到台灣倉庫為止）** | 12 |
| `weight_kg` | 單件商品重量（含包裝後出貨重量） | 0.3 |
| `packaging_cost` | 寄給客人的外包裝成本（泡棉氣柱袋+紙箱+品牌貼） | 15 |

> 備註：`cost_twd = (cost_rmb + head_freight_rmb) × exchange_rate`
> 現有公式只算 cost_rmb × exchange_rate，**頭程運費被漏掉**

#### 成本類（變動成本）

| 欄位 | 定義 | 填入範例 |
|------|------|--------|
| `platform_fee` | 蝦皮成交手續費（含金流費，全部%計） | 0.07 |
| `campaign_fee` | 蝦皮活動折讓費（週年慶/雙11等期間有效） | 0.03 |
| `coupon_rate` | 折價券折扣率（你設定的折扣%） | 0.05 |
| `return_rate` | 預估退貨率（歷史數據 or 品類預設值 2%） | 0.02 |
| `damage_rate` | 預估破損/瑕疵率（預設 1%） | 0.01 |

> 注意：`shipping_per_kg`（現有設定）= **蝦皮官方運費補貼計算**，是末端配送費，
> 不是頭程費。這兩件事要分開。

#### 現有公式的問題

```
現有：
  cost_twd = cost_rmb × exchange_rate        ← 漏頭程費
  shipping = weight_kg × shipping_per_kg     ← 這是末端配送，不是頭程

應改為：
  cost_twd = (cost_rmb + head_freight_rmb) × exchange_rate
  last_mile = weight_kg × shipping_per_kg    ← 末端配送（若平台包運則填0）
```

### 修改清單

1. `fl_products` 新增 `head_freight_rmb REAL DEFAULT 0`
2. `calc_full_cost()` 修正 `fixed_cost` 公式
3. 前端新增商品 Modal 加「頭程運費（人民幣）」欄位，旁邊附說明文字
4. `fl_settings` 加 `last_mile_fee`（末端配送費，預設 0，平台包運則無需填）

---

## Part 2：商品生命週期狀態流

### 現況問題

`fl_products.status` 只有 `active` / `archived`，你不知道：
- 這個商品是剛想到的靈感，還是已經在賣的？
- 哪些商品在等樣品？哪些在廣告測試？

### 10 階段狀態流

```
靈感發現 → 待調查 → 調查中 → 可進樣 → 已進樣
    → 待評估 → 可上架 → 已上架 → 廣告測試中 → 放大中 → 停止/淘汰
```

| 狀態代碼 | 中文名 | 說明 |
|---------|------|------|
| `idea` | 靈感發現 | 看到某個商品感覺有機會，還沒調查 |
| `investigating` | 調查中 | 正在分析競品/成本/差評 |
| `sample_pending` | 可進樣 | 調查結論可行，等待下單樣品 |
| `sample_received` | 已進樣 | 樣品到手，正在評估實物品質 |
| `evaluating` | 待評估 | 實物評估中（拍照/測試/填成本）|
| `ready` | 可上架 | 評估通過，準備上架 |
| `listed` | 已上架 | 蝦皮上架，尚未投廣告 |
| `testing_ads` | 廣告測試中 | 投入少量廣告觀察 ROAS |
| `scaling` | 放大中 | 廣告有效，正在擴大預算 |
| `stopped` | 停止/淘汰 | 虧損或庫存消化中，不再補貨 |

### 修改清單

1. `fl_products.status` 擴充為上述 10 種（舊的 `active` 對應 `listed`，`archived` 對應 `stopped`）
2. 前端商品列表加狀態篩選器
3. AI Office / Flow Lab 首頁加「各階段商品數量」看板
4. 進入 `listed` 時自動提醒：「此商品尚未填入成本，建議補全後才上架」

---

## Part 3：商品角色分類升級

### 現況問題

```python
# 現有邏輯（太簡單）
if gross_margin < 0.20:
    suggested_role = "引流款"
elif gross_margin < 0.40:
    suggested_role = "毛利款"
else:
    suggested_role = "主力款"
```

只用毛利率一個指標，會錯判。毛利低的不一定是引流款，毛利高的不一定是主力款。

### 正確的角色判斷邏輯（4 因素）

#### 引流款條件（都要符合）
- 市場搜尋量高（競品數多，代表有需求）
- 價格具競爭力（市場均價的 ±10% 以內）
- 毛利率可接受（15%-25%，虧損不能做）
- 適合帶來新客流量

#### 毛利款條件
- 有場景關聯性（可以搭配引流款帶買）
- 毛利率漂亮（30%-45%）
- 搜尋量中等，不需要靠它帶流量

#### 主力款條件
- 最能代表你的賣場品牌形象
- 毛利率 40% 以上
- 同時有一定搜尋量（不只靠帶買）
- 適合主打廣告投放

### AI 建議輸出格式（改為建議，不強制自動判斷）

```
建議角色：毛利款
信心度：75%
理由：
- 毛利率 38%，落在毛利款範圍
- 競品數量少，搜尋量中等（不適合做引流）
- 與辦公室場景商品關聯強，適合帶買
注意：若你主打辦公室客群，此商品也可作為「主力款場景商品」
→ 建議你確認後手動設定
```

### 修改清單

1. `ecommerce_selection_analyses` 加 `role_factors_json`（4 因素評分）
2. `calc_full_cost()` 輸出加 `role_reasoning`（為什麼建議這個角色）
3. 前端顯示角色建議 + 理由，旁邊有「確認」按鈕，未確認前顯示「建議中」badge
4. `fl_products.role_confirmed` BOOLEAN 欄位（false = AI 建議未確認）

---

## Part 4：差評 / 風險點結構化

### 現況

`ecommerce_selection_analyses.negative_reviews_json` 格式：
```json
[{"pain_point": "...", "frequency": "高", "opportunity": "..."}]
```

缺少：改善難度、風險等級。

### 新格式

```json
{
  "items": [
    {
      "pain_point": "風太小",
      "frequency": "高",
      "can_improve": true,
      "improve_difficulty": "低",
      "risk_level": "低",
      "notes": "換更大馬達可解決，不影響選品"
    },
    {
      "pain_point": "底座不穩",
      "frequency": "中",
      "can_improve": false,
      "improve_difficulty": "高",
      "risk_level": "中",
      "notes": "結構問題，需換供應商"
    }
  ],
  "overall_risk": "中",
  "risk_summary": "主要差評可透過選擇高評價批次改善，建議先進少量樣品驗證"
}
```

| 欄位 | 說明 |
|------|------|
| `can_improve` | 此差評點是否可改善 |
| `improve_difficulty` | 低/中/高 |
| `risk_level` | 低/中/高 |
| `overall_risk` | 整體風險等級（自動由最高 item 決定）|

### 修改清單

1. `competitor_analyzer.py` 輸出更新為新格式
2. `sage_scorer.py` 加 `overall_risk` 計算邏輯
3. 前端選品報告頁面加風險矩陣視覺化（顏色：綠/橘/紅）

---

## Part 5：商品關聯地圖

### 現況

`fl_products.scene` = 一行文字（例如 "辦公室舒適"），沒有結構化的關聯商品。

### 新設計

#### 新增 `fl_product_relations` 表

```sql
CREATE TABLE IF NOT EXISTS fl_product_relations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sku             TEXT NOT NULL REFERENCES fl_products(sku),
    related_sku     TEXT,               -- 若是已上架商品填 sku
    related_name    TEXT,               -- 若是未上架商品填名稱
    relation_type   TEXT NOT NULL,      -- bundle | cross_sell | upsell | scene_partner
    scene           TEXT,               -- 共同場景：辦公室午休 / 桌面整潔 / ...
    is_bundle_candidate BOOLEAN DEFAULT 0,
    notes           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

| 關係類型 | 說明 | 例子 |
|---------|------|------|
| `bundle` | 可做組合包 | 午休枕 + 眼罩 + 耳塞 |
| `cross_sell` | 結帳時推薦 | 買桌扇推薦眼罩 |
| `upsell` | 加價購 | 基本款→升級款 |
| `scene_partner` | 同場景可連帶 | 辦公室午休系列 |

#### 前端顯示

商品編輯頁面加「關聯商品」區塊：
```
核心場景：辦公室午休
連帶商品：
  ✅ 眼罩 (FL-03) — 已上架，bundle 建議
  ✅ 毛毯 (FL-07) — 已上架，cross_sell
  📋 耳塞 — 未上架，建議未來選品
  📋 桌上風扇 — 未上架，可做組合包
適合組合包：是
適合加價購：是
```

---

## Part 6：下一步建議輸出

### 現況

`fl_performance.next_action` = 一行文字，只在填入銷售數據時出現。選品階段、調查階段沒有「下一步」指引。

### AI 標準輸出格式

```json
{
  "recommendation": "建議進樣",
  "confidence": "高",
  "reasons": [
    "市場價格帶穩定（NT$199-399）",
    "主要差評點可透過選高評分批次改善",
    "預估毛利率 38%，符合毛利款標準",
    "與辦公室舒壓場景高度關聯"
  ],
  "next_steps": [
    "先進 3-5 件樣品，確認材質與噪音問題",
    "檢查是否有品牌標誌（版權風險）",
    "同步聯繫：午休枕 / 眼罩作為場景組合",
    "暫不投廣告，先完成場景組合再上架"
  ],
  "warnings": [
    "底座不穩是結構問題，需選高評分批次規避"
  ]
}
```

### 觸發時機

| 階段 | 觸發 | 輸出 |
|------|------|------|
| 候選商品分析後（Sage） | 自動 | 建議進樣 / 觀察 / 淘汰 |
| 廣告測試 7 天後（Tracker）| 自動 | 建議放大 / 停止 / 調整 |
| 庫存低於警戒線（Tracker）| 自動 | 補貨建議量 + 時間點 |
| 競品均價下跌 10%（未來）| 自動 | 調整定價策略通知 |

---

## 實作優先順序

### 第一批（最高影響，改公式正確性）

```
P0-A：fl_products 加 head_freight_rmb 欄位
P0-B：calc_full_cost() 修正頭程費計算
P0-C：前端新增商品表單加欄位定義說明文字
```

### 第二批（生命週期管理）

```
P1-A：fl_products.status 擴充為 10 階段
P1-B：前端商品列表加狀態看板
P1-C：AI Office 加「各階段商品數量」看板
```

### 第三批（智能升級）

```
P2-A：商品角色 4 因素判斷 + 人工確認機制
P2-B：差評結構化新格式
P2-C：fl_product_relations 表 + 前端關聯商品顯示
P2-D：AI 標準「下一步建議」輸出格式
```

---

## 欄位定義速查表（給填單人看的）

| 欄位 | 定義 | 單位 | 範例 |
|------|------|------|------|
| 商品成本 `cost_rmb` | 1688/供應商商品本身單價，不含任何運費 | 人民幣 | 38.5 |
| 頭程運費 `head_freight_rmb` | 中國到台灣的全程運費（含集運+國際段），按件攤算 | 人民幣 | 12 |
| 包材成本 `packaging_cost` | 寄給客人的所有包材費（泡棉+紙箱+品牌袋+貼紙） | 台幣 | 15 |
| 商品重量 `weight_kg` | 單件商品含包材的出貨重量 | 公斤 | 0.3 |
| 售價 `target_price` | 蝦皮定價（未折扣前） | 台幣 | 299 |
| 市場均價低 `market_price_low` | 主要競品最低售價 | 台幣 | 199 |
| 市場均價高 `market_price_high` | 主要競品最高售價 | 台幣 | 399 |
| 平台費率 `platform_fee` | 蝦皮成交服務費（含付款處理費，約 5-7%） | % | 0.07 |
| 活動費率 `campaign_fee` | 蝦皮活動折讓費（週年慶等，平時填 0） | % | 0.03 |
| 退貨率 `return_rate` | 預估退貨比例（品類預設 2%，精密品類填高一點）| % | 0.02 |
| 破損率 `damage_rate` | 預估破損/瑕疵比例（預設 1%）| % | 0.01 |

---

## 安全毛利率門檻（Harry 邏輯）

| 角色 | 安全毛利率下限 | 說明 |
|------|------------|------|
| 引流款 | 15%-25% | 低於 15% 不做，那是在賠錢衝量 |
| 毛利款 | 30%-45% | 這是你的主要獲利來源 |
| 主力款 | 40%+ | 高毛利 + 夠大流量才能做主力 |

> 注意：安全毛利率指含**全部 8 類成本後**的毛利，不是只扣商品成本。
