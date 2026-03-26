"""
測試 utils：http_client, file_io, logger
"""
import json
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch
import tempfile
import os


# ── file_io ──────────────────────────────────────────────────────────────────

def test_save_and_load_daily_json(tmp_path, monkeypatch):
    from src import utils
    import src.utils.file_io as file_io

    # 重導向輸出路徑到臨時目錄
    monkeypatch.setattr(file_io, "DAILY_REPORTS_DIR", tmp_path / "daily_reports")
    monkeypatch.setattr(file_io, "_DIR_MAP", {"daily_reports": tmp_path / "daily_reports"})

    data = {"title": "test", "score": 9}
    path = file_io.save_daily_json("daily_reports", data, "2026-03-10")
    assert path.exists()

    loaded = file_io.load_daily_json("daily_reports", "2026-03-10")
    assert loaded == data


def test_save_and_load_daily_md(tmp_path, monkeypatch):
    import src.utils.file_io as file_io
    monkeypatch.setattr(file_io, "DRAFTS_DIR", tmp_path / "drafts")
    monkeypatch.setattr(file_io, "_DIR_MAP", {"drafts": tmp_path / "drafts"})

    content = "# Test\n\nHello World"
    path = file_io.save_daily_md("drafts", content, "2026-03-10")
    assert path.exists()

    loaded = file_io.load_daily_md("drafts", "2026-03-10")
    assert loaded == content


def test_load_missing_returns_none(tmp_path, monkeypatch):
    import src.utils.file_io as file_io
    monkeypatch.setattr(file_io, "_DIR_MAP", {"daily_reports": tmp_path / "daily_reports"})

    result = file_io.load_daily_json("daily_reports", "1999-01-01")
    assert result is None


def test_today_format():
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    assert len(today) == 10
    assert today[4] == "-"


# ── logger ────────────────────────────────────────────────────────────────────

def test_get_logger_returns_logger():
    from src.utils.logger import get_logger
    log = get_logger("test_module")
    assert log.name == "test_module"
    assert log.handlers  # 至少有一個 handler


def test_get_logger_same_instance():
    from src.utils.logger import get_logger
    log1 = get_logger("same_name")
    log2 = get_logger("same_name")
    assert log1 is log2  # 同名返回同一個 logger


# ── http_client ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_returns_json(httpx_mock):
    from src.utils.http_client import get
    httpx_mock.add_response(json={"key": "value"}, url="https://example.com/test")
    result = await get("https://example.com/test")
    assert result == {"key": "value"}


@pytest.mark.asyncio
async def test_get_returns_none_on_persistent_error():
    from src.utils.http_client import get
    import httpx
    with patch("httpx.AsyncClient.get", AsyncMock(side_effect=httpx.RequestError("connection refused"))):
        result = await get("https://non-existent-host-12345.com/")
    assert result is None
