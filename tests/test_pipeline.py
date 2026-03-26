"""
測試 pipeline dry-run 模式
"""
import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_pipeline_dry_run():
    """dry-run 模式應完整跑完，不呼叫外部 API"""
    from src.pipeline import run_daily_pipeline
    result = await run_daily_pipeline(date_str="2026-03-10", dry_run=True)

    assert result is not None
    assert result["date"] == "2026-03-10"
    assert result["articles_count"] > 0
    assert result["clusters_count"] > 0
    assert len(result["top3"]) == 3


@pytest.mark.asyncio
async def test_pipeline_dry_run_saves_report(tmp_path, monkeypatch):
    """dry-run 應儲存每日報告"""
    import src.utils.file_io as file_io
    monkeypatch.setattr(file_io, "DAILY_REPORTS_DIR", tmp_path / "daily_reports")
    monkeypatch.setattr(file_io, "_DIR_MAP", {
        "daily_reports": tmp_path / "daily_reports",
        "drafts": tmp_path / "drafts",
        "threads_metrics": tmp_path / "threads_metrics",
        "weekly_reports": tmp_path / "weekly_reports",
        "raw_feed": tmp_path,
    })

    from src.pipeline import run_daily_pipeline
    await run_daily_pipeline(date_str="2026-03-10", dry_run=True)

    report_path = tmp_path / "daily_reports" / "2026-03-10.md"
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "Top 3" in content
