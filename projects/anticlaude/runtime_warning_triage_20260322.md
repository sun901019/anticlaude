# Runtime Warning Triage (2026-03-22)

## Summary

The log block contains a mix of:

1. **Intentional test noise**
2. **Expected local-environment warnings**
3. **A few real runtime quality issues worth cleaning up**

The system is not failing as a whole. Most of these entries are either:

- emitted by tests that deliberately exercise failure paths
- emitted because local API keys are missing
- emitted because "today" files do not exist yet

---

## 1. Test Noise: Safe to Ignore During Test Runs

These messages map directly to tests and are expected when the full suite runs:

### Workflow runtime failure-path tests

- `soft failure`
- `deliberate failure`
- `flaky: first attempt`
- `missing_step`
- `Node 'soft' failed after 1 attempt(s)`
- `Node 'always_fail' failed after 2 attempt(s)`

Source:

- `tests/test_graph_workflow.py`

Purpose:

- verify retries
- verify failure propagation
- verify skipped-node dependency behavior

### HTTP retry / network failure tests

- `GET https://non-existent-host-12345.com/`
- `超過最大重試次數`
- `第 1/2/3 次失敗：connection refused`

Source:

- `tests/test_utils.py`

Purpose:

- verify retry logic and failure fallback

### Skill-loader missing-skill tests

- `nonexistent_skill_xyz_999`
- `nonexistent_xyz_999`
- `tests\\.tmp\\pytest\\...\\nonexistent_skill.md`

Source:

- `tests/test_skill_loader.py`

Purpose:

- verify missing-skill handling returns empty string and does not crash

### GEO validator explosion

- `[GEO Gate] validation skipped (non-fatal): GEO validator exploded`

Source:

- `tests/test_dynamic_orchestrator_geo_ab.py`

Purpose:

- verify draft generation still succeeds if GEO validation crashes

### Review / publish failure-path tests

- `publish_post approved but no draft text found`
- `approval fail-approval-id`
- `approval test-approval-id`
- `approval required — created request ...`

Source:

- `tests/test_x_publish_trigger.py`

Purpose:

- verify publish behavior and non-crash behavior for missing draft text

### Misc test-pollution style warnings

- `tests\\.tmp\\pytest\\...\\daily_reports\\1999-01-01.json`

Source:

- `tests/test_utils.py`

Purpose:

- verify missing-file fallback

---

## 2. Local Environment Warnings: Expected Until Credentials Are Configured

These are not test bugs. They are expected in local development unless the keys are configured.

### Anthropic / CEO

- `ANTHROPIC_API_KEY 未設定，CEO Agent 無法運作`

Source:

- `src/agents/ceo.py`

Meaning:

- CEO agent falls back because Anthropic key is not configured

### Threads

- `THREADS_ACCESS_TOKEN 未設定`
- `Threads Token 已過期，請重新授權`

Source:

- `src/tracker/threads_client.py`

Meaning:

- Threads publishing/tracking cannot operate until the token is configured and valid

### Serper

- `SERPER_API_KEY 未設定，跳過 Serper 抓取`
- `Serper search failed (test query): network failure`
- `Serper serper_* 回傳空值`

Source:

- `src/scrapers/serper_scraper.py`
- related tests/mocks

Meaning:

- search pipeline is falling back because Serper is not configured or network is unavailable

### X search

- `[XSearch] ping failed: no network`

Meaning:

- local environment/network or credentials not available

### RSS / external network

- `RSS theverge 抓取失敗：Connection error`

Meaning:

- expected when network is unavailable in local/dev/test environment

---

## 3. File Warnings: Usually Harmless, but Should Be Made Quieter

### Missing daily report / draft of today

- `outputs/daily_reports/2026-03-22.md`
- `outputs/daily_reports/2026-03-22.json`
- `outputs/drafts/2026-03-22.md`

Source:

- `src/api/routes/health.py`
- `src/utils/file_io.py`

Meaning:

- `/api/today` tries to read today's report and draft
- those files simply do not exist yet

This is usually harmless if:

- the daily pipeline has not run yet
- no draft/report has been generated today

Recommended improvement:

- downgrade to quieter UI fallback
- avoid repeating the warning every refresh cycle

---

## 4. Real Runtime Quality Issues Worth Cleaning Up

These are the items that are not catastrophic, but should be improved.

### A. `publish_post approved but no draft text found`

Source:

- `src/api/routes/review.py`

Why it matters:

- if this happens outside tests, it means approval succeeded but the publish payload cannot be resolved

Recommended improvement:

- log more context
  - approval id
  - action
  - whether `evidence_json` existed
  - whether `drafts` query returned anything
- surface a clean operator message instead of silent/noisy warning

### B. Missing-file warning spam from `/api/today`

Why it matters:

- it is not a real failure
- repeated warnings create noise and lower trust

Recommended improvement:

- change missing daily report/draft from warning to info/debug for known-optional files
- or cache the absence for a short period

### C. Test and local runtime logs mixed together

Why it matters:

- operator cannot easily tell whether the system is broken or just running tests

Recommended improvement:

- separate test DB/log context
- tag test runs more clearly
- prevent test-generated approvals/runs from polluting operator-facing views

---

## 5. Practical Conclusion

### Not a major runtime failure

The following categories are mostly safe:

- graph failure-path logs
- fake network host logs
- missing fake skill logs
- GEO crash simulation logs
- test publish warnings

### Real but expected local configuration gaps

- Anthropic key missing
- Threads token missing/expired
- Serper key missing

### Worth cleaning next

1. reduce missing-file warning noise
2. improve publish-without-draft diagnostics
3. better separate test noise from real operator runtime noise

---

## 6. Recommended Next Actions

1. Keep test-failure-path logs out of operator-facing interpretation
2. Treat missing daily report/draft files as soft absence, not warning-level problems
3. Add better context to publish-post warning logs
4. Configure real keys only when you actually want those integrations active
