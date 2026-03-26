# E-commerce End-to-End Operator Experience Audit (2026-03-21)

## 1. Executive Summary

The current e-commerce system is already functional and significantly improved compared to earlier iterations.

However, from an operator-experience perspective, it still has four structural issues:

1. too many decisions appear too early
2. some settings and scenarios are mixed with product facts
3. pricing logic and role semantics are partially duplicated
4. the UI hierarchy is improved, but some surfaces still feel tool-like rather than product-like

This means the system does not need a rebuild.
It needs a strong refinement pass.

---

## 2. End-to-End Flow Assessment

## 2.1 Current flow shape

The current operator journey is roughly:

1. add product
2. optionally add procurement
3. inspect pricing preview
4. update performance
5. check product drawer
6. use pricing decision tools
7. use settings and supporting analysis

This is a reasonable backbone.

## 2.2 Main problem

The flow is still too compressed around the first step.

The Add Product experience still carries too much:

- intake facts
- pricing assumptions
- Shopee scenario settings
- advanced details
- recommendation interpretation

That makes the first step feel heavier than it should.

---

## 3. Where the UX Still Feels Strange

## 3.1 Add Product is still half Quick Add, half advanced configuration

This is the biggest issue.

Even after simplification, the Add Product experience still contains:

- market high/low
- ad budget
- packaging
- Shopee scenario controls
- notes and other secondary values

These are not all wrong, but they should not sit so close to the main first-step path.

### Better model

- Quick Add = first-known facts
- Product Detail = advanced settings

## 3.2 Shopee scenario settings still feel misplaced

The following still feel out of place inside the product-creation path:

- CCB
- promotion day
- fulfillment/prep days

These are scenario-level or environment-level concepts.
They should not behave like core product identity fields.

## 3.3 Role semantics are not yet perfectly clean

The system now has:

- target role
- suggested role
- viability
- pricing presets

These are related, but not identical.

If they are not visually and semantically separated, the operator can become uncertain about:

- what the system is suggesting
- what is fixed
- what is manually overrideable

## 3.4 Product detail is useful, but not yet a full advanced workspace

The drawer has become more informative, which is good.

But it still feels more like:

- a detailed viewer

than:

- a true product operating workspace

It should become the main place for:

- overrides
- scenario tuning
- market details
- pricing management
- AI recommendations

## 3.5 Procurement is improved, but still narrow

The procurement modal is no longer bare, which is good.

But it is still not fully answering the practical operator questions:

- what route is being used
- what ETA should I expect
- what will my landed unit cost become
- what will inventory look like after this batch

## 3.6 Some visual regions still feel inconsistent

The page has started moving toward a commerce-specific look, but some parts still feel like:

- generic dashboard remnants
- old utility-surface styling
- local orange accents added on top

The result is improved, but not fully unified yet.

## 3.7 Mojibake still hurts trust

Even when the workflow is good, garbled labels reduce perceived quality immediately.

This is not cosmetic-only.
It directly affects operator trust.

---

## 4. Functional Duplication Audit

## 4.1 Pricing logic duplication

This is the biggest architecture risk.

Pricing behavior currently exists in both:

- backend pricing engine
- frontend preview logic

This creates a maintenance hazard:

- same rule in two places
- role thresholds duplicated
- CCB/FSS/promo logic duplicated

### Recommendation

Make backend the single source of truth for:

- landed cost
- suggested price
- role fit
- viability

Frontend should display and lightly simulate only when unavoidable.

## 4.2 Role duplication

Role classification is currently reflected in multiple places:

- pricing outputs
- suggested labels
- manual role fields
- color/status logic

This should be normalized.

## 4.3 Teaching blocks vs working blocks

Some work surfaces still contain too much explanatory content relative to action UI.

This is a softer kind of duplication:

- explanation repeated where the recommendation already implies the meaning

### Recommendation

Move deep explanations to help/manual.
Keep only short in-context support on work surfaces.

---

## 5. What Should Be Split More Clearly

## 5.1 Product fact vs scenario vs default

These three types should become visually and structurally separate:

### Product fact

- SKU
- product name
- cost
- shipping fact
- goods type
- stock

### Product scenario

- target role
- target price
- promo assumptions
- CCB
- prep days

### Global default

- exchange rate
- fee presets
- shipping-rate tables
- return/default assumptions

If these three remain mixed, the system will always feel more confusing than it needs to.

## 5.2 Quick action vs deeper work

The product should separate:

- immediate entry actions
- serious review/configuration work

This is the difference between:

- modal
- drawer
- full page

Use each for the appropriate level of work.

---

## 6. What Can Be De-Emphasized

These are not necessarily useless, but they should not dominate the main workflow:

- long formula explanations
- tutorial-like blocks inside work pages
- repeated warnings that say the same thing in several places
- low-value summary cards that do not change the operator's next decision
- duplicated settings toggles across multiple surfaces

These should move to:

- help drawer
- secondary panel
- collapsible section
- settings page

---

## 7. What Should Be More Prominent

The current system becomes most valuable when it surfaces:

- suggested selling price
- break-even price
- suggested role
- stock risk
- margin health
- next recommended action

These should remain more prominent than:

- educational copy
- raw formula details
- rarely-used settings

---

## 8. Page-by-Page Improvement Directions

## 8.1 Products

Needs:

- cleaner Quick Add
- stronger next-action visibility
- more useful detail drawer

## 8.2 Procurement

Needs:

- richer restock impact preview
- route/ETA awareness
- better procurement history usefulness

## 8.3 Weekly Performance

Needs:

- stronger "what changed" focus
- stronger action recommendation emphasis

## 8.4 Pricing Decision

Needs:

- recommendation first
- breakdown second
- less educational clutter in the main path

## 8.5 Settings

Needs:

- clearer ownership of defaults
- cleaner grouping
- less duplication with product pages

## 8.6 Manual / Help

Needs:

- to absorb more explanatory burden
- so working pages can stay cleaner

---

## 9. Recommended Refinement Strategy

## Phase 1: Clarity cleanup

- clean mojibake
- standardize wording
- standardize role semantics

## Phase 2: Flow cleanup

- simplify Quick Add further
- move scenario controls out of first-step flow
- strengthen detail drawer ownership

## Phase 3: Architecture cleanup

- reduce formula duplication
- centralize defaults and pricing authority

## Phase 4: Visual polish

- unify commerce-local visual tokens
- improve hierarchy consistency
- reduce "mixed-style" feeling across e-commerce surfaces

---

## 10. Final Recommendation

The system is already powerful enough.

The highest-value work now is not adding more features.

It is:

- reducing clutter
- separating concerns
- removing duplication
- making recommendations clearer
- making the UI feel more intentional

The target standard should be:

"Fast to enter, easy to trust, and obvious what to do next."
