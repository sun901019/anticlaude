# E-commerce Operator Flow Design Optimization (2026-03-21)

## 1. Design Goal

This plan is not a full system rewrite.

The goal is to improve the current e-commerce operator experience inside the existing architecture by:

- simplifying product creation
- moving advanced settings to later surfaces
- making procurement easier to use
- improving pricing visibility
- introducing a more professional Shopee-inspired e-commerce visual language
- defining how AI agents should help refine the workflow

---

## 2. Current UX Problem

The current product creation flow is overloaded because it mixes too many concerns inside one Add Product modal.

The current modal mixes:

- product identity
- landed-cost inputs
- market and pricing details
- Shopee scenario controls
- role selection
- cost preview

This creates two problems:

1. Adding a product feels cognitively heavy.
2. Advanced settings appear before the operator actually needs them.

This should be fixed without rebuilding the whole e-commerce system.

---

## 3. Non-Goal

This optimization plan does **not** recommend:

- rewriting the whole e-commerce page
- replacing the whole information architecture
- removing the current fee engine
- redesigning everything into a new product

Instead, it recommends low-risk restructuring inside the existing system.

---

## 4. Target Experience

The operator experience should feel like this:

1. I found a product.
2. I add it quickly with only the fields I actually know.
3. The system immediately shows estimated landed cost and suggested prices.
4. I save the product first.
5. If I want more control, I open the product detail and adjust advanced settings there.

That should become the core interaction model.

---

## 5. Product Creation Flow Redesign

## 5.1 Quick Add Product

The Add Product modal should become a **Quick Add** surface.

### Required fields

- `sku`
- `product_name`
- `product_cost_rmb`
- `domestic_shipping_rmb`
- `shipping_mode`
- `goods_type`
- `initial_stock`

### Optional in Quick Add

- `notes`

### Remove from Quick Add default view

- `market_price_low`
- `market_price_high`
- `keyword`
- `supplier`
- `return_rate`
- `coupon_rate`
- `ad_budget`
- `ccb_plan`
- `is_promo_day`
- `fulfillment_days`
- manual role selection

These are not first-entry fields.

### Key rule

Quick Add should collect product facts, not environment simulation.

---

## 5.2 Quick Add Preview Panel

The live preview should become the center of the Add Product experience.

The panel should always show:

- landed total cost
- break-even price
- suggested traffic price
- suggested core price
- suggested profit price
- system-recommended role
- viability label

This should appear as soon as enough fields exist to compute it.

The user should feel:

"I already know whether this is interesting before I finish any advanced form."

---

## 5.3 Manual Role Selection Change

Current issue:

- the modal lets the operator choose a role
- while the system is also computing a suggested role

This creates semantic conflict.

### Better pattern

- Quick Add:
  - show `system suggested role`
- Product detail:
  - allow `manual role override`

This keeps the system helpful first and editable second.

---

## 6. Product Detail Redesign

After a product is saved, advanced settings should move into the product detail surface.

This can be a drawer or detail page.

### Recommended sections

#### Section A: Basic

- SKU
- name
- status
- role override
- notes

#### Section B: Cost & Logistics

- product cost RMB
- domestic shipping RMB
- shipping mode
- goods type
- weight
- packaging fee
- other cost

#### Section C: Pricing & Market

- target price
- market low/high
- keyword
- ad budget
- return rate
- coupon rate

#### Section D: Shopee Scenario

- CCB plan
- promo day
- prep days
- FSS mode or auto mode

#### Section E: AI Decision

- suggested price
- role fit
- price warning
- next recommendation

This keeps the first step simple while still preserving depth.

---

## 7. Procurement Flow Redesign

The current Add Inventory flow is too shallow.

It currently records:

- SKU
- cost RMB
- quantity
- purchase date
- supplier

That is not enough to help real restocking decisions.

### New procurement entry should include

- SKU
- quantity
- product unit cost RMB
- domestic shipping RMB
- shipping method
- exchange rate
- ETA
- notes

### Procurement preview should show

- total RMB
- estimated TWD
- estimated landed unit cost
- projected inventory after inbound

The procurement modal should answer:

"If I order this batch, what will my new cost basis and inventory situation look like?"

---

## 8. Move Settings Out of Product Creation

The current Add Product modal is noisy because system defaults are mixed with product inputs.

These should be moved into Settings:

- Shopee 2026 default fee environment
- exchange rate
- role margin presets
- ad budget presets
- shipping rate tables
- special goods premium
- low-stock threshold

### Product-level override still allowed

If a product needs a custom setting, it should override the global default inside product detail.

Priority order:

1. product override
2. scenario override
3. global default

This keeps creation simple while preserving accuracy.

---

## 9. Visual Direction: Shopee-Inspired, Not Shopee Clone

The current dashboard still uses the main AntiClaude purple accent language.

For the e-commerce area, a more domain-appropriate direction would improve professionalism.

### Recommended approach

Do not recolor the entire product.

Only give the e-commerce domain a local accent system inspired by Shopee:

- warm orange as primary commerce accent
- soft cream / warm neutral surfaces
- muted dark text
- restrained accent usage, not brand imitation

### Suggested e-commerce palette

- `commerce-accent`: `#EE4D2D`
- `commerce-accent-strong`: `#D93C1A`
- `commerce-accent-soft`: `#FFF1ED`
- `commerce-surface`: `#FFF8F4`
- `commerce-border`: `#F3D8CF`
- `commerce-text`: `#2E221D`
- `commerce-text-soft`: `#7A685F`

### Usage guidance

- use orange for CTA, recommendation emphasis, and e-commerce highlights
- keep main layout background neutral
- use soft orange only for supportive surfaces
- do not turn the whole dashboard into an orange wall

### Where to apply

- Add Product modal header accent
- price suggestion cards
- viability labels
- procurement CTA buttons
- e-commerce tab indicators

This gives the page a commerce identity without degrading the broader system aesthetic.

---

## 10. Layout and Hierarchy Recommendations

To reduce clutter, the e-commerce page should visually separate:

- product intake
- product management
- procurement
- performance
- AI recommendations

### Recommended page structure

#### Top zone

- key KPIs
- low-stock alerts
- review-required alerts

#### Middle zone

- products table
- quick actions

#### Detail zone

- side drawer / detail panel
- advanced pricing
- procurement history
- AI recommendations

This reduces the feeling that every action belongs inside one modal.

---

## 11. AI Employee Role in This Optimization

The operator asked for AI employees to help optimize the flow.

The best way to use them is not to let them all redesign randomly, but to assign clear roles.

### Lara

- decide the workflow split
- enforce that Quick Add only captures first-entry truth
- route advanced settings into detail/configuration surfaces

### Sage

- define pricing recommendation outputs
- validate role thresholds
- check whether the suggested role and suggested price are logically consistent

### Pixel

- refine the visual hierarchy
- introduce the e-commerce accent system
- reduce modal clutter
- make cards, status pills, and suggestion panels feel more intentional

### Lumi

- implement the front-end restructuring
- keep changes local to existing architecture
- ensure Add Product, product detail, and procurement flows align with the current backend

### Craft

- improve labels, helper text, empty states, warnings, and operator-facing copy
- make the system read like a practical sourcing tool instead of an internal calculator

---

## 12. Recommended Low-Risk Implementation Sequence

### Phase 1: Quick Add Simplification

- simplify Add Product modal
- remove advanced controls from default view
- keep live pricing preview visible

### Phase 2: Product Detail Expansion

- move advanced controls into detail drawer/page
- support role override and scenario override there

### Phase 3: Procurement Upgrade

- improve Add Inventory into a better restock workflow
- add landed-cost and stock-effect preview

### Phase 4: E-commerce Visual Polish

- apply local commerce color tokens
- improve CTA hierarchy
- improve recommendation visibility

This sequence improves UX without destabilizing the system.

---

## 13. Final Recommendation

The correct move is not a full rewrite.

The correct move is:

- make Add Product truly quick
- move complexity to later surfaces
- make pricing guidance visible immediately
- move environment defaults into Settings
- improve procurement ergonomics
- give the e-commerce area a more commerce-specific visual language

The result should feel like:

"Simple to add, clear to judge, powerful when I need more."
