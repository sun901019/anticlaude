"""
Registry Reader — 程式化讀取 _hub/registry/ 路由規則與能力定義
Phase 4：ai_os_gap_analysis_20260316.md — Skills registry 程式化

讓 orchestrator / CEO agent 能動態查詢「這個 task_type 由誰處理」
而不是硬編碼在每個模組裡。
"""
import json
from functools import lru_cache
from pathlib import Path

from src.utils.logger import get_logger

log = get_logger("registry.reader")

REGISTRY_DIR = Path(__file__).resolve().parents[2] / "_hub" / "registry"
SCHEMA_PATH  = REGISTRY_DIR / "registry_schema.json"


@lru_cache(maxsize=1)
def _load_schema() -> dict:
    """載入並快取 registry_schema.json"""
    if not SCHEMA_PATH.exists():
        log.warning(f"Registry schema 不存在：{SCHEMA_PATH}")
        return {}
    try:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        log.error(f"Registry schema 載入失敗：{e}")
        return {}


def get_routing_map() -> dict[str, str]:
    """
    回傳 task_type → agent_id 的路由對照表。
    來源：registry_schema.json routing_rules.mappings
    """
    schema = _load_schema()
    mappings = schema.get("routing_rules", {}).get("mappings", [])
    return {m["task_type"]: m["agent"] for m in mappings if "task_type" in m and "agent" in m}


def resolve_agent(task_type: str) -> str | None:
    """
    依 task_type 查詢負責的 agent id。
    找不到回傳 None。
    """
    return get_routing_map().get(task_type)


def list_task_types() -> list[str]:
    """回傳所有已登記的 task_type 清單"""
    return list(get_routing_map().keys())


def describe_routing() -> str:
    """回傳易讀的路由說明（供 CEO agent system prompt 使用）"""
    rmap = get_routing_map()
    if not rmap:
        return "（路由規則未載入）"
    lines = []
    for task_type, agent in sorted(rmap.items()):
        lines.append(f"  {task_type} → {agent}")
    return "\n".join(lines)
