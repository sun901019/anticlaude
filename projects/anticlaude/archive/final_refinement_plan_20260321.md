# Final Refinement Plan

Date: 2026-03-21
Purpose: define the final refinement phase required to move the current AITOS codebase from "strong and usable" to "clean, trustworthy, and fully optimized".

## 1. Current State Summary

The system is already in a strong state.

Verified baseline:
- backend tests are passing
- frontend production build is passing
- workflow runtime exists
- approval flow exists
- Flow Lab screenshot workflow exists
- review/office/reports UI exists
- adapter layer exists
- domain migration has started materially

This means the project is no longer missing its core architecture.
The remaining work is refinement and convergence.

## 2. Final Goal

The target is not a new architecture.
The target is a cleaner final version of the current one.

Definition of "done enough to feel complete":
- one clear approval model
- one trustworthy CEO inbox
- one clear backend-origin strategy in frontend
- readable runtime and UI text
- fewer transitional shims and duplicated semantics
- external integrations clearly classified by maturity
- Figma, video, and browser capabilities clearly marked as implemented vs partial vs deferred
- docs reduced to one current truth instead of many overlapping truths

## 3. Remaining Gaps

## 3.1 Approval semantics still need final unification

Current issue:
- `approval_requests` and `review_items` both exist
- bridging exists, but semantics are still not completely clean

Target:
- clearly define whether `review_items` is:
  - a curated CEO inbox
  - or a full mirror of all approval requests

Recommended decision:
- keep `approval_requests` as the source of truth
- keep `review_items` as a curated operator-facing inbox
- make that separation explicit in code, UI, and docs

## 3.2 Review dedup logic still needs refinement

Current issue:
- dedup/capping behavior is still action-based
- this can reduce spam, but it can also hide real distinct pending items

Target:
- dedup by a safer key:
  - `approval_id`
  - or `run_id + action`
  - or evidence fingerprint

## 3.3 Frontend API origin handling is still mixed

Current issue:
- `NEXT_PUBLIC_API_BASE`
- `NEXT_PUBLIC_API_URL`
- proxy-relative `/api`
- direct backend access

Target:
- standardize one env var
- standardize one API helper strategy
- document when direct backend access is allowed

## 3.4 Mojibake cleanup is not complete

Current issue:
- many corrupted comments/labels/descriptions remain readable enough to run, but not clean enough to maintain

Target:
- clean user-facing labels first
- then adapter descriptions
- then comments in runtime files

## 3.5 Domain migration is still transitional

Current issue:
- media and flow_lab moved significantly
- shims still remain
- trading is still skeletal

Target:
- reduce transitional ambiguity
- keep only intentional compatibility shims
- document what is still legacy and why

## 3.6 GEO/SEO is present but not universally enforced

Current issue:
- some flows use GEO/SEO strongly
- some rely on skill docs and conventions rather than consistent review enforcement

Target:
- make GEO/SEO reviewable and testable
- especially in:
  - topic selection
  - draft generation
  - final review

## 3.7 Figma is connected but not productized

Current issue:
- backend client and adapter exist
- system can read Figma
- there is not yet a full design-to-frontend operator workflow

Target:
- define if Figma is:
  - just a backend integration
  - or a true frontend generation capability

If yes, build:
- token extraction layer
- node selection workflow
- artifact output
- approval step

## 3.8 Video is only M1

Current issue:
- upload path exists
- approval path exists
- extraction/analysis depth is still limited

Target:
- either complete M2
- or clearly mark M2 as deferred until ffmpeg/cloud prerequisites are ready

## 3.9 Browser/CDP remains intentionally guarded

Current issue:
- capability exists
- productization and safety rules are intentionally incomplete

Target:
- do not rush this
- keep deferred unless:
  - session isolation
  - approval semantics
  - safe operator UX
  are all defined

## 3.10 LINE business alerts are not fully closed

Current issue:
- basic notify exists
- business workflows are still incomplete

Target:
- clarify whether LINE is:
  - just a notification channel
  - or a real operational alert system

If operational:
- complete price-drop and competitor-alert flows

## 4. Recommended Execution Order

## Phase A: semantic cleanup

1. Finalize approval model contract
2. Refine review dedup logic
3. Unify frontend API-origin handling

Reason:
- these are trust-layer issues
- they affect operator clarity across the whole system

## Phase B: readability and maintainability

4. Clean mojibake in runtime/UI text
5. Clean comments and adapter descriptions
6. Update docs to reflect current truth only

Reason:
- easier maintenance
- lower confusion
- better operator confidence

## Phase C: architecture convergence

7. Continue domain migration cleanup
8. reduce or document remaining shims
9. review workflow convergence across content / Flow Lab / review surfaces

Reason:
- this finishes the structural cleanup already in progress

## Phase D: enforcement and maturity

10. Turn GEO/SEO rules into stronger review/routing enforcement
11. validate X and LINE end-to-end operational paths
12. clarify which adapters are:
   - production-ready
   - guarded
   - partial
   - deferred

Reason:
- makes the system more trustworthy in real use

## Phase E: optional advanced productization

13. productize Figma workflow if design-to-code matters now
14. advance Video M2 if prerequisites are available
15. keep Browser/CDP deferred until governance is ready

Reason:
- these are useful, but should not be allowed to destabilize the now-strong core

## 5. Recommended Deliverables

The final refinement phase should aim to produce:

- one approval semantics document
- one API-origin convention
- one mojibake cleanup pass
- one domain migration status snapshot
- one adapter maturity matrix
- one GEO/SEO enforcement checklist
- one docs consolidation pass

## 6. What Can Wait

These should not block the main refinement phase:

- CoinCat implementation
- full trading domain productization
- aggressive Browser/CDP automation
- 1688/Taobao URL adapter phase
- any major stack rewrite

## 7. Practical Conclusion

The project does not need reinvention.
It needs finishing discipline.

The core architecture is already there.
The final phase is about:
- sharpening semantics
- removing ambiguity
- cleaning operational surfaces
- deciding which partial integrations should become fully productized

If this plan is executed well, the result will feel less like a fast-moving prototype and more like a durable operating system.
