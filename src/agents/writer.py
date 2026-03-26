"""
WriterAgent — 文案生成
輸入：Top 3 選題 + 已評分主題
輸出：每主題 2 個版本的草稿
模型：claude-sonnet（文案）+ claude-haiku（驗證）
"""
import time
from src.config import settings
from src.agents.base import BaseAgent, AgentResult


class WriterAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "writer_agent"

    @property
    def model(self) -> str:
        return settings.model_write

    async def run(self, top3: list[dict], scored: list[dict], date_str: str) -> AgentResult:
        t0 = time.monotonic()
        try:
            from src.ai.claude_writer import write_drafts
            drafts_path, drafts_list = await write_drafts(top3, scored, date_str)
            elapsed = int((time.monotonic() - t0) * 1000)
            self.log.info(
                f"文案生成完成：{len(drafts_list)} 篇，"
                f"write={self.model}，verify={settings.model_verify}，耗時={elapsed}ms"
            )
            return self._ok({"drafts_path": drafts_path, "drafts_list": drafts_list}, elapsed_ms=elapsed)
        except Exception as e:
            return self._fail(str(e))
