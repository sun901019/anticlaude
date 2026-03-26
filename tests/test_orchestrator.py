from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from src.agents import orchestrator


def _result(*, data, model="test-model", success=True, error=None):
    return SimpleNamespace(success=success, data=data, model_used=model, error=error)


@pytest.mark.asyncio
async def test_run_pipeline_returns_summary(monkeypatch):
    articles = [{"title": "A", "url": "https://example.com/a"}]
    clusters = [{"cluster_label": "Topic A"}]
    scored = [{"cluster_label": "Topic A", "score": 9.2}]
    top3 = [{"cluster_label": "Topic A"}]
    drafts = {
        "drafts_list": [{"cluster_label": "Topic A", "hook": "Hook"}],
        "drafts_path": "outputs/drafts/2026-03-16.md",
    }

    monkeypatch.setattr(
        "src.scrapers.aggregator.run_aggregator",
        AsyncMock(return_value=articles),
    )
    monkeypatch.setattr(
        orchestrator,
        "ClusterAgent",
        lambda: SimpleNamespace(run=AsyncMock(return_value=_result(data=clusters, model="cluster-model"))),
    )
    monkeypatch.setattr(
        orchestrator,
        "ScoreAgent",
        lambda: SimpleNamespace(run=AsyncMock(return_value=_result(data=scored, model="score-model"))),
    )
    monkeypatch.setattr(
        orchestrator,
        "StrategyAgent",
        lambda: SimpleNamespace(
            run=AsyncMock(
                return_value=_result(
                    data={"top3": top3, "weekly_insight": "insight"},
                    model="strategy-model",
                )
            )
        ),
    )
    monkeypatch.setattr(
        orchestrator,
        "WriterAgent",
        lambda: SimpleNamespace(run=AsyncMock(return_value=_result(data=drafts, model="writer-model"))),
    )

    save_daily_json = Mock()
    save_topics = Mock(return_value={"Topic A": 1})
    save_drafts = Mock()
    mark_agent_awaiting_human = Mock()

    monkeypatch.setattr(orchestrator, "save_daily_json", save_daily_json)
    monkeypatch.setattr(orchestrator, "mark_agent_awaiting_human", mark_agent_awaiting_human)
    monkeypatch.setattr("src.db.queries.get_recent_topic_labels", lambda days=7: [])
    monkeypatch.setattr("src.db.queries.save_topics", save_topics)
    monkeypatch.setattr("src.db.queries.save_drafts", save_drafts)
    monkeypatch.setattr("src.db.schema.init_db", lambda: None)
    monkeypatch.setattr("src.office.daily_summary.generate_daily_summary", lambda _d: None)
    monkeypatch.setattr("src.api.agent_status.update_agent_task", lambda *args, **kwargs: None)

    result = await orchestrator.run_pipeline(date_str="2026-03-16")

    assert result["date"] == "2026-03-16"
    assert result["articles_count"] == 1
    assert result["clusters_count"] == 1
    assert result["top3"] == top3
    assert result["drafts_path"] == drafts["drafts_path"]
    assert result["model_log"] == {
        "cluster": "cluster-model",
        "score": "score-model",
        "strategy": "strategy-model",
        "write": "writer-model",
    }
    save_daily_json.assert_called_once()
    mark_agent_awaiting_human.assert_called_once()
    save_topics.assert_called_once()
    save_drafts.assert_called_once()


@pytest.mark.asyncio
async def test_run_pipeline_handles_agent_exception(monkeypatch):
    monkeypatch.setattr(
        "src.scrapers.aggregator.run_aggregator",
        AsyncMock(return_value=[{"title": "A", "url": "https://example.com/a"}]),
    )

    async def raising_run(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        orchestrator,
        "ClusterAgent",
        lambda: SimpleNamespace(run=raising_run),
    )
    monkeypatch.setattr("src.db.queries.get_recent_topic_labels", lambda days=7: [])
    monkeypatch.setattr("src.api.agent_status.update_agent_task", lambda *args, **kwargs: None)

    result = await orchestrator.run_pipeline(date_str="2026-03-16")

    assert result == {}
