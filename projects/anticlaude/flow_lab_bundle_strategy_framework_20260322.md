# Flow Lab Bundle Strategy Framework

Date: 2026-03-22
Owner: Codex
Purpose: Convert practical ecommerce bundle tactics into a reusable Flow Lab system framework.

---

## 1. Core Principle

Bundle design is not just "selling two items together".

Its real purpose is:

- reclaim pricing power
- raise average order value
- create margin structure
- reduce direct price comparison
- improve inventory efficiency

For Flow Lab, bundle design should become an operator tool for:

- pricing
- merchandising
- inventory movement
- profit optimization

---

## 2. Four Bundle Types

## 2.1 Exclusive Bundle

### Goal

- avoid direct comparison
- create a unique SKU
- raise margin

### Logic

- main product
- plus a very low-cost complementary item
- packaged as a differentiated kit

### Example

- office desk percussion item
- plus silent pad / anti-vibration accessory

### Why it works

Competitors may sell the main item alone, but they usually do not sell the same exact kit.

This gives the seller:

- higher pricing freedom
- less comparison pressure
- stronger perceived value

### System label

- `exclusive_bundle`

### What the system should calculate

- combined landed cost
- recommended bundle price
- expected gross margin
- estimated premium versus single-item sale

---

## 2.2 Add-On Bundle

### Goal

- increase order value
- capture "might as well buy one more" behavior
- monetize cart momentum

### Logic

- strong main item
- plus very cheap add-on item
- usually framed as a special add-on price

### Example

- drawer organizer
- plus low-cost stress toy add-on

### Why it works

The customer already decided to buy the main item.

The add-on:

- feels cheap
- does not add much fulfillment burden
- often becomes nearly pure incremental profit

### System label

- `add_on_bundle`

### What the system should calculate

- main item landed cost
- add-on landed cost
- add-on-only profit
- total order value increase
- whether the add-on still preserves acceptable blended margin

---

## 2.3 Multi-Buy Bundle

### Goal

- push quantity
- leverage low marginal fulfillment cost
- convert single-item buyers into multi-item buyers

### Logic

- same item
- or same family different variants
- sold as 2-pack / 3-pack / pair deal

### Example

- two desk ornaments
- same comfort item for office + home
- same giftable item in a pair offer

### Why it works

For many small items:

- the second item does not double shipping pain
- the package cost increase is small
- the revenue increase is meaningful

### System label

- `multi_buy_bundle`

### What the system should calculate

- single-item price
- bundle price
- bundle discount
- per-unit margin after discount
- total order value uplift

---

## 2.4 Inventory-Cleanup Bundle

### Goal

- move slow inventory
- protect value perception
- use a strong item to carry a weaker item

### Logic

- hot or stable traffic item
- plus slow-moving or overstock item
- reframed as a premium package / limited kit / desk set

### Example

- strong organizer item
- plus slower premium decor item

### Why it works

Instead of discounting the weak item directly and damaging price perception:

- it borrows traffic from the stronger product
- feels like a better-value package
- helps convert dead inventory into cash

### System label

- `inventory_cleanup_bundle`

### What the system should calculate

- inventory pressure score
- blended landed cost
- bundle margin
- weak-item stock relief impact
- whether the bundle still meets the minimum acceptable margin

---

## 3. Bundle System Surface

The `組合設計` module should not just show arbitrary combinations.

It should let the operator:

1. choose products
2. choose bundle type
3. see the system calculate the business logic
4. get a recommended bundle price
5. understand why the bundle is useful

### Required bundle builder inputs

- product A
- product B
- optional product C
- bundle type
- target role / target margin
- optional target price override
- optional bundle note

### Required outputs

- combined landed cost
- recommended bundle price
- original combined price
- discount amount
- expected gross margin
- bundle rationale
- recommended use case

---

## 4. Bundle Logic by Type

The system should not use one pricing rule for every bundle type.

### 4.1 Exclusive Bundle

Recommended logic:

- allow higher target margin
- emphasize uniqueness
- allow pricing above simple sum discount logic

Suggested system focus:

- premium perception
- differentiated package naming
- bundle note / story

### 4.2 Add-On Bundle

Recommended logic:

- optimize for conversion uplift
- allow lower standalone margin on the add-on
- preserve blended order profit

Suggested system focus:

- low friction
- checkout-friendly pricing
- incremental profit display

### 4.3 Multi-Buy Bundle

Recommended logic:

- compare:
  - 1-item margin
  - 2-item total profit
  - 2-item per-unit margin
- show whether second-item discount is still worth it

Suggested system focus:

- order size uplift
- shipping dilution
- gift/dual-use rationale

### 4.4 Inventory-Cleanup Bundle

Recommended logic:

- factor in slow item urgency
- allow slightly lower margin if it releases stuck inventory
- protect visual value of the weak item

Suggested system focus:

- inventory turnover
- cash conversion
- non-destructive discounting

---

## 5. Bundle Recommendation Engine Upgrade

Current bundle logic is still too candidate-oriented.

Future recommendation logic should include:

- same family
- same scene
- main product + accessory
- traffic item + profit item
- home/office dual-use logic
- price ladder logic
- overstock relief logic

### Recommended bundle recommendation classes

- `traffic_bundle`
- `profit_bundle`
- `scene_bundle`
- `cleanup_bundle`

This makes the result understandable immediately.

---

## 6. How It Should Appear in the UI

## 6.1 Bundle list

Each suggested bundle should show:

- bundle name
- bundle type
- included products
- original total price
- recommended bundle price
- estimated margin
- short explanation

## 6.2 Bundle detail

Each bundle detail card should show:

- why these items belong together
- what strategy it serves
- whether it improves:
  - margin
  - order value
  - inventory turnover
- whether it should be:
  - tested
  - launched
  - rejected

## 6.3 Action buttons

Operator actions should include:

- save draft bundle
- mark as test bundle
- activate
- reject

---

## 7. Recommended Operator Workflow

### Path A: Starting from products you already sell

1. open `組合設計`
2. select live products
3. choose bundle type
4. let system calculate combined landed cost
5. review suggested price and margin
6. save or activate

### Path B: Starting from a strong product

1. choose a traffic/main product
2. system suggests compatible add-ons or premium companions
3. review margin and strategy fit
4. create bundle draft

### Path C: Starting from stock pressure

1. choose slow-moving product
2. system suggests strong companion products
3. review cleanup bundle pricing
4. activate if margin is acceptable

---

## 8. Relationship with Family / Variant

Bundle design should work together with family/variant grouping.

### Family

- the broader product concept
- example: `躺贏招財貓`

### Variant

- style / version / size / color / finish
- example: `閒樂款`

### Why this matters for bundles

Because bundles can then support:

- single item
- upgraded variant
- pair bundle
- premium family set

This is much more realistic than treating all related products as fully unrelated flat rows.

---

## 9. Required System Fields

Minimum fields for bundle calculation:

- `bundle_type`
- `product_ids`
- `base_price_sum`
- `bundle_price`
- `estimated_margin`
- `strategy_reason`
- `bundle_status`

Recommended additional fields:

- `scene`
- `family_context`
- `inventory_pressure_score`
- `aov_uplift`
- `incremental_profit`

---

## 10. Final Recommendation

Flow Lab should treat bundle design as a first-class operator tool.

The final objective is not:

- randomly suggesting product pairs

The final objective is:

- helping the operator choose the right bundle strategy for the right business purpose

That means every bundle should answer:

- why these products belong together
- what business problem this bundle solves
- what price it should use
- whether it improves margin, AOV, or inventory movement

This is the standard the `組合設計` module should now aim for.
