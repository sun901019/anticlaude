"""
每日全流程串接：抓取 → 聚類 → 評分 → 策略 → 文案 → 存檔
支援 --dry-run 模式（使用 mock 資料，不呼叫真實 API）
"""
import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.file_io import save_daily_md, save_daily_json, load_raw_feed

log = get_logger("pipeline")

# ── Mock 資料（dry-run 用）────────────────────────────────────────────────────

MOCK_ARTICLES = [
    {
        "title": "OpenAI releases GPT-5 with enhanced reasoning",
        "url": "https://example.com/1",
        "source": "techcrunch",
        "summary": "OpenAI 發布 GPT-5，推理能力大幅提升，對各行業影響深遠。",
        "published_at": datetime.now().isoformat(),
        "language": "en",
    },
    {
        "title": "Anthropic Claude 4 now supports 1M context window",
        "url": "https://example.com/2",
        "source": "venturebeat",
        "summary": "Anthropic 的 Claude 4 支援百萬 token 上下文，開發者生產力提升。",
        "published_at": datetime.now().isoformat(),
        "language": "en",
    },
    {
        "title": "AI 工具讓台灣工程師效率提升 300%",
        "url": "https://example.com/3",
        "source": "serper_zh",
        "summary": "調查顯示，善用 AI 工具的台灣工程師平均省下每天 2.5 小時。",
        "published_at": datetime.now().isoformat(),
        "language": "zh-TW",
    },
]

MOCK_CLUSTERS = [
    {
        "cluster_label": "GPT-5 發布影響",
        "articles": ["https://example.com/1"],
        "merged_summary": "OpenAI GPT-5 推出，推理能力是 GPT-4 的 3 倍，對內容創作、程式開發影響最大。",
        "score": 9,
        "post_type": "趨勢解讀",
        "score_reason": "重大 AI 新聞，台灣科技工作者高度關注",
    },
    {
        "cluster_label": "Claude 長文本突破",
        "articles": ["https://example.com/2"],
        "merged_summary": "Anthropic Claude 4 百萬 token 上下文，讓整本書的分析成為可能。",
        "score": 8,
        "post_type": "AI工具實測",
        "score_reason": "實用性高，適合工具實測類內容",
    },
    {
        "cluster_label": "AI 提升工程師效率",
        "articles": ["https://example.com/3"],
        "merged_summary": "台灣工程師使用 AI 工具後每天節省 2.5 小時，職場競爭力大增。",
        "score": 8,
        "post_type": "個人成長",
        "score_reason": "本地化數據，對受眾切身相關",
    },
]


async def run_daily_pipeline(date_str: str | None = None, dry_run: bool = False) -> dict:
    """
    執行每日流程
    返回 {"daily_report_path": ..., "drafts_path": ..., "top3": [...]}
    """
    d = date_str or datetime.now().strftime("%Y-%m-%d")
    log.info(f"{'[DRY-RUN] ' if dry_run else ''}開始執行每日 pipeline — {d}")

    # Step 1: 資料抓取
    if dry_run:
        articles = MOCK_ARTICLES
        log.info(f"[DRY-RUN] 使用 mock 素材：{len(articles)} 則")
    else:
        from src.scrapers.aggregator import run_aggregator
        articles = await run_aggregator(d)

    if not articles:
        log.error("沒有抓到任何素材，流程終止")
        return {}

    # Step 2: 取得歷史主題（供聚類去重）
    recent_labels: list[str] = []
    if not dry_run:
        try:
            from src.db.queries import get_recent_topic_labels
            recent_labels = get_recent_topic_labels(days=7)
            if recent_labels:
                log.info(f"歷史去重：過去 7 天已有 {len(recent_labels)} 個主題，避免重複")
        except Exception as e:
            log.warning(f"無法讀取歷史主題：{e}")

    # Step 3: Claude 聚類（Gemini 暫停）
    if dry_run:
        clusters = MOCK_CLUSTERS
        log.info("[DRY-RUN] 使用 mock 聚類結果")
    else:
        from src.ai.claude_cluster import cluster_articles_claude
        clusters = await cluster_articles_claude(articles, recent_labels=recent_labels)

    if not clusters:
        log.error("聚類失敗（Gemini + Claude 都無法完成），流程終止")
        return {}

    # Step 3: Claude 評分
    if dry_run:
        scored = MOCK_CLUSTERS
        log.info("[DRY-RUN] 使用 mock 評分結果")
    else:
        from src.ai.claude_scorer import score_topics
        scored = await score_topics(clusters)

    # Step 4: GPT 策略 Top 3
    if dry_run:
        strategy = {
            "top3": [
                {"cluster_label": t["cluster_label"], "rank": i + 1,
                 "strategy_reason": "mock 策略", "post_type": t["post_type"]}
                for i, t in enumerate(MOCK_CLUSTERS[:3])
            ],
            "weekly_insight": "[DRY-RUN] mock 洞察",
        }
    else:
        from src.ai.gpt_strategist import select_top3
        strategy = await select_top3(scored)

    top3 = strategy.get("top3", [])
    weekly_insight = strategy.get("weekly_insight", "")

    # Step 5: 生成每日報告
    report_lines = [
        f"# 每日素材報告 — {d}\n",
        f"## 週度洞察\n{weekly_insight}\n",
        f"## Top 3 主題\n",
    ]
    for item in top3:
        label = item.get("cluster_label", "")
        topic = next((t for t in scored if t["cluster_label"] == label), {})
        report_lines.append(
            f"### {item['rank']}. {label}\n"
            f"- **類型**：{item.get('post_type', '')}\n"
            f"- **評分**：{topic.get('score', 'N/A')}\n"
            f"- **策略理由**：{item.get('strategy_reason', '')}\n"
            f"- **摘要**：{topic.get('merged_summary', '')}\n"
        )
    report_lines.append("\n## 所有主題評分\n")
    for t in scored:
        report_lines.append(
            f"- [{t.get('score', 0)}分] **{t['cluster_label']}** — {t.get('score_reason', '')}\n"
        )

    report_md = "\n".join(report_lines)
    save_daily_md("daily_reports", report_md, d)

    # Step 6: 文案生成
    drafts_list = []
    if dry_run:
        drafts_path = ""
        log.info("[DRY-RUN] 跳過文案生成")
    else:
        from src.ai.claude_writer import write_drafts
        from src.ai.skill_loader import load_composite_skill
        geo_skill = load_composite_skill("geo_optimization_engine") or ""
        drafts_path, drafts_list = await write_drafts(top3, scored, d, extra_skill=geo_skill)

    # Step 7: 儲存結構化 JSON（供 dashboard 使用）
    if not dry_run:
        # 建立 cluster_label → scored topic 的 mapping
        topic_map = {t["cluster_label"]: t for t in scored}
        # 建立 cluster_label → draft 的 mapping
        draft_map = {d_item.get("cluster_label", ""): d_item for d_item in drafts_list}

        structured = {
            "date": d,
            "weekly_insight": weekly_insight,
            "top3": [
                {
                    **item,
                    **topic_map.get(item["cluster_label"], {}),
                    "draft": draft_map.get(item["cluster_label"], {}),
                }
                for item in top3
            ],
            "all_topics": scored,
        }
        save_daily_json("daily_reports", structured, d)

    # Step 8: 寫入 SQLite DB（topics + drafts）
    if not dry_run:
        try:
            from src.db.schema import init_db
            from src.db.queries import save_topics, save_drafts
            init_db()
            # 加上 rank 欄位再寫入
            ranked_scored = [dict(t, rank=(i + 1) if t["cluster_label"] in
                             {x["cluster_label"] for x in top3} else None)
                             for i, t in enumerate(scored)]
            topic_id_map = save_topics(ranked_scored, d)
            if drafts_list:
                save_drafts(drafts_list, topic_id_map, d)
        except Exception as e:
            log.warning(f"DB 寫入失敗（不影響主流程）：{e}")

    log.info(f"Pipeline 完成 — {d}")
    return {
        "date": d,
        "articles_count": len(articles),
        "clusters_count": len(clusters),
        "top3": top3,
        "drafts_path": drafts_path,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AntiClaude 每日 Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="使用 mock 資料，不呼叫真實 API")
    parser.add_argument("--date", type=str, help="指定日期 YYYY-MM-DD（預設今日）")
    args = parser.parse_args()

    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    result = asyncio.run(run_daily_pipeline(date_str=args.date, dry_run=args.dry_run))
    if result:
        print(f"\n[OK] 完成！")
        print(f"   素材數：{result.get('articles_count', 0)}")
        print(f"   主題數：{result.get('clusters_count', 0)}")
        print(f"   Top 3：{[t['cluster_label'] for t in result.get('top3', [])]}")
    else:
        print("[FAIL] Pipeline 執行失敗，請檢查 logs/")
