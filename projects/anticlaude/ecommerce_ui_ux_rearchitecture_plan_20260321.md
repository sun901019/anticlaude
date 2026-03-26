# E-commerce System UI/UX Rearchitecture Plan (2026-03-21)

## 1. Problem Statement

The current e-commerce product creation flow is too dense.

The operator experience is currently overloaded because:

- too many buttons appear inside the "Add Product" modal
- system-level pricing and fee controls are mixed into product creation
- product intake and product configuration are not clearly separated
- procurement entry is too primitive
- the operator is forced to think about advanced settings too early

This causes two UX failures:

1. Adding a product feels heavy instead of fast.
2. Important per-product settings are buried inside a noisy first-step form.

The redesign goal is to make the system feel like:

- quick to enter
- clear to understand
- expandable only when needed
- decision-supportive, not form-heavy

---

## 2. Design Direction

The system should be reorganized into three layers:

### Layer A: Global System Settings

These should not live inside the Add Product modal.

Move these into a dedicated system settings area:

- Shopee 2026 fee defaults
- exchange rate
- default return rate
- default damage/loss rate
- default low-stock threshold
- default shipping-mode rate tables
- default special-goods premium
- default role pricing presets

These are environment rules, not product-entry fields.

### Layer B: Quick Product Intake

This is the first product creation step.

The operator should only enter the minimum viable information required to register a product candidate.

### Layer C: Per-Product Detail Expansion

After a product exists, the operator can open a product detail panel and configure optional overrides:

- pricing strategy
- cost overrides
- market references
- logistics details
- promotion assumptions
- content strategy

This keeps product creation fast while still supporting deeper control.

---

## 3. Information Architecture

The recommended product system should be split into the following sections:

### 3.1 Dashboard

Purpose:

- monitor business state
- surface urgent action items
- summarize product health

Recommended blocks:

- estimated monthly revenue
- estimated monthly profit
- top 3 products by recent sales
- low-stock alerts
- products requiring price review
- products requiring restock review
- products with weak margin health

### 3.2 Products

Purpose:

- manage all products
- add products quickly
- open per-product detail and settings

Recommended sub-views:

- product table
- add product
- product detail drawer
- pricing preview
- status timeline

### 3.3 Procurement

Purpose:

- manage sourcing and restocking separately from product master data

Recommended sub-views:

- new procurement record
- procurement history
- cost conversion preview
- inbound inventory estimation

### 3.4 Performance

Purpose:

- update live performance data
- calculate product health

Recommended sub-views:

- performance update form
- profitability panel
- ROAS panel
- suggested next step

### 3.5 Selection

Purpose:

- evaluate product ideas before or alongside product launch

Recommended sub-views:

- candidate list
- AI analysis
- bundle ideas
- failure lessons
- markdown report viewer

### 3.6 Settings

Purpose:

- centralize system defaults and pricing environment

Recommended settings groups:

- Shopee fee presets
- logistics presets
- exchange rate
- role presets
- stock thresholds
- system assumptions

---

## 4. Product Creation UX Redesign

## 4.1 Current Problem

The Add Product interface currently tries to do too much:

- global environment selection
- product identity
- pricing assumptions
- logistics choices
- role logic
- fee conditions

This should be split.

## 4.2 New Product Creation Flow

### Step 1: Quick Add Product

Only show the fields the operator most likely knows immediately.

Recommended required fields:

- SKU
- product name
- product cost (RMB)
- 1688 domestic shipping (RMB)
- shipping mode
- goods type
- initial stock
- product status
- notes

Optional in quick add:

- target role

Do not show advanced fee and environment controls here by default.

### Step 2: Instant System Preview

Immediately after the basic fields are entered, show:

- landed cost estimate
- break-even price
- suggested traffic price
- suggested core price
- suggested profit price
- current viability label

This lets the operator decide whether to continue.

### Step 3: Save Product

Once saved, the product becomes editable in a richer detail panel.

---

## 5. Product Detail UX Redesign

After product creation, the operator should open a detail drawer or detail page.

This detail view should be divided into collapsible sections:

### Section A: Basic Info

- SKU
- name
- status
- role
- notes

### Section B: Cost and Logistics

- product cost RMB
- domestic shipping RMB
- shipping mode
- goods type
- weight
- packaging fee
- other cost

### Section C: Pricing Strategy

- suggested traffic price
- suggested core price
- suggested profit price
- chosen target price
- market low/high
- custom target margin
- ad budget assumption

### Section D: Shopee Environment

- promo day
- prep days
- FSS mode
- CCB mode

### Section E: Performance

- current price
- 7-day sales
- ad spend
- stock
- ROAS
- gross margin
- next action

### Section F: AI Recommendations

- price suggestion
- restock suggestion
- role suggestion
- warnings

The operator should only expand the sections they need.

---

## 6. Move Button Groups Out of Quick Add

The following controls are currently too noisy inside Add Product and should be moved out or hidden behind advanced sections:

- shipping mode presets with rate labels
- goods type switch
- CCB mode
- promo day
- prep days
- product role selector

Recommended new placement:

### Keep in Quick Add

- shipping mode
- goods type

Because these directly affect landed cost and are known early.

### Move to Product Detail or Settings

- CCB mode
- promo day
- prep days
- role overrides

These should be advanced controls, not part of fast intake.

### Move Fully to Global Settings

- rate tables
- default role presets
- default fee assumptions

These are environment controls and should not clutter product creation.

---

## 7. Suggested Pricing Display Model

The operator should always be able to see a pricing assistant panel.

Recommended visible outputs:

- break-even price
- traffic price suggestion
- core price suggestion
- profit price suggestion
- selected target price
- current estimated margin
- role fit
- market pressure warning

Recommended labels:

- Not Suitable
- Traffic
- Core
- Profit

The system should also explain:

- "At this price, estimated gross margin is X%"
- "At this price, product fits Core"
- "At current market ceiling, Profit is not realistic"

This makes the system useful as a decision tool, not only a calculator.

---

## 8. Procurement UX Redesign

## 8.1 Current Problem

Procurement is currently too thin and not ergonomic enough.

The operator needs a smoother flow for:

- selecting a product
- entering procurement batch info
- seeing currency conversion
- previewing updated inventory effect

## 8.2 Recommended Procurement Form

Fields:

- select SKU
- quantity
- product unit cost RMB
- domestic shipping RMB
- cross-border shipping method
- estimated cross-border shipping cost
- exchange rate
- arrival ETA
- notes

Live preview:

- total RMB
- estimated TWD
- estimated landed unit cost
- projected stock after inbound

### 8.3 Procurement History View

Each product should show:

- procurement history
- unit landed cost trend
- average procurement cost
- last restock date

This improves inventory decisions over time.

---

## 9. Settings Page Redesign

The Settings page should become the home of system assumptions.

Recommended sections:

### 9.1 Shopee Fee Environment

- base commission
- transaction fee
- promo surcharge
- long prep penalty
- FSS presets
- CCB presets

### 9.2 Logistics Defaults

- air cost table
- sea express cost table
- sea freight cost table
- special goods premium

### 9.3 Financial Defaults

- exchange rate
- default return rate
- default discount rate
- default packaging cost
- default ad budget presets

### 9.4 Role Presets

- traffic margin target
- core margin target
- profit margin target
- ad budget presets by role

This is where the system becomes configurable without polluting product intake.

---

## 10. Recommended Status Model

The current 10-stage product status flow is useful, but should be made easier to scan.

Recommended presentation:

- use a horizontal progress timeline on product detail
- use compact status pills in the product table
- keep editing status in detail, not as a heavy part of quick add

Suggested status sequence:

- inspiration
- research
- sample_possible
- sampled
- pending_evaluation
- launch_ready
- launched
- ad_testing
- scale
- stopped

---

## 11. Recommended Calculation Model

The system should distinguish between:

- global defaults
- product-level overrides
- scenario-level simulation

Priority order:

1. product override
2. scenario override
3. system default

This lets the operator:

- keep setup simple
- override only when needed
- maintain consistency across products

---

## 12. Recommended UI Pattern

The UI should move away from crowded button groups inside one modal.

Recommended pattern:

- quick-add modal for minimal entry
- persistent side preview panel for cost and price suggestion
- product detail drawer/page for advanced settings
- dedicated settings page for environment defaults

This creates a much clearer experience.

Avoid:

- too many toggles in one modal
- mixing defaults with per-product choices
- making the operator answer questions they do not know yet

---

## 13. Suggested Implementation Order

### Phase 1

- simplify Add Product modal
- move defaults into Settings
- add live pricing preview

### Phase 2

- add product detail drawer with collapsible sections
- support per-product overrides
- improve procurement entry

### Phase 3

- add full scenario simulation
- show pricing recommendation labels
- connect AI recommendations more tightly to product detail

### Phase 4

- improve dashboard action blocks
- procurement history analytics
- landed-cost trend analysis

---

## 14. Final Recommendation

The current system has strong logic, but the UX needs restructuring.

The correct redesign principle is:

- quick product creation
- advanced detail later
- system defaults centralized
- pricing suggestions always visible
- procurement separated from product identity

The operator should feel:

"I can add a product in seconds, then decide whether to go deeper."

That is the right experience for this system.
