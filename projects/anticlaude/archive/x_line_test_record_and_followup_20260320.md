# X / LINE Test Record And Follow-Up

Date: 2026-03-20
Scope: X publishing/search, LINE notify, current external-integration status

## What Was Tested

### Newly Added Tests
- `tests/test_x_adapter.py`
  - dry-run post validation
  - missing text validation
  - 280-char limit enforcement
  - dry-run delete validation
  - unsupported action rejection
  - approval gate on live post
  - allowed-agent enforcement
  - missing credential handling

- `tests/test_x_search.py`
  - bearer header generation
  - `search_recent()` query/limit handling
  - `get_user_timeline()` min clamp
  - `ping()` failure fallback

- `tests/test_notify.py`
  - LINE notify no-op without env vars
  - LINE notify request payload correctness

### Validation Commands
```powershell
python -m pytest tests/test_x_adapter.py tests/test_x_search.py tests/test_notify.py -q
python -m pytest tests -q
```

## Results

- Targeted X/LINE tests: `15 passed, 1 warning`
- Full suite: `266 passed, 1 warning`
- Remaining warning:
  - Windows `.pytest_cache` creation warning
  - not a feature failure

## Current Status

### X
- Backend publish/search capability is in place:
  - `src/publishers/x_client.py`
  - `src/social/x_search.py`
  - `src/adapters/x_adapter.py`
- Approval-gated dry-run behavior exists and is now covered by tests.
- Search helper behavior is now covered by tests.

### LINE
- Base LINE push helper exists:
  - `src/utils/notify.py`
- Basic notify payload behavior is now covered by tests.
- Existing runtime usage still appears function-based, not adapter-based.

## Gaps Found

### 1. LINE registry mismatch
- `src/adapters/registry.py` declares:
  - adapter name: `line_notify`
  - class name: `LineNotifyAdapter`
- Current codebase only has:
  - `src/utils/notify.py`
  - function: `send_line_notify()`
- No actual `LineNotifyAdapter` class was found.
- Impact:
  - registry metadata says the adapter is active
  - but the adapter contract is not fully implemented like X/Figma/CDP

### 2. X integration still needs end-to-end confirmation
- Unit-level behavior is now tested.
- Still worth confirming later:
  - approval -> publish execution path
  - live credential wiring in non-dry-run mode
  - production-safe error handling from real API responses

### 3. LINE business workflow still incomplete
- The bigger unfinished part is not the base notify helper.
- The unfinished part is the business workflow:
  - competitor price tracking
  - price-drop LINE alerts
  - weekly-report / scheduled notification closure

## Recommended Next Steps

### Priority 1
- Implement a real `LineNotifyAdapter` under `src/adapters/`
- Align registry metadata with actual import path/class
- Add adapter-level tests similar to `XPublishAdapter`

### Priority 2
- Add one end-to-end X publish path test at the workflow/approval boundary
- Keep API calls mocked; verify handoff and approval semantics, not real posting

### Priority 3
- Finish LINE business alert flow
- Suggested slice:
  1. competitor price event generation
  2. alert threshold policy
  3. LINE delivery path
  4. test coverage for alert trigger conditions

### Priority 4
- If browser/CDP later becomes part of X/LINE operations:
  - keep it approval-gated
  - isolate browser profile/session
  - add explicit dry-run/read-only tests first

## Practical Conclusion

- X: mostly wired, now with direct unit coverage
- LINE: base notify exists, but adapter normalization and business alert flow are still unfinished
- Current state is stable enough to continue, but the next clean-up target should be LINE adapter consistency and real alert workflow completion
