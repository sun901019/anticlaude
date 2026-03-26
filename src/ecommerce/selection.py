"""
Backward-compatibility shim.
Canonical location: src/domains/flow_lab/selection.py

All imports from this module still work.
"""
from src.domains.flow_lab.selection import (  # noqa: F401
    selection_router,
    compute_score,
    compute_financials,
    CandidateCreate,
    CandidatePatch,
    AnalysisCreate,
    ReportCreate,
    LessonCreate,
    ShortlistRequest,
    AutoAnalyzeRequest,
    BundleSave,
    create_candidate,
    list_candidates,
    get_candidate,
    patch_candidate,
    promote_to_product,
    analyze_candidate,
    auto_analyze_candidate,
    get_analysis,
    create_report,
    list_reports,
    get_report,
    get_portfolio,
    generate_shortlist,
    list_lessons,
    create_lesson,
    batch_analyze_candidates,
    suggest_bundles,
    save_bundle,
    list_bundles,
    update_bundle_status,
)
