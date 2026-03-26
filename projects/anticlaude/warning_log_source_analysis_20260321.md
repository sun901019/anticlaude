# Warning Log Source Analysis

Date: 2026-03-21
Purpose: explain the recent warning/error log lines and classify whether they indicate real runtime breakage or expected test/dev noise.

## Executive Summary

Most of the log lines shown are expected test-triggered or dev-environment-triggered warnings.

They do not mean the whole system failed in production at the same time.

The main pattern is:
- tests intentionally exercise failure paths
- the logger prints those failure paths
- pytest still passes because those failures are expected assertions

This is consistent with the current validated state:
- full test suite passes
- build passes

## Log-by-Log Classification

## 1. `social.x_search | [XSearch] ping failed: no network`

Meaning:
- X search ping was intentionally run in a no-network/failure scenario

Likely source:
- X search test path or mock-failure path

Classification:
- expected test/dev failure signal
- not by itself a production bug

## 2. `api.review | X publish failed for approval fail-approval-id: credentials missing`

Meaning:
- the review route tried to trigger an X publish flow
- credentials were intentionally absent

Confirmed source:
- `tests/test_x_publish_trigger.py`
- uses `fail-approval-id`

Classification:
- expected test case
- not a real live approval failure unless you were actively testing without X credentials

## 3. `api.review | publish_post approved but no text in evidence: ['some_other_key']`

Meaning:
- a `publish_post` approval was approved
- but its evidence payload intentionally did not include a valid text field

Confirmed source:
- `tests/test_x_publish_trigger.py`
- uses `evidence={"some_other_key": "value"}`

Classification:
- expected negative test path
- not a random system regression

## 4. `adapter.x_publish | approval required — created request ...`

Meaning:
- the X adapter correctly refused to write immediately
- it created an approval request instead

Confirmed source:
- `src/adapters/base.py`

Classification:
- expected normal behavior
- this is actually a healthy approval-gate signal

## 5. `workflows.runner | Task failed ... | API timeout`

Meaning:
- workflow runtime failure path was exercised

Confirmed source:
- `tests/test_workflow_runtime.py`
- explicitly calls `fail_task(..., error="API timeout")`

Classification:
- expected test failure path
- not evidence of a live workflow outage by itself

## 6. `http_client | GET https://non-existent-host-12345.com/ ... connection refused / retry / 超過最大重試次數`

Meaning:
- HTTP retry and failure handling was intentionally tested against a fake host

Confirmed source:
- `tests/test_utils.py`

Classification:
- expected test path
- good sign that retry/error logging is working

## 7. `file_io | 找不到檔案 ... daily_reports/1999-01-01.json`

Meaning:
- file-not-found handling was intentionally tested using a fake date/path

Confirmed source:
- `tests/test_utils.py`

Classification:
- expected test path

## 8. `threads_client | Threads Token 已過期，請重新授權`
## 9. `threads_client | THREADS_ACCESS_TOKEN 未設定`

Meaning:
- Threads client was invoked without valid credentials or with an expired-token mock path

Confirmed source behavior:
- these exact log lines are in `src/tracker/threads_client.py`

Most likely explanation:
- tests or local environment are intentionally exercising missing-token branches
- or the local environment does not currently have Threads credentials loaded

Classification:
- can be expected during tests/dev
- only becomes a real issue if you are actively trying to use Threads publish/sync in live mode

## 10. `skill_loader | Composite skill 文件不存在 ... nonexistent_...`

Meaning:
- missing-skill handling was intentionally tested

Confirmed source:
- `tests/test_skill_loader.py`
- uses:
  - `nonexistent_skill_xyz_999`
  - `nonexistent_xyz_999`
  - tmp test path missing skill

Classification:
- expected test path
- not a real missing production skill unless the missing filename is one you actually configured

## Practical Conclusion

These logs are mostly from deliberate negative-path tests.

They indicate:
- error handling paths are being exercised
- logging is noisy during tests
- the system is not silently swallowing failures

They do **not** indicate that all of these failures are happening simultaneously in the real product.

## What Would Count As A Real Runtime Problem

You should treat it as a real runtime problem only if:

- the same warnings appear while you are not running tests
- they repeat during normal product usage
- and they affect real features you are trying to use

Examples:
- real X publish attempt with correct credentials still says `credentials missing`
- real Threads sync attempt still says token missing when `.env` is configured
- real content generation tries to load a truly missing composite skill

## Recommended Handling

### 1. Do not panic when these appear during test runs

Many of them are intentionally expected.

### 2. Distinguish test noise from live runtime logs

Best future improvement:
- separate test logging from app runtime logging
- or lower some expected test-path logs from warning/error to debug in test context

### 3. Watch for repeat signals outside tests

If the same messages appear during real manual use, then inspect:
- env loading
- approval trigger payloads
- skill route configuration
- actual token presence

## Bottom Line

The logs you pasted mostly map directly to known negative-path tests:

- X publish trigger tests
- workflow failure tests
- utility/network retry tests
- skill loader missing-file tests

So this log block is mostly:
- expected test/dev noise
- not proof of a broad live-system failure
