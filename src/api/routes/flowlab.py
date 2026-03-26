"""
Flow Lab 視覺工作流路由
  POST /api/flowlab/screenshot-analyze        — 截圖上傳 → Vision 提取 → Shopee + Threads 草稿 → awaiting_approval
  GET  /api/flowlab/screenshots               — 列出所有截圖分析記錄
  GET  /api/flowlab/screenshots/{id}          — 取得單筆截圖分析結果
  POST /api/flowlab/screenshots/{id}/decide   — 核准 / 拒絕截圖分析

  POST /api/flowlab/video-upload              — 影片上傳（M1）→ 儲存 + 建立 DB 記錄 + 排程分析
  GET  /api/flowlab/video-analyses            — 列出所有影片分析記錄
  GET  /api/flowlab/video-analyses/{id}       — 取得單筆影片分析結果
  POST /api/flowlab/video-analyses/{id}/decide — 核准 / 拒絕影片分析
"""
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

from src.utils.logger import get_logger

router = APIRouter()
log = get_logger("api.flowlab")


class ScreenshotAnalyzeRequest(BaseModel):
    image_base64: str
    image_type: str = "image/jpeg"  # image/jpeg | image/png | image/webp
    context: str = ""               # 使用者附加說明（產品定位、目標客群等）


class ScreenshotDecideRequest(BaseModel):
    decision: str   # "approved" | "rejected"
    note: str = ""


@router.post("/api/flowlab/screenshot-analyze")
async def screenshot_analyze(body: ScreenshotAnalyzeRequest):
    """
    Phase 6 主入口：
    1. Claude Vision 提取產品資訊
    2. 生成 Shopee 文案 + Threads 草稿
    3. 寫入 artifacts 表
    4. 建立 approval_request（CEO 審核）
    5. 回傳提取結果 + 草稿
    """
    from src.agents.screenshot_analyzer import analyze_screenshot
    from src.db.connection import db

    analysis_id = str(uuid.uuid4())
    log.info(f"[FlowLab] screenshot-analyze 開始：id={analysis_id}")

    # Step 1-3: Vision 提取 + 草稿生成
    result = await analyze_screenshot(
        image_base64=body.image_base64,
        image_type=body.image_type,
        context=body.context,
    )

    if not result["ok"]:
        return {"ok": False, "error": result.get("error"), "analysis_id": analysis_id}

    extraction = result["extraction"]
    shopee_draft = result.get("shopee_draft", {})
    threads_draft = result.get("threads_draft", {})
    product_name = extraction.get("product_name", "未知產品")

    # Step 4: 寫入 DB
    try:
        with db() as conn:
            conn.execute(
                """INSERT INTO flowlab_screenshot_analyses
                   (id, extraction_json, shopee_draft, threads_draft, context, status)
                   VALUES (?,?,?,?,?,?)""",
                (
                    analysis_id,
                    json.dumps(extraction, ensure_ascii=False),
                    json.dumps(shopee_draft, ensure_ascii=False),
                    json.dumps(threads_draft, ensure_ascii=False),
                    body.context,
                    "pending",
                ),
            )
    except Exception as e:
        log.error(f"[FlowLab] DB 寫入失敗：{e}")
        return {"ok": False, "error": f"DB 寫入失敗：{e}", "analysis_id": analysis_id}

    # Step 5: Memory Fabric — 寫入 artifacts 表
    artifact_id = ""
    try:
        from src.workflows.runner import record_artifact
        art = record_artifact(
            producer="ori",
            artifact_type="screenshot_extraction",
            db_ref=f"flowlab_screenshot_analyses/{analysis_id}",
            metadata={
                "product_name": product_name,
                "analysis_id": analysis_id,
                "confidence": extraction.get("extraction_confidence", 0),
            },
        )
        artifact_id = art.id
        log.info(f"[FlowLab] artifact 記錄完成：{artifact_id}")
    except Exception as e:
        log.warning(f"[FlowLab] artifact 記錄失敗（不影響輸出）：{e}")

    # Step 6: 建立 approval_request（CEO 審核截圖分析結果）
    approval_id = ""
    try:
        from src.workflows.approval import request_approval
        approval_id = request_approval(
            action="approve_screenshot",
            evidence={
                "product_name": product_name,
                "analysis_id": analysis_id,
                "extraction": extraction,
                "shopee_draft": shopee_draft,
                "threads_draft": threads_draft,
            },
            risk_level="medium",
        )
        log.info(f"[FlowLab] approval_request 建立：{approval_id}")
    except Exception as e:
        log.warning(f"[FlowLab] approval_request 建立失敗：{e}")

    # 更新 DB 記錄 approval_id 和 artifact_id
    if approval_id or artifact_id:
        try:
            with db() as conn:
                conn.execute(
                    "UPDATE flowlab_screenshot_analyses SET approval_id=?, artifact_id=? WHERE id=?",
                    (approval_id, artifact_id, analysis_id),
                )
        except Exception as e:
            log.warning(f"[FlowLab] 更新 approval/artifact id 失敗：{e}")

    # Step 7: AI Office 通知
    try:
        from src.api.agent_status import mark_agent_awaiting_human
        mark_agent_awaiting_human(
            "ori",
            message=f"截圖分析完成：{product_name}，請確認草稿",
            action_type="approve_screenshot_analysis",
            ref_id=analysis_id,
            artifact_refs=[f"flowlab/screenshot/{analysis_id}"],
        )
    except Exception:
        pass

    return {
        "ok": True,
        "analysis_id": analysis_id,
        "artifact_id": artifact_id,
        "approval_id": approval_id,
        "product_name": product_name,
        "extraction": extraction,
        "shopee_draft": shopee_draft,
        "threads_draft": threads_draft,
    }


@router.get("/api/flowlab/screenshots")
async def list_screenshots(limit: int = 20, status: str | None = None):
    """列出截圖分析記錄"""
    from src.db.connection import db
    try:
        with db() as conn:
            if status:
                rows = conn.execute(
                    """SELECT id, extraction_json, status, context, created_at
                       FROM flowlab_screenshot_analyses WHERE status=?
                       ORDER BY created_at DESC LIMIT ?""",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, extraction_json, status, context, created_at
                       FROM flowlab_screenshot_analyses
                       ORDER BY created_at DESC LIMIT ?""",
                    (limit,),
                ).fetchall()
        results = []
        for r in rows:
            extraction = {}
            try:
                extraction = json.loads(r["extraction_json"] or "{}")
            except Exception:
                pass
            results.append({
                "id": r["id"],
                "product_name": extraction.get("product_name", "未知"),
                "category": extraction.get("category", ""),
                "confidence": extraction.get("extraction_confidence", 0),
                "status": r["status"],
                "created_at": r["created_at"],
            })
        return {"screenshots": results, "count": len(results)}
    except Exception as e:
        log.error(f"[FlowLab] 列表查詢失敗：{e}")
        return {"screenshots": [], "count": 0, "error": str(e)}


@router.get("/api/flowlab/screenshots/{analysis_id}")
async def get_screenshot(analysis_id: str):
    """取得單筆截圖分析結果（含完整草稿）"""
    from src.db.connection import db
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM flowlab_screenshot_analyses WHERE id=?",
                (analysis_id,),
            ).fetchone()
        if not row:
            return {"ok": False, "error": "分析記錄不存在"}
        return {
            "ok": True,
            "id": row["id"],
            "extraction": json.loads(row["extraction_json"] or "{}"),
            "shopee_draft": json.loads(row["shopee_draft"] or "{}"),
            "threads_draft": json.loads(row["threads_draft"] or "{}"),
            "approval_id": row["approval_id"],
            "artifact_id": row["artifact_id"],
            "status": row["status"],
            "context": row["context"],
            "created_at": row["created_at"],
        }
    except Exception as e:
        log.error(f"[FlowLab] 取得分析記錄失敗：{e}")
        return {"ok": False, "error": str(e)}


@router.post("/api/flowlab/screenshots/{analysis_id}/decide")
async def decide_screenshot(analysis_id: str, body: ScreenshotDecideRequest):
    """CEO 核准或拒絕截圖分析結果"""
    from src.db.connection import db
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT approval_id FROM flowlab_screenshot_analyses WHERE id=?",
                (analysis_id,),
            ).fetchone()
            if not row:
                return {"ok": False, "error": "分析記錄不存在"}

            conn.execute(
                "UPDATE flowlab_screenshot_analyses SET status=? WHERE id=?",
                (body.decision, analysis_id),
            )

            # 同步更新 approval_requests
            if row["approval_id"]:
                try:
                    from src.workflows.approval import decide
                    decide(row["approval_id"], body.decision, body.note)
                except Exception as e:
                    log.warning(f"[FlowLab] approval decide 失敗：{e}")

        log.info(f"[FlowLab] {analysis_id} → {body.decision}")
        return {"ok": True, "analysis_id": analysis_id, "decision": body.decision}
    except Exception as e:
        log.error(f"[FlowLab] decide 失敗：{e}")
        return {"ok": False, "error": str(e)}


# ── Video Analysis (M1) ────────────────────────────────────────────────────────

_ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}
_MAX_VIDEO_BYTES = 100 * 1024 * 1024   # 100 MB
_UPLOAD_DIR = Path("data/uploads/videos")


class VideoDecideRequest(BaseModel):
    decision: str   # "approved" | "rejected"
    note: str = ""


@router.post("/api/flowlab/video-upload")
async def video_upload(file: UploadFile = File(...)):
    """
    Video Ingestion M1 — 上傳影片並建立分析任務。

    1. 驗證檔案類型 + 大小
    2. 儲存至 data/uploads/videos/{uuid}.{ext}
    3. 建立 flowlab_video_analyses 記錄（status=processing）
    4. 記錄 workflow artifact
    5. 建立 approval_request（medium risk，進 CEO inbox）
    6. 觸發背景分析（M2 stub — VideoFrameAdapter not yet implemented）
    """
    from src.db.connection import db
    from src.db.schema import init_db

    # Validate content type
    content_type = file.content_type or ""
    if content_type not in _ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported video type: {content_type}. Allowed: mp4, mov, webm",
        )

    # Read and size-check
    data = await file.read()
    if len(data) > _MAX_VIDEO_BYTES:
        raise HTTPException(status_code=413, detail="Video exceeds 100 MB limit")

    # Determine extension
    ext_map = {
        "video/mp4": "mp4",
        "video/quicktime": "mov",
        "video/webm": "webm",
    }
    ext = ext_map.get(content_type, "mp4")
    video_id = str(uuid.uuid4())
    filename = f"{video_id}.{ext}"

    # Save to disk
    init_db()
    _UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    video_path = _UPLOAD_DIR / filename
    video_path.write_bytes(data)
    relative_path = f"data/uploads/videos/{filename}"
    log.info(f"[FlowLab/Video] saved {len(data)//1024}KB → {relative_path}")

    # Write DB record
    try:
        with db() as conn:
            conn.execute(
                """INSERT INTO flowlab_video_analyses
                   (id, video_path, original_filename, status)
                   VALUES (?,?,?,?)""",
                (video_id, relative_path, file.filename or filename, "processing"),
            )
    except Exception as e:
        log.error(f"[FlowLab/Video] DB write failed: {e}")
        raise HTTPException(status_code=500, detail=f"DB write failed: {e}")

    # Record artifact
    artifact_id = ""
    try:
        from src.workflows.runner import record_artifact
        art = record_artifact(
            producer="ori",
            artifact_type="video_analysis",
            file_path=relative_path,
            metadata={"video_id": video_id, "original_filename": file.filename or filename},
        )
        artifact_id = art.id
    except Exception as e:
        log.warning(f"[FlowLab/Video] artifact record failed (non-fatal): {e}")

    # Create approval request (medium risk → creates review_item in CEO inbox)
    approval_id = ""
    try:
        from src.workflows.approval import request_approval
        approval_id = request_approval(
            action="approve_video_analysis",
            risk_level="medium",
            evidence={
                "video_id": video_id,
                "original_filename": file.filename or filename,
                "file_size_kb": len(data) // 1024,
                "artifact_id": artifact_id,
            },
        )
    except Exception as e:
        log.warning(f"[FlowLab/Video] approval request failed (non-fatal): {e}")

    # Update DB with approval_id + artifact_id
    if approval_id or artifact_id:
        try:
            with db() as conn:
                conn.execute(
                    "UPDATE flowlab_video_analyses SET approval_id=?, artifact_id=? WHERE id=?",
                    (approval_id, artifact_id, video_id),
                )
        except Exception as e:
            log.warning(f"[FlowLab/Video] approval/artifact update failed: {e}")

    # M2 stub: frame extraction would be triggered here when VideoFrameAdapter is implemented
    log.info(
        f"[FlowLab/Video] M2 frame extraction deferred — "
        "VideoFrameAdapter stub, awaiting ffmpeg/cloud credentials"
    )

    return {
        "ok": True,
        "video_id": video_id,
        "video_path": relative_path,
        "artifact_id": artifact_id,
        "approval_id": approval_id,
        "status": "processing",
        "note": "Frame extraction pending — VideoFrameAdapter not yet implemented",
    }


@router.get("/api/flowlab/video-analyses")
async def list_video_analyses(limit: int = 20, status: str | None = None):
    """列出影片分析記錄"""
    from src.db.connection import db
    try:
        with db() as conn:
            if status:
                rows = conn.execute(
                    """SELECT id, video_path, original_filename, status, duration_secs, created_at
                       FROM flowlab_video_analyses WHERE status=?
                       ORDER BY created_at DESC LIMIT ?""",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, video_path, original_filename, status, duration_secs, created_at
                       FROM flowlab_video_analyses
                       ORDER BY created_at DESC LIMIT ?""",
                    (limit,),
                ).fetchall()
        return {
            "videos": [dict(r) for r in rows],
            "count": len(rows),
        }
    except Exception as e:
        log.error(f"[FlowLab/Video] list failed: {e}")
        return {"videos": [], "count": 0, "error": str(e)}


@router.get("/api/flowlab/video-analyses/{video_id}")
async def get_video_analysis(video_id: str):
    """取得單筆影片分析結果"""
    from src.db.connection import db
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT * FROM flowlab_video_analyses WHERE id=?",
                (video_id,),
            ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Video analysis not found")
        r = dict(row)
        # Deserialize JSON columns
        r["keyframe_paths"] = json.loads(r.get("keyframe_paths_json") or "[]")
        r["extracted_products"] = json.loads(r.get("extracted_products") or "[]")
        return {"ok": True, **r}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"[FlowLab/Video] get failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/flowlab/video-analyses/{video_id}/decide")
async def decide_video_analysis(video_id: str, body: VideoDecideRequest):
    """CEO 核准或拒絕影片分析結果"""
    from src.db.connection import db
    try:
        with db() as conn:
            row = conn.execute(
                "SELECT approval_id FROM flowlab_video_analyses WHERE id=?",
                (video_id,),
            ).fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Video analysis not found")

            conn.execute(
                "UPDATE flowlab_video_analyses SET status=? WHERE id=?",
                (body.decision, video_id),
            )

            if row["approval_id"]:
                try:
                    from src.workflows.approval import decide
                    decide(row["approval_id"], body.decision, body.note)
                except Exception as e:
                    log.warning(f"[FlowLab/Video] approval decide failed: {e}")

        log.info(f"[FlowLab/Video] {video_id} → {body.decision}")
        return {"ok": True, "video_id": video_id, "decision": body.decision}
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"[FlowLab/Video] decide failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
