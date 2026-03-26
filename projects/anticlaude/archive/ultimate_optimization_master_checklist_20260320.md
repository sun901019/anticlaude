# AITOS Ultimate Optimization Master Checklist

Date: 2026-03-20  
Goal: drive the project from “working and promising” to “fully optimized, semantically clean, and maintainable”

---

## 0. North Star

Target end-state:

- one clear system architecture
- one clear approval model
- one clear workflow runtime
- one clear skill-routing model
- one clear domain layout
- one clear operator UI
- low-noise, high-trust CEO decision surfaces
- stable runtime behavior
- low ambiguity in docs, folders, and naming

This checklist is intentionally exhaustive and grouped by optimization objective:

- precision refinement
- convergence
- semantic unification
- technical debt cleanup

---

## 1. Precision Refinement

### 1.1 Approval semantics
- Decide whether `review_items` is:
  - a full mirror of all pending approvals
  - or a curated CEO inbox
- Remove the current in-between state.
- Define the contract for:
  - `approval_requests`
  - `review_items`
  - `approval package`
  - `workflow pause/resume`
- Ensure each approval action has:
  - human-readable summary
  - rationale
  - risk classification
  - artifact links
  - follow-up behavior

### 1.2 Review dedup behavior
- Replace action-only dedup with a safer key:
  - `action + run_id`
  - or `action + approval_id`
  - or `action + evidence fingerprint`
- Prevent inbox spam without hiding distinct pending requests.
- Add tests for:
  - same action, different run
  - same run, repeated trigger
  - multiple pending approvals of same action

### 1.3 API origin handling
- Standardize frontend backend-origin usage.
- Use one env variable only:
  - choose `NEXT_PUBLIC_API_URL` or `NEXT_PUBLIC_API_BASE`
- Define one helper for:
  - proxy-relative reads
  - direct backend writes when needed
- Remove ad hoc direct-base duplication across pages.

### 1.4 Review UI correctness
- Keep the new cleanup controls.
- Add action-type filters.
- Add run_id / artifact-linked context in detail view.
- Make it obvious whether an item belongs to:
  - content
  - Flow Lab
  - system
  - external action
- Add empty-state explanations for each tab.

### 1.5 CEO decision package quality
- Ensure all high-value approvals render a standardized CEO package.
- Standardize package structure:
  - summary
  - why it matters
  - evidence
  - attached artifacts
  - risk
  - recommended action
  - reversible / irreversible
- Use the same package style across:
  - content pipeline
  - Flow Lab screenshot/video
  - external publishing
  - future trading research

---

## 2. Convergence

### 2.1 Workflow runtime convergence
- Move more business flows onto the graph/runtime path.
- Reduce logic duplication between:
  - legacy pipeline routes
  - dynamic orchestrator
  - graph workflow
- Prefer one orchestrated path per workflow family.

### 2.2 Domain convergence
- Continue migration into:
  - `src/domains/flow_lab/`
  - `src/domains/media/`
  - `src/domains/trading/`
- Keep shims temporary.
- Track which modules are:
  - fully migrated
  - shimmed
  - legacy-only
- Remove stale shim layers after migration stabilizes.

### 2.3 Adapter convergence
- Ensure all external integrations use AdapterBase consistently.
- Validate maturity per adapter:
  - `x_publish`
  - `line_notify`
  - `figma_api`
  - `chrome_cdp`
  - `video_frame_extractor`
- Clearly classify:
  - active and production-usable
  - active but guarded
  - planned
  - experimental

### 2.4 Content engine convergence
- Ensure all content paths use the same:
  - scoring rules
  - GEO/SEO rules
  - similarity checks
  - approval thresholds
- Avoid having one path use GEO strongly while another bypasses it.

### 2.5 Dashboard convergence
- Normalize page-level fetch behavior.
- Standardize error handling and loading states.
- Avoid page-specific bespoke fetch patterns where common helpers should exist.

---

## 3. Semantic Unification

### 3.1 Naming
- Standardize naming for:
  - API origin env vars
  - approval actions
  - review statuses
  - artifact types
  - workflow status labels
  - video/screenshot analysis statuses

### 3.2 Approval-related terms
- Decide exact meanings of:
  - pending
  - approved
  - rejected
  - deferred
  - awaiting_human
  - paused
- Make sure backend, tests, UI, and docs all use them the same way.

### 3.3 Skill terminology
- Standardize:
  - runtime-used
  - workflow-used
  - reference-only
  - planned
- Keep skill governance matrix aligned with runtime reality.

### 3.4 Artifact taxonomy
- Keep artifact types explicit and finite.
- Avoid ad hoc string drift.
- Review artifact coverage for:
  - draft
  - weekly_report
  - screenshot_extraction
  - video_analysis
  - selection_report
  - future research artifacts

### 3.5 Domain language
- Flow Lab terminology should consistently mean:
  - systemized product selection
  - decision model
  - analysis artifacts
- Media terminology should consistently mean:
  - topic research
  - persona fit
  - content strategy
  - GEO-aware draft generation

---

## 4. Technical Debt Cleanup

### 4.1 Mojibake and text corruption
- Clean runtime/UI comments and strings that still contain garbled text.
- Prioritize:
  - dashboard pages
  - adapter descriptions
  - config comments
  - review labels
- Keep Chinese or English, but make them valid and readable.

### 4.2 Frontend consistency
- Remove duplicated direct fetch logic where helpers already exist.
- Standardize:
  - error handling
  - retry behavior
  - fallback defaults
  - `cache: "no-store"` usage

### 4.3 Runtime health
- Add a stable backend health check for local/dev usage.
- Make dashboard degrade gracefully when backend is unavailable.
- Investigate and harden against:
  - `ECONNRESET`
  - `socket hang up`
  - localhost timeout behavior

### 4.4 DB hygiene
- Review indexes and cleanup paths for:
  - `review_items`
  - `approval_requests`
  - workflow tables
  - Flow Lab video/screenshot tables
- Add retention/cleanup strategy for:
  - rejected items
  - stale deferred items
  - old artifacts if desired

### 4.5 Test hygiene
- Keep regression tests for every semantics change.
- Add tests for:
  - approval dedup logic
  - cleanup endpoints
  - mixed dashboard fetch patterns
  - runtime fallback behavior
- Continue keeping build and full-suite green after each change batch.

---

## 5. Skills And GEO/SEO Optimization

### 5.1 Runtime skill adoption
- Ensure the most important skills are enforced where they matter most:
  - `content_creation`
  - `marketing_strategy`
  - `seo_optimization`
  - `research_analysis`
  - `geo_optimization_engine`
- Audit where skills are:
  - loaded automatically
  - implied by workflow only
  - merely documented

### 5.2 GEO/SEO hardening
- Convert GEO/SEO from “guidance” to “reviewable enforcement”.
- Define checklist for:
  - entity clarity
  - question-answer structure
  - authority signals
  - explicit viewpoint
  - answer-engine readability
  - topic purity
- Integrate this into:
  - Craft generation
  - Orio scoring
  - Sage review

### 5.3 Skill routing maturity
- Keep `task_type -> skill route` mapping current.
- Add review when:
  - task routes drift from actual runtime usage
  - new skills are added without routing metadata

### 5.4 Skill governance
- Apply the governance spec consistently:
  - task classification
  - pattern selection
  - supporting patterns
  - failure conditions
  - output contracts

---

## 6. External Integrations

### 6.1 X
- Validate full flow:
  - approval
  - dry run
  - publish
  - failure handling
- Add end-to-end mocked tests for final publish path.

### 6.2 LINE
- Complete business workflows:
  - competitor price tracking alerts
  - price-drop notifications
  - weekly/report notifications
- Keep adapter and helper behavior aligned.

### 6.3 Browser/CDP
- Keep deferred until:
  - session isolation is defined
  - approval policy is explicit
  - read-only vs write action behavior is fully governed

### 6.4 Video
- Complete M2:
  - frame extraction
  - optional transcript enrichment
  - stronger artifact output
- Keep M1 stable while M2 is blocked.

### 6.5 Figma
- Confirm actual token-driven integration path
- document read-only limits
- add integration tests if missing

---

## 7. Flow Lab Optimization

### 7.1 Screenshot and video workflow polish
- Keep screenshot-first and video-first flows aligned.
- Make approval questions and resulting artifacts consistent.

### 7.2 Candidate decision flow
- Ensure purchase-related approvals are visible in the right queue.
- Avoid mixing product selection actions with generic content review semantics.

### 7.3 Future 1688/Taobao path
- keep screenshot workflow as stable phase 1
- do not mix future URL ingestion into current stable path prematurely

---

## 8. Media Optimization

### 8.1 Threads workflow
- Ensure topic selection, format selection, first-reply planning, and GEO structure all align.
- Make sure every content workflow goes through:
  - topic fit
  - persona fit
  - source trust
  - draft generation
  - review/approval as needed

### 8.2 Operator visibility
- Keep Office timeline useful.
- Make sure the CEO can see:
  - what was researched
  - what was drafted
  - what is waiting
  - why something needs review

---

## 9. Documentation Optimization

### 9.1 Spec consolidation
- Keep the spec index current.
- Mark superseded docs clearly.
- Archive old planning docs aggressively.

### 9.2 Active-vs-historical separation
- Separate:
  - active architecture docs
  - completed audits
  - archived plans
  - external reference notes

### 9.3 Make operational docs shorter
- Keep one master roadmap
- one master index
- one master optimization checklist
- avoid spreading “current truth” across too many overlapping files

---

## 10. File And Folder Cleanup

### 10.1 Keep
- `src/`
- `dashboard/`
- `tests/`
- `projects/anticlaude/` for current active specs and audits

### 10.2 Archive
- older superseded planning docs
- one-off resolved planning files
- duplicate historical notes

### 10.3 Reduce ambiguity
- avoid leaving both “old path” and “new path” active longer than necessary
- remove temporary compatibility shims once migrations settle

---

## 11. Operational Readiness

### 11.1 Live runtime verification
- Standardize a check sequence for local/dev:
  - backend up
  - dashboard up
  - health endpoint up
  - key APIs responsive

### 11.2 Logging
- Ensure major failures leave human-readable logs.
- Especially for:
  - proxy/reset issues
  - approval sync
  - adapter failures
  - video pipeline deferrals

### 11.3 Safe failure modes
- non-critical dashboard widgets should fail soft
- high-risk writes should fail closed

---

## 12. Recommended Execution Order

### Phase A: semantic cleanup first
1. approval model clarity
2. review dedup refinement
3. API base/env unification
4. review/approval UI semantics

### Phase B: debt cleanup
5. mojibake cleanup
6. runtime health hardening
7. DB cleanup and retention rules

### Phase C: skill and workflow refinement
8. GEO/SEO enforcement path
9. skill routing and governance tightening
10. workflow convergence across media/flow lab

### Phase D: external and advanced capabilities
11. LINE business alerts
12. X end-to-end publish path validation
13. video M2
14. browser/CDP only after governance is ready

---

## 13. Definition Of “Best”

The system can be considered “best / optimized” only when all of these are true:

- no ambiguous approval surfaces
- no hidden pending work due to coarse dedup
- no mixed API-origin conventions
- no unreadable user-facing mojibake
- skills are clearly routed and enforced
- docs clearly distinguish current truth from historical notes
- dashboard runtime is operationally trustworthy
- tests and build remain green after each cleanup phase

---

## 14. Practical Conclusion

The project is already strong, but not yet fully optimized.

The remaining work is not about inventing a new architecture.
It is about finishing the hard part:

- refine
- converge
- unify semantics
- pay down technical debt

This checklist is the full working agenda for turning the current codebase into a best-in-class, operator-trustworthy AITOS implementation.
