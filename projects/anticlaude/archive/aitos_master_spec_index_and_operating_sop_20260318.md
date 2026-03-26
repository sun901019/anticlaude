# AITOS Master Spec Index and Operating SOP 2026-03-18

## 1. Purpose

This document gives you one consolidated view of:
- what AITOS is becoming
- how the operating flow should work
- what sources the system should collect from
- what scraping risk exists
- what should reach the CEO for approval
- what daily reports should exist
- what you can expect once the system is fully implemented

This is the bridge between:
- vision
- specs
- daily operating reality

## 2. What AITOS Is Becoming

AITOS is becoming:
- a `Python-first AI operating system`
- with `Next.js` as the CEO command center
- `FastAPI` as the control plane
- `file + DB memory fabric` as the long-form memory and artifact layer
- `workflow runtime` as the future state engine for approvals, retries, checkpoints, and multi-agent collaboration

Its business domains are becoming:
- `Flow Lab`
- `Media`
- `Trading` later

Its operational mode is:
- research
- analyze
- draft
- review
- approve
- publish or execute
- report

## 3. What You Will Eventually Be Able To Do

If the system is completed in the direction we discussed, your daily experience should become:

### Morning

You open the dashboard and see:
- what the system researched overnight
- what drafts were produced
- what topics are worth posting
- what ecommerce items are worth reviewing
- what is blocked or waiting
- what requires your approval

### During the day

You can:
- review artifacts
- approve or reject actions
- request fast answers or team analysis
- inspect why the system made a recommendation

### Evening / night

The system can:
- continue safe autonomous research
- compress the day into reports
- prepare tomorrow's suggested actions

So yes:
- daily morning reports are part of the target system
- evening/night summaries are also part of the target system
- approval-required items should be surfaced to you, not hidden in logs

## 4. Your Core Operating Model As CEO

You are not meant to be the manual operator.
You are meant to be:
- the architecture owner
- the final reviewer on high-impact decisions
- the person who approves, rejects, or redirects

So the target operating model is:

### AI agents do

- trend collection
- topic clustering
- product analysis
- draft generation
- initial scoring
- structured recommendations

### You do

- approve content or execution
- reject weak outputs
- refine direction
- decide on sensitive actions

## 5. What Sources The System Should Crawl / Read

Based on everything discussed so far, the source map should look like this:

## 5.1 Low to medium risk research sources

These are the best early-stage research sources:
- RSS feeds
- Google/search APIs
- Serper-like search results
- public web articles
- public GitHub repositories
- Dcard public titles and public posts where access is reasonable
- public ecommerce pages where legal/technical risk is acceptable

These are good for:
- Orio research
- Media topic discovery
- Flow Lab competitor/product signal collection

## 5.2 Higher-risk sources

These require more caution:
- Shopee
- Threads
- Instagram
- Facebook
- logged-in platform views
- anti-bot protected ecommerce pages

These should not be default unattended sources.

## 5.3 Special-case sources

These are useful but should be designed differently:
- 1688 / Taobao

Best initial strategy:
- screenshot-based visual workflow

Why:
- much lower implementation risk
- avoids anti-bot complexity initially
- still gives business value

## 6. Where The System Is Likely Crawling From Today

From the current repo structure, the practical source families already present or implied are:
- RSS
- Serper / web search
- Hacker News
- Perplexity-related scraping/research
- Threads metrics collection
- ecommerce/product DB and internal analysis

Current relevant modules include:
- [src/scrapers](C:/Users/sun90/Anticlaude/src/scrapers)
- [src/tracker](C:/Users/sun90/Anticlaude/src/tracker)
- [src/pipeline.py](C:/Users/sun90/Anticlaude/src/pipeline.py)
- [src/agents/night_shift.py](C:/Users/sun90/Anticlaude/src/agents/night_shift.py)

So the current system is already more web/research aware than a simple dashboard.
It is just not yet fully normalized into a domain-by-domain source registry.

## 7. Will You Get Blacklisted Or Shadow-Limited?

The honest answer is:
- yes, this can happen if scraping is careless
- no, it does not have to happen if the system is designed properly

The main risk is not "AI exists".
The risk is:
- how the system accesses platforms
- what identity it uses
- how often it hits them
- whether scraping and publishing are mixed together

## 7.1 Biggest blacklisting/shadow-risk causes

High-risk mistakes:
- using your real publishing account in scraping workflows
- frequent automated searching on social platforms
- logged-in scraping using the same account you post from
- aggressive loops with fixed intervals
- not stopping after 403/429 signals

## 7.2 Safest design rule

The safest rule is:

`research identity must be completely separated from publishing identity`

Meaning:
- research adapters should not depend on your main Threads account
- scraping should use public or isolated access paths where possible
- content publishing should happen as a separate approved action

## 7.3 Platform risk summary

Lowest practical risk:
- RSS
- public article scraping
- search APIs

Medium risk:
- Dcard public research
- public ecommerce listing/title extraction in moderation

High risk:
- Shopee
- Threads / IG / FB direct scraping
- any logged-in automation tied to your main identity

## 8. What Reports You Should Eventually Receive

You asked whether you should be able to see reports every morning and evening.

Answer:
- yes, that should be part of the operating system

Recommended report set:

## 8.1 Morning Report

Purpose:
- tell you what happened overnight
- tell you what needs your attention

Should include:
- top content topics
- draft status
- review queue summary
- Flow Lab product analysis summary
- blocked tasks
- system health
- approvals waiting

## 8.2 Evening Report

Purpose:
- summarize what was done during the day
- prepare context for the next morning

Should include:
- what content was created
- what was approved/rejected
- what system actions completed
- what remains pending

## 8.3 Night Shift Summary

Purpose:
- autonomous task summary
- workflow completion status
- recommendations for tomorrow

You already have the early shape of this in the current repo.

## 9. Will You See What Each Agent Did In The Middle?

That is part of the target system, yes.

But today it is only partially present.

Target state:
- you should see the workflow timeline
- node by node
- with artifacts and summaries
- and know who did what

The future visibility model should include:

### For each task/run

- who started it
- which agent worked on it
- what artifact they produced
- what confidence/risk they assigned
- whether it is waiting for approval
- whether it failed and why

This should surface in:
- AI Office
- Review Queue
- CEO Console for deeper cases

## 10. What Must Be Sent To You For Approval

Not everything should require your approval.
Only high-impact or risky actions should.

Recommended approval-required categories:

### Content

- final Threads post publication
- any brand-sensitive statement
- any controversial opinion piece

### Flow Lab

- promotion of a candidate into active product focus
- final Shopee-ready listing copy if you want strict approval
- any irreversible operational change

### External actions

- publishing to X / Threads
- deletion of published content
- high-risk browser-driven actions

### Future trading domain

- any research conclusion that could be interpreted as actionable trading output

## 11. What Does "I Remember We Discussed This" Translate To In Practice?

What we discussed becomes real when the system has these five primitives:

1. `task`
2. `event`
3. `artifact`
4. `approval`
5. `run`

Without these, the ideas exist only in documents.

With these, the system can actually:
- tell you what happened
- show intermediate steps
- pause for approval
- resume later
- generate daily reports

That is why the most important future implementation layer is the workflow/state skeleton.

## 12. Current Reality vs Target Reality

## Current reality

You already have:
- dashboard surfaces
- chat
- night shift
- review queue
- agent status
- reports
- file-based handoff
- scheduled jobs

But you do not fully have:
- normalized workflow state
- complete artifact lineage
- full checkpoint/resume
- consistent approval routing for all high-value operations
- a clean source registry with risk levels

## Target reality

You will have:
- every important task tracked
- every artifact linked to a task
- every approval surfaced to you
- every day summarized into morning/evening reports
- every high-risk action gated
- every agent's work visible as part of a workflow trace

## 13. Recommended SOP Structure

If you later want to formalize operations, your SOP should look like this:

## SOP 1: Research ingestion

- which sources are allowed
- which are public-only
- what frequency rules apply
- when to stop

## SOP 2: Topic and product analysis

- how Orio collects
- how Lala filters
- how Sage scores
- what gets saved as artifact

## SOP 3: Draft generation

- what Craft receives
- what output files are produced
- what metadata is stored

## SOP 4: Approval flow

- what must be approved
- what can auto-complete
- what the CEO sees

## SOP 5: Reporting

- morning report contents
- evening summary contents
- night shift summary contents

## SOP 6: Risk and platform protection

- source risk levels
- account isolation
- stop conditions
- legal boundaries

## 14. Recommended Immediate Planning Directions

If you are still staying in planning mode, the most useful next planning topics are:

1. Workflow schema
- run/task/event/artifact/approval

2. Source registry
- what source
- what purpose
- what risk level
- what collection method

3. Approval matrix
- which actions need CEO approval
- which actions can auto-complete

4. Report matrix
- what should appear morning vs evening vs night shift

5. Artifact policy
- what gets saved
- where
- how long
- what metadata is attached

## 15. Final Bottom Line

The system direction you want is achievable.

The end state you are describing is:
- yes, the system researches for you
- yes, it generates daily reports
- yes, it shows you intermediate work
- yes, it routes approvals to you
- yes, it can become safer if scraping and publishing are separated properly

The main thing that still needs to be formalized is:
- the workflow/state skeleton that turns all these ideas into an actual operating model
