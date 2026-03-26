# Claude Architecture Cleanup Brief (2026-03-22)

## Goal

This brief translates the latest architecture review into a focused cleanup task list for Claude.

Do **not** rewrite the whole project.
Do **not** expand scope with new features first.

Instead, fix the architectural inconsistencies and cleanup debt that most affect long-term stability and maintainability.

---

## Current Verified Baseline

- Backend test suite: `349 passed, 1 warning`
- Frontend production build: `PASS`

So this is **not** a broken system rescue task.
It is a **high-priority refinement and consistency cleanup** task.

---

## Priority 1: Normalize Task-Type Contracts

## Problem

Task-type support is still inconsistent across the AI stack.

The following layers must agree:

1. `src/agents/ceo.py`
2. `_hub/registry/registry_schema.json`
3. `src/agents/dynamic_orchestrator.py`
4. `src/ai/skill_routing.py`

Recent review found mismatch risk around task types such as:

- `system_debugging`
- `audience_analysis`
- `competitor_analysis`
- `content_planning`
- `backend_development`
- `ui_implementation`
- `design_evaluation`
- `ux_review`
- `product_evaluation`

## Required action

- Define one canonical set of supported task types
- Make all 4 layers match
- Remove dead task types or add missing support
- Ensure any task type reachable from CEO routing is actually executable downstream

## Success condition

- No CEO-routable task type should hit `unsupported task_type`
- Registry, handlers, and skill routes must be aligned

---

## Priority 2: Make Backend Pricing the Single Source of Truth

## Problem

The e-commerce domain still duplicates pricing logic:

- backend canonical pricing exists in `src/ecommerce/router.py`
- frontend still performs significant local pricing/preview logic in `dashboard/src/app/ecommerce/page.tsx`

This creates drift risk for:

- landed cost
- fee calculations
- role suggestion
- price recommendations
- market warnings

## Required action

- Keep backend `calc_full_cost()` as the only authority
- Reduce frontend logic to:
  - collect inputs
  - request backend estimate
  - render result
- Remove or reduce duplicated logic where practical

## Success condition

- Pricing logic changes require editing one authoritative source, not two

---

## Priority 3: Reduce E-commerce Page Overload

## Problem

`dashboard/src/app/ecommerce/page.tsx` currently carries too many responsibilities:

- dashboard
- products
- performance
- pricing decision
- settings
- manual
- selection/candidates
- analysis
- bundles
- reports
- lessons
- add product modal
- inbound modal
- product detail drawer
- mini review panel

This works, but it is now too dense and hard to maintain.

## Required action

Without rewriting the whole feature:

- extract smaller internal components or modules
- separate concerns more clearly
- reduce state sprawl in the main page file
- keep Product Detail, Quick Add, Inbound, Settings, and Pricing surfaces conceptually distinct

## Success condition

- `page.tsx` becomes easier to reason about
- UI changes in one area are less likely to break others

---

## Priority 4: Continue Mojibake Cleanup

## Problem

The project still contains corrupted Chinese text in:

- Python modules
- docs/specs
- UI strings
- collaboration/context files

This hurts:

- operator trust
- AI prompt quality
- maintainability
- future onboarding and debugging

## Required action

- clean mojibake in active runtime files first
- prioritize:
  - user-facing UI text
  - logs
  - architecture/runtime docs that affect implementation
- avoid mass blind replacements; fix high-signal files carefully

## Success condition

- critical active runtime files and user-facing surfaces no longer contain obvious garbled Chinese

---

## Scope Guidance

### In scope

- consistency cleanup
- contract cleanup
- pricing logic dedup
- e-commerce modular cleanup
- mojibake cleanup in active surfaces

### Out of scope

- large feature expansion
- full domain rewrite
- new product areas unrelated to current stability

---

## Recommended Execution Order

1. Normalize task-type contracts
2. Deduplicate pricing logic toward backend authority
3. Refactor `ecommerce/page.tsx` into smaller maintainable slices
4. Clean mojibake in active runtime/UI files
5. Re-run:
   - `python -m pytest tests -q`
   - `npm run build`

---

## Deliverable Expectation

At the end of the work, Claude should report:

1. Which task-type mismatches were fixed
2. Which pricing logic was removed from frontend or delegated to backend
3. Which e-commerce page slices were extracted or cleaned
4. Which mojibake files were fixed
5. Test and build verification results
