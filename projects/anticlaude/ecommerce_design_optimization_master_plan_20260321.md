# E-commerce Design Optimization Master Plan (2026-03-21)

## 1. Purpose

This document is the single implementation-facing design plan for improving the current e-commerce system.

It is intended to be given directly to Claude / Lara / implementation agents.

This plan covers:

- product structure
- page presentation
- Add Product UX
- product detail UX
- procurement UX
- pricing display
- visual language
- settings separation
- feature/logic deduplication
- low-value feature de-emphasis

Important scope rule:

- do **not** rebuild the whole e-commerce system
- improve the current implementation
- reduce clutter
- improve decision clarity
- make the product feel more professional and easier to use

---

## 2. Main Product Goal

The e-commerce system should become:

- easy to use daily
- visually clean
- clearly structured
- recommendation-first
- not overloaded with repeated controls
- not crowded with explanations and duplicated formulas

The operator should feel:

"I can add products quickly, understand the recommendation immediately, and go deeper only when needed."

---

## 3. Design Standard

The target experience is:

- calm
- professional
- commerce-oriented
- not messy
- not repetitive
- not tool-noisy

The system should not feel like:

- a giant calculator
- a dev dashboard
- a stack of repeated cards
- a form asking too many early questions

---

## 4. Current Verified Problems

These are the main issues still present in the current system:

1. Add Product is improved but still too heavy.
2. Shopee scenario controls still live inside Add Product.
3. Product detail is still only partially a true advanced workspace.
4. Procurement flow is better but still not a full restock decision tool.
5. Some labels/helper text still contain mojibake.
6. E-commerce visual direction has improved but is not fully unified.
7. Pricing and margin logic exist in both front-end and back-end, which creates duplication risk.
8. Some explanatory blocks and settings are still too visible in primary work surfaces.

---

## 5. Core Product Structure

The e-commerce area should be treated as five clear work surfaces:

1. `Products`
2. `Procurement`
3. `Weekly Performance`
4. `Pricing Decision`
5. `Settings`

And one support surface:

6. `Manual / Help`

Each surface must have one clear job.

---

## 6. Products Page

## 6.1 Main Job

Manage active products and quickly see what needs action.

## 6.2 Recommended layout

### Header

- title
- one-line purpose
- only 1-2 primary actions:
  - Quick Add Product
  - Add Procurement

### Summary row

Short decision cards only:

- needs repricing
- low stock
- weak margin
- scale candidates

### Main table

Columns should prioritize decision usefulness:

- SKU
- name
- status
- role
- target price
- estimated margin
- stock
- next action

### Product detail drawer

This is where advanced settings and deeper review should happen.

---

## 7. Quick Add Product

## 7.1 Main Job

Create a product quickly using only first-known facts.

## 7.2 Required fields

- `sku`
- `name`
- `cost_rmb`
- `head_freight_rmb`
- `freight_type`
- `goods_type`
- `init_stock`

## 7.3 Optional field

- `notes`

## 7.4 Remove from default Quick Add view

These should not be visible in the main Add Product flow:

- market low/high
- keyword
- supplier
- return rate
- coupon rate
- ad budget
- CCB plan
- promo day
- fulfillment days
- manual role selection

## 7.5 Always-visible preview

The preview should become the center of the modal.

Always show:

- landed cost
- break-even price
- suggested traffic price
- suggested core price
- suggested profit price
- suggested role
- viability label

## 7.6 Key rule

Quick Add should feel like registration plus recommendation, not setup plus simulation.

---

## 8. Product Detail View

## 8.1 Main Job

Handle advanced per-product configuration.

## 8.2 Required sections

### A. Basic

- SKU
- name
- status
- role override
- notes

### B. Cost & Logistics

- cost_rmb
- head_freight_rmb
- freight_type
- goods_type
- weight
- packaging cost
- extra cost

### C. Pricing & Market

- target price
- market low/high
- ad budget
- keyword
- role explanation

### D. Shopee Scenario

- CCB
- promo day
- prep days
- FSS mode / auto

### E. Performance

- sales
- ROAS
- stock
- margin
- next action

### F. AI Recommendation

- suggested price
- suggested role
- risk warning
- market-fit warning

## 8.3 Presentation rule

Do not dump all fields into one flat form.
Use grouped sections, tabs, or collapsible blocks.

---

## 9. Procurement Flow

## 9.1 Main Job

Help the operator decide what a new batch means, not just record inventory.

## 9.2 Required fields

- SKU
- quantity
- unit cost RMB
- purchase date
- supplier

## 9.3 Recommended additions

- shipping method
- ETA
- notes

## 9.4 Live preview should show

- total RMB
- estimated TWD
- landed unit cost
- projected stock after inbound
- cost ratio against target price if available

## 9.5 Goal

The procurement modal should answer:

"If I buy this batch, what does it do to cost and stock?"

---

## 10. Weekly Performance Page

## 10.1 Main Job

Show what changed this week and where intervention is needed.

## 10.2 Required content

- weekly revenue
- weekly profit
- average margin
- products that worsened
- products that improved
- low-stock risk
- action recommendations

## 10.3 Presentation rule

Focus on change and action, not static metrics only.

The page should answer:

"What changed this week, and what should I do?"

---

## 11. Pricing Decision Page

## 11.1 Main Job

Convert cost logic into an actual pricing decision.

## 11.2 Required output order

Show these first:

- break-even price
- traffic price
- core price
- profit price
- current target price
- resulting margin
- matched role
- warning if market cap is too low

Only after that show:

- fee breakdown
- formula details
- simulation mechanics

## 11.3 Rule

Recommendation first, mechanics second.

---

## 12. Settings Page

## 12.1 Main Job

Own the global environment and defaults.

## 12.2 Move these here

- Shopee fee defaults
- exchange rate
- shipping rate presets
- special goods premium
- return-rate default
- packaging default
- role preset targets
- ad budget presets

## 12.3 Important rule

Defaults should not be repeatedly editable inside every workflow.

Settings should be the stable home of reusable assumptions.

---

## 13. Manual / Help Page

## 13.1 Main Job

Explain terms and workflow when the operator needs context.

## 13.2 Recommended sections

- Shopee pricing terms
- procurement workflow
- role logic
- pricing logic
- FAQ

## 13.3 Rule

Working pages should have short inline help.
Long explanations belong here, not everywhere.

---

## 14. Pricing and Formula Rules

## 14.1 Single source of truth

Pricing and cost formulas should have one authority.

Recommended source of truth:

- backend `calc_full_cost()`

## 14.2 Front-end role

The front-end should display:

- backend output
- preview state
- user-facing explanation

It should not duplicate complex pricing logic when avoidable.

## 14.3 Dedup targets

Reduce duplication of:

- role classification
- CCB rules
- promo surcharge rules
- FSS switching logic
- suggested price formulas

---

## 15. Role Semantics

Use one consistent role classification:

- `< 25%` -> `not_suitable`
- `25% <= margin < 40%` -> `traffic`
- `40% <= margin < 50%` -> `core`
- `>= 50%` -> `profit`

Distinguish clearly between:

- `system suggested role`
- `manual role override`

Do not mix them in the same first-step interaction.

---

## 16. Shopee Scenario Controls

These controls are useful but should not dominate Quick Add:

- CCB
- promo day
- fulfillment days

Recommended placement:

- product detail
- pricing decision page
- settings defaults

Do not keep them as main-first-entry inputs.

---

## 17. Visual Language

## 17.1 Base system style

Use:

- warm neutral backgrounds
- calm borders
- strong typography hierarchy
- limited shadow use

## 17.2 E-commerce local accent

Use a Shopee-inspired orange accent for e-commerce surfaces only.

Suggested palette:

- `#EE4D2D`
- `#D93C1A`
- `#FFF1ED`
- `#FFF8F4`
- `#F3D8CF`
- `#2E221D`
- `#7A685F`

## 17.3 Apply orange to

- CTA buttons
- recommendation cards
- pricing panels
- restock prompts
- action highlights

## 17.4 Do not use orange for

- every card
- the whole page background
- body text everywhere

The page should feel premium, not loud.

---

## 18. Layout Rules

Use this product-wide layout rule:

### Zone A

Header + main purpose + primary action

### Zone B

Critical summary / KPIs / alerts

### Zone C

Main work surface

### Zone D

Secondary details / advanced settings / history

This should replace long undifferentiated pages.

---

## 19. Low-Value or Secondary Features

These should be reduced, moved, or de-emphasized if still prominent:

- long formula explanation blocks on work pages
- tutorial-style sections inside active workflow pages
- duplicated environment settings across multiple screens
- repeated analytics summaries that do not change action
- decorative cards with no decision value

Do not necessarily delete them.
Move them behind:

- help drawers
- "learn more"
- secondary tabs
- collapsible panels

---

## 20. High-Priority Cleanup

These are still important:

- mojibake string cleanup
- wording consistency
- review/approval wording clarity
- front-end and back-end formula deduplication
- visual token consistency

---

## 21. Recommended Implementation Order

### Phase 1

- simplify Quick Add
- promote preview panel
- remove advanced controls from first-step flow

### Phase 2

- improve product detail into real advanced workspace
- improve procurement workflow

### Phase 3

- move defaults into Settings
- reduce repeated controls

### Phase 4

- unify commerce color tokens
- refine typography and hierarchy
- clean remaining mojibake

### Phase 5

- de-emphasize low-value instructional clutter
- tighten weekly performance and pricing decision pages

---

## 22. Final Standard

The system should feel like:

- a premium operator console
- not a noisy admin system
- not a repeated set of forms
- not a teaching wall

The final product should optimize for:

- speed
- clarity
- trust
- decision support

The standard question for every screen should be:

"What should the operator do next, and is that obvious within 5 seconds?"
