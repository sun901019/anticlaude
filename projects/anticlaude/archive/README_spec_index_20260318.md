# AITOS Spec Index 2026-03-18

## 1. Purpose

This file is the master index for the planning/specification documents created so far.

Use it as:
- a reading guide
- a planning map
- a quick reference for future discussion

It does not replace the source documents.
It tells you what each document is for and in what order it is most useful to read.

## 2. Recommended Reading Order

If you want the fastest understanding of the whole system, read in this order:

1. [aitos_master_spec_index_and_operating_sop_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_master_spec_index_and_operating_sop_20260318.md)
2. [aitos_recommended_optimization_master_plan_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_recommended_optimization_master_plan_20260317.md)
3. [system_architecture_health_review_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/system_architecture_health_review_20260317.md)
4. [aitos_spec_mapping_v1_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_spec_mapping_v1_20260317.md)
5. [aitos_next_steps_roadmap_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_next_steps_roadmap_20260318.md)

If you only care about implementation direction:
- read sections 3, 4, and 5 below

If you only care about brand/content strategy:
- read sections 6 and 7 below

## 3. Core Architecture Documents

### [aitos_v3_optimization_reference_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_v3_optimization_reference_20260317.md)

Purpose:
- compares your AITOS v3.0 vision against the actual repo

Best for:
- understanding what already fits
- understanding what does not match yet
- deciding not to force a Node.js rewrite

### [aitos_recommended_optimization_master_plan_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_recommended_optimization_master_plan_20260317.md)

Purpose:
- the main optimization blueprint

Best for:
- understanding the target architecture
- seeing top-level priorities
- discussing future direction with one single reference file

### [system_architecture_health_review_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/system_architecture_health_review_20260317.md)

Purpose:
- audits the current system's runtime reality

Best for:
- known problems
- engineering debt
- repair priorities

### [aitos_v31_flowlab_architecture_consolidation_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_v31_flowlab_architecture_consolidation_20260318.md)

Purpose:
- consolidates your v3.1 architecture, Flow Lab visual-first plan, memory fabric, cache-first rules, and UI standards

Best for:
- checking whether the current blueprint is coherent
- understanding why Option B (state skeleton) is the best first implementation path

## 4. Workflow and Execution Documents

### [aitos_langgraph_adoption_plan_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_langgraph_adoption_plan_20260317.md)

Purpose:
- evaluates checkpoint/resume, approvals, workflow traces, long-running graphs, and multi-agent discussion

Best for:
- deciding how graph orchestration should enter the system
- deciding why Python-first orchestration is still preferred

### [aitos_spec_mapping_v1_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_spec_mapping_v1_20260317.md)

Purpose:
- maps the strategy/spec docs into current files, agents, and future package boundaries

Best for:
- bridging planning and implementation
- seeing what changes behavior now vs what is only guidance

### [aitos_master_spec_index_and_operating_sop_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_master_spec_index_and_operating_sop_20260318.md)

Purpose:
- operationalizes the vision into daily reporting, approval flow, source/risk model, and CEO experience

Best for:
- understanding what the system should feel like when complete
- understanding reports, approvals, and visibility requirements

### [aitos_next_steps_roadmap_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_next_steps_roadmap_20260318.md)

Purpose:
- clean step-by-step roadmap for what to do next

Best for:
- planning sequence
- deciding tomorrow/next-week priorities

## 5. Tooling, External Integration, and Safety

### [aitos_external_references_review_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_external_references_review_20260317.md)

Purpose:
- evaluates Paperclip, Claude HUD, chrome-cdp-skill, AI Night Shift, Threads strategy sources, and API guidance

Best for:
- understanding what external references are useful
- understanding what should be adopted carefully

### [x_and_figma_api_integration_notes_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/x_and_figma_api_integration_notes_20260318.md)

Purpose:
- records the intended integration model for X and Figma

Best for:
- future adapter planning
- auth model separation
- secret-handling decisions

### [cross_platform_scraping_guidelines_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/cross_platform_scraping_guidelines_20260318.md)

Purpose:
- defines cross-platform scraping safety, platform risk, and account-protection rules

Best for:
- avoiding blacklisting/shadow-limiting
- separating research and publishing identity

## 6. Brand, Content, and GEO Strategy

### [flow_lab_brand_strategy_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/flow_lab_brand_strategy_20260318.md)

Purpose:
- records Flow Lab's brand positioning, worldview, content pillars, and role implications

Best for:
- Flow Lab messaging
- product/content consistency
- future monetization framing

### [threads_algorithm_field_research_integration_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/threads_algorithm_field_research_integration_20260317.md)

Purpose:
- translates field-research Threads insights into practical content strategy

Best for:
- format choice
- first-hour interaction planning
- topic purity
- similarity guard logic

### [external_knowledge_ingestion_and_geo_defense_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/external_knowledge_ingestion_and_geo_defense_20260318.md)

Purpose:
- integrates external marketing knowledge and GEO-poisoning awareness into AITOS planning

Best for:
- understanding how Marketing-for-Founders influences Flow Lab and media writing
- understanding why trust and source diversity matter

### [skills_and_memory_audit_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/skills_and_memory_audit_20260318.md)

Purpose:
- audits whether current skills and memory are truly GEO-aware and well-preserved

Best for:
- understanding current limitations
- seeing why skills and memory still need normalization

## 7. UI and Design System Documents

### [ui_reverse_engineering_prompt_standard_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/ui_reverse_engineering_prompt_standard_20260318.md)

Purpose:
- formalizes reverse-engineering-first UI generation into a reusable AITOS standard

Best for:
- future Lara/Lumi/Pixel design work
- avoiding generic AI UI
- token-first Tailwind generation

## 8. Best Documents For Specific Questions

### "What is AITOS becoming overall?"

Read:
- [aitos_master_spec_index_and_operating_sop_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_master_spec_index_and_operating_sop_20260318.md)
- [aitos_recommended_optimization_master_plan_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_recommended_optimization_master_plan_20260317.md)

### "What should we build next?"

Read:
- [aitos_next_steps_roadmap_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_next_steps_roadmap_20260318.md)
- [system_architecture_health_review_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/system_architecture_health_review_20260317.md)

### "How do these specs map to current code?"

Read:
- [aitos_spec_mapping_v1_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/aitos_spec_mapping_v1_20260317.md)

### "How should Flow Lab be positioned?"

Read:
- [flow_lab_brand_strategy_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/flow_lab_brand_strategy_20260318.md)

### "How should Media / Threads be optimized?"

Read:
- [threads_algorithm_field_research_integration_20260317.md](C:/Users/sun90/Anticlaude/projects/anticlaude/threads_algorithm_field_research_integration_20260317.md)
- [external_knowledge_ingestion_and_geo_defense_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/external_knowledge_ingestion_and_geo_defense_20260318.md)

### "How safe is our scraping/tooling plan?"

Read:
- [cross_platform_scraping_guidelines_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/cross_platform_scraping_guidelines_20260318.md)
- [x_and_figma_api_integration_notes_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/x_and_figma_api_integration_notes_20260318.md)

### "Are our skills and memory already good enough?"

Read:
- [skills_and_memory_audit_20260318.md](C:/Users/sun90/Anticlaude/projects/anticlaude/skills_and_memory_audit_20260318.md)

## 9. Most Important Current Takeaways

If you only remember five things, remember these:

1. Do not rewrite to Node.js orchestration.
2. Build the workflow state skeleton (`run/task/event/artifact/approval`).
3. Keep research identity separate from publishing identity.
4. Flow Lab's core differentiator is "decision system", not "product selling".
5. Content/UI quality should become systemized, not prompt-only.

## 10. Bottom Line

This index is the entry point for future discussion.

If you return later and ask:
- "what should we talk about next?"

the answer should start here.
