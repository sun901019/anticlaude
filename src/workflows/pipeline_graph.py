"""
Backward-compatibility shim.
Canonical location: src/domains/media/pipeline_graph.py

All imports from this module still work.
"""
from src.domains.media.pipeline_graph import (  # noqa: F401
    build_content_pipeline,
    run_content_pipeline,
)
