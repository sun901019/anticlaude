# E-commerce Add Product UX Flow Optimization (2026-03-21)

## 1. Goal

This plan does **not** propose a full system rewrite.

The goal is narrower and more practical:

- simplify the Add Product experience
- move noisy advanced controls out of the first-step form
- keep the current architecture mostly intact
- improve overall professionalism of the e-commerce section
- introduce a Shopee-inspired orange accent direction without turning the whole dashboard into a clone

This is a focused UX and IA refinement, not a large rebuild.

---

## 2. Current UX Problem

The current `Add Product` modal in `dashboard/src/app/ecommerce/page.tsx` is overloaded because it mixes:

- product identity
- sourcing inputs
- logistics options
- pricing assumptions
- Shopee environment simulation
- role override
- cost preview

This creates three user experience problems:

### Problem A: Too many decisions too early

When the user just wants to create a product quickly, they are asked to think about:

- CCB
- promo day
- fulfillment days
- role
- packaging cost
- return rate
- coupon rate
- ad budget

This is too much for first entry.

### Problem B: Global assumptions are mixed into product creation

Some controls are really system defaults or scenario toggles, not true product identity:

- CCB mode
- promo day
- long prep penalty
- rate tables

These should not crowd the first creation flow.

### Problem C: The visual structure lacks hierarchy

The modal currently feels like one long stack of controls.
Even though some groups are collapsible, it still feels dense and "form-heavy".

---

## 3. Core UX Principle

The Add Product flow should answer only one question:

**"Can I register this product fast enough to decide whether it is worth deeper work?"**

That means:

- first step = minimal
- second step = system preview
- later detail = edit/product detail

The system should not force the operator to finish the whole business model in one modal.

---

## 4. Recommended Flow

## 4.1 New Add Product Flow

The first-step Add Product flow should contain only:

### Required

- `SKU`
- `Product Name`
- `Product Cost (RMB)`
- `1688 Domestic Shipping (RMB)`
- `Shipping Mode`
- `Goods Type`
- `Initial Stock`
- `Notes`

### Optional but acceptable in step 1

- `Target Role`

Only because role helps price suggestions early.

### Remove from step 1

These should not stay in the first modal body:

- CCB mode
- promo day
- fulfillment days
- packaging cost
- return rate
- coupon rate
- ad budget
- market low/high
- keyword
- supplier

These belong later.

---

## 4.2 Immediate Right-Side Preview

After entering the minimum fields, the user should immediately see a compact preview panel.

The preview should show:

- estimated landed cost
- break-even price
- suggested traffic price
- suggested core price
- suggested profit price
- current viability label

The preview should be the main decision helper.

This means the modal becomes:

- left side = input
- right side = pricing and viability preview

Instead of one long vertical form.

---

## 4.3 After Save: Product Detail Expansion

Once the product is created, advanced settings should move into:

- product detail drawer
or
- product edit page

This should contain the sections below.

### Section A: Basic Info

- SKU
- name
- notes
- status
- role

### Section B: Cost and Logistics

- product cost
- domestic shipping
- shipping mode
- goods type
- weight
- packaging cost
- extra cost

### Section C: Pricing Strategy

- target price
- market low/high
- suggested traffic/core/profit prices
- custom target margin
- ad budget

### Section D: Shopee Scenario

- CCB mode
- promo day
- fulfillment days
- FSS mode override if needed

### Section E: Performance and Actions

- current selling price
- 7-day sales
- ad spend
- stock
- next action

This makes step 1 fast while keeping the system powerful.

---

## 5. Global Settings vs Product Settings

The user explicitly does **not** want system defaults cluttering product creation.

That means the system should separate:

### Global Defaults

These should live in Settings:

- exchange rate
- Shopee fee defaults
- shipping rate defaults
- special goods premium
- default return rate
- default discount rate
- default ad assumptions by role

### Product-Level Overrides

These should live in product detail:

- actual packaging cost
- role override
- custom ad budget
- product-specific risk assumptions

### Scenario Toggles

These should live in a small simulation box or advanced panel:

- promo day
- CCB mode
- prep day penalty

This creates clean information hierarchy.

---

## 6. Procurement UX Improvement

The user also said the procurement flow is not good enough.

The procurement form should feel like a separate task from product creation.

## 6.1 Recommended Procurement Entry

Fields:

- select SKU
- quantity
- unit cost RMB
- domestic shipping RMB
- shipping mode
- estimated cross-border shipping
- exchange rate
- ETA
- notes

## 6.2 Live Procurement Preview

Show immediately:

- total RMB
- estimated TWD
- estimated landed unit cost
- projected stock after arrival

This is better than the current minimal batch entry because it gives context.

---

## 7. Visual Direction: Shopee-Inspired, Not Shopee-Cloned

The current dashboard still uses a warm purple accent system globally.

For the e-commerce domain, a more professional direction would be:

- keep the global dashboard shell neutral
- introduce an e-commerce-specific orange accent layer
- keep the app from feeling like a literal Shopee clone

## 7.1 Where the Orange Should Live

Use orange in:

- e-commerce page headers
- Add Product CTA
- pricing suggestion highlights
- viability badges
- inventory/profit action states

Do **not** make the whole app orange.

Keep these areas neutral:

- sidebar shell
- office pages
- review pages
- AI system pages

This preserves domain separation visually.

## 7.2 Recommended Color System

### Global Shell

- background: soft neutral
- text: dark slate / warm black
- border: pale sand/stone
- shell accent: keep current system or reduce it

### E-commerce Domain Accent

- primary orange: around Shopee-style orange but slightly muted
- soft orange background for highlights
- amber for warnings
- green for healthy profit
- red for not suitable / stop

Example direction:

- `--ecom-accent: #ee4d2d`
- `--ecom-accent-soft: #fff2ee`
- `--ecom-accent-deep: #d9481c`
- `--ecom-amber: #c67a12`

The page should feel commerce-oriented and energetic, but still fit the rest of the system.

## 7.3 Hierarchy Recommendation

Inside e-commerce pages:

- use orange for "create / commit / promote / calculate"
- use neutral cards for structure
- use subtle segmented blocks instead of too many bright cards
- let price suggestion panels feel more dashboard-like than form-like

---

## 8. Recommended Component-Level Changes

## 8.1 Add Product Modal

Current issue:

- too many controls
- too many button groups
- too much cognitive load

Recommended structure:

### Top

- title
- one-line explanation

### Main body: two-column

Left:

- quick required inputs

Right:

- live price suggestion
- viability label
- quick role explanation

### Bottom

- save product
- save and open details

## 8.2 Product Table

Recommended improvements:

- make edit action more visible, not only on hover
- add "Details" action separate from "Edit"
- show suggested price under target price in smaller type
- show role chip + confidence or source

## 8.3 Product Detail Drawer

This should become the home of advanced settings.

Use collapsible groups:

- Basic
- Cost
- Pricing
- Shopee Scenario
- Performance
- AI Suggestions

This matches how users think.

## 8.4 Settings Page

The current settings content feels text-heavy and mixed.

Recommended redesign:

- split into tabs or grouped blocks:
  - Fees
  - Logistics
  - Financial defaults
  - Role presets

This helps the user understand that these are defaults, not per-product fields.

---

## 9. AI Employee Collaboration Model

The user asked to "bring the AI employees in" for the flow optimization.

Recommended role assignment:

### Lara

- orchestrates the redesign scope
- ensures the Add Product flow stays minimal
- decides what belongs in Settings vs Product Detail

### Lumi

- implements the front-end restructuring
- converts the modal into a two-step or two-column experience
- simplifies input groups and visual hierarchy

### Pixel

- defines the e-commerce orange accent layer
- tunes spacing, surface hierarchy, and CTA emphasis
- prevents the UI from becoming a cheap Shopee imitation

### Sage

- reviews operator friction
- identifies where current controls create confusion
- checks if the preview logic is understandable and trustworthy

### Craft

- rewrites labels, hints, helper text, and section naming
- makes the whole flow feel simpler and more human-readable

This is the correct multi-agent collaboration pattern for the redesign.

---

## 10. Recommended Scope

This should be treated as a focused optimization project, not a platform rewrite.

### In scope

- Add Product simplification
- move advanced controls out of first-step flow
- better pricing preview
- better product detail layout
- procurement flow cleanup
- e-commerce-specific visual direction

### Out of scope for now

- replacing the whole dashboard shell
- rewriting all tabs
- changing the overall app architecture

This keeps the project realistic.

---

## 11. Recommended Implementation Phases

### Phase 1: Add Product Experience

- simplify fields
- remove noisy advanced controls
- add right-side pricing preview
- keep target role optional

### Phase 2: Product Detail Expansion

- move advanced controls into detail drawer/page
- add grouped sections

### Phase 3: Settings Cleanup

- move environment defaults out of Add Product
- redesign settings into grouped system blocks

### Phase 4: Procurement Refresh

- improve procurement entry
- add landed unit cost preview

### Phase 5: Visual Polish

- add e-commerce orange token layer
- refine CTA and section hierarchy
- improve professionalism without cloning Shopee

---

## 12. Final Conclusion

The current problem is not that the system needs a total rebuild.

The real problem is:

- too much is happening inside Add Product
- the information hierarchy is weak
- global assumptions and product-specific inputs are mixed together

The right solution is:

- keep product creation minimal
- move advanced settings to later surfaces
- centralize defaults in settings
- keep pricing suggestions visible
- give the e-commerce domain its own orange-accent visual identity

That would make the experience feel:

- simpler
- more professional
- more trustworthy
- easier to operate every day
