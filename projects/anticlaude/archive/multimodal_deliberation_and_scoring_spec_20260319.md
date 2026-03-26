# AITOS Multimodal Deliberation and Scoring Spec 2026-03-19

## 1. Purpose

This document defines how AITOS should handle multimodal inputs and turn them into:
- structured insights
- multi-agent discussion
- scoring
- approval-ready recommendations for the CEO

It covers:
- image input
- video input
- text/web input
- the discussion flow across agents
- the scoring model
- the approval output shown to the CEO

This is a specification document.
It does not mean the full flow is already implemented.

## 2. Short Answer to the CEO Question

Yes:
- you should be able to upload images
- and later also upload videos
- then let the system extract key points and summarize them for you

Current practical status:
- image input is already partially supported in CEO chat
- video understanding is not yet a complete production workflow
- this spec defines how video should be handled next

## 3. System Goal

The target experience is:

1. CEO uploads an image, screenshot, PDF page image, or video
2. AITOS extracts the important signal
3. Multiple agents discuss the material from different roles
4. Sage or another scoring agent evaluates confidence and risk
5. Lara prepares a concise decision package
6. CEO only sees:
   - what matters
   - what the agents concluded
   - what needs approval

The CEO should not need to read the full raw material unless desired.

## 4. Supported Input Types

## 4.1 Image

Examples:
- product screenshots
- 1688 / Taobao pages
- Threads screenshots
- dashboard screenshots
- design reference images
- charts

Expected output:
- visual summary
- extracted facts
- pain points
- opportunities
- recommended next action

## 4.2 Video

Examples:
- YouTube video
- short-form social clip
- Loom recording
- product demo clip
- UX walkthrough
- market analysis clip

Expected output:
- transcript summary
- key frames
- timeline highlights
- major claims
- actionable insights
- scoring and recommendation

## 4.3 Text / URL / Markdown

Examples:
- article links
- notes
- transcripts
- reports
- scraped content

Expected output:
- structured research artifact
- discussion summary
- decision suggestion

## 5. Core Design Principle

The system must not let every agent read the full raw asset.

Instead:
- one frontline agent or adapter reads the raw material
- that raw material is converted into a compact artifact
- downstream agents discuss the compact artifact only

This keeps:
- token cost lower
- reasoning cleaner
- traceability higher

## 6. Recommended Workflow

## 6.1 Stage A: Input Ingestion

Primary owner:
- `Lara`

Responsibilities:
- accept CEO input
- classify the input type
- assign domain
- create a workflow run
- decide whether the input goes to:
  - Flow Lab
  - Media
  - Trading
  - System optimization

Expected output:
- `InputIntakeArtifact`

Suggested fields:
- `source_type`
- `source_path`
- `domain`
- `intent`
- `priority`
- `submitted_by`
- `submitted_at`

## 6.2 Stage B: Raw Extraction

Primary owner:
- `Orio`

Adapter support:
- image adapter
- video adapter
- transcript adapter
- web reader adapter

Responsibilities:
- read the raw asset
- extract only the key information
- normalize it into a compact artifact

For image input:
- identify entities
- identify pain points
- identify claims or offers
- identify specs, text, or visible metrics

For video input:
- extract frames
- transcribe audio
- summarize by timeline blocks
- isolate important moments
- detect claims, arguments, demonstrations, and problems

Expected output:
- `VisualInsightArtifact` for images
- `VideoInsightArtifact` for videos
- `ResearchArtifact` for text/url input

## 6.3 Stage C: Deliberation

Primary owner:
- `Lara`

Participants:
- `Orio`
- `Lala`
- `Craft`
- `Sage`
- optional `Lumi`
- optional `Pixel`

Discussion rule:
- no free-form endless chatting
- each role contributes one bounded response
- discussion runs for limited rounds only

Recommended rounds:
- Round 1: independent viewpoints
- Round 2: critique / contradiction / risk review
- Round 3: synthesis by Lara

Hard limits:
- maximum 3 rounds
- maximum 1 critique pass per specialist
- stop early if confidence is already high

## 6.4 Stage D: Scoring

Primary owner:
- `Sage`

Sage must score the artifact after discussion.

Core scoring dimensions:
- `signal_quality_score`
- `relevance_score`
- `actionability_score`
- `risk_score`
- `confidence_score`

Optional domain-specific scores:

For Flow Lab:
- `pain_point_strength`
- `market_fit_score`
- `conversion_potential`

For Media:
- `persona_fit_score`
- `discussion_potential`
- `hook_strength`
- `similarity_risk`

For System optimization:
- `implementation_value`
- `safety_risk`
- `maintenance_cost`

## 6.5 Stage E: CEO Decision Package

Primary owner:
- `Lara`

The CEO should not receive the full debate transcript first.

The default package shown to the CEO should be:
- `one-screen summary`
- `why this matters`
- `top 3 insights`
- `main risks`
- `recommended action`
- `confidence level`
- `approve / reject / defer`

Optional expandable sections:
- evidence
- artifact preview
- debate trace
- raw source link/file

## 7. Agent Role Definition

## 7.1 Lara

Role:
- orchestrator
- scope controller
- round controller
- approval gate manager
- final explainer to CEO

Lara should decide:
- who participates
- how many rounds are needed
- when to stop discussion
- what gets sent for approval

## 7.2 Orio

Role:
- raw material reader
- multimodal extractor
- evidence collector

Orio is the only role that should normally read the full raw input first.

## 7.3 Lala

Role:
- strategic interpretation
- workflow direction
- format and angle selection

Typical questions:
- is this worth doing
- what kind of response or content is best
- what is the strategic angle

## 7.4 Craft

Role:
- output framing
- message construction
- conversion-aware synthesis

Typical outputs:
- draft summary
- content angle
- hook candidates
- product positioning language

## 7.5 Sage

Role:
- scoring
- contradiction detection
- risk and confidence review

Sage should be the main balancing force against weak or overexcited conclusions.

## 7.6 Lumi

Role:
- system and engineering evaluation

Use when the input implies:
- implementation work
- architecture impact
- code-change proposals

## 7.7 Pixel

Role:
- design and visual interpretation

Use when the input is:
- UI reference
- landing page reference
- design screenshot
- visual system critique

## 8. Scoring Rubric

## 8.1 Base Rubric

All multimodal deliberation outputs should end with these fields:

- `summary`
- `top_insights`
- `recommended_action`
- `risk_notes`
- `confidence_score`
- `needs_human_approval`

Scoring scale:
- `0-3`: weak
- `4-6`: usable but uncertain
- `7-8`: strong
- `9-10`: high-confidence and actionable

## 8.2 Approval Trigger Rule

Automatic approval gate should trigger when any of these are true:
- `risk_score >= 7`
- `external publication involved`
- `system change proposed`
- `money or inventory decision involved`
- `high uncertainty but high impact`

## 9. Video-Specific Flow

## 9.1 What should happen when CEO uploads a video

Recommended processing flow:

1. save original file
2. extract metadata
3. split into key frames
4. transcribe audio
5. produce timeline summary
6. create `VideoInsightArtifact`
7. send artifact into deliberation flow
8. return CEO summary

## 9.2 What the CEO should see for videos

Default summary card:
- video title or source
- short summary
- 3 key takeaways
- timeline highlights
- recommended next action
- confidence

Optional expand:
- transcript
- key frames
- debate trace
- raw file preview

## 9.3 Important note

Video support should be treated as:
- `planned and desirable`
- not yet fully complete in the current project state

So the answer is:
- yes, this should be part of the target system
- but it still needs implementation work to become a stable feature

## 10. Artifact Types Recommended

Recommended artifact additions:
- `InputIntakeArtifact`
- `VisualInsightArtifact`
- `VideoInsightArtifact`
- `TranscriptArtifact`
- `DeliberationArtifact`
- `ScoringArtifact`
- `DecisionPackageArtifact`

These should later map to the workflow artifact taxonomy.

## 11. Suggested Stop Rules

To avoid waste and endless agent discussion:

- stop after 3 rounds maximum
- stop early if `confidence_score >= 8` and `risk_score <= 4`
- stop early if two independent agents agree and Sage confirms low risk
- escalate to CEO immediately if disagreement remains high after round 2

## 12. Future UI Implications

The dashboard should later support:
- image upload
- video upload
- artifact preview
- key frame preview
- transcript view
- debate trace panel
- scoring breakdown panel
- approval actions

## 13. Suggested Implementation Order

Recommended order:

1. formalize new artifact types
2. add image artifact normalization
3. add video ingestion pipeline
4. connect debate flow to workflow runtime
5. connect Sage scoring to approval gate
6. build CEO decision package UI

## 14. Final Verdict

The multimodal deliberation direction is valid and strongly aligned with AITOS.

Image-based understanding is already partially on the path.
Video-based understanding should absolutely be part of the future system.

The correct target is not:
- raw multimodal input directly shown to every agent

The correct target is:
- one extractor reads the source
- agents deliberate over compact artifacts
- Sage scores
- Lara synthesizes
- CEO approves only what matters
