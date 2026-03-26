# AITOS v3.1 Flow Lab + Master Architecture Consolidation 2026-03-18

## 1. Executive Summary

Yes, I clearly understand the three core decisions in your v3.1 blueprint:

1. `DDD domain isolation`
2. `File + DB memory fabric`
3. `Keep Python FastAPI as the control plane`

My judgment is:
- this blueprint is stronger than a generic multi-agent system draft
- it is also compatible with the current repo direction
- but the current codebase is only partially aligned with this target state

So the right move is:
- do not rewrite the whole system
- do not force stack migration
- do not start from UI polish first
- instead, formalize the backend operating skeleton first

## 2. Core Understanding Of Your Blueprint

## 2.1 DDD domain isolation

Your intended rule is correct:
- business logic should be physically isolated by domain
- `flow_lab`, `media`, and `trading` should not become one mixed utility bucket

Why this matters:
- ecommerce workflows have different data, risk, and approval rules than media workflows
- trading will be even more sensitive and should not leak into content/ecommerce code
- domain isolation is the only way to keep future scale from becoming chaotic

Current repo state:
- partial alignment only
- `src/ecommerce/` already behaves like an early domain package
- content/media logic is still scattered across pipeline/orchestrator/skills/API files
- there is no true `src/domains/` boundary yet

Conclusion:
- your DDD direction is correct
- current repo should evolve into it gradually

## 2.2 File + DB memory fabric

Your intended rule is also correct:
- DB stores compact state and metadata
- file system stores the long-form outputs
- each agent wake-up should load only what is necessary

This is exactly the right defense against:
- context window bloat
- token waste
- stale conversation dependency
- hard-to-debug long sessions

Current repo state:
- already directionally aligned
- reports, outputs, handoff docs, state docs, and DB metadata already coexist
- but the model is not yet normalized into explicit `run/task/artifact/approval` structures

Conclusion:
- the principle is correct
- the implementation skeleton is not complete yet

## 2.3 Python FastAPI control plane

This decision is correct for this repo.

Why:
- scheduler is already in Python
- agent orchestration is already in Python
- DB access is already in Python
- AI integration logic is already in Python

If you switched orchestration to Node now:
- you would duplicate control logic
- split system responsibility across runtimes
- increase operational complexity without solving your main bottlenecks

Conclusion:
- keeping Python/FastAPI is the right architecture choice

## 3. Flow Lab 1688/Taobao Visual-First Workflow Assessment

Your proposed Phase 1 is very good.

Why it is strong:
- it bypasses anti-bot friction immediately
- it gives business value without waiting for scraper maturity
- it matches your existing multimodal/CEO Console direction
- it keeps human approval in the loop

The workflow itself is sound:

1. CEO uploads screenshot
2. vision-capable model extracts specs/pain points
3. content agent drafts Shopee + Threads copy
4. state becomes `awaiting_approval`
5. CEO reviews and approves

This is practical, low-risk, and aligned with your current capabilities.

## 4. What Is Worth Optimizing In Your Current System

## 4.1 The architecture is not yet truly domain-first

Current issue:
- business logic is still distributed by technical concern instead of strict bounded context

Examples:
- ecommerce has partial isolation
- media/content logic is still spread across orchestrator/pipeline/AI helpers/skills
- future trading would currently have no clean place to land

Optimization:
- introduce `src/domains/`
- migrate gradually, not with a big bang rewrite

## 4.2 The memory fabric needs a formal skeleton

Current issue:
- file + DB behavior exists
- but the state model is still implicit

Missing primitives:
- `task`
- `event`
- `run`
- `artifact`
- `approval`

Optimization:
- define these first before adding more complex workflows

## 4.3 Flow Lab visual ingestion is not yet a first-class workflow

Current issue:
- CEO Console supports image upload to chat now
- but that is not the same as a proper `Flow Lab visual upload workflow`

Missing pieces:
- upload endpoint scoped to Flow Lab
- artifact file naming/storage convention
- task creation
- approval queue integration
- domain-specific output format

Optimization:
- make this a dedicated domain workflow, not just a generic chat capability

## 4.4 API surface is too concentrated in one file

Current issue:
- `src/api/main.py` is overloaded

Impact:
- hard to reason about ownership
- hard to evolve domain boundaries
- hard to implement workflow-specific route modules cleanly

Optimization:
- split routes by concern and later by domain

## 4.5 Prompt caching principles are not yet systemized

Your benchmark is correct:
- static prefix must remain stable
- dynamic state should be appended as messages/reminders
- tool sets should not constantly mutate
- model switching should happen through handoff, not hot-switching in one session

Current repo state:
- partially aligned conceptually
- not yet formalized in request-building utilities or agent contracts

Optimization:
- add a request-construction standard for AI calls
- define static vs dynamic prompt sections explicitly

## 5. My Recommended Starting Point: Option B

If we follow your three options and ask:
"What should we write first right now?"

My answer is:
- `Option B: State tracking skeleton`

Why not A first:
- folders alone do not give runtime capability

Why not C first:
- upload endpoint without task/event/artifact skeleton will create a one-off workflow

Why B first is best:
- it creates the memory fabric backbone
- it supports Flow Lab Phase 1 immediately after
- it enables approval queue, checkpointing, and future graph workflows

So the correct order is:
1. B
2. C
3. A as gradual refactor

## 6. Recommended First Implementation Sequence

## Step 1: Build the state skeleton

Add models/tables for:
- `tasks`
- `events`
- `artifacts`
- `approvals`

Minimum fields:

### tasks
- `task_id`
- `domain`
- `workflow_type`
- `status`
- `assignee`
- `created_at`
- `updated_at`
- `input_summary`

### artifacts
- `artifact_id`
- `task_id`
- `artifact_type`
- `path`
- `summary`
- `created_at`

### events
- `event_id`
- `task_id`
- `event_type`
- `payload_json`
- `created_at`

### approvals
- `approval_id`
- `task_id`
- `status`
- `reviewer`
- `review_note`
- `created_at`

## Step 2: Build Flow Lab visual upload

After the skeleton exists:
- add a Flow Lab upload route
- save uploaded image
- create task row
- create artifact row
- move task to `processing`

## Step 3: Add extraction + drafting workers

Then:
- vision extract -> `1688_visual_raw.md`
- draft generation -> Shopee + Threads draft artifact
- task -> `awaiting_approval`

## Step 4: Connect review queue

Then:
- CEO reviews artifacts in UI
- approve or reject
- record approval row and event row

## 7. Cache-First Understanding

Yes, I understand how this should shape future FastAPI + Anthropic integration.

Correct request design:

1. static prefix first
   - system prompt
   - tool definitions
   - stable role instructions

2. dynamic state after that
   - task context
   - reminders
   - current status
   - artifact summaries

3. no mid-session model switch
   - use handoff instead

4. no tool churn inside one request shape
   - load a stable tool set per workflow type

This means your data structure should clearly separate:
- `static_prompt_prefix`
- `dynamic_messages`
- `artifact_context`
- `workflow_state`

That separation is worth implementing as a shared request-builder utility later.

## 8. Impeccable UI Understanding

Yes, I understand the anti-pattern you want to avoid.

How I would avoid "everything is a card":

1. Use typography and spacing first
- section titles
- density hierarchy
- grouping by rhythm, not by boxes

2. Reserve bordered surfaces for true interaction zones
- review items
- approval actions
- editable forms
- critical metrics

3. Use subtle tonal separation instead of hard containers everywhere
- layered backgrounds
- thin borders
- restrained shadow use

4. Make the layout feel editorial, not dashboard-generic
- asymmetry where useful
- breathing room
- clear visual sequence

So the UI rule is:
- not "never use cards"
- but "use containers only when the interaction model justifies them"

## 9. Suggested File/Module Destination For This Blueprint

Your v3.1 ideas should map like this:

### domain structure
- `src/domains/flow_lab/`
- `src/domains/media/`
- `src/domains/trading/`

### workflow skeleton
- `src/workflows/`

### Flow Lab Phase 1
- `src/domains/flow_lab/api/`
- `src/domains/flow_lab/services/`
- `src/domains/flow_lab/prompts/`

### memory fabric
- `src/state/` or `src/workflows/models.py`

### UI
- `dashboard/src/app/flow-lab/` or maintain current ecommerce surface and evolve carefully

## 10. Current Gaps Between Vision and Repo

The biggest current gaps are:

1. no explicit `src/domains/` boundary
2. no normalized memory-fabric models
3. no dedicated Flow Lab screenshot workflow
4. overloaded API module
5. no formal cache-first request-builder standard
6. frontend build health still not fully clean
7. encoding debt in docs/comments still exists

## 11. Bottom Line

Your v3.1 blueprint is coherent and worth following.

The strongest parts are:
- DDD boundaries
- file + DB memory fabric
- Python-first control plane
- Flow Lab visual-first Phase 1
- approval-centric operating model

The main optimization advice is:
- start from the state skeleton, not from folder cosmetics or endpoint convenience

If we were to start coding immediately, the best first formal step would be:
- build the memory-fabric backbone (`tasks/events/artifacts/approvals`)

That is the best foundation for everything else you want next.
