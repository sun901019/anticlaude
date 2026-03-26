# Skills and External References Usage Summary 2026-03-20

## 1. Short Answer

Not all skills are used in the same way.

There are three practical usage levels in the current system:

1. `runtime-used`
   - automatically injected by code during execution
2. `workflow-used`
   - used because Lara / the orchestrator / the workflow path chooses a task that depends on them
3. `reference-only`
   - stored as guidance or SOP, but not yet enforced by runtime on every call

So the answer is:

- some skills are used automatically
- some are only used when the workflow reaches the right task
- some are still guidance documents

This means your AI CEO / Lara effectively decides usage in two ways:

- directly, by selecting a task or workflow path
- indirectly, because certain task types auto-inject certain composite skills

---

## 2. What Is Automatically Used Right Now

These are the skills that are actually loaded by code today.

### Composite Skills That Are Runtime-Injected

- `content_creation`
  - used by `src/ai/claude_writer.py`
- `marketing_strategy`
  - used by `src/ai/gpt_strategist.py`
- `seo_optimization`
  - used by `src/ai/claude_scorer.py`
- `research_analysis`
  - used by:
    - `src/ai/competitor_analyzer.py`
    - `src/scrapers/perplexity_scraper.py`
- `geo_optimization_engine`
  - used by:
    - `src/agents/dynamic_orchestrator.py`
    - `src/workflows/pipeline_graph.py`
    - downstream drafting flows through `extra_skill`

### What This Means

These skills are not passive documents anymore.
They are part of prompt construction at runtime.

If the relevant task runs, these skills are loaded automatically.

---

## 3. Skills That Are Used Through Workflow Logic

These are important, but they are not injected into every model call as raw markdown.

### Operational Skills

- `ai/skills/write-threads-post.md`
- `ai/skills/select-topic.md`
- `ai/skills/workflow-daily-content.md`

Current role:

- they shape workflow expectations
- they guide handoffs and agent behavior
- they influence what Lara / Claude / Codex are expected to do

But:

- they are not yet fully enforced as runtime-injected skills on every call
- they are partly "execution SOP" rather than "always-loaded prompt blocks"

---

## 4. When Skills Actually Get Used

## 4.1 Automatic usage

A skill is automatically used when:

- a task handler explicitly injects it
- a graph node calls logic that loads it
- dynamic orchestrator adds it based on `task_type`

Examples:

- `draft_generation` -> loads GEO-related skill blocks
- scoring -> loads SEO optimization skill
- strategy -> loads marketing strategy skill

## 4.2 Conditional usage

A skill is only used when the workflow reaches the relevant branch.

Examples:

- no draft generation -> no `content_creation` injection
- no scoring -> no `seo_optimization`
- no research path -> no `research_analysis`

## 4.3 CEO / Lara decision effect

Lara does not manually "open every skill file every time".
Instead:

- Lara chooses the workflow
- Lara chooses the task path
- the chosen task path determines which runtime-injected skills activate

So yes:

`your AI CEO effectively decides when many skills are used, because task routing determines skill injection`

---

## 5. Are Skills Fully Enforced Yet

No, not fully.

Current reality:

- core composite skills: mostly real runtime usage
- operational workflow skills: partially enforced, partially documentation
- some standards still rely on agent discipline rather than hard runtime checks

So the system is no longer "skills exist only on paper", but it is also not yet "every skill is uniformly enforced by runtime."

---

## 6. External GitHub / Reference Material Status

Your previously provided GitHub / external references are mostly present in the planning layer, not fully converted into code features.

### References Already Incorporated into Planning Docs

- `EdoStra/Marketing-for-Founders`
  - reflected in GEO / marketing / messaging strategy docs
- `paperclipai/paperclip`
  - reflected as governance / operating-model reference
- `jarrodwatts/claude-hud`
  - documented as local operator tooling reference
- `pasky/chrome-cdp-skill`
  - documented as high-risk supervised browser-control reference
- `JudyaiLab/ai-night-shift`
  - reflected as runtime-pattern reference

### Where They Mostly Live Right Now

They are mainly captured in:

- `projects/anticlaude/aitos_external_references_review_20260317.md`
- `projects/anticlaude/external_knowledge_ingestion_and_geo_defense_20260318.md`
- `projects/anticlaude/aitos_recommended_optimization_master_plan_20260317.md`
- `projects/anticlaude/aitos_next_steps_roadmap_20260318.md`
- `projects/anticlaude/README_spec_index_20260318.md`

### Important Distinction

These references are:

- present in the system knowledge and planning layer
- partially reflected in skills and workflow design
- not all fully implemented as production features

So the answer is:

`yes, the GitHub/external references are still in the system context via docs and planning artifacts, but many of them are not yet fully operationalized in code`

---

## 7. Practical Interpretation for the CEO

If you ask:

`Will the system use my skills and references by default?`

Best answer:

- the system already uses the most important composite skills automatically in several core paths
- workflow/SOP skills are used when the relevant workflow is chosen
- Lara / the workflow path decides whether a skill becomes active
- external GitHub references mostly live in planning/spec/optimization docs until explicitly turned into code or adapters

---

## 8. Current Best Mental Model

Use this model:

- `Composite skills` = runtime weapon modules
- `ai/skills/*.md` = operating SOP and behavior guide
- `projects/anticlaude/*.md` = architecture memory, strategy memory, and future implementation reference

That is the current maturity level of the system.

---

## 9. Recommended Next Improvement

If you want stronger consistency later, the next upgrade should be:

1. define a formal `skill adoption matrix`
2. mark every skill as:
   - runtime-used
   - workflow-used
   - reference-only
   - deprecated
3. add hard runtime mapping from task_type -> required skills
4. expose active-skill info in the CEO / Office UI

That would make skill usage fully auditable instead of partly implicit.
