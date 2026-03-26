"""
StrategyAgent — 選題策略
輸入：已評分的主題列表
輸出：Top 3 選題 + 週度洞察
模型：gpt-4o（多樣性推理）
"""
import time
from src.config import settings
from src.agents.base import BaseAgent, AgentResult


class StrategyAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "strategy_agent"

    @property
    def model(self) -> str:
        return settings.model_strategy

    async def run(self, scored: list[dict]) -> AgentResult:
        t0 = time.monotonic()
        try:
            from src.ai.gpt_strategist import select_top3
            strategy = await select_top3(scored)
            elapsed = int((time.monotonic() - t0) * 1000)
            top3 = strategy.get("top3", [])
            self.log.info(f"選題完成：Top3={[t['cluster_label'] for t in top3]}，模型={self.model}，耗時={elapsed}ms")
            return self._ok(strategy, elapsed_ms=elapsed)
        except Exception as e:
            return self._fail(str(e))
