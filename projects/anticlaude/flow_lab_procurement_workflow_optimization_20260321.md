# Flow Lab Procurement Workflow Optimization (2026-03-21)

## 1. Problem Summary

The current Flow Lab selection/procurement flow is still too analysis-first.
It assumes the operator already knows target price, market range, keyword, and detailed cost breakdown at first entry.

That does not match the real sourcing workflow.

Actual operator behavior is closer to:

1. Spot a product.
2. Record only the fields already visible on 1688.
3. Let the system estimate whether the product is worth further work.
4. Fill in deeper market and pricing information later.

Therefore, the system should be restructured into a staged sourcing workflow instead of a single heavy form.

---

## 2. Recommended Workflow Structure

### Phase A: Quick Intake

Purpose: capture a product fast without blocking on unknown fields.

Recommended required fields:

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
- `product_role`
  - `traffic`
  - `core`
  - `profit`
- `notes`

These are the fields the operator usually knows immediately.

### Phase B: Cost Engine

Purpose: calculate the first viability estimate automatically.

System-calculated outputs:

- `landed_cost_twd`
- `estimated_cross_border_shipping_twd`
- `estimated_platform_fee_twd`
- `estimated_transaction_fee_twd`
- `estimated_fss_fee_twd`
- `estimated_ccb_fee_twd`
- `estimated_total_cost_twd`
- `suggested_floor_price_twd`
- `estimated_gross_margin_rate`
- `viability_status`

### Phase C: Detail Enrichment

Purpose: add optional market and strategy fields only when needed.

Recommended optional fields:

- `target_price_twd`
- `market_price_low_twd`
- `market_price_high_twd`
- `primary_keyword`
- `packaging_fee_twd`
- `other_cost_twd`
- `return_rate`
- `discount_rate`
- `restock_days`
- `category`

### Phase D: Strategy and Content Layer

Purpose: only after the product survives the cost screen.

Outputs:

- pricing recommendation
- product positioning
- Shopee listing draft
- Threads warm-up content
- approval package for CEO

---

## 3. Reverse-Derivation Pricing Model

The system should support not only forward calculation, but also reverse calculation.

### 3.1 Why Reverse Derivation Is Needed

In real operation, the user often does not know the final selling price yet.
Instead, the user may know only:

- product role
- desired gross margin band
- rough market ceiling

So the system must answer:

- "Given this cost structure, what selling price is required?"
- "If I want this to be a profit product, can it still survive the market?"
- "If I cap selling price at market high, what margin can I actually get?"

### 3.2 Reverse-Derivation Inputs

Recommended inputs:

- `product_role`
- `desired_margin_rate` (optional)
- `market_price_low_twd` (optional)
- `market_price_high_twd` (optional)
- `ccb_mode`
- `restock_days`
- all landed cost components

### 3.3 Reverse-Derivation Outputs

- `required_price_for_break_even`
- `required_price_for_role_target`
- `required_price_for_custom_margin`
- `max_affordable_landed_cost_at_market_price`
- `role_fit_result`
- `pricing_pressure_status`
- `suggested_price_twd`
- `suggested_price_range_twd`
- `suggested_role_based_price_twd`

### 3.4 Suggested Role Threshold Baseline

These should be centralized as configurable rules, not hardcoded in UI wording.

- `not_suitable`
  - gross margin: `< 25%`
  - focus: do not recommend under normal operating conditions
- `traffic`
  - gross margin: `25% - 40%`
  - focus: acquisition and conversion support
- `profit`
  - gross margin: `>= 40%`
  - focus: strong unit economics
- `core_potential`
  - gross margin: `>= 50%`
  - focus: main-product potential with room for discounts, ads, and operational error

These should remain configurable, but this is the current recommended baseline.

### 3.5 Suggested Selling Price Logic

Yes, the system should generate a suggested selling price automatically.

Recommended outputs:

- `break_even_price_twd`
- `minimum_viable_price_twd`
- `suggested_price_twd`
- `suggested_price_range_twd`
- `role_based_target_price_twd`
- `matched_role_result`

Recommended logic:

1. Compute landed total cost.
2. Apply Shopee 2026 fee stack.
3. Solve the selling price required to hit the selected role threshold.
4. If market low/high exists, compare against market ceiling.
5. Return a recommendation label:
   - `not_suitable`
   - `traffic`
   - `profit`
   - `core_potential`

Suggested target rules:

- `traffic`
  - solve for selling price at `25%` gross margin
- `profit`
  - solve for selling price at `40%` gross margin
- `core_potential`
  - solve for selling price at `50%` gross margin

The preview panel should show:

- current estimated landed cost
- break-even price
- suggested selling price
- suggested selling price range
- resulting gross margin
- matched role
- market fit warning

---

## 4. Shopee 2026 Fee Engine Design

The operator should not manually calculate Shopee charges every time.
These must become system rules.

### 4.1 Fee Components

- `commission_fee`
  - category-based
  - base `6%` for common categories
- `promo_surcharge`
  - `+2%` on campaign days when no qualifying CCB exemption is active
- `long_prep_penalty`
  - `+3%` if restock/prep days exceed 2
- `transaction_fee`
  - `2.5%`
  - base = product price + buyer shipping
- `fss_fee`
  - percentage mode: `6%`
  - fixed mode: `TWD 60`
- `ccb_fee`
  - `1.5%` for 5% cashback
  - `2.5%` for 10% cashback

### 4.2 FSS Auto-Switch Logic

Recommended default:

- when `selling_price_twd > 1000`, compare percent vs fixed and choose cheaper result
- otherwise default to percentage mode

### 4.3 CCB Decision Logic

System should simulate:

- no CCB
- 5% CCB
- 10% CCB

and show:

- total fee difference
- whether 10% CCB exemption is worth it on campaign days

---

## 5. 1688 Logistics Model

Current costing should be split into at least three layers:

### Layer 1: Product Cost

- `product_cost_rmb`

### Layer 2: 1688 Domestic Shipping

- `domestic_shipping_rmb`

This should remain operator-entered because 1688 can show address-based shipping directly.

### Layer 3: Cross-Border Consolidation

Use mode-based rule tables:

- `air`: `100-130 TWD/kg`
- `sea_express`: `35-55 TWD/kg`
- `sea_freight`: `15-25 TWD/kg`

### Layer 4: Special Goods Premium

- if `goods_type = special`
  - add `10-20 TWD/kg` premium

The system should not collapse all logistics into a single opaque field.

---

## 6. Input Form Redesign Recommendation

### 6.1 Step 1: Minimal Intake Form

Only show:

- SKU
- Product name
- Product cost RMB
- 1688 domestic shipping RMB
- Goods type
- Shipping mode
- Initial stock
- Product role
- Notes

### 6.2 Step 2: Optional Detail Drawer

Expandable advanced section:

- target price
- market low/high
- keyword
- packaging fee
- other cost
- return rate
- discount rate
- prep days

### 6.3 Step 3: System Preview Panel

Instant preview should show:

- estimated total landed cost
- break-even price
- recommended price band
- suggested selling price
- estimated margin band by role
- risk flags

This lets the operator decide before doing deeper work.

---

## 7. Architecture Implications

### 7.1 Current Gap

Current selection logic is still biased toward analysis objects rather than procurement-first entry.

### 7.2 Recommended Separation

Split into:

- `procurement_intake`
- `cost_engine`
- `market_enrichment`
- `content_generation`

This separation is better aligned with the real operator journey.

### 7.3 Data Model Additions

Recommended new or explicit fields:

- `product_cost_rmb`
- `domestic_shipping_rmb`
- `shipping_mode`
- `goods_type`
- `cross_border_rate_twd_per_kg`
- `special_goods_premium_twd_per_kg`
- `product_role`
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

---

## 8. Recommended Operator Experience

The ideal UX should feel like this:

1. "I found a product."
2. "I enter only what I already know."
3. "The system immediately tells me whether this has a chance."
4. "If yes, I enrich market and pricing details."
5. "Then the system helps me decide positioning, listing, and content."

This is much closer to real sourcing behavior than forcing a full analysis form at the start.

---

## 9. Recommended Next Implementation Direction

Priority order:

1. Redesign intake schema into required vs optional fields.
2. Centralize Shopee 2026 fee rules in a cost engine.
3. Add reverse-derivation pricing outputs.
4. Make product role thresholds configurable.
5. Move market price and keyword into enrichment phase instead of intake.
6. Expose a quick viability panel in Flow Lab UI.

---

## 10. Final Conclusion

The system should stop assuming the operator knows everything at intake time.

The better design is:

- capture quickly
- calculate automatically
- enrich later
- decide with structure

That change will make Flow Lab feel like a real sourcing operating system instead of a research-heavy data form.
