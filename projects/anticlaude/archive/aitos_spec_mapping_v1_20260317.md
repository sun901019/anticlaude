# AITOS Spec Mapping v1 2026-03-17

## 1. Purpose

This document bridges the gap between:
- the newly drafted AITOS strategy/spec documents
- the current AntiClaude codebase

It answers one practical question:

"How do these new specs map into the current system without rewriting everything?"

This is not a greenfield architecture document.
This is an implementation mapping document.

## 2. What Exists vs What Is New

## Existing system

Current system already has:
- Next.js command center
- FastAPI control plane
- Python agent modules
- dynamic task routing
- night shift
- CEO chat
- review queue
- ecommerce workflow
- file-based async handoff

Main current implementation anchors:
- [src/api/main.py](C:/Users/sun90/Anticlaude/src/api/main.py)
- [src/agents/orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/orchestrator.py)
- [src/agents/dynamic_orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/dynamic_orchestrator.py)
- [src/agents/ceo.py](C:/Users/sun90/Anticlaude/src/agents/ceo.py)
- [dashboard/src/app/chat/page.tsx](C:/Users/sun90/Anticlaude/dashboard/src/app/chat/page.tsx)
- [dashboard/src/app/office/page.tsx](C:/Users/sun90/Anticlaude/dashboard/src/app/office/page.tsx)
- [dashboard/src/lib/api.ts](C:/Users/sun90/Anticlaude/dashboard/src/lib/api.ts)

## New spec documents already created

- [aitos_v3_optimization_reference_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_v3_optimization_reference_20260317.md)
- [aitos_langgraph_adoption_plan_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_langgraph_adoption_plan_20260317.md)
- [aitos_external_references_review_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_external_references_review_20260317.md)
- [aitos_recommended_optimization_master_plan_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_recommended_optimization_master_plan_20260317.md)
- [threads_algorithm_field_research_integration_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/threads_algorithm_field_research_integration_20260317.md)

Current status:
- these are strategy/design documents only
- they do not yet change runtime behavior

## 3. Mapping Philosophy

Do not replace the current system.
Map new capabilities into existing components.

Meaning:
- extend current agents
- add new workflow contracts
- add new analytics and scoring
- add optional graph-capable flows
- keep the current product shell intact

## 4. Capability Mapping Overview

## A. Graph orchestration

Spec intent:
- checkpoint/resume
- approval pauses
- retryable workflows
- node trace

Map into:
- [src/agents/orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/orchestrator.py)
- [src/agents/dynamic_orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/dynamic_orchestrator.py)
- new `src/workflows/` package
- new DB/file-backed run state

Recommendation:
- do not replace existing orchestrators immediately
- introduce a new workflow layer beside them

## B. Multi-agent discussion

Spec intent:
- proposal/critique/revision
- selective deliberation mode

Map into:
- [src/agents/ceo.py](C:/Users/sun90/Anticlaude/src/agents/ceo.py)
- [src/agents/dynamic_orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/dynamic_orchestrator.py)
- future `src/workflows/deliberation.py`
- CEO Console UI in [chat/page.tsx](C:/Users/sun90/Anticlaude/dashboard/src/app/chat/page.tsx)

Recommendation:
- add `fast mode` vs `team analysis mode`
- only route selected tasks into deliberation

## C. Threads strategy optimization

Spec intent:
- topic purity
- format selection
- breakout cooldown
- first-hour engagement planning
- similarity guard

Map into:
- `ai/skills/workflow-daily-content.md`
- `ai/skills/write-threads-post.md`
- [src/agents/dynamic_orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/dynamic_orchestrator.py)
- future `src/content/` package
- metrics/dashboard endpoints later

## D. External tool adoption

Spec intent:
- supervised browser access
- operator observability
- governance references

Map into:
- local workstation setup docs
- future execution adapter layer
- not directly into core server runtime yet

## E. Trading expansion

Spec intent:
- bounded trading research system

Map into:
- future `src/trading/`
- future dashboard trading pages
- not into current content/ecommerce modules

## 5. Direct File/Module Mapping

## 5.1 CEO / Routing Layer

Current file:
- [src/agents/ceo.py](C:/Users/sun90/Anticlaude/src/agents/ceo.py)

Current role:
- route user request
- return chosen agent and response

Recommended upgrades:
- add `analysis_mode`
  - `fast`
  - `team`
- add optional evidence-aware response contract
- add deliberation path for selected prompts
- add approval recommendation output when needed

Future change type:
- modify existing file
- possibly split helper logic into `src/workflows/ceo_router.py`

## 5.2 Daily orchestrator

Current file:
- [src/agents/orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/orchestrator.py)

Current role:
- sequential daily pipeline coordination

Recommended upgrades:
- keep as legacy/simple path
- gradually move high-value flows into workflow nodes
- emit run_id and node events
- support checkpoint-aware operation later

Future change type:
- incremental refactor
- not immediate replacement

## 5.3 Dynamic task router

Current file:
- [src/agents/dynamic_orchestrator.py](C:/Users/sun90/Anticlaude/src/agents/dynamic_orchestrator.py)

Current role:
- route task_type to handlers

Recommended upgrades:
- ideal bridge point for graph-capable tasks
- add support for:
  - `discussion_mode`
  - `approval_state`
  - `run_id`
  - `artifact_refs`
- handlers should gradually return normalized task results

Future change type:
- high-priority upgrade target

## 5.4 API layer

Current file:
- [src/api/main.py](C:/Users/sun90/Anticlaude/src/api/main.py)

Current role:
- expose all system endpoints
- scheduler
- trigger backend operations

Recommended upgrades:
- add workflow endpoints:
  - `/api/workflows/run`
  - `/api/workflows/{run_id}`
  - `/api/workflows/{run_id}/resume`
  - `/api/workflows/{run_id}/approve`
  - `/api/workflows/{run_id}/retry`
- add richer event payloads
- add content analytics endpoints later

Future change type:
- additive

## 5.5 Content strategy layer

Current state:
- distributed across pipeline logic, skills, and prompts

Recommended new package:
- `src/content/`

Suggested modules:
- `strategy.py`
- `format_selector.py`
- `topic_fit.py`
- `similarity_guard.py`
- `post_sequence.py`
- `engagement_plan.py`
- `postmortem.py`

Purpose:
- convert Threads/content strategy specs into reusable runtime logic

## 5.6 Skills layer

Current files:
- [ai/skills/workflow-daily-content.md](C:/Users/sun90/Anticlaude/ai/skills/workflow-daily-content.md)
- [ai/skills/write-threads-post.md](C:/Users/sun90/Anticlaude/ai/skills/write-threads-post.md)

Recommended upgrades:
- inject topic purity rules
- inject format selection logic
- inject first-hour plan generation
- inject hook style options
- inject first reply generation

Future change type:
- direct content workflow improvement

## 5.7 Frontend command center

Current files:
- [dashboard/src/app/chat/page.tsx](C:/Users/sun90/Anticlaude/dashboard/src/app/chat/page.tsx)
- [dashboard/src/app/office/page.tsx](C:/Users/sun90/Anticlaude/dashboard/src/app/office/page.tsx)
- [dashboard/src/app/morning/page.tsx](C:/Users/sun90/Anticlaude/dashboard/src/app/morning/page.tsx)

Recommended upgrades:
- CEO Console:
  - `Fast Answer`
  - `Team Analysis`
- AI Office:
  - workflow run timeline
  - node status trace
  - approval queue
  - retry/resume controls
- Morning page:
  - post-engagement checklist
  - "what to do after publish" suggestions

Future change type:
- additive UX layer

## 6. Agent-by-Agent Mapping

## Orio

Current:
- research and ingestion

Add:
- topic purity score
- persona fit score
- semantic distance score
- trend source categorization

Likely future files:
- `src/content/topic_fit.py`
- `src/content/post_sequence.py`

## Lala

Current:
- strategy and prioritization

Add:
- format selection
- breakout follow-up planning
- adjacency planning after high-performing posts

Likely future files:
- `src/content/format_selector.py`
- `src/content/strategy.py`

## Craft

Current:
- draft writing

Add:
- hook variants
- thread open-loop structure
- first reply seed
- CTA/question generation

Likely future files:
- writing prompts
- content workflow logic

## Sage

Current:
- scoring and analysis

Add:
- similarity risk
- follower conversion analysis
- unconnected reach analysis
- breakout cooldown recommendation

Likely future files:
- `src/content/postmortem.py`
- analytics endpoint logic

## Lumi

Current:
- engineering and implementation

Add:
- execution adapter layer ownership
- workflow engine integration
- tool risk boundary implementation

## Pixel

Current:
- UX and presentation review

Add:
- workflow visibility design
- approval review cards
- evidence panels
- post-performance diagnostic UI

## CEO

Current:
- top-level routing

Add:
- mode selection
- synthesis from multi-agent discussion
- escalation and approval gate decisions

## 7. New Runtime Components To Add

These are the new building blocks that bridge specs into code.

## 7.1 `src/workflows/`

Suggested package:
- `base.py`
- `models.py`
- `runner.py`
- `checkpoint_store.py`
- `deliberation.py`
- `approval.py`
- `events.py`

Purpose:
- represent graph-ready workflows without rewriting all agents

## 7.2 `src/content/`

Purpose:
- make content strategy executable instead of prompt-only

## 7.3 DB / state additions

Need new concepts:
- workflow runs
- workflow checkpoints
- approvals
- artifacts
- post-performance diagnostics

Implementation can be:
- SQLite first
- file-backed checkpoint fallback where useful

## 8. Which Specs Change Runtime Immediately?

None of the current spec documents change runtime by themselves.

They only affect runtime after being mapped into:
- code
- skills
- prompts
- workflows
- UI controls

So the current state is:
- strategy docs exist
- code behavior mostly unchanged

## 9. Recommended Implementation Order

## Phase 1: Foundation

Implement first:
- workflow schemas
- run/task/event/artifact models
- build health cleanup
- encoding cleanup in key docs/code

## Phase 2: Content System Upgrade

Implement next:
- topic fit gate
- format selection
- first-hour engagement plan
- first reply generation
- similarity guard

## Phase 3: CEO Workflow Upgrade

Implement next:
- fast vs team mode in CEO Console
- deliberation path for selected questions
- evidence-aware responses

## Phase 4: Workflow Runtime

Implement next:
- run ids
- checkpoint/resume
- approval pause/resume
- node trace visibility

## Phase 5: Domain Expansion

Implement later:
- trading bounded context
- supervised browser research tooling
- more advanced adapter execution

## 10. What Should Stay Unchanged For Now

Do not immediately replace:
- Next.js frontend
- FastAPI backend
- current orchestrator paths
- current skill/handoff model

Do not immediately add:
- many permanent new agent personas
- unsupervised browser control
- full graph orchestration for every endpoint

## 11. Practical Translation: Spec to Code

If you want these specs to start affecting the system, the first real work items are:

1. add workflow data models
2. add `src/content/` strategy modules
3. update content-related skills
4. add `analysis_mode` in CEO chat
5. add post-performance analytics fields
6. add approval and checkpoint infrastructure

Until those are implemented, the specs remain guidance documents only.

## 12. Bottom Line

The new specs are not separate fantasy architecture.
They are not replacements for the current system either.

They are a new guidance layer that should be mapped into the current codebase incrementally.

So the correct interpretation is:
- not "new system instead of old system"
- not "automatic behavior change"
- but:
- "a structured upgrade path for the existing system"
