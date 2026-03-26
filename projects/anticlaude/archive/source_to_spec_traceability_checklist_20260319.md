# AITOS Source-to-Spec Traceability Checklist 2026-03-19

## 1. Purpose

This document verifies whether the major guidance blocks you provided have already been absorbed into the current AITOS planning documents.

It is a traceability checklist, not a new architecture spec.

Status meanings:
- `Fully captured`: the core intent and structure were already consolidated into one or more existing docs
- `Partially captured`: the main idea was captured, but some subpoints remain implicit or not yet broken into a dedicated spec
- `Not yet captured`: mentioned before, but not yet meaningfully translated into the current spec set

## 2. Overall Assessment

High-level result:
- Most major architecture, workflow, safety, and planning concepts have been captured
- The current gap is not missing direction, but missing fine-grained implementation specs
- The main remaining work is turning guidance into executable schemas, approval matrices, and source registries

## 3. Traceability by Source Block

## 3.1 Token and Memory Architecture

Source themes:
- prompt caching for skills
- artifact handoff instead of raw file fan-out
- vector retrieval instead of full-history prompting
- skill loader optimization
- artifact schema definition
- Lara as routing hub

Status:
- `Fully captured` for architecture direction
- `Partially captured` for implementation detail

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/aitos_langgraph_adoption_plan_20260317.md`
- `projects/anticlaude/aitos_master_spec_index_and_operating_sop_20260318.md`
- `projects/anticlaude/system_architecture_health_review_20260317.md`

Notes:
- The strategic direction is captured clearly
- What is still missing is a concrete runtime spec for:
  - skill cache lifecycle
  - cache invalidation rules
  - artifact schema taxonomy
  - retrieval policy

## 3.2 Solo AI Team Management Guidelines

Source themes:
- CEO as final decision-maker
- Lara as orchestrator
- specialist-only agent roles
- dumb scripts/adapters as layer 4
- file-based handoff over free-form multi-agent chatting
- approval inbox as hard gate

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/aitos_v31_flowlab_architecture_consolidation_20260318.md`
- `projects/anticlaude/aitos_master_spec_index_and_operating_sop_20260318.md`
- `projects/anticlaude/aitos_recommended_optimization_master_plan_20260317.md`

Notes:
- This is one of the most consistently preserved parts of the current planning set

## 3.3 Agent Skill Adoption List

Source themes:
- Lara: planning with files, acceptance checking, retry loop
- Lumi: brainstorming, TDD, simplification
- Pixel/Craft: anti-generic UI and visual testing
- multi-agent peer review for important changes

Status:
- `Partially captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/ui_reverse_engineering_prompt_standard_20260318.md`
- `projects/anticlaude/system_architecture_health_review_20260317.md`

Notes:
- The role philosophy is captured
- Missing dedicated follow-up specs:
  - role-by-role skill contract
  - retry criteria
  - acceptance criteria registry
  - peer review trigger matrix

## 3.4 Automation and Memory Toolkit

Source themes:
- local browser session reuse
- self-improving agent loop
- lossless memory compression
- skill vetting
- control center
- opencli/browser automation
- backup and restore

Status:
- `Partially captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/aitos_external_references_review_20260317.md`
- `projects/anticlaude/cross_platform_scraping_guidelines_20260318.md`
- `projects/anticlaude/x_and_figma_api_integration_notes_20260318.md`

Notes:
- The adoption model and risk framing were captured
- Still missing:
  - tool-by-tool adoption matrix
  - privilege model
  - backup retention policy
  - self-improvement rule-writing workflow

## 3.5 Visual Feedback and Optimization Loop

Source themes:
- image/video as system input
- multimodal insight extraction
- AI proposes changes, not self-executes them
- approval queue before overwrite or git actions
- self-modification limited to skills/prompts before core code

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/aitos_v31_flowlab_architecture_consolidation_20260318.md`
- `projects/anticlaude/ui_reverse_engineering_prompt_standard_20260318.md`

Notes:
- This logic is already reflected clearly in the current planning direction

## 3.6 External Skills Integration Blueprint

Source themes:
- zero-contamination boundary
- adapter pattern
- Pydantic-typed I/O
- extracting useful logic from LangChain/LlamaHub without importing the full framework
- MCP as isolated subprocess/server integration
- R&D sources treated as high-risk and reimplemented safely

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/aitos_external_references_review_20260317.md`
- `projects/anticlaude/cross_platform_scraping_guidelines_20260318.md`

Notes:
- This is already one of the strongest and clearest standards in the current document set

## 3.7 Skill Discovery and Integration Guide

Source themes:
- MCP registries
- GitHub search patterns
- source classes
- wrapper/client pattern
- timeout and exception shielding

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/aitos_external_references_review_20260317.md`

Notes:
- Discovery channels and safe adoption logic are preserved

## 3.8 Skill and Research Protocol

Source themes:
- no direct external API calls from agents
- cost-aware and cached research
- Tavily / Exa / Firecrawl / Jina / RSS strategy
- Orio scoring dimensions
- directory placement recommendations

Status:
- `Partially captured`

Mapped docs:
- `projects/anticlaude/aitos_token_memory_skill_integration_consolidation_20260319.md`
- `projects/anticlaude/cross_platform_scraping_guidelines_20260318.md`
- `projects/anticlaude/aitos_master_spec_index_and_operating_sop_20260318.md`

Notes:
- Source strategy and Orio scoring are captured
- What still needs a dedicated follow-up spec:
  - source registry
  - source trust scoring rubric
  - adapter-by-adapter placement plan
  - polling/scheduling policy

## 3.9 External Knowledge Ingestion

Source themes:
- Marketing-for-Founders as reusable growth knowledge
- UI reverse-engineering prompt standard
- using external references to improve Flow Lab and Media output quality

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/external_knowledge_ingestion_and_geo_defense_20260318.md`
- `projects/anticlaude/ui_reverse_engineering_prompt_standard_20260318.md`
- `projects/anticlaude/aitos_external_references_review_20260317.md`

Notes:
- The GitHub marketing source was incorporated
- The Google Doc itself was not fully fetched from the environment, but your pasted prompt and design rules were captured and formalized

## 3.10 Threads Research and GEO / Source-Poisoning Discussion

Source themes:
- Threads ranking behavior
- hook, format, reply, cooldown, and similarity logic
- GEO poisoning risk
- source trust and evidence lineage

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/threads_algorithm_field_research_integration_20260317.md`
- `projects/anticlaude/external_knowledge_ingestion_and_geo_defense_20260318.md`
- `projects/anticlaude/cross_platform_scraping_guidelines_20260318.md`

Notes:
- Strategy-level implications are already reflected in the current planning set

## 3.11 Flow Lab Brand Strategy

Source themes:
- Flow Lab as a decision-system brand
- AI + data + systemized ecommerce positioning
- content pillars and worldview

Status:
- `Fully captured`

Mapped docs:
- `projects/anticlaude/flow_lab_brand_strategy_20260318.md`
- `projects/anticlaude/aitos_v31_flowlab_architecture_consolidation_20260318.md`

Notes:
- This is already clearly preserved and reusable

## 4. What Was Not Lost

The following major ideas were not lost in the consolidation:
- Python-first control plane
- DDD-style domain separation
- file plus DB memory fabric
- approval-first execution model
- artifact-driven workflows
- high-risk tool isolation
- source-risk awareness for scraping and publishing
- Flow Lab as a systems brand, not a product-only brand
- Threads strategy as a structured operating model, not random posting

## 5. What Is Still Missing

The main gaps are not conceptual gaps.
They are specification gaps.

The most important missing follow-up docs are:
- `Workflow Schema Spec`
- `Approval Matrix`
- `Source Registry`
- `Artifact Taxonomy`
- `Agent Role Contract Spec`
- `Tool Adoption Matrix`

## 6. Final Verdict

Verdict:
- No major source block appears to have been dropped
- Several blocks were merged into broader categories instead of being preserved line by line
- The remaining work is to convert already-captured guidance into smaller implementation-ready specs

This means the current planning layer is directionally complete, but not yet fully operationalized.
