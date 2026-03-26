"""
CEO Chat & Dynamic Pipeline Routes
  POST /api/chat
  POST /api/pipeline/dynamic
  GET  /api/pipeline/dynamic/tasks
"""
import asyncio
import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.utils.logger import get_logger

router = APIRouter()
log = get_logger("api.chat")

# Tasks that the Dynamic Orchestrator can actually handle
_EXECUTABLE_TASKS = {
    "content_research", "market_analysis", "topic_strategy",
    "draft_generation", "data_analysis", "seo_analysis",
    "product_evaluation", "copywriting",
}


class ChatMessage(BaseModel):
    message: str
    context: list[dict] | None = None
    image_base64: str | None = None


@router.post("/api/chat")
async def ceo_chat(body: ChatMessage):
    """
    CEO Agent：接收使用者訊息，偵測意圖並路由或直接回應。
    若 CEO 判斷 auto_execute=True 且 task_type 在可執行清單中，
    自動呼叫 Dynamic Orchestrator 並將執行結果附回。
    """
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="message 不能為空")
    try:
        from src.agents.ceo import process_message
        result = await process_message(body.message, body.context, body.image_base64)

        task_type: str | None = result.get("task_type")
        auto_execute: bool = result.get("auto_execute", False)

        # Auto-execute low-risk tasks identified by CEO
        if auto_execute and task_type and task_type in _EXECUTABLE_TASKS:
            try:
                from src.agents.dynamic_orchestrator import run_task
                log.info(f"[CEO] auto-executing task_type={task_type}")
                exec_result = await run_task(task_type, context=None)
                result["execution"] = {
                    "triggered": True,
                    "task_type": task_type,
                    "ok": exec_result.get("ok", exec_result.get("success", False)),
                    "summary": _summarize_exec(exec_result, task_type),
                    "raw": exec_result,
                }
                log.info(f"[CEO] task completed: task_type={task_type} ok={result['execution']['ok']}")
            except Exception as exec_err:
                log.error(f"[CEO] auto-execution failed for {task_type}: {exec_err}")
                result["execution"] = {
                    "triggered": True,
                    "task_type": task_type,
                    "ok": False,
                    "summary": f"執行失敗：{str(exec_err)[:100]}",
                }
        else:
            result["execution"] = None

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _summarize_exec(result: dict, task_type: str) -> str:
    """Convert raw execution result into a short human-readable summary."""
    if not result:
        return "執行完成（無輸出）"

    if task_type == "content_research":
        count = result.get("articles_count", result.get("count", "?"))
        return f"研究完成，找到 {count} 篇文章"

    if task_type == "data_analysis":
        posts = result.get("posts_count", result.get("total_posts", "?"))
        eng = result.get("avg_engagement", "?")
        return f"數據分析完成：{posts} 篇貼文，平均互動率 {eng}%"

    if task_type == "topic_strategy":
        top3 = result.get("top3", [])
        if top3:
            labels = "、".join(t.get("cluster_label", "?")[:15] for t in top3[:3])
            return f"Top 3 主題：{labels}"
        return "策略分析完成"

    if task_type == "market_analysis":
        return result.get("summary", "市場分析完成")

    if task_type in ("draft_generation", "copywriting"):
        path = result.get("drafts_path", "")
        return f"草稿生成完成 → {path}" if path else "草稿生成完成（進入審核佇列）"

    if task_type == "product_evaluation":
        count = result.get("candidates_count", result.get("count", "?"))
        return f"選品評估完成，{count} 個候選"

    # fallback
    ok = result.get("ok", result.get("success", "?"))
    return f"任務完成 (ok={ok})"


class DeliberateRequest(BaseModel):
    question: str


@router.post("/api/chat/deliberate")
async def ceo_deliberate(body: DeliberateRequest):
    """
    CEO Multi-Agent Deliberation：向 Ori、Lala、Sage 平行諮詢後，
    由 CEO Claude 綜合給出建議。適合複雜決策與深度分析。
    """
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="question 不能為空")
    try:
        from src.agents.ceo import deliberate
        result = await deliberate(body.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/chat/deliberate/stream")
async def ceo_deliberate_stream(question: str = Query(...)):
    """
    SSE streaming version of CEO deliberation.
    Yields: data: {"type":"agent", "agent":..., "success":..., "summary":...}
            data: {"type":"synthesis", "consensus":..., "recommendation":..., ...}
            data: [DONE]
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="question 不能為空")

    async def event_gen():
        from src.agents.ceo import _consult_agent, _DELIBERATION_AGENTS, _DELIBERATION_PROMPT
        from src.config import settings
        import re

        # Step 1: Consult agents, yield each result as it completes
        agent_inputs: list[dict] = []
        tasks = {
            asyncio.create_task(_consult_agent(agent_id, task_type, question)): agent_id
            for agent_id, task_type in _DELIBERATION_AGENTS.items()
        }
        pending = set(tasks)
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                result = t.result()
                agent_inputs.append(result)
                payload = {"type": "agent", **result}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

        # Step 2: Synthesize with CEO Claude
        if not settings.anthropic_api_key:
            yield f"data: {json.dumps({'type': 'error', 'message': 'ANTHROPIC_API_KEY not set'})}\n\n"
            yield "data: [DONE]\n\n"
            return

        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        inputs_text = "\n".join(
            f"[{r['agent'].upper()}] {r['summary']}" for r in agent_inputs if r.get("success")
        ) or "（各顧問均未能提供有效資料）"
        synthesis_prompt = f"問題：{question}\n\n各顧問分析結果：\n{inputs_text}"

        try:
            resp = client.messages.create(
                model=settings.model_write,
                max_tokens=1024,
                system=_DELIBERATION_PROMPT,
                messages=[{"role": "user", "content": synthesis_prompt}],
            )
            raw = resp.content[0].text.strip()
            raw = re.sub(r"```(?:json)?\s*", "", raw).strip()
            synthesis = json.loads(raw)
        except Exception as e:
            synthesis = {
                "consensus": "無法解析", "key_insights": [], "divergences": None,
                "recommendation": "請重試", "confidence": "low", "next_steps": [],
            }
            log.warning(f"[Deliberate/stream] synthesis error: {e}")

        synthesis["type"] = "synthesis"
        synthesis["agent_inputs"] = agent_inputs
        yield f"data: {json.dumps(synthesis, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


class DynamicTaskRequest(BaseModel):
    task_type: str
    context: dict | None = None


@router.post("/api/pipeline/dynamic")
async def dynamic_pipeline(req: DynamicTaskRequest):
    """動態任務調度端點（Phase 4）"""
    if not req.task_type.strip():
        raise HTTPException(status_code=400, detail="task_type 不能為空")
    try:
        from src.agents.dynamic_orchestrator import run_task
        result = await run_task(req.task_type, req.context)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/pipeline/dynamic/tasks")
async def list_dynamic_tasks():
    """列出所有支援的動態任務類型"""
    try:
        from src.agents.dynamic_orchestrator import get_supported_tasks
        from src.registry.reader import describe_routing
        return {
            "supported_tasks": get_supported_tasks(),
            "routing_description": describe_routing(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
