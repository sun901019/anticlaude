# Ecommerce Bundle Activation Fix

Date: 2026-03-22
Owner: Codex

## Problem

The `組合設計` page appeared unresponsive.

Observed runtime log:

- `GET /api/ecommerce/selection/bundles/suggest HTTP/1.1" 405 Method Not Allowed`
- `GET /api/ecommerce/selection/portfolio HTTP/1.1" 200 OK`

This meant:

- portfolio data loaded successfully
- bundle suggestions did not load at all

So the operator would open `組合設計`, but no AI bundle suggestion payload would be returned.

## Root Cause

Frontend and backend request methods were mismatched.

### Frontend

`dashboard/src/app/ecommerce/page.tsx`

`loadBundles()` was calling:

- `GET /api/ecommerce/selection/bundles/suggest`

### Backend

`src/domains/flow_lab/selection.py`

The route is defined as:

- `POST /bundles/suggest`

This mismatch caused the 405.

## Fix

Updated frontend `loadBundles()` to use:

- `POST /api/ecommerce/selection/bundles/suggest`

This aligns the operator-side load action with the actual backend route contract.

## Result

After this fix, `組合設計` should trigger properly when:

1. the operator opens the `組合設計` tab
2. the page calls `loadBundles()`
3. the frontend now sends the correct `POST` request

## Notes

Current bundle activation remains operator-triggered, not automatic background refresh.

It still runs when:

- the `組合設計` tab is opened
- or the refresh action inside that tab is clicked

## Remaining Improvement

The route now works, but the bundle engine is still mainly:

- candidate/category based
- role-pair based

Future strengthening should shift it toward:

- live product families
- scene bundles
- main product + accessory logic
- operator-facing merchandising use cases
