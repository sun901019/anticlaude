# AITOS LangGraph Adoption Plan 2026-03-17

## 1. Recommendation

Yes, this is worth planning for.

But the recommendation is:
- adopt the `LangGraph` model gradually
- prefer a `Python-first orchestration path`
- do not rush into `LangGraph.js` as the new core runtime

Reason:
- your desired capabilities are exactly where graph orchestration becomes useful
- your current repo is already Python-centered
- forcing JS orchestration now would create a split-brain control plane

So the best strategy is:
1. keep `Next.js` as command center
2. keep `FastAPI` as control plane
3. add a graph-style orchestration layer inside the backend
4. later decide whether a dedicated JS orchestration edge is still needed

## 2. Why LangGraph Is Relevant For AITOS

You explicitly want:
- checkpoint / resume
- multi-step human approval
- visualizable workflow and debug traces
- retryable long-running workflows
- multi-agent discussion before final answers

These are not "nice to have" features.
They are strong signals that your system is moving from:
- scripted pipelines

to:
- stateful operating workflows

That is exactly the category where graph-based orchestration is useful.

## 3. What LangGraph Would Help With

## 3.1 Checkpoint / Resume

Use cases:
- Orio finishes research, then the run pauses
- CEO approves topic direction later
- Craft continues from the saved state
- a failed step resumes from the last node instead of restarting the full pipeline

Value:
- lower cost
- better reliability
- better operator trust

## 3.2 Multi-step Human Approval

Use cases:
- approve top 3 topics
- approve draft selection
- approve ecommerce promotion
- approve a high-risk external action

Value:
- makes CEO truly the supervisor, not the manual executor
- supports real `human-in-the-loop` governance

## 3.3 Visual Workflow / Debug Trace

Use cases:
- why did the system choose this topic?
- which agent changed the strategy?
- where did the run fail?
- which evidence was used?

Value:
- easier debugging
- easier trust-building
- better auditability

## 3.4 Retryable Long-running Graphs

Use cases:
- scraping fails on one source
- one agent output is malformed
- one API call times out
- one branch can be retried without discarding all work

Value:
- operational resilience
- lower rerun cost
- fewer full-pipeline failures

## 3.5 Multi-agent Deliberation

Use cases:
- Orio collects signals
- Lala forms strategic options
- Sage critiques evidence quality
- Craft reframes for audience resonance
- CEO synthesizes and approves

Value:
- better answer quality
- less single-model bias
- more realistic "team reasoning"

## 4. What You Should Not Do

Do not:
- rewrite the whole system into LangGraph immediately
- replace all current endpoints with graph execution at once
- add agent debate everywhere by default
- let unlimited agent discussion run without budget and stopping rules

Why:
- it will increase token cost quickly
- it can make outputs slower without improving quality
- it can make debugging harder if the graph is introduced before contracts are stable

## 5. Best Architecture Direction For This Repo

Recommended target:

- Layer 1: `Next.js` command center
- Layer 2: `FastAPI` control plane
- Layer 3: `Graph orchestration runtime`
- Layer 4: `execution adapters` for Python tools, APIs, CLI agents, and future MCP tools
- Layer 5: `memory fabric` with DB + files + artifacts + checkpoints

In other words:
- keep your current base
- insert graph orchestration between API and agent execution

## 6. Should It Be LangGraph.js Or LangGraph In Python?

Recommendation:
- use the LangGraph concept now
- prefer Python implementation first

Why:
- your orchestration, scheduler, DB access, and agent runtime already live in Python
- moving stateful graph logic to JS would split ownership across runtimes
- Python is the lower-risk place to prove the operating model

When `LangGraph.js` becomes reasonable:
- if you later build a dedicated event-driven Node gateway
- if the command center itself starts owning live workflow sessions
- if most tools and runtime boundaries move into TS

Current decision:
- plan around LangGraph-style orchestration
- do not anchor the plan to `LangGraph.js` specifically

## 7. Recommended New Roles

Your current roster is already good, but if you want stronger "employees discussing with each other", I recommend adding functional roles at the workflow level before adding many permanent personas.

## 7.1 Keep current core roles

- `ceo`: final synthesis, approval, escalation
- `ori`: research and signal collection
- `lala`: strategic framing and prioritization
- `craft`: writing and audience adaptation
- `sage`: critique, scoring, risk analysis, SEO/GEO, later trading analysis
- `lumi`: engineering and systems implementation
- `pixel`: UX and presentation review

## 7.2 Add workflow roles, not necessarily permanent characters

Recommended temporary roles:
- `critic`
  - attacks weak evidence, shallow reasoning, unsupported claims
- `planner`
  - turns broad intent into executable steps and approval gates
- `reviewer`
  - checks policy, quality bar, and completion criteria
- `risk_officer`
  - required for ecommerce promotion, publishing, and later trading workflows
- `trading_researcher`
  - future bounded role for market structure, backtests, setup review

Why this is better:
- it keeps the system composable
- you avoid turning every workflow need into a full-time persona
- role behavior can be invoked only where useful

## 8. Suggested Deliberation Patterns

Not every task needs the same discussion pattern.

## Pattern A: Fast Route

Use for:
- simple user questions
- low-risk lookups
- dashboard summaries

Flow:
- CEO router -> specialist -> response

## Pattern B: Proposal + Critique

Use for:
- content topic selection
- ecommerce product evaluation
- roadmap choices

Flow:
- proposer -> critic -> reviser -> CEO

## Pattern C: Multi-agent Debate

Use for:
- top topic selection
- ambiguous product strategy
- high-value research synthesis

Flow:
- Ori research
- Lala strategy proposal
- Sage critique
- Craft audience framing
- CEO synthesis

## Pattern D: Approval Workflow

Use for:
- post publishing
- candidate promotion
- high-risk actions

Flow:
- analysis -> recommendation -> awaiting_human -> resume -> execute -> report

## 9. Risks

## 9.1 Complexity Risk

Graph systems can become harder to understand than simple pipelines.

Mitigation:
- keep graphs small at first
- introduce one domain at a time
- define node contracts clearly

## 9.2 Cost Risk

Multi-agent debate can multiply LLM calls fast.

Mitigation:
- only use debate on selected workflow classes
- cap round count
- cap token budget
- use lighter models for critique and filtering

## 9.3 Latency Risk

More nodes means slower completion.

Mitigation:
- use async fan-out only where needed
- support "fast mode" and "deliberation mode"
- cache research artifacts

## 9.4 State Explosion Risk

Checkpoint systems can accumulate messy state and orphaned runs.

Mitigation:
- define run ids
- define artifact ids
- store node state in a normalized schema
- implement retention and cleanup

## 9.5 Human Approval UX Risk

Human-in-the-loop can become annoying if approvals are too frequent.

Mitigation:
- require approval only for meaningful gates
- bundle approvals where possible
- provide concise evidence cards in UI

## 9.6 Governance Risk

Debating agents can produce elegant nonsense if evidence quality is weak.

Mitigation:
- force citations/evidence references in graph state
- give critic/risk nodes veto power on unsupported claims
- log reasoning lineage

## 10. Prerequisites Before Adoption

Before introducing graph orchestration, define:

1. Task schema
- `task_id`
- `run_id`
- `task_type`
- `source_agent`
- `target_agent`
- `inputs`
- `artifacts`
- `status`
- `approval_state`
- `created_at`
- `updated_at`

2. Run schema
- `run_id`
- `workflow_type`
- `current_node`
- `checkpoint_state`
- `resume_token`
- `retry_count`
- `error`

3. Artifact schema
- `artifact_id`
- `artifact_type`
- `producer`
- `path`
- `summary`
- `created_at`

4. Event schema
- `run_started`
- `node_started`
- `node_completed`
- `node_failed`
- `awaiting_human`
- `resumed`
- `run_completed`

## 11. Suggested Adoption Roadmap

## Phase 1: Stabilize Current Control Plane

- clean encoding debt
- make dashboard build green
- normalize task/result/artifact contracts
- centralize event emission

## Phase 2: Introduce Graph Concepts Without Framework Lock-in

- represent workflows explicitly as nodes and edges
- add checkpoint records
- add approval pause/resume
- add workflow trace logging

Targets:
- content pipeline
- review queue
- ecommerce promotion approval

## Phase 3: Add Deliberation Workflows

- implement `proposal + critique + revision`
- implement `debate mode` only for selected tasks
- add scoring for answer quality and confidence

## Phase 4: Add UI Visibility

- run timeline
- current node
- blocked approvals
- artifact graph
- retry controls

## Phase 5: Add Trading Research Graph

- research ingest
- market structure analysis
- setup classification
- backtest node
- review/critique node
- playbook node

## 12. First Workflows To Convert

Best first candidates:

1. Content topic selection
- high value
- already multi-step
- already semi-agentic
- strong need for approval gates

2. CEO Console deep analysis mode
- ideal place for multi-agent discussion
- can expose a "fast answer" vs "team analysis" option

3. Ecommerce selection and promotion
- naturally fits analyze -> approve -> promote -> monitor

Do not start with:
- every single endpoint
- low-value dashboard fetches
- all workflows at once

## 13. Concrete Recommendation

Yes, include this in the optimization scope.

But the correct framing is:
- not "rewrite into LangGraph.js"
- instead "evolve AITOS into graph-capable orchestration"

Recommended decision:
- adopt graph orchestration as a target capability
- prefer Python-first implementation
- add multi-agent deliberation selectively
- add temporary workflow roles like `critic` and `risk_officer`
- keep your current agents as the permanent org chart

## 14. Bottom Line

Your instincts are correct.

The features you want are exactly the point where a normal pipeline starts becoming an operating system.

So yes:
- checkpoint/resume should be planned
- human approval should be formalized
- workflow tracing should be added
- retryable long tasks should be built
- multi-agent discussion should be introduced

But do it as a controlled architectural upgrade, not as a wholesale framework rewrite.
