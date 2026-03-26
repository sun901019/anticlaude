# AntiClaude / AITOS / Flow Lab
## Interview Presentation Deck

Use this as a PowerPoint-ready outline.
Recommended length: 10-12 slides, 8-12 minutes.

---

## Slide 1 — Title

**AntiClaude / AITOS / Flow Lab**  
AI Operating System + Ecommerce Decision Workspace

Subtitle:

- FastAPI + Next.js + SQLite
- Workflow runtime, approvals, AI agents, ecommerce operations

Speaker note:

> This is a self-built full-stack system that combines AI operations, workflow control, content systems, and an ecommerce operator workspace in one platform.

---

## Slide 2 — Problem I Wanted To Solve

Many real workflows were split across too many disconnected tools:

- AI generation had no governance
- review and approval were manual and messy
- ecommerce pricing relied on ad hoc spreadsheets
- product sourcing, content, and operator actions were not connected

Goal:

> build one controllable operator system instead of a pile of disconnected tools

---

## Slide 3 — What I Built

Three connected products inside one system:

- **AITOS / AI Office**: AI collaboration + approvals + workflow control
- **Media Engine**: topic strategy, draft generation, scoring, review
- **Flow Lab**: ecommerce pricing, sourcing, procurement, bundles

Key stack:

- Python FastAPI
- Next.js 14
- SQLite
- pytest

---

## Slide 4 — System Architecture

Architecture layers:

- `api/` transport layer
- `workflows/` runtime and approvals
- `domains/` business logic
- `adapters/` external integrations
- `dashboard/` operator UI

Key idea:

> move from prompts and pages to governed workflows and domain logic

Speaker note:

> I tried to keep business rules out of random UI code and converge them into maintainable backend/domain layers.

---

## Slide 5 — AI Operating System Model

Human + AI collaboration model:

- Human CEO at the top
- AI roles for strategy, research, writing, scoring, execution
- approval gates for high-risk actions
- artifacts and decision packages for auditability

Why it matters:

- AI becomes traceable
- risky actions require review
- work can pause, resume, and be audited

---

## Slide 6 — Workflow / Review / Approval System

Implemented:

- workflow runs
- tasks and events
- approval requests
- review queue
- CEO decision package
- resume / pause logic

Impact:

- human-in-the-loop control
- clearer operator trust
- better observability

---

## Slide 7 — Flow Lab Ecommerce System

Core capabilities:

- product quick add
- landed-cost estimation
- Shopee pricing logic
- QQL procurement mode
- top-down sourcing ceiling planning
- inbound and restock support
- weekly performance and decision support
- bundle design

Why it matters:

- turns ecommerce operations into a repeatable decision system

---

## Slide 8 — UX and Product Refinement

Major UX work I did:

- simplified product intake
- restructured product detail drawer
- improved inbound modal
- refined operator-facing ecommerce flows
- reduced confusion between pricing, logistics, and actions

Key lesson:

> good systems are not just feature-rich; they must reduce operator thinking cost

---

## Slide 9 — Reliability and Debugging Work

Representative fixes:

- notification spam containment
- test-side publish leak containment
- bundle endpoint schema/runtime repair
- test DB isolation recovery
- frontend/backend API alignment

Current baseline:

- `351 passed, 1 skipped, 1 warning`
- frontend production build passing

---

## Slide 10 — Evidence This Is a Real System

Current scale signals:

- 16 dashboard routes in production build
- about 101 backend route handlers
- 44 backend test files
- 15 Flow Lab products already in DB
- 1262 workflow runs recorded

Message:

> this is not a concept deck or a static demo; it is a live, evolving operator platform

---

## Slide 11 — What I Personally Contributed

I contributed across four layers:

- product and workflow design
- backend APIs and domain logic
- frontend operator UX
- debugging, quality recovery, and test stabilization

Interview framing:

> I can bridge product logic, implementation, and operational reliability instead of only working in one layer.

---

## Slide 12 — Current State and Next Direction

Current state:

- architecture is established
- core workflows run
- ecommerce operator surface is usable
- tests and build are green

Next direction:

- deeper formula convergence into backend truth
- richer family / variant modeling
- smarter bundle recommendations
- further UX cleanup and clarity

Closing line:

> I built an internal AI operating system and decision platform that is already working, measurable, and still actively improving.

---

## Optional Slide 13 — Demo Walkthrough

Suggested demo order:

1. Show dashboard / office
2. Show review queue / approvals
3. Show ecommerce / Flow Lab
4. Show product detail and pricing logic
5. Show bundle design
6. End with tests/build and architecture summary

---

## Optional Slide 14 — Fast 60-Second Version

> I built a full-stack AI operating system with FastAPI, Next.js, and SQLite. It combines workflow orchestration, review and approval gates, AI collaboration, content operations, and an ecommerce module called Flow Lab for pricing, sourcing, landed-cost analysis, procurement decisions, and bundle strategy. I also focused heavily on reliability by fixing runtime issues, stopping notification spam, stabilizing tests, and refining operator UX. The system currently passes 351 backend tests and builds successfully in production.

---

## Visual Guidance For PPT

Recommended design direction:

- clean white or soft gray background
- one accent color: deep orange or warm amber
- strong typography, low decoration
- 1 key diagram or 1 key statement per slide
- avoid screenshot overload

Suggested accent colors:

- `#F97316`
- `#EA580C`
- `#1F2937`
- `#F8FAFC`

---

## What To Put On Screen vs What To Say

On screen:

- short bullets
- metrics
- system diagram
- product screenshots

Say verbally:

- why the problem mattered
- how you designed the system
- what tradeoffs you made
- what you fixed when things broke

---

## Final Advice

When presenting, emphasize:

- this is a real operator system
- you solved both product and engineering problems
- you can build, debug, and refine
- you think in workflows, not just isolated features
