# Ecommerce Product Selection System Plan

Date: 2026-03-14
Project: AntiClaude / Flow Lab
System Name: Ecommerce Product Selection SOP System
Method Source: Harry Logic

## Purpose

This document converts the current `Harry Logic` product-selection SOP into a system plan that fits the existing `Anticlaude` architecture.

The goal is not only to document how a human should evaluate products.

The goal is to make the SOP executable inside your current system through:

- backend data models
- scoring logic
- research workflows
- dashboard views
- AI role collaboration
- report outputs
- memory accumulation

---

## Core Strategic Principle

The system should not search for random products.

It should search for:

- demand patterns
- pain points
- weak competitor execution
- margin opportunities
- brand-fit opportunities

The operating philosophy remains:

> Do not search for products. Search for problems to solve.

For Flow Lab, this means the system should prioritize:

- desk comfort
- office relaxation
- workstation upgrades
- daily work-life improvement products

This positions the brand inside:

- `Problem Market`
- with a `Lifestyle Improvement` overlay

---

## Executive Assessment Of Current System

You already have the foundation for this product-selection system.

### Existing pieces already present

- Backend ecommerce routes:
  - `src/ecommerce/router.py`
- Frontend ecommerce page:
  - `dashboard/src/app/ecommerce/page.tsx`
- Existing data/storage direction:
  - SQLite-backed project structure
- Existing AI role framework:
  - `Ori`, `Lala`, `Craft`, `Lumi`, `Pixel`, `Sage`
- Existing AI Office direction:
  - event-driven agent work visibility
- Earlier ecommerce spec:
  - `_hub/ecommerce_engine_spec.md`

### What this means

You do **not** need a separate ecommerce app.

You should extend the current system into a more professional product-selection engine.

That means:

- keep current `Flow Lab` section
- extend schema
- extend research workflow
- extend scoring logic
- add a dedicated selection module
- generate research outputs and memory

---

## System Objective

Build a product-selection engine that can:

1. collect candidate products
2. classify market type
3. filter operational risk
4. validate demand
5. analyze competition
6. extract negative-review pain points
7. calculate true landed cost
8. evaluate margin and pricing range
9. assign product role
10. generate an overall viability score
11. produce a recommendation report
12. store decisions and learning for future reuse

---

## SOP To System Mapping

## 1. Market Type Identification

### Human SOP meaning

The user determines whether a category/product belongs to:

- demand market
- trend market
- problem market

### System module

Recommended module:

- `Market Classification Engine`

### Inputs

- product/category keywords
- social discussion patterns
- trend curve
- product intent notes

### Outputs

- `market_type`
- `market_confidence`
- `market_reasoning`

### Recommended enum

- `demand`
- `trend`
- `problem`
- `hybrid`

For Flow Lab, many strong candidates will likely be:

- `problem`
- or `hybrid(problem + demand)`

---

## 2. Product Pool Creation

### Human SOP meaning

Instead of evaluating a single product, build a 30-50 item product pool from multiple sources.

### System module

Recommended module:

- `Candidate Pool Builder`

### Data sources

- TikTok
- Instagram
- Xiaohongshu
- Threads
- Amazon Best Seller
- Shopee hot items
- Taobao trending
- internal keyword list

### Recommended output structure

Each candidate should contain at least:

- `candidate_id`
- `product_name`
- `source_platform`
- `source_url`
- `category`
- `keywords`
- `first_seen_at`
- `discovery_notes`

### Recommendation

Do not store only approved products.

Store the full pool so the system learns:

- what was considered
- what was rejected
- why it was rejected

---

## 3. Initial Product Filtering

### Human SOP meaning

Remove candidates with high operational risk.

### System module

Recommended module:

- `Operational Risk Filter`

### Filter dimensions

- fragile
- high return probability
- IP/brand infringement risk
- complex electronics risk
- high after-sales burden
- oversized shipping burden

### Output

- `risk_flags`
- `risk_score`
- `filter_decision`
- `filter_reason`

### Recommendation

Use this as an early gate before expensive research steps.

That keeps the system efficient and aligned with store operations.

---

## 4. Demand Validation

### Human SOP meaning

Check whether demand is real and durable.

### System module

Recommended module:

- `Demand Validation Engine`

### Inputs

- search interest
- marketplace sales indicators
- social discussion frequency
- keyword coverage

### Output

- `demand_score`
- `demand_signal_summary`
- `demand_stability`

### Important rule

The system should distinguish:

- stable demand
- trend spike
- weak/noisy demand

This is critical because your SOP explicitly warns against chasing short-term virality without underlying strength.

---

## 5. Competition Analysis

### Human SOP meaning

Assess how crowded and undifferentiated the market is.

### System module

Recommended module:

- `Competition Analyzer`

### Key variables

- competitor count
- price clustering
- price ladder existence
- review dominance
- listing quality
- differentiation patterns

### Output

- `competition_score`
- `price_ladder_health`
- `competitive_landscape_notes`

### Important logic

Healthy market signal:

- clear price ladder
- multiple differentiated offers

Unhealthy market signal:

- everyone at the same price
- feature parity
- obvious price war

---

## 6. Negative Review Analysis

### Human SOP meaning

Find product weaknesses and improvement opportunities by reading 1-star and 2-star reviews.

### System module

Recommended module:

- `Negative Review Analyzer`

### This is one of the highest-value modules in the whole system

Because it directly supports:

- product differentiation
- better offers
- copywriting angles
- product improvement

### Required output

- `pain_points`
- `frequency_by_pain_point`
- `improvement_opportunities`
- `review_examples_summary`

### Example output format

- noisy -> propose silent version
- too small -> propose large version
- hard to clean -> propose easy-clean version
- weak materials -> propose upgraded materials

### Recommendation

This module should feed both:

- product viability score
- future marketing angle generation

---

## 7. Full Cost Calculation

### Human SOP meaning

Calculate true cost, not just supplier price.

### System module

Recommended module:

- `Unit Economics Engine`

### Cost inputs

- product cost
- shipping cost
- packaging cost
- platform fee
- payment fee
- advertising cost
- return-rate buffer
- handling/ops buffer

### Outputs

- `landed_cost`
- `recommended_floor_price`
- `gross_profit`
- `gross_margin`
- `break_even_roas`

### Recommendation

Your current system should stop at neither inventory nor simple pricing suggestions.

It should include unit-economics logic that supports:

- selection
- portfolio role assignment
- pricing decisions

---

## 8. Pricing Strategy

### Human SOP meaning

Selling price should usually be at least:

- `cost x 2.5`
- preferred `cost x 3`

### System module

Recommended module:

- `Pricing Strategy Engine`

### Outputs

- `min_viable_price`
- `target_price`
- `recommended_price_band`
- `margin_quality`

### Recommendation

Do not store only one recommended price.

Store:

- floor price
- target price
- stretch price

That allows you to reason better about:

- traffic product suitability
- hero product suitability
- promo flexibility

---

## 9. Product Role Assignment

### Human SOP meaning

Each product should play one role in the store:

- traffic product
- profit product
- hero product

### System module

Recommended module:

- `Portfolio Role Assigner`

### Output

- `recommended_role`
- `role_confidence`
- `role_reasoning`

### Store portfolio strategy

Recommended portfolio target:

- traffic: 40%
- profit: 40%
- hero: 20%

### Important note

This means product selection is not just single-product scoring.

It is also **store architecture design**.

That is a major professional upgrade compared with simple product research.

---

## 10. Product Scoring Model

### Human SOP meaning

Score products based on:

- demand
- competition
- profit
- pain point improvement
- brand fit

### System module

Recommended module:

- `Selection Scoring Engine`

### Suggested scoring model

Base formula from your SOP:

`score = demand * 2 + profit * 2 + pain_points + competition + brand_fit`

### Recommended system output

- `score_total`
- `score_breakdown`
- `viability_band`

### Recommended viability bands

- `40-50`: strong candidate
- `35-39`: viable candidate
- `30-34`: watchlist candidate
- `<30`: reject for now

### Recommendation

Keep score breakdown transparent.

That makes the system auditable and more useful for both human operators and AI agents.

---

## Recommended Database Design

You already have ecommerce-related tables. Do not replace them blindly.

Extend the system with a dedicated selection layer.

## Recommended new tables

### 1. `ecommerce_selection_candidates`

Purpose:

- full candidate pool

Suggested fields:

- `id`
- `candidate_id`
- `product_name`
- `market_type`
- `source_platform`
- `source_url`
- `category`
- `keywords_json`
- `risk_flags_json`
- `status`
- `created_at`
- `updated_at`

### 2. `ecommerce_selection_analyses`

Purpose:

- one analysis result per candidate per cycle

Suggested fields:

- `id`
- `candidate_id`
- `analysis_date`
- `demand_score`
- `competition_score`
- `profit_score`
- `pain_point_score`
- `brand_fit_score`
- `score_total`
- `score_breakdown_json`
- `market_metrics_json`
- `competition_metrics_json`
- `negative_reviews_json`
- `financials_json`
- `recommended_role`
- `decision_status`
- `reasoning`

### 3. `ecommerce_selection_reports`

Purpose:

- generated human-readable output

Suggested fields:

- `id`
- `analysis_id`
- `report_title`
- `report_markdown`
- `summary_json`
- `created_by_agent`
- `created_at`

### 4. `ecommerce_selection_lessons`

Purpose:

- memory and learning

Suggested fields:

- `id`
- `theme`
- `lesson_type`
- `lesson_text`
- `source_analysis_ids_json`
- `confidence`
- `created_at`

---

## Recommended API Design

Do not replace existing ecommerce routes. Extend them.

## Suggested route group

Prefix:

- `/api/ecommerce/selection`

### Core endpoints

- `POST /api/ecommerce/selection/candidates`
  - add candidate pool items
- `GET /api/ecommerce/selection/candidates`
  - list/search candidates
- `POST /api/ecommerce/selection/analyze/{candidate_id}`
  - run full SOP analysis
- `GET /api/ecommerce/selection/analysis/{candidate_id}`
  - fetch latest analysis
- `GET /api/ecommerce/selection/reports`
  - list reports
- `GET /api/ecommerce/selection/report/{analysis_id}`
  - fetch generated report
- `POST /api/ecommerce/selection/role-assign/{candidate_id}`
  - compute recommended product role
- `POST /api/ecommerce/selection/shortlist`
  - produce shortlist from score threshold

### Future endpoints

- `POST /api/ecommerce/selection/import/social`
- `POST /api/ecommerce/selection/import/marketplace`
- `POST /api/ecommerce/selection/reviews/scrape`
- `GET /api/ecommerce/selection/portfolio`
- `GET /api/ecommerce/selection/lessons`

---

## Recommended Dashboard Information Architecture

Your current ecommerce page should evolve into a multi-layer operations workspace.

## Recommended tabs

### 1. Overview

Shows:

- candidate count
- shortlisted count
- approved count
- market mix
- role mix
- average score

### 2. Candidate Pool

Shows:

- full product pool
- source platform
- category
- market type
- status
- quick filter flags

### 3. Analysis

Shows:

- selected candidate
- score breakdown
- demand indicators
- competition indicators
- pain point opportunities
- financial summary

### 4. Negative Reviews

Shows:

- grouped complaints
- frequency
- opportunity proposals
- improvement angles

### 5. Portfolio Roles

Shows:

- traffic/profit/hero distribution
- gaps in current assortment
- recommended next product type

### 6. Reports

Shows:

- generated product research reports
- shortlisted opportunities
- exportable markdown summaries

### 7. Memory / Lessons

Shows:

- repeated rejection reasons
- repeated winning patterns
- brand-fit patterns
- margin guardrails

---

## Recommended AI Role Assignment

To fit your existing agent system, this is the most natural role map.

### Ori

Responsibility:

- discovery
- source scanning
- candidate pool building
- early market signal gathering

### Lala

Responsibility:

- market framing
- category selection
- portfolio strategy
- brand alignment judgment

### Sage

Responsibility:

- scoring
- competition analysis
- unit economics
- decision audit

### Craft

Responsibility:

- report writing
- insight formatting
- product brief generation
- recommendation summaries

### Pixel

Responsibility:

- dashboard presentation design
- visual ranking logic
- insight readability

### Lumi

Responsibility:

- backend implementation
- schema design
- route integration
- automation wiring

This role split is important because it makes the product-selection system compatible with your wider AI Office concept.

---

## Memory And Learning Design

This system should not only generate one-off analyses.

It should accumulate selection intelligence over time.

## Memory layers

### Layer 1. Raw analysis memory

Store:

- candidate record
- analysis record
- report record

### Layer 2. Pattern memory

Extract recurring patterns like:

- products rejected due to low margin
- categories with strong pain-point opportunities
- repeated customer complaints across suppliers
- market types that fit Flow Lab best

### Layer 3. Strategy memory

Create reusable rules such as:

- avoid electronics with complex after-sales
- prioritize ergonomic desk upgrades with repeatable pain points
- reject categories without price ladder differentiation

## Recommended output location

- database for structured records
- `projects/anticlaude/` or `outputs/` for periodic markdown summaries

Recommended periodic report:

- `outputs/ecommerce_memory/product_selection_summary_YYYY-MM-DD.md`

---

## Professional Optimization Recommendations

### 1. Add a reject log, not just a shortlist

Beginners often only save winners.

That loses a lot of intelligence.

You should save:

- rejected candidates
- rejection reason
- rejection pattern

That will make the system more useful over time.

### 2. Treat role assignment as portfolio design, not tagging

`Traffic / Profit / Hero` should influence:

- price expectations
- margin thresholds
- content strategy
- ad strategy
- homepage emphasis

### 3. Add a confidence field to all AI-generated decisions

For example:

- market classification confidence
- review clustering confidence
- role assignment confidence
- final recommendation confidence

This makes the system more professional and easier to audit.

### 4. Preserve raw evidence where possible

For important analyses, keep:

- source links
- example reviews
- price screenshots or references
- search/trend snapshots

Without evidence, the system risks becoming too abstract.

### 5. Make the scoring engine transparent

Never return only:

- `final_score = 38`

Always return:

- sub-scores
- reason
- threshold interpretation

That is critical for operator trust.

### 6. Separate "candidate viability" from "launch readiness"

A product can be a good candidate but not ready for launch.

Suggested dual status:

- `selection_status`
- `launch_status`

This is a more mature operating model.

---

## Recommended Implementation Order

### Phase 1. Schema And Contract

Build first:

- table design
- pydantic schemas
- API contract doc
- score breakdown structure

### Phase 2. Candidate Pool System

Build:

- candidate CRUD
- source tracking
- filtering

### Phase 3. Core Analysis Engine

Build:

- market classification
- demand validation
- competition analysis
- full cost calculation
- role assignment
- final scoring

### Phase 4. Negative Review Intelligence

Build:

- review ingestion
- pain point clustering
- improvement opportunity generator

### Phase 5. Dashboard Productization

Build:

- candidate pool tab
- analysis detail tab
- portfolio role tab
- memory/lessons tab

### Phase 6. Memory And Reports

Build:

- report generation
- recurring lessons
- periodic summaries

### Phase 7. AI Office Integration

Build:

- show selection tasks in AI Office
- show role handoffs
- show created artifacts

---

## Acceptance Criteria

The system should be considered successful only if it can:

1. ingest a 30-50 item product pool
2. reject risky candidates early
3. score candidates transparently
4. classify candidate role into traffic/profit/hero
5. generate a readable selection report
6. store both winners and rejected candidates
7. accumulate learning across analysis cycles
8. support Flow Lab brand direction rather than generic ecommerce logic

---

## Final Recommendation

You should position this system as:

`Flow Lab Product Intelligence System`

not just:

`product selection tool`

Because what you are really building is:

- market intelligence
- product opportunity detection
- portfolio design
- margin discipline
- memory accumulation

That is much more valuable and much more defensible.
