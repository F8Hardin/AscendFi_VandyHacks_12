"""
Supervisor Agent — The Chief Financial Intelligence Officer.
50 years of finance experience. Orchestrates all specialized agents.

Key behaviours
──────────────
1. MANDATORY DELEGATION  — tool_choice="any" on every first API call forces
   ARIA to always consult at least one specialist agent before replying.
   The supervisor never answers financial questions directly.

2. PERSISTENT MEMORY — ConversationMemory loads prior conversations from
   ~/.financeai/history.json so ARIA remembers past sessions automatically.
"""

import json
from openai import OpenAI
from config import GEMINI_API_KEY, GEMINI_BASE_URL, SUPERVISOR_MODEL

from agents.risk_agent import create_risk_agent
from agents.debt_agent import create_debt_agent
from agents.behaviour_agent import create_behaviour_agent
from agents.investment_agent import create_investment_agent
from agents.wealth_agent import create_wealth_agent
from agents.research_agent import create_research_agent
from agents.agent_bus import bus
from memory.conversation_store import ConversationMemory
from tools.dashboard_generator import (
    DASHBOARD_TOOL_DEFINITIONS,
    execute_dashboard_tool,
    DASHBOARD_TOOL_FUNCTIONS,
)


SUPERVISOR_SYSTEM_PROMPT = """You are ARIA — Advanced Risk and Investment Advisor — a Chief Financial
Intelligence Officer with 50 years of experience across Wall Street, retail banking, wealth
management, and personal finance coaching.

You have seen every financial situation imaginable: dot-com crashes, housing crises, runaway inflation,
zero-interest-rate environments, and every kind of personal financial struggle. You speak plainly,
think deeply, and always prioritise your client's long-term financial wellbeing.

Your team of specialist agents:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 RESEARCH AGENT   — Live internet search: stock prices, news, rates, current events
🔴 RISK AGENT       — Credit score, overdraft risk, missing payment prediction
🟠 DEBT AGENT       — Debt payoff plans, consolidation analysis, freedom timeline
🟡 BEHAVIOUR AGENT  — Spending patterns, habit analysis, behavioural insights
🟢 INVESTMENT AGENT — Portfolio allocation, compound growth simulations, retirement
🔵 WEALTH AGENT     — Paycheck splitting, net worth tracking, wealth building roadmap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  MANDATORY DELEGATION RULE — THIS IS NON-NEGOTIABLE:
You MUST call at least one specialist agent tool for EVERY user message — no exceptions.
You are a PURE ORCHESTRATOR. You do not provide financial analysis directly.

Your workflow for EVERY message:
  Step 1 → Identify which agent(s) should handle this question
  Step 2 → Call them with the full relevant context from the user
  Step 3 → Receive their expert analysis
  Step 4 → Synthesise findings into one coherent, integrated recommendation
  Step 5 → Add your 50-year perspective and numbered next steps

ROUTING GUIDELINES:
- Current prices/rates/news → Research Agent FIRST, then the relevant specialist
- Stock/ETF/market prices   → Research Agent (always) + Investment Agent
- Interest rates / Fed news → Research Agent (always) + Debt or Wealth Agent
- Risk questions            → Risk Agent       (credit, overdraft, missing bills)
- Debt questions            → Debt Agent       (payoff, consolidation, credit cards, loans)
- Spending/habits           → Behaviour Agent  (patterns, triggers, habits, transactions)
- Investing/growth          → Investment Agent (stocks, retirement, simulations, portfolio)
- Income/budgeting          → Wealth Agent     (paycheck split, net worth, budgeting)
- Complex situations        → Multiple agents in logical sequence
- When in doubt             → Call the most relevant agent AND ask follow-up questions

CONTINUITY — REMEMBERING PAST CONVERSATIONS:
- Reference prior conversations naturally: "Last time we discussed your credit score of 648..."
- Track progress toward goals: "You mentioned wanting to pay off your Visa by December — you're on track."
- Notice changes: "Your overdraft risk has improved since we last spoke."
- Use the KNOWN USER PROFILE section below (if present) to personalise every response.

TONE:
- Speak as a trusted, experienced advisor — not a chatbot
- Be direct about risks but compassionate about struggles
- Celebrate wins genuinely
- When you don't have enough information, ask for what you need
- Always end with clear next steps numbered 1, 2, 3

Remember: the best financial advice combines rigorous analysis with human understanding.
Numbers matter, but so does the person behind them.
"""

# Comprehensive financial plan dashboard — supervisor-level tool (synthesises all agent data)
_PLAN_DASHBOARD_TOOL = next(
    t for t in DASHBOARD_TOOL_DEFINITIONS if t["name"] == "generate_financial_plan_dashboard"
)

# Tools the supervisor uses to call specialized agents
SUPERVISOR_TOOLS = [
    {
        "name": "call_research_agent",
        "description": (
            "Delegate to the Research Agent for: live stock prices, ETF prices, current interest rates, "
            "Fed policy updates, recent market news, company earnings, economic indicators, "
            "or any data that requires up-to-date information from the internet. "
            "Call this FIRST whenever the user asks about current prices, rates, or news. "
            "Its findings are shared with all other agents automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Specific research request, e.g. 'Find current AAPL and MSFT stock prices and today\\'s S&P 500 level'",
                },
            },
            "required": ["message"],
        },
    },
    {
        "name": "call_risk_agent",
        "description": "Delegate to the Risk Agent for: overdraft probability, credit score predictions, missing payment risk assessment. Provide all relevant financial data in the message.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Detailed financial question or data to send to the Risk Agent"},
            },
            "required": ["message"],
        },
    },
    {
        "name": "call_debt_agent",
        "description": "Delegate to the Debt Agent for: debt payoff strategies, avalanche/snowball plans, consolidation analysis, getting out of debt. Provide all debt details.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Detailed debt information and question for the Debt Agent"},
            },
            "required": ["message"],
        },
    },
    {
        "name": "call_behaviour_agent",
        "description": "Delegate to the Behaviour Agent for: spending habit analysis, identifying patterns and triggers, behavioural coaching, transaction analysis.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Spending data or behavioural question for the Behaviour Agent"},
            },
            "required": ["message"],
        },
    },
    {
        "name": "call_investment_agent",
        "description": "Delegate to the Investment Agent for: investment simulations, portfolio allocation, compound growth projections, retirement planning, comparing investment scenarios.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Investment question or financial data for the Investment Agent"},
            },
            "required": ["message"],
        },
    },
    {
        "name": "call_wealth_agent",
        "description": "Delegate to the Wealth Agent for: paycheck splitting strategy, net worth calculation, budgeting frameworks, wealth building roadmaps.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Income/wealth question or financial data for the Wealth Agent"},
            },
            "required": ["message"],
        },
    },
    _PLAN_DASHBOARD_TOOL,
]


class SupervisorAgent:
    def __init__(self):
        self.client = OpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL)
        self.agents = {
            "call_research_agent":   create_research_agent(),
            "call_risk_agent":       create_risk_agent(),
            "call_debt_agent":       create_debt_agent(),
            "call_behaviour_agent":  create_behaviour_agent(),
            "call_investment_agent": create_investment_agent(),
            "call_wealth_agent":     create_wealth_agent(),
        }

        # Load persistent memory — restores prior conversation history from disk
        self.memory = ConversationMemory()
        self.conversation_history: list[dict] = self.memory.get_context_messages()

        # Convert SUPERVISOR_TOOLS from Anthropic input_schema format → OpenAI function format
        self.openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
                },
            }
            for t in SUPERVISOR_TOOLS
        ]

    # ── System prompt ────────────────────────────────────────────────────────

    def _build_system_prompt(self) -> str:
        """
        Build the full system prompt, appending the user profile block
        from persistent memory if one exists.
        """
        prompt = SUPERVISOR_SYSTEM_PROMPT
        profile_block = self.memory.get_profile_block()
        if profile_block:
            prompt += f"\n\n{profile_block}"
        return prompt

    # ── Agent calling ────────────────────────────────────────────────────────

    def _call_agent(self, tool_name: str, message: str, stream_callback=None) -> str:
        agent = self.agents.get(tool_name)
        if not agent:
            return f"Error: unknown agent '{tool_name}'"

        agent_name = agent.name
        if stream_callback:
            stream_callback(f"\n\n  ┌─ [{agent_name}] ──────────────────────\n  │ ")

        buffer = []

        def agent_stream(token: str):
            buffer.append(token)
            if stream_callback:
                indented = token.replace("\n", "\n  │ ")
                stream_callback(indented)

        result = agent.run(message, stream_callback=agent_stream)

        if stream_callback:
            stream_callback(f"\n  └────────────────────────────────────\n")

        return result

    # ── Main chat loop ───────────────────────────────────────────────────────

    def chat(self, user_message: str, stream_callback=None) -> str:
        """
        Process a user message through the supervisor (Gemini) and its specialist team.

        Enforces mandatory delegation: tool_choice="required" on the first API call
        guarantees ARIA calls at least one specialist agent before replying.

        Persists every exchange to ~/.financeai/history.json for continuity
        across sessions.
        """
        self.conversation_history.append({"role": "user", "content": user_message})

        # Build messages: system prompt first, then conversation history
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages += list(self.conversation_history)

        full_response_parts = []
        first_api_call = True

        while True:
            # Mandatory delegation: "required" forces at least one tool call on first turn
            tool_choice = "required" if first_api_call else "auto"
            first_api_call = False

            # ── Non-streaming call ──────────────────────────────────────────
            # Gemini thinking models embed a `thought_signature` in every
            # function call.  The signature must be echoed back verbatim on
            # the next turn or Gemini returns 400 INVALID_ARGUMENT.
            # Using stream=False gives us the full message object so we can
            # round-trip the signature via model_dump().
            response = self.client.chat.completions.create(
                model=SUPERVISOR_MODEL,
                max_tokens=8192,
                tools=self.openai_tools,
                tool_choice=tool_choice,
                messages=messages,
                stream=False,
            )

            msg = response.choices[0].message
            current_content = msg.content or ""

            # Stream the text content character-by-character for UX
            if current_content and stream_callback:
                stream_callback(current_content)

            raw_tool_calls = msg.tool_calls or []

            if current_content:
                full_response_parts.append(current_content)

            # No tool calls — final response
            if not raw_tool_calls:
                break

            # Build the assistant message using model_dump() so that Gemini's
            # thought_signature (stored in model_extra by the OpenAI SDK) is
            # preserved verbatim in the request we send back.
            assistant_msg = msg.model_dump(exclude_none=True)
            assistant_msg["role"] = "assistant"

            # Ensure every tool call has a non-empty ID
            for i, tc in enumerate(raw_tool_calls):
                if not tc.id:
                    # Patch both the list object and the dict we'll send
                    fallback_id = f"call_{tc.function.name}_{i}"
                    assistant_msg["tool_calls"][i]["id"] = fallback_id

            # tool_calls_acc — reuse downstream execution logic unchanged
            tool_calls_acc = [
                {
                    "id": assistant_msg["tool_calls"][i]["id"],
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for i, tc in enumerate(raw_tool_calls)
            ]

            messages.append(assistant_msg)

            # Execute each tool call and collect results
            for tc in tool_calls_acc:
                try:
                    inputs = json.loads(tc["arguments"])
                except Exception:
                    inputs = {}

                if tc["name"] in DASHBOARD_TOOL_FUNCTIONS:
                    if stream_callback:
                        stream_callback(f"\n\n📊 Generating dashboard...")
                    result = execute_dashboard_tool(tc["name"], inputs)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": json.dumps(result) if isinstance(result, dict) else str(result),
                    })
                    continue

                agent_name = (
                    self.agents[tc["name"]].name
                    if tc["name"] in self.agents
                    else tc["name"]
                )
                if stream_callback:
                    stream_callback(f"\n\n🔄 Consulting {agent_name}...")

                agent_result = self._call_agent(
                    tc["name"],
                    inputs.get("message", ""),
                    stream_callback=stream_callback,
                )
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": agent_result,
                })

            if stream_callback:
                stream_callback("\n\n")

        final_response = "\n".join(full_response_parts).strip()

        # Store the clean exchange in in-memory history
        self.conversation_history.append({
            "role": "assistant",
            "content": final_response,
        })

        # Persist both turns to disk for cross-session continuity
        self.memory.add_message("user", user_message)
        self.memory.add_message("assistant", final_response)

        return final_response

    # ── Session management ───────────────────────────────────────────────────

    def reset_conversation(self):
        """Clear in-session history, agent bus, and persistent memory."""
        self.conversation_history = []
        self.memory.clear()
        bus.reset()

    def get_agent_insights(self) -> dict:
        """
        Return the latest published context from all specialist agents.
        Useful for the Supervisor to synthesise cross-agent findings.
        """
        return bus.get_all_agent_contexts()

    @property
    def memory_summary(self) -> str:
        """One-line description of persistent memory state."""
        return self.memory.get_summary_line()
