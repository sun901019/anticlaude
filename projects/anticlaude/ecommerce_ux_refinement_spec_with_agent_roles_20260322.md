# E-commerce UX Refinement Specification with Agent Roles (2026-03-22)

## 1. Purpose

This specification consolidates the current e-commerce refinement direction into one execution-ready UX design plan.

It focuses on:

- reducing clutter
- separating concerns
- improving pricing confidence
- making the system easier to operate daily
- assigning clear AI agent responsibilities for refinement work

This is not a full rebuild.
It is a structured refinement plan for the existing system.

---

## 2. Core Diagnosis

The current feeling of "messiness" is real and technically explainable.

The root cause is not that the system has too many capabilities.
The root cause is that one screen still mixes too many dimensions of work:

- procurement intake
- pricing simulation
- inventory/procurement updates
- global environment settings

This is a classic over-coupling problem.

The system should therefore be optimized by splitting responsibilities more clearly, not by deleting core capability.

---

## 3. Primary UX Goals

The target operator experience should be:

- simple at first touch
- deeper only when needed
- visually structured
- recommendation-led
- professional and trustworthy

The operator should feel:

"I understand what I need to fill in, what the system is calculating, and what I should decide next."

---

## 4. Main Refinement Directions

## 4.1 Settings Page Split

### Problem

The current settings experience mixes too many unrelated variables into one visual surface.

Examples:

- Shopee platform fee variables
- procurement/logistics variables
- QQL variables
- risk assumptions

This creates unnecessary cognitive pressure.

### Recommendation

Split the settings page into 3 tabs:

#### Tab A: Platform Fees

Includes:

- base Shopee commission
- transaction fee
- free-shipping fee
- promotion-day surcharge
- long-prep penalty

#### Tab B: Sourcing & Logistics

Includes:

- standard logistics defaults
- QQL exchange rate
- QQL service fee
- sea-express rate
- volumetric divisor
- shipping-related assumptions

#### Tab C: Operations & Risk

Includes:

- role margin thresholds
- return-rate default
- damage/loss-rate default
- low-stock threshold
- ad budget presets

### Why this improves the system

Settings are low-frequency actions.
They should be easy to locate, calm to scan, and grouped by mental model.

---

## 4.2 Add Product Flow Refinement

### Problem

The Add Product flow still asks too much too early.

### Recommended Quick Add fields

Keep only:

- SKU
- product name
- 1688 cost
- domestic shipping
- shipping mode
- goods type
- initial stock
- notes

### Move out of first-step flow

- market low/high
- target price
- ad budget
- CCB
- promo day
- fulfillment/prep days
- advanced role handling

### Additional improvement: volumetric protection

Add optional size fields:

- length
- width
- height

When present, show immediate system feedback:

- calculated volumetric weight
- billing weight used
- warning if volumetric weight exceeds actual weight

### Why this matters

This is not cosmetic.
It prevents real cross-border margin mistakes.

---

## 4.3 Pricing Decision Drawer / Panel Refinement

### Problem

The pricing panel still compresses too much information into one visual surface.

### Recommended information hierarchy

Split it into 3 explicit sections:

#### Section A: Cost Inputs

Operator-entered facts:

- 1688 cost
- domestic shipping
- weight / size
- packaging cost

#### Section B: System Calculations

Mostly read-only outputs:

- procurement cost
- logistics cost
- landed cost
- fee burden

If the operator wants to edit logistics/scenario assumptions, expose a small "edit" action instead of mixing all controls in the same visual block.

#### Section C: Pricing Decisions

The most visually prominent section.

Show:

- break-even price
- traffic price
- core price
- profit price
- suggested role
- margin result
- market pressure warning

### Scenario toggles

Put fast scenario toggles here, not in the intake form:

- promotion day
- long-prep / pre-order
- CCB plan
- FSS mode

### Why this improves the system

The operator's goal on this surface is not to "fill a form".
It is to decide a selling price.

---

## 4.4 Procurement / Restock Flow Refinement

### Problem

Procurement is improved, but still not fully decision-oriented.

### Recommended restock form

Include:

- SKU
- quantity
- cost RMB
- shipping method
- ETA
- supplier
- notes

### Required live outputs

- total RMB
- estimated TWD
- landed unit cost
- projected stock after inbound
- if target price exists: cost-to-price pressure

### Why this improves the system

The operator should understand the impact of the batch immediately, not only record it.

---

## 5. Visual and Layout Refinement

## 5.1 Overall direction

The e-commerce area should feel like a professional commerce operator console.

Recommended tone:

- warm neutral base
- Shopee-inspired orange accent
- restrained use of strong color
- strong hierarchy
- fewer noisy surfaces

## 5.2 Recommended local e-commerce palette

- `commerce-primary`: `#EE4D2D`
- `commerce-primary-strong`: `#D93C1A`
- `commerce-primary-soft`: `#FFF1ED`
- `commerce-surface`: `#FFF8F4`
- `commerce-border`: `#F3D8CF`
- `commerce-text`: `#2E221D`
- `commerce-muted`: `#7A685F`

## 5.3 Usage rule

Use orange for:

- primary CTA
- pricing recommendation panels
- operator prompts
- status emphasis

Do not use orange everywhere.
The page should feel premium, not loud.

---

## 6. Page-by-Page Simplification Rules

## 6.1 Products

Main job:

- manage products

Should prioritize:

- active products
- margin health
- stock health
- next action

Do not overload with explanation blocks.

## 6.2 Weekly Performance

Main job:

- show weekly change and required intervention

Prioritize:

- what changed
- which products worsened
- what to do next

## 6.3 Pricing Decision

Main job:

- choose a price

Recommendation must appear before fee mechanics.

## 6.4 Settings

Main job:

- control defaults

This page should be calm, tabbed, and low-noise.

## 6.5 Manual / Help

Main job:

- explain terms and workflow

Move deeper explanation here instead of crowding work pages.

---

## 7. Duplication and Cleanup Targets

The following still need cleanup:

### Logic duplication

- pricing calculations in more than one place
- role classification duplicated between surfaces
- repeated CCB/promo/FSS logic

### UX duplication

- repeated explanatory cards
- duplicated setting controls
- repeated warnings shown in multiple places

### Trust issues

- mojibake / garbled strings
- inconsistent naming
- mixed wording for role/recommendation/viability

---

## 8. AI Agent Responsibilities

## 8.1 Lara

Primary role:

- workflow and scope control

Responsibilities:

- enforce the split between Quick Add, product detail, procurement, and settings
- prevent scope creep into a full rewrite
- decide which settings belong globally vs per-product

## 8.2 Sage

Primary role:

- pricing logic validation

Responsibilities:

- verify role thresholds
- verify pricing output hierarchy
- verify scenario simulation logic
- confirm which metrics are decision-critical

## 8.3 Pixel

Primary role:

- visual hierarchy and polish

Responsibilities:

- apply commerce-local tokens
- reduce visual clutter
- improve card hierarchy
- refine spacing, sectioning, and emphasis

## 8.4 Lumi

Primary role:

- UI implementation

Responsibilities:

- modify current pages without rewriting the system
- simplify Add Product
- improve procurement UX
- restructure detail surfaces
- preserve build stability

## 8.5 Craft

Primary role:

- operator language and product clarity

Responsibilities:

- improve labels
- improve helper text
- rewrite warnings and descriptions
- reduce confusing copy

---

## 9. Recommended Execution Order

### Phase 1: High-impact cleanup

- clean mojibake
- simplify Quick Add
- move advanced fields out of first-step flow

### Phase 2: Decision-surface refinement

- restructure pricing panel into 3 sections
- improve procurement preview
- improve product detail grouping

### Phase 3: Settings refinement

- split settings page into tabs
- centralize defaults

### Phase 4: Visual polish

- unify e-commerce color tokens
- improve hierarchy and spacing

### Phase 5: Final cleanup

- remove duplicated explanation blocks
- reduce repeated settings controls
- ensure wording consistency

---

## 10. Final Standard

The e-commerce system should not feel like:

- a giant form
- a spreadsheet with buttons
- a tutorial page

It should feel like:

- a focused operator console
- a pricing and sourcing decision tool
- a professional commerce workflow system

The final design question for every surface should be:

"Is it obvious within 5 seconds what this page is for and what the operator should do next?"
