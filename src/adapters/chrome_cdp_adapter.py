"""
Browser / CDP Adapter (Playwright)
=====================================
Approval-gated browser automation via Playwright + Chromium CDP.
Risk: critical — can interact with authenticated sessions.
dry_run=True by default; all writes require requires_approval=True.

Supported actions (read-only by default):
  screenshot  — capture page screenshot
  get_text    — extract visible text from page
  get_html    — return full page HTML
  click       — click an element (requires approval + dry_run=False)
  fill        — fill a form field (requires approval + dry_run=False)
"""
from src.adapters.base import AdapterBase, AdapterResult
from src.config import settings
from src.utils.logger import get_logger

log = get_logger("adapters.chrome_cdp")

_READ_ACTIONS = {"screenshot", "get_text", "get_html"}
_WRITE_ACTIONS = {"click", "fill"}


class ChromeCDPAdapter(AdapterBase):
    name = "chrome_cdp"
    risk_level = "critical"
    timeout_seconds = 60
    requires_approval = True
    allowed_agents = ["ori", "sage"]

    async def execute(self, payload: dict) -> AdapterResult:
        """
        payload:
          action: str        — "screenshot" | "get_text" | "get_html" | "click" | "fill"
          url: str           — page URL to navigate to
          selector: str      — CSS selector (for click / fill / targeted extract)
          value: str         — value to fill (for fill action)
          dry_run: bool      — True = no mutations, read-only (default True)
          wait_for: str      — CSS selector to wait for before acting (optional)
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return AdapterResult(ok=False, error="playwright 未安裝，請執行 python -m playwright install chromium")

        action = payload.get("action", "screenshot")
        url = payload.get("url", "")
        dry_run = payload.get("dry_run", True)

        if not url:
            return AdapterResult(ok=False, error="url 不得為空")

        if action in _WRITE_ACTIONS and dry_run:
            return AdapterResult(
                ok=True,
                data={
                    "dry_run": True,
                    "action": action,
                    "url": url,
                    "selector": payload.get("selector"),
                    "status": "validated — not executed (dry_run=True)",
                },
            )

        if action not in _READ_ACTIONS and action not in _WRITE_ACTIONS:
            return AdapterResult(ok=False, error=f"未知 action: {action}")

        launch_args: dict = {
            "headless": settings.browser_headless,
        }
        if settings.browser_profile_dir:
            launch_args["user_data_dir"] = settings.browser_profile_dir

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(**{k: v for k, v in launch_args.items() if k != "user_data_dir"})
            ctx_args = {}
            if settings.browser_profile_dir:
                ctx_args["user_data_dir"] = settings.browser_profile_dir
            context = await browser.new_context()
            page = await context.new_page()

            await page.goto(url, wait_until="domcontentloaded")

            wait_for = payload.get("wait_for")
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=15000)

            if action == "screenshot":
                screenshot_bytes = await page.screenshot(full_page=True)
                await browser.close()
                return AdapterResult(
                    ok=True,
                    data={"screenshot_bytes_len": len(screenshot_bytes), "url": url},
                )

            if action == "get_text":
                selector = payload.get("selector", "body")
                el = page.locator(selector)
                text = await el.inner_text()
                await browser.close()
                return AdapterResult(ok=True, data={"text": text, "url": url})

            if action == "get_html":
                selector = payload.get("selector", "html")
                el = page.locator(selector)
                html = await el.inner_html()
                await browser.close()
                return AdapterResult(ok=True, data={"html": html[:50000], "url": url})

            if action == "click":
                selector = payload.get("selector", "")
                if not selector:
                    await browser.close()
                    return AdapterResult(ok=False, error="selector 不得為空")
                await page.click(selector)
                await browser.close()
                log.info(f"[ChromeCDP] clicked '{selector}' on {url}")
                return AdapterResult(ok=True, data={"clicked": selector, "url": url})

            if action == "fill":
                selector = payload.get("selector", "")
                value = payload.get("value", "")
                if not selector:
                    await browser.close()
                    return AdapterResult(ok=False, error="selector 不得為空")
                await page.fill(selector, value)
                await browser.close()
                log.info(f"[ChromeCDP] filled '{selector}' on {url}")
                return AdapterResult(ok=True, data={"filled": selector, "url": url})

            await browser.close()
            return AdapterResult(ok=False, error=f"未處理 action: {action}")
