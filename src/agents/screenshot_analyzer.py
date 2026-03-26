"""
Backward-compatibility shim.
Canonical location: src/domains/flow_lab/screenshot_analyzer.py

All imports from this module still work.
"""
from src.domains.flow_lab.screenshot_analyzer import (  # noqa: F401
    analyze_screenshot,
    EXTRACT_PROMPT,
    SHOPEE_DRAFT_PROMPT,
    THREADS_DRAFT_PROMPT,
)
