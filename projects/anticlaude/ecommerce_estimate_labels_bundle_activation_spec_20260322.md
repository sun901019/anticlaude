# Ecommerce Estimate Labels, Scenario Visibility, and Bundle Activation Spec

Date: 2026-03-22
Owner: Codex
Scope: Flow Lab ecommerce operator surface

## 1. Purpose

This spec clarifies three operator-facing problems that are still causing confusion:

1. `System Estimate` is currently misunderstood as Shopee listing price.
2. `CCB / promo day / fulfillment day` are calculated in backend logic but are not surfaced clearly enough in the UI.
3. `Bundles` exist, but the operator cannot easily tell when bundle analysis is actually triggered or what logic it depends on.

This document also records the remaining cleanup work required to make the ecommerce workspace more intuitive and less noisy.

---

## 2. Current Verified State

The following points were verified directly from active code.

### 2.1 `System Estimate` is not Shopee selling price

In the current ecommerce product/inbound surfaces, the estimate shown in cost/logistics-related panels is **not** the final Shopee price.

It is currently one of the following:

- `landed_cost`
- `fixed_cost`
- `platform_fee_rate`
- inbound unit landed estimate
- total batch inbound estimate

So the current label `系統估算` is too vague.

### 2.2 Current backend pricing logic

In `src/ecommerce/router.py`, `calc_full_cost(...)` currently computes:

- product cost in TWD
- cross-border freight
- local shipping estimate
- packaging cost
- FSS cost
- commission cost
- transaction cost
- CCB cost
- promo cost
- fulfillment penalty cost
- risk cost
- coupon cost
- landed cost
- suggested prices
- role suggestion
- market warning

Verified formulas:

- `ccb_cost = selling_price * ccb_rate`
- `promo_cost = selling_price * promo_rate if (is_promo_day and ccb_plan != "ccb10") else 0`
- `penalty_cost = selling_price * penalty_rate if fulfillment_days > 2 else 0`

### 2.3 Current UI gap

Although backend math is active, the operator-facing display is still not explicit enough.

Current user confusion is reasonable because:

- numbers are shown without enough source labels
- `platform_fee_rate` looks like a complete fee summary, but it currently only reflects:
  - commission
  - transaction
  - FSS percent baseline
- promo/CCB/penalty are often only visible inside deeper breakdowns or not visually emphasized enough

### 2.4 Bundle analysis current trigger

Bundle analysis is **not always-on**.

Current trigger behavior:

- `loadBundles()` is called when top-level tab id becomes `bundles`
- `BundlesTab` renders existing product relations and AI suggestions
- operator can manually refresh bundle suggestions from inside the Bundles tab

This means the current bundle engine activates when:

1. the operator opens the `Bundles` tab
2. or explicitly clicks refresh inside the Bundles tab

### 2.5 Bundle logic current basis

The current AI bundle suggestion engine is still mostly selection-driven.

It relies on:

- candidate/category grouping
- recommended roles
- role pair combinations such as:
  - traffic + core
  - traffic + profit
  - core + profit

This is useful, but it is still closer to:

- selection analysis

than to:

- live product operation
- same family variants
- scene-based bundle selling
- accessory pairing

---

## 3. Direct Answers to Current Questions

## 3.1 What does `System Estimate` mean now?

Current meaning:

- in inbound: estimated landed unit cost and batch procurement impact
- in logistics/cost areas: landed cost and fee breakdown foundation

It does **not** mean:

- final Shopee listed selling price

So the current label should be changed.

### Recommended rename

Replace vague labels like:

- `系統估算`

with clearer business labels:

- `落地成本估算`
- `進貨落地估算`
- `平台費率摘要`
- `情境加成摘要`

This should remove the current mental mismatch.

## 3.2 Does `CCB` really affect calculation?

Yes.

It is calculated backend-side as:

- `ccb_cost = selling_price * ccb_rate`

Mapped examples:

- `none = 0%`
- `ccb5 = 1.5%`
- `ccb10 = 2.5%`

But the UI must show that clearly in small annotation text.

## 3.3 Does `Promo Day` really affect calculation?

Yes.

It is calculated backend-side as:

- `promo_cost = selling_price * promo_rate if is_promo_day and ccb_plan != "ccb10"`

Meaning:

- promo surcharge applies only when promo-day is enabled
- and it is waived for `ccb10`

The problem is not the formula itself.
The problem is that the operator does not get strong enough visual confirmation of the active scenario.

## 3.4 When can Bundles actually be used?

Current practical answer:

Bundles become useful when one of these exists:

1. existing product relations already saved
2. analyzed candidates with compatible roles and categories
3. operator opens Bundles tab and loads AI suggestions

Current activation path:

- open `Bundles`
- review saved bundle relations
- refresh AI bundle suggestions
- save bundle recommendations if useful

So right now it is **operator-invoked**, not background-always-on.

---

## 4. Required UI Clarifications

## 4.1 Every metric should show its source in small text

This is required.

Each displayed summary number should have a small sublabel showing exactly what it comes from.

### Example

#### `落地成本估算`

Small text:

- `商品成本 + 頭程/代購 + 跨境運費 + 包材`

#### `平台基礎費率`

Small text:

- `成交 6% + 金流 2.5% + FSS 6%`

#### `情境加成`

Small text:

- `CCB 1.5% + 活動日 2% + 備貨懲罰 3%`

#### `風險預估`

Small text:

- `退貨率 2% + 破損率 1% + 優惠券 0%`

This should be generated from current settings values, not hardcoded copy.

## 4.2 Promo-day state must be visually obvious

Current issue:

- operator clicks promo-day
- formula changes
- but current surface does not strongly communicate that the scenario is now in promo mode

Required improvement:

- show visible scenario chips near decision summary:
  - `平日`
  - `活動日 +2%`
  - `CCB5 +1.5%`
  - `CCB10 +2.5% / 活動日免加成`
  - `備貨 3 天 +3%`
- chips must stay visible even when advanced settings are collapsed

This is a direct operator trust issue.

## 4.3 `market_price_low` and `market_price_high` must live together

Current behavior:

- market high participates more strongly in warnings
- market low is mostly context

UX recommendation:

- keep both as one grouped section:
  - `市場價格帶`
- do not split them semantically

Display:

- `最低價`
- `最高可成交價`

Optional future expansion:

- hot-selling range
- premium sellable range

---

## 5. Feature Simplification Decisions

## 5.1 Remove top-level Pricing Lab / Pricing Simulation

Decision:

- remove or strongly demote it from the primary operator surface

Reason:

- product detail already contains most pricing decision behavior
- keeping a separate top-level pricing lab causes role overlap
- the operator should not need two different pricing workspaces for the same SKU

Replacement:

- pricing belongs inside product detail decision workflow

## 5.2 Remove Selection Research room from primary workspace

The following are low-value for current operator workflow and should be removed from the primary ecommerce work area:

- Candidates
- Analysis
- Reports
- Lessons

These can be:

- archived
- hidden behind a lab/tools area
- or removed from the ecommerce operator nav entirely

## 5.3 Keep Bundles and strengthen them

Bundles should remain.

They are one of the few secondary tools that have strong downstream business value.

They support:

- increasing AOV
- pairing traffic + profit items
- family/scene-based selling
- accessory/cross-sell design

---

## 6. Bundles: Required Product Direction

## 6.1 Bundles should shift from selection-driven to live-product-driven

Current logic is candidate/category/role oriented.

Target logic should gradually move toward:

- same family grouping
- scene pairing
- main product + accessory
- low-margin traffic item + higher-margin add-on
- style ladder
- room/desk/usage-theme matching

## 6.2 Bundles should present like this

### Section A: Existing bundle relations

Show:

- source product
- related product
- relation type
- scene
- notes

### Section B: AI bundle suggestions

Show:

- bundle name
- why this bundle is recommended
- included products
- combined original price
- bundle selling price
- estimated margin
- expected role logic

### Section C: Actionability

The operator should be able to:

- accept bundle suggestion
- edit bundle price
- add notes
- mark as:
  - draft bundle
  - testable bundle
  - active bundle

## 6.3 When should bundle analysis run?

Short answer:

- when the operator opens Bundles
- when bundle data needs refresh

Future improvement:

Bundle suggestions should also be refreshable when:

- a new family is created
- a new variant is added
- a new complementary live product is listed

---

## 7. Family / Variant Naming Cleanup

Current internal fields:

- `family_name`
- `variant_name`

Current problem:

- technically fine
- operator-unfriendly

Recommended operator labels:

- `系列名稱`
- `款式名稱`

### Operator examples

#### Same family

- 系列名稱: `躺贏招財貓`

#### Variants

- 款式名稱: `閒樂款`
- 款式名稱: `招財款`
- 款式名稱: `大尺寸款`

This makes the data-entry mental model much more intuitive.

---

## 8. Concrete Fixes Required

## 8.1 Rename labels

Replace:

- `系統估算`

with:

- `落地成本估算`
- `平台費率摘要`
- `情境加成摘要`

depending on context

## 8.2 Add source sublabels everywhere important

Must add small text under:

- landed cost
- platform fee rate
- scenario surcharge
- suggested price cards
- inbound estimate

These source labels must reflect current settings values dynamically.

## 8.3 Make promo-day state obvious

Required visible indicators:

- always-visible chips
- summary line in decision area
- not only hidden in advanced settings

## 8.4 Remove top-level Pricing Lab

- remove from primary nav
- keep pricing decision inside product detail only

## 8.5 Remove Selection Research from primary nav

Remove or demote:

- Candidates
- Analysis
- Reports
- Lessons

## 8.6 Keep and strengthen Bundles

- keep Bundles visible
- strengthen business logic
- shift toward family/live-product/scene logic

## 8.7 Improve operator wording

Replace engineering-facing wording with operator-facing wording:

- `family_name` -> `系列名稱`
- `variant_name` -> `款式名稱`

---

## 9. Recommended Execution Order

### Phase A

- rename estimate labels
- add source sublabels
- add stronger scenario chips for promo/CCB/fulfillment

### Phase B

- remove top-level pricing lab
- remove/demote selection research tabs from primary workspace
- keep Bundles only

### Phase C

- strengthen Bundles toward family/live-product usage
- align family/variant UX wording

### Phase D

- optional future expansion:
  - family-level bundle suggestions
  - bundle recommendations triggered by live product relationships

---

## 10. Final Recommendation

The ecommerce workspace should converge toward this:

- `在售商品`
- `補貨入庫`
- `組合設計`
- `系統設定`
- `操作手冊`

And remove or demote:

- `定價實驗室`
- `選品研究室`
  - Candidates
  - Analysis
  - Reports
  - Lessons

This will make the operator surface much cleaner and more aligned with the user's real workflow.
