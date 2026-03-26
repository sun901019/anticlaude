# E-commerce Page-by-Page Presentation Specification (2026-03-21)

## 1. Design Objective

The e-commerce system should feel:

- professional
- calm
- clear
- decision-oriented
- easy to use daily

It should **not** feel:

- crowded
- repetitive
- form-heavy
- visually noisy
- like a developer tool instead of an operator tool

This specification defines how each major e-commerce surface should be presented so the system becomes genuinely useful and polished.

---

## 2. Overall Design Principles

## 2.1 One page, one primary job

Each page should have one clear main purpose.

Examples:

- Products page = manage products
- Weekly performance page = monitor what changed
- Pricing decision page = decide pricing
- Settings page = control defaults
- Manual/help page = learn terms and workflow

No page should try to do all of these at once.

## 2.2 Summary first, detail later

Every page should first answer:

- what matters now
- what the system recommends
- what the operator should do next

Only after that should it expose deeper detail.

## 2.3 Reduce early decisions

The system should not ask for advanced values too early.

Quick actions should stay quick.
Detailed tuning should happen later.

## 2.4 Make decisions visible

The best value of the system is not raw data.
The best value is decision assistance.

Therefore, recommendation outputs should always be more visually obvious than raw supporting detail.

## 2.5 Visually separate domains

E-commerce should have its own design tone:

- warm commerce accent
- calm neutral foundation
- stronger emphasis on pricing, stock, and action

---

## 3. Visual Language

## 3.1 Base Tone

Recommended overall tone:

- soft warm neutral background
- dark warm text
- light structured borders
- very limited heavy shadows

The system should feel more like a premium operator dashboard than a crowded admin panel.

## 3.2 E-commerce Accent

Use a Shopee-inspired but not cloned commerce palette.

Suggested tokens:

- `commerce-primary`: `#EE4D2D`
- `commerce-primary-strong`: `#D93C1A`
- `commerce-primary-soft`: `#FFF1ED`
- `commerce-surface`: `#FFF8F4`
- `commerce-border`: `#F3D8CF`
- `commerce-text`: `#2E221D`
- `commerce-muted`: `#7A685F`

## 3.3 Where orange should appear

Use orange for:

- pricing recommendations
- CTA buttons
- important operator actions
- commerce status highlights
- restock / action prompts

Do not use orange for:

- entire page backgrounds
- all cards
- every label
- all text

The page should feel controlled, not loud.

## 3.4 Typography and hierarchy

The page should clearly separate:

- page title
- section title
- KPI label
- important metric
- helper explanation

Use stronger typography hierarchy instead of many boxes.

---

## 4. Products Page: In-Stock Products

## 4.1 Primary purpose

Manage active products and quickly decide whether a product needs:

- pricing action
- stock action
- status change
- deeper review

## 4.2 Page structure

### Zone A: Header

- page title: `Products`
- short subtitle:
  - "Manage active products, cost health, and next actions."
- primary actions:
  - `Quick Add Product`
  - `Add Procurement`

### Zone B: Decision summary row

Cards:

- products needing repricing
- low stock products
- weak margin products
- products ready to scale

This row should be short, high-signal, and visual.

### Zone C: Main product table

This is the main workspace.

Columns should prioritize decision usefulness:

- SKU
- product name
- status
- current role
- target price
- estimated margin
- stock
- next action

De-emphasize secondary fields here.

### Zone D: Product detail drawer

Clicking a product should open a rich detail surface.

This should be the place for:

- advanced pricing
- logistics detail
- market detail
- overrides
- notes
- AI suggestions

## 4.3 UX rules

- Quick Add should stay minimal
- the table should stay scannable
- advanced settings must not be forced into the table or the quick-add flow

---

## 5. Quick Add Product

## 5.1 Primary purpose

Register a product fast, not complete every setting.

## 5.2 Required fields

- SKU
- product name
- product cost RMB
- domestic shipping RMB
- shipping mode
- goods type
- initial stock

## 5.3 Immediate outputs

The modal should immediately show:

- landed cost
- break-even price
- suggested traffic price
- suggested core price
- suggested profit price
- suggested role

## 5.4 What should not dominate this flow

- campaign scenario controls
- detailed market analysis
- long instructional text
- too many toggles

The operator should be able to finish Quick Add in under a minute.

---

## 6. Product Detail View

## 6.1 Primary purpose

This is where advanced configuration and deeper review happen.

## 6.2 Recommended sections

### A. Basic

- SKU
- name
- status
- role
- notes

### B. Cost & Logistics

- product cost
- domestic shipping
- shipping mode
- goods type
- weight
- packaging
- extra cost

### C. Pricing & Market

- target price
- market low/high
- keyword
- ad budget
- role override

### D. Shopee Scenario

- CCB
- promo day
- prep days
- FSS mode

### E. Performance

- 7-day sales
- stock
- ROAS
- margin
- suggested action

### F. AI Recommendation

- suggested price
- role fit
- market warning
- procurement warning

## 6.3 Presentation style

Use collapsible sections or tabs inside the drawer/page.
Do not dump all fields into one long form.

---

## 7. Weekly Performance Page

## 7.1 Primary purpose

Show what changed this week and where intervention is needed.

## 7.2 Page structure

### Zone A: Weekly headline

- total 7-day revenue
- total 7-day profit
- average margin
- products with worsening performance

### Zone B: Change-focused product list

The table should focus on movement, not static information.

Columns:

- SKU / name
- 7-day sales
- 7-day revenue
- ad spend
- ROAS
- margin
- stock days remaining
- change vs last period
- recommended action

## 7.3 Recommended visual emphasis

Highlight:

- margin drop
- stock risk
- underperforming ads
- strong winners

The page should tell the operator:

"What changed this week, and what should I do about it?"

---

## 8. Pricing Decision Page

## 8.1 Primary purpose

Turn cost and fee logic into an actual pricing decision.

## 8.2 Page structure

### Zone A: Product selector

- choose product
- show key product summary

### Zone B: Pricing recommendation panel

This should be the visual center of the page.

Show:

- break-even price
- traffic price
- core price
- profit price
- current target price
- resulting margin
- matched role
- warning if market cap is too low

### Zone C: Cost breakdown

Show detailed supporting numbers:

- procurement cost
- logistics cost
- Shopee fee
- transaction fee
- FSS
- CCB
- promo surcharge
- prep penalty

This section should support the decision, not overpower it.

### Zone D: Scenario controls

These can remain here because this page is specifically about pricing simulation.

Examples:

- promo day
- CCB
- prep days
- FSS mode

## 8.3 UX rule

Recommendation first, mechanics second.

The operator should see the answer before digging into the math.

---

## 9. Settings Page

## 9.1 Primary purpose

Own system defaults and reusable assumptions.

## 9.2 Recommended sections

### A. Shopee fee environment

- base commission
- transaction fee
- promo surcharge
- prep penalty
- FSS
- CCB assumptions

### B. Logistics defaults

- shipping-rate presets
- special-goods premium

### C. Financial defaults

- exchange rate
- default packaging cost
- default return rate
- default discount rate

### D. Role presets

- traffic margin target
- core margin target
- profit margin target
- ad budget presets

## 9.3 UX rule

Settings should feel stable, clean, and low-frequency.
Do not overload with too many inline explanations.
Use short descriptions and a linked help/manual surface.

---

## 10. Manual / Help Page

## 10.1 Primary purpose

Teach terms and workflow only when needed.

## 10.2 Structure

Recommended sections:

- Shopee fee terms
- procurement workflow
- pricing logic
- product role logic
- FAQ

## 10.3 UX rule

The manual should not compete with the working pages.
It should support them.

Good pattern:

- short inline tooltip on working page
- detailed explanation in help page or help drawer

---

## 11. What Should Be De-Emphasized or Removed

## 11.1 De-emphasize

- long instructional blocks on active work pages
- too many formula cards in the main workspace
- repeated settings controls across multiple screens
- duplicated analytics blocks that do not change operator action

## 11.2 Move to secondary surfaces

- tutorial-like content
- verbose explanations
- advanced fee simulation that is not part of the page's main task
- low-frequency experimental tools

## 11.3 Remove if still present

- redundant helper cards that say the same thing as the preview panel
- decorative cards with no decision value
- duplicated warnings shown in multiple places

---

## 12. Final Product Standard

The e-commerce system should feel like:

- a premium operator console
- not a messy admin tool
- not a giant calculator
- not a teaching document

The product should give the operator:

- clarity
- confidence
- speed
- useful recommendations

The standard for every screen should be:

"What should I do next, and why?"
