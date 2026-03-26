"""
Craft 選品報告模組：Claude Sonnet 自動產出 Markdown 報告
輸入：product_name + 完整 analysis dict
輸出：(report_markdown: str, summary: dict)
"""
import json
from datetime import date

import anthropic

from src.config import settings
from src.utils.logger import get_logger

log = get_logger("craft_reporter")

MODEL = "claude-sonnet-4-6"


def generate_selection_report(product_name: str, analysis: dict) -> tuple[str, dict]:
    """
    Craft 自動產選品報告
    回傳 (markdown報告文字, summary_json dict)
    失敗時回傳簡易 fallback 報告
    """
    score_total = analysis.get("score_total", 0)
    viability_band = analysis.get("viability_band", "watchlist")
    reasoning = analysis.get("reasoning", "")
    scores = {
        "需求強度": analysis.get("demand_score", "-"),
        "競爭健康度": analysis.get("competition_score", "-"),
        "利潤空間": analysis.get("profit_score", "-"),
        "痛點機會": analysis.get("pain_point_score", "-"),
        "品牌適配": analysis.get("brand_fit_score", "-"),
    }
    competitor_data = analysis.get("competitor_data", {})
    pain_points = competitor_data.get("pain_points", [])
    price_range = competitor_data.get("price_range", {})
    financials = analysis.get("financials", {})

    today = date.today().isoformat()
    fallback_md = f"""# 選品報告：{product_name}
> 分析日期：{today} ｜ 評分：{score_total}/50 ｜ 建議：{viability_band}

## 一句話結論
{reasoning or '請參考評分細項進行決策。'}

## 評分細項
| 維度 | 分數 |
|------|------|
""" + "\n".join(f"| {k} | {v}/10 |" for k, v in scores.items())

    fallback_summary = {
        "score": score_total,
        "role": analysis.get("recommended_role", ""),
        "top_pain_points": pain_points[:3],
        "viability_band": viability_band,
    }

    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY 未設定，使用 fallback 報告")
        return fallback_md, fallback_summary

    pain_text = "、".join(pain_points[:5]) if pain_points else "無明確資料"
    price_text = f"NT${price_range.get('min', '?')} ~ NT${price_range.get('max', '?')}" if price_range else "無資料"
    financials_text = json.dumps(financials, ensure_ascii=False) if financials else "無財務資料"

    prompt = f"""你是 Flow Lab 的內容策略師（Craft）。請為以下選品分析產出一份選品報告。

商品名稱：{product_name}
分析日期：{today}
加權總分：{score_total}/50
建議定位：{analysis.get('recommended_role', '未定')}（{viability_band}）

評分細項：
{json.dumps(scores, ensure_ascii=False)}

競品市場價格區間：{price_text}
主要痛點：{pain_text}
財務資訊：{financials_text}
分析說明：{reasoning or '無'}

請以下方格式輸出 Markdown 報告（只輸出報告本文，不要多餘說明）：

# 選品報告：{product_name}
> 分析日期：{today} ｜ 評分：{score_total}/50 ｜ 建議：{viability_band}

## 一句話結論
（2句話說明是否建議進貨及主要理由）

## 評分細項
| 維度 | 分數 | 說明 |
（各維度說明，含分數）

## 主要風險
（2-3個風險點）

## 差異化機會
（從痛點找到的改善機會，2-3點）

## 財務試算
（簡單表格：建議進貨價/售價/預估毛利率）"""

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        report_md = message.content[0].text.strip()
        summary = {
            "score": score_total,
            "role": analysis.get("recommended_role", ""),
            "top_pain_points": pain_points[:3],
            "viability_band": viability_band,
        }
        log.info(f"Craft 報告產出完成：{product_name}（{len(report_md)} 字）")
        return report_md, summary
    except Exception as e:
        log.error(f"Craft 報告 Claude 呼叫失敗：{e}")
        return fallback_md, fallback_summary
