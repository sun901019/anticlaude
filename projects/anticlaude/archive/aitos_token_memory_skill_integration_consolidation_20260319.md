# AITOS Token, Memory, Skill, and Integration Consolidation 2026-03-19

## 1. Purpose

This document consolidates the new governance ideas you provided into one organized structure.

It groups them into clear categories so they can later become:
- architecture rules
- workflow rules
- adapter standards
- skill adoption standards
- future implementation priorities

This is a consolidation document only.
It does not change runtime behavior by itself.

## 2. Core Strategic Themes

Across all the content you provided, the system direction can be reduced to six major themes:

1. `Token minimization and cache-first prompting`
2. `Artifact-based memory and handoff`
3. `Strict hierarchy in solo AI team management`
4. `External skill integration via adapters only`
5. `Visual/multimodal input as optimization and business input`
6. `Human approval as the final safety boundary`

Those six themes are coherent and mutually reinforcing.

## 3. Category A: Token and Memory Architecture

## 3.1 What the rule is

LLM calls must not repeatedly:
- reread long SOPs
- pass huge raw files between agents
- carry bloated conversation history

The target model is:
- cache stable prompts
- hand off compressed artifacts
- retrieve only relevant memory when needed

## 3.2 The three-pillar system

### Pillar 1: Skill caching

Goal:
- agents should not reread long skills every run

Architecture direction:
- cache role prompt + skill SOP + stable tool definitions
- pass only short task instructions later

Practical implication for AITOS:
- static prompt prefix needs to be separated from dynamic runtime state
- skills should be versioned so cache invalidation is controlled

### Pillar 2: Artifact handoff

Goal:
- downstream agents read conclusions, not giant raw files

Practical implication:
- Orio is allowed to read raw data
- downstream agents should consume structured artifacts

This is one of the strongest and most correct principles in your whole architecture.

### Pillar 3: Vector retrieval

Goal:
- use semantic retrieval instead of stuffing all history into prompts

Future direction:
- ChromaDB or pgvector
- retrieve only the few most relevant successful examples

## 3.3 What this means for implementation

The architecture needs:
- `skill loader`
- `artifact schemas`
- retrieval-ready artifact metadata
- clear distinction between:
  - raw data
  - compressed artifact
  - retrieved examples

## 4. Category B: Solo AI Team Management Model

## 4.1 The four-layer hierarchy

Your proposed hierarchy is strong and should be preserved:

### Layer 1: Human CEO
- strategy
- priority
- final approval

### Layer 2: Lara / AI CEO
- routing
- decomposition
- orchestration

### Layer 3: Specialist agents
- Orio
- Lala
- Craft
- Sage
- Lumi
- Pixel

### Layer 4: Dumb scripts / adapters
- stable execution
- no hallucination
- pure automation

This is exactly the right way to avoid:
- role confusion
- agent overlap
- recursive chaos

## 4.2 Key operating rule

The most important management principle is:
- agents should not free-chat with each other endlessly

Instead:
- they should communicate through artifacts and constrained handoffs

That is operationally correct and token-efficient.

## 5. Category C: Quality Gates and Approval Model

## 5.1 Core rule

Never trust "AI says it is done".

Required control layers:
- peer review where useful
- approval queue for high-risk actions
- human final approval for external or irreversible actions

## 5.2 What should be approval-gated

High-priority approval categories:
- public posting
- core system modifications
- risky adapter behaviors
- business-critical ecommerce decisions

## 5.3 Self-modification boundary

The rule you gave is strong:
- self-modification may initially apply only to skill/prompt markdown
- not to core Python logic without sandbox/test/approval

This is a very important safety boundary and should stay.

## 6. Category D: Agent Skill Adoption Model

## 6.1 Lara

Desired core capabilities:
- planning with files
- acceptance-criteria enforcement
- retry gating when output quality is insufficient

This is a good direction because Lara should act as:
- planner
- supervisor
- validator

not merely router

## 6.2 Lumi

Desired core capabilities:
- brainstorming before implementation
- TDD-oriented thinking
- code simplification after implementation

This is strong because it fights:
- brittle code
- overgrown control flow
- AI-generated spaghetti

## 6.3 Pixel and Craft

Desired core capabilities:
- anti-generic visual taste
- visual QA
- stronger copy and presentation quality

Especially good:
- requiring Playwright-like visual validation for UI review

## 6.4 Review model

The multi-agent review direction is good:
- logic review
- safety review
- style review

This is stronger than asking one agent to do all dimensions at once.

## 7. Category E: External Skills and MCP Integration

## 7.1 Core rule

This is one of the most important boundaries:

> No external skill should touch core AITOS directly.

Everything must be:
- isolated
- wrapped
- typed
- error-contained

That means:
- adapters first
- direct third-party dependency exposure never

## 7.2 The three source categories are good

### Category A: Native Python tools

Examples:
- LlamaHub-style loaders
- LangChain community tools

Best tactic:
- extract core logic
- wrap locally
- avoid dragging full framework complexity into AITOS

### Category B: MCP servers

Best tactic:
- treat them as independent processes
- access via client boundary
- isolate crashes from main app

### Category C: R&D / high-risk scripts

Best tactic:
- treat as experimental
- re-implement carefully
- high risk label
- CEO approval required

This categorization is strong and worth preserving.

## 7.3 Standard adapter rules

Every adapter should define:
- Pydantic input
- Pydantic output
- timeout
- exception interception
- normalized error result
- risk level

This is one of the clearest implementation standards in your current planning set.

## 8. Category F: Trend Research and Source Strategy

## 8.1 Main principle

Do not let Orio become a raw data dump.

Orio should output:
- scored
- filtered
- structured research artifacts

## 8.2 Good research stack direction

Your suggested stack is reasonable:
- search APIs first
- RSS for stable feeds
- web-to-markdown tools second
- avoid expensive or unstable direct social scraping when possible

## 8.3 Orio scoring model

These three scores are especially strong:
- `topic_fit_score`
- `persona_fit_score`
- `source_trust_score`

These should absolutely remain in the future design.

## 9. Category G: Visual Feedback and Optimization Loop

## 9.1 Why this is valuable

This is not only a UX feature.
It is a system-learning channel.

The idea is:
- CEO provides image/video/screenshot
- system extracts insight
- system proposes optimization
- proposal enters approval queue

That is excellent because it lets:
- research
- UI review
- prompt refinement
- system evolution

all happen through a safe, reviewable pipeline

## 9.2 Best boundary you defined

The strongest safety rule here is:
- AI may propose system modifications
- AI may not directly rewrite core logic without approval and sandboxing

This rule should remain non-negotiable.

## 10. What Is Most Valuable In This Whole Set

The most valuable ideas here are:

1. artifact funneling instead of raw context passing
2. clear agent hierarchy
3. adapters as contamination barriers
4. approval queue as the system's legal and operational firewall
5. skill caching and memory compression
6. using multimodal inputs for optimization, not only content generation

## 11. What Still Needs Sharpening

These ideas are good, but still need formal consolidation into implementation specs.

Main missing pieces:

## 11.1 Normalized workflow state

You still need:
- `run`
- `task`
- `event`
- `artifact`
- `approval`

Without these, the architecture remains partially conceptual.

## 11.2 Skill cache lifecycle

You need to define:
- when cache is created
- what invalidates it
- how skill versioning works
- how model-specific cache keys are managed

## 11.3 Artifact taxonomy

You need a formal artifact list such as:
- `ResearchArtifact`
- `DraftArtifact`
- `VisualInsightArtifact`
- `ReviewArtifact`
- `PatchProposalArtifact`

## 11.4 Source/adapter registry

You need one place that records:
- adapter name
- source type
- risk level
- auth requirements
- allowed agents
- timeout
- fallback policy

## 12. Recommended Classification For Future Implementation

These ideas should eventually map into separate spec buckets:

### Bucket 1: Workflow state
- tasks
- events
- runs
- approvals
- artifacts

### Bucket 2: Skill/runtime
- skill loading
- skill cache
- prompt assembly
- model routing

### Bucket 3: External integration
- adapters
- MCP clients
- search/research tools
- browser/session tools

### Bucket 4: Optimization loop
- multimodal insight extraction
- patch proposal generation
- approval diff review

### Bucket 5: Safety and governance
- risk levels
- approval rules
- allowed self-modification scope
- backup/restore policy

## 13. Strategic Bottom Line

This new material does not change the overall direction.
It strengthens it.

What it reinforces is:
- AITOS should become a highly controlled, artifact-driven, Python-first operating system
- not a loose collection of talking agents
- not a giant prompt chain
- not an uncontrolled auto-runner

It also confirms that the next most important engineering step is still:
- formal workflow state and artifact structure

Because that is the foundation that all the other ideas depend on.
