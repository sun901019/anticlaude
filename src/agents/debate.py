"""
DebateAgent — 雙視角策略辯論

同時呼叫兩個策略視角（穩健派 vs 突破派），
各自從不同角度選出 Top 3，供 JudgeAgent 綜合裁決。

穩健派（Lala A）：數據優先，選高互動率類型，降低風險
突破派（Lala B）：潛力優先，選爆發點主題，接受一定風險換成長
"""
import asyncio
import json
import time
from openai import OpenAI

from src.config import settings
from src.agents.base import BaseAgent, AgentResult
from src.feedback.memory import get_rich_memory_context
from src.utils.logger import get_logger

log = get_logger("debate_agent")

_DEBATE_BASE_PROMPT = """你是 Sun Lee 的內容策略顧問。
請根據以下評分主題，從「{persona_name}」的角度選出今天最值得發的 Top 3。

{persona_instruction}

---

**評分後的主題清單：**
{scored_topics_json}

---

**歷史受眾數據：**
{memory_section}

---

**選題規則：**
1. 3 篇必須涵蓋不同類型（AI工具實測 / 趨勢解讀 / 職涯觀點 / 個人成長 / 時事分析）
2. 若有台灣在地相關主題，優先納入一篇
3. 整體節奏：3 篇要有輕重緩急

請用以下 JSON 格式回覆，不要有其他說明文字：
{{
  "persona": "{persona_name}",
  "top3": [
    {{
      "cluster_label": "主題名稱（原文不變）",
      "rank": 1,
      "reason": "選這個的理由（60字內，說明從你的視角為什麼選這篇）",
      "post_type": "貼文類型",
      "risk_level": "low / medium / high"
    }}
  ],
  "strategy_note": "整體策略說明（80字內，說明這組選題背後的邏輯）"
}}"""

_CONSERVATIVE_PERSONA = (
    "穩健派策略師",
    """你的選題哲學：
- 優先選歷史互動率高的內容類型（數據說話）
- 避免高爭議性主題，保護帳號的信任度與穩定成長
- 傾向受眾高度匹配的安全選題
- 至少 2 篇是有過往成功案例支撐的類型""",
)

_AGGRESSIVE_PERSONA = (
    "突破派策略師",
    """你的選題哲學：
- 優先選有爆發潛力的新話題，即使類型未被充分驗證
- 至少 1 篇選有爭議性、能引起留言討論的主題
- 傾向新鮮角度，不重複已發過的類型
- 願意用 1 篇「賭一把」換取潛在高成長""",
)


async def _call_one_persona(
    client: OpenAI,
    scored_topics: list[dict],
    persona_name: str,
    persona_instruction: str,
    memory_section: str,
) -> dict:
    prompt = _DEBATE_BASE_PROMPT.format(
        persona_name=persona_name,
        persona_instruction=persona_instruction,
        scored_topics_json=json.dumps(scored_topics, ensure_ascii=False),
        memory_section=memory_section,
    )
    resp = client.chat.completions.create(
        model=settings.model_strategy,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,
    )
    raw = resp.choices[0].message.content or ""
    import re
    raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {"persona": persona_name, "top3": [], "strategy_note": "解析失敗"}


class DebateAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "debate_agent"

    @property
    def model(self) -> str:
        return settings.model_strategy

    async def run(self, scored: list[dict]) -> AgentResult:
        t0 = time.monotonic()

        if not settings.openai_api_key:
            log.warning("OPENAI_API_KEY 未設定，DebateAgent 跳過")
            return self._fail("OPENAI_API_KEY 未設定")

        memory = get_rich_memory_context()
        memory_section = memory.get("strategy_section", "（尚無歷史數據）")

        client = OpenAI(api_key=settings.openai_api_key)

        log.info("DebateAgent：穩健派 vs 突破派 同步辯論中...")
        try:
            conservative, aggressive = await asyncio.gather(
                asyncio.to_thread(
                    _call_one_persona, client, scored,
                    _CONSERVATIVE_PERSONA[0], _CONSERVATIVE_PERSONA[1], memory_section
                ),
                asyncio.to_thread(
                    _call_one_persona, client, scored,
                    _AGGRESSIVE_PERSONA[0], _AGGRESSIVE_PERSONA[1], memory_section
                ),
            )
        except Exception as e:
            return self._fail(str(e))

        elapsed = int((time.monotonic() - t0) * 1000)
        log.info(
            f"辯論完成 — 穩健派：{[t['cluster_label'] for t in conservative.get('top3', [])]}  "
            f"突破派：{[t['cluster_label'] for t in aggressive.get('top3', [])]}  耗時={elapsed}ms"
        )
        return self._ok(
            {"conservative": conservative, "aggressive": aggressive},
            elapsed_ms=elapsed,
        )
