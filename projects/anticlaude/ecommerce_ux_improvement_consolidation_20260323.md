# E-commerce UX Improvement Consolidation (2026-03-23)

## Purpose
This document consolidates the latest operator-facing UX issues in `/ecommerce` and turns them into a practical refinement plan.

Scope:
- Dashboard overview
- Products table
- Product drawer
- Weekly performance table
- Bundle design
- Settings and manual surfaces
- End-to-end operator flow from product intake to launch

Goal:
- Make the ecommerce workspace more obvious, actionable, and trustworthy
- Reduce scanning burden
- Make problem items surface themselves
- Reduce unnecessary navigation and repeated interpretation

---

## Current UX Diagnosis

The ecommerce system is no longer structurally broken. The remaining problem is not missing business logic; it is operator friction.

The current UI still asks the operator to:
- infer why data is empty
- scan too much to find issues
- switch contexts too often
- mentally connect cost, pricing, stock, and next action

This creates a system that is powerful but still heavier than it should be.

---

## Priority Problems and Fix Direction

## 1. Overview Page: empty metrics look like failure

### Current problem
When monthly revenue, monthly profit, or average margin cannot be computed yet, the page shows `—`.
The operator sees:
- `NT$ —`
- `—`
- `0 active SKUs`
- `no sales data`

This looks like the system is broken, especially when products clearly exist elsewhere.

### Why this is bad
- It creates doubt immediately
- It hides the required next step
- `0 active SKUs` is especially misleading if products already exist

### Required improvement

#### Replace empty metrics with guided empty states
Instead of raw `—`, show:
- metric label
- temporary empty value
- small hint text
- one clear CTA

Example:
- `Monthly Revenue Estimate`
  - `Not enough weekly sales data yet`
  - `Update weekly sales for at least one active product`
  - `Go update →`

#### Active SKU count must reflect actual product count
This card should count products from the product list, not only products with complete sales/performance records.

#### Design rule
- Empty state hint: muted warm orange
- CTA: clear action link
- Keep it instructional, not apologetic

---

## 2. Alert Cards: visible but not actionable

### Current problem
Cards like:
- Need pricing
- Low stock
- Weak margin
- Ready to scale

are visible, but if clicking them does nothing, they fail the operator mentally.

### Why this is bad
- User expectation is immediate drill-down
- The card already implies a filtered list exists
- Without filtering, the card becomes decorative rather than useful

### Required improvement

#### Alert cards must toggle table filters
Each card should:
- apply a filter to the product list
- visually indicate active state
- allow second click to remove the filter

#### Visual behavior
- active card = deeper background, clearer border, subtle shadow
- inactive card = normal state

#### Filter mapping
- Need pricing
  - products with missing or incomplete pricing data
- Low stock
  - products below low-stock threshold
- Weak margin
  - products with margin under target or below warning floor
- Ready to scale
  - products with healthy margin and positive sales signal

---

## 3. Problem products do not stand out enough

### Current problem
A product with negative margin can still visually blend into the rest of the list.

### Why this is bad
- The operator must scan every row manually
- As the list grows, weak products become easier to miss

### Required improvement

#### Add severity-driven row styling

Priority 1:
- negative margin row gets pale red/orange background

Priority 2:
- warning icon beside product name

Priority 3:
- critical items float to top when sorting by default

#### Suggested severity levels
- Critical:
  - negative margin
  - zero or broken pricing
- Warning:
  - low stock
  - weak ROAS
  - weak margin
- Opportunity:
  - healthy margin and scale potential

---

## 4. Product drawer still requires too much switching

### Current problem
Even after recent improvements, the product drawer still forces the operator to move across logical clusters:
- cost understanding
- pricing choice
- stock / operations

Tabs reduced clutter, but they still segment a single decision process.

### Why this is bad
Real operator flow is:
1. understand the product
2. understand cost
3. decide price
4. choose next action

That is one vertical flow, not three separate mental spaces.

### Required improvement

#### Preferred direction: single long-form decision drawer
Replace heavy tab dependence with one vertically scrollable layout:
- Basic info
- Cost breakdown
- Pricing decision
- Operations
- Danger zone

#### Drawer content order
1. Header summary
2. AI recommendation / status card
3. Market price band
4. Cost and platform fee breakdown
5. Recommended Shopee price block
6. Scenario settings
7. Action buttons
8. Delete area

#### Optional enhancement
Allow a full-screen mode for focused product work.

---

## 5. Weekly performance table is overloaded

### Current problem
Too many columns compete at once:
- price
- sales
- revenue
- ad spend
- margin
- ROAS
- stock
- strategy
- ad advice
- action

The most important column can easily be pushed off-screen.

### Why this is bad
- Horizontal scanning cost is too high
- Critical decision guidance is visually buried

### Required improvement

#### Default to a compact strategic view
Show only:
- Product
- 7-day sales
- Margin %
- ROAS
- Recommended action

#### Secondary fields move into expand mode
Expanded row or detail section should contain:
- current price
- 7-day revenue
- ad spend
- stock
- strategy
- ad advice

#### Visual form
Recommended action should be badge-based:
- green = scale
- orange = adjust price
- red = evaluate removal

---

## 6. Delete action needs stronger protection

### Current problem
Delete is a destructive action but can still visually sit too close to routine actions.

### Why this is bad
- High misclick risk
- Weak trust in the interface

### Required improvement

#### Create a real danger zone
At drawer bottom:
- separator line
- red-tinted zone
- short irreversible warning
- destructive button styling

#### Mandatory confirmation dialog
Message:
- `Delete this product? This action cannot be undone.`

---

## 7. Overall flow lacks explicit stage guidance

### Current problem
The system expects the user to infer what stage a product is in and what comes next.

### Required improvement

#### Add a stage model visible in list and drawer
Recommended sequence:
- Sample received
- Cost confirmed
- Price configured
- Ready to list
- Listed

#### Purpose
This makes the system answer:
- where this product is now
- what is missing
- what the next action should be

---

## Clarified Surface Model

## Top-level tabs to keep
- Overview
- Products
- Weekly Performance
- Bundle Design
- Settings
- Manual

## Top-level tabs to remove or keep out of primary flow
- Pricing Lab / Pricing Decision as standalone top-level surface
- Selection Research Lab
- Candidates
- Analysis
- Reports
- Lessons

These may remain as archive/lab/internal tools, but should not compete with operator core work.

---

## Recommended Product Surface Model

## Products page responsibilities
- quick product management
- issue surfacing
- quick actions
- product selection for deeper inspection

## Drawer responsibilities
- full product evaluation and decision execution

## Weekly Performance responsibilities
- weekly business review and action prioritization

## Bundle Design responsibilities
- bundle strategy and pricing power design

## Settings responsibilities
- defaults, thresholds, fee environment

## Manual responsibilities
- ecommerce-only operational handbook

---

## Bundle Design: recommended role and activation

## What Bundle Design should become
Not a research toy.
It should become a merchandising decision tool.

### Preferred bundle types
- Exclusive bundle
- Add-on bundle
- Multi-buy bundle
- Inventory cleanup bundle

### Activation expectation
Bundle logic should activate when:
- user enters Bundle Design page
- user manually creates or edits a bundle
- user asks the system to suggest bundles

### Better recommendation basis
The next version should prioritize:
- same family
- same scene
- main product + accessory
- high-margin complement
- cleanup support pairings

Not only:
- category
- role complement

---

## Family / Variant grouping

## Why this is needed
The same product family should not always appear as unrelated rows.

Example:
- 躺贏招財貓 - 躺贏
- 躺贏招財貓 - 閒樂
- 躺贏招財貓 - 躺賺

These should be grouped under one product family.

## Data meaning
- `Family name` = series-level product identity
- `Variant name` = style / version under that family

## Better operator wording
Replace technical wording with:
- `系列名稱`
- `款式名稱`

## UI behavior
- main table can collapse/expand family
- family row shows:
  - total stock
  - best margin
  - variant count
- variant rows show per-style details

## Quick Add behavior
Support:
- create new family
- add variant under existing family

---

## Naming and meaning cleanup

## System estimate
If the current estimate block is not actually Shopee selling price, do not label it that way.

Recommended split:
- `Landed Cost Estimate`
  - purchase + procurement + cross-border + packaging
- `Shopee Suggested Price`
  - output after role + fee + scenario calculation
- `Base Platform Fee`
  - commission + transaction + FSS
- `Scenario Surcharge`
  - CCB + promo-day surcharge + fulfillment penalty

## Required micro-labels
Every key numeric block should show source notes in small type.

Examples:
- `Commission 6%`
- `Transaction 2.5%`
- `FSS 6%`
- `CCB 1.5%`
- `Promo +2%`
- `Fulfillment +3%`

---

## High-frequency actions should move closer

These should be reachable with fewer steps:
- Update weekly sales
- Open inbound restock
- Adjust target price

### Recommended improvement
Products table row actions:
- `Update sales`
- `Restock`
- `Open details`

This reduces unnecessary drawer opening for routine operations.

---

## Color semantics

Color should mean something, not just decorate.

Recommended map:
- Red = loss / danger / destructive action
- Orange = warning / needs attention
- Green = healthy / ready to scale
- Purple or blue = opportunity / strategic upgrade

Do not reuse the same orange for unrelated meanings.

---

## Implementation order

## Phase 1: clarity and guidance
- Fix empty KPI guidance states
- Fix active SKU count
- Make alert cards filter the table
- Add source sublabels to key metrics

## Phase 2: product handling
- Add problem-row emphasis
- Rebuild drawer into a vertically structured decision flow
- Isolate danger zone

## Phase 3: table simplification
- Simplify weekly performance default columns
- Convert action text into badges
- add row-level quick actions in products list

## Phase 4: grouping and merchandising
- Add family/variant grouping
- Upgrade bundle logic toward merchandising

---

## Agent role split

## Lara
- prioritize the sequence
- ensure no overlap between major surfaces

## Lumi
- implement table filtering
- rebuild drawer structure
- wire stage/status guidance
- simplify data flow

## Pixel
- refine hierarchy, spacing, severity states, empty states
- ensure color semantics stay consistent

## Sage
- define warning thresholds and recommended actions
- verify action badges and problem highlighting rules

## Craft
- rewrite helper copy, empty-state wording, guidance text, and ecommerce manual language

---

## Final principle

The ecommerce workspace should not feel like a spreadsheet with features attached.
It should feel like a decision console that constantly answers:

- what is wrong
- what matters now
- what should I do next

That is the standard for the next refinement pass.

