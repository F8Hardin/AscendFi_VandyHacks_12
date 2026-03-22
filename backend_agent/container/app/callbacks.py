import asyncio
from typing import Any
from langchain_core.callbacks import AsyncCallbackHandler


class StreamingAgentCallbackHandler(AsyncCallbackHandler):
    """Puts typed events onto an asyncio.Queue for the SSE generator to consume."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token:
            await self.queue.put({"type": "token", "text": token})

    async def on_tool_start(
        self, serialized: dict, input_str: str, **kwargs: Any
    ) -> None:
        await self.queue.put({
            "type": "tool_start",
            "name": serialized.get("name", ""),
            "input": input_str,
        })

    async def on_tool_end(self, output: str, **kwargs: Any) -> None:
        await self.queue.put({
            "type": "tool_end",
            "output": output[:300] if output else "",  # truncate for frontend
        })

    async def on_agent_finish(self, finish: Any, **kwargs: Any) -> None:
        await self.queue.put(None)  # sentinel — signals stream is done

    async def on_chain_error(self, error: Exception, **kwargs: Any) -> None:
        await self.queue.put({"type": "error", "message": str(error)})
        await self.queue.put(None)

    async def on_tool_error(self, error: Exception, **kwargs: Any) -> None:
        await self.queue.put({"type": "tool_error", "message": str(error)})
