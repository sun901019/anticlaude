"""
Canonical location: src/domains/flow_lab/selection.py
(Migrated from src/ecommerce/selection.py)

Flow Lab 選品引擎 API
掛載路徑：/api/ecommerce/selection（由 router.py include）

Lifecycle 說明：
  ecommerce_selection_candidates → 候選品全池（含被拒品、學習用）
  ecommerce_selection_analyses   → 每輪完整 SOP 評分結果
  ecommerce_selection_reports    → 生成報告
  ecommerce_selection_lessons    → 學習記憶

注意：與 fl_products / fl_decisions 是不同 lifecycle，不互相干擾。
"""
import uuid
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from src.db.connection import db
from src.utils.logger import get_logger

log = get_logger("domains.flow_lab.selection")

selection_router = APIRouter(prefix="/selection", tags=["ecommerce-selection"])


# ─── Sage Auto-Lesson 觸發器 ──────────────────────────────────────────────────

def _emit_sage(status: str, task: str = "", artifact_refs: list | None = None,
               target_agent_id: str = "") -> None:
    """向 AI Office 發送 Sage 狀態更新"""
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            "sage", status=status, task=task, title=task,
            task_type="analysis", priority="normal",
            source_agent_id="", target_agent_id=target_agent_id,
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass


def _emit_ori(status: str, task: str = "", target: str = "",
              artifact_refs: list | None = None) -> None:
    """向 AI Office 發送 Ori 狀態更新"""
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            "ori", status=status, task=task, title=task,
            task_type="research", priority="normal",
            source_agent_id="", target_agent_id=target,
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass


def _emit_craft(status: str, task: str = "", source: str = "",
                artifact_refs: list | None = None) -> None:
    """向 AI Office 發送 Craft 狀態更新"""
    try:
        from src.api.agent_status import update_agent_task
        update_agent_task(
            "craft", status=status, task=task, title=task,
            task_type="content", priority="normal",
            source_agent_id=source, target_agent_id="",
            artifact_refs=artifact_refs or [],
        )
    except Exception:
        pass


def _auto_lesson_on_decision(candidate_id: str, new_status: str) -> None:
    """
    當候選品狀態變為 approved / rejected 時，
    Sage 自動從最新分析中抽取 lesson 並寫入 ecommerce_selection_lessons。
    累積 10 條後觸發規則整合提醒。
    """
    if new_status not in ("approved", "rejected"):
        return

    lesson_type = "winning_pattern" if new_status == "approved" else "rejection_pattern"
    _emit_sage("working", f"自動抽取選品學習記憶：{candidate_id}")

    try:
        with db() as conn:
            # 取得候選品基本資料
            cand = conn.execute(
                """SELECT product_name, category, market_type
                   FROM ecommerce_selection_candidates WHERE candidate_id=?""",
                (candidate_id,)
            ).fetchone()
            if not cand:
                return
            cand = dict(cand)

            # 取得最新分析結果
            analysis = conn.execute(
                """SELECT id as analysis_id, score_total, viability_band, recommended_role,
                          role_confidence, role_reasoning, reasoning, financials_json
                   FROM ecommerce_selection_analyses
                   WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1""",
                (candidate_id,)
            ).fetchone()

            if not analysis:
                # 無分析資料時仍記錄決策結果
                theme = cand["product_name"]
                lesson_text = (
                    f"【{new_status.upper()}】{cand['product_name']}（{cand.get('category','未分類')}）"
                    f" 在無評分數據下被{('核准' if new_status == 'approved' else '拒絕')}，"
                    f"需補充分析後才能形成有效模式。"
                )
                analysis_ids = []
            else:
                analysis = dict(analysis)
                import json as _json
                financials = {}
                if analysis.get("financials_json"):
                    try:
                        financials = _json.loads(analysis["financials_json"])
                    except Exception:
                        pass

                theme = f"{cand['product_name']} ({cand.get('category','未分類')})"
                score = analysis.get("score_total", 0)
                band = analysis.get("viability_band", "unknown")
                role = analysis.get("recommended_role", "未定義")
                reasoning = analysis.get("reasoning") or analysis.get("role_reasoning") or ""
                margin = financials.get("gross_margin", "N/A")

                if new_status == "approved":
                    lesson_text = (
                        f"核准模式：{cand['product_name']} 評分 {score}/50（{band}），"
                        f"定位 {role}，品類 {cand.get('category','未分類')}，"
                        f"毛利率 {margin}。"
                        f"決策理由：{reasoning}"
                    )
                else:
                    lesson_text = (
                        f"拒絕模式：{cand['product_name']} 評分 {score}/50（{band}），"
                        f"定位 {role}，品類 {cand.get('category','未分類')}，"
                        f"毛利率 {margin}。"
                        f"拒絕理由：{reasoning}"
                    )
                analysis_ids = [analysis["analysis_id"]]

            # 寫入 lesson
            import json as _json
            conn.execute(
                """INSERT INTO ecommerce_selection_lessons
                   (theme, lesson_type, lesson_text, source_analysis_ids_json, confidence)
                   VALUES (?,?,?,?,?)""",
                (theme, lesson_type, lesson_text,
                 _json.dumps(analysis_ids, ensure_ascii=False), 0.7)
            )

            # 檢查 lesson 總數是否達到 10 條，若達到則發出整合提醒
            total_lessons = conn.execute(
                "SELECT COUNT(*) as n FROM ecommerce_selection_lessons"
            ).fetchone()["n"]

        _emit_sage(
            "idle",
            artifact_refs=[f"ecommerce/selection/lessons/{candidate_id}"]
        )

        if total_lessons >= 10 and total_lessons % 10 == 0:
            _trigger_sage_rule_synthesis(total_lessons)

    except Exception as e:
        _emit_sage("idle")
        import logging
        logging.getLogger("selection").warning(f"auto_lesson 失敗：{e}")

def _trigger_sage_rule_synthesis(lesson_count: int) -> None:
    """
    累積 N 條 lesson 後，Sage 用 Claude 整合成選品規則，
    寫入 ai/context/flowlab-selection-rules.md，供 Ori 下次搜尋時參考。
    """
    import json as _json
    from pathlib import Path
    import anthropic as _anthropic

    _emit_sage("working", f"整合選品學習規則（共 {lesson_count} 條經驗）")
    try:
        with db() as conn:
            rows = conn.execute(
                "SELECT lesson_type, lesson_text, confidence FROM ecommerce_selection_lessons ORDER BY id DESC LIMIT 30"
            ).fetchall()
        if not rows:
            return

        lessons_text = "\n".join(
            f"[{r['lesson_type']}] {r['lesson_text']}" for r in rows
        )
        prompt = f"""你是 Flow Lab 選品策略師（Sage）。
以下是過去 {len(rows)} 筆選品決策的經驗教訓：

{lessons_text}

請整合成 3-5 條具體的選品規則，格式為 Markdown，適合注入 Ori 的競品研究 prompt。
每條規則包含：規則說明、適用情境、成功條件。
只輸出規則本文，不要額外說明。"""

        from src.config import settings as _settings
        if not _settings.anthropic_api_key:
            return
        client = _anthropic.Anthropic(api_key=_settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        rules_md = message.content[0].text.strip()

        rules_path = Path(__file__).parents[2] / "ai" / "context" / "flowlab-selection-rules.md"
        rules_path.write_text(
            f"# Flow Lab 選品規則（Sage 自動整合）\n"
            f"> 更新時間：{date.today().isoformat()} ｜ 來源：{lesson_count} 條學習記憶\n\n"
            f"{rules_md}\n",
            encoding="utf-8",
        )
        log.info(f"Sage 規則整合完成：{rules_path}")
    except Exception as e:
        log.warning(f"_trigger_sage_rule_synthesis 失敗：{e}")
    finally:
        _emit_sage("idle")


# ─── 評分公式 ─────────────────────────────────────────────────────────────────

def compute_score(demand: float, competition: float, profit: float,
                  pain_point: float, brand_fit: float) -> tuple[float, str]:
    """score = demand*2 + profit*2 + pain_points + competition + brand_fit"""
    total = demand * 2 + profit * 2 + pain_point + competition + brand_fit
    if total >= 40:
        band = "strong"
    elif total >= 35:
        band = "viable"
    elif total >= 30:
        band = "watchlist"
    else:
        band = "reject"
    return round(total, 1), band


def compute_financials(cost_rmb: float, exchange_rate: float = 4.5,
                       platform_fee: float = 0.05, payment_fee: float = 0.12,
                       ad_cost_est: float = 0.0, role: str = "毛利款") -> dict:
    """計算落地成本、最低售價、建議售價、毛利率"""
    role_margin = {"引流款": 0.25, "毛利款": 0.40, "主力款": 0.35}
    target_margin = role_margin.get(role, 0.35)
    landed = cost_rmb * exchange_rate
    total_fee = platform_fee + payment_fee
    min_price = landed / (1 - target_margin - total_fee)
    target_price = round(min_price * 1.1 / 10) * 10
    gross_margin = (target_price - landed) / target_price - total_fee if target_price else 0
    break_even_roas = target_price / ad_cost_est if ad_cost_est > 0 else None
    return {
        "landed_cost_twd": round(landed, 1),
        "min_viable_price": round(min_price, 1),
        "target_price": target_price,
        "gross_margin": round(gross_margin, 3),
        "break_even_roas": round(break_even_roas, 2) if break_even_roas else None,
    }


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class CandidateCreate(BaseModel):
    product_name: str
    source_platform: Optional[str] = "manual"
    source_url: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[list[str]] = None
    market_type: Optional[str] = None          # demand|trend|problem|hybrid
    market_confidence: Optional[float] = None
    risk_flags: Optional[list[str]] = None     # fragile|ip|complex_electronics|...
    discovery_notes: Optional[str] = None
    created_by_agent: Optional[str] = "ori"


class CandidatePatch(BaseModel):
    status: Optional[str] = None               # candidate|shortlisted|approved|rejected
    selection_status: Optional[str] = None     # evaluating|viable|rejected|watchlist
    launch_status: Optional[str] = None        # not_ready|ready|launched
    market_type: Optional[str] = None
    market_confidence: Optional[float] = None
    risk_flags: Optional[list[str]] = None
    risk_score: Optional[float] = None
    discovery_notes: Optional[str] = None


class AnalysisCreate(BaseModel):
    # 各維度評分 1-10
    demand_score: float = Field(ge=1, le=10)
    competition_score: float = Field(ge=1, le=10)
    profit_score: float = Field(ge=1, le=10)
    pain_point_score: float = Field(ge=1, le=10)
    brand_fit_score: float = Field(ge=1, le=10)
    # 市場/競品明細（可選）
    market_metrics: Optional[dict] = None
    competition_metrics: Optional[dict] = None
    # 財務計算輸入（可選，有則自動計算）
    financials: Optional[dict] = None          # cost_rmb, exchange_rate, platform_fee, payment_fee, ad_cost_est
    # 負評痛點（可選）
    negative_reviews: Optional[list[dict]] = None  # [{pain_point, frequency, opportunity}]
    # 角色建議（可由系統推算或手動指定）
    recommended_role: Optional[str] = None
    role_confidence: Optional[float] = None
    role_reasoning: Optional[str] = None
    # 決策
    decision_status: Optional[str] = "待評估"
    reasoning: Optional[str] = None
    analyzed_by_agent: Optional[str] = "sage"


class ReportCreate(BaseModel):
    report_title: Optional[str] = None
    created_by_agent: Optional[str] = "craft"


class LessonCreate(BaseModel):
    theme: str
    lesson_type: str  # rejection_pattern|winning_pattern|margin_rule|brand_rule
    lesson_text: str
    source_analysis_ids: Optional[list[int]] = None
    confidence: Optional[float] = 0.5


class ShortlistRequest(BaseModel):
    min_score: float = 35.0
    max_count: int = 10


# ─── Candidates ──────────────────────────────────────────────────────────────

@selection_router.post("/candidates")
def create_candidate(body: CandidateCreate):
    candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
    import json
    with db() as conn:
        conn.execute("""
            INSERT INTO ecommerce_selection_candidates
            (candidate_id, product_name, source_platform, source_url, category,
             keywords_json, market_type, market_confidence, risk_flags_json,
             discovery_notes, created_by_agent)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            candidate_id, body.product_name, body.source_platform,
            body.source_url, body.category,
            json.dumps(body.keywords or [], ensure_ascii=False),
            body.market_type, body.market_confidence,
            json.dumps(body.risk_flags or [], ensure_ascii=False),
            body.discovery_notes, body.created_by_agent,
        ))
    # 新增候選後，Ori 進入待命狀態（告知 AI Office 有新候選）
    _emit_ori("working", f"候選品已加入：{body.product_name}，等待開始分析", target="sage")
    import threading
    threading.Timer(3.0, lambda: _emit_ori("idle")).start()

    return {"ok": True, "candidate_id": candidate_id, "product_name": body.product_name}


@selection_router.get("/candidates")
def list_candidates(
    status: Optional[str] = Query(None),
    market_type: Optional[str] = Query(None),
    source_platform: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
):
    conditions = []
    params: list = []
    if status and status != "all":
        conditions.append("status = ?")
        params.append(status)
    if market_type:
        conditions.append("market_type = ?")
        params.append(market_type)
    if source_platform:
        conditions.append("source_platform = ?")
        params.append(source_platform)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params.append(limit)
    with db() as conn:
        rows = conn.execute(
            f"SELECT * FROM ecommerce_selection_candidates {where} ORDER BY created_at DESC LIMIT ?",
            params
        ).fetchall()
    return [dict(r) for r in rows]


@selection_router.get("/candidates/{candidate_id}")
def get_candidate(candidate_id: str):
    with db() as conn:
        c = conn.execute(
            "SELECT * FROM ecommerce_selection_candidates WHERE candidate_id=?",
            (candidate_id,)
        ).fetchone()
        if not c:
            raise HTTPException(404, f"候選品 {candidate_id} 不存在")
        analysis = conn.execute(
            "SELECT * FROM ecommerce_selection_analyses WHERE candidate_id=? ORDER BY analysis_date DESC LIMIT 1",
            (candidate_id,)
        ).fetchone()
        reports = conn.execute(
            "SELECT id, report_title, created_at FROM ecommerce_selection_reports WHERE candidate_id=? ORDER BY created_at DESC",
            (candidate_id,)
        ).fetchall()
    return {
        "candidate": dict(c),
        "latest_analysis": dict(analysis) if analysis else None,
        "reports": [dict(r) for r in reports],
    }


@selection_router.patch("/candidates/{candidate_id}")
def patch_candidate(candidate_id: str, body: CandidatePatch):
    import json
    with db() as conn:
        c = conn.execute(
            "SELECT id FROM ecommerce_selection_candidates WHERE candidate_id=?",
            (candidate_id,)
        ).fetchone()
        if not c:
            raise HTTPException(404, f"候選品 {candidate_id} 不存在")
        updates: dict = {}
        if body.status is not None:
            updates["status"] = body.status
        if body.selection_status is not None:
            updates["selection_status"] = body.selection_status
        if body.launch_status is not None:
            updates["launch_status"] = body.launch_status
        if body.market_type is not None:
            updates["market_type"] = body.market_type
        if body.market_confidence is not None:
            updates["market_confidence"] = body.market_confidence
        if body.risk_flags is not None:
            updates["risk_flags_json"] = json.dumps(body.risk_flags, ensure_ascii=False)
        if body.risk_score is not None:
            updates["risk_score"] = body.risk_score
        if body.discovery_notes is not None:
            updates["discovery_notes"] = body.discovery_notes
        if not updates:
            return {"ok": True, "candidate_id": candidate_id}
        sets = ", ".join(f"{k}=?" for k in updates)
        conn.execute(
            f"UPDATE ecommerce_selection_candidates SET {sets}, updated_at=CURRENT_TIMESTAMP WHERE candidate_id=?",
            [*updates.values(), candidate_id]
        )

    # 3-C：狀態改為 approved/rejected 時觸發 Sage auto-lesson
    if body.status in ("approved", "rejected"):
        _auto_lesson_on_decision(candidate_id, body.status)
        # Craft 決策完成，回到 idle
        try:
            from src.api.agent_status import mark_agent_done
            mark_agent_done("craft")
        except Exception:
            pass

    return {"ok": True, "candidate_id": candidate_id}


@selection_router.post("/candidates/{candidate_id}/promote")
def promote_to_product(candidate_id: str):
    """
    將 approved 候選品升格為 fl_products 商品。
    自動填入名稱、品類、角色（來自最新分析），SKU 自動生成。
    """
    import json as _json
    with db() as conn:
        c = conn.execute(
            "SELECT * FROM ecommerce_selection_candidates WHERE candidate_id=?",
            (candidate_id,)
        ).fetchone()
        if not c:
            raise HTTPException(404, f"候選品 {candidate_id} 不存在")
        c = dict(c)
        if c["status"] != "approved":
            raise HTTPException(400, f"候選品狀態為 {c['status']}，只有 approved 才能升格")

        # 取最新分析結果
        analysis = conn.execute(
            "SELECT * FROM ecommerce_selection_analyses WHERE candidate_id=? ORDER BY created_at DESC LIMIT 1",
            (candidate_id,)
        ).fetchone()
        analysis = dict(analysis) if analysis else {}

        # 生成 SKU
        existing = conn.execute("SELECT sku FROM fl_products ORDER BY id DESC LIMIT 1").fetchone()
        if existing:
            try:
                last_num = int(existing["sku"].replace("FL-", ""))
                new_sku = f"FL-{last_num + 1:02d}"
            except Exception:
                new_sku = f"FL-{candidate_id[:4].upper()}"
        else:
            new_sku = "FL-01"

        # 避免 SKU 重複
        while conn.execute("SELECT 1 FROM fl_products WHERE sku=?", (new_sku,)).fetchone():
            n = int(new_sku.replace("FL-", "")) + 1
            new_sku = f"FL-{n:02d}"

        product_type = c.get("category") or "general"
        role = analysis.get("recommended_role") or "profit"
        conn.execute(
            """
            INSERT INTO fl_products
            (sku, name, product_type, status, role, role_confirmed, cost_rmb)
            VALUES (?,?,?,?,?,0,0)
            """,
            (
                new_sku,
                c["product_name"],
                product_type,
                "idea",
                role,
            ),
        )
        return {
            "ok": True,
            "sku": new_sku,
            "product_name": c["product_name"],
            "message": f"promoted to fl_products: {new_sku}",
        }

        conn.execute("""
            INSERT INTO fl_products
            (sku, name, product_type, status, role, role_confirmed, cost_rmb)
            VALUES (?,?,?,?,?,0,0)
        """, (
            new_sku,
            c["product_name"],
            c.get("category") or "待分類",
            "idea",
            analysis.get("recommended_role") or "測試款",
        ))

    return {
        "ok": True,
        "sku": new_sku,
        "product_name": c["product_name"],
        "message": f"已升格為 fl_products：{new_sku}",
    }


# ─── Analyses ─────────────────────────────────────────────────────────────────

@selection_router.post("/analyze/{candidate_id}")
def analyze_candidate(candidate_id: str, body: AnalysisCreate):
    import json
    # 確認候選品存在
    with db() as conn:
        c = conn.execute(
            "SELECT product_name FROM ecommerce_selection_candidates WHERE candidate_id=?",
            (candidate_id,)
        ).fetchone()
        if not c:
            raise HTTPException(404, f"候選品 {candidate_id} 不存在")

    candidate_name = c["product_name"]

    # Step 1: Ori 搜尋競品
    _emit_ori("working", f"搜尋 {candidate_name} 競品資料與市場信號", target="sage")

    # 計算加權總分
    score_total, viability_band = compute_score(
        body.demand_score, body.competition_score, body.profit_score,
        body.pain_point_score, body.brand_fit_score,
    )
    score_breakdown = {
        "demand": body.demand_score,
        "competition": body.competition_score,
        "profit": body.profit_score,
        "pain_points": body.pain_point_score,
        "brand_fit": body.brand_fit_score,
        "formula": f"{body.demand_score}*2 + {body.profit_score}*2 + {body.pain_point_score} + {body.competition_score} + {body.brand_fit_score}",
        "weighted_total": score_total,
    }

    # 財務計算
    financials_result: dict = {}
    if body.financials:
        f = body.financials
        role = body.recommended_role or "毛利款"
        financials_result = compute_financials(
            cost_rmb=f.get("cost_rmb", 0),
            exchange_rate=f.get("exchange_rate", 4.5),
            platform_fee=f.get("platform_fee", 0.05),
            payment_fee=f.get("payment_fee", 0.12),
            ad_cost_est=f.get("ad_cost_est", 0),
            role=role,
        )

    # 自動推算角色（若未手動指定）
    recommended_role = body.recommended_role
    role_confidence = body.role_confidence
    if not recommended_role:
        if score_total >= 40 and body.profit_score >= 7:
            recommended_role, role_confidence = "主力款", 0.75
        elif body.profit_score >= 8:
            recommended_role, role_confidence = "毛利款", 0.70
        else:
            recommended_role, role_confidence = "引流款", 0.60

    today = date.today().isoformat()
    with db() as conn:
        cur = conn.execute("""
            INSERT INTO ecommerce_selection_analyses
            (candidate_id, analysis_date,
             demand_score, competition_score, profit_score, pain_point_score, brand_fit_score,
             score_total, score_breakdown_json, viability_band,
             market_metrics_json, competition_metrics_json, negative_reviews_json, financials_json,
             recommended_role, role_confidence, role_reasoning,
             decision_status, reasoning, analyzed_by_agent)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            candidate_id, today,
            body.demand_score, body.competition_score, body.profit_score,
            body.pain_point_score, body.brand_fit_score,
            score_total, json.dumps(score_breakdown, ensure_ascii=False), viability_band,
            json.dumps(body.market_metrics or {}, ensure_ascii=False),
            json.dumps(body.competition_metrics or {}, ensure_ascii=False),
            json.dumps(body.negative_reviews or [], ensure_ascii=False),
            json.dumps({**financials_result, **(body.financials or {})}, ensure_ascii=False),
            recommended_role, role_confidence, body.role_reasoning,
            body.decision_status, body.reasoning, body.analyzed_by_agent,
        ))
        analysis_id = cur.lastrowid
        # 同步更新候選品 selection_status
        new_sel_status = {
            "strong": "viable", "viable": "viable",
            "watchlist": "watchlist", "reject": "rejected",
        }.get(viability_band, "evaluating")
        conn.execute(
            "UPDATE ecommerce_selection_candidates SET selection_status=?, updated_at=CURRENT_TIMESTAMP WHERE candidate_id=?",
            (new_sel_status, candidate_id)
        )

    # Step 2: Sage 評分完成，交接給 Craft
    _emit_ori("idle")
    _emit_sage("working", f"對 {candidate_name} 進行 SOP 評分分析",
               target_agent_id="craft")

    # Step 3: Craft 產選品報告
    _emit_sage("idle")
    _emit_craft("working", f"整理 {candidate_name} 選品報告", source="sage",
                artifact_refs=[f"ecommerce/selection/analysis/{candidate_id}"])

    import json as _json
    try:
        from src.ai.craft_reporter import generate_selection_report
        analysis_for_report = {
            "score_total": score_total, "viability_band": viability_band,
            "demand_score": body.demand_score, "competition_score": body.competition_score,
            "profit_score": body.profit_score, "pain_point_score": body.pain_point_score,
            "brand_fit_score": body.brand_fit_score, "recommended_role": recommended_role,
            "reasoning": body.reasoning or "", "competitor_data": body.competition_metrics or {},
            "financials": financials_result,
        }
        report_md, report_summary = generate_selection_report(candidate_name, analysis_for_report)
        with db() as conn:
            conn.execute("""
                INSERT INTO ecommerce_selection_reports
                (analysis_id, candidate_id, report_title, report_markdown, summary_json, created_by_agent)
                VALUES (?,?,?,?,?,?)
            """, (
                analysis_id, candidate_id,
                f"選品報告：{candidate_name}",
                report_md,
                _json.dumps(report_summary, ensure_ascii=False),
                "craft",
            ))
    except Exception as _e:
        log.warning(f"Craft 報告生成失敗（不影響分析結果）：{_e}")

    # Phase 4.3: Memory Fabric — 選品報告寫入 artifacts 表
    try:
        from src.workflows.runner import record_artifact
        record_artifact(
            producer="craft",
            artifact_type="selection_report",
            db_ref=f"ecommerce_selection_reports/{candidate_id}",
            metadata={"candidate_id": candidate_id, "analysis_id": analysis_id,
                      "product_name": candidate_name, "score_total": score_total},
        )
    except Exception as _ae:
        log.warning(f"[MemoryFabric] selection_report artifact 記錄失敗：{_ae}")

    # Step 4: Craft awaiting_human — 等待你決策
    _emit_craft("idle")
    from src.api.agent_status import mark_agent_awaiting_human
    mark_agent_awaiting_human(
        "craft",
        message=f"{candidate_name} 選品報告完成，請決策",
        action_type="approve_purchase",
        ref_id=candidate_id,
        artifact_refs=[f"ecommerce/selection/analysis/{candidate_id}"],
    )

    return {
        "ok": True,
        "analysis_id": analysis_id,
        "score_total": score_total,
        "score_breakdown": score_breakdown,
        "viability_band": viability_band,
        "recommended_role": recommended_role,
        "role_confidence": role_confidence,
        **financials_result,
    }


class AutoAnalyzeRequest(BaseModel):
    category: str = ""
    notes: str = ""


@selection_router.post("/auto-analyze/{candidate_id}")
def auto_analyze_candidate(candidate_id: str, body: AutoAnalyzeRequest):
    """
    Phase 3A 全自動分析流程：
    Ori 搜競品 → Sage 自動評分 → Craft 產報告 → awaiting_human
    """
    import json
    from src.ai.competitor_analyzer import research_competitor
    from src.ai.sage_scorer import auto_score_candidate
    from src.ai.craft_reporter import generate_selection_report

    # 確認候選品存在
    with db() as conn:
        c = conn.execute(
            "SELECT product_name FROM ecommerce_selection_candidates WHERE candidate_id=?",
            (candidate_id,)
        ).fetchone()
        if not c:
            raise HTTPException(404, f"候選品 {candidate_id} 不存在")

    product_name = c["product_name"]

    # Step 1: Ori 搜尋競品
    _emit_ori("working", f"搜尋「{product_name}」競品資料與市場信號", target="sage")
    competitor_data = {}
    try:
        competitor_data = research_competitor(product_name, body.category)
    except Exception as e:
        log.warning(f"Ori 競品研究失敗，繼續流程：{e}")
    _emit_ori("idle")

    # Step 2: Sage 自動評分
    _emit_sage("working", f"對「{product_name}」進行 SOP 評分分析", target_agent_id="craft")
    scores = auto_score_candidate(product_name, competitor_data)

    demand_score = int(scores.get("demand_score", 5))
    competition_score = int(scores.get("competition_score", 5))
    profit_score = int(scores.get("profit_score", 5))
    pain_point_score = int(scores.get("pain_point_score", 5))
    brand_fit_score = int(scores.get("brand_fit_score", 5))
    market_type = scores.get("market_type", "demand")
    sage_reasoning = scores.get("reasoning", "")
    next_steps_data = {
        "recommendation": scores.get("recommendation", "觀察"),
        "confidence": scores.get("recommendation_confidence", "低"),
        "reasons": scores.get("recommendation_reasons", []),
        "next_steps": scores.get("next_steps", []),
        "warnings": scores.get("warnings", []),
    }

    score_total, viability_band = compute_score(
        demand_score, competition_score, profit_score, pain_point_score, brand_fit_score
    )
    score_breakdown = {
        "demand": demand_score, "competition": competition_score,
        "profit": profit_score, "pain_points": pain_point_score,
        "brand_fit": brand_fit_score,
        "formula": f"{demand_score}*2 + {profit_score}*2 + {pain_point_score} + {competition_score} + {brand_fit_score}",
        "weighted_total": score_total,
    }

    # 自動推算角色
    if score_total >= 40 and profit_score >= 7:
        recommended_role, role_confidence = "主力款", 0.75
    elif profit_score >= 8:
        recommended_role, role_confidence = "毛利款", 0.70
    else:
        recommended_role, role_confidence = "引流款", 0.60

    today = date.today().isoformat()
    with db() as conn:
        cur = conn.execute("""
            INSERT INTO ecommerce_selection_analyses
            (candidate_id, analysis_date,
             demand_score, competition_score, profit_score, pain_point_score, brand_fit_score,
             score_total, score_breakdown_json, viability_band,
             market_metrics_json, competition_metrics_json, negative_reviews_json, financials_json,
             recommended_role, role_confidence, role_reasoning,
             next_steps_json,
             decision_status, reasoning, analyzed_by_agent)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            candidate_id, today,
            demand_score, competition_score, profit_score, pain_point_score, brand_fit_score,
            score_total, json.dumps(score_breakdown, ensure_ascii=False), viability_band,
            json.dumps(competitor_data, ensure_ascii=False),
            json.dumps({"market_type": market_type}, ensure_ascii=False),
            json.dumps(competitor_data.get("pain_points", []), ensure_ascii=False),
            json.dumps({}, ensure_ascii=False),
            recommended_role, role_confidence, sage_reasoning,
            json.dumps(next_steps_data, ensure_ascii=False),
            "pending", sage_reasoning, "sage_auto",
        ))
        analysis_id = cur.lastrowid
        new_sel_status = {
            "strong": "viable", "viable": "viable",
            "watchlist": "watchlist", "reject": "rejected",
        }.get(viability_band, "evaluating")
        conn.execute(
            "UPDATE ecommerce_selection_candidates SET selection_status=?, updated_at=CURRENT_TIMESTAMP WHERE candidate_id=?",
            (new_sel_status, candidate_id)
        )
    _emit_sage("idle")

    # Step 3: Craft 產選品報告
    _emit_craft("working", f"整理「{product_name}」選品報告", source="sage",
                artifact_refs=[f"ecommerce/selection/analysis/{candidate_id}"])
    analysis_for_report = {
        "score_total": score_total, "viability_band": viability_band,
        "demand_score": demand_score, "competition_score": competition_score,
        "profit_score": profit_score, "pain_point_score": pain_point_score,
        "brand_fit_score": brand_fit_score, "recommended_role": recommended_role,
        "reasoning": sage_reasoning, "competitor_data": competitor_data,
        "financials": {},
    }
    report_md, report_summary = generate_selection_report(product_name, analysis_for_report)
    with db() as conn:
        conn.execute("""
            INSERT INTO ecommerce_selection_reports
            (analysis_id, candidate_id, report_title, report_markdown, summary_json, created_by_agent)
            VALUES (?,?,?,?,?,?)
        """, (
            analysis_id, candidate_id,
            f"選品報告：{product_name}",
            report_md,
            json.dumps(report_summary, ensure_ascii=False),
            "craft_auto",
        ))
    _emit_craft("idle")

    # Phase 4.3: Memory Fabric — 選品報告寫入 artifacts 表
    try:
        from src.workflows.runner import record_artifact
        record_artifact(
            producer="sage",
            artifact_type="selection_report",
            db_ref=f"ecommerce_selection_reports/{candidate_id}",
            metadata={"candidate_id": candidate_id, "analysis_id": analysis_id,
                      "product_name": product_name, "score_total": score_total},
        )
    except Exception as _ae:
        log.warning(f"[MemoryFabric] selection_report artifact 記錄失敗：{_ae}")

    # Step 4: awaiting_human — 等待你決策
    from src.api.agent_status import mark_agent_awaiting_human
    mark_agent_awaiting_human(
        "craft",
        message=f"{product_name} 選品報告完成，請決策",
        action_type="approve_purchase",
        ref_id=candidate_id,
        artifact_refs=[f"ecommerce/selection/analysis/{candidate_id}"],
    )

    return {
        "ok": True,
        "analysis_id": analysis_id,
        "candidate_id": candidate_id,
        "score_total": score_total,
        "viability_band": viability_band,
        "recommended_role": recommended_role,
    }


@selection_router.get("/analysis/{candidate_id}")
def get_analysis(candidate_id: str):
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM ecommerce_selection_analyses WHERE candidate_id=? ORDER BY analysis_date DESC LIMIT 1",
            (candidate_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"候選品 {candidate_id} 尚無分析結果")
    return dict(row)


# ─── Reports ──────────────────────────────────────────────────────────────────

@selection_router.post("/reports/{analysis_id}")
def create_report(analysis_id: int, body: ReportCreate):
    import json
    with db() as conn:
        a = conn.execute(
            "SELECT * FROM ecommerce_selection_analyses WHERE id=?", (analysis_id,)
        ).fetchone()
        if not a:
            raise HTTPException(404, f"分析 {analysis_id} 不存在")
        a = dict(a)
        c = conn.execute(
            "SELECT product_name, category, market_type FROM ecommerce_selection_candidates WHERE candidate_id=?",
            (a["candidate_id"],)
        ).fetchone()
        c = dict(c) if c else {}

    today = date.today().isoformat()
    title = body.report_title or f"{c.get('product_name', '未命名')} 選品報告 {today}"

    score_bd = json.loads(a.get("score_breakdown_json") or "{}")
    financials = json.loads(a.get("financials_json") or "{}")
    neg_reviews = json.loads(a.get("negative_reviews_json") or "[]")

    pain_points_md = ""
    for r in neg_reviews:
        pain_points_md += f"- **{r.get('pain_point','')}**（出現 {r.get('frequency',0)} 次）→ {r.get('opportunity','')}\n"

    report_md = f"""# {title}

> 評估日期：{today}
> 分析員：{a.get("analyzed_by_agent", "sage")}

---

## 基本資訊

| 欄位 | 內容 |
|------|------|
| 商品名稱 | {c.get('product_name', '-')} |
| 類別 | {c.get('category', '-')} |
| 市場類型 | {c.get('market_type', '-')} |
| 建議角色 | {a.get('recommended_role', '-')} |
| 角色信心 | {a.get('role_confidence', '-')} |

---

## 評分結果

**總分：{a.get('score_total', 0)} / 50 → {a.get('viability_band', '-').upper()}**

| 維度 | 分數 | 權重 |
|------|------|------|
| 需求強度 | {score_bd.get('demand', '-')} | x2 |
| 競品環境 | {score_bd.get('competition', '-')} | x1 |
| 獲利潛力 | {score_bd.get('profit', '-')} | x2 |
| 痛點機會 | {score_bd.get('pain_points', '-')} | x1 |
| 品牌契合 | {score_bd.get('brand_fit', '-')} | x1 |

公式：`{score_bd.get('formula', '-')}`

---

## 財務概覽

| 項目 | 數值 |
|------|------|
| 落地成本（TWD） | {financials.get('landed_cost_twd', '-')} |
| 最低售價 | {financials.get('min_viable_price', '-')} |
| 建議售價 | {financials.get('target_price', '-')} |
| 預估毛利率 | {financials.get('gross_margin', '-')} |

---

## 負評痛點與機會

{pain_points_md or "（尚未填入）"}

---

## 決策

**{a.get('decision_status', '待評估')}** — {a.get('reasoning', '尚未填入決策理由')}
"""

    summary = {
        "score": a.get("score_total"),
        "viability_band": a.get("viability_band"),
        "role": a.get("recommended_role"),
        "financials": financials,
    }

    with db() as conn:
        cur = conn.execute("""
            INSERT INTO ecommerce_selection_reports
            (analysis_id, candidate_id, report_title, report_markdown, summary_json, created_by_agent)
            VALUES (?,?,?,?,?,?)
        """, (analysis_id, a["candidate_id"], title,
              report_md, json.dumps(summary, ensure_ascii=False),
              body.created_by_agent))
        report_id = cur.lastrowid

    return {"ok": True, "report_id": report_id, "report_title": title, "preview": report_md[:300]}


@selection_router.get("/reports")
def list_reports(candidate_id: Optional[str] = Query(None)):
    with db() as conn:
        if candidate_id:
            rows = conn.execute(
                "SELECT id, analysis_id, candidate_id, report_title, created_by_agent, created_at FROM ecommerce_selection_reports WHERE candidate_id=? ORDER BY created_at DESC",
                (candidate_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, analysis_id, candidate_id, report_title, created_by_agent, created_at FROM ecommerce_selection_reports ORDER BY created_at DESC LIMIT 50"
            ).fetchall()
    return [dict(r) for r in rows]


@selection_router.get("/reports/{report_id}")
def get_report(report_id: int):
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM ecommerce_selection_reports WHERE id=?", (report_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, f"報告 {report_id} 不存在")
    return dict(row)


# ─── Portfolio ────────────────────────────────────────────────────────────────

@selection_router.get("/portfolio")
def get_portfolio():
    with db() as conn:
        rows = conn.execute("""
            SELECT a.recommended_role, COUNT(*) as count
            FROM ecommerce_selection_analyses a
            JOIN ecommerce_selection_candidates c ON a.candidate_id = c.candidate_id
            WHERE c.status IN ('shortlisted', 'approved')
            GROUP BY a.recommended_role
        """).fetchall()
        total = conn.execute(
            "SELECT COUNT(*) as n FROM ecommerce_selection_candidates WHERE status IN ('shortlisted','approved')"
        ).fetchone()

    dist = {r["recommended_role"]: r["count"] for r in rows}
    n = dict(total)["n"] if total else 0
    gaps = []
    for role, target_pct in [("主力款", 0.2), ("毛利款", 0.4), ("引流款", 0.4)]:
        current = dist.get(role, 0)
        target = round(n * target_pct)
        if current < target:
            gaps.append(f"缺 {role}（目前 {current}，建議至少 {target}）")

    return {
        "approved_count": n,
        "role_distribution": dist,
        "portfolio_target": {"引流款": "40%", "毛利款": "40%", "主力款": "20%"},
        "gaps": gaps or ["組合比例均衡"],
    }


@selection_router.post("/shortlist")
def generate_shortlist(body: ShortlistRequest):
    with db() as conn:
        rows = conn.execute("""
            SELECT c.candidate_id, c.product_name, c.market_type,
                   a.score_total, a.viability_band, a.recommended_role, a.analysis_date
            FROM ecommerce_selection_analyses a
            JOIN ecommerce_selection_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.score_total >= ?
              AND c.status NOT IN ('rejected')
            ORDER BY a.score_total DESC
            LIMIT ?
        """, (body.min_score, body.max_count)).fetchall()
    return [dict(r) for r in rows]


# ─── Lessons ─────────────────────────────────────────────────────────────────

@selection_router.get("/lessons")
def list_lessons(lesson_type: Optional[str] = Query(None)):
    with db() as conn:
        if lesson_type:
            rows = conn.execute(
                "SELECT * FROM ecommerce_selection_lessons WHERE lesson_type=? ORDER BY confidence DESC",
                (lesson_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM ecommerce_selection_lessons ORDER BY confidence DESC, created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


@selection_router.post("/lessons")
def create_lesson(body: LessonCreate):
    import json
    with db() as conn:
        cur = conn.execute("""
            INSERT INTO ecommerce_selection_lessons
            (theme, lesson_type, lesson_text, source_analysis_ids_json, confidence)
            VALUES (?,?,?,?,?)
        """, (
            body.theme, body.lesson_type, body.lesson_text,
            json.dumps(body.source_analysis_ids or [], ensure_ascii=False),
            body.confidence,
        ))
    return {"ok": True, "lesson_id": cur.lastrowid}


# ─── Bundle / Combo Design ────────────────────────────────────────────────────

class BundleSave(BaseModel):
    bundle_name: str
    scene: Optional[str] = None
    description: Optional[str] = None
    candidate_ids: list[str]
    bundle_price: Optional[float] = None
    suggestion_reason: Optional[str] = None
    status: Optional[str] = "suggested"


@selection_router.post("/batch-analyze")
def batch_analyze_candidates():
    """
    批量觸發所有 candidate 狀態（尚未分析）的候選品進行 auto-analyze。
    背景執行，即時回傳待分析清單。
    """
    import threading
    with db() as conn:
        rows = conn.execute("""
            SELECT c.candidate_id, c.product_name, c.category
            FROM ecommerce_selection_candidates c
            WHERE c.status = 'candidate'
            AND NOT EXISTS (
                SELECT 1 FROM ecommerce_selection_analyses a
                WHERE a.candidate_id = c.candidate_id
            )
        """).fetchall()
    pending = [dict(r) for r in rows]
    if not pending:
        return {"ok": True, "message": "沒有待分析的候選品", "count": 0}

    class _Req:
        def __init__(self, cat): self.category = cat; self.notes = ""

    def _run():
        for item in pending:
            try:
                req = _Req(item.get("category") or "")
                auto_analyze_candidate(item["candidate_id"], req)
            except Exception as e:
                log.warning(f"批量分析 {item['candidate_id']} 失敗：{e}")

    threading.Thread(target=_run, daemon=True).start()
    return {
        "ok": True,
        "message": f"已觸發 {len(pending)} 個候選品批量分析（背景執行）",
        "count": len(pending),
        "candidates": [p["product_name"] for p in pending],
    }


@selection_router.post("/bundles/suggest")
def suggest_bundles():
    """
    在售商品組合推薦（live-product based）。

    Priority order:
      1. fl_product_relations — manually set relations → 直接成組（source: relation）
      2. family_id 相同 → 同系列組合（source: family）
      3. role 互補，在售商品 → 角色互補組合（source: role）

    Fallback: 舊候選池邏輯（source: candidate）

    過濾條件：status IN active/listed/pending, total_stock > 0, cost_rmb NOT NULL
    輸出加 bundle_type: traffic | profit | scene
    """
    from collections import defaultdict

    COMPLEMENTARY_PAIRS = [
        ("引流款", "毛利款"),
        ("引流款", "主力款"),
        ("毛利款", "主力款"),
    ]
    MIN_STOCK        = 1     # at least 1 unit in stock (prevents OOS bundles)
    MARGIN_FLOOR     = 0.10  # skip margin check when no performance data (None → 0)
    MAX_PRICE_RATIO  = 8.0   # allow wider price spread for small catalogs
    HIGH_STOCK_FLOOR = 5     # units threshold for "slow-moving / overstock" detection

    def _dynamic_discount(avg_margin: float) -> float:
        """折扣依毛利動態調整，避免薄利商品被過度打折"""
        if avg_margin >= 0.50: return 0.85   # 15% off — 毛利豐厚可以讓利
        if avg_margin >= 0.40: return 0.88   # 12% off
        if avg_margin >= 0.30: return 0.92   #  8% off
        return 0.95                           #  5% off — 毛利薄，保守折扣

    def _is_compatible(prods: list) -> bool:
        """Guard: 過濾掉不合理的配對"""
        stocks  = [p.get("stock") or 0 for p in prods]
        prices  = [p.get("price") or 0 for p in prods]
        # raw margins — None means no performance data, not zero margin
        raw_margins = [p.get("gross_margin") for p in prods]
        # 任一商品庫存不足
        if min(stocks) < MIN_STOCK:
            return False
        # 若有實際毛利資料，才做毛利門檻檢查（None = 尚無績效資料，不能當負面信號）
        known = [m for m in raw_margins if m is not None]
        if known:
            avg_m = sum(known) / len(known)
            if avg_m < MARGIN_FLOOR:
                return False
        # 價格差距太懸殊（可能完全不同品類）
        nonzero_prices = [p for p in prices if p > 0]
        if len(nonzero_prices) >= 2:
            if max(nonzero_prices) / min(nonzero_prices) > MAX_PRICE_RATIO:
                return False
        return True

    def _bundle_type(role_comp: str, avg_margin: float, source: str, is_cleanup: bool = False) -> str:
        # inventory cleanup bundles → dedicated type
        if is_cleanup:
            return "cleanup"
        # family/scene_partner → always scene (meaningful context, not fallback)
        if source in ("family",):
            return "scene"
        # explicit traffic pairing + low margin → traffic
        if "引流款" in role_comp and avg_margin < 0.35:
            return "traffic"
        # high combined margin → profit
        if avg_margin >= 0.40:
            return "profit"
        # role pairing without clear traffic/profit signal → scene
        return "scene"

    def _viability_score(products: list, source: str, price_sum: float) -> float:
        """
        可行性評分（越高越優先顯示）
          - 平均毛利       × 40  (最重要：毛利健康的組合才值得推)
          - 最低庫存分     × 0.5 (兩件都要有足夠庫存)
          - 價格梯度分     × 10  (有明確高低價差 → 升級購買動機)
          - 來源加成              (手動設定 > 同系列 > 角色互補)
        """
        margins = [p.get("gross_margin") or 0 for p in products]
        stocks  = [p.get("stock") or 0 for p in products]
        prices  = [p.get("price") or 0 for p in products]
        avg_m   = sum(margins) / len(margins) if margins else 0
        min_stk = min(stocks) if stocks else 0
        max_p   = max(prices) if prices else 0
        min_p   = min(prices) if prices else 0
        ladder  = (max_p - min_p) / max_p if max_p > 0 else 0
        source_bonus = {"relation": 25, "family": 15, "role": 5, "candidate": 0}.get(source, 0)
        return round(avg_m * 40 + min_stk * 0.5 + ladder * 10 + source_bonus, 3)

    def _make_bundle(name: str, scene: str, source: str,
                     products: list, role_comp: str, bundle_type: str,
                     reason: str, action: str) -> dict:
        prices = [p.get("price") or 0 for p in products]
        margins = [p.get("gross_margin") or 0 for p in products]
        price_sum = sum(prices)
        avg_margin = sum(margins) / len(margins) if margins else 0
        discount = _dynamic_discount(avg_margin)
        bundle_price = round(price_sum * discount / 10) * 10 if price_sum else 0
        return {
            "bundle_name": name,
            "bundle_type": bundle_type,
            "scene": scene,
            "source": source,
            "products": products,
            "role_composition": role_comp,
            "base_price_sum": price_sum,
            "bundle_price": bundle_price,
            "discount_pct": round(1 - discount, 2),
            "estimated_margin": round(avg_margin, 3),
            "viability_score": _viability_score(products, source, price_sum),
            "suggestion_reason": reason,
            "bundle_action": action,
        }

    suggestions: list = []
    seen_pairs: set = set()  # avoid duplicate SKU pairs

    with db() as conn:
        # ── Live products ──────────────────────────────────────────────────
        live_rows = conn.execute("""
            SELECT
                p.sku,
                p.name,
                p.role,
                p.target_price,
                (
                    SELECT f.gross_margin
                    FROM fl_performance f
                    WHERE f.sku = p.sku
                    ORDER BY f.record_date DESC, f.id DESC
                    LIMIT 1
                ) AS gross_margin_est,
                COALESCE((
                    SELECT SUM(i.quantity)
                    FROM fl_inventory i
                    WHERE i.sku = p.sku
                ), 0) AS total_stock,
                p.family_id,
                p.family_name,
                p.variant_name
            FROM fl_products p
            WHERE p.status IN ('active','listed','pending','scaling','testing_ads')
              AND COALESCE((
                    SELECT SUM(i.quantity)
                    FROM fl_inventory i
                    WHERE i.sku = p.sku
                ), 0) > 0
        """).fetchall()

        # ── Relations ─────────────────────────────────────────────────────
        rel_rows = conn.execute("""
            SELECT
                r.sku AS source_sku,
                r.related_sku,
                r.relation_type,
                r.scene,
                r.notes,
                p1.name AS src_name,
                p1.role AS src_role,
                p1.target_price AS src_price,
                (
                    SELECT f.gross_margin
                    FROM fl_performance f
                    WHERE f.sku = p1.sku
                    ORDER BY f.record_date DESC, f.id DESC
                    LIMIT 1
                ) AS src_margin,
                COALESCE((
                    SELECT SUM(i.quantity)
                    FROM fl_inventory i
                    WHERE i.sku = p1.sku
                ), 0) AS src_stock,
                p2.name AS rel_name,
                p2.role AS rel_role,
                p2.target_price AS rel_price,
                (
                    SELECT f.gross_margin
                    FROM fl_performance f
                    WHERE f.sku = p2.sku
                    ORDER BY f.record_date DESC, f.id DESC
                    LIMIT 1
                ) AS rel_margin,
                COALESCE((
                    SELECT SUM(i.quantity)
                    FROM fl_inventory i
                    WHERE i.sku = p2.sku
                ), 0) AS rel_stock
            FROM fl_product_relations r
            JOIN fl_products p1 ON r.sku = p1.sku
            JOIN fl_products p2 ON r.related_sku = p2.sku
            WHERE COALESCE((
                    SELECT SUM(i.quantity)
                    FROM fl_inventory i
                    WHERE i.sku = p1.sku
                ), 0) > 0
              AND COALESCE((
                    SELECT SUM(i.quantity)
                    FROM fl_inventory i
                    WHERE i.sku = p2.sku
                ), 0) > 0
        """).fetchall()

    sku_map = {r["sku"]: dict(r) for r in live_rows}

    # Priority 1: manual relations
    for r in rel_rows:
        pair = tuple(sorted([r["source_sku"], r["related_sku"]]))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)

        src = {"sku": r["source_sku"], "name": r["src_name"], "role": r["src_role"] or "—",
               "price": r["src_price"] or 0, "gross_margin": r["src_margin"] or 0,
               "stock": r["src_stock"] or 0}
        rel = {"sku": r["related_sku"], "name": r["rel_name"], "role": r["rel_role"] or "—",
               "price": r["rel_price"] or 0, "gross_margin": r["rel_margin"] or 0,
               "stock": r["rel_stock"] or 0}

        if not _is_compatible([src, rel]):
            continue

        rel_label = {"bundle": "組合包", "cross_sell": "搭配推薦",
                     "upsell": "升級品", "scene_partner": "場景搭檔"}.get(r["relation_type"], r["relation_type"])
        scene = r["scene"] or "手動設定"
        role_comp = f"{src['role']}+{rel['role']}"
        avg_margin = ((src["gross_margin"] or 0) + (rel["gross_margin"] or 0)) / 2
        btype = _bundle_type(role_comp, avg_margin, "relation")

        reason = f"已手動設定為「{rel_label}」關係"
        if r["notes"]:
            reason += f"：{r['notes']}"
        action = "可直接上架蝦皮組合包或製作搭配內容"

        suggestions.append(_make_bundle(
            name=f"{src['name']} × {rel['name']}",
            scene=scene, source="relation",
            products=[src, rel], role_comp=role_comp,
            bundle_type=btype, reason=reason, action=action,
        ))

    # Priority 2: same family — full permutation, pick best-scoring pair per family
    import itertools
    family_groups: dict = defaultdict(list)
    for p in live_rows:
        if p["family_id"]:
            family_groups[p["family_id"]].append(dict(p))

    for fid, members in family_groups.items():
        if len(members) < 2:
            continue
        fname = members[0].get("family_name") or "同系列"
        best_pair = None
        best_score = -1.0

        for a, b in itertools.combinations(members, 2):
            pair = tuple(sorted([a["sku"], b["sku"]]))
            if pair in seen_pairs:
                continue
            prods = [
                {"sku": a["sku"], "name": a["name"], "role": a["role"] or "—",
                 "price": a["target_price"] or 0, "gross_margin": a["gross_margin_est"],
                 "stock": a["total_stock"] or 0},
                {"sku": b["sku"], "name": b["name"], "role": b["role"] or "—",
                 "price": b["target_price"] or 0, "gross_margin": b["gross_margin_est"],
                 "stock": b["total_stock"] or 0},
            ]
            if not _is_compatible(prods):
                continue
            score = _viability_score(prods, "family", sum(p["price"] for p in prods))
            if score > best_score:
                best_score = score
                best_pair = (pair, prods, a, b)

        if not best_pair:
            continue
        pair, prods, a, b = best_pair
        seen_pairs.add(pair)
        role_comp = f"{prods[0]['role']}+{prods[1]['role']}"
        a_label = a.get("variant_name") or a["name"]
        b_label = b.get("variant_name") or b["name"]
        suggestions.append(_make_bundle(
            name=f"{fname}·{a_label}+{b_label}",
            scene=fname, source="family",
            products=prods, role_comp=role_comp,
            bundle_type="scene",
            reason=f"同屬「{fname}」系列，{a_label}搭配{b_label}，有升級購買動機；系列內評分最佳配對。",
            action="適合做系列組合頁或內容展示，引導升級消費",
        ))

    # Priority 3: role complementarity — full permutation per pair type, pick best viability score
    role_map: dict = defaultdict(list)
    for p in live_rows:
        if p["role"]:
            role_map[p["role"]].append(dict(p))

    action_map = {
        "traffic": "引流款帶客流，高毛利款收利潤，適合同時投廣告",
        "profit":  "兩款毛利均健康，組合包保護整體利潤，避免單靠折扣衝量",
        "scene":   "角色互補，客單提升，適合一起上架或同步做內容",
    }

    for role_a, role_b in COMPLEMENTARY_PAIRS:
        a_list = role_map.get(role_a, [])
        b_list = role_map.get(role_b, [])
        if not a_list or not b_list:
            continue
        # full permutation of all a×b combinations, pick best viability score
        best_pair = None
        best_score = -1.0
        for a in a_list:
            for b in b_list:
                if a["sku"] == b["sku"]:
                    continue
                pair = tuple(sorted([a["sku"], b["sku"]]))
                if pair in seen_pairs:
                    continue
                prods = [
                    {"sku": a["sku"], "name": a["name"], "role": role_a,
                     "price": a["target_price"] or 0, "gross_margin": a["gross_margin_est"],
                     "stock": a["total_stock"] or 0},
                    {"sku": b["sku"], "name": b["name"], "role": role_b,
                     "price": b["target_price"] or 0, "gross_margin": b["gross_margin_est"],
                     "stock": b["total_stock"] or 0},
                ]
                if not _is_compatible(prods):
                    continue
                score = _viability_score(prods, "role", sum(p["price"] for p in prods))
                if score > best_score:
                    best_score = score
                    best_pair = (pair, prods)

        if not best_pair:
            continue
        pair, prods = best_pair
        seen_pairs.add(pair)
        role_comp = f"{role_a}+{role_b}"
        avg_margin = sum(p["gross_margin"] or 0 for p in prods) / len(prods)
        btype = _bundle_type(role_comp, avg_margin, "role")
        price_sum = sum(p["price"] for p in prods)
        discount = _dynamic_discount(avg_margin)
        bundle_price = round(price_sum * discount / 10) * 10

        suggestions.append(_make_bundle(
            name=f"{prods[0]['name']} × {prods[1]['name']}",
            scene="角色互補", source="role",
            products=prods, role_comp=role_comp, bundle_type=btype,
            reason=f"{role_a}帶流量，{role_b}提升客單毛利；組合包省 {round((1-discount)*100)}%，客單提升至 NT${bundle_price}。",
            action=action_map.get(btype, "適合一起上架"),
        ))

    # Priority 4: inventory cleanup — pair high-stock items with 引流款
    traffic_products = role_map.get("引流款", [])
    for p in live_rows:
        if (p["total_stock"] or 0) < HIGH_STOCK_FLOOR:
            continue
        if p["role"] == "引流款":
            continue  # traffic item doesn't need cleanup pairing with itself
        if not traffic_products:
            break
        # pick the best traffic partner not already seen
        for t in sorted(traffic_products, key=lambda x: x.get("gross_margin_est") or 0, reverse=True):
            pair = tuple(sorted([p["sku"], t["sku"]]))
            if pair in seen_pairs:
                continue
            prods = [
                {"sku": t["sku"], "name": t["name"], "role": t["role"] or "引流款",
                 "price": t["target_price"] or 0, "gross_margin": t["gross_margin_est"],
                 "stock": t["total_stock"] or 0},
                {"sku": p["sku"], "name": p["name"], "role": p["role"] or "主力款",
                 "price": p["target_price"] or 0, "gross_margin": p["gross_margin_est"],
                 "stock": p["total_stock"] or 0},
            ]
            if not _is_compatible(prods):
                break
            seen_pairs.add(pair)
            role_comp = f"{prods[0]['role']}+{prods[1]['role']}"
            suggestions.append(_make_bundle(
                name=f"清庫存特組·{p['name']} × {t['name']}",
                scene="庫存優化", source="role",
                products=prods, role_comp=role_comp, bundle_type="cleanup",
                reason=f"「{p['name']}」庫存達 {p['total_stock']} 件，搭配引流款加速去化；組合包保護單品定價，避免直接打折傷毛利。",
                action="適合做限時套組，引流款帶客流，順帶消化高庫存",
            ))
            break  # one cleanup bundle per slow-moving product

    # Fallback: old candidate-pool logic (source: candidate)
    import json as _json
    with db() as conn:
        cand_rows = conn.execute("""
            SELECT c.candidate_id, c.product_name, c.category,
                   a.recommended_role, a.score_total, a.financials_json
            FROM ecommerce_selection_analyses a
            JOIN ecommerce_selection_candidates c ON a.candidate_id = c.candidate_id
            WHERE c.status NOT IN ('rejected')
              AND a.recommended_role IS NOT NULL
            ORDER BY c.category, a.score_total DESC
        """).fetchall()

    cand_items = []
    for r in cand_rows:
        fin = _json.loads(r["financials_json"] or "{}")
        cand_items.append({
            "candidate_id": r["candidate_id"],
            "product_name": r["product_name"],
            "category": r["category"] or "一般",
            "role": r["recommended_role"],
            "score": r["score_total"],
            "target_price": fin.get("target_price", 0) or 0,
            "gross_margin": fin.get("gross_margin", 0) or 0,
        })

    cand_groups: dict = defaultdict(list)
    for item in cand_items:
        cand_groups[item["category"]].append(item)

    for scene, members in cand_groups.items():
        crole_map: dict = defaultdict(list)
        for m in members:
            crole_map[m["role"]].append(m)
        for role_a, role_b in COMPLEMENTARY_PAIRS:
            a_list2 = crole_map.get(role_a, [])
            b_list2 = crole_map.get(role_b, [])
            if not a_list2 or not b_list2:
                continue
            a2 = max(a_list2, key=lambda x: x["score"] or 0)
            b2 = max(b_list2, key=lambda x: x["score"] or 0)
            if a2["candidate_id"] == b2["candidate_id"]:
                continue
            price_sum = (a2["target_price"] or 0) + (b2["target_price"] or 0)
            avg_margin = ((a2["gross_margin"] or 0) + (b2["gross_margin"] or 0)) / 2
            cand_discount = _dynamic_discount(avg_margin)
            bundle_price = round(price_sum * cand_discount / 10) * 10
            role_comp = f"{role_a}+{role_b}"
            suggestions.append({
                "bundle_name": f"{scene}·{role_comp}候選套組",
                "bundle_type": _bundle_type(role_comp, avg_margin, "candidate"),
                "scene": scene,
                "source": "candidate",
                "products": [
                    {"name": a2["product_name"], "role": role_a, "price": a2["target_price"], "gross_margin": a2["gross_margin"]},
                    {"name": b2["product_name"], "role": role_b, "price": b2["target_price"], "gross_margin": b2["gross_margin"]},
                ],
                "role_composition": role_comp,
                "base_price_sum": price_sum,
                "bundle_price": bundle_price,
                "discount_pct": round(1 - cand_discount, 2),
                "estimated_margin": round(avg_margin, 3),
                "suggestion_reason": f"候選品互補配對（尚未上架）：{role_a}帶流量，{role_b}提升毛利。",
                "bundle_action": "上架後可轉為正式組合",
            })

    # Sort: live products first (by viability_score desc), candidates last
    live = sorted(
        [s for s in suggestions if s.get("source") != "candidate"],
        key=lambda x: x.get("viability_score", 0), reverse=True,
    )
    candidates = [s for s in suggestions if s.get("source") == "candidate"]
    sorted_suggestions = live + candidates

    return {"suggestions": sorted_suggestions, "count": len(sorted_suggestions)}


@selection_router.post("/bundles")
def save_bundle(body: BundleSave):
    """確認後儲存組合包"""
    import json
    with db() as conn:
        names = []
        for cid in body.candidate_ids:
            c = conn.execute(
                "SELECT product_name FROM ecommerce_selection_candidates WHERE candidate_id=?", (cid,)
            ).fetchone()
            names.append(dict(c)["product_name"] if c else cid)

        cur = conn.execute("""
            INSERT INTO ecommerce_selection_bundles
            (bundle_name, scene, description, candidate_ids_json, product_names_json,
             bundle_price, suggestion_reason, status)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            body.bundle_name, body.scene, body.description,
            json.dumps(body.candidate_ids, ensure_ascii=False),
            json.dumps(names, ensure_ascii=False),
            body.bundle_price, body.suggestion_reason, body.status or "suggested",
        ))
    return {"ok": True, "bundle_id": cur.lastrowid}


@selection_router.get("/bundles")
def list_bundles(status: Optional[str] = Query(None)):
    with db() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM ecommerce_selection_bundles WHERE status=? ORDER BY created_at DESC",
                (status,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM ecommerce_selection_bundles ORDER BY created_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]


@selection_router.patch("/bundles/{bundle_id}/status")
def update_bundle_status(bundle_id: int, status: str):
    with db() as conn:
        conn.execute(
            "UPDATE ecommerce_selection_bundles SET status=? WHERE id=?",
            (status, bundle_id)
        )
    return {"ok": True, "bundle_id": bundle_id, "status": status}
