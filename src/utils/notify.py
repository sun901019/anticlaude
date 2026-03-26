"""
通知工具：LINE Messaging API（Push Message）
沒有設定 LINE_CHANNEL_ACCESS_TOKEN / LINE_USER_ID 時靜默跳過。
"""
import httpx
from src.config import settings
from src.utils.logger import get_logger

log = get_logger("notify")

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


async def send_line_notify(message: str) -> None:
    token = settings.line_channel_access_token
    user_id = settings.line_user_id
    if not token or not user_id:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                LINE_PUSH_URL,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json={
                    "to": user_id,
                    "messages": [{"type": "text", "text": message}],
                },
            )
            if resp.status_code == 200:
                log.info(f"LINE 通知已發送：{message[:40]}")
            else:
                log.warning(f"LINE 通知失敗：{resp.status_code} {resp.text}")
    except Exception as e:
        log.warning(f"LINE 通知例外：{e}")
