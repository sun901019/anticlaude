"""
MemoryContext — 集中管理所有 Agent 可用的歷史記憶

所有 Agent 透過此模組取得格式化的記憶注入內容，
不再各自實作零散的 get_latest_insights() 呼叫。

回傳三種格式化段落，分別對應：
  - scorer_section  → ScoreAgent 用（類型表現 + 趨勢）
  - strategy_section → StrategyAgent 用（類型排行 + 策略建議）
  - writer_section  → WriterAgent 用（最佳 Hook + 字數 + hashtag）
"""
import json
from src.utils.logger import get_logger

log = get_logger("memory")


def _build_hot_topic_pattern(multi_insights: list[dict]) -> str:
    """
    從最新 3 期 audience_insights 彙整高互動主題模式。
    找出在多期均有高互動率的主題類型，供 Lala 選題參考。
    """
    if not multi_insights:
        return "  （尚無多期數據）"

    # 彙總各類型跨期互動率
    cat_totals: dict[str, list[float]] = {}
    for insight in multi_insights:
        cat_perf = insight.get("category_performance", {})
        if isinstance(cat_perf, str):
            try:
                cat_perf = json.loads(cat_perf)
            except Exception:
                continue
        for cat, data in cat_perf.items():
            if isinstance(data, dict):
                eng = data.get("avg_engagement", 0)
                cat_totals.setdefault(cat, []).append(float(eng))

    if not cat_totals:
        return "  （尚無分類數據）"

    # 計算各類型平均互動率並排序
    cat_avg = [
        (cat, sum(vals) / len(vals), len(vals))
        for cat, vals in cat_totals.items()
    ]
    cat_avg.sort(key=lambda x: x[1], reverse=True)

    lines = []
    for cat, avg_eng, periods in cat_avg:
        trend_label = f"連續 {periods} 期高互動" if avg_eng >= 3.0 else f"{periods} 期均值"
        lines.append(f"  - {cat}：均值互動率 {avg_eng:.1f}%（{trend_label}）")

    return "\n".join(lines)


def get_rich_memory_context() -> dict:
    """
    回傳所有 Agent 可用的完整記憶上下文。
    若 DB 無資料，回傳 has_data=False（不報錯，讓 Agent 照常跑）。
    """
    try:
        from src.feedback.analysis_engine import get_latest_insights, get_latest_insights_multi
        insights = get_latest_insights()
        multi_insights = get_latest_insights_multi(n=3)
    except Exception as e:
        log.warning(f"無法讀取 audience_insights：{e}")
        insights = None
        multi_insights = []

    top_hooks: list[dict] = []
    try:
        from src.db.queries import get_top_hooks
        top_hooks = get_top_hooks(limit=5)
    except Exception:
        pass

    if not insights:
        return {
            "has_data": False,
            "scorer_section": "",
            "strategy_section": "",
            "writer_section": "",
        }

    # ── 解析 category_performance ─────────────────────────────────────────────
    category_perf = insights.get("category_performance", {})
    if isinstance(category_perf, str):
        try:
            category_perf = json.loads(category_perf)
        except Exception:
            category_perf = {}

    # ── 解析 effective_hashtags ───────────────────────────────────────────────
    effective_hashtags = insights.get("effective_hashtags", [])
    if isinstance(effective_hashtags, str):
        try:
            effective_hashtags = json.loads(effective_hashtags)
        except Exception:
            effective_hashtags = []

    # ── 格式化各欄位 ──────────────────────────────────────────────────────────
    period_days    = insights.get("period_days", 30)
    best_day       = insights.get("best_posting_day", "N/A")
    best_hour      = insights.get("best_posting_hour", "N/A")
    trend          = insights.get("engagement_trend", "N/A")
    growth         = insights.get("growth_rate", "N/A")
    summary        = insights.get("strategic_summary", "")
    optimal_length = insights.get("avg_optimal_length", "N/A")
    hashtag_str    = "、".join(effective_hashtags) if effective_hashtags else "N/A"

    # 類型表現列表（依互動率排序）
    perf_entries = []
    for cat, data in category_perf.items():
        if isinstance(data, dict):
            perf_entries.append((cat, data))
    perf_entries.sort(key=lambda x: x[1].get("avg_engagement", 0), reverse=True)

    perf_lines = [
        f"  - {cat}：互動率 {d.get('avg_engagement', 'N/A')}%，"
        f"平均觀看 {d.get('avg_views', 'N/A')}，共 {d.get('count', 0)} 篇"
        for cat, d in perf_entries
    ]
    perf_text = "\n".join(perf_lines) if perf_lines else "  （尚無分類數據）"

    # 高互動 Hook 列表
    hook_lines = [
        f"  「{h['hook']}」（互動率 {h.get('engagement_rate', 'N/A')}%）"
        for h in top_hooks if h.get("hook")
    ]
    hook_text = "\n".join(hook_lines) if hook_lines else "  （尚無高互動 Hook 紀錄）"

    # 高互動主題模式（近 3 期趨勢，供 Lala 選題）
    hot_topic_pattern = _build_hot_topic_pattern(multi_insights)

    # ── scorer_section ────────────────────────────────────────────────────────
    scorer_section = (
        "---\n\n"
        "【歷史受眾表現數據（請參考此數據調整評分）】\n"
        f"分析週期：過去 {period_days} 天\n"
        f"各類型表現（互動率由高到低）：\n{perf_text}\n"
        f"最佳發文日：{best_day}  最佳發文時段：{best_hour} 時\n"
        f"互動率趨勢：{trend}  成長率：{growth}%\n"
        f"有效 hashtag：{hashtag_str}\n"
        f"策略建議：{summary}\n\n"
        "---"
    )

    # ── strategy_section ──────────────────────────────────────────────────────
    strategy_section = (
        f"【高互動主題模式（近 3 期趨勢）】\n{hot_topic_pattern}\n\n"
        f"各類型歷史互動表現（互動率由高到低）：\n{perf_text}\n"
        f"互動趨勢：{trend}，成長率：{growth}%\n"
        f"策略建議：{summary}"
    )

    # ── writer_section ────────────────────────────────────────────────────────
    writer_section = (
        "---\n\n"
        "【受眾偏好記憶（根據歷史數據調整文案風格）】\n"
        f"最佳發文時段：{best_day} {best_hour} 時\n"
        f"最適字數：{optimal_length} 字\n"
        f"有效 hashtag（優先使用這些）：{hashtag_str}\n"
        f"高互動 Hook 範例（學習感覺，不要逐字複製）：\n{hook_text}\n"
        f"策略建議：{summary}\n\n"
        "---"
    )

    return {
        "has_data": True,
        "category_performance": category_perf,
        "top_hooks": top_hooks,
        "best_posting_day": best_day,
        "best_posting_hour": best_hour,
        "effective_hashtags": effective_hashtags,
        "avg_optimal_length": optimal_length,
        "engagement_trend": trend,
        "growth_rate": growth,
        "strategic_summary": summary,
        "scorer_section": scorer_section,
        "strategy_section": strategy_section,
        "writer_section": writer_section,
    }
