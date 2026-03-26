# CoinCat Planning and Isolation Strategy 2026-03-20

## 1. Purpose

This document plans the future CoinCat system based on:
- `CoinCat_FullAuto_v1.md`
- `coincat_strategy_system_blueprint.md`
- `CoinCat_Ultimate_Master_System.md`

This is planning only.
It must **not** be integrated into the active AITOS runtime yet.

## 2. Short Conclusion

CoinCat should be treated as:
- a future trading research and execution system
- high-risk
- technically adjacent to AITOS
- but operationally separate from the current Media + Flow Lab system

My recommendation is:
- `plan it now`
- `do not integrate it into the active production path yet`
- `keep it isolated as its own bounded context, and possibly its own repo/service later`

## 3. What CoinCat Actually Is

From the three documents, CoinCat is not just:
- a single strategy
- a few indicators
- a trading bot script

It is aiming to become:
- a complete derivatives trading operating system
- with market data ingestion
- derivatives / OI / funding interpretation
- multi-scenario strategy logic
- signal generation
- risk control
- paper trading
- live execution
- reporting
- AI-assisted analysis and optimization

This is much larger than a normal "trading feature".

## 4. Why It Should Not Be Mixed Into Current AITOS Yet

## 4.1 Risk class is much higher

Current AITOS core areas:
- Media
- Flow Lab
- AI Office
- approval and artifacts

CoinCat adds:
- exchange credentials
- real money risk
- latency-sensitive logic
- data integrity requirements
- execution failure risk
- regulatory and operational risk

That makes it fundamentally different from content and ecommerce workflows.

## 4.2 Runtime shape is different

Current AITOS shape is mostly:
- scheduled workflows
- artifact generation
- approval queues
- draft/report output

CoinCat needs:
- high-frequency or near-real-time data handling
- feature pipelines
- scenario scoring
- position tracking
- execution engine
- risk engine
- backtesting / paper trading / live switching

This is closer to a trading platform than a normal agent workflow.

## 4.3 Failure cost is different

If Media fails:
- bad draft
- lost time

If Flow Lab fails:
- bad recommendation
- wasted review time

If CoinCat fails:
- bad trade
- direct financial loss
- wrong exposure
- uncontrolled order placement

So the system boundary must be stricter.

## 5. Recommended Positioning

CoinCat should be defined as:

`A future independent trading domain and possibly an independent service that can later plug into AITOS through reports, approval, and strategy review surfaces.`

In other words:
- AITOS can eventually supervise CoinCat
- but CoinCat should not initially be implemented as just another small module under the existing active business flows

## 6. Recommended Isolation Strategy

## 6.1 Current phase: planning only

For now:
- keep CoinCat documents under `projects/anticlaude/`
- do not wire CoinCat into `src/api/main.py`
- do not add exchange secrets into current active env flow
- do not attach CoinCat to active schedulers
- do not let CoinCat share production approval semantics with Media/Flow Lab yet

## 6.2 Future code boundary

Best option later:
- either separate repo
- or separate bounded context under something like:

```text
src/domains/trading/coincat/
```

Recommended internal structure:

```text
src/domains/trading/coincat/
├── data/
│   ├── fetchers/
│   ├── normalizers/
│   └── storage/
├── features/
├── structure/
├── chip/
├── scenarios/
├── signals/
├── risk/
├── execution/
├── papertrade/
├── backtest/
├── reporting/
├── models/
└── orchestrator/
```

## 6.3 Separate infrastructure

CoinCat should later have its own:
- env vars
- exchange credentials
- DB tables or separate DB
- logs
- scheduler
- report outputs
- risk limits

Strong recommendation:
- separate SQLite/Postgres schema
- separate `.env` namespace
- separate report directory

## 7. System Modules Implied by the Blueprint

The docs consistently point to these engines:

1. `Data Fetcher`
2. `Feature Engine`
3. `Structure Engine`
4. `Chip Engine`
5. `Scenario Engine`
6. `Signal Engine`
7. `Risk Engine`
8. `Execution Engine`
9. `Logger / Position / Reports`
10. `Backtest / Paper Trade / Live Mode`

That is a coherent architecture.

The good news:
- the architecture direction is strong
- the system is decomposable
- it fits a domain-driven design approach

The caution:
- this is a large engineering scope
- not a quick feature branch

## 8. Recommended Delivery Phases

## Phase 0: Planning Only

Goal:
- no runtime integration
- finalize domain model
- finalize data schema
- finalize execution safety policy

Outputs:
- architecture docs
- source mapping
- feature dictionary
- scenario taxonomy
- risk policy draft

## Phase 1: Research-Only System

Goal:
- no trading
- no paper orders
- no live orders

Capabilities:
- pull market + derivatives data
- compute features
- classify scenarios
- produce LONG / SHORT / HOLD research suggestions
- save reports

This should be the first real implementation phase.

## Phase 2: Backtest + Replay

Goal:
- no live execution yet

Capabilities:
- replay historical candles
- replay derived signals
- evaluate scenarios
- measure strategy hit rate, drawdown, expectancy, win/loss profile

This phase is mandatory before any paper trading.

## Phase 3: Paper Trade

Goal:
- simulated execution only

Capabilities:
- position lifecycle simulation
- stop loss / take profit
- partial exits
- account balance simulation
- trade journal

This is the earliest point where "automation" is meaningful.

## Phase 4: Human-Approved Live Assist

Goal:
- still not fully autonomous

Capabilities:
- signal generated automatically
- execution still requires approval
- orders only placed after explicit human confirmation

This should come before full-auto live mode.

## Phase 5: Controlled Full Auto

Goal:
- only after strong paper-trade and human-approved live history

Requirements:
- tight risk caps
- strict kill switch
- exchange health checks
- latency and retry policy
- position reconciliation
- alerting
- incident fallback

## 9. What Can Be Optimized Already at the Planning Stage

## 9.1 Reduce scope aggressively

Your docs are ambitious.
That is good for vision, but too broad for first implementation.

The first optimization is:
- reduce v1 to the smallest useful research core

Recommended true v1:
- one exchange first
- one symbol or a tiny symbol set
- one time-frame stack
- only 3 scenarios
- no live execution
- research + paper-trade only

## 9.2 Separate research from execution

Do not build:
- signal engine
- risk engine
- execution engine

all at once.

Build in order:
- data
- features
- structure/scenario
- report
- backtest
- paper trade
- live execution last

## 9.3 Avoid TradingView dependency lock-in

The docs mention replacing manual TradingView reading with your own logic.

That is good.

Planning recommendation:
- define structure logic in code-native terms
- not in screenshot-driven or indicator-platform-specific terms

Examples:
- breakout definition
- compression definition
- OI expansion definition
- funding heat definition
- liquidation pressure proxy

These should be formalized as code-level rules.

## 9.4 Formalize risk policy before execution

Before live execution exists, define:
- max daily loss
- max open positions
- max exposure per symbol
- max leverage
- kill-switch conditions
- data gap fallback
- exchange API failure behavior

This should exist before "Execution Engine" is built.

## 9.5 Keep AI advisory, not sovereign

Given your current vision, AI should initially help with:
- scenario interpretation
- anomaly explanation
- report generation
- post-trade review
- strategy comparison

AI should not initially be the sole controller of:
- live entry
- position sizing
- stop movement
- leverage changes

Those should remain deterministic first.

## 10. Where CoinCat Can Reuse AITOS Concepts Later

CoinCat should not be integrated now.
But later it can reuse some AITOS concepts:

- `workflow runs`
- `artifacts`
- `approval gates`
- `daily / nightly reports`
- `review inbox`
- `AI CEO summary packaging`

Good reuse candidates:
- workflow primitives
- artifact logging
- approval surfaces
- office-style status visibility

Bad reuse candidates:
- current Media/Flow Lab DB tables
- current scheduling assumptions
- current content-agent assumptions

## 11. Recommended Future Deliverables

When you decide to really start, I recommend producing these docs first:

1. `CoinCat Domain Model Spec`
2. `CoinCat Data Schema Spec`
3. `CoinCat Feature Dictionary`
4. `CoinCat Scenario Taxonomy`
5. `CoinCat Risk Policy v1`
6. `CoinCat Research-Only Workflow Spec`
7. `CoinCat Paper Trade Workflow Spec`
8. `CoinCat Live Execution Safety Checklist`

## 12. Final Recommendation

My recommendation is clear:

- CoinCat is a valid and promising future direction
- it should be planned now
- it should remain isolated for now
- it should not be merged into the active AITOS runtime yet

Best current path:

`Treat CoinCat as a future independent trading bounded context, with Phase 1 focused on research and paper-trade only, and defer live automation until the system proves itself through data, backtests, and controlled review.`
