# AITOS Full Project Review

Date: 2026-03-20  
Reviewer: Codex

## Validation Snapshot

### Verified Successfully
- Full backend suite: `268 passed, 1 warning`
- Dashboard production build: passed

### Remaining Warning
- Windows pytest cache warning for `.pytest_cache`
- This is not a product/runtime correctness failure

## Overall Assessment

The project is already beyond prototype stage. The core AITOS shape is real:

- Python-first control plane is working
- workflow runtime / graph / approval primitives are in place
- Flow Lab screenshot and video M1 paths exist
- dashboard pages build successfully
- tests are broad and improving

The repo is in a strong state, but there are still several architectural and product-level issues that should be treated as active follow-up work.

## Primary Findings

### 1. Review inbox and approval system are still semantically split
Severity: High

Evidence:
- `src/api/routes/review.py`
- `src/api/routes/workflows.py`
- live DB counts observed during review:
  - `review_items`: pending = 2
  - `approval_requests`: pending = 28

Why this matters:
- The system currently has two approval surfaces:
  - `review_items`
  - `approval_requests`
- Even after the bridge work, they still do not represent the same queue.
- A CEO can reasonably assume “my review queue shows everything pending”, but that is not currently true.

Impact:
- UI trust issue
- possible missed approvals
- confusing product behavior when some items appear in Office approval cards but not in Review Queue

Recommendation:
- Either fully unify around one approval model
- or clearly separate:
  - `workflow approvals`
  - `curated CEO review inbox`
- and label both explicitly in UI

### 2. Review-item dedup is now too coarse and can hide real pending requests
Severity: High

Evidence:
- `src/workflows/approval.py:63-76`

Current behavior:
- review-item creation is skipped when there is already a pending `review_item` for the same `action`
- the dedup key is effectively action-only

Why this matters:
- if two different screenshot approvals exist at the same time, only one mirrored inbox item may be created
- same problem for video approvals or publish actions
- this reduces noise, but it can also hide real pending work

Impact:
- potential missing CEO decisions
- invisible backlog
- mismatch between `approval_requests` and `review_items`

Recommendation:
- dedup by a more specific key:
  - action + run_id
  - or action + approval_id
  - or action + evidence hash
- do not dedup all pending requests by action alone

### 3. Frontend API base configuration is inconsistent
Severity: Medium

Evidence:
- `dashboard/src/lib/api.ts:156,172,202,235,255,266,277,292,300,317`
- `dashboard/src/app/office/page.tsx:358,532,576,744,1047`
- `dashboard/src/app/metrics/page.tsx:10`
- `dashboard/src/app/chat/page.tsx:512`

Current state:
- some code uses `NEXT_PUBLIC_API_URL`
- some code uses `NEXT_PUBLIC_API_BASE`
- some code uses proxy-relative `/api/...`
- some code calls `http://localhost:8000` directly

Why this matters:
- harder deployment configuration
- easier to break one page while another page still works
- makes debugging proxy/runtime issues more confusing

Recommendation:
- standardize on one env var
- define a single API origin helper
- clearly separate:
  - proxy-relative GETs
  - direct backend POST/PATCH/DELETE exceptions if truly needed

### 4. Runtime proxy/backend responsiveness issue still exists as an operational risk
Severity: Medium

Evidence:
- documented separately in `projects/anticlaude/proxy_socket_hangup_issue_20260320.md`
- affected routes:
  - `/api/review-queue/stats`
  - `/api/approvals/pending`

Why this matters:
- build and tests passing does not guarantee local runtime health
- dev UX is degraded when the dashboard proxy hangs or resets

Recommendation:
- add a live health-check workflow
- add backend startup/status verification before dashboard polling
- consider softer UI fallback for non-critical polling widgets

### 5. Mojibake remains in runtime code and user-facing text
Severity: Medium

Evidence:
- `src/adapters/registry.py`
- `src/utils/notify.py`
- `dashboard/src/lib/api.ts`
- several dashboard pages and comments still contain garbled text fragments

Important note:
- a replacement-character scan (`�`) is no longer flagging files
- however, mojibake still exists as corrupted-but-valid UTF-8 text

Why this matters:
- poor operator UX
- confusing labels and maintenance burden
- harder onboarding for future contributors

Recommendation:
- run a targeted cleanup pass on runtime/UI strings
- prioritize:
  - dashboard labels
  - adapter descriptions
  - comments that affect maintenance

### 6. External adapter architecture is mostly good, but still uneven in maturity
Severity: Medium

Evidence:
- `src/adapters/registry.py`
- `src/adapters/x_adapter.py`
- `src/adapters/chrome_cdp_adapter.py`
- `src/adapters/line_adapter.py`

Assessment:
- X adapter is in reasonable shape
- LINE adapter now exists and is better aligned
- Chrome/CDP exists, but should still be treated as high-risk and not “fully productized”
- video frame extractor is still planned-only

Recommendation:
- keep adapter maturity visible in docs/UI
- do not treat all “active” adapters as equally production-ready

## Architecture Review

### What Looks Good
- `src/workflows/`
  - real workflow primitives and graph runtime
- `src/domains/`
  - domain migration has started materially
- `src/adapters/`
  - external integrations are being normalized through contracts
- dashboard
  - enough UI exists to inspect runs, approvals, Flow Lab, and reports

### What Is Still Transitional
- `review_items` vs `approval_requests`
- legacy shims vs fully migrated domain modules
- direct backend calls vs proxy-relative calls
- governance docs vs runtime-enforced behavior

## Documentation / File Structure Review

### Strong
- `projects/anticlaude/` now serves as a substantial planning and audit layer
- backlog, audit, roadmap, governance, and integration documents are all traceable

### Risk
- document volume is now large enough that duplication is likely
- some newer docs supersede older ones, but that relationship is not always obvious

Recommendation:
- keep `README_spec_index_20260318.md` current
- archive superseded planning docs aggressively
- separate:
  - active specs
  - historical notes
  - completed audits

## Suggested Next Priorities

1. Fix approval-model clarity
   - decide whether `review_items` is a full mirror or a curated inbox
   - then make UI and DB semantics match

2. Refine review dedup logic
   - reduce noise without hiding distinct pending approvals

3. Standardize frontend API origin handling
   - one env var
   - one helper
   - fewer ad hoc direct-base calls

4. Clean mojibake in user-facing surfaces
   - especially dashboard and adapter descriptions

5. Keep runtime health separate from build health
   - add operational checks for local backend responsiveness

## Practical Conclusion

The project is structurally strong and already usable, but it is not yet “fully clean and complete”.

The most important remaining problem is no longer missing features. It is alignment:

- approval semantics
- queue visibility
- runtime consistency
- UI text quality

If these are cleaned up, the system will move from “impressive and working” to “trustworthy and operationally clear”.
