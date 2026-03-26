# Integration Status Matrix
> Date: 2026-03-21
> Purpose: define what each external integration actually does now, and what is deferred.

## Status Legend
- ✅ **Production-ready** — implemented, tested, used in real workflows
- 🟡 **Partial** — backend wired, some business logic missing or not E2E verified
- ⏸ **Deferred** — adapter/client exists, not wired into any live workflow intentionally
- ❌ **Not implemented** — nothing yet

---

## LINE Notify

| Capability | Status | Notes |
|------------|--------|-------|
| Basic push notification | ✅ | `send_line_notify()` in `src/utils/notify.py`, used by night_shift + pipeline |
| Nightly summary | ✅ | Night shift (22:00) sends LINE summary if token is set |
| Competitor price-drop alert | 🟡 | `run_price_check_and_notify()` wired at 20:00 in scheduler — needs `COMPETITOR_KEYWORDS_RAW` env var populated and at least one prior price check to compute change |
| Business workflow alerts | ⏸ | Beyond price drops, no other business events trigger LINE |

**Decision: LINE = notification channel only.** Not a two-way operational system. Price-drop alert is now fully wired.

---

## X (Twitter / Threads)

| Capability | Status | Notes |
|------------|--------|-------|
| Post draft text | 🟡 | `XPublishAdapter` exists, `dry_run=True` default, OAuth 1.0a wired |
| Auto-post on review approval | 🟡 | `/api/review-queue/{id}` PATCH triggers `_trigger_x_publish()` via BackgroundTasks when `publish_post` is approved |
| E2E live post verified | ❌ | Not tested with real X API credentials in production |

**Action needed:** Set `DRY_RUN=false` in env + verify with real X credentials before enabling live posts.

---

## Figma

| Capability | Status | Notes |
|------------|--------|-------|
| Read file metadata | ✅ | `GET /api/figma/file?file_key=...` |
| Read components | ✅ | `GET /api/figma/nodes` |
| Read comments | ✅ | `GET /api/figma/comments` |
| Export image URLs | ✅ | `GET /api/figma/images` |
| Send images to Pixel for UX feedback | ✅ | `/figma` page "發送給 Pixel 分析" button |
| Design token extraction | ⏸ | Not implemented — would require parsing node styles |
| Design → frontend code generation | ⏸ | Deferred — requires token layer + node selection + artifact output pipeline |

**Decision: Figma = read-only design reference + UX feedback loop.** Design-to-code generation is deferred until Figma token extraction layer is built.

---

## Video

| Capability | Status | Notes |
|------------|--------|-------|
| Upload video | ✅ | `POST /api/flowlab/upload-video` |
| Approval gate for video analysis | ✅ | Creates review_item `approve_video_analysis` |
| M1: extract product info from screenshot (image) | ✅ | Flow Lab screenshot analyze fully works |
| M2: ffmpeg frame extraction | 🟡 | `VideoFrameAdapter` implemented but requires ffmpeg binary on PATH |
| M3: Vision model analysis of frames | ⏸ | Deferred — requires M2 (ffmpeg) + Claude Vision / Gemini Vision integration |

**Decision: Video = M1 (screenshot) is production-ready. M2/M3 deferred until ffmpeg is installed and Vision analysis path is scoped.**

---

## Browser / CDP (Playwright)

| Capability | Status | Notes |
|------------|--------|-------|
| Adapter exists | ✅ | `src/adapters/chrome_cdp_adapter.py` |
| Approval-gated | ✅ | `requires_approval=True`, `dry_run=True` default |
| Session isolation | ⏸ | Not implemented — each call opens a new browser context, no isolation policy |
| Operator workflow | ⏸ | No UI surface — adapter is not exposed in Office or any page |
| Governance doc | ✅ | `projects/anticlaude/browser_cdp_governance_20260321.md` |

**Decision: CDP = guarded adapter, intentionally not exposed in UI.** Do not add to Office or any operator surface until session isolation and approval semantics are fully defined.

---

## Serper (Search)

| Capability | Status | Notes |
|------------|--------|-------|
| Sync search (competitor_analyzer.py) | ✅ | Used in ecommerce selection analysis |
| Async search (serper_client.py) | ✅ | New: used by competitor_tracker |

---

## Summary Table

| Integration | Operational Today | Notes |
|-------------|-------------------|-------|
| LINE Notify | ✅ | Token must be set in env |
| X Publish | 🟡 | dry_run=True until credentials verified |
| Figma Read | ✅ | File key must be set in env |
| Video M1 | ✅ | Screenshot analysis fully works |
| Video M2/M3 | ⏸ | ffmpeg required |
| CDP/Browser | ⏸ | Not exposed in UI intentionally |
| Competitor tracking | 🟡 | Wired but needs COMPETITOR_KEYWORDS_RAW set |
