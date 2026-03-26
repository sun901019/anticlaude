# AI Office Vision

> Purpose: define the target effect, current state, and implementation path for AntiClaude AI Office.
> Updated: 2026-03-15

## Implementation Status (2026-03-15)

| Feature | Status |
|---------|--------|
| Structured AgentTask + AgentEvent model | DONE |
| SSE real-time snapshot streaming | DONE |
| 6 agent cards with role/status/task | DONE |
| `awaiting_human` status + orange card UI | DONE |
| Action buttons (approve/reject/select draft) | DONE |
| Activity stream with agent filter | DONE |
| Phase 3A: Ori real Serper search | DONE |
| Phase 3A: Sage auto-scoring via Claude | DONE |
| Phase 3A: Craft auto-report generation | DONE |
| Scheduled job events emit to AI Office | DONE |
| LINE Notify on awaiting_human | DONE |
| Sage rule synthesis on 10 lessons | DONE |
| Real pipeline driving office activity | DONE (pipeline runs daily at 08:00) |

## Product Intent

AI Office is not just a dashboard.

It is the operating room for AntiClaude as an AI company.

The intended user experience is:
- each AI employee has a clear role
- work is visible in real time
- tasks move from one agent to another
- outputs are traceable
- the human owner can understand team status at a glance

The target feeling is:
- not "system logs"
- not "a status board"
- but "a live digital team at work"

## What AI Office Should Eventually Show

### 1. Agent Identity

Each agent should have:
- persona
- domain responsibility
- current status
- current assignment
- recent output
- next handoff target

Core team:
- Ori: research and input discovery
- Lala: strategy and angle selection
- Craft: writing and content production
- Lumi: engineering and system implementation
- Sage: analysis and decision support
- Pixel: design and presentation

### 2. Work Objects

AI Office needs first-class work objects, not just text status.

Examples:
- task
- brief
- research packet
- strategy memo
- draft
- review
- implementation ticket
- report

Each work object should have:
- id
- title
- owner agent
- upstream source
- downstream handoff
- status
- timestamps
- output reference

### 3. Workflow Visibility

The office should show:
- what entered the system
- who is handling it now
- what was produced
- where it goes next
- where it is blocked

This means AI Office should visualize workflow state, not just agent state.

### 4. Handoff Chain

The core experience should make multi-agent cooperation visible.

Example chain:
- Ori finds signal
- Lala chooses angle
- Craft writes output
- Pixel packages presentation
- Sage evaluates performance
- Lumi implements tooling or automation around the loop

The user should be able to see:
- previous step
- current step
- next step

### 5. Outcome Traceability

Every meaningful action should link to an output.

Examples:
- research note
- selected topic
- draft content
- design asset
- dashboard change
- analytics insight

AI Office should answer:
- what did this agent actually produce
- where can I open it
- what happened after it

## Current State（截至 2026-03-14）

Phase 1–5 均已完成，AI Office 已從雛形升級為可信控制室。

Current implementation:
- real-time SSE status feed（直連 port 8000，`NEXT_PUBLIC_API_BASE` env var）
- visual cards for six agents（Ori / Lala / Craft / Lumi / Sage / Pixel）
- structured task state（task_id / task_type / priority / source_agent / target_agent / artifact_refs）
- persistent timeline（agent_events.jsonl → `/api/agents/events`）
- handoff lifecycle（blocked / done / handoff_pending helpers in agent_status.py）
- artifact linking（artifactLink() maps file paths to dashboard routes）
- real workflow instrumentation（orchestrator / tracker / feedback / ecommerce all emit）
- daily memory summary（daily_summary.py，triggered at end of orchestrator）
- one-click startup（start.ps1 with port conflict detection）
- Lala hot-topic injection（high-engagement pattern from 3 periods of audience_insights）
- Flow Lab learning loop（approved/rejected → Sage auto-lesson → 10-count consolidation）

Current files:
- `dashboard/src/app/office/page.tsx`
- `src/api/agent_status.py`
- `src/agents/orchestrator.py`
- `src/office/daily_summary.py`
- `src/feedback/memory.py`（get_rich_memory_context with hot topic pattern）

## Remaining Gaps

### Gap 1. Timeline Agent Filter UI

Timeline shows all events but lacks filter chips by agent.

Needed:
- frontend agent chips (Ori / Lala / Craft / all)
- API supports `?agent_id=` query param

### Gap 2. Threads Audience Segmentation → Lala

Basic audience_insights injection is done.
Deep segmentation (age / profession / interest) not yet injected into topic selection.

### Gap 3. Flow Lab Rules → Lala Integration

Sage auto-lesson is implemented.
Aggregated rules not yet fed back into Lala content-strategist prompt.
Triggered once lesson count accumulates sufficiently.

## Execution Plan

### Phase 1. Structured Agent State

Goal:
- upgrade from text-only status to typed task status

Implementation:
- extend `src/api/agent_status.py`
- add task metadata model
- update office UI to render richer state

Definition of done:
- each agent can expose one active task with metadata
- UI shows owner, task type, age, and next step

### Phase 2. Team Timeline

Goal:
- make work history persistent and reviewable

Implementation:
- add event log storage
- append agent events from backend
- render a real timeline in office UI

Definition of done:
- recent events survive reload
- user can inspect what happened in order

### Phase 3. Handoff System

Goal:
- visualize collaboration, not just occupancy

Implementation:
- add handoff event schema
- represent transitions between agents
- render previous/current/next state in UI

Definition of done:
- a task can visibly move from one agent to another

### Phase 4. Artifact Linking

Goal:
- tie work to outputs

Implementation:
- attach files, DB records, or URLs to tasks and events
- expose recent deliverables in UI

Definition of done:
- every major completed task has a linked artifact

### Phase 5. Real Workflow Instrumentation

Goal:
- AI Office reflects actual AntiClaude operations

Implementation:
- instrument pipeline, content, analytics, and ecommerce workflows
- emit agent events from real execution points

Definition of done:
- office activity is generated by real work, not only manual status updates

## Initial Technical Direction

Recommended backend additions:
- `AgentTask`
- `AgentEvent`
- `AgentHandoff`

Recommended fields for `AgentTask`:
- `id`
- `agent_id`
- `title`
- `task_type`
- `status`
- `priority`
- `started_at`
- `updated_at`
- `source_agent_id`
- `target_agent_id`
- `artifact_refs`

Recommended fields for `AgentEvent`:
- `id`
- `task_id`
- `agent_id`
- `event_type`
- `message`
- `created_at`
- `metadata`

## Codex Role

Codex can execute this plan.

Default responsibilities:
- define schemas
- implement backend state model
- wire event emission
- build office UI updates
- review integration gaps while doing so

Codex should treat AI Office as a product system, not only a page component.

## Immediate Next Step

Best next implementation step:
- Phase 1

Specifically:
- replace plain status text with structured task state in `src/api/agent_status.py`
- update `dashboard/src/app/office/page.tsx` to render richer agent cards and a more meaningful in-progress panel
