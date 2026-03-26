# Full Markdown Implementation Gap Audit

Date: 2026-03-21
Scope: repo-wide `.md` audit from the perspective of current AITOS architecture, implemented code, active specs, and remaining execution gaps.

## 1. Audit Method

This audit separates markdown files into four groups:

1. Active system specs
2. Operational collaboration docs
3. Historical or archived planning docs
4. External library/reference docs

Only groups 1 and part of group 2 should be treated as implementation commitments.

This is important because the repo contains many `.md` files that are:
- historical
- reference-only
- external imported knowledge
- generated outputs

Those should not be counted as "unfinished implementation work" unless they were explicitly promoted into the active AITOS roadmap.

## 2. What Counts As Active Implementation Scope

The active implementation scope currently comes mainly from:

- [README_spec_index_20260318.md](C:\Users\sun90\Anticlaude\projects\anticlaude\README_spec_index_20260318.md)
- [ultimate_optimization_master_checklist_20260320.md](C:\Users\sun90\Anticlaude\projects\anticlaude\ultimate_optimization_master_checklist_20260320.md)
- [full_project_review_20260320.md](C:\Users\sun90\Anticlaude\projects\anticlaude\full_project_review_20260320.md)
- [aitos_master_spec_index_and_operating_sop_20260318.md](C:\Users\sun90\Anticlaude\projects\anticlaude\aitos_master_spec_index_and_operating_sop_20260318.md)
- [aitos_execution_plan_20260319.md](C:\Users\sun90\Anticlaude\projects\anticlaude\aitos_execution_plan_20260319.md)
- [aitos_open_gaps_and_todo_20260320.md](C:\Users\sun90\Anticlaude\projects\anticlaude\aitos_open_gaps_and_todo_20260320.md)

These are the main documents that should drive execution.

## 3. Files That Should NOT Be Treated As Missing Implementation

These file families are real and useful, but should not be counted as "unfinished features":

### 3.1 Historical archives

- `projects/anticlaude/archive/*.md`
- `_archive/*.md`

These are historical plans and earlier snapshots.
They should be preserved or archived, not executed as current roadmap items.

### 3.2 Generated outputs

- `outputs/drafts/*.md`
- `outputs/office_memory/*.md`
- `outputs/daily_reports/*.md`
- `outputs/weekly_reports/*.md`

These are artifacts, not specs.

### 3.3 External libraries / imported skill repos

- `_hub/skills_library/**`
- most `_hub/shared/**` reference markdown
- `dashboard/node_modules/**`

These are references or third-party content.
They should influence the system only when explicitly adopted into active AITOS specs or runtime behavior.

### 3.4 Collaboration logs

- `ai/state/sprint.md`
- `ai/state/progress-log.md`
- `ai/handoff/*.md`

These are operational memory, not architecture promises.

## 4. What Is Already Materially Implemented

From an architecture perspective, the following major spec themes are already materially real:

### 4.1 Python-first AITOS control plane

Implemented:
- FastAPI control plane
- APScheduler usage
- SQLite persistence
- route modularization
- workflow runtime models

Status:
- implemented

### 4.2 Workflow runtime foundation

Implemented:
- `run`
- `task`
- `event`
- `artifact`
- `approval_request`
- graph runner
- pause/resume
- CEO decision package

Files:
- [src/workflows](C:\Users\sun90\Anticlaude\src\workflows)

Status:
- implemented

### 4.3 Flow Lab visual-first workflow

Implemented:
- screenshot upload path
- screenshot analysis path
- video upload M1 path
- artifacts
- approvals
- dashboard Flow Lab page

Status:
- screenshot path implemented
- video path partially implemented

### 4.4 Skills and routing foundation

Implemented:
- skill loader
- skill routing matrix
- runtime usage for several composite skills
- workflow usage for multiple operational skills

Status:
- implemented but not fully enforced everywhere

### 4.5 External adapter foundation

Implemented:
- adapter base
- registry
- x adapter
- figma adapter
- line adapter
- chrome cdp adapter
- video frame adapter stub

Status:
- foundation implemented
- maturity uneven

### 4.6 Domain migration foundation

Implemented:
- `src/domains/media`
- `src/domains/flow_lab`
- `src/domains/trading`
- migration of several major media/flow_lab modules

Status:
- partial to strong
- not fully complete

## 5. Real Remaining Gaps From The Active Markdown Specs

These are the actual unfinished items that still matter after cross-checking the docs against the codebase.

## 5.1 Approval surface is still semantically split

Current state:
- `approval_requests` exists
- `review_items` exists
- bridging exists
- they are not yet one fully clean semantic model

Why it matters:
- CEO inbox trust
- queue visibility
- operator understanding

Code evidence:
- [approval.py](C:\Users\sun90\Anticlaude\src\workflows\approval.py)
- [review.py](C:\Users\sun90\Anticlaude\src\api\routes\review.py)
- [workflows.py](C:\Users\sun90\Anticlaude\src\api\routes\workflows.py)

Status:
- partially implemented
- still needs semantic unification

## 5.2 Review dedup logic is still too coarse

Current state:
- review inbox mirroring uses a pending-count cap by action
- this reduces spam but can still hide distinct pending items

Code evidence:
- [approval.py](C:\Users\sun90\Anticlaude\src\workflows\approval.py)

Status:
- not fully resolved

Recommended direction:
- replace action-only grouping with a key such as:
  - `action + approval_id`
  - `action + run_id`
  - evidence fingerprint

## 5.3 Frontend backend-origin handling is not yet fully unified

Current state:
- `dashboard/src/lib/api.ts` uses `NEXT_PUBLIC_API_BASE`
- some pages still use `NEXT_PUBLIC_API_URL`
- some calls use proxy-relative `/api`

Code evidence:
- [api.ts](C:\Users\sun90\Anticlaude\dashboard\src\lib\api.ts)
- [metrics/page.tsx](C:\Users\sun90\Anticlaude\dashboard\src\app\metrics\page.tsx)
- [chat/page.tsx](C:\Users\sun90\Anticlaude\dashboard\src\app\chat\page.tsx)

Status:
- partially implemented
- still needs convergence

## 5.4 Runtime proxy/backend responsiveness remains an operational risk

Current state:
- proxy and route definitions exist
- there has already been an observed `ECONNRESET / socket hang up` runtime issue
- this is not fully solved at the system-operability layer

Relevant doc:
- [proxy_socket_hangup_issue_20260320.md](C:\Users\sun90\Anticlaude\projects\anticlaude\proxy_socket_hangup_issue_20260320.md)

Status:
- unresolved operational issue

## 5.5 Mojibake cleanup is not finished

Current state:
- major corruption improved
- replacement-char scans are better
- many runtime comments/labels/descriptions still contain garbled text

Likely impact areas:
- adapter descriptions
- config comments
- dashboard labels
- older route comments

Status:
- partially implemented

## 5.6 Domain migration is not fully complete

Current state:
- media and flow_lab moved substantially
- trading remains skeletal
- some shim/backward-compat paths still exist

Code evidence:
- [src/domains](C:\Users\sun90\Anticlaude\src\domains)

Status:
- partially implemented

## 5.7 GEO/SEO is only partially enforced

Current state:
- skill docs and runtime injection exist
- GEO/SEO guidance is real
- enforcement is not yet universal across every content path

Meaning:
- some flows are strongly GEO-aware
- others still rely on conventions rather than hard review gates

Status:
- partially implemented

## 5.8 Figma is integrated, but not productized into a full design-to-frontend workflow

Current state:
- Figma client exists
- Figma adapter exists
- registry entry is active
- token config exists
- read-only only

Missing:
- dedicated operator workflow
- design-token extraction layer
- UI for node selection / preview
- full implementation path into frontend generation

Relevant doc:
- [figma_integration_status_20260321.md](C:\Users\sun90\Anticlaude\projects\anticlaude\figma_integration_status_20260321.md)

Status:
- partially implemented

## 5.9 Video ingestion is still only M1

Current state:
- upload exists
- DB record exists
- approval path exists
- adapter exists only as stub
- frame extraction M2 is blocked

Code evidence:
- [video_adapter.py](C:\Users\sun90\Anticlaude\src\adapters\video_adapter.py)
- [flowlab/page.tsx](C:\Users\sun90\Anticlaude\dashboard\src\app\flowlab\page.tsx)

Status:
- partially implemented

## 5.10 Browser/CDP is present but still not a trusted production capability

Current state:
- adapter exists
- registry marks it active
- governance is still intentionally conservative

Missing:
- session-isolation policy
- hardened approval rules
- clear operator workflow
- production trust level

Status:
- implemented as guarded capability
- not yet productized

## 5.11 LINE business workflows are not fully complete

Current state:
- LINE notify helper and adapter exist
- basic notification plumbing exists

Still missing:
- competitor-price alert workflow completion
- price-drop alert productization
- fully verified weekly/report notification path

Status:
- partially implemented

## 5.12 X is mostly implemented but still needs final end-to-end hardening

Current state:
- X publish client exists
- search module exists
- adapter exists
- direct tests were added

Still worth improving:
- final approval -> publish verification
- stronger end-to-end mocked integration path
- operator-facing flow clarity

Status:
- mostly implemented

## 5.13 1688 / Taobao URL-based ingestion is not implemented

Current state:
- screenshot-first Flow Lab path exists
- URL adapter path was always a later phase

Status:
- intentionally not implemented yet

This is not a regression.
It is still a planned future phase.

## 5.14 A/B testing and some content-optimization items remain open

Examples from planning layer:
- A/B test mechanism
- engagement-plan maturity
- some stronger content intelligence loops

Status:
- partially implemented

## 5.15 Trading domain is only planned/skeleton

Current state:
- domain folder exists
- CoinCat planning docs exist
- no real bounded trading system is active in the main runtime

Status:
- intentionally deferred

This should not be forced into current mainline implementation yet.

## 6. Architecture-Fit Assessment

From the perspective of your desired system architecture, the current repo is:

- strongly aligned with Python-first control plane
- strongly aligned with workflow runtime + approval model
- strongly aligned with Flow Lab screenshot-first direction
- moderately aligned with full domain-driven separation
- moderately aligned with full multimodal deliberation
- moderately aligned with fully governed skill enforcement
- partially aligned with polished operator-facing design workflow

So the project is not off-track.
It is in a late-stage convergence phase.

## 7. Files Or Document Families That Can Be Consolidated Later

These are not immediate delete candidates, but they are likely future consolidation targets:

### 7.1 Overlapping active audits and plans

Examples:
- `aitos_recommended_optimization_master_plan_20260317.md`
- `aitos_next_steps_roadmap_20260318.md`
- `current_gap_optimization_and_cleanup_review_20260320.md`
- `ultimate_optimization_master_checklist_20260320.md`
- `full_project_review_20260320.md`

These are all useful, but long-term they should probably collapse into:
- one master roadmap
- one master review
- one master optimization checklist

### 7.2 Old one-off planning docs

Examples:
- `plan_20260317_langgraph_geo_aitos_v2.md`
- older archived `plan_20260314*` and `plan_20260315*`

These should stay historical, not active.

### 7.3 Integration-note docs that may later become handbook sections

Examples:
- `x_and_figma_api_integration_notes_20260318.md`
- `cross_platform_scraping_guidelines_20260318.md`
- `skill_design_governance_fit_review_20260320.md`

These may later be absorbed into:
- one tooling handbook
- one skill governance handbook

## 8. Recommended Next Execution Priorities

If the goal is to align the codebase with the active markdown architecture as closely as possible, the next priorities should be:

1. Unify approval semantics
2. Fix review dedup logic
3. Unify frontend API origin handling
4. Continue mojibake cleanup
5. Finish domain migration cleanup and reduce shims
6. Harden GEO/SEO enforcement into review/routing
7. Advance video ingestion from M1 to M2
8. Complete LINE business-alert flows
9. Productize Figma workflow if design-to-code matters now
10. Keep Browser/CDP guarded until governance is complete

## 9. Bottom Line

After scanning the repo-wide markdown landscape against the current codebase:

- many markdown files are historical or reference-only and should not be treated as missing implementation
- the active AITOS architecture is already substantially real
- the remaining work is no longer broad feature invention
- the remaining work is convergence, semantic cleanup, selective productization, and technical debt reduction

The biggest true remaining gaps are:
- approval model clarity
- review dedup correctness
- API-origin consistency
- mojibake cleanup
- final domain convergence
- partial integrations becoming fully productized workflows
