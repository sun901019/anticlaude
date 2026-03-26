"""
Health & Overview Routes
  GET /health
  GET /api/health
  GET /api/today
"""
from datetime import datetime

from fastapi import APIRouter
from src.utils.file_io import load_daily_json, load_daily_md
from src.utils.logger import get_logger

router = APIRouter()
log = get_logger("api.health")


@router.get("/health")
async def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


@router.get("/api/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


@router.get("/api/today")
async def get_today(date: str | None = None):
    d = date or datetime.now().strftime("%Y-%m-%d")
    structured = load_daily_json("daily_reports", d)
    report = load_daily_md("daily_reports", d)
    drafts = load_daily_md("drafts", d)
    return {
        "date": d,
        "structured": structured,
        "report": report,
        "drafts": drafts,
        "has_data": bool(structured or report or drafts),
    }
