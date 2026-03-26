# Flow Lab End-to-End Product Intake and Pricing Specification (2026-03-21)

## 1. Objective

This specification consolidates the full Flow Lab product-intake and pricing logic into a single operator-friendly workflow.

The design goal is:

- make sourcing easier at first entry
- avoid blocking on unknown fields
- calculate realistic Shopee 2026 profitability automatically
- support reverse-derivation pricing
- classify products by role and viability
- guide the operator step by step instead of forcing a heavy analysis form

---

## 2. Core Design Philosophy

The system should not assume the operator knows everything at the first moment a product is discovered.

The correct operating order is:

1. find a product
2. input only the data already known
3. let the system compute landed cost and viability
4. enrich market and pricing details later
5. generate strategy, content, and listing assets after the product survives the cost screen

Therefore, the Flow Lab system should be procurement-first, not analysis-first.

---

## 3. End-to-End Workflow

### Step 1: Quick Product Intake

Purpose: capture a candidate product quickly.

Required fields:

- `sku`
- `product_name`
- `product_cost_rmb`
- `domestic_shipping_rmb`
- `shipping_mode`
  - `air`
  - `sea_express`
  - `sea_freight`
- `goods_type`
  - `general`
  - `special`
- `initial_stock`
- `target_role`
  - `traffic`
  - `core`
  - `profit`
- `notes`

These are the fields the operator usually knows immediately.

### Step 2: Cost Engine

Purpose: estimate total landed cost and platform burden.

System-calculated outputs:

- `landed_cost_twd`
- `cross_border_shipping_twd`
- `platform_fee_twd`
- `transaction_fee_twd`
- `fss_fee_twd`
- `ccb_fee_twd`
- `estimated_ad_cost_twd`
- `estimated_total_cost_twd`
- `break_even_price_twd`
- `suggested_price_twd`
- `suggested_price_range_twd`
- `estimated_margin_rate`
- `role_fit_result`
- `viability_status`

### Step 3: Detail Enrichment

Purpose: add optional fields later, only if needed.

Optional fields:

- `market_price_low_twd`
- `market_price_high_twd`
- `target_price_twd`
- `primary_keyword`
- `packaging_fee_twd`
- `other_cost_twd`
- `return_rate`
- `discount_rate`
- `restock_days`
- `category`
- `weight_kg`

### Step 4: Decision and Output Layer

Purpose: convert a viable candidate into an operational asset.

Outputs:

- recommended selling price
- recommended product role
- pricing warning
- product viability summary
- Shopee listing direction
- Threads warm-up direction
- approval package for CEO

---

## 4. Shopee 2026 Fee Model

Shopee 2026 should be built into the system as rules, not manually entered every time.

### 4.1 Commission Fee

- normal days:
  - category-based
  - default assumption for common categories: `6%`
- promotion days:
  - if no qualifying cashback exemption, add `2%`
- long prep / pre-order penalty:
  - if prep days `> 2`, add `3%`

### 4.2 Transaction Fee

- `2.5%`
- calculation base:
  - product selling price
  - plus buyer-paid shipping if included in Shopee fee base

### 4.3 Free Shipping Service (FSS)

Two modes:

- percentage mode:
  - `6%`
- fixed mode:
  - `TWD 60`

Recommended switching rule:

- if estimated selling price is higher than `TWD 1000`, compare both modes and choose the cheaper result
- otherwise default to percentage mode

### 4.4 Cashback Program (CCB)

Supported options:

- none
- `5% cashback` -> extra `1.5%`
- `10% cashback` -> extra `2.5%`

The system should also simulate whether the 10% cashback option meaningfully offsets campaign-day pressure.

---

## 5. 1688 Logistics Model

1688 procurement must be split into visible cost layers.

### Layer 1: Product Cost

- `product_cost_rmb`

### Layer 2: 1688 Domestic Shipping

- `domestic_shipping_rmb`

This should remain operator-entered, since 1688 can already show address-based shipping.

### Layer 3: Cross-Border Consolidation

Supported shipping modes:

- `air`
  - `100-130 TWD/kg`
- `sea_express`
  - `35-55 TWD/kg`
- `sea_freight`
  - `15-25 TWD/kg`

### Layer 4: Special Goods Premium

If the product is `special`:

- add `10-20 TWD/kg` extra

This prevents all logistics cost from being hidden inside one opaque field.

---

## 6. Role Classification Rules

The system should classify products by margin band.

### Final Role Thresholds

- `< 25%`
  - `not_suitable`
- `25% <= margin < 40%`
  - `traffic`
- `40% <= margin < 50%`
  - `core`
- `>= 50%`
  - `profit`

This avoids overlap and makes classification deterministic.

### Interpretation

- `not_suitable`
  - not recommended under normal operating conditions
- `traffic`
  - acceptable as a traffic or entry product
- `core`
  - good main-product range with business support capacity
- `profit`
  - strong margin center, can absorb discounts, ad cost, and operational error more safely

---

## 7. Reverse-Derivation Pricing Logic

The system must support reverse pricing when the operator does not know the selling price yet.

### 7.1 Core Goal

The system should answer:

- what selling price is required just to break even
- what selling price is required to qualify as traffic/core/profit
- whether the market ceiling can support the target role

### 7.2 Reverse-Derivation Inputs

- landed total cost
- Shopee fee environment
- target role
- optional custom margin target
- optional market low/high
- optional advertising budget assumption

### 7.3 Reverse-Derivation Outputs

- `break_even_price_twd`
- `required_price_for_target_role`
- `required_price_for_custom_margin`
- `suggested_price_twd`
- `suggested_price_range_twd`
- `matched_role_result`
- `pricing_pressure_status`
- `market_fit_warning`

---

## 8. Pricing Formula

### 8.1 Percentage-Only Case

When all relevant fees are percentage-based:

`Suggested Price = Landed Total Cost / (1 - Platform Variable Fee Rate - Target Margin Rate - Advertising Budget Rate)`

This is the correct reverse-derivation structure.

### 8.2 Mixed Fee Case

When there is a fixed fee such as `FSS = TWD 60`, that fixed amount must not be treated as a percentage.

Correct structure:

`Suggested Price = (Landed Total Cost + Fixed Fees) / (1 - Variable Fee Rate - Target Margin Rate - Advertising Budget Rate)`

Therefore:

- percentage fees belong in the denominator
- fixed fees belong in the numerator

This is required for Shopee 2026 correctness.

---

## 9. Role-Based Suggested Selling Price Presets

The system should offer one-click price generation.

### 9.1 Recommended Presets

- `Generate Traffic Price`
  - target margin: `25%`
  - ad budget: `10%`
- `Generate Core Price`
  - target margin: `40%`
  - ad budget: `15%`
- `Generate Profit Price`
  - target margin: `55%`
  - ad budget: `5%`

These presets are for pricing strategy, not for final classification labels.

### 9.2 Important Distinction

There are two related but different concepts:

1. `Role classification`
   - based on actual resulting margin
2. `Pricing strategy preset`
   - used to generate a recommended selling price target

The system must keep these two concepts separate.

---

## 10. Environment Simulation Controls

The system should let the operator simulate the current environment.

Required controls:

- `Is Promotion Day?`
  - if true, add `2%` surcharge where applicable
- `Is Pre-Order / Long Prep?`
  - if true, add `3%`
- `FSS Mode`
  - percentage mode
  - fixed `TWD 60`
- `CCB Mode`
  - none
  - 5%
  - 10%

These controls directly affect the suggested selling price.

---

## 11. Recommended UI Flow

### Step A: Intake Form

Show only the essentials first:

- SKU
- Product name
- Product cost RMB
- 1688 domestic shipping RMB
- Shipping mode
- Goods type
- Initial stock
- Target role
- Notes

### Step B: Advanced Drawer

Expandable section for later:

- market low/high
- keyword
- target price
- packaging fee
- other cost
- return rate
- discount rate
- restock days
- category
- weight

### Step C: System Result Panel

The preview should show:

- landed total cost
- break-even price
- suggested selling price
- suggested price range
- resulting margin
- matched role
- market-fit warning
- FSS mode recommendation

### Step D: One-Click Strategy Buttons

Buttons:

- `Generate Traffic Price`
- `Generate Core Price`
- `Generate Profit Price`

Each button should recalculate suggested price immediately.

---

## 12. Recommended SOP

The system should guide the operator like this:

1. Input 1688 sourcing data.
2. The system calculates landed total cost.
3. The system asks:
   - "What is this product for?"
4. The operator chooses:
   - traffic
   - core
   - profit
5. The system reads current 2026 fee environment.
6. The system outputs:
   - recommended selling price
   - break-even price
   - resulting margin
   - classification result
   - market-fit warning if market price exists

Example:

- landed total cost: `TWD 120`
- target role: `traffic`
- environment: normal day, FSS percentage mode

System output:

- recommended selling price: `TWD 215`
- break-even price: `TWD 158`
- estimated realized margin: `25%`
- classification: `traffic`

---

## 13. Architecture Implications

Current selection logic is still too analysis-heavy.

The recommended architecture split is:

- `procurement_intake`
- `cost_engine`
- `market_enrichment`
- `pricing_strategy`
- `content_generation`

This is better aligned with the real operator workflow than one large candidate-analysis form.

### Recommended Schema Additions

- `product_cost_rmb`
- `domestic_shipping_rmb`
- `shipping_mode`
- `goods_type`
- `weight_kg`
- `cross_border_rate_twd_per_kg`
- `special_goods_premium_twd_per_kg`
- `target_role`
- `market_price_low_twd`
- `market_price_high_twd`
- `target_price_twd`
- `packaging_fee_twd`
- `other_cost_twd`
- `return_rate`
- `discount_rate`
- `restock_days`
- `ccb_mode`
- `fss_mode`
- `is_promo_day`
- `is_preorder`

---

## 14. Final Conclusion

The Flow Lab system should evolve into a sourcing operating system that:

- captures product opportunities quickly
- calculates real 2026 platform economics automatically
- supports reverse-derivation pricing
- classifies products by role and viability
- gives the operator suggested selling prices immediately
- delays non-essential fields until later

The most important principle is:

Do not force the operator to know everything at intake time.

The better system is:

- input fast
- calculate automatically
- enrich later
- decide with structure
