# Test Data Pollution And Review Queue Noise

Date: 2026-03-21
Purpose: explain why review/approval/log entries keep appearing even when the user did not manually create screenshot/video/content approval tasks.

## Executive Summary

The key issue is not just noisy logs.

The real issue is:

**some tests are writing approval requests, review queue items, and workflow runs into the real application SQLite database**

Because of that:
- the review queue gets polluted by test-created items
- approval logs appear for fake scenarios
- workflow runs such as `media_run`, `flowlab_run`, and `rejection_test` show up even though they were created by tests
- the user ends up seeing and rejecting items that should never have reached the real operator surface

## Core Cause

## 1. The database connection is global and points to the real app DB

File:
- [src/db/connection.py](C:\Users\sun90\Anticlaude\src\db\connection.py)

Current behavior:
- `DB_PATH = BASE_DIR / "data" / "anticlaude.db"`

This means the default database is the real application database.

There is currently no automatic per-test DB isolation in this module.

## 2. The tests use the real app and real DB path

Example:
- [tests/test_x_publish_trigger.py](C:\Users\sun90\Anticlaude\tests\test_x_publish_trigger.py)

This test:
- imports `app` from `src.api.main`
- imports `db` from `src.db.connection`
- calls `request_approval(...)`
- patches `/api/review-queue/{id}`

This means the test is not just mocking logic.
It is actually creating:
- `approval_requests`
- `review_items`

in the real configured database unless DB isolation is explicitly patched.

## 3. The current pytest temp fixture does not isolate the SQLite DB

File:
- [tests/conftest.py](C:\Users\sun90\Anticlaude\tests\conftest.py)

What it does:
- creates workspace-local temporary directories for file-based tmp fixtures

What it does NOT currently do:
- redirect `src.db.connection.DB_PATH`
- patch the app to use a temporary test database
- isolate workflow/review/approval persistence from the real app DB

## Evidence From The Logs

These log lines match named test scenarios:

### X publish trigger tests

Log examples:
- `X publish failed for approval fail-approval-id: credentials missing`
- `X publish OK for approval test-approval-id: {'tweet_id': '999'}`
- `publish_post approved but no text in evidence: ['some_other_key']`

Confirmed source:
- [tests/test_x_publish_trigger.py](C:\Users\sun90\Anticlaude\tests\test_x_publish_trigger.py)

### Workflow runtime tests

Log examples:
- `Run started: ... | flowlab_run`
- `Run started: ... | media_run`
- `Run started: ... | rejection_test`

Confirmed source:
- [tests/test_workflow_runtime.py](C:\Users\sun90\Anticlaude\tests\test_workflow_runtime.py)

### Approval/review sync logs

Log examples:
- `review_item 1012 → synced approval ... → approved`
- `review_item 1010 → synced approval ... → rejected`
- `Approval requested: ... | action=publish_post | risk=high`
- `Review inbox item created for approval ...`

These are consistent with the tests creating real review and approval rows.

## Why You Keep Seeing Things To Reject

Because the tests create records in the same database that your real UI reads.

That means your operator surfaces are currently mixing:
- real user-created approvals
- fake test approvals

So even after recent review queue cleanup improvements, the queue can still be polluted by test data.

## Why This Is Worse Than Just Console Noise

This is not only a logging issue.

It affects:
- the real review queue
- approval counts
- operator trust
- dashboard state
- workflow history

It can also cause:
- confusion about what the AI really asked for
- fake pending approvals
- fake review badges
- unnecessary manual rejection effort

## Secondary Observation: Duplicate Log Lines

Some log lines appear twice.

This can happen because:
- multiple tests exercise the same branch
- the same route is called in multiple test cases
- log handlers may be attached twice in certain dev/test startup sequences

But the more important issue is not the duplication.
The more important issue is that test-generated records are reaching the real DB at all.

## Recommended Fix

## Priority 1: isolate SQLite per test session or per test module

The test suite should not use `data/anticlaude.db` directly for workflow/review/approval tests.

Recommended approaches:

### Option A: patch `DB_PATH` to a temporary sqlite file

Best general fix:
- create a pytest fixture that patches:
  - `src.db.connection.DB_PATH`
- initialize schema into a temp DB
- run tests against that temporary DB

### Option B: patch `get_conn()` during relevant test modules

For tests touching:
- workflow runtime
- approval bridge
- review routes
- X publish trigger
- Flow Lab approval routes

redirect the connection to a temp DB.

### Option C: separate integration-test DB from operator DB

Use something like:
- real app: `data/anticlaude.db`
- test integration DB: `tests/.tmp/pytest/.../anticlaude_test.db`

## Priority 2: add teardown cleanup for test-created review/approval rows

Even with DB isolation, cleanup should exist for tests that create:
- `review_items`
- `approval_requests`
- workflow runs
- artifacts

## Priority 3: clearly mark test-created rows if isolation is not immediately fixed

This is only a temporary mitigation.

If isolation cannot be done immediately:
- add a marker in evidence/context/created_by
- make UI hide test-created rows

But this is not the preferred long-term solution.

The correct fix is DB isolation.

## Practical Impact Assessment

Severity:
- high for operator trust
- medium for engineering correctness

Why high:
- it directly pollutes CEO approval surfaces
- it creates fake human work

## Recommended Short-Term Action

1. Stop treating these review items as real work
2. Assume the current strange approval rows may be test residue
3. Fix test DB isolation before adding more approval/review tests
4. Clean existing test-polluted rows from the real DB after the fix

## Bottom Line

The main problem is:

**test cases that exercise approval/review/workflow behavior are currently writing into the same SQLite database used by the real app**

That is why:
- fake approvals appear
- fake review items show up
- fake runs/logs keep appearing
- and you have to manually reject things that should never have reached your inbox
