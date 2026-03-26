"""
週報引擎：整合 7 天數據，GPT-4o 生成週報
輸出：outputs/weekly_reports/week_YYYY-WW.md
"""
import json
from pathlib import Path
from datetime import datetime

from openai import OpenAI

from src.config import settings
from src.utils.file_io import load_daily_json, load_daily_md, save_weekly_md, list_recent_dates
from src.utils.logger import get_logger

log = get_logger("weekly_report")

PROMPT_PATH = Path(__file__).parent.parent / "ai" / "prompts" / "weekly_prompt.txt"
MODEL = "gpt-4o"


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _load_week_data() -> tuple[list[dict], list[str]]:
    """讀取最近 7 天的 threads_metrics 和 daily_reports 摘要"""
    dates = list_recent_dates("threads_metrics", 7)

    metrics = []
    for d in dates:
        data = load_daily_json("threads_metrics", d)
        if data:
            metrics.extend(data if isinstance(data, list) else [data])

    reports = []
    for d in list_recent_dates("daily_reports", 7):
        md = load_daily_md("daily_reports", d)
        if md:
            reports.append(f"## {d}\n{md[:500]}...")  # 每日報告只取前 500 字

    return metrics, reports


async def generate_weekly_report(week_str: str | None = None) -> str:
    """生成週報，回傳輸出路徑"""
    metrics, reports = _load_week_data()

    if not metrics and not reports:
        log.warning("沒有足夠的歷史數據生成週報")
        return ""

    if not settings.openai_api_key:
        log.warning("OPENAI_API_KEY 未設定，跳過週報生成")
        return ""

    client = OpenAI(api_key=settings.openai_api_key)
    prompt_template = _load_prompt()
    prompt = prompt_template.format(
        threads_metrics_json=json.dumps(metrics, ensure_ascii=False),
        daily_reports_json=json.dumps(reports, ensure_ascii=False),
    )

    log.info("GPT-4o 生成週報中...")
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4096,
        )
        content = response.choices[0].message.content
        path = save_weekly_md(content, week_str)
        log.info(f"週報已儲存：{path}")
        # Phase 4.4: Memory Fabric — 週報寫入 artifacts 表
        try:
            from src.workflows.runner import record_artifact
            record_artifact(
                producer="sage",
                artifact_type="weekly_report",
                file_path=str(path),
                metadata={"week_str": week_str or "", "metrics_count": len(metrics)},
            )
        except Exception as _ae:
            log.warning(f"[MemoryFabric] weekly_report artifact 記錄失敗：{_ae}")
        return str(path)
    except Exception as e:
        log.error(f"GPT 週報生成失敗：{e}")
        return ""
