"""
Base agent class — all specialized agents extend this.
Handles the tool-use agentic loop with streaming, peer-context injection,
and automatic post-run publishing to the AgentBus.

Two base classes are provided:
  - BaseFinancialAgent        — Anthropic Claude (Supervisor, Risk, Investment)
  - OpenAICompatibleAgent     — OpenAI / Gemini / Qwen via OpenAI-compatible endpoints
                                (Debt → GPT-4o mini, Behaviour → Gemini Flash, Wealth → Qwen-Plus)

Tool execution routing:
  - block.type == "tool_use"        → custom Python tools (calculators + market data + ML)
  - block.type == "server_tool_use" → handled by Anthropic servers (web search/fetch)
  - stop_reason == "pause_turn"     → server-side tool loop hit iteration limit; re-send

Agent communication (AgentBus):
  - Before run: peer summaries from other agents are prepended to the user message
  - After run:  the agent's response summary is published to the bus for peers to read
"""

import json
from typing import Optional
import anthropic
import google.generativeai as genai
from config import MODEL, STREAM_MAX_TOKENS
from tools.financial_calculators import execute_tool
from tools.market_data import execute_market_tool
from tools.ml_predictor import execute_ml_tool
from agents.agent_bus import bus


# Names of server-side tools — Anthropic-hosted only, skip for other providers
SERVER_SIDE_TOOLS = {"web_search", "web_fetch"}


class BaseFinancialAgent:
    def __init__(self, name: str, system_prompt: str, tools: list[dict], model: str = MODEL):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.model = model
        self.client = anthropic.Anthropic()

    # ── Tool routing ───────────────────────────────────────────────────────────

    def _execute_custom_tool(self, name: str, inputs: dict) -> str:
        """
        Route a tool call to the correct executor.
        Priority: financial calculators → ML predictor → market data.
        Server-side tools (web_search, web_fetch) are never called here.
        """
        from tools.financial_calculators import TOOL_FUNCTIONS
        from tools.market_data import MARKET_TOOL_FUNCTIONS
        from tools.ml_predictor import ML_TOOL_FUNCTIONS

        from tools.dashboard_generator import DASHBOARD_TOOL_FUNCTIONS, execute_dashboard_tool
        from tools.web_search import WEB_SEARCH_TOOL_FUNCTIONS, execute_web_search_tool
        from tools.spending_predictor import SPENDING_PREDICTOR_FUNCTIONS, execute_spending_predictor_tool

        if name in TOOL_FUNCTIONS:
            return execute_tool(name, inputs)
        if name in ML_TOOL_FUNCTIONS:
            return execute_ml_tool(name, inputs)
        if name in MARKET_TOOL_FUNCTIONS:
            return execute_market_tool(name, inputs)
        if name in DASHBOARD_TOOL_FUNCTIONS:
            return execute_dashboard_tool(name, inputs)
        if name in WEB_SEARCH_TOOL_FUNCTIONS:
            return execute_web_search_tool(name, inputs)
        if name in SPENDING_PREDICTOR_FUNCTIONS:
            return execute_spending_predictor_tool(name, inputs)

        import json
        return json.dumps({"error": f"Unknown tool: {name}"})

    # ── Bus helpers ────────────────────────────────────────────────────────────

    def _inject_peer_context(self, user_message: str) -> str:
        """Prepend available peer-agent summaries to the user message."""
        context_block = bus.get_peer_context_block(self.name)
        if not context_block:
            return user_message
        return f"{user_message}\n\n{context_block}"

    def _extract_summary(self, response: str) -> str:
        """Extract a brief summary from the response for peer injection."""
        if not response:
            return ""
        text = response.strip()[:500]
        # Try to end at a natural sentence boundary
        for sep in (". ", ".\n", "! ", "? "):
            idx = text.rfind(sep)
            if idx > 60:
                return text[: idx + 1].strip()
        return text.strip()

    def _publish_result(self, response: str, topic: str = "") -> None:
        """Publish a summary of this agent's findings to the bus."""
        if not response:
            return
        if not topic:
            topic = self.name.lower().replace(" ", "_") + "_finding"
        summary = self._extract_summary(response)
        bus.publish(sender=self.name, topic=topic, data=response[:2000], summary=summary)

    # ── Main agentic loop ──────────────────────────────────────────────────────

    def run(self, user_message: str, stream_callback=None) -> str:
        """
        Run the agent on a message. Handles the full tool-use loop including:
        - Peer context injection from the AgentBus
        - Custom Python tool execution (calculators + ML predictor + market data)
        - Server-side tool pass-through (web_search, web_fetch)
        - pause_turn re-send (when server-side tools hit the 10-iteration limit)
        - Post-run publishing of findings to the AgentBus

        stream_callback(text) is called for each streamed token if provided.
        Returns the final text response.
        """
        enriched_message = self._inject_peer_context(user_message)
        messages = [{"role": "user", "content": enriched_message}]
        full_response = ""
        MAX_CONTINUATIONS = 10
        continuations = 0

        while continuations < MAX_CONTINUATIONS:
            with self.client.messages.stream(
                model=self.model,
                max_tokens=STREAM_MAX_TOKENS,
                system=self.system_prompt,
                thinking={"type": "adaptive"},
                tools=self.tools if self.tools else None,
                messages=messages,
            ) as stream:
                current_text: list[str] = []

                for event in stream:
                    if (
                        event.type == "content_block_delta"
                        and event.delta.type == "text_delta"
                    ):
                        token = event.delta.text
                        current_text.append(token)
                        full_response += token
                        if stream_callback:
                            stream_callback(token)

                response = stream.get_final_message()

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "pause_turn":
                # Server-side tool loop hit iteration limit — re-send to continue
                continuations += 1
                messages.append({"role": "assistant", "content": response.content})
                continue

            if response.stop_reason == "tool_use":
                # Custom Python tool call — execute locally and return results
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use" and block.name not in SERVER_SIDE_TOOLS:
                        result = self._execute_custom_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                messages.append({"role": "user", "content": tool_results})
                full_response = ""
                continue

            break

        # Publish findings to bus so other agents can build on them
        self._publish_result(full_response)

        return full_response


# ── OpenAI-compatible agent (GPT-4o mini / Gemini Flash / Qwen-Plus) ──────────

class OpenAICompatibleAgent(BaseFinancialAgent):
    """
    Specialist agent backed by any OpenAI-compatible API endpoint.
    Used for: Debt Agent (GPT-4o mini), Behaviour Agent (Gemini Flash),
              Wealth Agent (Qwen-Plus via DashScope).

    Converts Anthropic tool schema format → OpenAI function-calling format.
    Web search/fetch tools are skipped (Anthropic server-side only).
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        tools: list[dict],
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
    ):
        super().__init__(name=name, system_prompt=system_prompt, tools=tools, model=model)
        self.is_gemini = "gemini" in model.lower()
        if self.is_gemini:
            genai.configure(api_key=api_key)
            self.genai_tools = self._to_gemini_tools()
            self.genai_model = genai.GenerativeModel(model, tools=self.genai_tools)
        else:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key, base_url=base_url)

    # ── Tool format conversion ─────────────────────────────────────────────────

    def _to_openai_tools(self) -> list[dict]:
        """Convert Anthropic input_schema format → OpenAI function-calling format."""
        result = []
        for t in (self.tools or []):
            if t["name"] in SERVER_SIDE_TOOLS:
                continue  # web_search/web_fetch are Anthropic-only
            result.append({
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
                },
            })
        return result

    def _to_gemini_tools(self) -> list[dict]:
        """Convert Anthropic input_schema format → Gemini function-calling format."""
        result = []
        for t in (self.tools or []):
            if t["name"] in SERVER_SIDE_TOOLS:
                continue
            result.append({
                "function_declarations": [{
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
                }]
            })
    def _convert_to_gemini_history(self, messages):
        history = []
        for msg in messages:
            if msg["role"] == "system":
                continue
            elif msg["role"] == "user":
                history.append({"role": "user", "parts": [{"text": msg["content"]}]} )
            elif msg["role"] == "assistant":
                parts = []
                if "content" in msg and msg["content"]:
                    parts.append({"text": msg["content"]})
                if "tool_calls" in msg:
                    for tc in msg["tool_calls"]:
                        parts.append({"function_call": {"name": tc["function"]["name"], "args": json.loads(tc["function"]["arguments"])}})
                history.append({"role": "model", "parts": parts})
            elif msg["role"] == "tool":
                fr = {"name": "function_name", "response": msg["content"]}
                history.append({"role": "user", "parts": [{"function_response": fr}]})
        return history

    def run(self, user_message: str, stream_callback=None) -> str:
        enriched_message = self._inject_peer_context(user_message)
        if self.is_gemini:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": enriched_message},
            ]
            history = self._convert_to_gemini_history(messages)
            chat = self.genai_model.start_chat(history=history)
            response = chat.send_message(enriched_message, stream=True)
            full_response = ""
            function_calls = []
            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    if stream_callback:
                        stream_callback(chunk.text)
                if hasattr(chunk, 'function_call') and chunk.function_call:
                    function_calls.append(chunk.function_call)
            if function_calls:
                for fc in function_calls:
                    result = self._execute_custom_tool(fc.name, fc.args)
                    chat.send_message(genai.protos.Content(
                        parts=[genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fc.name,
                                response=result
                            )
                        )]
                    ))
                final_response = chat.send_message("", stream=True)
                for chunk in final_response:
                    if chunk.text:
                        full_response += chunk.text
                        if stream_callback:
                            stream_callback(chunk.text)
            self._publish_result(full_response)
            return full_response
        else:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user",   "content": enriched_message},
            ]
            full_response = ""
        openai_tools = self._to_openai_tools()
        MAX_ITERATIONS = 10

        for _ in range(MAX_ITERATIONS):
            create_kwargs: dict = {
                "model":      self.model,
                "max_tokens": 8192,
                "messages":   messages,
                "stream":     True,
            }
            if openai_tools:
                create_kwargs["tools"] = openai_tools

            stream = self.client.chat.completions.create(**create_kwargs)

            # Accumulate streamed content and tool call chunks
            content = ""
            tool_calls_acc: list[dict] = []
            finish_reason = None

            for chunk in stream:
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                finish_reason = choice.finish_reason or finish_reason
                delta = choice.delta

                if delta.content:
                    content += delta.content
                    full_response += delta.content
                    if stream_callback:
                        stream_callback(delta.content)

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        # Extend accumulator list as new tool call indices arrive
                        idx = tc.index or 0
                        while idx >= len(tool_calls_acc):
                            tool_calls_acc.append({"id": "", "name": "", "arguments": ""})
                        if tc.id:
                            tool_calls_acc[idx]["id"] += tc.id
                        if tc.function and tc.function.name:
                            tool_calls_acc[idx]["name"] += tc.function.name
                        if tc.function and tc.function.arguments:
                            tool_calls_acc[idx]["arguments"] += tc.function.arguments

            if not tool_calls_acc:
                break

            # Ensure every tool call has a non-empty ID (Gemini sometimes omits it)
            for i, tc in enumerate(tool_calls_acc):
                if not tc["id"]:
                    tc["id"] = f"call_{tc['name']}_{i}"

            if tool_calls_acc:
                # Append assistant turn with tool_calls
                # Omit content when empty — Gemini rejects content="" alongside tool_calls
                assistant_msg: dict = {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {"name": tc["name"], "arguments": tc["arguments"], "thought_signature": "signature"},
                        }
                        for tc in tool_calls_acc
                    ],
                }
                if content:
                    assistant_msg["content"] = content
                messages.append(assistant_msg)

                # Execute each tool and collect results
                for tc in tool_calls_acc:
                    try:
                        inputs = json.loads(tc["arguments"])
                    except Exception:
                        inputs = {}
                    result = self._execute_custom_tool(tc["name"], inputs)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })

                full_response = ""
                continue

            break

        self._publish_result(full_response)
        return full_response
