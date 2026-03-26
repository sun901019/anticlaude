"""
Orio Scorer — 三分研究評分模型
================================
來源：aitos_next_steps_roadmap_20260318.md Phase 4
      aitos_token_memory_skill_integration_consolidation_20260319.md §8.3

三個核心分數：
  topic_fit_score    — 主題與品牌受眾的匹配度
  persona_fit_score  — 主題與 Sun（創作者本人）的人設契合度
  source_trust_score — 資料來源的可信度

輸出一個複合分，供 Lala 選題時排序。

設計原則：Orio 不輸出原始資料，輸出「已評分的結構化 artifact」。
"""
from dataclasses import dataclass, field


# ── Persona 定義（Sun Lee，@sunlee._.yabg）───────────────────────────────────

_PERSONA_KEYWORDS = {
    # 正面匹配（加分）
    "positive": {
        "AI", "GPT", "Claude", "LLM", "自動化", "Agent", "生產力",
        "職涯", "創業", "系統思維", "工作流", "工具", "科技", "成長",
        "Threads", "創作者", "個人品牌",
    },
    # 負面匹配（扣分）
    "negative": {
        "遊戲", "娛樂", "八卦", "明星", "追劇", "美食", "旅遊",
        "政治", "股票", "期貨",  # 非 Sun 的主要發文方向
    },
}

# ── Source Trust 分數映射（source → 0.0-1.0）─────────────────────────────────

_SOURCE_TRUST: dict[str, float] = {
    # 高信任（原始研究 + 知名媒體）
    "arxiv": 0.95,
    "openai": 0.90,
    "anthropic": 0.90,
    "google": 0.85,
    "mit technology review": 0.85,
    "wired": 0.80,
    "techcrunch": 0.75,
    "hacker news": 0.70,
    "the verge": 0.70,
    # 中信任
    "medium": 0.55,
    "substack": 0.55,
    "twitter": 0.50,
    "x.com": 0.50,
    "threads": 0.50,
    "reddit": 0.45,
    # 低信任（社群或未知）
    "unknown": 0.30,
    "rss": 0.40,
}

_DEFAULT_SOURCE_TRUST = 0.40


@dataclass
class OrioScore:
    topic_fit_score: float      # 0.0–1.0：主題 × 品牌受眾匹配度
    persona_fit_score: float    # 0.0–1.0：主題 × Sun 人設契合度
    source_trust_score: float   # 0.0–1.0：資料來源可信度
    composite_score: float      # 加權複合分（0.0–1.0）
    passed: bool                # composite_score >= 0.45 才推薦給 Lala
    reasons: list[str] = field(default_factory=list)


# 複合分加權
_WEIGHTS = {
    "topic_fit":    0.45,
    "persona_fit":  0.35,
    "source_trust": 0.20,
}


def _score_persona_fit(label: str, summary: str) -> tuple[float, list[str]]:
    """根據標題 + 摘要計算 persona_fit_score"""
    text = (label + " " + summary).lower()
    reasons = []
    score = 0.5

    pos_hits = [kw for kw in _PERSONA_KEYWORDS["positive"] if kw.lower() in text]
    neg_hits = [kw for kw in _PERSONA_KEYWORDS["negative"] if kw.lower() in text]

    if pos_hits:
        boost = min(0.4, len(pos_hits) * 0.12)
        score += boost
        reasons.append(f"正向人設關鍵字：{', '.join(pos_hits[:3])}")
    if neg_hits:
        penalty = min(0.35, len(neg_hits) * 0.15)
        score -= penalty
        reasons.append(f"負向人設關鍵字（扣分）：{', '.join(neg_hits[:2])}")

    return round(max(0.0, min(1.0, score)), 2), reasons


def _score_source_trust(source: str) -> float:
    """根據來源名稱查詢信任分數"""
    source_lower = (source or "").lower()
    for key, trust in _SOURCE_TRUST.items():
        if key in source_lower:
            return trust
    return _DEFAULT_SOURCE_TRUST


def score_topic(topic: dict) -> OrioScore:
    """
    對單一主題計算三分模型分數。

    Args:
        topic: 含 cluster_label, merged_summary, post_type, source(optional) 的 dict

    Returns:
        OrioScore
    """
    from src.content.topic_fit import check_topic_fit

    label = topic.get("cluster_label", "")
    summary = topic.get("merged_summary", "")
    source = topic.get("source", "unknown")

    reasons: list[str] = []

    # 1. Topic Fit（品牌受眾匹配）
    fit = check_topic_fit(topic)
    topic_fit = fit.score
    reasons.extend(fit.reasons[:2])

    # 2. Persona Fit（Sun 人設契合）
    persona_fit, persona_reasons = _score_persona_fit(label, summary)
    reasons.extend(persona_reasons)

    # 3. Source Trust（來源可信度）
    source_trust = _score_source_trust(source)
    if source_trust >= 0.8:
        reasons.append(f"高信任來源：{source}")
    elif source_trust <= 0.4:
        reasons.append(f"來源信任度偏低：{source}（{source_trust:.0%}）")

    # 4. 複合分
    composite = round(
        topic_fit * _WEIGHTS["topic_fit"]
        + persona_fit * _WEIGHTS["persona_fit"]
        + source_trust * _WEIGHTS["source_trust"],
        3,
    )

    return OrioScore(
        topic_fit_score=topic_fit,
        persona_fit_score=persona_fit,
        source_trust_score=source_trust,
        composite_score=composite,
        passed=composite >= 0.45,
        reasons=reasons,
    )


def rank_topics(topics: list[dict]) -> list[dict]:
    """
    對主題列表排序，回傳含 orio_score 欄位的主題列表（降序）。

    Args:
        topics: 主題 dict 列表

    Returns:
        含 orio_score: OrioScore dict 的主題列表（僅返回 passed=True 的主題，按 composite_score 降序）
    """
    scored = []
    for t in topics:
        s = score_topic(t)
        if s.passed:
            scored.append({
                **t,
                "orio_score": {
                    "topic_fit": s.topic_fit_score,
                    "persona_fit": s.persona_fit_score,
                    "source_trust": s.source_trust_score,
                    "composite": s.composite_score,
                    "reasons": s.reasons,
                },
            })
    scored.sort(key=lambda x: x["orio_score"]["composite"], reverse=True)
    return scored
