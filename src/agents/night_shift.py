# encoding: utf-8
"""
Night Shift Agent — Phase 5

夜間自治推進：自動執行低風險任務，生成夜班摘要，發 LINE 通知。

設計原則：
- 純新增，不動現有排程（08:00/20:00/週一09:00）
- 只執行無需人工授權的任務（content_research / data_analysis）
- 不發布貼文、不核准選品、不做有副作用的操作
- 任何失敗都靜默繼續，不中斷其他任務
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger

log = get_logger("night_shift")

# 只執行「無副作用」的自治任務
AUTONOMOUS_TASKS = ["content_research", "data_analysis"]

# 夜班摘要輸出目錄
REPORTS_DIR = Path(__file__).parent.parent.parent / "_hub" / "reports"
SPRINT_FILE = Path(__file__).parent.parent.parent / "ai" / "state" / "sprint.md"


# ── 數據收集 ──────────────────────────────────────────────────────────────────

def _count_sprint_tasks() -> dict[str, int]:
    """讀 sprint.md，統計各狀態任務數量"""
    counts = {"done": 0, "todo": 0, "in_progress": 0, "blocked": 0}
    try:
        text = SPRINT_FILE.read_text(encoding="utf-8")
        counts["done"]        = len(re.findall(r"^\- \[x\]", text, re.MULTILINE))
        counts["todo"]        = len(re.findall(r"^\- \[ \]", text, re.MULTILINE))
        counts["in_progress"] = len(re.findall(r"^\- \[~\]", text, re.MULTILINE))
        counts["blocked"]     = len(re.findall(r"^\- \[!\]", text, re.MULTILINE))
    except Exception:
        pass
    return counts


def _get_db_stats() -> dict[str, Any]:
    """從 DB 讀取今日數據快照"""
    today = datetime.now().strftime("%Y-%m-%d")
    stats: dict[str, Any] = {"posts_today": 0, "drafts_today": 0, "pending_review": 0}
    try:
        from src.db.connection import db
        with db() as conn:
            stats["posts_today"] = conn.execute(
                "SELECT COUNT(*) FROM posts WHERE date(posted_at)=?", (today,)
            ).fetchone()[0] or 0
            stats["drafts_today"] = conn.execute(
                "SELECT COUNT(*) FROM drafts WHERE date(created_at)=?", (today,)
            ).fetchone()[0] or 0
            try:
                stats["pending_review"] = conn.execute(
                    "SELECT COUNT(*) FROM review_items WHERE status='pending'"
                ).fetchone()[0] or 0
            except Exception:
                pass
    except Exception:
        pass
    return stats


# ── 摘要生成 ──────────────────────────────────────────────────────────────────

def _build_suggestions(db_stats: dict[str, Any], sprint_counts: dict[str, int]) -> str:
    lines = []
    if db_stats["drafts_today"] > 0:
        lines.append(f"1. 選擇今日 {db_stats['drafts_today']} 篇草稿發布（前往首頁 /）")
    else:
        lines.append("1. 觸發 Pipeline 生成今日草稿（前往 CEO Console /chat）")
    if db_stats["pending_review"] > 0:
        lines.append(f"2. 處理 {db_stats['pending_review']} 筆待審 Review Queue（前往 /review）")
    if sprint_counts["blocked"] > 0:
        lines.append(f"3. 解決 {sprint_counts['blocked']} 個阻塞任務（查看 sprint.md）")
    if not lines:
        lines.append("1. 系統運行正常，查看晨報確認今日計畫")
    return "\n".join(lines)


def _write_nightly_summary(
    date_str: str,
    sprint_counts: dict[str, int],
    db_stats: dict[str, Any],
    task_results: list[dict],
) -> Path:
    """生成並寫入夜班摘要 markdown"""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    task_lines = []
    for r in task_results:
        if r.get("success"):
            task_lines.append(f"- ✅ {r['task_type']}（by {r.get('agent', '?')}）")
        else:
            task_lines.append(
                f"- ❌ {r['task_type']} 失敗：{r.get('error', '未知')}"
            )
    tasks_block = "\n".join(task_lines) if task_lines else "- （無自動任務）"

    suggestions = _build_suggestions(db_stats, sprint_counts)

    content = f"""# Nightly Summary — {date_str}
> 生成時間：{now_str}
> 生成者：AntiClaude Night Shift（自動）

---

## 今晚自動執行任務
{tasks_block}

## 今日數據快照
- 今日發布：{db_stats['posts_today']} 篇
- 今日草稿：{db_stats['drafts_today']} 篇
- 待審 Review Queue：{db_stats['pending_review']} 筆

## Sprint 狀態
- ✅ 已完成：{sprint_counts['done']} 項
- 🔲 待辦：{sprint_counts['todo']} 項
- 🔄 進行中：{sprint_counts['in_progress']} 項
- 🚫 阻塞：{sprint_counts['blocked']} 項

## 明日建議
{suggestions}

---
*由 AntiClaude Night Shift 自動生成*
"""
    out_path = REPORTS_DIR / f"nightly_summary_{date_str}.md"
    out_path.write_text(content, encoding="utf-8")
    log.info(f"[NightShift] 夜班摘要已寫入：{out_path}")
    return out_path


# ── 公開 API ──────────────────────────────────────────────────────────────────

def get_last_night_shift() -> dict[str, Any]:
    """讀取最近的夜班摘要，供 status endpoint 使用"""
    try:
        files = sorted(REPORTS_DIR.glob("nightly_summary_*.md"), reverse=True)
        if not files:
            return {"ran": False, "message": "尚無夜班記錄"}
        latest = files[0]
        date_str = latest.stem.replace("nightly_summary_", "")
        content = latest.read_text(encoding="utf-8")
        success_count = content.count("✅")
        failed_count = content.count("❌")
        return {
            "ran": True,
            "date": date_str,
            "tasks_success": success_count,
            "tasks_failed": failed_count,
            "summary_preview": content[:500],
        }
    except Exception as e:
        return {"ran": False, "error": str(e)}


async def run_night_shift() -> dict[str, Any]:
    """
    夜班主函數：執行所有自治任務，生成摘要，發 LINE 通知。

    Returns:
        執行結果摘要 dict
    """
    date_str = datetime.now().strftime("%Y-%m-%d")
    log.info(f"[NightShift] 開始夜班 {date_str}...")

    # 1. Sprint 狀態快照
    sprint_counts = _count_sprint_tasks()
    log.info(f"[NightShift] Sprint 狀態：{sprint_counts}")

    # 2. DB 數據快照
    db_stats = _get_db_stats()

    # 3. 執行自治任務（逐一，失敗不影響後續）
    from src.agents.dynamic_orchestrator import run_task
    task_results: list[dict] = []

    for task_type in AUTONOMOUS_TASKS:
        log.info(f"[NightShift] 執行任務：{task_type}")
        try:
            result = await run_task(task_type, {})
            result["task_type"] = task_type
            task_results.append(result)
            status = "✅" if result.get("success") else "❌"
            log.info(f"[NightShift] {status} {task_type}")
        except Exception as e:
            task_results.append({
                "task_type": task_type,
                "success": False,
                "error": str(e),
                "agent": "none",
            })
            log.error(f"[NightShift] {task_type} 失敗：{e}")

    # 4. 生成夜班摘要
    summary_path = _write_nightly_summary(
        date_str, sprint_counts, db_stats, task_results
    )

    # 5. LINE 通知（token 未設定時靜默跳過）
    success_count = sum(1 for r in task_results if r.get("success"))
    try:
        from src.utils.notify import send_line_notify
        msg = (
            f"[AntiClaude] 🌙 夜班完成 {date_str}\n"
            f"自動任務：{success_count}/{len(task_results)} 完成\n"
            f"Sprint：{sprint_counts['done']} 已完成 / {sprint_counts['todo']} 待辦\n"
            f"今日草稿：{db_stats['drafts_today']} 篇 | 待審：{db_stats['pending_review']} 筆"
        )
        await send_line_notify(msg)
    except Exception:
        pass

    log.info(f"[NightShift] 夜班完成：{success_count}/{len(AUTONOMOUS_TASKS)} 任務成功")
    return {
        "date": date_str,
        "tasks_run": len(task_results),
        "tasks_success": success_count,
        "sprint_counts": sprint_counts,
        "db_stats": db_stats,
        "summary_path": str(summary_path),
        "task_results": task_results,
    }
