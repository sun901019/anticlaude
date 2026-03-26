# Browser / CDP Governance Policy
**Project:** AntiClaude
**Version:** 1.0
**Date:** 2026-03-21
**Status:** Draft — adapter exists, governance NOT yet productized
**Owner:** Claude Code (Lumi) + Codex

---

## 1. Session Isolation Policy

Every CDP (Chrome DevTools Protocol) session must run in a fully isolated browser environment.

### Rules
- **Fresh profile per session.** Each invocation of `chrome_cdp_adapter.py` launches Playwright with `user_data_dir=None` (no persistent user data directory). Browser state — cookies, localStorage, cached credentials — is discarded when the session ends.
- **No shared context.** Multiple concurrent CDP tasks must never share a browser context or page object. Each task receives its own `BrowserContext`.
- **Ephemeral launch arguments.** The adapter passes `--no-first-run`, `--no-default-browser-check`, `--disable-extensions`, and `--incognito` (or equivalent) to Chromium to prevent any ambient profile loading.
- **Session lifetime.** A session is alive only for the duration of a single task execution. The browser process is terminated (context closed, browser closed) in the `finally` block regardless of outcome.

---

## 2. Allowed vs. Disallowed Actions

### Allowed (Read-Only) — No human approval required
| Action | Method |
|--------|--------|
| Take a full-page screenshot | `page.screenshot()` |
| Scrape visible page text / HTML | `page.content()`, `page.inner_text()` |
| Extract structured data (tables, lists) | DOM query via `page.query_selector_all()` |
| Read page title / URL / metadata | `page.title()`, `page.url` |
| Navigate to a URL (GET only) | `page.goto(url, wait_until="networkidle")` |

### Disallowed (Write Actions) — Always require explicit human approval
| Action | Reason |
|--------|--------|
| Form submission (`page.click()` on submit) | Irreversible data mutation |
| Filling in text inputs (`page.fill()`) | Could authenticate, post, or purchase |
| Clicking buttons, links (any DOM click) | Risk of triggering payments, publishes, deletions |
| File upload | Could exfiltrate or mutate external data |
| Cookie injection / `page.set_extra_http_headers()` with auth headers | Session hijacking risk |
| JavaScript execution via `page.evaluate()` | Arbitrary code execution in page context |
| Downloading files to disk | Storage side-effect |

> **Hard rule:** Any action not explicitly listed as "Allowed" above is treated as Disallowed.

---

## 3. Approval Gate Rules

### Risk Classification
| Risk Level | Examples | Approval Required? | dry_run Bypass Allowed? |
|------------|----------|--------------------|-------------------------|
| `low` | Screenshot, scrape | No | N/A |
| `medium` | Navigate to authenticated page | Recommended | Yes, with `dry_run=True` |
| `critical` | Form submit, click, JS eval | **Always** | **Never** |

### Gate Implementation
- `chrome_cdp_adapter.py` inherits from `AdapterBase.safe_execute()`.
- When `risk_level == "critical"`, `safe_execute()` calls `approval_bridge.request_approval()` and blocks until a human decision is received.
- `dry_run=True` is accepted only for `low` and `medium` risk actions. For `critical` risk, `dry_run=True` is **rejected at the gate** — the adapter returns an error without executing.
- Approval decisions are persisted in the `approval_requests` table (workflow DB) with `requester`, `action_summary`, `risk_level`, `decision`, and `decided_at` fields.

### Timeout Policy
- Approval requests time out after **10 minutes** if no human decision is received.
- On timeout, the action is treated as **rejected** — the task fails cleanly and logs `approval_timeout`.

---

## 4. Operator Workflow

### How the CEO Agent Triggers a CDP Task

```
CEO Agent (src/agents/ceo.py)
  └─ detects intent: "take a screenshot of X" / "scrape page Y"
  └─ routes to: dynamic_orchestrator → task_handler: "browser_cdp"
      └─ calls chrome_cdp_adapter.execute({
             "action": "screenshot",
             "url": "https://...",
             "risk_level": "low"
         })
```

### What the Operator Sees
1. **Task submitted:** CEO Console shows a task card with status `running`.
2. **For read-only actions:** The adapter executes immediately. Result (screenshot path or scraped text) appears in the task card within seconds.
3. **For write/critical actions:** The task card transitions to `awaiting_approval`. The Review Queue (`/review`) shows a new item with:
   - Action summary (what will be clicked / submitted)
   - Target URL
   - Risk level badge (`critical`)
   - Irreversibility warning banner

### What the Operator Decides
- **Approve:** Adapter proceeds with the write action. Decision logged.
- **Reject:** Adapter returns `AdapterResult(ok=False, error="rejected_by_operator")`. Task marked failed.
- **No action (timeout 10 min):** Auto-rejected, task marked failed with `approval_timeout`.

---

## 5. Anti-Detection Measures

The adapter is designed for legitimate internal automation (screenshots, scraping own staging/preview URLs). The following settings reduce automation fingerprinting in cases where the target site may have bot-detection:

| Measure | Implementation |
|---------|---------------|
| Headless mode | `headless=True` passed to `playwright.chromium.launch()` |
| No persistent profile | `user_data_dir=None` — fresh profile every session |
| Realistic viewport | `viewport={"width": 1280, "height": 800}` (not 0x0) |
| No automation flag in UA | `args=["--disable-blink-features=AutomationControlled"]` |
| No extension / devtools protocol exposure | `--no-first-run`, `--disable-extensions` |

> **Note:** These measures are not intended for bypassing site access controls or Terms of Service. CDP tasks must only target URLs that the operator has legitimate access to.

---

## 6. Current Implementation Status

| Component | Status | File |
|-----------|--------|------|
| CDP Adapter (Playwright) | **Implemented** | `src/adapters/chrome_cdp_adapter.py` |
| Approval Bridge | **Implemented** | `src/adapters/approval_bridge.py` |
| AdapterBase safe_execute | **Implemented** | `src/adapters/adapter_base.py` |
| Approval DB table | **Implemented** | `approval_requests` (workflow DB) |
| Review Queue UI (Approve/Reject) | **Implemented** | `dashboard/src/app/review/page.tsx` |
| CDP task handler in DynamicOrchestrator | **Partial** — no `browser_cdp` task type yet | `src/agents/dynamic_orchestrator.py` |
| CEO intent detection for CDP | **Not yet** | `src/agents/ceo.py` |
| Figma API routes | **In progress** (Claude Code) | `src/api/routes/figma.py` |
| Figma operator UI page | **In progress** (Claude Code) | `dashboard/src/app/figma/page.tsx` |
| Governance policy (this doc) | **Created** | `projects/anticlaude/browser_cdp_governance_20260321.md` |
| Governance productized into code | **NOT YET** | — |

---

## 7. Next Steps to Productize

1. **Add `browser_cdp` task type to DynamicOrchestrator**
   - File: `src/agents/dynamic_orchestrator.py`
   - Add `_handle_browser_cdp(task)` handler that unpacks `url`, `action`, `risk_level` from task params and calls `chrome_cdp_adapter.execute()`

2. **Wire CEO intent detection for CDP actions**
   - File: `src/agents/ceo.py`
   - Add intent patterns: `"screenshot"`, `"scrape"`, `"open page"`, `"take snapshot"`
   - Route to `dynamic_orchestrator` with task type `"browser_cdp"`

3. **Enforce dry_run rejection for critical risk at adapter level**
   - File: `src/adapters/chrome_cdp_adapter.py`
   - Add guard: `if risk_level == "critical" and dry_run: return AdapterResult(ok=False, error="dry_run_not_allowed_for_critical_risk")`

4. **Add CDP action to approval_matrix.py**
   - Ensure `ApprovalMatrix` has a row for `chrome_cdp` with `critical` risk level and `requires_approval=True`

5. **Write end-to-end integration test**
   - File: `tests/test_chrome_cdp_governance.py`
   - Mock Playwright, verify: screenshot passes without approval, form-submit is blocked, critical action with dry_run=True returns error

6. **Dashboard: CDP task result display**
   - Show screenshot thumbnail in task result card (CEO Console or a new `/browser` operator page)

7. **Audit log**
   - Every CDP session (approved or rejected) emits an event to the `workflow_events` table for compliance traceability
