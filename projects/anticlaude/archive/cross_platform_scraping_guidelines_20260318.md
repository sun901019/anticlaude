# Cross-Platform Scraping Guidelines 2026-03-18

## 1. Purpose

This document records the operating guidelines for cross-platform scraping inside AITOS.

The goal is:
- collect trend and market signals safely
- reduce technical detection risk
- protect the CEO's personal brand accounts
- keep research workflows legally and operationally bounded

This is a planning and safety document.
It is not an instruction to bypass platform protections unlawfully.

## 2. Technical Operating Principles

## 2.1 Header camouflage

Rule:
- requests should include a realistic `User-Agent`

Why:
- many platforms block obviously automated or empty-header requests immediately

Practical meaning:
- do not send bare default library requests
- use stable browser-like request headers where lawful and appropriate

## 2.2 Randomized pacing

Rule:
- never scrape with rigid fixed intervals

Why:
- fixed timing is a common automation signature

Practical meaning:
- use randomized delays between actions
- avoid bursty loops without pause control

## 2.3 Avoid logged-in scraping by default

Rule:
- if public data is enough, do not use a logged-in personal account

Why:
- logged-in scraping links automation risk to a real identity/account

Practical meaning:
- prefer public, anonymous, low-risk collection paths
- do not attach research automation to your main social account

## 3. Platform Risk Profile

## 3.1 Dcard

Risk:
- relatively lower technical friction

Useful role:
- trend discovery
- title harvesting
- topic clustering

Constraint:
- still keep frequency conservative
- still treat access policy seriously

## 3.2 Shopee

Risk:
- very high

Observed issue:
- complex request protection and anti-bot behavior

Guidance:
- do not force a brittle direct-request strategy
- treat it as a high-friction source
- if later needed, use safer, reviewed adapter patterns

## 3.3 Threads / Instagram / Facebook

Risk:
- high

Why:
- these platforms protect user graph and behavior aggressively
- repeated scraping/search behavior can create account risk

Guidance:
- never tie scraping automation to the main publishing account
- isolate research behavior from brand/personal publishing identity

## 4. Brand and Account Safety Rules

## 4.1 Account isolation

Rule:
- scraping and publishing must be separated

Practical meaning:
- research collection should never depend on the CEO's main Threads account
- publishing identity should remain operationally clean

## 4.2 Only collect low-risk public data

Allowed target types:
- public titles
- public trend signals
- public prices
- public product descriptions
- public post-level themes

Do not target:
- private messages
- personal data
- private profiles
- CAPTCHA bypass workflows

## 4.3 Stop on warning signals

Critical warnings:
- `403`
- `429`
- repeated forced login or challenge pages

Required response:
- stop immediately
- cool down
- inspect frequency and routing
- do not brute-force retries

## 5. Legal and Ethical Constraints

## 5.1 Copyright

Rule:
- collected material should be used as inspiration, signal, or structured input
- do not republish source text verbatim as your own

## 5.2 robots.txt awareness

Rule:
- check the target site's `robots.txt` and access expectations

Why:
- this is part of baseline operational hygiene

## 5.3 Avoid unlawful or abusive collection behavior

Rule:
- do not design the system around defeating access controls or extracting protected personal data

## 6. AITOS-Specific Design Recommendations

## 6.1 Separate research adapters from publishing adapters

Recommended future split:
- `research adapters`
- `publishing adapters`

Why:
- they have different risk profiles
- they should not share credentials or identities

## 6.2 Add risk level to every external source

Suggested source risk classes:
- `low`
- `medium`
- `high`
- `manual_only`

Example:
- Dcard: `low-medium`
- Shopee: `high`
- Threads/IG/FB: `manual_only` or `high`

## 6.3 Human approval for high-risk sources

For high-risk platforms:
- require manual enablement
- do not include them in unattended workflows by default

## 6.4 Artifact-only downstream flow

Recommended pattern:
- scraping result becomes a compact artifact
- downstream agents only consume the cleaned artifact
- they do not directly re-hit the source platform

This reduces:
- repeated platform contact
- token waste
- system complexity

## 7. Risk Assessment: Dcard Titles -> Threads Draft Workflow

Requested question:
- what is the easiest technical failure point in the flow
- how should it be designed to keep the Threads account safest

## 7.1 Most likely technical failure point

The easiest failure point is not actually writing the Threads draft.

The riskiest and easiest failure point is:
- unstable or over-aggressive upstream collection behavior

More specifically:
- scraping frequency too high
- poor request hygiene
- building the workflow around live repeated fetching instead of cached artifacts
- mixing collection identity with publishing identity

If those fail:
- research source access gets blocked
- or worse, social account reputation is indirectly affected if identities/tools overlap

## 7.2 Safest architecture for this workflow

Best design:

1. Dcard collection is done by a research-only adapter
2. only public titles and minimal metadata are extracted
3. results are normalized into a local artifact
4. Orio clusters titles into themes
5. Lala selects topics that fit your persona
6. Craft writes Threads draft from the artifact
7. publishing is handled separately and only after approval

This keeps the Threads account safe because:
- the publishing account never participates in scraping
- the writing step uses local artifacts, not live scraping
- the final post is transformed commentary, not copied source material

## 7.3 Additional safety rules for this workflow

Use:
- low-frequency collection windows
- deduplicated topic extraction
- cached artifacts
- human review before publishing

Do not use:
- your main Threads login in the collection pipeline
- automated cross-platform engagement loops tied to scraping identity
- direct copy-paste from Dcard into Threads

## 8. Recommended AITOS Role Mapping

### Orio

Responsibilities:
- collect public titles safely
- cluster themes
- identify discussion-worthy signals
- avoid risky source behavior

### Lala

Responsibilities:
- filter for persona fit
- remove off-brand or low-value topics
- avoid topic dilution

### Craft

Responsibilities:
- transform trend signals into original commentary
- avoid copying
- write for reply-worthy engagement

### Sage

Responsibilities:
- review trust/risk of source usage
- check similarity and originality risk
- evaluate whether a topic is worth publishing

## 9. Future Implementation Guidelines

Recommended future module placement:
- `src/social/`
- `src/research/`
- or future domain-based placement under `src/domains/media/`

Suggested modules:
- `dcard_client.py`
- `trend_normalizer.py`
- `topic_clusterer.py`
- `threads_draft_pipeline.py`

## 10. Bottom Line

The safest way to use cross-platform scraping in AITOS is:
- public-data only
- low-frequency
- identity-isolated
- artifact-first
- human-reviewed before publishing

For the specific `Dcard -> Threads draft` flow:
- the biggest failure risk is upstream collection design
- the biggest account-safety rule is to keep scraping and publishing completely separated
