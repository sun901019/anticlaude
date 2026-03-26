# AntiClaude / AITOS / Flow Lab
## Interview Portfolio Report

Updated: 2026-03-25

---

## 1. Executive Summary

This project is a self-built AI operating system and operator workspace that combines:

- an AI collaboration layer
- a workflow / approval runtime
- a content operations system
- an ecommerce decision platform called **Flow Lab**
- a unified dashboard for review, approvals, reporting, and execution

It is not a single demo page. It is a working full-stack system with:

- Python FastAPI backend
- Next.js 14 dashboard
- SQLite operational data layer
- workflow graph runtime
- approval / review queue
- AI agent orchestration
- ecommerce pricing and sourcing logic
- multimodal routes for screenshots and video

Current engineering baseline:

- Backend test suite: `351 passed, 1 skipped, 1 warning`
- Frontend build: `next build` passing
- App routes: 16 active dashboard pages in the current app router build
- API endpoints: about 100 route handlers across backend surfaces

---

## 2. Product Vision

The system was designed to solve a practical problem:

> how to turn scattered AI tools, content workflows, ecommerce decisions, and operator tasks into one controllable operating system.

The project evolved into three connected products:

### A. AI Office / AITOS

An internal AI operating system where the user acts as Human CEO and AI roles collaborate through:

- orchestration
- task routing
- approval gates
- artifacts
- memory
- reporting

### B. Media / Content Engine

A Python-first content system with:

- topic strategy
- draft generation
- GEO / SEO enforcement
- scoring
- review queue
- publishing hooks

### C. Flow Lab

An ecommerce operator workspace focused on:

- product intake
- landed-cost calculation
- Shopee pricing decisions
- sourcing decisions
- procurement and inbound handling
- bundle design
- performance review

---

## 3. What I Built

### Backend Platform

I built and iteratively refined a backend platform that includes:

- FastAPI application layer
- modular API routes
- workflow engine and graph runtime
- approval / review request system
- SQLite schema and migrations
- domain isolation for media and flow_lab
- adapter layer for external capabilities

Representative backend areas:

- `src/api/`
- `src/workflows/`
- `src/domains/media/`
- `src/domains/flow_lab/`
- `src/adapters/`
- `src/db/`

### Frontend Operator Dashboard

I designed and iterated on a dashboard with dedicated surfaces for:

- chat
- office
- review
- morning report
- reports
- flowlab
- ecommerce
- figma
- system

Representative frontend areas:

- `dashboard/src/app/`
- `dashboard/src/components/`

### AI Collaboration Layer

I turned AI usage into a governed system rather than one-off prompts:

- CEO routing logic
- task-type dispatch
- skills loading and routing
- debate / judge patterns
- review gates
- human approval checkpoints

### Ecommerce / Flow Lab

I implemented the most product-heavy logic in the ecommerce domain:

- landed cost logic
- pricing decision logic
- Shopee 2026 fee handling
- QQL procurement mode
- top-down sourcing ceiling logic
- bundle strategy framework
- operator-facing ecommerce UX refinement

---

## 4. System Architecture

### Core Stack

- Backend: Python, FastAPI, APScheduler
- Frontend: Next.js 14 App Router, TypeScript, React
- Database: SQLite
- Testing: pytest
- AI providers: Claude / Gemini / GPT integration surfaces

### Architectural Pattern

The system follows a practical modular pattern:

- `api/` for transport and route surfaces
- `workflows/` for runtime and approvals
- `domains/` for business logic
- `adapters/` for external integrations
- `db/` for schema and persistence
- `dashboard/` for operator UI

### Why This Matters

This architecture let me avoid a common trap:

- UI logic and backend logic drifting apart
- AI behavior becoming opaque
- ecommerce calculations living only in spreadsheets
- approvals being bypassed

Instead, the system is converging toward:

- one operator workspace
- one backend truth for business logic
- auditable AI decisions
- maintainable domain separation

---

## 5. Key Capabilities

### 5.1 Workflow and Approval Runtime

Implemented:

- workflow runs
- tasks
- events
- artifacts
- approval requests
- graph runner with pause / resume
- checkpoint store
- CEO decision package generation

Why it matters:

- turns AI work into traceable operations
- allows human approval before high-risk actions
- supports resumable multi-step execution

### 5.2 Review Queue and CEO Control Surface

Implemented:

- review inbox
- approval package API
- decision flow for approve / reject / defer
- review cleanup and dedup improvements

Why it matters:

- prevents AI actions from silently bypassing the operator
- gives a practical human-in-the-loop control model

### 5.3 Content Engine

Implemented:

- topic research
- strategy scoring
- draft generation
- GEO / SEO related skill injection
- quality scoring
- review and publishing hooks

Why it matters:

- connects content generation to governance and quality control
- avoids raw prompt-only workflows

### 5.4 Flow Lab Ecommerce Engine

Implemented:

- quick-add product intake
- landed-cost estimation
- pricing decision logic
- QQL procurement integration
- sourcing ceiling planning
- inbound modal
- weekly performance table
- bundle design surface
- family / variant planning direction

Why it matters:

- replaces scattered manual calculations with a decision workspace
- supports both sourcing-first and market-first product decisions

### 5.5 Multimodal / Media Surfaces

Implemented or planned with working scaffolding:

- screenshot analysis route
- video upload path
- figma integration surface
- visual operator flows

Why it matters:

- expands the system beyond text-only automation

---

## 6. Most Important Problems I Solved

### Problem 1: Approval and notification noise

Issue:

- repeated pending-decision notifications were spamming the operator

Fix:

- added persistent notification dedup using SQLite-backed dispatch tracking

Result:

- repeated Flow Lab approval events no longer send duplicate LINE notifications every time the same event re-enters the flow

### Problem 2: Test data leaking into live behavior

Issue:

- test-style social publish paths could hit real publish logic if tokens existed locally

Fix:

- contained the Threads leg in test-side dual-publish logic
- improved test isolation

Result:

- test text such as `Hello world` no longer leaks into real social surfaces during test runs

### Problem 3: Bundle recommendation runtime failures

Issue:

- bundle suggestion route crashed due to schema/query mismatch

Fix:

- aligned bundle logic with actual schema
- derived margin from performance records
- derived stock from inventory records

Result:

- `/api/ecommerce/selection/bundles/suggest` stabilized

### Problem 4: Ecommerce page overload

Issue:

- the ecommerce page had become too heavy and mixed too many responsibilities

Fix:

- started modular extraction
- reduced the main page file substantially
- split shared components and major sub-surfaces

Result:

- operator UX improved and codebase became more maintainable

### Problem 5: Test baseline trust

Issue:

- test DB isolation and schema drift had damaged trust in the backend test baseline

Fix:

- strengthened repo-local DB test isolation
- repaired schema usage in failing domains

Result:

- full suite returned to green: `351 passed, 1 skipped, 1 warning`

---

## 7. Representative Engineering Decisions

### Decision A: Python-first backend authority

I intentionally converged critical business logic toward the backend so the UI would not become a second source of truth.

Example:

- pricing logic should come from backend-calculated values rather than duplicated frontend formulas

### Decision B: Approval before autonomy

High-impact actions should not quietly execute.

Examples:

- publishing
- operator notifications
- workflow continuation

This led to:

- approval matrix
- review queue
- checkpoint-based resume logic

### Decision C: Operator UX should reduce thinking cost

In the ecommerce system, the best improvements were not always adding more features.

The better pattern was:

- fewer first-step fields
- clearer next actions
- problem rows surfacing automatically
- scenario labels that explain why a number exists

### Decision D: Domain separation over one giant app file

As the system grew, I pushed toward:

- `domains/media`
- `domains/flow_lab`
- adapter boundaries
- thinner route handlers

This matters because the project is not a toy demo anymore.

---

## 8. My Contribution Framing for Interviews

If I had to explain what I personally did in interview language:

### Product Thinking

- defined operator workflows around real use cases
- turned vague AI ideas into systemized execution rules
- translated practical ecommerce operations into software logic

### Full-Stack Delivery

- implemented backend APIs
- refined database schema and query logic
- built and iterated dashboard pages
- connected frontend operator surfaces to backend decision logic

### AI Systems Design

- designed human-in-the-loop AI workflows
- introduced skills, routing, review, and approval patterns
- built a more governable AI collaboration model

### Reliability and Debugging

- repaired runtime failures
- stabilized noisy notification flows
- rebuilt test trust
- verified work with repeated build and pytest validation

---

## 9. Current Project State

### Working and Demonstrable Today

- dashboard build passes
- backend tests pass
- review and approval system works
- ecommerce pricing and sourcing flows work
- Flow Lab bundle recommendation route works
- notification spam issue has been contained
- multiple dashboard pages are live and routable

### Still Being Refined

- deeper frontend/backend formula convergence
- final ecommerce UX cleanup
- remaining mojibake cleanup
- further bundle intelligence based on family / variant / live product context
- stronger presentation and operator guidance layers

This is important in interview framing:

> the project is already real and usable, but still actively improving in quality and product clarity.

---

## 10. Quantifiable Signals

Current verifiable signals from the local project state:

- Backend test files: `44`
- Backend suite: `351 passed, 1 skipped, 1 warning`
- Frontend app routes built: `16`
- Approximate API handlers: `101`
- Flow Lab products in DB: `15`
- Workflow runs in DB: `1262`
- Approval records in DB: `29`
- Review items currently in DB: `4`

These numbers help frame the project as an actual system rather than a concept deck.

---

## 11. Suggested Interview Storyline

If presenting verbally, the clearest order is:

1. Start with the problem
   - I wanted one system to manage AI work, content operations, and ecommerce decisions instead of scattered tools.
2. Show the architecture
   - FastAPI + Next.js + SQLite + workflow runtime + approvals.
3. Show the AI operating model
   - Human CEO + AI roles + approval gates + artifacts.
4. Show Flow Lab
   - product intake, landed cost, pricing, sourcing, bundles.
5. Show reliability and debugging
   - green tests, build passing, runtime fixes, notification containment.
6. End with why it matters
   - this is a self-built operator system, not just a UI mockup.

---

## 12. Short Interview Version

If the interviewer asks for a concise summary:

> I built a full-stack AI operating system and ecommerce decision workspace using FastAPI, Next.js, and SQLite. It includes workflow orchestration, approval gates, review queues, content operations, and a Flow Lab ecommerce module for pricing, sourcing, landed-cost estimation, and bundle strategy. I’ve also spent a lot of time on reliability work: test isolation, runtime debugging, notification dedup, API alignment, and operator UX refinement. The project is currently build-clean and test-green, with 351 passing backend tests and a working multi-page dashboard.

---

## 13. Interview Q&A Preparation

### If asked: "What is the hardest part?"

Answer direction:

- making AI behavior governable
- keeping backend logic and frontend behavior aligned
- turning ecommerce heuristics into maintainable system logic

### If asked: "What did you learn?"

Answer direction:

- product clarity matters as much as technical implementation
- approval and observability are critical in AI systems
- duplicated business logic quickly becomes a trust problem

### If asked: "What would you improve next?"

Answer direction:

- further formula centralization in backend services
- stronger family / variant product modeling
- richer bundle recommendation logic based on real product and sales context
- tighter UI guidance for operator workflows

---

## 14. Final Positioning

This project demonstrates capability in:

- product thinking
- backend engineering
- frontend implementation
- AI systems design
- workflow orchestration
- ecommerce logic modeling
- debugging and quality recovery

For interview use, the strongest framing is:

> I didn’t just build features. I built an evolving operating system that coordinates AI, workflows, approvals, and ecommerce decisions in one controllable environment.
