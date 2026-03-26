# E-commerce Architecture Optimization Plan (2026-03-21)

## 1. Current State Assessment

The current e-commerce system is no longer a prototype.
It already has a usable working backbone:

- product management
- procurement entry
- pricing preview
- cost calculation
- performance updates
- role recommendation
- selection workflow
- settings support

This means the system is structurally viable.

However, it is not yet fully refined as a professional operator-grade product.

The current state is best described as:

- functionally strong
- structurally promising
- still carrying UX and architecture debt

---

## 2. What Is Already Strong

## 2.1 Clear functional coverage

The system already covers the major e-commerce work domains:

- products
- procurement
- performance
- pricing
- selection
- settings

## 2.2 Pricing engine exists

The system already has a meaningful pricing and fee engine.

It supports:

- Shopee 2026 fee assumptions
- role-based pricing output
- break-even and suggested pricing logic

## 2.3 The front-end is not empty

The e-commerce page already includes:

- Add Product
- Add Procurement
- product list
- product detail drawer
- pricing preview
- recommendation output

This means optimization can build on the current structure rather than requiring replacement.

---

## 3. Current Weak Points

## 3.1 Quick Add is still not pure enough

The Add Product experience still contains too many second-stage decisions.

The main issue:

- product facts
- scenario settings
- pricing assumptions
- advanced detail

are still too close together.

## 3.2 Product detail is not yet the full advanced workspace

A proper professional operator flow needs:

- fast first entry
- rich later detail

The system has the first half, but the second half is not fully realized yet.

## 3.3 Formula logic is duplicated

There is still duplication risk between:

- front-end calculations
- back-end calculations

This is dangerous because pricing logic should have one authority.

## 3.4 Settings ownership is not fully clean

Some values that should belong to global defaults are still too close to product creation.

Examples:

- CCB
- promo-day scenario
- prep-day penalty logic
- reusable rate assumptions

## 3.5 Visual system is improving but not fully unified

The e-commerce area is starting to gain a commerce-specific visual identity, which is good.

But it still feels partially mixed between:

- generic dashboard styling
- local commerce styling

## 3.6 Some operator trust issues remain

Examples:

- mojibake / garbled labels
- repeated concepts
- duplicated controls
- inconsistent wording between role, recommendation, and viability

---

## 4. Main Optimization Goal

The next phase should not add more random features.

The next phase should optimize for:

- clarity
- speed
- confidence
- maintainability
- decision support

The e-commerce system should feel like:

"A clean product operator console, not a crowded admin spreadsheet."

---

## 5. Recommended Architecture Model

The architecture should be mentally split into five operator layers:

### Layer A: Quick Intake

Purpose:

- register a product fast

### Layer B: Product Detail

Purpose:

- manage advanced per-product configuration

### Layer C: Procurement

Purpose:

- manage sourcing and inbound batches

### Layer D: Performance & Pricing Decisions

Purpose:

- review actual results and take actions

### Layer E: Global Defaults

Purpose:

- define reusable assumptions and fee environment

This layered model should become the UX structure.

---

## 6. Product Flow Optimization

## 6.1 Quick Add Product

Keep it minimal.

Required:

- SKU
- product name
- cost RMB
- domestic shipping RMB
- shipping mode
- goods type
- initial stock

Optional:

- notes

Move the rest out.

## 6.2 Product Detail

Use this as the advanced control center.

It should own:

- role override
- target price
- market high/low
- packaging
- extra cost
- ad budget
- return rate
- keyword
- Shopee scenario settings

## 6.3 Product table

The product table should prioritize decision usefulness.

Keep the primary fields visible:

- name
- SKU
- role
- margin
- price
- stock
- next action

Do not overload the main table with low-signal detail.

---

## 7. Procurement Optimization

Procurement should evolve from a simple record form into a restock decision tool.

Recommended procurement improvements:

- shipping method
- ETA
- total RMB
- estimated TWD
- landed unit cost
- projected stock after inbound
- procurement history visibility

The procurement interaction should tell the operator:

"What happens if I buy this batch?"

---

## 8. Pricing Engine Optimization

## 8.1 One source of truth

The back-end should become the sole authority for:

- total cost calculation
- role classification
- suggested selling price
- break-even price
- scenario-based fee logic

The front-end should render outputs and lightweight preview state, not become a second pricing engine.

## 8.2 Role standardization

The role model should be fixed and consistent:

- `< 25%` -> `not_suitable`
- `25% <= margin < 40%` -> `traffic`
- `40% <= margin < 50%` -> `core`
- `>= 50%` -> `profit`

## 8.3 Pricing display order

Show:

- break-even price
- traffic price
- core price
- profit price
- current target price
- suggested role

before the detailed formula explanation.

---

## 9. Settings Optimization

Settings should become the clear home of global defaults.

Move and centralize:

- Shopee fee presets
- exchange rate
- shipping defaults
- special goods premium
- return-rate default
- packaging default
- role margin targets
- role ad budget presets

This will reduce clutter elsewhere and improve consistency.

---

## 10. Visual and UX Optimization

## 10.1 Visual goal

The e-commerce area should feel:

- cleaner
- warmer
- more professional
- more commerce-native

## 10.2 Visual strategy

Use:

- neutral warm base
- commerce orange accent
- stronger typography hierarchy
- fewer but more meaningful surfaces

## 10.3 UX rule

Recommendation should visually dominate explanation.

The user should see:

- what the system thinks
- what action is recommended

before reading detailed fee mechanics.

---

## 11. What Should Be De-Emphasized

These are not always useless, but should no longer occupy prime space:

- long formula explanation blocks
- tutorial-like text inside working surfaces
- repeated settings controls across multiple screens
- duplicated summary cards that do not change action
- decorative blocks without decision value

These can be moved to:

- help/manual page
- collapsible panels
- secondary tabs

---

## 12. High-Priority Cleanup

Before calling the architecture "fully refined", these should be cleaned:

- formula duplication
- mojibake labels
- wording consistency
- role/recommendation semantics
- scenario/default separation
- local commerce token consistency

---

## 13. Suggested Execution Order

### Phase 1

- simplify Quick Add
- move advanced fields out
- keep recommendation preview central

### Phase 2

- strengthen product detail as advanced workspace
- improve procurement UX

### Phase 3

- centralize settings ownership
- reduce repeated controls

### Phase 4

- unify commerce-local visual language
- clean strings and wording

### Phase 5

- de-emphasize low-value instructional clutter
- finish formula/logic deduplication

---

## 14. Final Verdict

The e-commerce architecture is already good enough to build on.

It does **not** need a full rewrite.

What it needs is:

- simplification
- clearer ownership
- cleaner UX layering
- stronger visual consistency
- less duplication

The system is structurally strong.
The next step is to make it feel truly polished.
