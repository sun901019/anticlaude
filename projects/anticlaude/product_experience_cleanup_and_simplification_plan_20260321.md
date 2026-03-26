# Product Experience Cleanup and Simplification Plan (2026-03-21)

## 1. Objective

This document defines the next-level refinement plan for the overall AntiClaude product experience.

Focus areas:

- architecture clarity
- layout and visual hierarchy
- color direction
- user experience simplification
- removal or de-emphasis of low-value features

The goal is not to remove capability.
The goal is to reduce friction, reduce noise, and increase operator trust.

---

## 2. Current Overall Assessment

The system is already powerful, but it is starting to carry the typical cost of rapid feature growth:

- too many entry points
- too many surfaces with similar concepts
- too many settings shown too early
- mixed visual languages
- a few pages feel productized, others still feel tool-like

This means the next stage should focus less on adding features and more on:

- simplification
- consistency
- readability
- prioritization

---

## 3. Architecture-Level Recommendations

## 3.1 Clarify the Product Pillars

The UI should make the product feel like four clear pillars:

- `Command`
  - CEO Console
  - Review
  - Morning
- `Operate`
  - E-commerce
  - Flow Lab
  - Office
- `Observe`
  - Reports
  - Metrics
  - Insights
- `System`
  - Settings
  - Figma
  - System health

This gives the product a clearer mental model.

### Recommendation

Use these pillars more intentionally in navigation and page grouping.

---

## 3.2 Reduce Concept Overlap

There are several concepts that are currently too close together:

- review vs approvals
- flowlab vs ecommerce
- reports vs insights vs metrics
- office vs chat vs morning

These should stay separate technically, but be presented more clearly in UX.

### Recommendation

Use page subtitles and inline helper text to explain:

- what this page is for
- what it is not for
- what decision the operator should make here

---

## 4. Layout Recommendations

## 4.1 Stronger Page Structure

Several pages still feel like long tool dashboards rather than intentional product surfaces.

Recommended default page layout pattern:

### Zone A: Page header

- title
- one-line purpose
- 1 to 2 primary actions only

### Zone B: Critical summary

- KPIs
- alerts
- required approvals
- system recommendations

### Zone C: Main workspace

- table
- editor
- timeline
- analysis panel

### Zone D: Secondary detail

- advanced settings
- notes
- history
- low-priority diagnostics

The key principle:

Do not let every page become one continuous pile of cards and controls.

---

## 4.2 Reduce Modal Dependence

The project currently relies heavily on modal interactions.

This creates fatigue and hides context.

### Recommendation

Use this pattern:

- modal for quick-create
- drawer for detail inspection
- full page for serious work

This will make the system feel more mature.

---

## 5. Color and Visual Language Recommendations

## 5.1 Current Issue

The visual system is partially split:

- some pages use the older AntiClaude purple direction
- e-commerce is moving toward orange
- some utility pages remain neutral

This is not wrong, but it needs stronger rules.

## 5.2 Recommended Color Strategy

### Global system palette

Use a restrained neutral foundation:

- warm off-white background
- soft gray/stone borders
- dark warm text

### Domain accents

Use accent by domain, not by random component:

- `Command / AI / system`: violet / indigo family
- `E-commerce / Flow Lab`: orange / coral family
- `Reports / analytics`: teal / blue family
- `Warnings / review`: amber / red family

This keeps brand variety while preserving order.

## 5.3 E-commerce Color Recommendation

The Shopee-inspired direction is good, but should remain controlled.

Use orange for:

- CTA
- recommendation emphasis
- commerce-specific preview panels
- role/price cards

Do not use orange everywhere.

Too much orange will make the page noisy and cheap.

---

## 6. UX Recommendations

## 6.1 Make the System More Decision-Oriented

The best parts of the system are where it helps the operator make a decision.

For example:

- suggested price
- suggested role
- restock advice
- approval summary

### Recommendation

Every major page should answer:

- what matters right now
- what the system recommends
- what the operator should do next

If a page cannot answer those three questions, it should be simplified.

---

## 6.2 Reduce Early Cognitive Load

Do not ask users for values they do not know yet.

Examples that should often be delayed:

- keyword
- market range
- campaign scenario
- deep fee switches
- advanced role overrides

This rule should apply across the whole product, not only e-commerce.

---

## 6.3 Improve Operator Trust

The system is strong, but trust is still hurt by:

- mojibake
- duplicated concepts
- inconsistent naming
- occasional noisy warnings

### Recommendation

High-priority cleanup:

- string cleanup
- naming cleanup
- scenario-vs-default distinction
- review/approval wording consistency

---

## 7. Low-Value or De-emphasizable Features

These are not necessarily useless, but they are lower-priority than workflow clarity.

## 7.1 Candidate for De-Emphasis

### Very formula-heavy explanatory blocks

If a page shows too many teaching-style formula cards, consider reducing them or moving them behind "Learn more".

The operator usually needs:

- result
- recommendation
- warning

not a wall of formulas every time.

### Over-detailed helper sections in the primary workspace

Examples:

- long SOP walkthroughs on main pages
- too many education blocks mixed with action UI

Better pattern:

- primary workflow first
- tutorial/help second

### Repetitive environment controls

If the same settings appear in multiple places:

- keep only one editable home
- elsewhere show summary + shortcut

### Extra decorative cards with little action value

If a card does not:

- summarize status
- support a decision
- reduce uncertainty

then it may not deserve primary page space.

---

## 7.2 Candidate for Archive or Secondary Placement

These should be reviewed for secondary placement rather than full deletion:

- long instructional sections on active work pages
- low-frequency experimental blocks
- duplicated analytics summaries
- duplicated action triggers across multiple tabs

---

## 8. Page-Specific Recommendations

## 8.1 E-commerce

- keep Quick Add minimal
- move advanced controls to product detail
- strengthen pricing recommendation visibility
- continue procurement UX improvement
- finish commerce color-token unification

## 8.2 Review

- keep it focused on decisions only
- avoid mixing operational diagnostics into the review inbox
- ensure approved/rejected/deferred cleanup remains simple

## 8.3 Office

- make agent activity easier to scan
- surface only decision-relevant process detail by default
- put deep traces behind expandable panels

## 8.4 Reports / Insights / Metrics

These should be better separated by job:

- `Reports`
  - narrative summary
- `Metrics`
  - quantitative monitoring
- `Insights`
  - analysis and interpretation

If these feel too similar, their headers and empty states should clarify the distinction.

---

## 9. Recommended Simplification Rules

Use these rules product-wide:

1. One page, one primary job.
2. One modal, one decision.
3. Defaults live in settings, not everywhere.
4. System recommendation should appear before advanced tuning.
5. Advanced controls should be hidden until needed.
6. Domain colors should be intentional, not scattered.
7. Explanations should support the action, not compete with it.

---

## 10. Recommended Next Execution Order

### Phase 1: Cleanup

- mojibake cleanup
- wording consistency
- remove redundant helper clutter

### Phase 2: UX tightening

- simplify Quick Add surfaces
- move advanced controls to later surfaces
- reduce redundant settings duplication

### Phase 3: Visual unification

- global neutral refinement
- domain accent rules
- consistent card/button/tag styles

### Phase 4: Product maturity

- refine detail drawers/pages
- reduce modal overload
- make decision outputs more central

---

## 11. Final Recommendation

The biggest improvement now does not come from adding more features.

It comes from making the existing system feel:

- clearer
- calmer
- more trustworthy
- more intentionally structured

The next design standard should be:

"Less noise, more signal."
