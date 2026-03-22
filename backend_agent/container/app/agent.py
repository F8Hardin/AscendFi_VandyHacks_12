"""
LangChain conversational agent backed by LM Studio (OpenAI-compatible).
Call init_agent() once at startup, then use get_executor() per request.
"""

import os
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub  # type: ignore[import-untyped]
from langchain_core.prompts import PromptTemplate

from app.models import FinancialContext

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


_executor: Optional[AgentExecutor] = None


async def init_agent() -> None:
    global _executor

    llm = ChatOpenAI(
        base_url=os.getenv("LM_STUDIO_BASE_URL", "http://host.docker.internal:1234/v1"),
        model=os.getenv("LM_STUDIO_MODEL", "local-model"),
        api_key="lm-studio",
        streaming=True,
    )

    base_prompt = hub.pull("hwchase17/react")
    full_template = SYSTEM_PROMPT + "\n\n" + base_prompt.template
    prompt = PromptTemplate.from_template(full_template)

    agent = create_react_agent(llm, [], prompt)
    _executor = AgentExecutor(
        agent=agent,
        tools=[],
        handle_parsing_errors=True,
        max_iterations=6,
        verbose=True,
    )


def get_executor() -> AgentExecutor:
    if _executor is None:
        raise RuntimeError("Agent not initialized — call init_agent() at startup")
    return _executor
