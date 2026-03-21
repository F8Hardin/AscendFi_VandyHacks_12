import asyncio
import json
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from app.agent import init_agent, get_executor, _context_summary
from app.callbacks import StreamingAgentCallbackHandler
from app.models import ChatRequest

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_agent()
    yield


app = FastAPI(title="AscendFi Agent", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    executor = get_executor()
    queue: asyncio.Queue = asyncio.Queue()
    handler = StreamingAgentCallbackHandler(queue)

    # Build input dict — include the financial context snapshot in the prompt
    user_input = request.messages[-1].content if request.messages else ""
    context_note = (
        f"\n\nUser's financial context:\n{_context_summary(request.context)}"
        if request.context
        else ""
    )
    full_input = user_input + context_note

    async def event_generator():
        task = asyncio.ensure_future(
            executor.ainvoke(
                {"input": full_input},
                config={"callbacks": [handler]},
            )
        )

        while True:
            event = await queue.get()
            if event is None:
                break
            yield f"data: {json.dumps(event)}\n\n"

        # Ensure the task is fully complete before ending the stream
        try:
            await task
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
