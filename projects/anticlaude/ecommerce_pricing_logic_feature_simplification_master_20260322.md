# Flow Lab E-commerce Pricing Logic, Feature Simplification, and Family/Variant Optimization Master Spec

Date: 2026-03-22
Owner: Codex
Scope: `dashboard/src/app/ecommerce/*`, `src/ecommerce/router.py`, related operator UX and pricing logic

---

## 1. Goal

This document consolidates the current-state audit and the next optimization direction for the Flow Lab e-commerce system.

It answers the operator questions below:

- What does current pricing decision logic actually depend on?
- Does `CCB` really affect calculation?
- Does `promo day` really affect calculation?
- Why does the pricing UI feel like some switches do nothing?
- How are `cost & logistics` and `system estimate` currently calculated?
- Is the top-level `Pricing Decision` page still needed?
- Should `Candidates / Analysis / Reports / Lessons` remain?
- How should `Bundles` be strengthened?
- How should `family / variant` grouping be added so related products are not always shown as flat independent products?

This is not a full rewrite plan. It is a convergence-and-simplification plan for making the operator experience cleaner, more trustworthy, and easier to maintain.

---

## 2. Current Pricing Decision Logic: What It Depends On

## 2.1 In Product Detail > Decision tab

The current product-level pricing decision logic is primarily driven by these fields:

### Core product facts
- `cost_rmb`
- `head_freight_rmb`
- `weight_kg`
- `packaging_cost`
- `procurement_mode`
- `freight_type`
- `is_special_goods`
- `length_cm`
- `width_cm`
- `height_cm`

### Pricing and market context
- `target_price`
- `market_price_high`
- `market_price_low`

### Scenario settings
- `ccb_plan`
- `is_promo_day`
- `fulfillment_days`
- `ad_budget` (currently more of UI/scenario context than fully unified backend truth)

### Risk assumptions
- `return_rate`
- `damage_rate`
- `coupon_rate`

### Global settings from backend
- `commission_fee`
- `transaction_fee`
- `fss_pct`
- `fss_fixed`
- `fss_threshold`
- `promo_surcharge`
- `fulfillment_penalty`
- `exchange_rate`
- `shipping_per_kg`
- `qql_exchange_rate`
- `qql_service_fee`
- `sea_express_rate`
- `volumetric_divisor`
- `traffic_margin_target`
- `core_margin_target`
- `profit_margin_target`

---

## 2.2 Current data flow

### Quick Add preview
`QuickAddModal` triggers `calcPreview()`, which calls:

- `POST /api/ecommerce/calc-cost`

That endpoint uses backend logic in:

- `src/ecommerce/router.py`
- `calc_full_cost(...)`
- `_market_warning(...)`
- `_calc_ceiling(...)`

### Product detail drawer
`ProductDrawer` receives `prices` from:

- `fetchDrawerPrices()` in `dashboard/src/app/ecommerce/page.tsx`

That request also goes to:

- `POST /api/ecommerce/calc-cost`

This means the product drawer now partially uses backend truth for:

- `landed_cost`
- `fee_rate`
- `market_warning`
- `traffic/core/profit` suggested prices
- `top-down sourcing ceiling`

This is good progress.

---

## 3. Does CCB Actually Affect Calculation?

## Answer
Yes. `CCB` is currently included in backend calculation.

### Where it is calculated
In `src/ecommerce/router.py`:

- `ccb_rate = CCB_RATES.get(ccb_plan, 0.0)`
- `ccb_cost = selling_price * ccb_rate`

### Current rate mapping
- `none` -> `0.0`
- `ccb5` -> `0.015`
- `ccb10` -> `0.025`

### What it affects
It affects:
- total variable cost
- profit
- gross margin
- suggested role
- recommended price bands

### Why it may feel like it is not working
The UI currently shows a simplified `fee_rate` / `platform_fee_rate` field that only reflects:

- commission
- transaction
- FSS percentage

It does **not** visually reflect all of:
- `ccb`
- `promo`
- `penalty`
- `risk`
- `coupon`

So the backend is calculating it, but the displayed summary is not communicating it clearly enough.

## Required improvement
Replace or extend the current simplified fee summary with:

- `base_platform_fee_rate`
- `scenario_fee_rate`
- `total_variable_rate`

Or show an expanded fee summary:

- Base fee
- CCB
- Promo surcharge
- Fulfillment penalty
- Risk assumption
- Coupon assumption

---

## 4. Does Promo Day Actually Affect Calculation?

## Answer
Yes, backend logic already applies promo-day surcharge.

### Where it is calculated
In `src/ecommerce/router.py`:

```python
promo_cost = selling_price * promo_rate if (is_promo_day and ccb_plan != "ccb10") else 0
```

### Important current rule
If:
- `is_promo_day = true`
- `ccb_plan != "ccb10"`

then promo surcharge is added.

If:
- `ccb_plan == "ccb10"`

promo surcharge is intentionally waived.

### Why it may look broken
There are two UX issues:

1. The operator does not see a strong visible delta when toggling promo day.
2. The compact displayed `fee_rate` does not explain the surcharge clearly.

So this is less a broken formula problem and more a weak operator feedback problem.

## Required improvement
When promo day is active, show:

- a visible badge: `Promo +2% active`
- the delta amount in TWD
- a note when `ccb10` suppresses promo surcharge:
  - `Promo surcharge waived by CCB10`

This should appear directly in:
- Quick Add preview
- Product detail > decision/logistics

---

## 5. How Current Cost & Logistics Logic Works

## 5.1 Standard 1688 path

Backend `calc-cost` currently uses:

- `cost_rmb * exchange_rate`
- cross-border freight from either:
  - `weight_kg * freight_per_kg`
  - or fallback `head_freight_rmb * exchange_rate`
- `packaging_cost`
- Shopee fees
- risk assumptions

For standard mode, freight depends on:
- `freight_type`
  - `sea_fast`
  - `sea_regular`
  - `air`
- `is_special_goods`

If special goods:
- `special_goods_surcharge` is added per kg

## 5.2 QQL path

For `procurement_mode == qql_agent`:

Backend uses:

### Procurement stage
- `(cost_rmb + head_freight_rmb) * qql_exchange_rate * (1 + qql_service_fee)`

### Cross-border stage
- volumetric weight:
  - `(length_cm * width_cm * height_cm) / volumetric_divisor`
- billable weight:
  - `max(weight_kg, volumetric_weight)`
- sea express:
  - `billable_weight * sea_express_rate`

### Then backend feeds total into `calc_full_cost(...)`

This means current `system estimate` is based on:
- procurement mode
- actual/estimated logistics inputs
- platform fee settings
- risk settings

---

## 6. Why Current UI Still Feels Confusing

The main issue is not only missing features.
The bigger issue is mixed responsibilities.

## 6.1 In Product Detail > Decision
It still mixes:
- editable inputs
- system outputs
- scenario controls
- market context
- role evaluation
- top-down sourcing tool

That is too much for one “decision” area.

## 6.2 In product creation flow
Quick Add is much better than before, but the product lifecycle still spreads decision logic across:
- Quick Add
- Product Drawer
- Pricing Decision top-level tab
- Inbound modal
- Performance tab

## 6.3 In navigation
The system still surfaces too many secondary tools as first-class tabs:
- `Candidates`
- `Analysis`
- `Reports`
- `Lessons`

For current operator needs, those are too heavy and distract from the main workflow.

---

## 7. Market Low Price and Market High Price: What to Do

## 7.1 Current state
- `market_price_high` is actively used by backend `_market_warning(...)`
- `market_price_low` is mostly stored and displayed, but not meaningfully used in core pricing judgment

## 7.2 UX issue
Right now:
- `market_price_high` is shown in the main decision area
- `market_price_low` is hidden inside advanced settings

This feels wrong because both are market context fields and belong together.

## 7.3 Recommendation

Move them into one shared section:

### Section name
`市場價格帶`

### Display
- `市場低價`
- `市場高價`
- optional future:
  - `熱銷帶低`
  - `熱銷帶高`
  - `偏高可成交帶低`
  - `偏高可成交帶高`

### Priority
- `market_price_high`: recommended input
- `market_price_low`: optional but useful

### Why keep `market_price_low`
It helps identify:
- whether you are entering price-war territory
- how wide the market band is
- whether a product is truly suitable as a traffic product

---

## 8. Top-Level Pricing Decision: Keep, Remove, or Reposition?

## 8.1 Current problem
The top-level `Pricing Decision` tab and the product drawer’s `Decision` tab overlap heavily.

This creates confusion:
- Where should I make the real decision?
- Which one is source-of-truth?
- Why do both surfaces exist?

## 8.2 Recommendation

Do **not** keep it as a primary navigation item in its current form.

### Better options

#### Option A: Demote to secondary tool
Rename it to:
- `Pricing Lab`
- `Pricing Sandbox`
- `Scenario Lab`

Use it only for:
- one-off simulations
- cross-product experimentation
- education/debugging of pricing rules

#### Option B: Remove from main nav
If the product drawer already provides:
- current target price
- suggested prices
- market warning
- top-down ceiling
- scenario toggles

then the top-level pricing tab no longer needs to sit in primary nav.

## Recommended decision
Demote it from primary nav.
Keep the capability, but stop presenting it as a main workspace.

---

## 9. Candidate Pool / Analysis / Reports / Lessons: Keep or Remove?

## 9.1 Current operator reality
Based on current operator feedback:
- these are not heavily used
- they increase visual and navigational weight
- they distract from the main merchandising loop

## 9.2 Recommendation

### Demote or remove from primary UI
The following should be removed from top-level primary tab navigation:
- `Candidates`
- `Analysis`
- `Reports`
- `Lessons`

### What to do with them

#### Option 1: Hide behind one secondary section
Create:
- `Selection Archive`
- `Research`
- `Labs`

Put those tools there if you want to preserve them.

#### Option 2: Soft-remove from product UI
Keep backend/API intact for now, but remove them from primary operator workspace.

This is the best choice for now.

## 9.3 Why this is good
It reduces the main job of the e-commerce system to:

1. Add product
2. Group into family / variant
3. Price it
4. Inbound / restock it
5. Monitor performance
6. Bundle it

That is much cleaner.

---

## 10. Bundles: Keep and Strengthen

Bundles are high-value and should stay.

## 10.1 Why bundles matter
Bundles directly support:
- higher AOV
- better role separation
- better merchandising
- family-level upsell logic

## 10.2 Recommendation

Strengthen bundles into a true operator feature:

### Display
- recommended companion products
- family-aware bundle suggestions
- reason tags:
  - same use case
  - same gift scenario
  - same desk aesthetic
  - upsell ladder

### Future capabilities
- single item -> upgrade bundle
- main item + accessory
- traffic item -> profit bundle

---

## 11. Family / Variant Grouping: Required Next Phase

This is a very worthwhile addition.

## 11.1 Problem
Related products such as:
- 躺贏招財貓
- 躺贏閒樂

should not always appear as completely separate flat products.

## 11.2 Recommendation

Create:
- `Product Family`
- `Variant`

### Product Family
Represents:
- the core product concept / series

### Variant
Represents:
- style
- color
- model
- packaging version
- sub-name

## 11.3 Main list behavior

List should show:
- one family row
- expandable variant rows

Family row should show:
- family name
- number of variants
- role mix
- total stock
- best-selling variant
- performance summary

Expanded variant rows should show:
- SKU
- variant name
- target price
- stock
- margin
- status

## 11.4 Quick Add support

Quick Add should allow:
- create new family
- add variant to existing family

### Quick Add choices
At the top of modal:
- `新商品家族`
- `加入既有家族`

If existing family:
- choose family
- enter variant name / SKU

## 11.5 Product detail behavior

Product detail should show:
- current family name
- sibling variants
- variant count
- family-level bundle hints

## 11.6 Inbound / performance support

Inbound should support:
- variant-level stock
- family-level stock awareness

Performance should support:
- family aggregate row
- variant comparison

## 11.7 Execution order
1. Data model
2. API support
3. list expand/collapse
4. Quick Add branch
5. Product detail family context
6. inbound/performance family awareness

## 11.8 Agent roles
- `Lara`: overall workflow and responsibility split
- `Lumi`: schema/API/frontend implementation
- `Pixel`: family/variant list interaction and visual hierarchy
- `Sage`: check duplication risk and operator clarity
- `Craft`: naming / labels / operator wording

---

## 12. What Should Be Changed Next

## Priority A: Operator clarity
1. Put `market_price_low` next to `market_price_high`
2. Separate:
   - market context
   - scenario controls
   - backend outputs
3. show promo/CCB deltas clearly in pricing results

## Priority B: Navigation cleanup
1. remove/demote:
   - Candidates
   - Analysis
   - Reports
   - Lessons
2. keep and strengthen:
   - Bundles
3. demote:
   - top-level Pricing Decision -> Pricing Lab / secondary tool

## Priority C: Product family model
1. add family/variant grouping
2. stop flat duplication of related products

## Priority D: Formula communication
1. keep backend as pricing truth
2. expose clearer fee breakdown
3. distinguish:
   - base platform fee
   - scenario surcharge
   - risk assumptions

---

## 13. Recommended Final Information Architecture

## Primary tabs
- Dashboard
- Products
- Performance
- Settings
- Manual
- Bundles

## Secondary or hidden tools
- Pricing Lab
- Candidates
- Analysis
- Reports
- Lessons

## Product Drawer tabs
- `decision`
  - role
  - suggested prices
  - target price
  - market band
  - role fit
  - market warning
- `logistics`
  - landed cost
  - fee summary
  - procurement fields
  - freight mode
  - QQL dimensions
- `ops`
  - stock
  - notes
  - status

## Decision tab cleanup rule
Do not keep these mixed in one visual layer:
- market low/high
- promo/ccb/fulfillment toggles
- sourcing ceiling
- role cards
- warning messages

Split into:
- Market band
- Suggested prices
- Ceiling tool
- Advanced scenario

---

## 14. Final Conclusion

The current system is not broken.
But the operator pain is real because:

- some scenario controls are hidden in the wrong place
- some calculated logic is real, but poorly communicated
- some top-level tabs no longer justify primary placement
- same-family products still lack grouping

The main direction is:

- keep the core pricing engine
- clarify what affects pricing
- reduce top-level surface area
- strengthen bundles
- add family/variant grouping
- move secondary research tools out of the primary workspace

This will make the system:

- cleaner
- easier to trust
- easier to operate
- easier to maintain

