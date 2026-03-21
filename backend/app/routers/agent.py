import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agents import get_agent, set_active_agent, list_agents
from app.models.chat import ChatRequest
from app.models.financial import FinancialContext

router = APIRouter()


# ── Agent management ──────────────────────────────────────────────────────

@router.get("/agents")
async def get_agents():
    """List all registered agents."""
    return {"agents": list_agents()}


@router.post("/agents/{name}/activate")
async def activate_agent(name: str):
    """Switch the active agent at runtime."""
    set_active_agent(name)
    return {"active_agent": name}


# ── Conversational chat (SSE) ─────────────────────────────────────────────

@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    agent = get_agent()

    async def event_generator():
        async for chunk in agent.chat_stream(request.messages, request.context):
            yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── Predictive risk ───────────────────────────────────────────────────────

@router.post("/predict/missing-payments")
async def predict_missing_payments(context: FinancialContext):
    return await get_agent().predict_missing_payments(context)


@router.post("/predict/overdraft")
async def predict_overdraft(context: FinancialContext):
    return await get_agent().overdraft_probability(context)


@router.post("/predict/credit-score")
async def predict_credit_score(context: FinancialContext):
    return await get_agent().credit_score_shifts(context)


# ── Debt optimization ─────────────────────────────────────────────────────

@router.post("/debt/optimize")
async def optimize_debt(context: FinancialContext):
    return await get_agent().optimize_debt(context)


# ── Behavioral spending ───────────────────────────────────────────────────

@router.post("/spending/analyze")
async def analyze_spending(context: FinancialContext):
    return await get_agent().analyze_spending(context)


# ── Autonomous finance ────────────────────────────────────────────────────

@router.post("/finance/autonomous-plan")
async def autonomous_plan(context: FinancialContext):
    return await get_agent().autonomous_plan(context)
