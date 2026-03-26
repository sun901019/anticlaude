"""
API Shared State
=================
Asyncio locks and mutable status vars shared between:
  - HTTP route handlers (read state, acquire locks)
  - APScheduler callbacks in main.py (acquire locks, write status)

Import from here instead of referencing main.py globals.
"""
import asyncio

# ── Execution locks (prevent concurrent runs) ────────────────────────────────
pipeline_lock = asyncio.Lock()
tracker_lock = asyncio.Lock()
weekly_lock = asyncio.Lock()
feedback_lock = asyncio.Lock()
night_shift_lock = asyncio.Lock()

# ── Pipeline status (shown in dashboard warnings) ────────────────────────────
pipeline_last_error: str = ""
pipeline_last_error_at: str = ""
pipeline_last_success_at: str = ""

# ── Night shift last result ───────────────────────────────────────────────────
night_shift_last_result: dict = {}
