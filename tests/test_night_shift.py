# encoding: utf-8
import pytest
from unittest.mock import patch, MagicMock
from src.agents.night_shift import _count_sprint_tasks, _get_db_stats, get_last_night_shift, AUTONOMOUS_TASKS


def test_autonomous_tasks_are_safe():
    """確認自治任務清單只含無副作用任務"""
    safe = {"content_research", "data_analysis"}
    for t in AUTONOMOUS_TASKS:
        assert t in safe, f"{t} 不在安全任務清單中"


def test_count_sprint_tasks_returns_dict():
    counts = _count_sprint_tasks()
    assert isinstance(counts, dict)
    for key in ("done", "todo", "in_progress", "blocked"):
        assert key in counts
        assert isinstance(counts[key], int)


def test_count_sprint_tasks_non_negative():
    counts = _count_sprint_tasks()
    for v in counts.values():
        assert v >= 0


def test_get_db_stats_returns_dict():
    stats = _get_db_stats()
    assert isinstance(stats, dict)
    assert "posts_today" in stats
    assert "drafts_today" in stats
    assert "pending_review" in stats


def test_get_last_night_shift_no_files():
    """無夜班記錄時回傳 ran=False"""
    with patch("src.agents.night_shift.REPORTS_DIR") as mock_dir:
        mock_dir.glob.return_value = []
        result = get_last_night_shift()
        assert result["ran"] is False


def test_get_last_night_shift_structure():
    """若有記錄，結構正確"""
    result = get_last_night_shift()
    assert "ran" in result


@pytest.mark.asyncio
async def test_run_night_shift_returns_expected_keys():
    """run_night_shift 回傳值包含所有預期欄位"""
    from src.agents.night_shift import run_night_shift
    from pathlib import Path

    async def _mock_run_task(task_type, ctx=None):
        return {"success": True, "agent": "ori", "task_type": task_type}

    with patch("src.agents.dynamic_orchestrator.run_task", side_effect=_mock_run_task), \
         patch("src.agents.night_shift._write_nightly_summary",
               return_value=Path("/tmp/nightly_summary_2026-03-17.md")), \
         patch("src.utils.notify.send_line_notify", return_value=None):
        result = await run_night_shift()

    assert "date" in result
    assert "tasks_run" in result
    assert "tasks_success" in result
    assert "sprint_counts" in result
    assert "db_stats" in result
