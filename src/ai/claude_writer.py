"""
Backward-compatibility shim.
Canonical location: src/domains/media/writer.py

All imports from this module still work.
"""
from src.domains.media.writer import (  # noqa: F401
    write_drafts,
    VERIFY_PROMPT,
)
