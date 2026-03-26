"""
Screenshot Analyzer — Claude Vision 產品截圖提取引擎
Canonical location: src/domains/flow_lab/screenshot_analyzer.py

Phase 6.2：接收 base64 圖片（1688/Taobao 截圖），呼叫 Claude Vision，
提取結構化產品資訊，供後續 Shopee 文案 + Threads 草稿生成使用。
"""
import json
import re
from src.config import settings
from src.utils.logger import get_logger

log = get_logger("domains.flow_lab.screenshot_analyzer")

EXTRACT_PROMPT = """你是 Flow Lab 的選品分析師，專門分析電商產品截圖。

請從這張圖片中提取以下資訊，以 JSON 格式回覆：

```json
{
  "product_name": "產品中文名稱",
  "category": "品類（如：香氛 / 辦公用品 / 健康 / 美妝 / 家居）",
  "specs": ["規格 1", "規格 2"],
  "selling_points": ["賣點 1", "賣點 2", "賣點 3"],
  "buyer_pain_points": ["買家痛點 1", "買家痛點 2"],
  "suggested_price_range": "建議定價區間（如：299-499 TWD）",
  "platform_origin": "來源平台（1688 / Taobao / 其他）",
  "extraction_confidence": 0.85,
  "notes": "特殊觀察或不確定之處"
}
```

規則：
- 若圖片中文字模糊或不完整，在 notes 中說明，extraction_confidence 相應降低
- selling_points 聚焦「對台灣消費者的實際好處」，不要翻譯中國行銷語言
- buyer_pain_points 從買家視角思考，而非賣家視角
- 若看到價格，換算為台幣（人民幣 × 4.5），並在 notes 中標注原始價格
- 只回覆 JSON，不要其他說明文字
"""

SHOPEE_DRAFT_PROMPT = """你是 Flow Lab 的電商文案專員（Craft）。

根據以下產品資訊，生成 Shopee 商品標題和描述，符合台灣買家習慣：

**產品資訊：**
{extraction_json}

**使用者補充說明：**
{context}

請回覆 JSON：
```json
{{
  "title": "Shopee 商品標題（含關鍵詞，≤ 40 字）",
  "description": "商品描述（分段，重點強調痛點解決 + 規格，≤ 300 字）",
  "hashtags": ["#標籤1", "#標籤2", "#標籤3"],
  "geo_keywords": ["AI 引擎可引用的關鍵詞 1", "關鍵詞 2"]
}}
```

規格：
- 標題：關鍵詞前置，不要純行銷語言
- 描述：先寫「誰適合用 + 解決什麼問題」，再寫規格，結尾附使用情境
- 融入 GEO 原則：嵌入「人因工程」「極簡設計」等可引用術語（如適用）
- 只回覆 JSON，不要其他文字
"""

THREADS_DRAFT_PROMPT = """你是 Flow Lab 的 Threads 內容創作者（Craft）。

根據以下 Flow Lab 產品資訊，生成一則台灣科技工作者社群貼文：

**產品資訊：**
{extraction_json}

**使用者補充說明：**
{context}

格式要求：
- 風格：朋友分享好物，不是廣告
- 字數：120-200 字
- Hook：第一行就要抓住人，可以是問題或意外發現
- 避免：「革命性」「顛覆性」「值得注意的是」等 AI 痕跡詞
- 結尾：軟性互動，問讀者意見（不要說「按讚分享」）

請回覆 JSON：
```json
{{
  "hook": "第一行（Hook）",
  "content": "完整貼文內容",
  "first_reply": "發文後 5 分鐘內自己留的第一則留言（問題或補充）",
  "format": "short"
}}
```

只回覆 JSON，不要其他文字。
"""


def _parse_json_response(text: str) -> dict:
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {}


async def analyze_screenshot(
    image_base64: str,
    image_type: str = "image/jpeg",
    context: str = "",
) -> dict:
    """
    Claude Vision 截圖分析：提取產品資訊 + 生成 Shopee + Threads 草稿。

    Args:
        image_base64: base64 編碼的圖片
        image_type:   MIME type（image/jpeg | image/png | image/webp）
        context:      使用者附加說明（如產品定位、目標客群）

    Returns:
        {
            extraction: dict,
            shopee_draft: dict,
            threads_draft: dict,
            ok: bool,
            error: str | None,
        }
    """
    if not settings.anthropic_api_key:
        return {"ok": False, "error": "ANTHROPIC_API_KEY 未設定", "extraction": {}}

    import anthropic
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Step 1: Claude Vision — 提取產品資訊
    log.info("[ScreenshotAnalyzer] 呼叫 Claude Vision 提取產品資訊...")
    extraction = {}
    try:
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": image_type,
                            "data": image_base64,
                        },
                    },
                    {"type": "text", "text": EXTRACT_PROMPT},
                ],
            }],
        )
        extraction = _parse_json_response(resp.content[0].text)
        log.info(f"[ScreenshotAnalyzer] 提取完成：{extraction.get('product_name', '未知產品')}")
    except Exception as e:
        log.error(f"[ScreenshotAnalyzer] Vision 提取失敗：{e}")
        return {"ok": False, "error": str(e), "extraction": {}}

    extraction_str = json.dumps(extraction, ensure_ascii=False)

    # Step 2: Shopee 文案生成
    shopee_draft = {}
    try:
        resp2 = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": SHOPEE_DRAFT_PROMPT.format(
                    extraction_json=extraction_str,
                    context=context or "無特殊說明",
                ),
            }],
        )
        shopee_draft = _parse_json_response(resp2.content[0].text)
        log.info("[ScreenshotAnalyzer] Shopee 草稿生成完成")
    except Exception as e:
        log.warning(f"[ScreenshotAnalyzer] Shopee 草稿生成失敗：{e}")

    # Step 3: Threads 草稿生成
    threads_draft = {}
    try:
        resp3 = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": THREADS_DRAFT_PROMPT.format(
                    extraction_json=extraction_str,
                    context=context or "無特殊說明",
                ),
            }],
        )
        threads_draft = _parse_json_response(resp3.content[0].text)
        log.info("[ScreenshotAnalyzer] Threads 草稿生成完成")
    except Exception as e:
        log.warning(f"[ScreenshotAnalyzer] Threads 草稿生成失敗：{e}")

    return {
        "ok": True,
        "error": None,
        "extraction": extraction,
        "shopee_draft": shopee_draft,
        "threads_draft": threads_draft,
    }
