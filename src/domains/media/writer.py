"""
Canonical location: src/domains/media/writer.py
(Migrated from src/ai/claude_writer.py)

Claude Sonnet：為 Top 3 主題生成繁中 Threads 文案（每主題 2 版本）
輸出至 outputs/drafts/YYYY-MM-DD.md
"""
import json
from pathlib import Path
from datetime import datetime

import anthropic

from src.config import settings, ABOUT_ME_PATH
from src.feedback.memory import get_rich_memory_context
from src.utils.file_io import save_daily_md
from src.utils.logger import get_logger
from src.ai.skill_loader import format_skill_block
from src.content.format_selector import select_format
from src.content.topic_fit import check_topic_fit

log = get_logger("domains.media.writer")

PROMPT_PATH = Path(__file__).parents[3] / "src" / "ai" / "prompts" / "writing_prompt.txt"
MODEL = settings.model_write
MODEL_VERIFY = settings.model_verify


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _load_about_me() -> str:
    if ABOUT_ME_PATH.exists():
        return ABOUT_ME_PATH.read_text(encoding="utf-8")
    return "台灣科技圈創作者，受眾為對 AI 有興趣的科技工作者"


def _parse_draft(text: str) -> dict:
    import re
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return {}


def _format_drafts_md(drafts: list[dict], date_str: str) -> str:
    """將 drafts 格式化為 Markdown"""
    lines = [f"# 貼文草稿 — {date_str}\n"]
    for i, draft in enumerate(drafts, 1):
        label = draft.get("cluster_label", f"主題 {i}")
        lines.append(f"---\n\n## 主題 {i}：{label}\n")
        va = draft.get("version_a", {})
        vb = draft.get("version_b", {})
        lines.append(f"### 版本 A（{va.get('style', '資訊型')}）\n\n{va.get('content', '')}\n")
        lines.append(f"### 版本 B（{vb.get('style', '故事型')}）\n\n{vb.get('content', '')}\n")
    return "\n".join(lines)


VERIFY_PROMPT = """請檢查以下 Threads 貼文是否有 AI 寫作痕跡，並評分（1-10）。

**扣分條件：**
- 含禁用詞（此外、值得注意的是、不容置疑、深刻的影響）→ 各扣 2 分
- 含否定排比（不僅...而且...、這不僅是...而且是...）→ 扣 3 分
- 三段式列舉（一、二、三 或 首先、其次、最後）→ 扣 2 分
- 誇大形容詞（革命性、顛覆性、令人嘆為觀止）→ 各扣 2 分
- 翻譯腔（在這個快速發展的時代、讓我們一起探索）→ 扣 2 分

**貼文內容：**
{content}

如果分數 >= 7，直接回覆原文（不做任何修改）。
如果分數 < 7，修改後回覆修改版本。
只回覆貼文全文，不要評分說明、不要其他文字。"""


def _verify_and_fix_draft(client, draft: dict, label: str) -> dict:
    """對 version_a 和 version_b 進行品質驗證，低於標準時自動修改"""
    for version_key in ("version_a", "version_b"):
        version = draft.get(version_key, {})
        content = version.get("content", "")
        if not content:
            continue
        try:
            verify_msg = client.messages.create(
                model=MODEL_VERIFY,
                max_tokens=1024,
                messages=[{"role": "user", "content": VERIFY_PROMPT.format(content=content)}],
            )
            fixed = verify_msg.content[0].text.strip()
            if fixed and fixed != content:
                log.info(f"品質驗證：{label} {version_key} 已修正")
                draft[version_key]["content"] = fixed
        except Exception as e:
            log.warning(f"品質驗證失敗（{label} {version_key}）：{e}")
    return draft


async def write_drafts(top3: list[dict], scored_topics: list[dict], date_str: str | None = None, extra_skill: str = "") -> str:
    """
    為 Top 3 主題各生成 2 版文案
    回傳輸出的 Markdown 路徑
    """
    d = date_str or datetime.now().strftime("%Y-%m-%d")
    about_me = _load_about_me()
    prompt_template = _load_prompt()

    # 建立 cluster_label → 完整主題資料 的 mapping
    topic_map = {t["cluster_label"]: t for t in scored_topics}

    # 載入受眾記憶（高互動 Hook + 最佳 hashtag + 策略建議）
    memory = get_rich_memory_context()
    memory_section = memory.get("writer_section", "")
    if memory.get("has_data"):
        log.info("WriterAgent：已注入受眾記憶（高互動 Hook + hashtag + 策略建議）")

    if not settings.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY 未設定，跳過文案生成")
        return ""

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    drafts = []

    for item in top3:
        label = item.get("cluster_label", "")
        topic = topic_map.get(label, item)
        post_type = topic.get("post_type", "趨勢解讀")
        merged_summary = topic.get("merged_summary", "")

        # Phase 5.7: Topic Fit Gate — 記錄不匹配警告（不阻擋，Lala 已篩過）
        fit = check_topic_fit(topic)
        if not fit.passed:
            log.warning(f"[TopicFit] {label} 品牌適配分數 {fit.score}（{', '.join(fit.reasons[:2])}）")

        # Phase 5.7: Format Selection — 依主題特性決定格式指引
        fmt = select_format(topic)
        format_block = (
            f"\n\n---\n## [Format Instruction]\n\n"
            f"建議格式：**{fmt.format}**（{fmt.max_words} 字以內）\n"
            f"理由：{fmt.rationale}\n"
            f"{'注意：請分串輸出，每串不超過 150 字。' if fmt.use_thread else ''}"
            f"\n---\n"
        )
        log.info(f"[FormatSelector] {label} → {fmt.format} ({fmt.max_words}字)")

        # 注入 Composite Skill：content_creation（寫作原則 + AI 痕跡去除）
        skill_block = format_skill_block("content_creation", "Content Creation Skill")

        geo_block = f"\n\n---\n## [GEO Optimization Engine]\n\n{extra_skill.strip()}\n---\n" if extra_skill else ""
        prompt = prompt_template.format(
            about_me=about_me,
            cluster_label=label,
            post_type=post_type,
            merged_summary=merged_summary,
            memory_section=memory_section,
        ) + format_block + skill_block + geo_block

        log.info(f"Claude 生成文案：{label}")
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = message.content[0].text
            draft = _parse_draft(raw_text)
            if draft:
                draft = _verify_and_fix_draft(client, draft, label)
                drafts.append(draft)
        except Exception as e:
            log.error(f"Claude 文案生成失敗（{label}）：{e}")

    md_content = _format_drafts_md(drafts, d)
    path = save_daily_md("drafts", md_content, d)
    log.info(f"文案草稿已儲存：{path}")
    return str(path), drafts  # 同時回傳結構化資料
