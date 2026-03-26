# AI Office Review 2026-03-14

> Scope: compare current AI Office implementation against the project plan and identify remaining risks, gaps, and reinforcement opportunities.

## Findings

### 1. Frontend and backend access patterns are still inconsistent

Files:
- `dashboard/src/app/office/page.tsx`
- `dashboard/src/lib/api.ts`
- `dashboard/next.config.js`

Current state:
- most frontend requests use relative `/api/...`
- the office SSE stream still points to `http://localhost:8000/api/agents/stream`

Risk:
- AI Office depends on two different access patterns at once
- when frontend and backend are restarted differently, the page can partially work and partially fail
- this makes debugging much harder and was one of the reasons the office page became unreliable during review

What should be improved:
- standardize all AI Office traffic on one access path
- either use rewrite-based `/api/...` everywhere
- or use one explicit backend base URL everywhere

### 2. Startup guidance and runtime behavior are out of sync

Files:
- `README.md`
- `START_HERE.md`
- `CLAUDE.md`
- `src/api/main.py`

Current state:
- project docs still describe the usual dev startup flow
- actual review found that `uvicorn --reload` can fail in this environment with permission issues
- frontend startup can also fail if started with the wrong command path in PowerShell

Risk:
- a correct code change may still look broken because the running services are stale or never started properly
- AI Office review results become misleading if the runtime is not actually loading the latest code

What should be improved:
- add one canonical startup note for the current Windows environment
- document the safest frontend/backend launch commands
- clearly separate "normal local startup" from "this machine's current constraints"

### 3. Project plan documents are partially outdated

Files:
- `projects/anticlaude/ai_office_vision.md`
- `projects/anticlaude/ai_office_remaining_work.md`

Current state:
- planning docs still describe some items as future work even though parts of them now exist in code
- examples:
  - structured task metadata already exists
  - event logging already exists
  - demo handoff route already exists

Risk:
- Claude Code or future agents may under- or over-estimate what has already been implemented
- planning discussions can drift because docs are no longer a precise source of truth

What should be improved:
- update planning docs to mark:
  - completed
  - partially completed
  - not started
- avoid leaving mixed historical and current state in the same sections

### 4. Event API reports requested count, not actual count

File:
- `src/api/main.py`

Current state:
- `/api/agents/events` returns `{"count": limit}` instead of the actual number of returned events

Risk:
- the UI or later monitoring logic can misread how many events were actually loaded
- this becomes more problematic once pagination or replay behavior is added

What should be improved:
- return the real number of events
- optionally also return `limit` separately if needed

### 5. Timeline persistence exists at the storage layer, but not yet as a real product feature

Files:
- `src/api/agent_status.py`
- `dashboard/src/app/office/page.tsx`

Current state:
- events are appended to `outputs/office_memory/agent_events.jsonl`
- the UI can read recent events
- but the timeline is still closer to a lightweight event feed than a true replayable office history

Risk:
- the system appears to have memory, but the product experience still does not fully cash in on it
- there is no filtering, replay, grouping, status lifecycle, or reliable artifact navigation

What should be improved:
- promote timeline persistence from "log file exists" to "first-class office feature"
- add:
  - real count
  - ordering guarantees
  - grouping by task
  - agent/task filters
  - artifact links

### 6. Real workflow instrumentation is only partially complete

Files:
- `src/agents/orchestrator.py`
- `src/api/agent_status.py`
- `projects/anticlaude/ai_office_handoff_memory.md`

Current state:
- daily orchestrator now reflects the intended handoff direction better than before
- but AI Office still does not fully represent:
  - feedback flow
  - metrics/tracker loop
  - ecommerce work
  - blocked or done lifecycle

Risk:
- the office currently reflects a subset of AntiClaude operations
- users may assume the whole company view is live when only one major path is wired

What should be improved:
- explicitly mark which workflows are live
- wire the remaining systems one by one

## Open Questions

1. Should AI Office use one shared backend base URL across the whole dashboard, or should it continue relying on Next rewrites?
2. Should event memory stay in JSONL under `outputs/`, or should it move into SQLite once replay/filtering becomes more important?
3. Should demo handoff remain a permanent office feature, or only a development aid?

## Reinforcement Opportunities

### A. Add a runtime health checklist

Suggested file:
- `projects/anticlaude/ai_office_runtime_checklist.md`

Useful checks:
- frontend reachable at `/office`
- backend reachable at `/api/agents/status`
- stream reachable
- events endpoint reachable
- demo handoff reachable

### B. Add workflow coverage tracking

Suggested section in docs:
- which workflows are fully wired
- which are partial
- which are still planned

This would reduce ambiguity for Claude Code and other agents.

### C. Add memory summarization

The current event log is a good start, but agents will not "get smarter" from raw logs alone.

Best reinforcement:
- daily summary from event log
- lessons learned
- handoff failures
- repeated blockages
- write summary back into `.md` or a structured store

## Status Summary

Completed:
- structured task metadata
- demo handoff route
- event logging
- basic timeline feed

Partially completed:
- persistent timeline
- real workflow instrumentation
- handoff visibility
- documentation synchronization

Not yet completed:
- startup stabilization guidance
- artifact linking as a product feature
- blocked/done lifecycle
- memory summarization
