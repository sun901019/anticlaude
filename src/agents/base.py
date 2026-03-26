"""
BaseAgent — 所有 Agent 的統一介面
每個 Agent 是獨立的 API 呼叫單元，彼此不共享 context
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.utils.logger import get_logger


@dataclass
class AgentResult:
    """Agent 輸出的統一格式"""
    agent_name: str
    success: bool
    data: Any                           # 實際輸出（型別由各 Agent 定義）
    model_used: str = ""
    elapsed_ms: int = 0
    error: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class BaseAgent(ABC):
    """
    所有 Agent 的基底類別。
    
    設計原則：
    - 每次 run() 建立新的 API client（隔離 context）
    - model 從 config 讀取，不 hardcode
    - 輸入/輸出型別明確
    """

    def __init__(self):
        self.log = get_logger(self.name)

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 識別名稱"""
        ...

    @property
    @abstractmethod
    def model(self) -> str:
        """使用的模型，從 config 讀取"""
        ...

    @abstractmethod
    async def run(self, **kwargs) -> AgentResult:
        """執行 Agent，回傳 AgentResult"""
        ...

    def _ok(self, data: Any, model: str = "", elapsed_ms: int = 0) -> AgentResult:
        return AgentResult(
            agent_name=self.name, success=True,
            data=data, model_used=model or self.model, elapsed_ms=elapsed_ms
        )

    def _fail(self, error: str) -> AgentResult:
        self.log.error(f"[{self.name}] 失敗：{error}")
        return AgentResult(agent_name=self.name, success=False, data=None, error=error)

    def _emit(self, status: str, task: str = "") -> None:
        """向 AI Office 發送狀態更新（失敗不影響主流程）"""
        office_id: str = getattr(self, "office_id", "")
        if not office_id:
            return
        try:
            from src.api.agent_status import set_agent_status
            set_agent_status(office_id, status, task)
        except Exception:
            pass
