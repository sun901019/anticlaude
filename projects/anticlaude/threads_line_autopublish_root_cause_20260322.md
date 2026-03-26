# Threads / LINE Auto-Publish Root Cause

Date: 2026-03-22

## What Happened

Two different problems were mixed together:

1. Repeated operator alerts on LINE
2. Test-like content such as `Hello world` or `Test tweet content` reaching the social publish path

## Root Cause A: LINE spam from repeated awaiting-human events

The repeated messages such as:

- `[Flow Lab] 選品報告完成，請決策`
- `[AntiClaude] 分析完成，等待確認`

came from:

- `src/api/agent_status.py`
- `mark_agent_awaiting_human()`

Flow Lab and approval-related flows can re-enter `awaiting_human` through retries or
duplicate execution paths. Previously, each re-entry attempted to send a LINE push again.

## Root Cause B: test publish text could hit real social publish code

The text `Hello world` / `Test tweet content` came from test code, not business content.

Primary source:

- `tests/test_x_publish_trigger.py`

Important detail:

- the direct `_trigger_dual_publish(...)` tests were mocking the X adapter
- but they were not mocking the Threads leg
- `_trigger_dual_publish()` calls both:
  - `_trigger_x_publish()`
  - `_trigger_threads_publish()`

That meant a local test run could reach the real Threads publish function if valid
Threads credentials were present in the environment.

## Fixes Applied

### 1. Durable notification dedup for LINE/operator alerts

Implemented in:

- `src/api/agent_status.py`
- `src/db/schema.py`

Behavior:

- dedup key = `agent_id + action_type + ref_id + message`
- window = `10 minutes`
- dedup is now persisted in SQLite via `notification_dispatches`

This prevents repeated operator notifications for the same event, even across backend reloads.

### 2. Test safety for dual publish

Implemented in:

- `tests/test_x_publish_trigger.py`

Behavior:

- the Threads leg is now mocked in the direct `_trigger_dual_publish()` tests
- test content like `Hello world` can no longer leak into real Threads posting during test runs

## Verified

- `python -m pytest tests/test_x_publish_trigger.py -q`
  - `6 passed, 1 warning`
- `python -m pytest tests/test_agent_status.py -q`
  - `11 passed, 1 warning`
- `python -m pytest tests -q`
  - `351 passed, 1 warning`

## Practical Conclusion

If you saw repeated LINE pushes and test-like content posts, the causes were:

- repeated `awaiting_human` notification calls without durable dedup
- test code that exercised the dual-publish path without mocking the Threads side

Both are now patched.
