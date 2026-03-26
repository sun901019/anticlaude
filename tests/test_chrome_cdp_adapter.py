"""Tests for ChromeCDPAdapter — 5 test cases."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.adapters.chrome_cdp_adapter import ChromeCDPAdapter


def _adapter():
    return ChromeCDPAdapter()


# ── 1. Missing url ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_missing_url_returns_error():
    adapter = _adapter()
    with patch("src.adapters.chrome_cdp_adapter.async_playwright", create=True):
        # Patch playwright import inside the module
        import sys
        mock_pw_module = MagicMock()
        with patch.dict(sys.modules, {"playwright.async_api": mock_pw_module}):
            result = await adapter.execute({"action": "screenshot", "url": ""})
    assert result.ok is False


# ── 2. action="click" dry_run=True ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_click_dry_run_true_no_browser():
    adapter = _adapter()
    import sys
    mock_pw_module = MagicMock()
    with patch.dict(sys.modules, {"playwright.async_api": mock_pw_module}):
        result = await adapter.execute({
            "action": "click",
            "url": "https://example.com",
            "selector": "#btn",
            "dry_run": True,
        })
    assert result.ok is True
    assert result.data.get("dry_run") is True


# ── 3. action="fill" dry_run=True ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fill_dry_run_true_no_browser():
    adapter = _adapter()
    import sys
    mock_pw_module = MagicMock()
    with patch.dict(sys.modules, {"playwright.async_api": mock_pw_module}):
        result = await adapter.execute({
            "action": "fill",
            "url": "https://example.com",
            "selector": "#input",
            "value": "hello",
            "dry_run": True,
        })
    assert result.ok is True
    assert result.data.get("dry_run") is True


# ── 4. Unknown action dry_run=False → ok=False ────────────────────────────────

@pytest.mark.asyncio
async def test_unknown_action_not_dry_run_returns_error():
    adapter = _adapter()
    import sys

    # Build a mock async context manager for async_playwright()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()

    mock_pw_instance = AsyncMock()
    mock_pw_instance.chromium = MagicMock()
    mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_async_playwright = MagicMock()
    mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_pw_instance)
    mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=False)

    mock_pw_module = MagicMock()
    mock_pw_module.async_playwright = mock_async_playwright

    with patch.dict(sys.modules, {"playwright.async_api": mock_pw_module}), \
         patch("src.adapters.chrome_cdp_adapter.settings") as mock_settings:
        mock_settings.browser_headless = True
        mock_settings.browser_profile_dir = ""
        result = await adapter.execute({
            "action": "explode",
            "url": "https://example.com",
            "dry_run": False,
        })
    assert result.ok is False


# ── 5. action="screenshot" dry_run=True ──────────────────────────────────────

@pytest.mark.asyncio
async def test_screenshot_dry_run_true_ok():
    """screenshot is a read action — dry_run has no effect, but we can test
    that with a mocked playwright it returns ok=True."""
    adapter = _adapter()
    import sys

    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b"fake_bytes")
    mock_page.goto = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_browser.close = AsyncMock()

    mock_pw_instance = AsyncMock()
    mock_pw_instance.chromium = MagicMock()
    mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_async_playwright = MagicMock()
    mock_async_playwright.return_value.__aenter__ = AsyncMock(return_value=mock_pw_instance)
    mock_async_playwright.return_value.__aexit__ = AsyncMock(return_value=False)

    mock_pw_module = MagicMock()
    mock_pw_module.async_playwright = mock_async_playwright

    with patch.dict(sys.modules, {"playwright.async_api": mock_pw_module}), \
         patch("src.adapters.chrome_cdp_adapter.settings") as mock_settings:
        mock_settings.browser_headless = True
        mock_settings.browser_profile_dir = ""
        result = await adapter.execute({
            "action": "screenshot",
            "url": "https://example.com",
            "dry_run": True,
        })
    assert result.ok is True
