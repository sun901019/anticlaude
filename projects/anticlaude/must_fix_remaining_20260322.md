# Must-Fix Remaining Items (2026-03-22)

## Purpose

This file summarizes the highest-priority remaining issues across the project after the latest architecture, UX, and feature progress.

It is intentionally short and execution-oriented.

---

## P0: Critical Engineering Trust Issues

### 1. Fix the broken pytest baseline

Problem:

- full test suite currently fails at fixture setup
- root cause is `tests/conftest.py`
- `isolated_test_db(tmp_path_factory)` uses Windows temp root and hits `PermissionError`

Impact:

- backend cannot be reliably verified
- new regressions are masked
- engineering trust is degraded

Required fix:

- move isolated test DB creation to repo-local temp path
- keep `ANTICLAUDE_DB` override
- re-run full `pytest`

Success condition:

- full suite returns to green or exposes only real post-fixture failures

---

### 2. Normalize task-type contracts across the whole AI stack

Problem:

- CEO, registry, dynamic orchestrator, and skill routing do not agree on supported task types
- visible symptom: `unsupported task_type: system_debugging`

Known mismatches:

- `system_debugging`
- `audience_analysis`
- `competitor_analysis`
- `content_planning`
- `backend_development`
- `ui_implementation`
- `design_evaluation`
- `ux_review`
- `product_evaluation`

Impact:

- Lara/CEO may route tasks that the executor layer cannot actually run
- AI employee system feels unreliable

Required fix:

- define one canonical task-type list
- make these 4 layers match:
  - `src/agents/ceo.py`
  - `_hub/registry/registry_schema.json`
  - `src/agents/dynamic_orchestrator.py`
  - `src/ai/skill_routing.py`

Success condition:

- all user-facing routed task types are registered, handled, and skill-routed consistently

---

## P1: Runtime Stability and Signal Quality

### 3. Reduce Next.js dev-runtime instability

Problem:

- intermittent `ECONNRESET`
- proxy `socket hang up`
- occasional `.next/server/pages/_document.js` / `MODULE_NOT_FOUND`

Likely cause:

- stale `.next` artifacts
- Windows dev HMR instability
- heavy dev recompilation / proxy timing mismatch

Impact:

- local operator confidence drops
- false perception that app is broken

Required fix:

- define a stable local dev cleanup flow
- reduce polling pressure on fragile endpoints
- improve fail-soft handling in frontend
- review any app/pages-router legacy residue if issues persist after cache reset

Success condition:

- dev runtime errors become rare and recoverable

---

### 4. Clean up runtime warning noise

Problem:

- warning logs mix:
  - test noise
  - missing optional files
  - missing local credentials
  - real runtime issues

Impact:

- hard to distinguish real failures from harmless noise

Required fix:

- downgrade optional missing-file logs
- improve diagnostics for real warnings
- separate test noise from operator-facing runtime interpretation

Examples to improve:

- missing `outputs/daily_reports/YYYY-MM-DD.*`
- `publish_post approved but no draft text found`

Success condition:

- logs become easier to trust and triage

---

## P1: E-commerce Logic / UX Integrity

### 5. Make backend pricing the only source of truth

Problem:

- frontend still computes a significant amount of pricing logic
- backend already has canonical `calc_full_cost()`

Impact:

- drift risk between UI and API
- duplicated maintenance

Required fix:

- frontend should request/display backend results
- keep only lightweight preview UX on frontend if absolutely necessary
- centralize role suggestion / fee logic / recommendation logic on backend

Success condition:

- one authoritative pricing engine

---

### 6. Finish the e-commerce UX cleanup

Problem:

- e-commerce surface is much better now, but still not fully clean

Remaining friction:

- Quick Add still too heavy
- Product Detail still mixes fact/simulation/action
- Inbound modal still underpowered as a procurement decision tool
- top-level `Pricing Decision` may overlap with Product Detail
- manual/help still needs e-commerce-only scope

Required fix:

- keep refining according to the latest e-commerce UX specs

Success condition:

- product feels simpler, calmer, and more professional without losing capability

---

## P2: Productization Gaps

### 7. Finish partially productized integrations

Areas still not fully mature:

- Figma: integrated, but not a full design-to-frontend workflow
- Browser/CDP: controlled capability, not mature product flow
- Video: progressed, but still needs final hardening
- X / LINE: partially integrated, still need final operator-grade polish in some paths

Impact:

- not blocking core operation
- still worth finishing after core engineering cleanup

---

## Recommended Execution Order

1. Fix `tests/conftest.py`
2. Re-run full backend test suite
3. Normalize task-type contracts
4. Reduce runtime log noise
5. Stabilize local Next dev runtime
6. Deduplicate e-commerce pricing logic
7. Complete e-commerce UX cleanup
8. Finish lower-priority productization gaps

---

## Final Guidance

The project is already strong in shape and scope.

The remaining work is not a rewrite.
It is the last phase of:

- engineering trust repair
- contract alignment
- runtime cleanup
- UX refinement
- product polish
