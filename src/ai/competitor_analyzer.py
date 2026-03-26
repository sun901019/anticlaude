"""
Ori 競品研究模組：Serper 搜尋 + Gemini Flash 結構化
輸入：product_name, category
輸出：結構化競品資料 dict
"""
import json
import re
from pathlib import Path

import httpx
from google import genai

from src.config import settings
from src.utils.logger import get_logger
from src.ai.skill_loader import format_skill_block

log = get_logger("competitor_analyzer")

SERPER_SEARCH_URL = "https://google.serper.dev/search"
GEMINI_MODEL = "gemini-2.5-flash"
_TIMEOUT = 30.0


def _serper_search(query: str) -> list[dict]:
    """同步呼叫 Serper，回傳搜尋結果列表"""
    if not settings.serper_api_key:
        return []
    try:
        resp = httpx.post(
            SERPER_SEARCH_URL,
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "gl": "tw", "hl": "zh-TW", "num": 8},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("organic", []):
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
            })
        return results
    except Exception as e:
        log.warning(f"Serper 搜尋失敗（{query[:30]}）：{e}")
        return []


def _gemini_structure(product_name: str, raw_results: list[dict], selection_rules: str = "") -> dict:
    """用 Gemini Flash 把原始搜尋結果整理成結構化競品分析"""
    if not settings.gemini_api_key or not raw_results:
        return {}
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        snippets = "\n".join(
            f"- {r['title']}: {r['snippet']}" for r in raw_results[:20]
        )
        rules_hint = f"\n\n參考選品規則：\n{selection_rules[:600]}" if selection_rules else ""
        # 注入 Composite Skill：research_analysis（Ori 的研究品質標準）
        skill_block = format_skill_block("research_analysis", "Research Analysis Skill")

        prompt = f"""你是電商選品分析師。以下是關於「{product_name}」的競品搜尋結果：{skill_block}

{snippets}{rules_hint}

請整理成以下 JSON 格式（只輸出 JSON，不要多餘文字）：
{{
  "competitor_count": <估計在售賣家數量，整數>,
  "price_range": {{"min": <最低價 NT$，整數>, "max": <最高價 NT$，整數>}},
  "avg_rating": <平均評分 1-5，浮點數，若不明確填 0>,
  "pain_points": [
    {{
      "pain_point": "<差評描述，繁中>",
      "frequency": "<高/中/低>",
      "can_improve": <true/false，是否可透過換供應商或選品規避>,
      "improve_difficulty": "<低/中/高>",
      "risk_level": "<低/中/高>",
      "notes": "<一句說明，繁中>"
    }}
  ],
  "overall_risk": "<低/中/高，依最嚴重的 pain_point 決定>",
  "risk_summary": "<30字內整體風險說明，繁中>",
  "market_type_hint": "<demand/trend/problem/hybrid 擇一>",
  "demand_signal": "<high/medium/low 擇一>",
  "raw_summary": "<50字內市場概述，繁中>"
}}"""
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        text = re.sub(r"```(?:json)?\s*", "", response.text).strip().rstrip("```").strip()
        return json.loads(text)
    except Exception as e:
        log.warning(f"Gemini 競品結構化失敗：{e}")
        return {}


def _load_selection_rules() -> str:
    """讀取 Sage 整合的選品規則（若存在），注入競品分析 context"""
    try:
        rules_path = Path(__file__).parents[2] / "ai" / "context" / "flowlab-selection-rules.md"
        if rules_path.exists():
            return rules_path.read_text(encoding="utf-8")
    except Exception:
        pass
    return ""


def research_competitor(product_name: str, category: str = "") -> dict:
    """
    Ori 競品研究主函數
    回傳結構化競品資料，失敗時回傳空 dict（不中斷流程）
    """
    log.info(f"Ori 競品研究開始：{product_name}")

    queries = [
        f"{product_name} 蝦皮 熱銷",
        f"{product_name} 評價 缺點 ptt",
        f"{product_name} site:shopee.tw",
    ]
    if category:
        queries.append(f"{category} {product_name} 台灣市場")

    raw_results = []
    for q in queries:
        results = _serper_search(q)
        raw_results.extend(results)
        log.info(f"  查詢「{q[:30]}」→ {len(results)} 筆")

    if not raw_results:
        log.warning("Serper 無結果，回傳空競品資料")
        return {}

    selection_rules = _load_selection_rules()
    if selection_rules:
        log.info("Ori 已載入 Sage 選品規則作為分析 context")

    structured = _gemini_structure(product_name, raw_results, selection_rules)
    log.info(f"Ori 競品研究完成：{len(raw_results)} 筆原始資料 → {structured.get('demand_signal', '?')} 需求")
    return structured
