"""
CEO Agent — 意圖偵測 + 動態路由
接收使用者任意輸入，判斷意圖並路由至對應 agent / 直接回應
Phase 3 實作：ai_os_gap_analysis_20260316.md
"""
import json
import re

from src.config import settings
from src.utils.logger import get_logger

log = get_logger("ceo_agent")

# ── 路由規則（對應 project_routing_map.md）──────────────────────────────────

ROUTING_MAP = {
    "content_research":    "ori",
    "market_analysis":     "ori",
    "competitor_analysis": "ori",
    "topic_strategy":      "lala",
    "audience_analysis":   "lala",
    "content_planning":    "lala",
    "draft_generation":    "craft",
    "copywriting":         "craft",
    "seo_analysis":        "sage",
    "data_analysis":       "sage",
    "product_evaluation":  "sage",
    "ui_implementation":   "lumi",
    "backend_development": "lumi",
    "system_debugging":    "lumi",
    "ux_review":           "pixel",
    "design_evaluation":   "pixel",
}

AGENT_DESCRIPTIONS = {
    "ori":   "Ori（研究）— 市場研究、競品分析、選品候選",
    "lala":  "Lala（策略）— 內容策略、選題規劃、受眾分析",
    "craft": "Craft（內容）— Threads 貼文、電商文案寫作",
    "sage":  "Sage（分析）— 數據分析、SEO 分析、選品評分",
    "lumi":  "Lumi（工程）— 程式開發、系統維護、API 建置",
    "pixel": "Pixel（設計）— UX 審核、設計建議",
    "none":  "CEO 直接回應（一般問答）",
}

# ── System Prompt ─────────────────────────────────────────────────────────────

CEO_SYSTEM_PROMPT = """你是 AntiClaude 的 CEO Agent，Sun Lee 的 AI 首席助理。
工作語言：繁體中文。

你的職責：
1. 理解使用者的請求意圖
2. 判斷應由哪個 agent 處理，或直接回答
3. 決定是否立即自動執行（auto_execute）或等使用者確認

你管理的 AI 團隊：
- Ori（研究）：market_research、competitor_analysis、content_research
- Lala（策略）：topic_strategy、audience_analysis、content_planning
- Craft（內容）：draft_generation、copywriting
- Sage（分析）：seo_analysis、data_analysis、product_evaluation
- Lumi（工程）：ui_implementation、backend_development、system_debugging
- Pixel（設計）：ux_review、design_evaluation

auto_execute 判斷規則：
- true（低風險，自動執行）：content_research、data_analysis、market_analysis、product_evaluation、topic_strategy
- false（高風險，等使用者確認）：draft_generation、copywriting、seo_analysis、ui_implementation、backend_development
- agent="none" 時永遠 false

若使用者詢問系統狀態、解釋概念、一般問答，agent 設為 "none"，直接回答。
若需要啟動某個 agent 執行任務，設為對應 agent id。

請以純 JSON 格式回覆（不要 markdown code fence）：
{
  "intent": "一句話描述使用者意圖",
  "agent": "agent_id（ori/lala/craft/sage/lumi/pixel/none）",
  "task_type": "任務類型（或 null）",
  "auto_execute": true,
  "response": "給使用者的回覆（繁中，300字內，清晰直接）",
  "actions": ["建議下一步1", "建議下一步2"]
}"""


# ── 核心函數 ──────────────────────────────────────────────────────────────────

def _build_user_content(message: str, image_base64: str | None):
    if not image_base64:
        return message

    media_type = "image/jpeg"
    data = image_base64
    if image_base64.startswith("data:") and "," in image_base64:
        header, data = image_base64.split(",", 1)
        match = re.match(r"data:(image/[^;]+);base64", header)
        if match:
            media_type = match.group(1)

    return [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": data,
            },
        },
        {"type": "text", "text": message},
    ]


async def process_message(
    message: str,
    context: list[dict] | None = None,
    image_base64: str | None = None,
) -> dict:
    """
    CEO Agent 處理使用者訊息。

    Args:
        message: 使用者輸入
        context: 對話歷史（可選），格式 [{"role": "user"|"assistant", "content": "..."}]

    Returns:
        dict: {intent, agent, task_type, response, actions}
    """
    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY 未設定，CEO Agent 無法運作")
        return _fallback("CEO Agent 尚未初始化，請確認 ANTHROPIC_API_KEY 已設定。")

    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # 組裝對話歷史
    messages = []
    if context:
        for turn in context[-6:]:  # 最近 3 輪對話
            if turn.get("role") in ("user", "assistant") and turn.get("content"):
                messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": _build_user_content(message, image_base64)})

    try:
        resp = client.messages.create(
            model=settings.model_write,   # claude-sonnet-4-6
            max_tokens=1024,
            system=CEO_SYSTEM_PROMPT,
            messages=messages,
        )
        raw = resp.content[0].text.strip()
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            # 嘗試提取 JSON 物件
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group())
                except json.JSONDecodeError:
                    return _fallback(raw[:400])
            else:
                return _fallback(raw[:400])

        # 正規化欄位
        result.setdefault("intent", "")
        result.setdefault("agent", "none")
        result.setdefault("task_type", None)
        result.setdefault("auto_execute", False)
        result.setdefault("response", "")
        result.setdefault("actions", [])

        log.info(
            f"CEO 路由：intent={result['intent'][:40]} → agent={result['agent']} "
            f"task={result['task_type']}"
        )
        return result

    except Exception as e:
        log.error(f"CEO Agent 呼叫失敗：{e}")
        return _fallback(f"處理時發生錯誤：{str(e)[:100]}")


def _fallback(message: str) -> dict:
    return {
        "intent": "錯誤",
        "agent": "none",
        "task_type": None,
        "response": message,
        "actions": [],
    }


def get_agent_description(agent_id: str) -> str:
    return AGENT_DESCRIPTIONS.get(agent_id, agent_id)


def get_routing_map() -> dict:
    return ROUTING_MAP.copy()


# ── Multi-Agent Deliberation ───────────────────────────────────────────────────

_DELIBERATION_PROMPT = """你是 AntiClaude 的 CEO Agent，正在召集多位 AI 顧問進行集體討論。
工作語言：繁體中文。

以下是各顧問對同一問題的分析結果（JSON 格式）。
你的任務：
1. 整合各顧問的觀點，找出共識與分歧
2. 給出最終的綜合建議
3. 明確指出最推薦的行動方案

輸出純 JSON（不要 markdown code fence）：
{
  "consensus": "各顧問的共識摘要（1-2 句）",
  "key_insights": ["洞察1", "洞察2", "洞察3"],
  "divergences": "主要分歧點（若無則填 null）",
  "recommendation": "最終建議行動方案（具體、可執行）",
  "confidence": "high|medium|low",
  "next_steps": ["步驟1", "步驟2"]
}"""

# Which agents participate in deliberation and what task they handle
_DELIBERATION_AGENTS: dict[str, str] = {
    "ori":   "content_research",
    "lala":  "topic_strategy",
    "sage":  "data_analysis",
}


async def _consult_agent(agent_id: str, task_type: str, question: str) -> dict:
    """Run a single agent task as part of multi-agent deliberation."""
    try:
        from src.agents.dynamic_orchestrator import run_task
        ctx = {"query": question, "topic": question, "date_str": None}
        if task_type == "content_research":
            ctx["date_str"] = None
        result = await run_task(task_type, ctx)
        return {
            "agent": agent_id,
            "task_type": task_type,
            "success": result.get("success", False),
            "summary": str(result.get("data", result.get("error", "")))[:500],
        }
    except Exception as e:
        return {"agent": agent_id, "task_type": task_type, "success": False, "summary": str(e)[:200]}


async def deliberate(question: str) -> dict:
    """
    Multi-agent deliberation: consult Ori, Lala, Sage in parallel,
    then synthesize with CEO Agent.

    Returns:
        {
            "consensus": str,
            "key_insights": list[str],
            "divergences": str | None,
            "recommendation": str,
            "confidence": str,
            "next_steps": list[str],
            "agent_inputs": list[dict],  # raw per-agent results
        }
    """
    import asyncio

    if not settings.anthropic_api_key:
        return {"error": "CEO Agent 尚未初始化", "recommendation": "請確認 ANTHROPIC_API_KEY 已設定"}

    log.info(f"[Deliberation] starting multi-agent consultation for: {question[:60]}")

    # Step 1: Consult agents in parallel
    tasks = [
        _consult_agent(agent_id, task_type, question)
        for agent_id, task_type in _DELIBERATION_AGENTS.items()
    ]
    agent_inputs = await asyncio.gather(*tasks)

    # Step 2: Synthesize with CEO Claude
    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    inputs_json = "\n".join(
        f"[{r['agent'].upper()}] {r['summary']}"
        for r in agent_inputs
        if r.get("success")
    ) or "（各顧問均未能提供有效資料，請基於問題本身給出建議）"

    synthesis_prompt = f"問題：{question}\n\n各顧問分析結果：\n{inputs_json}"

    try:
        import re
        resp = client.messages.create(
            model=settings.model_write,
            max_tokens=1024,
            system=_DELIBERATION_PROMPT,
            messages=[{"role": "user", "content": synthesis_prompt}],
        )
        raw = resp.content[0].text.strip()
        raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
        result = json.loads(raw)
    except (json.JSONDecodeError, Exception) as e:
        log.warning(f"[Deliberation] synthesis parse error: {e}")
        result = {
            "consensus": "無法解析",
            "key_insights": [],
            "divergences": None,
            "recommendation": "請重試或直接向各 agent 詢問",
            "confidence": "low",
            "next_steps": [],
        }

    result["agent_inputs"] = [dict(r) for r in agent_inputs]
    log.info(f"[Deliberation] complete. confidence={result.get('confidence')}")
    return result
