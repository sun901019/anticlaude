# Ecommerce Surface Truth Recheck Spec

Date: 2026-03-22
Owner: Codex
Purpose: Re-check the latest Flow Lab ecommerce UI after recent changes and correct earlier outdated recommendations.

---

## 1. What was re-checked

This recheck was done directly against active code, not against earlier planning assumptions.

Files reviewed:

- `dashboard/src/app/ecommerce/page.tsx`
- `dashboard/src/app/ecommerce/components/ProductDrawer.tsx`
- `dashboard/src/app/ecommerce/components/QuickAddModal.tsx`
- `dashboard/src/app/ecommerce/components/InboundModal.tsx`
- `dashboard/src/app/ecommerce/components/SelectionTabs.tsx`
- `src/ecommerce/router.py`

---

## 2. Corrections to previous assumptions

The following earlier recommendations are now outdated and should no longer be treated as pending.

### 2.1 Top-level Pricing Lab / Selection Research removal

This has effectively already been completed at the main operator navigation level.

Current primary/secondary nav now only includes:

- `營運總覽`
- `在售商品`
- `週績效表`
- `組合設計`
- `系統設定`
- `說明書`

So the following are no longer primary top-level workspace tabs:

- Pricing Lab / Pricing Decision lab
- Candidates
- Analysis
- Reports
- Lessons

This is already aligned with the intended simplification direction.

### 2.2 Market low/high grouping

This has also already been implemented in Product Drawer.

Current state:

- `market_price_low`
- `market_price_high`

are shown together in a single grouped section:

- `市場價格帶`

So this item should also no longer be treated as pending.

---

## 3. What `System Estimate` really is

The current operator confusion is valid.

The value currently shown in cost/logistics-related surfaces is **not the Shopee selling price**.

It is currently closer to:

- landed cost estimate
- procurement/transport estimate
- fee breakdown foundation

Examples of what it includes depending on surface:

- product cost in TWD
- cross-border freight
- shipping estimate
- packaging cost
- platform fee summary

So the current naming is still misleading.

### Recommended correction

Do **not** rename the existing landed-cost figure to `蝦皮售價`.

Instead split the operator surface into two clearly different outputs:

#### A. `落地成本估算`

Meaning:

- 商品成本 + 頭程/代購 + 跨境運費 + 包材

This answers:

- how much it costs to get the item into sellable inventory

#### B. `蝦皮建議售價`

Meaning:

- calculated selling recommendation after:
  - role target margin
  - platform fee
  - scenario surcharge
  - optional market ceiling logic

This answers:

- what the item should be sold for on Shopee

### Why not directly rename `System Estimate` to `蝦皮售價`

Because the current number is not the final selling price.

If it were renamed directly, the operator would be misled into thinking:

- procurement estimate = actual listing price

That would be a business-logic error, not a UX improvement.

---

## 4. Re-checked meaning of `情境加成`

The user called out this term specifically, and the recheck confirms that it should be used more precisely.

`情境加成` should not mean all platform fees.

It should mean only the conditional surcharge layer caused by the current selling scenario.

### Correct meaning of `情境加成`

This layer includes:

- `CCB`
- `活動日加成`
- `備貨天數懲罰`

It does **not** include:

- base commission
- transaction fee
- base FSS

Those belong to:

- `平台基礎費率`

### Recommended final surface breakdown

The operator should see three layers:

#### 1. `落地成本估算`

- 商品成本 + 頭程/代購 + 跨境運費 + 包材

#### 2. `平台基礎費率`

- 成交 X%
- 金流 X%
- FSS X% or fixed NT$60

#### 3. `情境加成`

- CCB X%
- 活動日 X%
- 備貨懲罰 X%

This is the correct mental model.

---

## 5. Current backend truth for scenario math

Verified in `src/ecommerce/router.py`:

- `ccb_cost = selling_price * ccb_rate`
- `promo_cost = selling_price * promo_rate if (is_promo_day and ccb_plan != "ccb10") else 0`
- `penalty_cost = selling_price * penalty_rate if fulfillment_days > 2 else 0`

So backend-side:

- CCB is active
- promo day is active
- fulfillment penalty is active

The current issue is mostly presentation clarity, not missing backend math.

---

## 6. What still needs improvement after recheck

These are the items that are still genuinely pending.

### 6.1 Metric naming is still confusing

Pending:

- rename vague estimate wording
- distinguish landed cost vs Shopee suggested selling price

### 6.2 Source annotations are still incomplete

The user asked for all important metrics to include small explanatory text such as:

- 成交 6%
- 金流 2.5%
- FSS 6%
- CCB 1.5%
- 活動日 2%
- 備貨 3 天 +3%

This is still not fully implemented.

### 6.3 Scenario visibility should be stronger

Even though advanced settings now show a summary line, it should be made more obvious in the decision area.

Recommended:

- visible chips near pricing summary
- example:
  - `平日`
  - `活動日 +2%`
  - `CCB5 +1.5%`
  - `CCB10 +2.5% / 活動日免加成`
  - `備貨 3 天 +3%`

### 6.4 Bundles are still candidate-oriented

Current activation and logic:

- triggered when `Bundles` tab opens
- refreshable by operator
- logic still based largely on:
  - category
  - recommended role
  - role pairing

This works, but it is not yet the final desired model.

Still needed:

- stronger live-product logic
- family/variant awareness
- scene pairing
- main product + accessory pairing

### 6.5 Family/variant naming is still not operator-friendly enough

Current data fields are still rendered with developer-style wording in some places.

Recommended UI wording:

- `系列名稱`
- `款式名稱`

instead of exposing internal naming concepts directly.

### 6.6 Mojibake remains in active ecommerce UI

This is still visible in active code and should continue to be cleaned.

---

## 7. Bundle Design: current activation truth

This was rechecked to answer the user directly.

### Current activation

Bundle logic currently runs when:

1. the operator opens the `組合設計` tab
2. or manually refreshes bundle suggestions inside that tab

### Current logic basis

Current bundle suggestions are derived from:

- analyzed candidate pool
- category grouping
- recommended roles
- role complement combinations

### Current practical value

Bundles are usable now, but their logic is still better suited to:

- selection analysis

than to:

- live merchandising
- same-family pricing ladder
- real cross-sell design

### Recommended next step

Keep Bundles.

Strengthen them toward:

- product family grouping
- scene-based pairing
- live product relations
- accessory pairing
- AOV growth

---

## 8. Final corrected status

### Already done

- top-level workspace has been simplified
- `市場低價` and `市場高價` are grouped together
- backend scenario math is active

### Still pending

- rename estimate outputs clearly
- add complete source sublabels behind each important metric
- make scenario state more visible
- strengthen Bundles beyond candidate/category logic
- improve family/variant operator wording
- continue mojibake cleanup

---

## 9. Recommended next implementation order

### Phase A

- rename `System Estimate` surfaces into:
  - `落地成本估算`
  - `蝦皮建議售價`
  - `平台基礎費率`
  - `情境加成`

### Phase B

- add dynamic small-text formula/source labels for each metric

### Phase C

- make promo/CCB/fulfillment scenario chips always visible

### Phase D

- upgrade Bundles toward live-product/family logic

### Phase E

- clean remaining operator wording and mojibake

---

## 10. Final recommendation

Do not keep speaking about ecommerce in abstract categories only.

From now on, the operator surface should consistently distinguish:

- `這商品進來要花多少`
- `平台固定會吃多少`
- `這次情境會多吃多少`
- `所以蝦皮建議賣多少`

That is the core clarity model the ecommerce UI should now converge to.
