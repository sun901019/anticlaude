"""
Structured agent status state for AI Office.

Phase 1 adds a typed task model while keeping compatibility with the
existing set_agent_status(agent_id, status, task) call pattern used by agents.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, AsyncIterator

from src.config import OUTPUTS_DIR
from src.db.connection import db

AUTO_IDLE_MINUTES = 30
NOTIFY_DEDUP_MINUTES = 10

AGENTS: dict[str, dict[str, str]] = {
    "ori": {
        "nickname": "Ori",
        "role": "研究主導",
        "emoji": "RF",
        "desc": "蒐集訊號、彙整資料，建立研究脈絡與競品洞察。",
    },
    "lala": {
        "nickname": "Lala",
        "role": "策略主導",
        "emoji": "ST",
        "desc": "選定角度、排定優先順序，制定內容定位策略。",
    },
    "craft": {
        "nickname": "Craft",
        "role": "內容主導",
        "emoji": "WR",
        "desc": "將創意轉化為可發佈的文案草稿與貼文。",
    },
    "lumi": {
        "nickname": "Lumi",
        "role": "工程主導",
        "emoji": "EN",
        "desc": "建置系統、修復串接，負責程式碼交付與部署。",
    },
    "sage": {
        "nickname": "Sage",
        "role": "分析主導",
        "emoji": "AN",
        "desc": "回顧成效、評估決策，解讀數據與表現訊號。",
    },
    "pixel": {
        "nickname": "Pixel",
        "role": "設計主導",
        "emoji": "DS",
        "desc": "塑造視覺呈現、設計系統與介面細節打磨。",
    },
}


def _now_iso() -> str:
    return datetime.now().isoformat()


def _should_send_human_notification(signature: str) -> bool:
    """
    Best-effort in-process dedup for awaiting_human notifications.

    This prevents the same approval/report event from notifying the operator
    repeatedly within a short time window.
    """
    now = datetime.now()

    # Lazily keep the state local to this module.
    global _recent_human_notifications
    live: dict[str, str] = {}
    for sig, seen in _recent_human_notifications.items():
        try:
            seen_at = datetime.fromisoformat(seen)
            if now - seen_at <= timedelta(minutes=NOTIFY_DEDUP_MINUTES):
                live[sig] = seen
        except Exception:
            continue
    _recent_human_notifications = live

    last_seen = _recent_human_notifications.get(signature)
    if last_seen:
        try:
            seen_at = datetime.fromisoformat(last_seen)
            if now - seen_at <= timedelta(minutes=NOTIFY_DEDUP_MINUTES):
                return False
        except Exception:
            pass

    # Durable dedup so backend restarts or repeated worker paths do not spam
    # the operator with the same approval/report notification.
    try:
        with db() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notification_dispatches (
                    signature       TEXT PRIMARY KEY,
                    channel         TEXT NOT NULL,
                    event_type      TEXT,
                    ref_id          TEXT,
                    payload_json    TEXT,
                    last_sent_at    TEXT NOT NULL,
                    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            row = conn.execute(
                "SELECT last_sent_at FROM notification_dispatches WHERE signature=?",
                (signature,),
            ).fetchone()
            if row:
                try:
                    seen_at = datetime.fromisoformat(row["last_sent_at"])
                    if now - seen_at <= timedelta(minutes=NOTIFY_DEDUP_MINUTES):
                        _recent_human_notifications[signature] = row["last_sent_at"]
                        return False
                except Exception:
                    pass
            now_iso = now.isoformat()
            conn.execute(
                """
                INSERT INTO notification_dispatches (
                    signature, channel, event_type, ref_id, payload_json, last_sent_at, updated_at
                ) VALUES (?, 'line', 'awaiting_human', '', '{}', ?, ?)
                ON CONFLICT(signature) DO UPDATE SET
                    last_sent_at=excluded.last_sent_at,
                    updated_at=excluded.updated_at
                """,
                (signature, now_iso, now_iso),
            )
    except Exception:
        # Fall back to in-process dedup only; notification dedup must never
        # block the operator workflow if DB is temporarily unavailable.
        pass

    _recent_human_notifications[signature] = now.isoformat()
    return True


def _default_task() -> dict[str, Any]:
    return {
        "id": "",
        "title": "",
        "task_type": "",
        "status": "idle",
        "priority": "normal",
        "started_at": "",
        "updated_at": _now_iso(),
        "source_agent_id": "",
        "target_agent_id": "",
        "artifact_refs": [],
        "action_type": "",
        "ref_id": "",
    }


_status: dict[str, dict[str, Any]] = {
    agent_id: {
        "status": "idle",
        "task": "",
        "updated_at": _now_iso(),
        "task_meta": _default_task(),
        "last_task": "",
        "last_active_at": "",
    }
    for agent_id in AGENTS
}

_subscribers: list[asyncio.Queue[str]] = []
OFFICE_MEMORY_DIR = OUTPUTS_DIR / "office_memory"
EVENTS_LOG_PATH = OFFICE_MEMORY_DIR / "agent_events.jsonl"
_recent_human_notifications: dict[str, str] = {}


def _state_log_path() -> Path:
    from datetime import date
    return OFFICE_MEMORY_DIR / f"agent_state_{date.today().isoformat()}.jsonl"


def _persist_state(agent_id: str) -> None:
    """每次狀態變更時寫入今日 state log，後端重啟可恢復"""
    try:
        OFFICE_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        state = _merge_agent(agent_id)
        entry = {"agent_id": agent_id, "saved_at": _now_iso(), "state": state}
        with _state_log_path().open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def restore_today_state() -> None:
    """啟動時讀取今日 state log，恢復最後一次狀態（跳過 idle 與逾時狀態）"""
    path = _state_log_path()
    if not path.exists():
        return
    latest: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            entry = json.loads(line)
            aid = entry.get("agent_id")
            if aid and aid in _status:
                latest[aid] = entry["state"]
        except Exception:
            continue
    now = datetime.now()
    for aid, saved in latest.items():
        if saved.get("status") not in ("working", "awaiting_human"):
            continue
        # 超過 AUTO_IDLE_MINUTES 的舊狀態不恢復，避免 demo 殘留
        try:
            updated = datetime.fromisoformat(saved.get("updated_at", ""))
            if now - updated > timedelta(minutes=AUTO_IDLE_MINUTES):
                continue
        except Exception:
            continue
        _status[aid]["status"] = saved["status"]
        _status[aid]["task"] = saved.get("task", "")
        _status[aid]["updated_at"] = saved.get("updated_at", _now_iso())
        _status[aid]["task_meta"] = saved.get("task_meta") or _default_task()


def _merge_agent(agent_id: str) -> dict[str, Any]:
    return {
        **AGENTS[agent_id],
        **deepcopy(_status[agent_id]),
    }


def get_all_status() -> dict[str, dict[str, Any]]:
    """Return a full agent state snapshot."""
    return {agent_id: _merge_agent(agent_id) for agent_id in AGENTS}


def _emit_snapshot(agent_ids: list[str] | None = None) -> None:
    ids = agent_ids or list(AGENTS.keys())
    payload = json.dumps({agent_id: _merge_agent(agent_id) for agent_id in ids})
    dead: list[asyncio.Queue[str]] = []
    for queue in list(_subscribers):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            # Queue full = client likely disconnected; schedule for removal
            dead.append(queue)
    for q in dead:
        try:
            _subscribers.remove(q)
        except ValueError:
            pass


def _append_event(agent_id: str) -> None:
    OFFICE_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    state = _merge_agent(agent_id)
    event = {
        "recorded_at": _now_iso(),
        "agent_id": agent_id,
        "status": state["status"],
        "task": state["task"],
        "task_meta": state["task_meta"],
    }
    with EVENTS_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    _persist_state(agent_id)


def get_recent_events(limit: int = 50, agent_id: str | None = None) -> list[dict[str, Any]]:
    """Return recent AI Office events from the local event log."""
    if not EVENTS_LOG_PATH.exists():
        return []

    lines = EVENTS_LOG_PATH.read_text(encoding="utf-8").splitlines()
    events: list[dict[str, Any]] = []
    for line in reversed(lines):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            if agent_id and event.get("agent_id") != agent_id:
                continue
            events.append(event)
            if len(events) >= limit:
                break
        except json.JSONDecodeError:
            continue
    return events


def run_demo_handoff() -> list[dict[str, str]]:
    """Emit a minimal three-agent handoff so AI Office can show workflow movement."""
    shared_task_id = uuid.uuid4().hex[:8]
    start = _now_iso()

    update_agent_task(
        "ori",
        status="working",
        task="整理今日 AI 訊號",
        title="整理今日 AI 訊號",
        task_type="research",
        priority="high",
        source_agent_id="",
        target_agent_id="lala",
        artifact_refs=["outputs/office_memory/demo_research_packet.md"],
        task_id=shared_task_id,
        started_at=start,
    )
    update_agent_task(
        "lala",
        status="working",
        task="選定內容角度",
        title="選定內容角度",
        task_type="strategy",
        priority="high",
        source_agent_id="ori",
        target_agent_id="craft",
        artifact_refs=["outputs/office_memory/demo_strategy_brief.md"],
        task_id=shared_task_id,
        started_at=start,
    )
    update_agent_task(
        "craft",
        status="working",
        task="撰寫 Threads 草稿",
        title="撰寫 Threads 草稿",
        task_type="content",
        priority="high",
        source_agent_id="lala",
        target_agent_id="pixel",
        artifact_refs=["outputs/office_memory/demo_threads_draft.md"],
        task_id=shared_task_id,
        started_at=start,
    )
    return [
        {"from": "ori", "to": "lala", "task": "整理今日 AI 訊號"},
        {"from": "lala", "to": "craft", "task": "選定內容角度"},
        {"from": "craft", "to": "pixel", "task": "撰寫 Threads 草稿"},
    ]


def _check_auto_idle() -> None:
    now = datetime.now()
    changed_ids: list[str] = []
    for agent_id, state in _status.items():
        if state["status"] not in ("working", "blocked", "handoff_pending", "awaiting_human"):
            continue
        updated_at = datetime.fromisoformat(state["updated_at"])
        if now - updated_at <= timedelta(minutes=AUTO_IDLE_MINUTES):
            continue
        state["status"] = "idle"
        state["task"] = ""
        state["updated_at"] = _now_iso()
        state["task_meta"] = _default_task()
        changed_ids.append(agent_id)

    if changed_ids:
        # 儲存 last_task 再清除
        for agent_id in changed_ids:
            s = _status[agent_id]
            last_title = s.get("task_meta", {}).get("title") or s.get("task", "")
            if last_title:
                s["last_task"] = last_title
                s["last_active_at"] = s.get("updated_at", _now_iso())
        _emit_snapshot(changed_ids)


def mark_agent_done(agent_id: str, artifact_refs: list[str] | None = None) -> None:
    """Mark agent task as done and transition to idle after logging."""
    if agent_id not in _status:
        return
    timestamp = _now_iso()
    current = _status[agent_id]
    task_meta = deepcopy(current.get("task_meta") or _default_task())
    task_meta["status"] = "done"
    task_meta["updated_at"] = timestamp
    if artifact_refs is not None:
        task_meta["artifact_refs"] = list(artifact_refs)
    current["task_meta"] = task_meta
    current["updated_at"] = timestamp
    _append_event(agent_id)
    _emit_snapshot([agent_id])
    # 儲存「上次任務」記錄，idle 後仍可顯示
    last_title = task_meta.get("title") or current.get("task", "")
    if last_title:
        current["last_task"] = last_title
        current["last_active_at"] = timestamp
    # transition to idle — 完整清除 task_meta 避免舊數據殘留
    current["status"] = "idle"
    current["task"] = ""
    current["task_meta"] = _default_task()
    current["updated_at"] = _now_iso()
    _emit_snapshot([agent_id])


def mark_agent_blocked(agent_id: str, reason: str = "") -> None:
    """Mark agent as blocked (waiting for external input or dependency)."""
    if agent_id not in _status:
        return
    timestamp = _now_iso()
    current = _status[agent_id]
    task_meta = deepcopy(current.get("task_meta") or _default_task())
    task_meta["status"] = "blocked"
    task_meta["updated_at"] = timestamp
    current["status"] = "blocked"
    current["task"] = reason or current.get("task", "")
    current["updated_at"] = timestamp
    current["task_meta"] = task_meta
    _append_event(agent_id)
    _emit_snapshot([agent_id])


def mark_agent_handoff_pending(agent_id: str, target_agent_id: str) -> None:
    """Mark agent as waiting for handoff acceptance."""
    if agent_id not in _status:
        return
    timestamp = _now_iso()
    current = _status[agent_id]
    task_meta = deepcopy(current.get("task_meta") or _default_task())
    task_meta["status"] = "handoff_pending"
    task_meta["target_agent_id"] = target_agent_id
    task_meta["updated_at"] = timestamp
    current["status"] = "handoff_pending"
    current["updated_at"] = timestamp
    current["task_meta"] = task_meta
    _append_event(agent_id)
    _emit_snapshot([agent_id])


def mark_agent_awaiting_human(
    agent_id: str,
    message: str = "",
    action_type: str = "",
    ref_id: str = "",
    artifact_refs: list[str] | None = None,
) -> None:
    """
    標記 agent 為等待人類決策狀態。
    action_type 讓前端知道要顯示哪種行動按鈕：
      'approve_purchase' | 'select_draft' | 'confirm_analysis'
    ref_id 關聯的 candidate_id 或 analysis_id。
    """
    if agent_id not in _status:
        return
    timestamp = _now_iso()
    current = _status[agent_id]
    task_meta = deepcopy(current.get("task_meta") or _default_task())
    task_meta["status"] = "awaiting_human"
    task_meta["updated_at"] = timestamp
    task_meta["action_type"] = action_type
    task_meta["ref_id"] = ref_id
    if artifact_refs is not None:
        task_meta["artifact_refs"] = list(artifact_refs)
    current["status"] = "awaiting_human"
    current["task"] = message or current.get("task", "")
    current["updated_at"] = timestamp
    current["task_meta"] = task_meta
    _append_event(agent_id)
    _emit_snapshot([agent_id])

    # LINE 通知（deduplicated to avoid repeated spam for the same decision event）
    try:
        import asyncio as _asyncio
        from src.utils.notify import send_line_notify
        notify_msg = f"[AntiClaude] {message or agent_id} 等待你決策"
        if action_type == "approve_purchase":
            notify_msg = f"[Flow Lab] 選品報告完成，請決策：{message}"
        elif action_type == "select_draft":
            notify_msg = f"[AntiClaude] 今日文案草稿已就緒，請選擇發文版本"
        signature = json.dumps(
            {
                "agent_id": agent_id,
                "action_type": action_type,
                "ref_id": ref_id,
                "message": message or "",
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        if not _should_send_human_notification(signature):
            return
        try:
            loop = _asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(send_line_notify(notify_msg))
            else:
                loop.run_until_complete(send_line_notify(notify_msg))
        except RuntimeError:
            _asyncio.run(send_line_notify(notify_msg))
    except Exception:
        pass


def set_agent_status(agent_id: str, status: str, task: str = "") -> None:
    """
    Compatibility helper used by existing agents.

    This updates the plain-text task and derives a minimal structured task.
    """
    if agent_id not in _status:
        return

    current = _status[agent_id]
    timestamp = _now_iso()
    current["status"] = status
    current["task"] = task
    current["updated_at"] = timestamp

    task_meta = deepcopy(current.get("task_meta") or _default_task())
    if status == "working":
        if not task_meta["id"]:
            task_meta["id"] = uuid.uuid4().hex[:8]
            task_meta["started_at"] = timestamp
        if task:
            task_meta["title"] = task
        task_meta["status"] = "in_progress"
    else:
        task_meta["status"] = "idle"
        task_meta["target_agent_id"] = ""
    task_meta["updated_at"] = timestamp
    current["task_meta"] = task_meta

    _append_event(agent_id)
    _emit_snapshot([agent_id])


def update_agent_task(
    agent_id: str,
    *,
    status: str,
    task: str = "",
    title: str = "",
    task_type: str = "",
    priority: str = "normal",
    source_agent_id: str = "",
    target_agent_id: str = "",
    artifact_refs: list[str] | None = None,
    task_id: str = "",
    started_at: str = "",
) -> None:
    """Update an agent with structured task metadata."""
    if agent_id not in _status:
        return

    timestamp = _now_iso()
    resolved_title = title or task
    resolved_status = "in_progress" if status == "working" else "idle"
    existing = _status[agent_id].get("task_meta") or _default_task()

    task_meta = {
        "id": task_id or existing.get("id") or uuid.uuid4().hex[:8],
        "title": resolved_title,
        "task_type": task_type or existing.get("task_type", ""),
        "status": resolved_status,
        "priority": priority or existing.get("priority", "normal"),
        "started_at": started_at or existing.get("started_at") or timestamp,
        "updated_at": timestamp,
        "source_agent_id": source_agent_id,
        "target_agent_id": target_agent_id,
        "artifact_refs": list(artifact_refs or []),
    }

    _status[agent_id] = {
        "status": status,
        "task": task or resolved_title,
        "updated_at": timestamp,
        "task_meta": task_meta,
    }
    _append_event(agent_id)
    _emit_snapshot([agent_id])


async def sse_generator() -> AsyncIterator[str]:
    """SSE stream for AI Office live updates."""
    queue: asyncio.Queue[str] = asyncio.Queue(maxsize=50)
    _subscribers.append(queue)
    try:
        yield f"data: {json.dumps(get_all_status())}\n\n"
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=25)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                _check_auto_idle()
                yield ": keepalive\n\n"
    finally:
        if queue in _subscribers:
            _subscribers.remove(queue)
