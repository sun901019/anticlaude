# Figma Integration Status Review

Date: 2026-03-21
Scope: Current Figma integration status in AITOS, what is already implemented, what is still missing, and what it means for Claude-assisted frontend work.

## Executive Summary

Figma is connected at the backend integration layer.

The project already has:
- a real async Figma REST client
- a real adapter registered as active
- configuration support for `FIGMA_API_TOKEN`

The current integration is read-only and infrastructure-level.
It is not yet a full end-to-end "Claude reads Figma and automatically produces approved frontend output" workflow.

## Confirmed Implemented Pieces

### 1. Figma client exists

File:
- [src/integrations/figma_client.py](C:\Users\sun90\Anticlaude\src\integrations\figma_client.py)

Current supported operations:
- `get_file`
- `get_file_nodes`
- `get_comments`
- `get_file_images`
- `ping`

Observed characteristics:
- uses `X-Figma-Token`
- uses Figma REST API v1
- read-only behavior
- async `httpx` implementation

### 2. Figma adapter exists

File:
- [src/adapters/figma_adapter.py](C:\Users\sun90\Anticlaude\src\adapters\figma_adapter.py)

Current adapter behavior:
- adapter name: `figma_api`
- risk level: `medium`
- approval required: `False`
- allowed agents: `["pixel"]`

Supported actions:
- `ping`
- `get_file`
- `get_nodes`
- `get_comments`
- `get_images`

Important limitation:
- adapter is read-only
- no mutation/write-back flow exists

### 3. Registry wiring exists

File:
- [src/adapters/registry.py](C:\Users\sun90\Anticlaude\src\adapters\registry.py)

Current registry state:
- `figma_api` is marked `active`
- module path points to `src.adapters.figma_adapter`
- class name is `FigmaAdapter`

### 4. Config support exists

File:
- [src/config.py](C:\Users\sun90\Anticlaude\src\config.py)

Current config field:
- `figma_api_token: Optional[str]`

This means the system is structurally ready to authenticate against Figma if the token is present in `.env`.

## What This Means Right Now

## Backend readiness

Backend-side Figma access is already present.
If `FIGMA_API_TOKEN` is configured and valid, the system should be able to:
- verify connectivity
- fetch a Figma file
- fetch specific nodes
- fetch file comments
- fetch rendered node image URLs

## Claude frontend assistance readiness

Claude cannot yet be described as having a complete production-ready Figma-to-frontend pipeline.

Current state is better described as:
- Figma read access: yes
- adapter integration: yes
- automatic design ingestion into frontend workflow: partial
- end-to-end design-to-code flow: not yet complete

## Main Gaps Still Remaining

### 1. No dedicated productized Figma workflow

There is currently no clear user-facing workflow such as:
- select Figma file or node
- send node payload into a frontend generation pipeline
- produce structured design tokens
- generate implementation artifacts
- route through review/approval

### 2. No dedicated API route surfaced for Figma workflow

Based on current code search, Figma appears at the integration and adapter layer, but not as a clearly exposed business workflow route.

This means the integration exists technically, but not yet as a first-class operator-facing feature.

### 3. No dashboard UI for Figma operations

There is no visible Figma page/panel currently confirmed in `dashboard/` for:
- entering a file key
- selecting nodes
- previewing pulled design data
- sending a design extraction job into implementation

### 4. Agent access is currently narrow

The adapter currently allows:
- `pixel`

This is sensible for safety, but it also means the integration is not yet broadly wired into:
- `lara`
- `lumi`
- CEO-facing design workflow

### 5. No confirmed design-token extraction layer

The current adapter can retrieve raw Figma data and rendered images, but there is no confirmed module yet for:
- palette extraction
- typography extraction
- spacing/radius/shadow tokenization
- Tailwind token generation
- shadcn/ui mapping

### 6. No verified end-to-end tests yet

Sprint notes still indicated integration tests as pending around Figma/X/CDP.
So the integration is real, but test maturity still appears incomplete.

## Can Claude Directly Use Figma for Frontend Design?

Short answer:
- partially yes for reading design data
- not yet fully yes for a polished automatic frontend production workflow

More precise answer:
- Claude can be given Figma-derived data once the adapter is invoked
- the system can likely support design-aware frontend implementation
- but the repo does not yet show a complete, explicit, operator-friendly "Figma -> tokens -> React/Tailwind UI -> approval" pipeline

## Recommended Next Steps

### Priority 1: verify adapter in isolation

Add or complete direct tests for:
- token missing
- ping
- get_file
- get_nodes
- get_comments
- get_images
- failure handling

### Priority 2: define a Figma workflow contract

Create a documented workflow such as:
1. CEO or Pixel supplies `file_key` and `node_ids`
2. adapter fetches node data and image URLs
3. parser converts raw data to `DesignInsightArtifact`
4. Lumi uses artifact to generate frontend implementation
5. output goes to approval package

### Priority 3: add a token extraction layer

Recommended future module examples:
- `src/domains/media/design/token_extractor.py`
- `src/domains/media/design/figma_parser.py`
- `src/domains/media/design/tailwind_mapper.py`

Target outputs:
- `design_audit.md`
- `design_tokens.json`
- `tailwind-theme.ts`
- implementation brief for Claude/Lumi

### Priority 4: add operator-facing UI

Recommended future dashboard capability:
- Figma input form
- node selection
- preview of pulled screenshots
- design token preview
- "send to frontend implementation" action

### Priority 5: define approval and risk semantics

Even though Figma is read-only now, generated frontend output should still be routed through:
- review package
- approval decision
- implementation validation

## Final Assessment

Figma is already connected enough to count as a real integration.
It is not fake, not just planned, and not just documented.

However, it is still at the "adapter + backend capability" stage, not yet at the "fully operational design-to-frontend system" stage.

The best current description is:
- Figma backend integration: implemented
- Figma workflow productization: partial
- Figma-driven frontend automation: not fully completed yet
