# Ecommerce Variant Grouping and Next-Phase Plan

Date: 2026-03-22

## Goal

Define the next refinement phase for the Flow Lab ecommerce system after the current drawer, pricing, inbound, and performance improvements.

This phase focuses on:

- grouping same-family products under one expandable product family
- reducing product list noise
- improving operator clarity for same-category / same-series items
- continuing the final UX convergence work that is still not fully complete

## Problem Statement

The current ecommerce product model is still too flat.

Examples:

- `躺贏招財貓`
- `躺贏閒樂`

These are not truly unrelated products. They are variants or styles under the same product family.

When they are displayed as separate top-level products:

- the product list becomes visually noisy
- stock and pricing comparisons become harder
- the operator loses the sense of "series-level" management
- the system feels more like a spreadsheet than a product OS

## Design Direction

Introduce a two-level product structure:

1. Product Family
2. Variant / Style / Child Product

The UI should present a family-first view, with expandable rows or grouped cards.

## Information Model

### Product Family

Represents the shared parent group.

Suggested fields:

- `family_id`
- `family_name`
- `category`
- `base_keyword`
- `shared_scene`
- `shared_notes`
- `family_status`

Examples:

- `躺贏系列`
- `午睡枕系列`
- `腕托系列`

### Variant

Represents a specific sellable version under one family.

Suggested fields:

- `sku`
- `family_id`
- `variant_name`
- `style_label`
- `target_role`
- `target_price`
- `market_price_low`
- `market_price_high`
- `cost_rmb`
- `head_freight_rmb`
- `weight_kg`
- `status`
- `stock`

Examples:

- `躺贏招財貓`
- `躺贏閒樂`

## UX Proposal

### 1. Product List: Family-First Display

Top-level product list should show one family row/card first.

Each family row should display:

- family name
- number of variants
- combined stock
- price range
- main recommended role
- aggregate health summary

Expandable action:

- click to expand variants

Expanded child rows should show:

- SKU
- variant name
- role
- target price
- margin
- stock
- status

### 2. Quick Add Flow

Quick Add should support two entry paths:

- `Create new family`
- `Add variant to existing family`

This keeps the first step simple.

Required Quick Add behavior:

- if operator is adding a brand-new product line, create family first
- if operator is adding another style/color/version, attach it to an existing family

### 3. Product Detail / Drawer

When opening product detail:

- family summary should appear at top
- current variant detail should appear below
- sibling variants should be visible in a small side section or switcher

Suggested structure:

1. Family summary
2. Current variant decision panel
3. Logistics / ops
4. Sibling variants quick switch

### 4. Performance View

Performance table should optionally group by family.

Two modes:

- `Variant view`
- `Family view`

Family view should help answer:

- which series is working
- which series is underperforming
- which family deserves more budget

### 5. Inbound / Restock

Inbound modal should allow:

- inbound to one specific variant
- see family-level context

Helpful display:

- selected variant stock
- sibling stock summary
- family sales velocity
- family-level stock risk

This avoids over-restocking one weak variant while another sibling is actually the main seller.

## Why This Matters

This change improves:

- list readability
- operator clarity
- family-level merchandising
- multi-style product management
- future support for bundles / upgrades / style ladders

It also matches the real ecommerce mental model better:

- one concept
- multiple sellable versions

## What Should Stay Separate

Do not mix family grouping with pricing simulation logic.

Keep responsibilities separate:

- family/variant structure = product organization
- pricing logic = backend pricing engine
- inbound = inventory operation
- manual = help content only

## Recommended Execution Order

### Phase A: Data Model Preparation

- add optional `family_id`
- add optional `family_name`
- allow products without family initially for backward compatibility

### Phase B: UI Grouping

- add grouped product list UI
- support collapse / expand
- show family summary metrics

### Phase C: Quick Add Upgrade

- add "new family / existing family" entry mode
- keep variant creation fast

### Phase D: Product Detail Upgrade

- show sibling variants
- show family context above variant context

### Phase E: Performance and Inbound Family Awareness

- add family-mode performance aggregation
- add sibling/family context to inbound workflow

## Remaining UX Convergence Work Still Worth Doing

Even after the current successful phases, these items are still worth finishing:

1. Further slim the `decision` tab in `ProductDrawer`
2. Continue moving residual frontend pricing/business logic into backend responses
3. Keep cleaning mojibake in active UI text
4. Clarify the difference between:
   - top-level pricing simulation
   - product-level decision view

## Suggested AI Agent Roles

### Lara

- decide execution order
- ensure grouping does not break current operator flow

### Lumi

- implement family/variant schema plumbing
- refactor list/detail/inbound UI

### Pixel

- define grouped list visual hierarchy
- make collapse/expand interaction feel clean and calm

### Sage

- validate that family grouping reduces operator noise instead of hiding critical variant signals

### Craft

- improve family / variant naming clarity if needed

## Implementation Guardrails

- do not rebuild ecommerce from scratch
- preserve current product records
- make family linkage optional first
- keep backward compatibility for existing SKUs
- avoid mixing family grouping with unrelated pricing refactors in one large patch

## Success Criteria

This phase is successful when:

- same-family products no longer feel duplicated in the main list
- operator can expand one family and manage all variants together
- Quick Add remains simple
- product detail becomes more intuitive for style-based product lines
- inbound and performance views feel more decision-oriented, not more cluttered
