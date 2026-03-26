"""
Threads Graph API 封裝
Base URL: https://graph.threads.net/v1.0
"""
from src.config import settings
from src.utils.http_client import get
from src.utils.logger import get_logger

log = get_logger("threads_client")

BASE_URL = "https://graph.threads.net/v1.0"


def _token() -> str | None:
    return settings.threads_access_token


def _user_id() -> str | None:
    return settings.threads_user_id


async def get_me() -> dict | None:
    """取得自己的 Threads 帳號資料"""
    token = _token()
    if not token:
        log.warning("THREADS_ACCESS_TOKEN 未設定")
        return None

    url = f"{BASE_URL}/me"
    params = {
        "fields": "id,username,threads_profile_picture_url",
        "access_token": token,
    }
    result = await get(url, params=params)
    if isinstance(result, dict) and "error" in result:
        err = result["error"]
        if err.get("code") == 190:
            log.error("Threads Token 已過期，請重新授權")
        else:
            log.error(f"Threads API 錯誤：{err}")
        return None
    return result


async def get_recent_posts(limit: int = 50) -> list[dict]:
    """取得最近的貼文列表"""
    token = _token()
    user_id = _user_id()
    if not token or not user_id:
        log.warning("THREADS_ACCESS_TOKEN 或 THREADS_USER_ID 未設定")
        return []

    url = f"{BASE_URL}/{user_id}/threads"
    params = {
        "fields": "id,text,timestamp,media_type",
        "limit": limit,
        "access_token": token,
    }
    result = await get(url, params=params)
    if not isinstance(result, dict):
        log.error("取得貼文列表失敗")
        return []

    if "error" in result:
        err = result["error"]
        if err.get("code") == 190:
            log.error("Threads Token 已過期，請重新授權")
        else:
            log.error(f"Threads API 錯誤：{err}")
        return []

    return result.get("data", [])


async def publish_post(text: str) -> dict:
    """
    發布一則純文字貼文到 Threads。
    Step 1: 建立 media container
    Step 2: 發布 container
    回傳 {"ok": True, "threads_post_id": "...", "container_id": "..."}
    """
    import httpx as _httpx
    token = _token()
    user_id = _user_id()
    if not token or not user_id:
        log.error("THREADS_ACCESS_TOKEN 或 THREADS_USER_ID 未設定，無法發文")
        return {"ok": False, "error": "未設定 Threads 憑證"}

    try:
        # Step 1: 建立 container
        create_resp = _httpx.post(
            f"{BASE_URL}/{user_id}/threads",
            params={
                "media_type": "TEXT",
                "text": text,
                "access_token": token,
            },
            timeout=20.0,
        )
        create_resp.raise_for_status()
        container_id = create_resp.json().get("id")
        if not container_id:
            log.error(f"建立 Threads container 失敗：{create_resp.text}")
            return {"ok": False, "error": "container 建立失敗"}

        # Step 2: 發布
        publish_resp = _httpx.post(
            f"{BASE_URL}/{user_id}/threads_publish",
            params={
                "creation_id": container_id,
                "access_token": token,
            },
            timeout=20.0,
        )
        publish_resp.raise_for_status()
        post_id = publish_resp.json().get("id")
        if not post_id:
            log.error(f"發布 Threads 貼文失敗：{publish_resp.text}")
            return {"ok": False, "error": "發布失敗", "container_id": container_id}

        log.info(f"Threads 發文成功：post_id={post_id}")
        return {"ok": True, "threads_post_id": post_id, "container_id": container_id}

    except Exception as e:
        log.error(f"Threads 發文失敗：{e}")
        return {"ok": False, "error": str(e)}


async def get_post_insights(post_id: str) -> dict | None:
    """取得單篇貼文的互動數據"""
    token = _token()
    if not token:
        return None

    url = f"{BASE_URL}/{post_id}/insights"
    params = {
        "metric": "views,likes,replies,reposts,quotes",
        "access_token": token,
    }
    result = await get(url, params=params)
    if not isinstance(result, dict) or "error" in result:
        log.warning(f"取得貼文 {post_id} 數據失敗")
        return None

    # 解析 insights data 格式 → {metric: value}
    metrics = {}
    for item in result.get("data", []):
        name = item.get("name")
        value = item.get("values", [{}])[0].get("value", 0) if item.get("values") else item.get("total_value", {}).get("value", 0)
        metrics[name] = value

    return metrics
