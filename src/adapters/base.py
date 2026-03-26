"""
Adapter Base Contract
=====================
每個外部系統適配器必須繼承 AdapterBase 並實作 execute()。
透過 safe_execute() 呼叫以獲得 timeout + 異常隔離保護。
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Literal

from pydantic import BaseModel


RiskLevel = Literal["low", "medium", "high", "critical"]


class AdapterResult(BaseModel):
    """標準化輸出契約 — 所有 adapter 回傳此格式"""
    ok: bool
    data: Any = None
    error: str | None = None
    adapter_name: str = ""
    duration_ms: float = 0.0
    risk_level: RiskLevel = "medium"


class AdapterBase(ABC):
    """
    所有外部 adapter 的 ABC。

    子類必須定義：
        name:              adapter 識別名（用於 registry + logging）
        risk_level:        操作風險等級
        timeout_seconds:   最長等待秒數（超時自動中斷）
        requires_approval: 是否需要人工審核才能執行
        allowed_agents:    哪些 agent 允許使用此 adapter
    """
    name: str = "base"
    risk_level: RiskLevel = "medium"
    timeout_seconds: int = 30
    requires_approval: bool = False
    allowed_agents: list[str] = []

    @abstractmethod
    async def execute(self, payload: dict) -> AdapterResult:
        """實作外部系統呼叫邏輯，回傳 AdapterResult"""
        ...

    async def safe_execute(
        self,
        payload: dict,
        agent_id: str = "",
        pre_approved: bool = False,
        run_id: str | None = None,
        task_id: str | None = None,
    ) -> AdapterResult:
        """
        安全包裝層：timeout + exception 隔離 + duration 計時 + 審核閘。

        若 adapter.requires_approval=True 且 pre_approved=False，
        系統自動建立 ApprovalRequest（進入 CEO review inbox）並回傳
        ok=False + pending approval_id，由呼叫方輪詢後再以 pre_approved=True 重試。

        所有外部呼叫都應走此方法，不要直接呼叫 execute()。
        """
        from src.utils.logger import get_logger
        log = get_logger(f"adapter.{self.name}")

        # 允許代理人檢查
        if self.allowed_agents and agent_id and agent_id not in self.allowed_agents:
            return AdapterResult(
                ok=False,
                error=f"agent '{agent_id}' 不在允許清單 {self.allowed_agents}",
                adapter_name=self.name,
                risk_level=self.risk_level,
            )

        # 審核閘：requires_approval=True 且未取得明確授權時，建立審核請求並暫停
        if self.requires_approval and not pre_approved:
            # dry_run payloads are always allowed (no external side-effects)
            if not payload.get("dry_run", False):
                try:
                    from src.workflows.approval import request_approval
                    approval_id = request_approval(
                        action=self.name,
                        evidence={"agent_id": agent_id, "payload_keys": list(payload.keys())},
                        risk_level=self.risk_level,
                        run_id=run_id,
                        task_id=task_id,
                    )
                    log.warning(
                        f"[Adapter:{self.name}] approval required — created request {approval_id}"
                    )
                    return AdapterResult(
                        ok=False,
                        error="approval_required",
                        data={"approval_id": approval_id, "action": self.name},
                        adapter_name=self.name,
                        risk_level=self.risk_level,
                    )
                except Exception as gate_err:
                    # Approval system unavailable — fail safe (block execution)
                    log.error(f"[Adapter:{self.name}] approval gate error: {gate_err}")
                    return AdapterResult(
                        ok=False,
                        error=f"approval gate unavailable: {gate_err}",
                        adapter_name=self.name,
                        risk_level=self.risk_level,
                    )

        start = time.monotonic()
        log.info(f"[Adapter:{self.name}] execute start (risk={self.risk_level}, agent={agent_id or 'unknown'})")
        try:
            result = await asyncio.wait_for(
                self.execute(payload),
                timeout=self.timeout_seconds,
            )
            result.duration_ms = round((time.monotonic() - start) * 1000, 1)
            result.adapter_name = self.name
            result.risk_level = self.risk_level
            log.info(f"[Adapter:{self.name}] ok={result.ok} duration={result.duration_ms}ms")
            return result
        except asyncio.TimeoutError:
            duration_ms = round((time.monotonic() - start) * 1000, 1)
            log.error(f"[Adapter:{self.name}] timeout after {self.timeout_seconds}s")
            return AdapterResult(
                ok=False,
                error=f"timeout after {self.timeout_seconds}s",
                adapter_name=self.name,
                duration_ms=duration_ms,
                risk_level=self.risk_level,
            )
        except Exception as e:
            duration_ms = round((time.monotonic() - start) * 1000, 1)
            log.error(f"[Adapter:{self.name}] exception: {e}")
            return AdapterResult(
                ok=False,
                error=str(e),
                adapter_name=self.name,
                duration_ms=duration_ms,
                risk_level=self.risk_level,
            )
