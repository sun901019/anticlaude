# Intermittent Proxy ECONNRESET Analysis

Date: 2026-03-21
Scope: repeated `Failed to proxy http://localhost:8000/... Error: socket hang up` events observed from the Next.js dev server while the FastAPI backend later resumes returning `200 OK`.

## 1. Observed Symptoms

From the captured logs:

- repeated Next.js proxy failures for:
  - `/api/pipeline/status`
  - `/api/review-queue/stats`
- repeated Node-side:
  - `Error: socket hang up`
  - `code: 'ECONNRESET'`
- also observed:
  - `Fast Refresh had to perform a full reload`
- shortly after the failure burst, the backend returned normal responses:
  - `GET /api/health -> 200`
  - `GET /api/pipeline/status -> 200`
  - `GET /api/approvals/pending -> 200`
  - `GET /api/review-queue/stats -> 200`

This is the key signal:
- the backend was not permanently down
- the routes were not missing
- the failure was intermittent

## 2. Most Likely Classification

This looks like a transient dev-runtime coordination issue, not a stable route/code bug.

Most likely category:
- Next.js dev proxy + Fast Refresh + backend availability timing issue

Not the most likely category:
- missing route
- broken API contract
- permanent backend crash

## 3. Why This Pattern Happens

The sequence suggests the following:

1. Next.js dev server is proxying many polling requests to `localhost:8000`
2. During that period, one of these happens:
   - backend is restarting
   - backend worker is temporarily blocked
   - backend connection is closed while Node is still proxying
   - Fast Refresh triggers a full reload and invalidates active client-side polling at the same time
3. Node proxy sees the upstream socket close unexpectedly
4. Next logs `socket hang up / ECONNRESET`
5. Backend finishes recovering and starts returning `200 OK` again

This is consistent with intermittent upstream disconnect, not persistent misconfiguration.

## 4. Evidence Supporting This Conclusion

### 4.1 The backend later responds normally

The same endpoints later return `200 OK`.

That means:
- route exists
- backend process is alive at least part of the time
- the issue is not "endpoint missing"

### 4.2 The failure is concentrated around dev activity

The log includes:
- `Fast Refresh had to perform a full reload`

This is a strong signal that the frontend dev process was in a hot-reload/rebuild cycle when some requests were in flight.

### 4.3 The affected endpoints are polled endpoints

The failing routes are high-frequency UI status endpoints:
- `/api/pipeline/status`
- `/api/review-queue/stats`

These are exactly the kind of endpoints that surface transient coordination issues first.

### 4.4 Earlier project behavior already showed similar instability

This repo already had previous documented proxy/runtime instability around:
- `socket hang up`
- `ECONNRESET`
- local proxy behavior

This new incident matches that same family more than a new logic regression.

## 5. Most Likely Root Causes

Ordered from most likely to less likely:

### 5.1 Backend temporary restart or blocking

If FastAPI is restarting, reloading, or briefly blocking on startup/file IO, the Node proxy can hit a dead upstream socket.

### 5.2 Next.js dev hot-reload / full reload timing

During Fast Refresh or a full reload:
- client polling requests may be duplicated
- old chunk state may still issue requests
- upstream sockets may be closed mid-flight

### 5.3 Too many aggressive polling calls in dev

If several widgets poll frequently:
- pipeline status
- review stats
- approvals
- health

then transient backend stalls become much more visible.

### 5.4 Local Windows dev environment instability

Windows file watching, local process reload timing, and dev-server coordination can produce this more often than a clean production environment.

### 5.5 Keep-alive or proxy connection reuse edge cases

`next.config.js` already disables keep-alive in `httpAgentOptions`.
That helps, but does not fully eliminate transient upstream disconnects during reload/restart windows.

## 6. What This Is Probably NOT

### Not primarily a missing endpoint

Because the same endpoints later return `200 OK`.

### Not primarily a broken rewrite rule

Because the proxy clearly reaches `localhost:8000`, just not reliably during that window.

### Not enough evidence for a permanent backend crash

Because recovery happens immediately afterward.

## 7. Additional Signals In The Log

### 7.1 Missing daily report file

Observed:
- `找不到檔案：... outputs\\daily_reports\\2026-03-21.md`

This is a separate issue.
It indicates expected daily output was not present yet, but it is not the root cause of the proxy resets.

### 7.2 Fast Refresh full reload

This strongly supports the dev-runtime instability interpretation.

## 8. Practical Interpretation

Current interpretation:

- this is mainly a dev-mode resilience problem
- not a confirmed application-logic failure
- the backend and routes appear valid
- the proxy path itself appears valid
- the unstable part is the live coordination between:
  - Next dev server
  - frontend polling
  - backend responsiveness during reload/block windows

## 9. Recommended Hardening Steps

### Priority 1: reduce polling pressure in dev

For endpoints like:
- `/api/pipeline/status`
- `/api/review-queue/stats`

do one or more of:
- increase polling interval
- pause polling when tab is hidden
- back off after repeated failures
- avoid parallel polling bursts during page mount

### Priority 2: make backend health gating stricter

Before non-critical widgets poll:
- confirm `/api/health` is healthy
- short-circuit if backend currently unavailable

### Priority 3: fail soft in UI

For sidebar/topnav cards:
- show stale last-known values
- show temporary unavailable state
- do not spam console endlessly

### Priority 4: inspect backend reload/restart behavior

If FastAPI runs with reload in dev:
- watch whether code changes or file writes trigger frequent restarts
- confirm whether restarts coincide with the reset bursts

### Priority 5: log the exact first upstream failure cause

If possible, add structured backend-side and frontend-side diagnostics around:
- request start
- request abort
- server restart
- reload event

This would let you distinguish:
- backend restart
- request timeout
- upstream disconnect
- local dev proxy glitch

## 10. Recommended Conclusion For Project Tracking

This issue should currently be tracked as:

`Intermittent local dev proxy instability between Next.js dev proxy and FastAPI backend`

Severity:
- medium for dev experience
- low for production confidence unless reproduced in production build/runtime

## 11. Bottom Line

This log does not currently prove that your system logic is broken.

It more strongly suggests:
- the dev server and backend briefly fall out of sync
- Node sees the upstream socket close
- the system then recovers and resumes normal `200 OK` behavior

So the right response is:
- harden dev-mode resilience
- reduce noisy polling
- improve health-gated fallback behavior
- keep monitoring for patterns that would indicate a true backend crash
