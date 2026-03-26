"""
AI Office 每日工作摘要產生器（Phase 6 第 2 層記憶）

從 agent_events.jsonl 讀取今日事件，產出:
  outputs/office_memory/summary_YYYY-MM-DD.md
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, date

from src.config import OUTPUTS_DIR
from src.utils.logger import get_logger

log = get_logger("office.daily_summary")

OFFICE_MEMORY_DIR = OUTPUTS_DIR / "office_memory"
EVENTS_LOG_PATH = OFFICE_MEMORY_DIR / "agent_events.jsonl"

AGENT_NAMES = {
    "ori": "Ori（研究）",
    "lala": "Lala（策略）",
    "craft": "Craft（內容）",
    "lumi": "Lumi（工程）",
    "sage": "Sage（分析）",
    "pixel": "Pixel（設計）",
}


def generate_daily_summary(target_date: str | None = None) -> str:
    """
    讀取 agent_events.jsonl，過濾今日事件，產出 Markdown 摘要。
    回傳寫出的檔案路徑。
    """
    d = target_date or date.today().isoformat()

    if not EVENTS_LOG_PATH.exists():
        log.warning("agent_events.jsonl 不存在，跳過摘要產生")
        return ""

    lines = EVENTS_LOG_PATH.read_text(encoding="utf-8").splitlines()
    today_events: list[dict] = []

    import json
    for line in lines:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            recorded = event.get("recorded_at", "")
            if recorded.startswith(d):
                today_events.append(event)
        except json.JSONDecodeError:
            continue

    if not today_events:
        log.info(f"[{d}] 今日無 AI Office 事件，跳過摘要")
        return ""

    # 統計各 agent 工作次數與任務
    agent_tasks: dict[str, list[str]] = defaultdict(list)
    blocked_events: list[dict] = []
    done_events: list[dict] = []
    artifact_count = 0

    for ev in today_events:
        agent_id = ev.get("agent_id", "")
        status = ev.get("status", "")
        task_meta = ev.get("task_meta") or {}
        title = task_meta.get("title") or ev.get("task", "")
        artifacts = task_meta.get("artifact_refs") or []

        if status == "working" and title:
            agent_tasks[agent_id].append(title)
        if status == "blocked":
            blocked_events.append(ev)
        if status == "done":
            done_events.append(ev)
        artifact_count += len(artifacts)

    # 最忙的 agent
    busiest = max(agent_tasks.items(), key=lambda x: len(x[1]), default=(None, []))

    lines_out: list[str] = [
        f"# AI Office 工作摘要 — {d}",
        "",
        f"> 產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> 今日事件總數：{len(today_events)}",
        "",
        "---",
        "",
        "## 今日各角色工作紀錄",
        "",
    ]

    for agent_id, tasks in sorted(agent_tasks.items()):
        name = AGENT_NAMES.get(agent_id, agent_id)
        unique_tasks = list(dict.fromkeys(tasks))  # deduplicate preserving order
        lines_out.append(f"### {name}")
        for t in unique_tasks:
            lines_out.append(f"- {t}")
        lines_out.append("")

    if not agent_tasks:
        lines_out.append("今日無角色工作紀錄。")
        lines_out.append("")

    lines_out += [
        "---",
        "",
        "## 摘要統計",
        "",
        f"- 活躍角色數：{len(agent_tasks)}",
        f"- 完成事件：{len(done_events)}",
        f"- 阻塞事件：{len(blocked_events)}",
        f"- 產出 artifact 引用數：{artifact_count}",
    ]

    if busiest[0]:
        lines_out.append(f"- 最忙角色：{AGENT_NAMES.get(busiest[0], busiest[0])}（{len(busiest[1])} 次工作）")

    if blocked_events:
        lines_out += ["", "---", "", "## 阻塞事件", ""]
        for ev in blocked_events:
            agent_id = ev.get("agent_id", "")
            reason = ev.get("task", "未知原因")
            lines_out.append(f"- **{AGENT_NAMES.get(agent_id, agent_id)}**：{reason}")

    lines_out.append("")

    content = "\n".join(lines_out)

    OFFICE_MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OFFICE_MEMORY_DIR / f"summary_{d}.md"
    out_path.write_text(content, encoding="utf-8")
    log.info(f"[{d}] AI Office 摘要已產出：{out_path}")
    return str(out_path)
