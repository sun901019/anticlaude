# Skill Adoption Matrix 2026-03-20

## 1. Purpose

This matrix maps major current AITOS skills into a consistent governance model.

It answers:

- what each skill is for
- which pattern it primarily uses
- whether it is actually used at runtime
- whether it is only used through workflow/SOP
- what is still missing before it becomes fully governed

---

## 2. Status Labels

- `runtime-used`
  - directly loaded/injected by code during execution
- `workflow-used`
  - used because a workflow or handoff depends on it
- `reference-only`
  - documentation/guidance only
- `partial`
  - some runtime effect exists, but enforcement is incomplete

---

## 3. Matrix

| Skill | Layer | Main Role | Task Type | Primary Pattern | Supporting Patterns | Current Status | Main Activation Path | Main Gaps |
|------|------|------|------|------|------|------|------|------|
| `content_creation` | composite | drafting / writing discipline | document generation | Generator | Tool Wrapper | `runtime-used` | `src/ai/claude_writer.py` | not yet explicitly tied to formal output contract schema |
| `marketing_strategy` | composite | topic strategy / selection logic | strategy generation | Tool Wrapper | Generator | `runtime-used` | `src/ai/gpt_strategist.py` | no explicit failure contract or score threshold policy |
| `seo_optimization` | composite | SEO/GEO scoring lens | quality review | Reviewer | Tool Wrapper | `runtime-used` | `src/ai/claude_scorer.py` | still mostly prompt-level, not yet full rubric object |
| `research_analysis` | composite | research quality framing | research / analysis | Tool Wrapper | Reviewer | `runtime-used` | `src/ai/competitor_analyzer.py`, `src/scrapers/perplexity_scraper.py` | not yet connected to trust-scoring contract everywhere |
| `geo_optimization_engine` | composite | GEO entity/citation/format rules | content generation | Tool Wrapper | Generator | `runtime-used` | `src/agents/dynamic_orchestrator.py`, `src/workflows/pipeline_graph.py` | not yet universally injected into every relevant content path |
| `write-threads-post.md` | ai skill | Threads writing SOP | document generation | Generator | Tool Wrapper | `workflow-used` | daily content workflow / handoff expectations | not yet directly runtime-injected as structured policy |
| `select-topic.md` | ai skill | topic filtering / top3 selection SOP | quality review / topic selection | Reviewer | Tool Wrapper | `workflow-used` | `workflow-daily-content.md`, human/agent execution discipline | not yet enforced by one shared runtime contract |
| `workflow-daily-content.md` | ai skill | end-to-end media workflow | multi-step process | Pipeline | Reviewer | `workflow-used` | daily content flow design and orchestration expectations | partially implemented in graph runtime, but still not a formal skill manifest |
| `workflow-*` future graph specs | projects/specs | process governance | multi-step process | Pipeline | Reviewer | `reference-only` | planning/spec layer | needs formal task-to-pattern routing |
| `Flow Lab visual workflow` specs | projects/specs | screenshot-first ecommerce process | multi-step process | Pipeline | Generator, Reviewer | `partial` | route + UI + artifact flow now exists | still needs richer domain migration and future video/URL adapters |
| `multimodal deliberation spec` | projects/specs | image/video/insight discussion | high-risk multi-step process | Pipeline | Reviewer, Tool Wrapper | `reference-only` | planning/spec layer | video path not implemented yet |
| `skill governance spec` | governance | meta-policy for skill design and selection | governance / routing | Tool Wrapper | Pipeline, Reviewer, Inversion | `reference-only` | planning/governance layer | needs orchestrator-aware adoption matrix usage |

---

## 4. Current Interpretation

## Strongly Adopted Already

These are already meaningfully active:

- `content_creation`
- `marketing_strategy`
- `seo_optimization`
- `research_analysis`
- `geo_optimization_engine`

These matter because they are no longer only documentation.
They affect runtime prompt construction today.

## Operationally Important but Not Fully Runtime-Enforced

These already influence system behavior, but mostly through workflow design and agent discipline:

- `write-threads-post.md`
- `select-topic.md`
- `workflow-daily-content.md`

These are important because they shape how Lara / agents are expected to operate,
but they still need stronger runtime enforcement if you want auditable consistency.

## Governance and Future-Layer Skills

These are important, but still mostly architecture memory:

- multimodal deliberation
- Flow Lab Phase 2 / video specs
- skill governance spec

They are not wasted.
They are just not yet fully operationalized.

---

## 5. What This Matrix Improves

If you adopt this matrix as part of AITOS governance, it improves the system in five major ways.

### 5.1 Skill Usage Becomes Auditable

Right now, some skills are used implicitly.

This matrix makes it visible:

- which skills are truly active
- which are only guidance
- which still need wiring

That reduces confusion and duplicate documents.

### 5.2 Lara Can Route More Intelligently

Once mapped, Lara can decide:

- this task needs `Generator`
- this task is high-risk, so also require `Reviewer`
- this task is unclear, so force `Inversion` first

That means better task routing and fewer shallow outputs.

### 5.3 High-Risk Outputs Become Safer

This helps formalize that:

- code generation
- strategy generation
- business recommendation
- complex workflows

should not go straight from generation to output without review.

That directly supports your approval-gated system design.

### 5.4 Context Loading Becomes Cleaner

This matrix helps enforce:

- do not preload all skills
- load only the relevant ones
- reduce token waste

That supports your cache-first / memory-fabric architecture.

### 5.5 Skill Sprawl Becomes Manageable

As your system grows, you will keep adding:

- new skills
- new SOPs
- new specs
- new external references

Without a matrix, that becomes messy.

With a matrix, every new skill must answer:

- what is it for
- when does it trigger
- what pattern is primary
- what output contract does it obey
- what failure conditions exist

That is long-term maintainability.

---

## 6. Best Immediate Use

This matrix is most useful right now for:

1. reviewing existing skills
2. deciding what needs runtime wiring next
3. deciding which high-risk flows require mandatory review
4. identifying where `Inversion` is missing

---

## 7. Recommended Next Actions

Best next follow-up steps:

1. add a new column later for:
   - `required references`
   - `required assets`
   - `output contract`
   - `failure conditions`
2. define task_type -> skill mapping in a machine-readable form
3. expose active skill set in Office / CEO UI for transparency
4. require `Reviewer` in all high-risk generation paths
5. identify where `Inversion` should be added before generation

---

## 8. Bottom Line

This matrix does not just organize documents.

It moves AITOS from:

- "we have many skills"

to:

- "we know which skills are active, why they are active, and how they should be governed"

That is a real architecture upgrade.
