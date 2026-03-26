"""
SQLite 連線管理
資料庫路徑：data/anticlaude.db

Override for tests: set env var ANTICLAUDE_DB to a temp path so tests never
touch the real production database.
"""
import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

from src.config import BASE_DIR

# Kept for import compatibility (e.g. alembic, scripts that reference DB_PATH directly).
# Use _resolve_db_path() for actual connections — reads env var at call time so
# tests can override without reimporting the module.
DB_PATH = BASE_DIR / "data" / "anticlaude.db"


def _resolve_db_path() -> Path:
    override = os.environ.get("ANTICLAUDE_DB")
    return Path(override) if override else DB_PATH


def get_conn() -> sqlite3.Connection:
    path = _resolve_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
