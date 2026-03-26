# E-commerce UI Implementation Brief (2026-03-21)

## Purpose

This document is the implementation handoff for improving the current e-commerce UI.

Important:

- This is **not** a full rewrite.
- The goal is to improve the current UX inside the existing architecture.
- The main target file is:
  - `dashboard/src/app/ecommerce/page.tsx`

---

## Read First

Before implementation, read these files in order:

1. `projects/anticlaude/ecommerce_operator_flow_design_optimization_20260321.md`
2. `projects/anticlaude/flow_lab_end_to_end_product_intake_and_pricing_spec_20260321.md`
3. `projects/anticlaude/flow_lab_procurement_workflow_optimization_20260321.md`

---

## Main Objective

Make the current e-commerce page easier to use by:

- simplifying Add Product
- moving advanced fields out of the first-step modal
- improving procurement / restock entry UX
- making pricing suggestions more visible
- introducing a Shopee-inspired commerce accent direction

The result should feel simpler, clearer, and more professional.

---

## What To Change

## 1. Simplify Add Product Modal

The Add Product modal should become a **Quick Add Product** flow.

### Keep in Quick Add

- `sku`
- `name`
- `cost_rmb`
- `head_freight_rmb` or domestic shipping RMB
- `freight_type`
- `goods_type`
- `init_stock`
- `notes`

### Remove from default modal view

- market price low/high
- keyword
- supplier
- return rate
- coupon rate
- ad budget
- CCB plan
- promo day
- fulfillment days
- manual role selector

### UX rule

The operator should be able to add a product quickly without answering advanced questions.

---

## 2. Promote Preview to Primary Panel

The live pricing preview is useful and should become more prominent.

It should always show, as soon as enough fields exist:

- landed cost
- break-even price
- suggested traffic price
- suggested core price
- suggested profit price
- suggested role
- viability label

The preview should feel like the main value of the modal, not a secondary block buried below many settings.

---

## 3. Move Advanced Controls to Product Detail / Later Surface

These should not remain in the default Add Product experience:

- `ccb_plan`
- `is_promo_day`
- `fulfillment_days`
- ad budget
- coupon rate
- return rate
- keyword
- market low/high
- supplier

### New placement

Move them into:

- a product detail drawer
or
- a product edit panel
or
- a clearly labeled advanced section outside Quick Add

Priority:

- Quick Add first
- advanced detail later

---

## 4. Change Role Handling

Current issue:

- the system computes a suggested role
- the modal also asks the user to choose a role immediately

This is noisy.

### Desired behavior

- Quick Add:
  - show system suggested role only
- Product detail:
  - allow manual role override

Do not force manual role choice in the first-step flow.

---

## 5. Improve Procurement / Add Inventory UX

Current Add Inventory is too basic.

Improve it into a better procurement/restock modal.

### Add or expose more useful fields

- SKU
- quantity
- unit cost RMB
- shipping method
- ETA
- supplier
- notes

### Add live preview

- total RMB
- estimated TWD
- estimated landed unit cost
- projected stock after inbound

The modal should answer:

"If I buy this batch, what will happen to cost and stock?"

---

## 6. Introduce a Commerce Accent Visual Direction

Do not recolor the whole application.

Only improve the e-commerce page with a commerce-specific local accent system inspired by Shopee.

### Suggested direction

- warm orange accent
- soft cream surfaces
- calm dark text
- restrained use of orange for CTA and recommendation emphasis

### Suggested palette

- `#EE4D2D`
- `#D93C1A`
- `#FFF1ED`
- `#FFF8F4`
- `#F3D8CF`
- `#2E221D`
- `#7A685F`

### Apply to

- Add Product modal emphasis
- price suggestion cards
- CTA buttons
- viability labels
- procurement actions

Do not make the whole UI look like a direct Shopee clone.

---

## 7. Keep Existing Architecture

Do not redesign the whole product system.

This task should fit the current codebase:

- keep current tabs
- keep current page structure
- keep current pricing engine
- keep current backend APIs unless small UI-alignment changes are needed

This is a UX refinement task, not a platform rewrite.

---

## 8. Implementation Priority

### Phase 1

- simplify Add Product modal
- make preview more prominent
- hide or move advanced controls

### Phase 2

- improve Add Inventory / procurement UX
- expose better landed-cost context

### Phase 3

- apply commerce accent styling to e-commerce page surfaces
- improve visual hierarchy

---

## 9. Deliverable Expectations

Expected deliverables:

- updated `dashboard/src/app/ecommerce/page.tsx`
- any small supporting UI helpers if necessary
- no unnecessary architecture rewrite
- maintain working build
- maintain pricing-preview correctness

---

## 10. Validation Requirements

After implementation:

1. run front-end build
2. verify the e-commerce page still works
3. confirm Add Product is simpler than before
4. confirm pricing preview still appears
5. confirm procurement flow is clearer than before

---

## 11. Final Instruction

Do not stop at writing more documentation.

Use this brief to implement the UI changes directly.
