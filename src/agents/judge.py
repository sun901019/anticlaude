"""
JudgeAgent — 辯論裁決者

讀取 DebateAgent 的雙視角結果，
用 Claude Sonnet 綜合裁決出最終 Top 3 + 理由。

Claude 做 Judge（而非 GPT）：因為需要細膩的中文判斷與品牌語感。
"""
import json
import time
import anthropic

from src.config import settings
from src.agents.base import BaseAgent, AgentResult
from src.utils.logger import get_logger

log = get_logger("judge_agent")

_JUDGE_PROMPT = """你是 Sun Lee 的首席內容策略裁判。

以下是兩位策略師對今天選題的辯論結果：

---

**穩健派（{conservative_persona}）的建議：**
Top 3：{conservative_top3}
策略邏輯：{conservative_note}

---

**突破派（{aggressive_persona}）的建議：**
Top 3：{aggressive_top3}
策略邏輯：{aggressive_note}

---

**你的裁決任務：**
1. 分析兩派建議的優缺點
2. 選出最終 Top 3（可以從任一派選，也可以混搭）
3. 最終選題要同時考慮：穩定互動（不要全部賭注）+ 至少一篇有突破潛力
4. 3 篇必須涵蓋不同類型，不能全是 AI 工具類

請用以下 JSON 格式回覆，不要有其他說明文字：
{{
  "top3": [
    {{
      "cluster_label": "主題名稱（原文不變）",
      "rank": 1,
      "strategy_reason": "選這個的理由（80字內）",
      "post_type": "貼文類型",
      "adopted_from": "穩健派 / 突破派 / 混合"
    }}
  ],
  "weekly_insight": "本次辯論洞察（100字內，說明今天選題策略的核心考量）",
  "debate_summary": "穩健派 vs 突破派 最大分歧點（50字內）"
}}"""


def _fmt_top3(top3: list[dict]) -> str:
    return "、".join(t.get("cluster_label", "") for t in top3)


class JudgeAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "judge_agent"

    @property
    def model(self) -> str:
        return settings.model_score  # Claude Sonnet — 細膩判斷

    async def run(self, debate_result: dict) -> AgentResult:
        t0 = time.monotonic()

        if not settings.anthropic_api_key:
            log.warning("ANTHROPIC_API_KEY 未設定，JudgeAgent 跳過")
            return self._fail("ANTHROPIC_API_KEY 未設定")

        conservative = debate_result.get("conservative", {})
        aggressive = debate_result.get("aggressive", {})

        prompt = _JUDGE_PROMPT.format(
            conservative_persona=conservative.get("persona", "穩健派"),
            conservative_top3=_fmt_top3(conservative.get("top3", [])),
            conservative_note=conservative.get("strategy_note", ""),
            aggressive_persona=aggressive.get("persona", "突破派"),
            aggressive_top3=_fmt_top3(aggressive.get("top3", [])),
            aggressive_note=aggressive.get("strategy_note", ""),
        )

        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        log.info("JudgeAgent：裁決辯論結果中...")
        try:
            message = client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = message.content[0].text
            import re
            raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
            result = json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    result = json.loads(match.group())
                except Exception as e:
                    return self._fail(f"JSON 解析失敗：{e}")
            else:
                return self._fail("JudgeAgent 回應無法解析")
        except Exception as e:
            return self._fail(str(e))

        elapsed = int((time.monotonic() - t0) * 1000)
        top3 = result.get("top3", [])
        log.info(
            f"裁決完成 — 最終 Top3：{[t['cluster_label'] for t in top3]}  "
            f"分歧點：{result.get('debate_summary', '')}  耗時={elapsed}ms"
        )
        return self._ok(result, elapsed_ms=elapsed)
