"""
X (Twitter) Publish Adapter
==============================
Publishes tweets via X API v2 using OAuth 1.0a.
Risk: high (public post, irreversible)
Approval: required
dry_run defaults to True to prevent accidental posts.
"""
from src.adapters.base import AdapterBase, AdapterResult
from src.config import settings
from src.publishers.x_client import post_tweet, delete_tweet


class XPublishAdapter(AdapterBase):
    name = "x_publish"
    risk_level = "high"
    timeout_seconds = 60
    requires_approval = True
    allowed_agents = ["craft"]

    async def execute(self, payload: dict) -> AdapterResult:
        """
        payload:
          action: str        — "post" | "delete" (default "post")
          text: str          — 貼文內容（≤ 280 chars, required for post）
          tweet_id: str      — tweet ID (required for delete)
          reply_to_id: str   — 若為回覆，填入父貼文 ID
          dry_run: bool      — True 時只驗證不實際發文（default True）
        """
        # Validate credentials
        if not all([
            settings.x_api_key,
            settings.x_api_key_secret,
            settings.x_access_token,
            settings.x_access_token_secret,
        ]):
            return AdapterResult(ok=False, error="X API credentials 未完整設定")

        action = payload.get("action", "post")
        dry_run = payload.get("dry_run", True)

        if action == "post":
            text = payload.get("text", "")
            if not text:
                return AdapterResult(ok=False, error="text 不得為空")
            if len(text) > 280:
                return AdapterResult(ok=False, error=f"貼文超過 280 字（{len(text)} 字）")

            if dry_run:
                return AdapterResult(
                    ok=True,
                    data={"dry_run": True, "text_preview": text[:50], "char_count": len(text), "status": "validated"},
                )

            reply_to_id = payload.get("reply_to_id")
            data = await post_tweet(
                text=text,
                api_key=settings.x_api_key,
                api_secret=settings.x_api_key_secret,
                access_token=settings.x_access_token,
                access_token_secret=settings.x_access_token_secret,
                reply_to_id=reply_to_id,
            )
            return AdapterResult(ok=True, data=data)

        if action == "delete":
            tweet_id = payload.get("tweet_id", "")
            if not tweet_id:
                return AdapterResult(ok=False, error="tweet_id 不得為空")

            if dry_run:
                return AdapterResult(
                    ok=True,
                    data={"dry_run": True, "tweet_id": tweet_id, "status": "validated"},
                )

            data = await delete_tweet(
                tweet_id=tweet_id,
                api_key=settings.x_api_key,
                api_secret=settings.x_api_key_secret,
                access_token=settings.x_access_token,
                access_token_secret=settings.x_access_token_secret,
            )
            return AdapterResult(ok=True, data=data)

        return AdapterResult(ok=False, error=f"未知 action: {action}")
