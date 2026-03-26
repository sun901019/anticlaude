"""
Tests for skill cache lifecycle (mtime-based invalidation).
Covers: cache hit, cache miss on file change, eviction, manual invalidate.
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch


# ── Helpers ───────────────────────────────────────────────────────────────────

def _reset_cache():
    from src.ai import skill_loader
    skill_loader._cache.clear()


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestSkillCacheLifecycle:
    def setup_method(self):
        _reset_cache()

    def test_loads_existing_skill(self, tmp_path):
        skill_file = tmp_path / "test_skill.md"
        skill_file.write_text("# My Skill\nDo something.", encoding="utf-8")

        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            result = sl.load_composite_skill("test_skill")
            assert "Do something" in result
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_cache_hit_returns_same_content(self, tmp_path):
        skill_file = tmp_path / "cached.md"
        skill_file.write_text("cached content", encoding="utf-8")

        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            first = sl.load_composite_skill("cached")
            second = sl.load_composite_skill("cached")
            assert first == second == "cached content"
            # Cache should have exactly 1 entry
            assert "cached" in sl._cache
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_cache_invalidates_on_file_change(self, tmp_path):
        skill_file = tmp_path / "changing.md"
        skill_file.write_text("version 1", encoding="utf-8")

        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            v1 = sl.load_composite_skill("changing")
            assert v1 == "version 1"

            # Simulate file update by writing new content and bumping mtime
            skill_file.write_text("version 2", encoding="utf-8")
            # Force mtime to be strictly newer (avoid filesystem resolution issues)
            new_mtime = skill_file.stat().st_mtime + 1
            os.utime(skill_file, (new_mtime, new_mtime))

            v2 = sl.load_composite_skill("changing")
            assert v2 == "version 2"
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_missing_skill_returns_empty(self, tmp_path):
        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            result = sl.load_composite_skill("nonexistent_skill")
            assert result == ""
            # Missing file should not be cached
            assert "nonexistent_skill" not in sl._cache
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_strips_frontmatter(self, tmp_path):
        skill_file = tmp_path / "fm_skill.md"
        skill_file.write_text("---\ntitle: Test\n---\nActual content here.", encoding="utf-8")

        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            result = sl.load_composite_skill("fm_skill")
            assert "---" not in result
            assert "Actual content here." in result
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_manual_invalidate_single(self, tmp_path):
        skill_file = tmp_path / "inv.md"
        skill_file.write_text("to be invalidated", encoding="utf-8")

        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            sl.load_composite_skill("inv")
            assert "inv" in sl._cache
            removed = sl.invalidate_skill_cache("inv")
            assert removed == 1
            assert "inv" not in sl._cache
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_manual_invalidate_all(self, tmp_path):
        for name in ("a", "b", "c"):
            (tmp_path / f"{name}.md").write_text(f"skill {name}", encoding="utf-8")

        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        try:
            for name in ("a", "b", "c"):
                sl.load_composite_skill(name)
            assert len(sl._cache) == 3
            removed = sl.invalidate_skill_cache()
            assert removed == 3
            assert len(sl._cache) == 0
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir

    def test_evicts_oldest_at_capacity(self, tmp_path):
        import src.ai.skill_loader as sl
        orig_dir = sl.COMPOSITE_SKILLS_DIR
        orig_max = sl.MAX_CACHE_SIZE
        sl.COMPOSITE_SKILLS_DIR = tmp_path
        sl.MAX_CACHE_SIZE = 3
        try:
            for i in range(4):
                (tmp_path / f"skill_{i}.md").write_text(f"content {i}", encoding="utf-8")
                sl.load_composite_skill(f"skill_{i}")
            # Cache should not exceed MAX_CACHE_SIZE
            assert len(sl._cache) <= 3
        finally:
            sl.COMPOSITE_SKILLS_DIR = orig_dir
            sl.MAX_CACHE_SIZE = orig_max
