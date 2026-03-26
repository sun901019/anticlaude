"""
ClusterAgent — 新聞聚類
輸入：原始文章列表
輸出：去重主題列表
模型：claude-haiku（快速模式識別，不需複雜推理）
"""
import time
from src.config import settings
from src.agents.base import BaseAgent, AgentResult


class ClusterAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "cluster_agent"

    @property
    def model(self) -> str:
        return settings.model_cluster

    async def run(self, articles: list[dict], recent_labels: list[str] | None = None) -> AgentResult:
        t0 = time.monotonic()
        try:
            # 1. 先試 Gemini Flash（速度快、成本低，擅長大量素材聚類）
            from src.ai.gemini_cluster import cluster_articles as gemini_cluster
            clusters = gemini_cluster(articles)

            # 2. Gemini 失敗或回傳空 → fallback 到 Claude
            if not clusters:
                self.log.info("Gemini 聚類無結果，fallback 到 Claude...")
                from src.ai.claude_cluster import cluster_articles_claude
                clusters = await cluster_articles_claude(articles, recent_labels=recent_labels or [])
                model_used = self.model
            else:
                model_used = "gemini-2.5-flash"

            elapsed = int((time.monotonic() - t0) * 1000)
            self.log.info(f"聚類完成：{len(clusters)} 個主題，模型={model_used}，耗時={elapsed}ms")
            return self._ok(clusters, elapsed_ms=elapsed)
        except Exception as e:
            return self._fail(str(e))
