"""
JSON / Markdown 讀寫工具，依日期自動命名
"""
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any

from src.config import (
    DAILY_REPORTS_DIR,
    DRAFTS_DIR,
    THREADS_METRICS_DIR,
    WEEKLY_REPORTS_DIR,
    RAW_FEED_DIR,
    OUTPUTS_DIR,
)
from src.utils.logger import get_logger

log = get_logger("file_io")

_DIR_MAP = {
    "daily_reports": DAILY_REPORTS_DIR,
    "drafts": DRAFTS_DIR,
    "threads_metrics": THREADS_METRICS_DIR,
    "weekly_reports": WEEKLY_REPORTS_DIR,
    "raw_feed": RAW_FEED_DIR,
}


def _ensure(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _current_week() -> str:
    """回傳 week_YYYY-WW 格式"""
    now = datetime.now()
    return f"week_{now.strftime('%Y-%V')}"


# ── JSON ────────────────────────────────────────────────────────────────────

def save_daily_json(folder: str, data: Any, date_str: str | None = None) -> Path:
    """儲存為 outputs/<folder>/YYYY-MM-DD.json"""
    d = date_str or _today()
    target_dir = _DIR_MAP.get(folder)
    if target_dir is None:
        target_dir = OUTPUTS_DIR / folder
    path = _ensure(target_dir / f"{d}.json")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info(f"已儲存 {path}")
    return path


def load_daily_json(folder: str, date_str: str) -> Any | None:
    """讀取 outputs/<folder>/YYYY-MM-DD.json"""
    target_dir = _DIR_MAP.get(folder, OUTPUTS_DIR / folder)
    path = target_dir / f"{date_str}.json"
    if not path.exists():
        log.debug(f"檔案尚未生成：{path}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_raw_feed(data: Any, date_str: str | None = None) -> Path:
    """儲存原始素材到 uploads/raw_feed_YYYY-MM-DD.json"""
    d = date_str or _today()
    path = _ensure(RAW_FEED_DIR / f"raw_feed_{d}.json")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info(f"已儲存原始素材：{path}")
    return path


def load_raw_feed(date_str: str | None = None) -> Any | None:
    d = date_str or _today()
    path = RAW_FEED_DIR / f"raw_feed_{d}.json"
    if not path.exists():
        log.debug(f"原始素材尚未生成：{path}")
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ── Markdown ─────────────────────────────────────────────────────────────────

def save_daily_md(folder: str, content: str, date_str: str | None = None) -> Path:
    """儲存為 outputs/<folder>/YYYY-MM-DD.md"""
    d = date_str or _today()
    target_dir = _DIR_MAP.get(folder, OUTPUTS_DIR / folder)
    path = _ensure(target_dir / f"{d}.md")
    path.write_text(content, encoding="utf-8")
    log.info(f"已儲存 {path}")
    return path


def load_daily_md(folder: str, date_str: str) -> str | None:
    target_dir = _DIR_MAP.get(folder, OUTPUTS_DIR / folder)
    path = target_dir / f"{date_str}.md"
    if not path.exists():
        log.debug(f"檔案尚未生成：{path}")
        return None
    return path.read_text(encoding="utf-8")


def save_weekly_md(content: str, week_str: str | None = None) -> Path:
    """儲存為 outputs/weekly_reports/week_YYYY-WW.md"""
    w = week_str or _current_week()
    path = _ensure(WEEKLY_REPORTS_DIR / f"{w}.md")
    path.write_text(content, encoding="utf-8")
    log.info(f"已儲存週報：{path}")
    return path


def list_recent_dates(folder: str, days: int = 7) -> list[str]:
    """列出最近 N 天有資料的日期（降序）"""
    target_dir = _DIR_MAP.get(folder, OUTPUTS_DIR / folder)
    if not target_dir.exists():
        return []
    files = sorted(target_dir.glob("*.json"), reverse=True) + sorted(
        target_dir.glob("*.md"), reverse=True
    )
    dates = []
    for f in files:
        stem = f.stem
        if len(stem) == 10:  # YYYY-MM-DD
            dates.append(stem)
    return list(dict.fromkeys(dates))[:days]
