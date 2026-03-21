"""
LangChain ReAct agent backed by Claude, with tools loaded from the FastMCP server.
Call init_agent() once at startup, then use get_executor() per request.
"""

import os
import sys
from typing import Optional

from langchain_anthropic import ChatAnthropic
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp import StdioServerParameters

from app.models import FinancialContext

SYSTEM_PROMPT = (
    "You are AscendFi, a compassionate and expert AI financial recovery advisor. "
    "You help users predict financial risks, optimize debt payoff, understand spending behavior, "
    "and build autonomous finance plans. Always be empathetic, practical, and non-judgmental. "
    "When you need financial data or calculations, use the available tools — pass the user's "
    "financial context as a JSON string. Only call tools when the user's question requires it."
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


_executor: Optional[AgentExecutor] = None
_mcp_client: Optional[MultiServerMCPClient] = None


async def init_agent() -> None:
    global _executor, _mcp_client

    _mcp_client = MultiServerMCPClient(
        {
            "finance": StdioServerParameters(
                command=sys.executable,
                args=["app/mcp_server.py"],
                env={
                    **os.environ,
                    "BACKEND_URL": os.getenv("BACKEND_URL", "http://localhost:8000"),
                    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY", ""),
                },
            )
        }
    )
    await _mcp_client.__aenter__()
    tools = _mcp_client.get_tools()

    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        streaming=True,
    )

    # Pull the standard ReAct prompt from LangChain hub and prepend our system message
    base_prompt = hub.pull("hwchase17/react")
    from langchain_core.prompts import PromptTemplate
    react_template = base_prompt.template
    full_template = SYSTEM_PROMPT + "\n\n" + react_template
    prompt = PromptTemplate.from_template(full_template)

    agent = create_react_agent(llm, tools, prompt)
    _executor = AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        max_iterations=6,
        verbose=True,
    )


def get_executor() -> AgentExecutor:
    if _executor is None:
        raise RuntimeError("Agent not initialized — call init_agent() at startup")
    return _executor
