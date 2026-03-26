"""
Composite Skill Loader
從 _hub/shared/skills/composite/ 載入技能定義，注入至 agent system prompt
Phase 3：active_capabilities_manifest.md 技能注入實作

Cache策略：mtime-based invalidation
  - 每次呼叫時比對 .md 檔案的 mtime
  - 若 mtime 改變（檔案被更新）→ 自動重新載入，無需重啟服務
  - 進程記憶體中保留最多 MAX_CACHE_SIZE 個 skill 的快取
  - token_memory §11.2 要求：skill cache 要有版本感知，避免陳舊技能注入
"""
from pathlib import Path
from src.utils.logger import get_logger

log = get_logger("skill_loader")

COMPOSITE_SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / "_hub" / "shared" / "skills" / "composite"

MAX_CACHE_SIZE = 32

# Cache entry: skill_name → (mtime_ns, content)
# mtime_ns = file modification time in nanoseconds (int); content = stripped text
_cache: dict[str, tuple[int, str]] = {}


def _strip_frontmatter(text: str) -> str:
    """移除 YAML frontmatter（--- ... ---）"""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            return text[end + 3:].lstrip("\n")
    return text


def load_composite_skill(skill_name: str) -> str:
    """
    載入 composite skill 定義文件，回傳純文字內容（去除 frontmatter）。

    自動偵測 .md 檔案修改：若檔案 mtime 改變，快取失效並重新載入。
    skill_name: 如 "content_creation", "geo_optimization_engine"
    """
    skill_path = COMPOSITE_SKILLS_DIR / f"{skill_name}.md"
    if not skill_path.exists():
        log.warning(f"Composite skill 文件不存在：{skill_path}")
        _cache.pop(skill_name, None)
        return ""

    try:
        current_mtime = skill_path.stat().st_mtime_ns
    except OSError as e:
        log.error(f"無法讀取 skill 檔案 mtime [{skill_name}]：{e}")
        return ""

    cached = _cache.get(skill_name)
    if cached is not None and cached[0] == current_mtime:
        return cached[1]

    # Cache miss or file changed — reload
    try:
        text = skill_path.read_text(encoding="utf-8")
        content = _strip_frontmatter(text)
    except Exception as e:
        log.error(f"載入 composite skill 失敗 [{skill_name}]：{e}")
        return ""

    # Evict oldest entry if at capacity
    if len(_cache) >= MAX_CACHE_SIZE and skill_name not in _cache:
        oldest = next(iter(_cache))
        del _cache[oldest]
        log.debug(f"[SkillCache] 驅逐舊快取：{oldest}")

    _cache[skill_name] = (current_mtime, content)
    log.info(f"[SkillCache] 載入 skill '{skill_name}' (mtime={current_mtime})")
    return content


def invalidate_skill_cache(skill_name: str | None = None) -> int:
    """
    手動失效快取。
    skill_name=None → 清除全部快取，回傳清除數量。
    skill_name=<name> → 只清除指定 skill。
    """
    if skill_name is None:
        count = len(_cache)
        _cache.clear()
        log.info(f"[SkillCache] 全部快取已清除（{count} 個）")
        return count
    if skill_name in _cache:
        del _cache[skill_name]
        log.info(f"[SkillCache] 已清除快取：{skill_name}")
        return 1
    return 0


def format_skill_block(skill_name: str, title: str | None = None) -> str:
    """
    將 composite skill 內容格式化為 prompt 中的 <skill> 區塊。
    回傳空字串若 skill 不存在。
    """
    content = load_composite_skill(skill_name)
    if not content:
        return ""
    header = title or skill_name.replace("_", " ").title()
    return f"\n\n---\n## [Composite Skill: {header}]\n\n{content.strip()}\n---\n"
