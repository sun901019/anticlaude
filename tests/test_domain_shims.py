"""Tests that domain migration shims correctly re-export their canonical modules."""


class TestMediaShims:
    def test_write_drafts_shim(self):
        from src.domains.media.writer import write_drafts as canonical
        from src.ai.claude_writer import write_drafts as shim
        assert shim is canonical

    def test_verify_prompt_shim(self):
        from src.domains.media.writer import VERIFY_PROMPT as canonical
        from src.ai.claude_writer import VERIFY_PROMPT as shim
        assert shim is canonical

    def test_select_top3_shim(self):
        from src.domains.media.strategist import select_top3 as canonical
        from src.ai.gpt_strategist import select_top3 as shim
        assert shim is canonical

    def test_score_topics_shim(self):
        from src.domains.media.scorer import score_topics as canonical
        from src.ai.claude_scorer import score_topics as shim
        assert shim is canonical


class TestFlowLabShims:
    def test_selection_router_shim(self):
        from src.domains.flow_lab.selection import selection_router as canonical
        from src.ecommerce.selection import selection_router as shim
        assert shim is canonical

    def test_compute_score_shim(self):
        from src.domains.flow_lab.selection import compute_score as canonical
        from src.ecommerce.selection import compute_score as shim
        assert shim is canonical

    def test_compute_financials_shim(self):
        from src.domains.flow_lab.selection import compute_financials as canonical
        from src.ecommerce.selection import compute_financials as shim
        assert shim is canonical

    def test_selection_shim_exports_key_functions(self):
        # Verify key functions are importable from old path
        from src.ecommerce.selection import (
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
        assert callable(create_candidate)
        assert callable(list_candidates)
        assert callable(get_candidate)
        assert callable(patch_candidate)
        assert callable(promote_to_product)
        assert callable(analyze_candidate)
        assert callable(auto_analyze_candidate)
        assert callable(get_analysis)
        assert callable(create_report)
        assert callable(list_reports)
        assert callable(get_report)
        assert callable(get_portfolio)
        assert callable(generate_shortlist)
        assert callable(list_lessons)
        assert callable(create_lesson)
        assert callable(batch_analyze_candidates)
        assert callable(suggest_bundles)
        assert callable(save_bundle)
        assert callable(list_bundles)
        assert callable(update_bundle_status)

    def test_selection_shim_exports_models(self):
        from src.ecommerce.selection import (
            CandidateCreate,
            CandidatePatch,
            AnalysisCreate,
            ReportCreate,
            LessonCreate,
            ShortlistRequest,
            AutoAnalyzeRequest,
            BundleSave,
        )
        # Just importing without error proves the shim works
        assert CandidateCreate is not None
        assert CandidatePatch is not None
        assert AnalysisCreate is not None
        assert ReportCreate is not None
        assert LessonCreate is not None
        assert ShortlistRequest is not None
        assert AutoAnalyzeRequest is not None
        assert BundleSave is not None
