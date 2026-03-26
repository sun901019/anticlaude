"""pytest 設定：async 支援 + test DB isolation"""
import os
import shutil
import sys
import uuid
from pathlib import Path

import pytest

# Force UTF-8 on Windows (CP950 console causes mojibake in captured stdout/stderr)
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


# 讓所有 async test 自動使用 asyncio
def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")


@pytest.fixture(autouse=True)
def isolated_test_db():
    """
    Redirect all DB writes to a temp SQLite so tests never pollute data/anticlaude.db.

    Sets ANTICLAUDE_DB env var before any test runs; src.db.connection._resolve_db_path()
    picks it up at connection time (not import time), so even already-imported modules
    will use the test DB for every sqlite3.connect() call inside a test.

    Uses a repo-local path to avoid Windows system-temp permission issues.
    """
    test_db_dir = Path("tests/.tmp/db").resolve()
    test_db_dir.mkdir(parents=True, exist_ok=True)
    test_db = test_db_dir / "test_anticlaude.db"
    if test_db.exists():
        test_db.unlink(missing_ok=True)
    os.environ["ANTICLAUDE_DB"] = str(test_db)

    # Bootstrap schema so tests can actually write/read tables
    from src.db.schema import DDL
    from src.db.connection import get_conn
    conn = get_conn()
    try:
        conn.executescript(DDL)
        conn.commit()
    finally:
        conn.close()

    yield test_db


@pytest.fixture
def tmp_path():
    """Use a workspace-local temp dir to avoid Windows temp permission issues."""
    path = Path("tests/.tmp/pytest") / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)
