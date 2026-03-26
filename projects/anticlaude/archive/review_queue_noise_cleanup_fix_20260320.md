# Review Queue Noise And Cleanup Fix

Date: 2026-03-20

## Reported Problems

1. The review queue kept accumulating many approval-like items even when no screenshot or video had been uploaded manually.
2. Approved / deferred items had no cleanup action in the review UI, so they accumulated indefinitely.
3. This made the review queue feel noisy and less trustworthy as a CEO-facing inbox.

## Root Cause

### 1. Too many approval actions were mirrored into `review_items`
- `src/workflows/approval.py` previously mirrored every medium/high approval into `review_items`.
- That included internal workflow gates such as:
  - `select_draft`
- Result:
  - internal pipeline approvals generated CEO inbox noise
  - the queue looked full even when the user had not manually triggered Flow Lab screenshot/video work

### 2. Cleanup was only available for rejected items
- `dashboard/src/app/review/page.tsx` only exposed a purge button for the rejected tab
- backend cleanup support was also effectively limited to rejected records
- approved and deferred items could remain forever

## Fix Applied

### Approval mirroring narrowed to a whitelist
- File: `src/workflows/approval.py`
- Changed review queue mirroring from:
  - all medium/high approvals
- To:
  - only explicit CEO-inbox actions:
    - `publish_post`
    - `promote_product`
    - `approve_screenshot`
    - `approve_video_analysis`
    - `approve_purchase`

### New review cleanup API
- File: `src/api/routes/review.py`
- Added:
  - `DELETE /api/review-queue?status=approved`
  - `DELETE /api/review-queue?status=rejected`
  - `DELETE /api/review-queue?status=deferred`
  - `DELETE /api/review-queue?status=decided`

### Review UI rebuilt and cleaned up
- File: `dashboard/src/app/review/page.tsx`
- Improvements:
  - clean status labels and actions
  - cleanup button for approved / rejected / deferred / all decided
  - better detail modal copy
  - less mojibake / malformed strings

### Frontend API helper added
- File: `dashboard/src/lib/api.ts`
- Added:
  - `cleanupReviewQueue()`

## Test Coverage Added / Updated

- File: `tests/test_approval_bridge.py`
- Now verifies:
  - `select_draft` no longer creates review inbox noise
  - `publish_post` still creates a review item
  - screenshot/video review decisions still sync correctly
  - cleanup endpoint removes approved items
  - cleanup endpoint removes deferred items from review queue only

## Validation

```powershell
python -m pytest tests -q
```

Result:
- `268 passed, 1 warning`

```powershell
npm.cmd run build
```

Result:
- dashboard build passed

## Expected User-Facing Effect

### Better
- The review queue should no longer be flooded by internal draft-selection approvals.
- Only more intentional CEO-facing review actions should appear there.
- Approved / deferred items can now be cleaned up from the UI.

### Still Separate
- `approval_requests` still exist as the workflow/graph approval primitive.
- `review_items` now behave more like a curated CEO inbox, not a mirror of every internal approval.

## Future Improvements

1. Add age-based cleanup helpers
   - e.g. clear approved items older than 7 days

2. Add action-type filters to the review page
   - useful when screenshot/video approvals and content approvals coexist

3. Add a one-click “archive decided items” action
   - UX alternative to destructive delete

4. Consider showing `approval_requests` and `review_items` more explicitly as separate concepts in UI
   - reduces confusion when one exists without the other
