# Skill Design Governance Fit Review 2026-03-20

## 1. Short Answer

Yes.
This specification is worth adopting.

But it should be adopted as:

- a `governance layer`
- a `skill design standard`
- a `selection and execution policy`

It should **not** be treated as a direct replacement for all current skills.

In other words:

- it is good for governing how skills are designed and used
- it is not a drop-in replacement for existing task-specific skills

---

## 2. Why It Fits AITOS Well

Your current system has already grown into multiple layers:

- runtime-injected composite skills
- workflow SOP skills
- planning/spec documents
- approval and graph workflow logic

What is still missing is a unified rule for:

- how to classify a task
- when to load which skill
- when review is mandatory
- how multiple patterns should be combined

This governance spec directly addresses that gap.

It is especially compatible with AITOS because AITOS already depends on:

- skill selection
- workflow branching
- approval gates
- delayed loading of domain knowledge
- high-risk output review

So this document is aligned with the direction of the system.

---

## 3. Best Way to Position It

This spec should sit above current individual skills.

Recommended role:

- `meta-skill policy`
- `skill architecture standard`
- `task-to-pattern routing guide`

That means:

- existing skills like `write-threads-post.md` do not disappear
- instead, they should later be classified under this governance model

Example:

- `write-threads-post.md`
  - Primary Pattern: `Generator`
  - Supporting Pattern: `Tool Wrapper`
- `select-topic.md`
  - Primary Pattern: `Reviewer`
  - Supporting Pattern: `Tool Wrapper`
- `workflow-daily-content.md`
  - Primary Pattern: `Pipeline`
  - Supporting Pattern: `Reviewer`

---

## 4. What It Improves Immediately

If adopted, this spec would improve four weak spots in the current repo.

### 4.1 Skill Selection Consistency

Right now, some skills are:

- runtime-used
- workflow-used
- reference-only

but there is no single formal rule describing why.

This governance spec fixes that by forcing:

- task classification first
- pattern selection second
- knowledge loading last

### 4.2 Context Discipline

This spec strongly reinforces one of your best architecture decisions:

- do not preload everything
- load knowledge only when needed

That matches your:

- cache-first direction
- memory-fabric direction
- token-cost discipline

### 4.3 Better Skill Composition

Your system is already implicitly combining patterns.

Examples:

- content workflow = pipeline + generator + reviewer
- market analysis = tool wrapper + reviewer
- approval workflows = pipeline + reviewer

This spec gives that combination an explicit vocabulary:

- primary pattern
- supporting patterns

That is useful for both humans and agents.

### 4.4 Safer High-Risk Output

The requirement that high-risk tasks must go through review/checkpoint is a good fit for:

- code generation
- strategy design
- business recommendations
- multi-step workflow output

This is already culturally consistent with AITOS.

---

## 5. What Should Not Be Done

Do **not** apply this spec by rewriting everything immediately.

Bad rollout:

- rewrite all existing skills into a new format at once
- force every request through all five pattern checks
- inject governance text into every runtime prompt

That would create overhead and context bloat.

Instead, this spec should first be adopted as:

- a design reference for future skills
- a migration standard for important existing skills
- a routing guide for Lara / orchestrator logic

---

## 6. Recommended Adoption Model

## Phase A: Governance Only

Use this spec as:

- design guidance
- review checklist for new skills
- classification framework

No broad runtime changes yet.

## Phase B: Skill Inventory Mapping

Map existing skills into the governance structure:

- task type
- primary pattern
- supporting patterns
- references
- assets
- output contract
- failure conditions

This should produce a `skill adoption matrix`.

## Phase C: Orchestrator Awareness

Later, let Lara / orchestration logic use this structure to decide:

- which skill to load
- whether review is mandatory
- whether inversion is needed before generation

## Phase D: Runtime Enforcement for High-Risk Flows

Only after the model is stable:

- enforce pattern rules in high-risk workflows
- especially:
  - content generation
  - business recommendation
  - code generation
  - approval-gated workflows

---

## 7. Best Fit Inside AITOS

Recommended placement conceptually:

- `governance`
- `skill policy`
- `meta-skill standard`

Good future file candidates:

- `projects/anticlaude/skill_design_governance_spec.md`
- or later: `ai/governance/skill-pattern-policy.md`

For now, it fits best as a planning and governance reference, not a runtime prompt file.

---

## 8. How It Relates to Existing AITOS Patterns

This governance spec maps cleanly onto current AITOS behavior.

### Current AITOS Equivalent Concepts

- `Tool Wrapper`
  - composite skills
  - adapter-bound domain/tool logic

- `Generator`
  - writing and report generation
  - structured drafting

- `Reviewer`
  - scoring
  - approval packaging
  - quality checking

- `Inversion`
  - still relatively weak in current repo
  - should be strengthened for unclear/high-risk requests

- `Pipeline`
  - already strongly aligned with graph workflow direction

So the spec is not alien to the current system.
It mostly formalizes what AITOS is already becoming.

---

## 9. Best Practical Use for Your System

The best practical value is:

### For Lara

- classify tasks before delegating
- decide whether inversion is needed
- decide whether review is mandatory
- decide whether to use pipeline or direct generation

### For Skill Authors

- ensure each skill has:
  - trigger conditions
  - output contract
  - failure conditions
  - pattern identity

### For Future Runtime

- support explicit task -> pattern -> skill routing
- avoid loading irrelevant knowledge
- reduce skill ambiguity

---

## 10. Recommendation

My recommendation is:

`Adopt this specification, but adopt it as a governance layer first, not as a full runtime rewrite.`

That is the correct level for it right now.

---

## 11. Suggested Next Step

The best next follow-up would be:

1. create a `Skill Adoption Matrix`
2. classify existing major skills by:
   - task type
   - primary pattern
   - supporting patterns
   - runtime-used / workflow-used / reference-only
3. identify which high-risk flows must always include `Reviewer`
4. identify where `Inversion` is currently missing

That would turn this governance spec from a good idea into an actionable system standard.
