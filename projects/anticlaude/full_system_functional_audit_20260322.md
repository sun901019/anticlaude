# Full System Functional Audit (2026-03-22)

## Executive Summary

The project is **not generally broken**, but it is **not fully healthy** either.

Current state:

- Frontend production build: **PASS**
- Backend full test suite: **FAIL**
- Main cause of test-suite failure: **one session fixture regression**
- Additional functional inconsistency found: **task-type contract mismatch across CEO / registry / orchestrator layers**

This means:

- the UI can still build and ship
- many runtime features are likely still usable
- but the engineering trust baseline is currently degraded

---

## 1. Baseline Validation

### 1.1 Frontend build

Command:

- `npm run build` in `dashboard/`

Result:

- **PASS**
- 18 pages generated successfully

This confirms:

- current app-router structure is valid
- type-checking passed in production build
- there is no active build-blocking frontend regression

### 1.2 Backend tests

Command:

- `python -m pytest tests -q`

Result:

- **FAIL**
- `349 errors`

Important clarification:

- this is **not** 349 unrelated feature failures
- almost the entire suite is failing because of a **single fixture-level setup error**

---

## 2. Primary Active Failure: Test DB Isolation Fixture

### 2.1 Root cause

File:

- `tests/conftest.py`

Problem:

- the session-scoped fixture `isolated_test_db(tmp_path_factory)` calls:
  - `tmp_path_factory.mktemp("db")`
- on this Windows environment, pytest tries to create that under:
  - `C:\\Users\\sun90\\AppData\\Local\\Temp\\pytest-of-sun90`
- that path currently throws:
  - `PermissionError: [WinError 5] Access denied`

### 2.2 Practical effect

Because the fixture is `autouse=True` and session-scoped:

- every test depends on it
- fixture setup fails before tests really run
- the suite collapses into a wall of `PermissionError`

### 2.3 Severity

**Critical**

This is the single highest-priority engineering issue right now, because:

- it blocks confidence in the entire backend
- it masks real regressions
- it prevents clean functional verification

### 2.4 Recommended fix

Do not use pytest temp roots that resolve into the system temp directory.

Instead:

- create the isolated test DB inside the repo-local temp area
  - e.g. `tests/.tmp/pytest-db/...`
- keep using `ANTICLAUDE_DB` env override
- ensure bootstrap schema still runs on the repo-local DB

---

## 3. Task-Type Contract Audit

## 3.1 Layers compared

The following layers should agree on task types:

1. `src/agents/ceo.py` -> `ROUTING_MAP`
2. `_hub/registry/registry_schema.json` -> `routing_rules.mappings`
3. `src/agents/dynamic_orchestrator.py` -> `HANDLERS`
4. `src/ai/skill_routing.py` -> `TASK_SKILL_ROUTES`

### 3.2 Findings

These task types currently do **not** align across layers:

- `system_debugging`
  - present in CEO only
- `audience_analysis`
  - present in CEO only
- `competitor_analysis`
  - present in CEO only
- `content_planning`
  - present in registry only
- `backend_development`
  - present in CEO + registry
  - missing in handlers + skill routes
- `ui_implementation`
  - present in CEO + registry
  - missing in handlers + skill routes
- `design_evaluation`
  - present in CEO + registry
  - missing in handlers + skill routes
- `ux_review`
  - present in CEO + registry
  - missing in handlers + skill routes
- `product_evaluation`
  - present in CEO + handlers + skill routes
  - missing in registry

### 3.3 Most visible symptom

This explains errors like:

- `unsupported task_type: system_debugging`

Reason:

- CEO routes it
- registry does not register it
- dynamic orchestrator does not handle it

### 3.4 Severity

**High**

This breaks AI routing reliability and operator trust.

### 3.5 Recommended fix

Create one canonical task-type contract and make all 4 layers match.

Minimum acceptable action:

- either fully support a task type across all layers
- or remove it from CEO-facing routing

---

## 4. Runtime Warning Review

### 4.1 Most warnings are not catastrophic

Previously inspected runtime warnings fall into these buckets:

- test noise
- missing local API keys/tokens
- missing optional output files for "today"

Examples:

- `ANTHROPIC_API_KEY` not set
- `THREADS_ACCESS_TOKEN` missing/expired
- `SERPER_API_KEY` missing
- today's draft/report files missing

These are not system-wide breakages.

### 4.2 Real runtime cleanup targets still worth doing

- missing-file warnings from `/api/today` are too noisy
- `publish_post approved but no draft text found` needs stronger diagnostics
- dev proxy noise (`ECONNRESET`, `socket hang up`) should be softened by better polling/backoff behavior

Severity:

- **Medium**

These mostly affect operator confidence and local-dev stability.

---

## 5. Frontend / API Contract Check

### 5.1 API base env var

Current check:

- `dashboard/src/lib/api.ts` uses `NEXT_PUBLIC_API_BASE`

Observation:

- no mixed use of `NEXT_PUBLIC_API_URL` was found in the checked frontend sources

Conclusion:

- this specific env-var inconsistency appears cleaned up

### 5.2 Review queue / approval semantics

Observation:

- there is a documented and mostly coherent split:
  - `review_items` = curated operator inbox
  - `approval_requests` = workflow-internal gate

Conclusion:

- the model is much better than before
- but semantic complexity remains high and requires continued discipline

Severity:

- **Low to Medium**

---

## 6. E-commerce Surface

### 6.1 Functional status

The e-commerce page still builds and the overall architecture is viable.

Known quality issues remain, but they are mainly:

- UX overload
- duplicated pricing logic between frontend and backend
- mixed concerns between product facts, simulation assumptions, and global settings

These are **refinement issues**, not current hard failures.

### 6.2 Severity

- **Medium**

This affects usability more than runtime correctness.

---

## 7. What Is Healthy Right Now

These areas currently look stable enough:

- frontend production build
- app-router page generation
- overall domain layout direction
- review/approval architecture direction
- e-commerce page existence and operator coverage
- Figma / Flow Lab / Office / Review surfaces still present in build

---

## 8. What Is Not Healthy Right Now

### Critical

1. Full backend verification is blocked by test fixture regression

### High

2. Task-type routing contract mismatch across CEO / registry / handlers / skill routing

### Medium

3. Runtime warning noise still obscures real issues
4. Frontend/backend pricing logic duplication still exists in e-commerce
5. Local dev proxy stability remains noisy

---

## 9. Recommended Priority Order

1. Fix `tests/conftest.py` DB isolation fixture to use repo-local temp DB
2. Re-run full pytest and identify real post-fixture failures
3. Normalize task-type contract across all 4 layers
4. Reduce warning noise and improve diagnostic clarity
5. Continue e-commerce UX / pricing dedup refinement after engineering trust baseline is restored

---

## 10. Final Conclusion

The project is **close to strong**, but **not yet fully trustworthy** from an engineering health perspective.

Most important truth:

- the frontend is shippable
- the backend is not currently verifiable because the test harness is broken

So the system is **not "missing everything"**.
It is instead in this state:

- product shape: strong
- build health: strong
- test trust: currently broken
- orchestration contract consistency: incomplete

That is the correct diagnosis.
