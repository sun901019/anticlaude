# Flow Lab Pending + New Features Master Spec (2026-03-22)

## Purpose
This document consolidates:

- current ecommerce/Flow Lab progress
- confirmed improvements already shipped
- remaining convergence issues
- operator UX cleanup requirements
- architecture cleanup requirements
- the new Top-Down sourcing ceiling feature
- recommended execution order for Claude / Lara

This file is intended to become the single handoff file for the next iteration.

---

## 1. Current State Snapshot

### Verified baseline
- backend tests: `349 passed, 1 warning`
- frontend production build: pass

### What is already meaningfully improved

#### Ecommerce UI
- Quick Add is more intake-oriented than before
- QQL volumetric-weight feedback exists
- instant suggested-price card is clearer
- inbound/restock modal now shows:
  - current-vs-new landed cost comparison
  - ETA
  - projected stock coverage
  - AI-style restock suggestion
- product detail drawer now has:
  - header summary
  - decision cards
  - tab split (`pricing`, `cost`, `more`)
- manual/help has been moved closer to ecommerce-only content

#### Code organization
- `dashboard/src/app/ecommerce/components/` now exists
- extracted component files include:
  - `ecommerce-shared.tsx`
  - `ManualTab.tsx`
  - `CandidatesTab.tsx`
  - `AnalysisTab.tsx`
  - `SelectionTabs.tsx`

#### Test/build trust
- current engineering baseline is green again
- previous test-fixture failure has been fixed

---

## 2. What Is Still Not Fully Done

These are the important remaining gaps.

## 2.1 Ecommerce page is improved, but not yet properly converged

### Current issue
`dashboard/src/app/ecommerce/page.tsx` is still too large and still carries too many responsibilities.

Even after extraction work, the file remains very large and still directly owns:
- dashboard logic
- active products table
- pricing simulation
- settings
- manual
- inventory modal
- product detail drawer
- review mini-inbox filtering
- selection flow glue code

### Why this matters
- harder to maintain
- harder to debug
- future AI changes still risk touching too many concerns at once
- UI cleanup will keep feeling partial if structural separation is not finished

### Required direction
Continue breaking the page into responsibility-based pieces, not cosmetic pieces only.

Recommended next extraction targets:
- `ProductDrawer.tsx`
- `QuickAddModal.tsx`
- `InboundModal.tsx`
- `PricingSimulationTab.tsx`
- `SettingsTab.tsx`
- `ProductsTab.tsx`
- `PerformanceTab.tsx`

---

## 2.2 Pricing/business logic is still duplicated

### Current issue
Backend already has a canonical pricing engine:
- `src/ecommerce/router.py::calc_full_cost()`

But frontend still performs meaningful business computation:
- `calcPreview()`
- `fetchDrawerPrices()`
- market warning decisions
- role evaluation against local price bands
- cost/logistics display math inside drawer cost tab

### Why this matters
- same product can show different truth in different UI surfaces
- fee-rule changes require multiple edits
- operator trust drops if preview numbers diverge from saved/API numbers

### Required direction
Move toward:
- backend computes business truth
- frontend only renders:
  - preview request payload
  - structured backend response
  - lightweight display logic only

### Specific backend-owned outputs that should be returned
- landed cost
- price_traffic
- price_core
- price_profit
- suggested_role
- viability
- market_fit
- role_reasoning
- market_warning
- scenario_summary

### Specific frontend logic that should be removed or minimized
- direct role threshold comparisons
- local fee-rate composition
- local landed-cost math
- hardcoded market ceiling logic

---

## 2.3 Product detail drawer still mixes too many layers

### Current issue
The drawer is better, but the pricing tab still mixes:
- role selection
- price recommendations
- scenario controls
- target price input
- market context input
- role fit evaluation
- warning output

### Why this matters
The operator still has to mentally separate:
- what is fact
- what is scenario
- what is system output
- what is final decision

### Required direction
Product detail should become a true operator workspace with cleaner separation.

### Recommended drawer structure

#### Layer A — Header summary
- SKU
- name
- status
- role
- target price
- stock
- one-line AI summary

#### Layer B — Decision cards
- current target price
- traffic/core/profit suggested prices
- estimated margin
- stock health
- next action

#### Layer C — Sections/tabs

##### 1. Decision
Should contain only:
- role override
- suggested 3-price card
- target price
- market context
- result summary

Do not keep full scenario controls expanded by default.

##### 2. Logistics
Should contain only:
- procurement mode
- cost fields
- weight
- dimensions
- freight mode
- special-goods toggle
- read-only system estimate panel

##### 3. Ops
Should contain only:
- stock summary
- notes
- status
- buttons for:
  - update sales
  - restock
  - archive/delete

### Immediate micro-UX fix
Rename tabs for clarity:
- `pricing` -> `decision`
- `cost` -> `logistics`
- `more` -> `ops`

---

## 2.4 Top-level Pricing Simulation still overlaps with drawer pricing

### Current issue
Both places answer:
- what should I price this at
- what role does this fit
- what should I do next

### Why this matters
Duplicated entry points create operator hesitation:
- should I do this in the drawer?
- should I do this in pricing simulation?

### Required direction
Clarify responsibility:

#### Product detail pricing
- SKU-specific operational decision
- used after product exists

#### Pricing Simulation
- sandbox / what-if lab
- compare scenarios without editing product state
- useful before committing a price

### Recommended UX change
Rename top-level tab:
- from `定價模擬` or `定價決策`
- to `Pricing Lab` / `價格實驗室`

And clearly describe:
- does not modify product until saved elsewhere

---

## 2.5 Quick Add still contains fields that belong later

### What is right now
Quick Add is much better than before.

### What is still wrong
It still risks becoming half-intake, half-decision.

### Quick Add should only contain first-known facts

Keep:
- name
- SKU optional
- procurement mode
- cost RMB
- domestic shipping RMB
- weight
- dimensions only when needed
- initial stock optional

Move out of Quick Add:
- target price
- market range inputs
- ad budget
- CCB
- promo day
- fulfillment days
- role override
- notes

### Why
First-pass product intake must stay fast and low-friction.

---

## 2.6 Inbound/restock is better, but not fully product-grade yet

### What is already good
- cost delta vs product record
- ETA
- days coverage
- AI suggestion

### What still needs work
- stronger emphasis on landed unit cost
- stronger emphasis on cash needed
- stronger emphasis on stock coverage after restock
- clear warning severity

### Recommended outputs
The modal should answer these 5 questions instantly:
- how much cash am I spending?
- what is the new unit landed cost?
- when will stock arrive?
- how many days of stock will this buy me?
- is this restock too small / healthy / too aggressive?

### Recommended severity states
- under-order
- healthy restock
- over-stock risk
- no-sales-data yet

---

## 2.7 Market price fields are only partially used

### Current behavior
- `market_price_high` is partially used for warnings
- `market_price_low` is mostly stored/displayed, not deeply used

### What they should become
They should be optional market context, not required first-pass input.

### Recommended use
If filled:
- compare suggested price against ceiling/floor
- judge whether current role is market-fit
- produce clearer recommendation:
  - viable only as traffic
  - viable as core
  - can support premium/profit strategy

If not filled:
- do not block pricing output

### Future extension
Later, market context can upgrade from simple low/high to:
- floor price
- hot-selling band
- premium sellable band

But that is not required for the next step.

---

## 2.8 Manual/help should remain ecommerce-only

### Current direction
Correct and worth keeping.

### Required content scope
Keep only:
- product intake
- pricing logic
- QQL / 1688 sourcing logic
- inbound/restock
- weekly performance interpretation
- Shopee fee terms

### Remove/de-emphasize
- broad AI office/system instructions
- duplicated teaching inside active work screens

---

## 3. New Feature To Add: Top-Down Sourcing Ceiling Calculator

This is the new module that should be introduced next.

Reference:
- `projects/anticlaude/flow_lab_top_down_sourcing_ceiling_spec_20260322.md`

### Purpose
Allow the operator to start from market price and role target, then compute the maximum upstream sourcing cost ceiling.

### Why it matters
This supports a second sourcing workflow:

- Bottom-Up:
  - found a product cost first
  - ask what selling price is viable

- Top-Down:
  - found a hot market selling price first
  - ask what max sourcing cost is acceptable

This is especially useful for:
- 1688 screening
- QQL negotiation
- deciding whether to stop evaluating a supplier immediately

### Minimal required inputs
- target market price (TWD)
- target role
- estimated weight (kg)
- optional dimensions
- procurement mode

### Minimal required outputs
- target unit profit
- max landed cost
- freight reserve
- max sourcing cost in TWD
- max sourcing ceiling in RMB
- decision sentence

### Best placement
Do **not** bury this inside product detail first.

Better choices:
- separate `Top-Down Sourcing` tool
- or a second mode inside `Pricing Lab`

### Recommendation
Place it under the pricing/sourcing tool family, not inside Quick Add.

---

## 4. Architecture Cleanup Still Relevant

Although ecommerce UX is the current focus, the broader architecture cleanup still matters.

## 4.1 Task-type contract normalization
This was improved, but should remain monitored across:
- `src/agents/ceo.py`
- `_hub/registry/registry_schema.json`
- `src/agents/dynamic_orchestrator.py`
- `src/ai/skill_routing.py`

### Goal
Every task the CEO can route must be:
- registered
- handled
- skill-routed

## 4.2 Mojibake cleanup
This is no longer exploding everywhere, but it is still not safely "done".

### Why it still matters
- hurts operator trust
- hurts prompt quality
- hurts maintainability
- makes manual/help and agent copy look less professional

### Required approach
- keep scanning runtime-visible strings
- clean active UI text first
- clean active Python/runtime comments second
- archive/legacy text last

---

## 5. Recommended Execution Order

## Phase 1 — Convergence of existing ecommerce UX
1. Finish component extraction from `ecommerce/page.tsx`
2. Rename drawer tabs to role-based operator language
3. Continue slimming drawer decision tab
4. Remove repeated teaching copy from active work surfaces
5. Clarify `Pricing Lab` vs product-detail pricing responsibility

## Phase 2 — Pricing truth unification
6. Move pricing/business truth fully to backend responses
7. Remove duplicate frontend fee/landed-cost/role logic
8. Make frontend render-only for pricing outputs wherever possible

## Phase 3 — Restock/product operations polish
9. Strengthen inbound modal as a decision tool
10. Improve performance tab action priority and signal hierarchy
11. Keep manual ecommerce-only

## Phase 4 — New top-down tool
12. Add Top-Down Sourcing Ceiling Calculator
13. Connect it to current settings and role targets
14. Allow later handoff into normal product intake flow

---

## 6. Claude Implementation Priorities

If Claude only works on the next most valuable items, prioritize:

### Priority 1
- ecommerce page modularization
- pricing truth consolidation to backend

### Priority 2
- drawer tab cleanup
- pricing lab responsibility clarification
- inbound modal polish

### Priority 3
- top-down sourcing ceiling module

---

## 7. AI Agent Roles

### Lara
- enforce scope
- keep changes convergent, not expansive
- stop unnecessary feature sprawl

### Lumi
- extract components
- centralize backend pricing usage
- reduce page state complexity

### Pixel
- improve hierarchy, density, grouping, and visual quietness
- keep commerce styling professional and focused

### Sage
- validate pricing safety
- validate operator warnings
- ensure market/freight assumptions remain trustworthy

### Craft
- refine labels, hints, microcopy, manual text
- remove unnecessary cognitive load from operator language

---

## 8. Final Summary

The ecommerce system is no longer missing core capability.

The remaining job is:
- convergence
- deduplication
- role separation
- clearer operator flow
- stronger trust in system-calculated outputs

And after that:
- add the top-down sourcing ceiling module to complete the two-way pricing/sourcing decision system.
