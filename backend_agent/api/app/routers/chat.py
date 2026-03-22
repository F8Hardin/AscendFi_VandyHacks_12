import json
import os

import httpx
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.models.financial import FinancialContext

router = APIRouter()

SYSTEM_PROMPT = (
    "You are AscendFi, a compassionate and expert AI financial recovery advisor. "
    "You help users predict financial risks, optimize debt payoff, understand spending behavior, "
    "and build autonomous finance plans. Always be empathetic, practical, and non-judgmental."
)


def _context_summary(ctx: FinancialContext) -> str:
    return (
        f"Financial snapshot:\n"
        f"- Monthly income: ${ctx.monthly_income:,.2f}\n"
        f"- Checking balance: ${ctx.checking_balance:,.2f}\n"
        f"- Savings: ${ctx.savings_balance:,.2f}\n"
        f"- Credit score: {ctx.credit_score or 'unknown'}\n"
        f"- Bills: {len(ctx.bills)} upcoming\n"
        f"- Debts: {len(ctx.debts)} accounts "
        f"(total ${sum(d.balance for d in ctx.debts):,.2f})\n"
        f"- Life events: {[e.value for e in ctx.life_events] or 'none'}"
    )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    lm_base = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    lm_model = os.getenv("LM_STUDIO_MODEL", "local-model")

    # Build messages list with system prompt first
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Qwen (and most models) require the first non-system message to be from the user.
    # Drop any leading assistant messages (e.g. the UI's initial greeting).
    chat_messages = list(request.messages)
    while chat_messages and chat_messages[0].role != "user":
        chat_messages.pop(0)

    # Append financial context to the last user message
    context_note = (
        f"\n\nUser's financial context:\n{_context_summary(request.context)}"
        if request.context
        else ""
    )
    for i, msg in enumerate(chat_messages):
        content = msg.content
        if i == len(chat_messages) - 1 and msg.role == "user" and context_note:
            content += context_note
        messages.append({"role": msg.role, "content": content})

    async def event_generator():
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    f"{lm_base}/chat/completions",
                    json={"model": lm_model, "messages": messages, "stream": True},
                    headers={"Authorization": "Bearer lm-studio"},
                ) as response:
                    if not response.is_success:
                        body = await response.aread()
                        yield f"data: {json.dumps({'type': 'error', 'message': f'LM Studio {response.status_code}: {body.decode()[:200]}'})}\n\n"
                        yield f"data: {json.dumps({'type': 'done'})}\n\n"
                        return

                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        raw = line[6:].strip()
                        if raw == "[DONE]":
                            break
                        try:
                            chunk = json.loads(raw)
                            delta = chunk["choices"][0]["delta"]
                            # thinking models (e.g. Qwen3) emit reasoning_content before content
                            thinking = delta.get("reasoning_content", "")
                            if thinking:
                                yield f"data: {json.dumps({'type': 'thinking', 'text': thinking})}\n\n"
                            token = delta.get("content", "")
                            if token:
                                yield f"data: {json.dumps({'type': 'token', 'text': token})}\n\n"
                        except Exception:
                            continue

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
