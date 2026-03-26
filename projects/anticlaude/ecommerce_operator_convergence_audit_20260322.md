# Ecommerce Operator Convergence Audit (2026-03-22)

## Purpose
This document audits the current Flow Lab ecommerce experience from the operator point of view.
Focus:
- reduce mental load
- separate responsibilities more clearly
- remove duplicated pricing logic
- make product operations more direct and trustworthy

## Current Reality
The ecommerce system is already functional and fairly complete, but the operator experience still feels busy because one page is carrying too many different jobs at once.

The current `dashboard/src/app/ecommerce/page.tsx` still combines:
- dashboard summary
- active product management
- weekly performance
- pricing simulator
- settings
- manual/help
- candidate pool
- analysis
- bundles
- reports
- lessons
- quick add modal
- inbound/restock modal
- product detail drawer

This is the main reason the page feels heavy even when individual sections are not broken.

## Main Findings

### 1. Product facts, scenario settings, and global defaults are still mixed
These are three different layers:

- Product facts:
  - SKU
  - name
  - cost
  - domestic freight
  - weight
  - dimensions
  - packaging
  - supplier

- Scenario settings:
  - CCB plan
  - promo day
  - fulfillment days
  - ad budget
  - market high/low
  - target price

- Global defaults:
  - exchange rate
  - QQL fee
  - shipping rates
  - margin targets
  - default return/damage rates

The UI currently still lets these leak into each other, especially in Quick Add and product detail pricing.

### 2. Pricing remains duplicated between frontend and backend
Backend authority already exists in `src/ecommerce/router.py::calc_full_cost()`.
But frontend still performs local pricing-related work:

- `calcPreview()`
- local market warning decisions
- local role evaluation against drawer prices
- local landed-cost estimation inside the cost tab

This creates drift risk.

Desired rule:
- backend computes all business truth
- frontend only renders returned results

### 3. Quick Add is still not truly "quick"
The current Quick Add is improved, but it still tries to do too much.
For first-pass intake, the operator mainly needs:

- SKU
- product name
- procurement mode
- cost RMB
- domestic shipping RMB
- weight
- optional dimensions if QQL

Everything else should be delayed.

The current modal still includes:
- target price
- market low/high
- ad budget
- CCB
- promo day
- fulfillment days
- role override

These belong to later decision/configuration, not first capture.

### 4. Product detail drawer is improved but still overloaded
The drawer is much better than before, but it still mixes:

- editable inputs
- derived system estimates
- pricing strategy
- scenario switches
- stock actions
- status management

The current 3 tabs (`pricing`, `cost`, `more`) are not wrong, but the "pricing" tab still contains too many controls that should not sit together.

Better separation:

- Pricing Decision
  - read-mostly pricing output
  - role fit
  - market fit
  - one-click strategy picks

- Cost & Logistics
  - editable operational inputs
  - procurement mode
  - weight/dimensions
  - freight mode

- Product Ops
  - stock
  - status
  - notes
  - sales update
  - inbound/restock

### 5. Top-level "Pricing Simulation" tab overlaps with product detail pricing
The top-nav pricing tab is useful only if it has a clearly different purpose.

Right now it overlaps with the drawer because both try to answer:
- what should I price this at
- what is the margin
- what should I do next

Recommended positioning:
- Product detail pricing = SKU-specific operational decision
- Pricing Simulation tab = isolated what-if lab for comparing scenarios across one SKU

If that distinction is not strengthened, the tab should be de-emphasized in navigation.

### 6. Inbound/restock flow is useful but still too calculation-light
The inbound modal now shows more than before, but it should become a stronger decision tool.

Most helpful additions:
- estimated arrival date prominence
- projected stock coverage prominence
- landed unit cost prominence
- compare new landed unit cost vs current product cost
- risk wording:
  - under-order
  - healthy restock
  - over-stock risk

### 7. Manual/help is cleaner but should stay ecommerce-only
This direction is correct.
The manual should only explain:
- product intake
- pricing
- QQL / 1688 procurement
- restock
- performance interpretation
- Shopee fee terms

It should not drift back into broader AI office or general system help.

## Operator-Centered Convergence Plan

### A. Quick Add should become a 2-minute capture step
Keep only:
- SKU
- name
- procurement mode
- cost RMB
- domestic shipping RMB
- weight
- dimensions when QQL

Move out:
- target price
- market low/high
- ad budget
- CCB
- promo day
- fulfillment days
- role override
- notes

Quick Add output:
- product created
- initial landed-cost estimate
- initial suggested role
- "continue in product detail" CTA

### B. Product detail should become the main operator workspace
This should be the true place for ongoing product operation.

Recommended structure:

1. Header summary
- SKU
- name
- status
- role
- target price
- current stock
- one-line AI suggestion

2. Decision cards
- landed cost
- suggested traffic/core/profit prices
- current target price vs system recommendation
- margin health
- market fit

3. Tabs or sections
- Pricing Decision
- Cost & Logistics
- Product Ops

4. Action footer
- save changes
- update sales
- inbound/restock
- open pricing lab
- delete/archive

### C. Settings should remain low-frequency and clearly grouped
The current tab split is correct:
- platform
- sourcing
- ops

Improve by:
- adding one-line impact description per group
- reducing visual density
- surfacing only the few settings most likely to change often
- moving exotic values deeper if needed

### D. Performance should be more action-oriented
Weekly performance should show:
- gross margin
- ROAS
- stock risk
- next action

De-emphasize numbers that do not change decisions.
Highlight:
- raise price
- restock now
- keep testing
- stop/clear

### E. Navigation should reflect job frequency
Recommended priority:

Primary:
- Dashboard
- Active Products
- Performance

Secondary:
- Pricing Simulation
- Settings
- Manual

Tertiary / lower-emphasis:
- Candidates
- Analysis
- Bundles
- Reports
- Lessons

If tertiary areas remain in the same primary nav band, the page still feels crowded.

## Duplications to Remove

### Remove or reduce in frontend
- local role classification logic
- local market warning logic
- local landed-cost formula blocks
- local fee composition assumptions

These should come from backend response payloads.

### Keep only as UI state
- show/hide detail
- input drafts before save
- display formatting
- local optimistic preview shell if needed

## Specific UX Recommendations

### Recommendation 1: make scenario controls advanced, not default
CCB / promo day / fulfillment days should not dominate first-line workflows.
They should appear:
- in advanced pricing settings
- or behind a small "simulate Shopee scenario" expander

### Recommendation 2: treat market low/high as optional market context
This matches your workflow better.
If present:
- use for market fit and warning
If absent:
- do not block pricing recommendations

### Recommendation 3: make system estimates visually read-only
Operators trust the system more when derived numbers look stable.
Do not make estimated sections feel like editable spreadsheets.

### Recommendation 4: make inbound/restock feel like a buying decision
The modal should answer:
- how much cash is needed
- what landed cost will become
- when it arrives
- how many days of stock it buys
- whether that restock size is too small / healthy / too large

### Recommendation 5: reduce repeated teaching on work screens
Work pages should contain short hints only.
Long explanations belong in the ecommerce manual.

## High-Priority Refactors

1. Move pricing/business truth fully to backend and return richer structured results.
2. Slim Quick Add to first-pass intake only.
3. Rebalance product detail into a true operator workspace.
4. Reposition Pricing Simulation as a lab, not a second product detail.
5. Upgrade inbound modal into a decision tool, not just a form.
6. Keep manual ecommerce-only and move teaching text out of work views.
7. De-emphasize tertiary tabs in navigation.

## AI Agent Roles For This Optimization

### Lara
- enforce scope
- keep "no full rewrite" boundary
- ensure page responsibilities stay separated

### Lumi
- implement component extraction
- move business formulas to backend usage
- reduce page state coupling

### Pixel
- rework hierarchy, spacing, visual grouping, emphasis
- make commerce UI feel focused and professional

### Sage
- review pricing trust, warning clarity, operator safety
- validate that scenario controls do not mislead

### Craft
- tighten labels, microcopy, help text, CTA wording
- reduce operator confusion caused by mixed terminology

## Final Direction
The ecommerce system does not need a rebuild.
It needs convergence:

- less mixed responsibility
- less duplicated calculation
- fewer first-step fields
- stronger product detail workspace
- clearer navigation priority
- more stable system-truth presentation

That is what will make it feel direct, professional, and easier to trust.
