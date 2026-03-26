# Current Gap, Optimization, and Cleanup Review 2026-03-20

## 1. Current State Snapshot

Validated current state:

- backend tests: `172 passed, 1 warning`
- dashboard production build: passed
- graph workflow runtime: landed
- Flow Lab screenshot workflow: landed
- CEO approval center: landed
- approval bridge: landed
- initial domain migration: started

Practical completion estimate:

- core architecture / workflow backbone: `~85%`
- high-risk capability completion: `~60-70%`

---

## 2. What Is Still Missing

## 2.1 Core Remaining Gaps

These are the real remaining gaps that still matter.

### A. Approval Model Is Bridged, Not Fully Unified

Current state:

- `approval_requests` exists
- `review_items` exists
- bridge logic now exists between them

Still missing:

- a final canonical approval model
- clear rule for when each table is authoritative
- potential cleanup/migration plan if one eventually becomes only a view or inbox layer

Why it matters:

- prevents model confusion
- improves CEO inbox clarity
- simplifies future workflow routing

### B. Domain Migration Is Started, Not Finished

Current state:

- `src/domains/media/`
- `src/domains/flow_lab/`
- `src/domains/trading/`
- at least one migration step has started

Still missing:

- real business logic relocation from legacy flat modules
- stable domain ownership boundaries
- reduced duplication between legacy paths and new domain paths

Why it matters:

- this is the real DDD finish line
- current codebase still has old and new structures coexisting

### C. Video Ingestion Is Still Spec-First

Current state:

- `VideoInsightArtifact` exists
- spec exists
- adapter stub exists
- tests/spec-level scaffolding exists

Still missing:

- real frame extraction
- real transcription
- real upload-to-analysis path
- real review UI flow for video artifacts

Why it matters:

- multimodal capability is still incomplete in practice

### D. Browser / CDP Control Is Still Not Implemented

Current state:

- planned in adapter registry
- no production-grade implementation

Still missing:

- isolated session control
- approval boundaries
- safe supervised browser execution model

Why it matters:

- this is the highest-risk future integration area

### E. Mojibake / Garbled Text Debt Still Exists

Current state:

- encoding handling improved
- UTF-8 runtime mitigation improved

Still missing:

- cleanup of garbled comments and user-facing strings across runtime files

Why it matters:

- hurts maintainability
- hurts UI clarity
- creates false confidence because runtime still passes while text quality is degraded

---

## 3. What Could Be Better Even If Not Strictly Broken

## 3.1 Make Active Skill Usage Transparent

Current state:

- core composite skills are injected at runtime
- operational skills are partly workflow/SOP level

Improvement:

- expose active skill set per workflow/task in Office UI
- make Lara’s skill routing auditable

Benefit:

- better governance
- less confusion about whether a skill is truly active

## 3.2 Add Task-Type to Skill Mapping as a First-Class Contract

Current state:

- some mapping exists implicitly
- governance docs now exist

Improvement:

- create formal `task_type -> required skills -> optional skills -> mandatory reviewer?`

Benefit:

- better routing consistency
- easier future automation for Lara

## 3.3 Promote CEO Package to a System-Wide Standard

Current state:

- CEO package exists for approvals

Improvement:

- use the same package structure across:
  - content approvals
  - Flow Lab approvals
  - future multimodal decisions
  - future trading research approvals

Benefit:

- consistent executive experience
- cleaner human-in-the-loop design

## 3.4 Reduce Legacy Parallel Paths

Current state:

- graph runtime exists
- older orchestration flows still exist

Improvement:

- gradually converge more flows onto one canonical workflow runtime

Benefit:

- fewer duplicated behaviors
- fewer hidden inconsistencies

---

## 4. Recommended Next Planning / Optimization Priorities

Best next priorities:

1. finalize approval model ownership
2. continue domain migration deliberately
3. complete video ingestion implementation
4. keep browser control deferred until safety model is ready
5. run a controlled mojibake cleanup pass
6. define machine-readable task-to-skill routing
7. standardize CEO package across all decision surfaces

---

## 5. File Cleanup Analysis

This section focuses mainly on `projects/anticlaude/`, because that is where planning/spec sprawl exists.

Important principle:

- do not delete useful architecture memory casually
- prefer:
  - `keep`
  - `archive`
  - `consolidate`
  - `delete candidate`

---

## 6. Keep

These are still high-value current references and should stay.

### Core Current References

- `README_spec_index_20260318.md`
- `aitos_open_gaps_and_todo_20260320.md`
- `aitos_implementation_status_audit_20260319.md`
- `aitos_progress_recheck_20260319.md`
- `aitos_master_spec_index_and_operating_sop_20260318.md`
- `aitos_next_steps_roadmap_20260318.md`
- `skill_adoption_matrix_20260320.md`
- `skill_design_governance_fit_review_20260320.md`
- `skills_and_external_refs_usage_summary_20260320.md`
- `coincat_planning_and_isolation_strategy_20260320.md`

### Still Relevant Strategic References

- `aitos_recommended_optimization_master_plan_20260317.md`
- `aitos_token_memory_skill_integration_consolidation_20260319.md`
- `multimodal_deliberation_and_scoring_spec_20260319.md`
- `spec_video_ingestion.md`
- `flow_lab_brand_strategy_20260318.md`
- `cross_platform_scraping_guidelines_20260318.md`

---

## 7. Archive Candidates

These still have historical value, but they are no longer ideal as primary working docs.

Recommended action:

- move later into something like `projects/anticlaude/archive/`
- do not delete immediately

### Early-Phase Plans That Have Been Superseded

- `plan_20260314_optimization_roadmap.md`
- `plan_20260314_agent_wiring.md`
- `plan_20260314_framework_migration.md`
- `plan_20260314_p1p2_and_tests.md`
- `plan_20260314_phase3_roadmap.md`
- `plan_20260315_bugfix_office_and_inventory.md`
- `plan_20260315_tech_debt_cleanup.md`
- `plan_20260315_office_light_theme.md`
- `plan_20260315_master_roadmap.md`
- `plan_20260315_future_roadmap.md`
- `plan_20260315_system_audit.md`
- `plan_20260317_langgraph_geo_aitos_v2.md`

### Older Review Docs That Are Mostly Absorbed Elsewhere

- `ai_office_review_2026-03-14.md`
- `ai_office_recommendations.md`
- `ai_office_execution_plan.md`
- `architecture_load_audit_2026-03-14.md`
- `ai_office_remaining_work.md`

These are not worthless, but they are likely no longer top-level docs.

---

## 8. Consolidation Candidates

These are useful, but some could be merged into fewer master docs over time.

### Possible Consolidation Groups

#### A. Architecture / Strategy Group

- `aitos_v3_optimization_reference_20260317.md`
- `aitos_v31_flowlab_architecture_consolidation_20260318.md`
- `aitos_recommended_optimization_master_plan_20260317.md`
- `system_architecture_health_review_20260317.md`

Potential future result:

- one master architecture + execution priorities doc

#### B. Skills / Governance Group

- `skills_and_memory_audit_20260318.md`
- `skills_and_external_refs_usage_summary_20260320.md`
- `skill_design_governance_fit_review_20260320.md`
- `skill_adoption_matrix_20260320.md`

Potential future result:

- one `AITOS Skill Governance Handbook`

#### C. Workflow / Runtime Group

- `aitos_token_memory_skill_integration_consolidation_20260319.md`
- `multimodal_deliberation_and_scoring_spec_20260319.md`
- `spec_video_ingestion.md`
- `aitos_open_gaps_and_todo_20260320.md`

Potential future result:

- one `AITOS Workflow Runtime Handbook`

---

## 9. Delete Candidates

These should be reviewed carefully before deletion, but they are the best candidates.

### Strong Delete Candidate

- `ecommerce_product_selection_system_plan.cd`

Reason:

- unusual extension
- likely duplicate / intermediate artifact
- lower confidence as a canonical planning doc

### Possible Delete Candidates After Archival Review

- very small early-context files that are now clearly superseded:
  - `project_context.md`
  - `ai_office_handoff_memory.md`

Only delete if:

- their contents are fully preserved elsewhere
- no current doc links to them

Otherwise archive instead of deleting.

---

## 10. Recommended Cleanup Strategy

Best cleanup order:

1. create `projects/anticlaude/archive/`
2. move old `plan_20260314*` and `plan_20260315*` files into archive
3. keep all 2026-03-17 onward master/spec/governance docs at top level
4. review `ecommerce_product_selection_system_plan.cd`
5. only after review, delete obvious duplicates or malformed artifacts

---

## 11. Bottom Line

The system is in a strong state now.

What remains is no longer "build the foundation".
What remains is:

- unifying models
- finishing migrations
- implementing high-risk planned features carefully
- cleaning documentation and encoding debt

The codebase itself is already meaningfully operational.
The next level of improvement is mostly about:

- governance
- consistency
- cleanup
- finishing the last high-risk capability gaps
