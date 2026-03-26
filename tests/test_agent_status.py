"""
測試 Agent 狀態機完整生命週期
"""
from unittest.mock import AsyncMock

import pytest
from src.api.agent_status import (
    get_all_status,
    set_agent_status,
    update_agent_task,
    mark_agent_done,
    mark_agent_blocked,
    mark_agent_handoff_pending,
    mark_agent_awaiting_human,
)


def test_initial_state():
    """所有 agent 初始狀態應存在且有效"""
    status = get_all_status()
    for agent_id in ["ori", "lala", "craft", "lumi", "sage", "pixel"]:
        assert agent_id in status
        assert status[agent_id]["status"] in (
            "idle", "working", "blocked", "handoff_pending", "awaiting_human", "done"
        )


def test_set_agent_working():
    """set_agent_status 設為 working 應更新狀態"""
    set_agent_status("ori", "working", "測試任務")
    status = get_all_status()
    assert status["ori"]["status"] == "working"
    assert status["ori"]["task"] == "測試任務"


def test_update_agent_task_structured():
    """update_agent_task 應建立結構化 task_meta"""
    update_agent_task(
        "lala",
        status="working",
        task="策略分析",
        task_type="strategy",
        source_agent_id="ori",
        target_agent_id="craft",
    )
    status = get_all_status()
    meta = status["lala"]["task_meta"]
    assert meta["task_type"] == "strategy"
    assert meta["source_agent_id"] == "ori"
    assert meta["target_agent_id"] == "craft"
    assert meta["status"] == "in_progress"


def test_mark_agent_done():
    """mark_agent_done 應將 agent 回到 idle"""
    set_agent_status("craft", "working", "寫文案")
    mark_agent_done("craft", artifact_refs=["outputs/drafts/test.md"])
    status = get_all_status()
    assert status["craft"]["status"] == "idle"


def test_mark_agent_blocked():
    """mark_agent_blocked 應設定 blocked 狀態"""
    mark_agent_blocked("sage", "等待 Ori 提供競品資料")
    status = get_all_status()
    assert status["sage"]["status"] == "blocked"
    assert status["sage"]["task_meta"]["status"] == "blocked"


def test_mark_agent_handoff_pending():
    """mark_agent_handoff_pending 應設定交接狀態"""
    set_agent_status("ori", "working", "分群任務")
    mark_agent_handoff_pending("ori", target_agent_id="lala")
    status = get_all_status()
    assert status["ori"]["status"] == "handoff_pending"
    assert status["ori"]["task_meta"]["target_agent_id"] == "lala"


def test_mark_agent_awaiting_human():
    """mark_agent_awaiting_human 應設定等待人決策狀態"""
    mark_agent_awaiting_human(
        "craft",
        message="選品報告完成，請決策",
        action_type="approve_purchase",
        ref_id="candidate_123",
    )
    status = get_all_status()
    assert status["craft"]["status"] == "awaiting_human"
    assert status["craft"]["task_meta"]["action_type"] == "approve_purchase"
    assert status["craft"]["task_meta"]["ref_id"] == "candidate_123"


def test_awaiting_human_with_artifact_refs():
    """mark_agent_awaiting_human 應正確存入 artifact_refs"""
    mark_agent_awaiting_human(
        "sage",
        message="分析完成，等待確認",
        action_type="confirm_analysis",
        ref_id="analysis_456",
        artifact_refs=["ecommerce/selection/analysis/analysis_456"],
    )
    status = get_all_status()
    assert status["sage"]["task_meta"]["artifact_refs"] == [
        "ecommerce/selection/analysis/analysis_456"
    ]


def test_all_six_agents_exist():
    """確認 6 個 agent 都存在且有完整欄位"""
    status = get_all_status()
    for agent_id in ["ori", "lala", "craft", "lumi", "sage", "pixel"]:
        assert agent_id in status
        assert "nickname" in status[agent_id]
        assert "role" in status[agent_id]
        assert "task_meta" in status[agent_id]


def test_mark_agent_awaiting_human_deduplicates_notifications(monkeypatch):
    """Duplicate awaiting_human events should not spam LINE notifications."""
    import src.api.agent_status as agent_status

    agent_status._recent_human_notifications.clear()
    mock_notify = AsyncMock()
    monkeypatch.setattr("src.utils.notify.send_line_notify", mock_notify)

    kwargs = {
        "message": "測試桌面植物盆栽 選品報告完成，請決策",
        "action_type": "approve_purchase",
        "ref_id": "candidate_plant_001",
    }

    mark_agent_awaiting_human("craft", **kwargs)
    mark_agent_awaiting_human("craft", **kwargs)

    assert mock_notify.await_count == 1


def test_mark_agent_awaiting_human_deduplicates_notifications_after_cache_clear(monkeypatch):
    """DB-backed dedup should still work even if in-process cache is cleared."""
    import src.api.agent_status as agent_status

    agent_status._recent_human_notifications.clear()
    mock_notify = AsyncMock()
    monkeypatch.setattr("src.utils.notify.send_line_notify", mock_notify)

    kwargs = {
        "message": "測試桌面植物盆栽 選品報告完成，請決策",
        "action_type": "approve_purchase",
        "ref_id": "candidate_plant_002",
    }

    mark_agent_awaiting_human("craft", **kwargs)
    agent_status._recent_human_notifications.clear()
    mark_agent_awaiting_human("craft", **kwargs)

    assert mock_notify.await_count == 1
