# E-commerce Product Detail UX Rebuild Specification (2026-03-22)

## 1. Purpose

This document defines how the current product detail drawer / detail panel in the e-commerce system should be redesigned.

The goal is to make product detail feel:

- structured
- decision-oriented
- easy to scan
- easy to edit
- clearly separated between viewing and configuring

This is not a full page rewrite.
It is a targeted redesign of the product detail experience inside the current system.

---

## 2. Current Problem

The current product detail area is informative, but still feels messy.

The root issues are:

- too many information types appear at once
- "view" and "edit" are not clearly separated
- cost, pricing, market, notes, and inventory are visually too close together
- the operator has to mentally reorganize the data before acting

In other words:

The panel behaves like a data dump more than a product operating workspace.

---

## 3. Main Design Goal

When the operator opens a product detail, the system should immediately answer:

1. What is the current state of this product?
2. What does the system think should happen next?
3. Where do I go if I want to change something?

If the drawer does not answer these within a few seconds, it is not doing its job.

---

## 4. New Product Detail Structure

The product detail should be rebuilt into four layers.

## Layer A: Header Summary

This is the first visible block.

It should contain:

- product name
- SKU
- product status
- current role
- one-line product summary
- one-line AI recommendation

### Goal

Give the operator instant orientation.

### Example content

- `SKU: FL-016`
- `Status: Ad Testing`
- `Role: Core`
- `AI says: Margin is healthy, but stock may run out in 6 days.`

---

## Layer B: Decision Cards

This should be the most visually prominent area after the header.

Recommended cards:

- `Current Price`
- `Suggested Price`
- `Estimated Margin`
- `Stock Risk`
- `Next Action`

### Why

These are the values the operator cares about most.

The system should not force the operator to read cost breakdowns before seeing the final recommendation.

### Presentation rule

Use strong visual hierarchy:

- larger numbers
- clear labels
- colored emphasis only where helpful

---

## Layer C: Expandable Working Sections

After the summary and decision cards, show deeper sections.

These sections should be collapsible or tabbed.

### Section 1: Basic

Contains:

- name
- SKU
- notes
- status
- role override

### Section 2: Cost & Logistics

Contains:

- cost RMB
- domestic shipping RMB
- shipping mode
- goods type
- weight
- dimensions
- packaging fee
- extra cost

### Section 3: Pricing & Market

Contains:

- target price
- market low/high
- keyword
- ad budget
- break-even price
- suggested traffic/core/profit prices

### Section 4: Shopee Scenario

Contains:

- CCB
- promo day
- fulfillment/prep days
- FSS mode

### Section 5: Performance

Contains:

- current stock
- 7-day sales
- ROAS
- ad spend
- estimated margin
- recent action history

### Section 6: Notes & History

Contains:

- operator notes
- procurement history summary
- pricing history summary
- decision history

---

## Layer D: Actions Footer

The bottom of the detail panel should contain the main actions.

Recommended actions:

- `Edit Product`
- `Open Pricing Decision`
- `Add Procurement`
- `Update Performance`
- `Archive / Stop Product`

### Rule

Actions should not be hidden inside the information sections.
They should live in one obvious action zone.

---

## 5. Viewing vs Editing Separation

This is one of the most important fixes.

The current product detail should distinguish clearly between:

- read-only summary
- editable configuration
- historical records

### Recommended pattern

- default view: read-first
- edit mode: explicit

Do not make every block look editable all the time.

The operator should never wonder:

"Am I looking at current system output, or am I editing a setting?"

---

## 6. Information Hierarchy Rules

To remove the messy feeling, the drawer should follow this order:

1. identity
2. system recommendation
3. final decision signals
4. editable settings
5. supporting detail
6. historical context

This is the correct hierarchy.

### What should not happen

Do not begin with:

- raw cost details
- long notes
- low-signal metadata

These should come later.

---

## 7. Visual Design Direction

The product detail should use a commerce-local visual style that feels professional.

### Tone

- warm neutral base
- orange accent only on actionable/high-value outputs
- soft cards
- strong spacing and typography hierarchy

### Good emphasis targets

- suggested price
- next action
- low stock warning
- unhealthy margin
- role fit

### Bad emphasis targets

- every field
- every section header
- all historical data equally

The panel should feel calm, not loud.

---

## 8. What Should Be Reduced or Hidden

These should be de-emphasized inside product detail:

- low-value repeated descriptions
- duplicated pricing explanation already shown elsewhere
- redundant settings already managed globally
- fields the operator almost never changes

These can move into:

- collapsible "Advanced"
- "History"
- dedicated settings page

---

## 9. AI Agent Design Responsibilities

To optimize this panel properly, the AI employees should have distinct responsibilities.

## Lara

Role:

- structure owner

Responsibilities:

- define the panel hierarchy
- enforce the split between summary, decisions, details, and actions
- prevent scope creep into a full product rewrite

## Sage

Role:

- decision logic reviewer

Responsibilities:

- define which metrics deserve top placement
- validate role fit and recommendation logic
- ensure the panel answers "what should happen next?"

## Pixel

Role:

- visual design owner

Responsibilities:

- redesign the drawer layout
- define card emphasis
- tune spacing, section separation, and visual rhythm
- apply commerce color usage without clutter

## Lumi

Role:

- implementation owner

Responsibilities:

- refactor the current detail panel into layered sections
- preserve current data wiring
- keep interactions understandable and maintainable

## Craft

Role:

- operator copy owner

Responsibilities:

- improve labels
- reduce confusing wording
- rewrite helper lines, warnings, and system recommendation text

---

## 10. Recommended Build Order

### Phase 1

- redesign header summary
- add decision card row
- improve AI recommendation wording

### Phase 2

- reorganize cost/pricing/scenario/performance into collapsible sections
- separate read vs edit states

### Phase 3

- add action footer
- improve history section
- reduce duplicated content

### Phase 4

- visual polish
- spacing cleanup
- mojibake cleanup

---

## 11. Final Standard

The product detail experience should feel like:

- a focused operating panel
- not an overloaded side drawer

When the operator opens it, they should instantly know:

- what the product is
- whether the product is healthy
- what the system recommends
- what action is available next

That is the design target for this rebuild.
