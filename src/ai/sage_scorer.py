"""
Sage 自動評分模組：Claude Sonnet 依 SOP 評分
輸入：product_name + competitor_data
輸出：各維度分數 dict
"""
import json
import re
from pathlib import Path

import anthropic

from src.config import settings
from src.utils.logger import get_logger

log = get_logger("sage_scorer")

MODEL = "claude-sonnet-4-6"
SOP_PATH = Path(__file__).parents[2] / "ai" / "skills" / "product-scoring.md"


def _load_sop() -> str:
    try:
        return SOP_PATH.read_text(encoding="utf-8")
    except Exception:
        return "依需求強度、競爭健康度、利潤空間、痛點機會、品牌適配度五個維度評分（各1-10分）"


def _parse_scores(text: str) -> dict:
    text = re.sub(r"```(?:json)?\s*", "", text).strip().rstrip("```").strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*?\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    log.error("無法解析 Sage 評分回應")
    return {}


def auto_score_candidate(product_name: str, competitor_data: dict) -> dict:
    """
    Sage 自動評分主函數
    回傳分數 dict，失敗時回傳 fallback 中等分數
    """
    fallback = {
        "demand_score": 5, "competition_score": 5, "profit_score": 5,
        "pain_point_score": 5, "brand_fit_score": 5,
        "market_type": "demand", "overall_risk": "中",
        "risk_summary": "自動評分失敗，建議手動確認",
        "reasoning": "自動評分失敗，使用預設中等分數",
        "recommendation": "觀察",
        "recommendation_confidence": "低",
        "recommendation_reasons": ["自動評分失敗，請手動檢視"],
        "next_steps": ["手動填入成本資料", "搜尋競品確認市場需求"],
        "warnings": [],
    }

    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY 未設定，使用 fallback 分數")
        return fallback

    sop = _load_sop()
    comp_text = json.dumps(competitor_data, ensure_ascii=False, indent=2) if competitor_data else "（無競品資料）"

    prompt = f"""你是 Flow Lab 的選品分析師（Sage）。
品牌定位：辦公室療育，主打桌面療癒商品，目標客群為台灣辦公室工作者。

以下是商品「{product_name}」的競品研究資料：
{comp_text}

評分 SOP 參考：
{sop[:800]}

請依以下標準輸出 JSON（只輸出 JSON，不要多餘文字）：
{{
  "demand_score": <1-10，需求強度，搜尋量高/蝦皮熱銷=高分>,
  "competition_score": <1-10，競爭健康度，有價格梯次=高分，全部同質=低分>,
  "profit_score": <1-10，利潤空間，成本×3可達售價=高分>,
  "pain_point_score": <1-10，痛點改善機會，消費者抱怨明確=高分>,
  "brand_fit_score": <1-10，品牌適配度，符合辦公療育=高分>,
  "market_type": "<demand/trend/problem/hybrid 擇一>",
  "overall_risk": "<低/中/高，綜合差評可改善性與競爭風險>",
  "risk_summary": "<30字內風險說明，繁中>",
  "reasoning": "<100字內評分說明，繁中>",
  "recommendation": "<建議進樣/建議觀察/建議淘汰 擇一>",
  "recommendation_confidence": "<高/中/低>",
  "recommendation_reasons": [
    "<理由1，繁中>",
    "<理由2，繁中>"
  ],
  "next_steps": [
    "<下一步行動1，繁中>",
    "<下一步行動2，繁中>",
    "<下一步行動3，繁中>"
  ],
  "warnings": [
    "<需注意的風險點，若無則空陣列>"
  ]
}}"""

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text
        scores = _parse_scores(text)
        if not scores or "demand_score" not in scores:
            log.warning("Sage 評分解析失敗，使用 fallback")
            return fallback
        log.info(f"Sage 自動評分完成：{product_name} → {scores.get('demand_score')}/{scores.get('profit_score')}/{scores.get('brand_fit_score')}")
        return scores
    except Exception as e:
        log.error(f"Sage 評分 Claude 呼叫失敗：{e}")
        return fallback
