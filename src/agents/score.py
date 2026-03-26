"""
ScoreAgent — 主題評分
輸入：聚類主題列表
輸出：含評分的主題列表
模型：claude-sonnet（複雜多維度判斷）
"""
import time
from src.config import settings
from src.agents.base import BaseAgent, AgentResult


class ScoreAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "score_agent"

    @property
    def model(self) -> str:
        return settings.model_score

    async def run(self, clusters: list[dict]) -> AgentResult:
        t0 = time.monotonic()
        try:
            from src.ai.claude_scorer import score_topics
            scored = await score_topics(clusters)
            elapsed = int((time.monotonic() - t0) * 1000)
            self.log.info(f"評分完成：{len(scored)} 個主題，模型={self.model}，耗時={elapsed}ms")
            return self._ok(scored, elapsed_ms=elapsed)
        except Exception as e:
            return self._fail(str(e))
