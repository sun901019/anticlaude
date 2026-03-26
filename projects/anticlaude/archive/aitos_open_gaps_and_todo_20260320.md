# AITOS Open Gaps and TODO 2026-03-20

## Purpose

This document is the current execution backlog for AITOS.
It summarizes what is still missing, partially implemented, or high-priority for follow-up.

Use this file as the primary "what to do next" reference for implementation agents.

---

## 1. Highest-Priority Gaps

These are the most important items because they affect architecture correctness, safety, or CEO control.

### 1. Approval Gate Enforcement ✅ DONE 2026-03-20

- Rejected approval → `fail_run()` immediately on resume (graph.py)
- Approved gate → added to `completed_nodes`, skipped cleanly
- `list_approvals_for_run()` added to checkpoint_store.py
- Tests: `test_resume_skips_approved_gate`, exhausted retry, soft failure
- **Remaining**: test for unauthorized direct resume (no approval record at all) — low priority now that hard gate is in place

### 2. Graph Dependency Semantics ✅ DONE 2026-03-20

- `save_outputs.depends_on` now includes `["draft_generation", "draft_approval"]` when `with_approval_gate=True`
- Added test: `test_save_outputs_depends_on_approval_gate`

### 3. Unified Approval Model ✅ DECIDED 2026-03-20

**Decision**: Keep both tables, define layers, bridge not merge.
- `approval_requests` = machine gate (tied to run_id, controls workflow continuation)
- `review_items` = CEO inbox (UI-facing, options/recommended/deadline, not tied to run)
- Correct bridge: approval gate may optionally create a review_item; CEO decision on review_item syncs back to approval_request.status
- See `ai/state/decisions.md` for full rationale

---

## 2. Major Architecture Gaps

### 4. Domain Isolation Not Fully Landed

Target direction:
- `src/domains/flow_lab/`
- `src/domains/media/`
- `src/domains/trading/`

Current state:
- architecture direction is documented
- implementation still mostly lives in legacy flat modules

Required follow-up:
- gradually move business logic into bounded domain packages
- avoid one-shot rewrite
- start with:
  - media workflow logic
  - flow_lab screenshot workflow
  - trading reserved as future isolated domain only

### 5. Adapter Boundary Not Fully Applied

Current state:
- `src/adapters/` exists
- registry exists
- X and Figma stubs exist

Open problem:
- not all external integrations are routed through adapters yet
- browser/CDP remains planned, not implemented

Required follow-up:
- move all external-facing integrations behind adapter contracts
- define timeout / retry / risk_level consistently
- keep browser control disabled until session isolation and approval rules exist

### 6. Workflow Runtime Not Yet Universal

Current state:
- workflow primitives exist
- graph runtime exists
- daily content pipeline has a graph path

Open problem:
- not all major workflows use the same runtime yet
- some flows still use older orchestration paths

Required follow-up:
- choose the target runtime for each workflow:
  - daily content
  - Flow Lab visual workflow
  - review/approval workflow
  - future multimodal workflow
- reduce parallel orchestration patterns over time

---

## 3. Content and Media Gaps

### 7. GEO Skill Lifecycle ✅ DONE 2026-03-20

- Replaced `@lru_cache` with mtime-based manual cache in `src/ai/skill_loader.py`
- Cache entry: `skill_name → (mtime_ns, content)`; auto-reloads if file changed
- MAX_CACHE_SIZE=32, FIFO eviction; `invalidate_skill_cache()` for manual control
- Tests: `tests/test_skill_cache.py` (8 tests: hit, invalidation, eviction, frontmatter strip, missing skill)

### 8. Content Workflow Coverage

Current state:
- `src/content/` exists
- topic fit, similarity guard, engagement plan, and scoring exist

Open problem:
- these modules are not yet consistently wired into every content path

Required follow-up:
- ensure topic selection, drafting, approval packaging, and reporting all use the same scoring/ranking logic
- document where each content module is applied

### 9. Threads Safety and Publishing Separation

Current state:
- Threads publishing exists via API
- metrics collection exists

Open problem:
- research identity vs publishing identity separation is still mostly a planning rule, not a system-enforced boundary

Required follow-up:
- document and enforce source/publishing separation
- keep scraping/browsing workflows isolated from production posting credentials

---

## 4. Multimodal and Flow Lab Gaps

### 10. Video Ingestion Is Not Implemented Yet

Current state:
- multimodal deliberation is planned
- image-based CEO and Flow Lab workflows exist

Open problem:
- video upload / frame extraction / transcript / artifact generation is still spec-level

Required follow-up:
- define upload path
- define frame extraction/transcript adapter
- define `VideoInsightArtifact`
- define review UI for video-derived insights

### 11. Flow Lab Phase 2 Not Started

Current state:
- screenshot-first Flow Lab workflow exists

Open problem:
- URL-based ingestion for 1688 / Taobao is not implemented
- anti-bot-safe adapter strategy is still planning only

Required follow-up:
- keep this in planning until adapter and risk controls are mature
- if started later, begin with supervised research-only ingestion

---

## 5. Data and Model Gaps

### 12. Artifact Taxonomy ✅ DONE 2026-03-20

- Added `"selection_report"` to `ArtifactType` Literal in `src/workflows/models.py`
- Pydantic now validates artifact_type on every Artifact model creation
- All known types covered: draft, analysis, report, product_spec, screenshot_extraction, weekly_report, nightly_summary, selection_report, other
- **Remaining**: if new types are added by future modules, they must be added to this Literal

### 13. Datetime Handling ✅ DONE 2026-03-20

- Migrated all `datetime.utcnow()` → `datetime.now(timezone.utc)` in:
  - src/workflows/models.py
  - src/workflows/checkpoint_store.py
  - src/workflows/runner.py
  - tests/test_graph_workflow.py
- 0 DeprecationWarnings in test suite

### 14. Encoding / Mojibake Debt Still Exists

Current state:
- new planning docs are clean
- runtime still contains mojibake in multiple files and strings

Required follow-up:
- perform a controlled encoding cleanup pass
- prioritize:
  - user-visible strings
  - logs
  - comments that affect maintenance

---

## 6. Tooling and UI Gaps

### 15. Browser Control Is Still Planned Only

Current state:
- browser/CDP appears in registry as planned

Open problem:
- no real Chrome/Edge session control is implemented yet

Required follow-up:
- do not treat browser control as available
- if implemented later:
  - use isolated profile
  - require explicit approval
  - keep it outside unattended production flows

### 16. CEO Visibility Is Improving but Not Complete

Current state:
- office page shows artifacts and workflow runs
- Flow Lab page exists

Open problem:
- not every workflow exposes a full CEO decision package
- approval evidence packaging is still inconsistent

Required follow-up:
- standardize CEO-facing package:
  - summary
  - risk
  - evidence
  - artifact links
  - approve / reject action

---

## 7. Future Work That Should Stay Deferred

These are valid directions, but should not be mixed into the current production path yet.

### Deferred but Planned
- CoinCat trading system
- live browser automation
- autonomous trading execution
- high-risk scraping paths
- full graph migration of all workflows at once

Reason:
- they require stricter isolation, stronger runtime controls, and more mature approval enforcement

---

## 8. Recommended Execution Order

If an implementation agent continues from here, the recommended order is:

1. Fix approval gate enforcement in graph resume flow
2. Tighten graph dependency semantics around approval nodes
3. Unify approval model (`review_items` vs `approval_requests`)
4. Add artifact taxonomy validation
5. Clean up timezone-aware datetime usage
6. Expand domain isolation gradually (`media`, `flow_lab`)
7. Standardize CEO decision package output
8. Implement skill cache invalidation/versioning
9. Plan video ingestion in executable detail
10. Defer CoinCat and high-risk browser automation until core safety is stronger

---

## 9. Direct Instruction for Implementation Agents

When using this document:

- do not re-open broad architecture debates unless a conflict is found
- prioritize the items in Section 1 first
- do not treat planned capabilities as implemented capabilities
- update `ai/state/sprint.md` and `ai/state/progress-log.md` after each completed item
- if an item is deferred, write the reason explicitly instead of silently skipping it
