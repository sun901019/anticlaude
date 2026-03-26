"""
LINE Notify Adapter
===================
Wraps src.utils.notify.send_line_notify() in the AdapterBase contract.

Supported action:
  push   — send a text push message to the configured LINE user

Payload:
  {
    "action": "push",           # optional, defaults to "push"
    "message": "...",           # required: text to send
    "dry_run": False            # optional: if True, skips actual send
  }
"""
from src.adapters.base import AdapterBase, AdapterResult


class LineNotifyAdapter(AdapterBase):
    name = "line_notify"
    risk_level = "low"
    timeout_seconds = 10
    requires_approval = False
    allowed_agents = ["ori", "craft", "sage"]

    async def execute(self, payload: dict) -> AdapterResult:
        message: str = payload.get("message", "")
        if not message:
            return AdapterResult(ok=False, error="message 欄位不能為空")

        if payload.get("dry_run", False):
            return AdapterResult(ok=True, data={"dry_run": True, "message": message})

        from src.utils.notify import send_line_notify
        try:
            await send_line_notify(message)
            return AdapterResult(ok=True, data={"message": message})
        except Exception as e:
            return AdapterResult(ok=False, error=str(e))
