# Flow Lab E-commerce Bundle Logic, Surface Cleanup, and Operator Clarity Spec

Date: 2026-03-22
Owner: Codex
Scope: ecommerce operator UX, bundle logic explanation, pricing/logistics display clarity, selection-surface reduction

---

## 1. What the user actually needs

The operator does not want more tools.
The operator wants:

- fewer tabs
- clearer logic
- cleaner pricing explanation
- a useful bundle tool
- family/variant language that is easy to understand

This spec responds to these exact concerns:

- How does bundle design currently work?
- What logic does bundle analysis use?
- Why is the current Pricing Lab not useful?
- What does the “system estimate” in cost/logistics actually mean?
- Can every estimated value show its source?
- Why are `family_name` and `variant_name` confusing?
- Can the Selection Research area be removed?

---

## 2. Bundle Design: How It Currently Works

## 2.1 Current UI presentation

The current `Bundles` tab has two different sections:

### Section A: saved bundle relations
It reads from:
- `GET /api/ecommerce/bundles`

It displays:
- source product
- related product list
- relation type
  - bundle
  - cross_sell
  - upsell
  - scene_partner
- scene
- notes

This is the manually persisted bundle layer.

### Section B: AI bundle suggestions
It reads from:
- `POST /api/ecommerce/selection/bundles/suggest`
- `GET /api/ecommerce/selection/portfolio`

It displays:
- suggested bundle name
- role composition
- included products
- total base price
- bundle price
- discount %
- estimated margin
- reason text

This is the AI suggestion layer.

---

## 2.2 Current backend bundle logic

Current AI bundle suggestion logic is in:

- `src/domains/flow_lab/selection.py`
- endpoint: `/api/ecommerce/selection/bundles/suggest`

### Current logic steps

1. Take non-rejected candidates
2. Read:
   - `candidate category`
   - `recommended_role`
   - `score_total`
   - `financials_json.target_price`
   - `financials_json.gross_margin`
3. Group candidates by `category`
4. Build complementary role pairs:
   - traffic + core
   - traffic + profit
   - core + profit
5. Pick the highest-score product in each role pair
6. Compute:
   - `base_price_sum`
   - `bundle_price = base_price_sum * 0.88`
   - `estimated_margin = average gross margin`
7. Output reason text

### Important reality
This means current bundle suggestion is based on:
- category grouping
- role complementarity
- target price
- score ranking

It is **not** yet based on:
- actual product family structure
- actual historical co-purchase behavior
- same-scene naming hierarchy
- manual operator pair rules

---

## 2.3 Why current bundle feature still feels weak

It is not because there is no logic.
It is because the current logic is:

- selection-oriented
- candidate-oriented
- category-role pairing oriented

But your real use case is:

- live product operations
- merchandising
- what can be sold together on Shopee

So the current bundle feature is technically present, but conceptually still tied too much to the old selection-research workflow.

---

## 3. Recommended new bundle design direction

## 3.1 Bundles should remain

Bundles are one of the few secondary modules that should **not** be removed.

They matter because they support:
- AOV growth
- upsell
- cross-sell
- same-family product strategy
- main-item + accessory logic

## 3.2 New bundle presentation

The bundle area should be shown as:

### Layer A: current manual bundle relations
- primary product
- recommended companion products
- relation badge
- reason
- scene

### Layer B: system bundle suggestions
- suggested pair/group
- expected price ladder
- expected role combination
- reason
- operator action
  - save relation
  - ignore
  - convert to bundle design

## 3.3 Stronger bundle logic direction

Next-phase bundle logic should use:

- same family
- same usage scene
- traffic + profit pairing
- main product + accessory
- same aesthetic/style cluster

This is much more useful than pure category pairing.

---

## 4. Pricing Lab: Recommended removal

## 4.1 Current state

The top-level `decision` tab is still present and acts like a pricing lab.

It overlaps too much with:
- Product detail > decision tab
- Quick Add preview
- top-down ceiling calculator

## 4.2 Recommendation

Remove it from the main ecommerce operator workspace.

### Why
- It duplicates product-level pricing decision
- It creates another place to do the same thinking
- It increases UI weight
- It is not needed for daily operation

## 4.3 Better replacement

The operator should use:
- Quick Add preview
- Product detail > decision

If a sandbox is ever needed later, it can come back as:
- hidden secondary tool
- not a top-level workspace tab

## Decision
Remove the top-level `Pricing Decision` tab from primary ecommerce navigation.

---

## 5. Cost & Logistics “System Estimate”: What It Actually Means

## 5.1 It is NOT the Shopee selling price

The current `system estimate` in logistics/cost-related surfaces is **not** “the Shopee listing price.”

It is mainly a backend-derived estimate of:

- landed cost
- fee summary
- recommended role-based prices

## 5.2 In ProductDrawer > logistics

Current backend-driven values:
- `landed_cost`
- `fee_rate`

### `landed_cost`
This is currently:

`fixed_base = cost_twd + freight + shipping + packaging_cost`

Meaning:
- procurement cost
- cross-border freight
- shipping/logistics
- packaging

It does **not** mean final selling price.

### `fee_rate`
This is currently:

`commission_rate + transaction_rate + fss_pct`

This is only a simplified platform-fee summary.

It does **not** currently include:
- CCB
- promo surcharge
- fulfillment penalty
- return/damage assumptions
- coupon assumptions

That mismatch is a major reason the UI feels unclear.

---

## 5.3 What should be shown instead

Every pricing/cost estimate block should show a source line.

### Example for landed cost
`落地成本 = 商品成本 + 頭程/代購 + 跨境運費 + 包材`

### Example for platform fee summary
`平台基礎費率 = 成交 6% + 金流 2.5% + FSS 6%`

### Example for scenario surcharge
`情境加成 = CCB 1.5% + 活動日 2% + 備貨懲罰 3%`

### Example for risk assumptions
`風險預留 = 退貨率 2% + 破損率 1% + 折扣率 X%`

This should be visible as:
- short subtitle
- tooltip
- or collapsible breakdown note

The operator should never need to guess what the estimate means.

---

## 6. CCB and Promo Day: Why They Feel Broken

## Reality
Backend calculation does include both:

### CCB
- `ccb_cost = selling_price * ccb_rate`

### Promo day
- `promo_cost = selling_price * promo_rate if is_promo_day and ccb_plan != "ccb10"`

### Special rule
If `ccb_plan == "ccb10"`, promo surcharge is waived.

## Why it feels broken
Because current summary UI does not show the delta clearly.

## Required UI fix
Whenever CCB or promo day changes:
- show the changed cost amount
- show the changed percentage
- show explanatory note

Example:
- `CCB5 applied: +1.5%`
- `Promo day applied: +2.0%`
- `Promo waived by CCB10`

---

## 7. Market Low / High: How They Should Be Displayed

`market_price_low` and `market_price_high` should be presented together.

### Current issue
- `market_price_high` is visible
- `market_price_low` is hidden in advanced settings

This makes the operator think they are unrelated.

### Recommendation
Create one block:

## 市場價格帶
- 市場低價
- 市場高價

Optional future expansion:
- 熱銷價低
- 熱銷價高
- 偏高可成交價低
- 偏高可成交價高

---

## 8. Family Name / Variant Name: Why Current Language Is Not Intuitive

## 8.1 Current issue

In Quick Add advanced settings, the fields:
- `family_name`
- `variant_name`

are technically correct, but not operator-friendly.

The operator reaction is valid:
- What is family?
- What is variant?
- What am I supposed to type?

## 8.2 Better labels

Replace the UI labels with simpler business language:

### `family_name`
Recommended display label:
- `系列名稱`
- or `同系列商品名稱`

Help text:
- `同一商品概念下的共用名稱，例如：躺贏招財貓`

### `variant_name`
Recommended display label:
- `款式名稱`
- or `變化款名稱`

Help text:
- `同系列下的具體款式，例如：閒樂款 / 招財款 / 升級版`

## 8.3 Operator mental model

Example:
- 系列名稱：`躺贏招財貓`
- 款式名稱：`閒樂款`

This is much more intuitive than `family` / `variant`.

---

## 9. Selection Research Area: Recommended removal from primary surface

## 9.1 Current modules
- Candidates
- Analysis
- Reports
- Lessons

## 9.2 Recommendation

Remove these from the primary ecommerce workspace.

### Why
- low current usage
- too much navigation weight
- tied to old research workflow
- distracts from live product operations

## 9.3 Keep bundles only

Among those selection-era modules:
- `Bundles` should stay
- the others should be removed from primary nav

If needed, they can live behind:
- archive
- lab
- research

But not in the main operator workflow.

---

## 10. Recommended final ecommerce primary navigation

Keep:
- Dashboard
- Products
- Performance
- Bundles
- Settings
- Manual

Remove or demote:
- Decision / Pricing Lab
- Candidates
- Analysis
- Reports
- Lessons

---

## 11. Required implementation changes

## Phase A: Clarity fixes
- move `market_price_low` beside `market_price_high`
- add explanatory source lines for every estimate block
- explicitly show CCB/promo/penalty deltas

## Phase B: Surface cleanup
- remove top-level Pricing Decision tab
- remove or demote Candidates / Analysis / Reports / Lessons
- keep Bundles as primary

## Phase C: Bundle upgrade
- reframe bundles around live products, not only selection candidates
- add same-family / same-scene / traffic+profit pairing logic

## Phase D: Naming cleanup
- rename `family_name` UI label -> `系列名稱`
- rename `variant_name` UI label -> `款式名稱`
- add operator examples under each field

---

## 12. Final conclusion

The main issue is not that the system lacks logic.
The issue is that:

- useful logic exists but is not explained clearly
- low-value modules still occupy primary space
- naming is too technical for the actual operator

The right direction is:

- keep the pricing engine
- make estimates explain themselves
- keep Bundles and strengthen them
- remove top-level research clutter
- rename family/variant into operator language

This will make the system:

- cleaner
- easier to trust
- easier to operate
- more obviously useful

