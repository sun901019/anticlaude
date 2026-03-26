# Flow Lab Notification Spam Fix

Date: 2026-03-22

## Problem

The operator was receiving repeated LINE notifications such as:

- `[Flow Lab] 選品報告完成，請決策`
- `[AntiClaude] 分析完成，等待確認`

The same approval/report event could trigger multiple notifications within a short time window.

## Root Cause

The repeated messages were not caused by Threads publishing. They were triggered by `mark_agent_awaiting_human()` in:

- `src/api/agent_status.py`

That function always attempted to send a LINE notification whenever an agent entered `awaiting_human`, even if the same event had already been notified moments earlier.

This was especially visible in Flow Lab paths that can re-enter approval states from:

- Flow Lab selection analysis
- Screenshot approval flow
- Workflow approval gates
- Retry / duplicate execution paths

## Fix Applied

Added durable notification deduplication in `src/api/agent_status.py`.

### Dedup key

The dedup signature uses:

- `agent_id`
- `action_type`
- `ref_id`
- `message`

### Dedup window

- `10 minutes`

If the same signature appears again within that window, the LINE notification is skipped.

## Persistence Model

Dedup now uses two layers:

1. In-process memory cache for fast short-circuiting
2. SQLite-backed persistence in `notification_dispatches`

This means duplicate Flow Lab/operator notifications remain suppressed even after
a backend reload, as long as the same event signature is retriggered within the
dedup window.

## Files Changed

- `src/db/schema.py`
- `src/api/agent_status.py`
- `tests/test_agent_status.py`

## Validation

- Targeted test: `python -m pytest tests/test_agent_status.py -q`
  - Result: `11 passed, 1 warning`
- Full backend suite: `python -m pytest tests -q`
  - Result: `351 passed, 1 warning`

## Expected Effect

The same Flow Lab approval/report event should no longer spam repeated operator notifications during short retry loops or duplicate handoff paths.

## Remaining Caveat

This is now durable for a single SQLite-backed deployment, but it is still not
multi-instance distributed dedup.

If the system later runs multiple backend instances, the same concept should be
moved to Redis or another shared store.
