# encoding: utf-8
from src.ai.skill_loader import load_composite_skill, format_skill_block, _strip_frontmatter


def test_strip_frontmatter_removes_yaml():
    text = "---\nname: test\ndescription: hello\n---\n\n# Content\nHello world"
    result = _strip_frontmatter(text)
    assert "# Content" in result
    assert "name: test" not in result


def test_strip_frontmatter_no_frontmatter():
    text = "# Just a title\nContent here"
    result = _strip_frontmatter(text)
    assert result == text


def test_load_known_skill_has_content():
    content = load_composite_skill("content_creation")
    assert isinstance(content, str)
    assert len(content) > 100


def test_load_known_skill_no_frontmatter():
    content = load_composite_skill("content_creation")
    assert not content.strip().startswith("---")


def test_load_unknown_skill_returns_empty():
    content = load_composite_skill("nonexistent_skill_xyz_999")
    assert content == ""


def test_format_skill_block_known():
    block = format_skill_block("content_creation")
    assert "[Composite Skill:" in block
    assert len(block) > 50


def test_format_skill_block_custom_title():
    block = format_skill_block("content_creation", "My Custom Title")
    assert "My Custom Title" in block


def test_format_skill_block_unknown_returns_empty():
    block = format_skill_block("nonexistent_xyz_999")
    assert block == ""
