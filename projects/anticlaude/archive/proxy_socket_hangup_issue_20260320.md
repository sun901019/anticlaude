# Proxy Socket Hang Up Issue

Date: 2026-03-20
Scope: dashboard proxy failures for `review-queue/stats` and `approvals/pending`

## Reported Error

Frontend/runtime logs reported repeated proxy failures like:

```text
Error: socket hang up
code: 'ECONNRESET'
Failed to proxy http://localhost:8000/api/review-queue/stats
Failed to proxy http://localhost:8000/api/approvals/pending
```

## What Was Checked

### 1. Route existence
Confirmed the backend routes exist in code:

- `src/api/routes/review.py`
  - `GET /api/review-queue/stats`
- `src/api/routes/workflows.py`
  - `GET /api/approvals/pending`

So this is not a missing-route bug.

### 2. Dashboard proxy configuration
Confirmed the Next.js dashboard rewrites `/api/:path*` to the backend:

- `dashboard/next.config.js`

```js
{
  source: "/api/:path*",
  destination: "http://localhost:8000/api/:path*",
}
```

So the proxy target path is configured correctly.

### 3. Frontend fetch usage
Confirmed frontend calls are using `/api/...` proxy paths for these reads:

- `dashboard/src/lib/api.ts`
  - `fetchReviewStats()`
  - `fetchPendingApprovals()`

This means the failing requests are using the Next rewrite layer, not the direct backend URL path.

### 4. Direct localhost probe
Tried direct requests to:

- `http://localhost:8000/api/review-queue/stats`
- `http://localhost:8000/api/approvals/pending`

Observed behavior:
- both requests timed out
- no immediate JSON response returned

## Current Diagnosis

The evidence currently points to a runtime/backend availability issue, not a missing frontend path:

- routes exist
- rewrite exists
- frontend fetches are pointed at the expected paths
- direct localhost requests also failed to respond

Most likely causes:

1. backend process is not currently healthy
2. backend process is hanging on DB access or another blocking operation
3. backend was restarting or dead when the dashboard attempted to proxy
4. a local dev-session issue exists between Next dev server and FastAPI server

## Important Note

This issue is different from the previously validated test/build state:

- tests can still pass
- build can still pass

because those checks do not guarantee that the live FastAPI process at `localhost:8000` is healthy at runtime.

## Follow-Up Plan

### Priority 1: runtime health verification
- verify whether FastAPI is actually running on port `8000`
- verify `/api/health` or equivalent health endpoint response in a live session
- check whether the backend process logs show exceptions around the time of proxy failure

### Priority 2: isolate hang source
- directly test these endpoints while backend logs are visible:
  - `/api/review-queue/stats`
  - `/api/approvals/pending`
- if they hang, inspect:
  - DB connection state
  - long-running locks
  - any route code waiting on blocking operations

### Priority 3: make frontend failures softer
- make `fetchPendingApprovals()` and other read-only dashboard fetches degrade gracefully
- consider returning safe defaults on transient proxy errors for non-critical dashboard widgets

### Priority 4: add runtime troubleshooting checklist
- backend running?
- correct `.env`?
- DB file accessible?
- port `8000` occupied by expected process?
- dashboard and backend started in compatible order?

## Practical Conclusion

The new `ECONNRESET / socket hang up` issue should be tracked as:

- not a missing route problem
- not a broken rewrite definition
- most likely a live backend responsiveness problem on `localhost:8000`

This should be fixed and verified in a live dev session, not only through unit tests.
