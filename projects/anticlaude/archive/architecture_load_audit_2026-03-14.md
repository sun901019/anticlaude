# AntiClaude Architecture Load Audit

Date: 2026-03-14
Scope: `Anticlaude` project architecture docs, role design, skills placement, import/load positions, and execution alignment

## Executive Judgment

Current status is **directionally correct but not yet guaranteed-correct at runtime**.

That means:

- Your folders and concepts are mostly placed in the right areas.
- Your project already shows a clear split between runtime code, project docs, and capability libraries.
- But the system still lacks a strict enough **source-of-truth contract** to guarantee that "the right task always loads the right role/skill/context" every time.

So the honest answer is:

- `Yes`: the structure is already meaningful and professional enough to keep scaling.
- `No`: it is not yet strong enough to assume all agents, docs, and skills will always load correctly without drift.

---

## What Is Already Good

### 1. Top-level separation is mostly correct

Your current layout already has the right intent:

- `src/`
  - executable backend logic
- `dashboard/`
  - executable frontend logic
- `projects/anticlaude/`
  - project-specific rules, specs, operational docs
- `_hub/`
  - reusable capability library, agents, shared skills, registries
- `_context/`
  - broader contextual memory/reference material
- `data/`, `outputs/`, `uploads/`
  - storage/output/runtime artifacts

This is a strong foundation. It shows you are not mixing runtime code with loose prompt notes.

### 2. Role thinking and system thinking already exist

Your project does not treat agents as random labels. It already assumes:

- roles
- skills
- workflows
- handoff
- outputs
- memory

That is important because it means the system can evolve into a real operating model, not just a UI theme.

### 3. Existing ecommerce structure is already extendable

For Flow Lab / ecommerce, you already have:

- runtime backend routes in `src/ecommerce/router.py`
- frontend page in `dashboard/src/app/ecommerce/page.tsx`
- earlier concept spec in `_hub/ecommerce_engine_spec.md`

So the ecommerce product-selection system should be treated as an **extension of the current system**, not a separate rebuild.

---

## Where It Is Still Weak

### 1. Source of truth is split across too many layers

Right now, meaning is distributed across:

- `_hub/registry/...`
- `_hub/shared/agents/...`
- `projects/anticlaude/...`
- `src/...`
- `dashboard/...`

This is not automatically wrong. The issue is that not all five layers currently play different roles with strict enough boundaries.

Result:

- one concept may exist in docs but not in code
- one role may exist in `_hub` but not be wired into project runtime
- one project doc may say something newer than code implements
- an AI coding agent may read the wrong layer first and assume that is the current truth

### 2. Role loading and skill loading are still implied, not enforced

At the moment, the system feels like:

- "roles exist"
- "skills exist"
- "documents describe them"

But it is still weaker on:

- exact load trigger
- exact task-to-role routing rule
- exact role-to-skill resolution
- exact fallback behavior when multiple sources conflict

Without these, the system can look organized while still behaving inconsistently.

### 3. Project docs and implementation can drift

This is the most likely long-term failure mode.

Typical drift patterns:

- `projects/anticlaude/*.md` says a workflow exists, but `src/` does not emit those events
- `_hub/` contains a richer role definition than runtime actually uses
- frontend reflects aspirational states while backend still uses older payloads
- Claude Code or another agent updates code without updating the project-level operational spec

### 4. Runtime truth is not yet explicit enough

The system needs a stronger answer to this question:

> When a task arrives, exactly which file decides which role, which skill, which schema, which output format, and which handoff path will be used?

Until that answer is explicit, "correct placement" is only partial.

---

## Recommended Truth Model

To make the system load correctly and predictably, define these layers clearly:

### Layer 1. Capability Truth

Location:

- `_hub/registry/`
- `_hub/shared/agents/`
- `_hub/shared/skills/`

Purpose:

- describe what is available in the wider AI-OS
- define reusable capabilities
- define persona/skill libraries

Rule:

- `_hub/` is the **library of possible capabilities**
- `_hub/` is **not automatically the active runtime truth for this project**

### Layer 2. Project Operational Truth

Location:

- `projects/anticlaude/`

Purpose:

- define what this project currently uses
- define active workflows
- define active role responsibilities
- define which capabilities from `_hub/` are adopted here

Rule:

- if `_hub/` and project docs disagree, `projects/anticlaude/` wins for this project

### Layer 3. Executable Truth

Location:

- `src/`
- `dashboard/`

Purpose:

- actual runtime behavior
- API contracts
- UI rendering
- persistence

Rule:

- code must implement project truth
- if code differs from project truth, that is a defect and should be logged

### Layer 4. Runtime Artifact Truth

Location:

- `data/`
- `outputs/`

Purpose:

- actual evidence of system behavior
- reports, event logs, decisions, histories, summaries

Rule:

- runtime artifacts do not define policy
- they prove whether policy is actually being followed

---

## What To Add So Loading Becomes Reliable

### 1. Add a project-level routing map

Recommended new doc:

- `projects/anticlaude/project_routing_map.md`

This file should explicitly answer:

- task type -> owner role
- owner role -> required skills
- input source -> schema
- output artifact -> storage location
- completion event -> next handoff

Example:

- `content_research` -> `ori`
- `topic_strategy` -> `lala`
- `draft_generation` -> `craft`
- `ui_or_system_implementation` -> `lumi`
- `analysis_or_review` -> `sage`

This removes ambiguity for Claude Code, Codex, and future agents.

### 2. Add an active-capability manifest

Recommended new doc:

- `projects/anticlaude/active_capabilities_manifest.md`

It should list:

- active agents used by this project
- active skills used by this project
- inactive/parked capabilities
- source doc for each capability
- runtime integration status

That lets you distinguish:

- available in library
- adopted in project
- actually wired in code

### 3. Add doc-to-code sync requirement

Every major system area should have:

- project spec
- API contract
- runtime implementation
- acceptance checklist

Minimum policy:

- if runtime changes API/schema/role behavior, project docs must be updated in the same work cycle

### 4. Add conflict resolution rule

When multiple docs mention the same role/process, define precedence:

1. `projects/anticlaude/` operational docs
2. executable contracts in `src/` and `dashboard/`
3. `_hub/registry/`
4. `_hub/shared/...`
5. `_context/`

This will prevent agents from loading older or more generic instructions by mistake.

---

## Assessment of Current Roles and Skills Placement

## Role placement

Current judgment: **good conceptual placement, partial runtime binding**

Strong points:

- role definitions and personas are separated from runtime code
- project docs already treat agents as organizational actors
- AI Office direction reinforces operational visibility

Weak points:

- not every role appears to have a fully defined runtime trigger
- not every role has a clean input/output contract
- some roles are still stronger as concept/persona than as executable operator

What to improve:

- define a strict contract for each active role:
  - trigger
  - input
  - expected output
  - handoff target
  - memory writeback

## Skills placement

Current judgment: **library is rich, project adoption is still under-specified**

Strong points:

- `_hub` is appropriately used as a capability library
- there is enough material to support specialization

Weak points:

- "available skill" and "active skill for this project" are not the same thing
- there is not yet a small enough project-specific skill shortlist

What to improve:

- maintain a project-level approved skill list
- tag each active workflow with its required skills
- mark optional vs required skills

---

## Assessment of Import / Load Positions

Current judgment: **folder placement is mostly right, loading logic is not yet explicit enough**

The problem is not mainly where files sit.

The problem is whether the system has an unambiguous answer for:

- where task routing starts
- where role resolution starts
- where workflow truth starts
- where fallback is decided

Recommendation:

- keep the current folder structure
- improve the explicit load map instead of reorganizing folders again

In other words:

- do not spend energy on another large directory reshuffle
- spend energy on stronger mapping and runtime contracts

---

## Professional Upgrade Recommendations

### Recommendation A. Turn project docs into a real operating layer

`projects/anticlaude/` should become:

- the active playbook
- the accepted truth for this project
- the first place coding agents consult for current operational rules

That means this folder should contain:

- vision docs
- workflow docs
- active role manifest
- schema references
- routing map
- execution plans
- reviews

### Recommendation B. Separate persona from execution role

You currently have both:

- human-facing brand personas
- technical execution roles

That is good, but they should be mapped explicitly.

Example:

- `Ori` -> research operator
- `Lala` -> strategy operator
- `Craft` -> content production operator
- `Lumi` -> implementation operator
- `Pixel` -> presentation/design operator
- `Sage` -> analysis/review operator

This should live in a dedicated mapping file.

### Recommendation C. Make every important workflow schema-first

Before more UI or more automation, define schemas for:

- task
- handoff
- event
- artifact
- memory summary
- report

When schemas are stable, both humans and coding agents stop guessing.

### Recommendation D. Track integration status for each system area

For each major domain, keep an integration table:

- specified
- partially implemented
- fully implemented
- verified

Suggested domains:

- content pipeline
- AI Office
- ecommerce
- feedback
- weekly reports
- tracker

---

## Final Answer

Your current architecture, docs, role design, skill placement, and import positions are **good enough to scale**, but **not yet rigorous enough to guarantee correct loading every time**.

The real gap is not folder placement. It is:

- source-of-truth discipline
- routing clarity
- role-to-skill contract clarity
- doc-to-code synchronization

So the upgrade path is:

1. Keep the existing structure
2. Strengthen project operational truth in `projects/anticlaude/`
3. Add a routing map and active capability manifest
4. Make workflows schema-first
5. Treat code mismatch vs docs as a defect, not as normal drift

If you do that, your system will stop being "well-organized on paper" and become "predictably loadable in practice".
