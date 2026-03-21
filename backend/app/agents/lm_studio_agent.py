"""
LMStudioAgent — FinancialAgentBase implementation backed by a local LM Studio server.

LM Studio exposes an OpenAI-compatible API at http://localhost:1234/v1 by default.
Start the local server in LM Studio before using this agent.

Env vars:
  LM_STUDIO_BASE_URL  — default: http://localhost:1234/v1
  LM_STUDIO_MODEL     — default: local-model (LM Studio accepts any string here)
"""

import os
import json
from typing import AsyncIterator

from openai import OpenAI

from app.agents.base import FinancialAgentBase
from app.models.chat import Message
from app.models.financial import (
    FinancialContext,
    PredictionResult,
    DebtPlan,
    SpendingAnalysis,
    AutonomousPlan,
)

SYSTEM_PROMPT = """You are AscendFi, a compassionate and expert AI financial recovery advisor.
You help users predict financial risks, optimize debt payoff, understand spending behavior,
and build autonomous finance plans. Always be empathetic, practical, and non-judgmental.
When returning structured data, respond ONLY with valid JSON matching the requested schema."""


def _client() -> OpenAI:
    return OpenAI(
        base_url=os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1"),
        api_key="lm-studio",  # LM Studio doesn't validate the key, but the field is required
    )


def _model() -> str:
    return os.getenv("LM_STUDIO_MODEL", "local-model")


def _context_summary(ctx: FinancialContext) -> str:
    return f"""Financial snapshot:
- Monthly income: ${ctx.monthly_income:,.2f}
- Checking balance: ${ctx.checking_balance:,.2f}
- Savings: ${ctx.savings_balance:,.2f}
- Credit score: {ctx.credit_score or 'unknown'}
- Bills: {len(ctx.bills)} upcoming
- Debts: {len(ctx.debts)} accounts (total ${sum(d.balance for d in ctx.debts):,.2f})
- Life events: {[e.value for e in ctx.life_events] or 'none'}"""


def _structured_call(prompt: str) -> dict:
    """Single-shot call expecting JSON back."""
    response = _client().chat.completions.create(
        model=_model(),
        messages=[
            {"role": "user", "content": f"{SYSTEM_PROMPT}\n\n---\n{prompt}"},
        ],
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


class LMStudioAgent(FinancialAgentBase):

    async def predict_missing_payments(
        self, context: FinancialContext
    ) -> PredictionResult:
        prompt = f"""{_context_summary(context)}

Analyze whether the user is at risk of missing upcoming bill payments.
Respond with JSON matching this schema:
{{
  "risk_level": "low|moderate|high|critical",
  "probability": <0.0-1.0>,
  "summary": "<one sentence>",
  "contributing_factors": ["<factor>", ...],
  "recommendations": ["<action>", ...]
}}"""
        data = _structured_call(prompt)
        return PredictionResult(**data)

    async def overdraft_probability(
        self, context: FinancialContext
    ) -> PredictionResult:
        bills_total = sum(b.amount for b in context.bills)
        prompt = f"""{_context_summary(context)}
Upcoming bills total: ${bills_total:,.2f}

Estimate the probability of a checking account overdraft in the next 30 days.
Respond with JSON matching this schema:
{{
  "risk_level": "low|moderate|high|critical",
  "probability": <0.0-1.0>,
  "summary": "<one sentence>",
  "contributing_factors": ["<factor>", ...],
  "recommendations": ["<action>", ...]
}}"""
        data = _structured_call(prompt)
        return PredictionResult(**data)

    async def credit_score_shifts(
        self, context: FinancialContext
    ) -> PredictionResult:
        prompt = f"""{_context_summary(context)}

Predict significant credit score changes (positive or negative) over the next 3-6 months.
Respond with JSON matching this schema:
{{
  "risk_level": "low|moderate|high|critical",
  "probability": <0.0-1.0>,
  "summary": "<one sentence>",
  "contributing_factors": ["<factor>", ...],
  "recommendations": ["<action>", ...]
}}"""
        data = _structured_call(prompt)
        return PredictionResult(**data)

    async def optimize_debt(self, context: FinancialContext) -> DebtPlan:
        debts_desc = "\n".join(
            f"- {d.name}: ${d.balance:,.2f} @ {d.interest_rate}% APR, min ${d.minimum_payment}/mo ({d.type})"
            for d in context.debts
        )
        prompt = f"""{_context_summary(context)}

Debts:
{debts_desc or "None"}

Create the optimal debt payoff plan. Consider avalanche (highest interest first),
snowball (smallest balance first), and hybrid approaches.
Respond with JSON matching this schema:
{{
  "strategy": "<strategy name>",
  "steps": [{{"month": 1, "action": "<description>", "target_debt": "<name>", "extra_payment": <amount>}}, ...],
  "estimated_payoff_months": <int>,
  "total_interest_saved": <float>,
  "summary": "<2-3 sentences>"
}}"""
        data = _structured_call(prompt)
        return DebtPlan(**data)

    async def analyze_spending(self, context: FinancialContext) -> SpendingAnalysis:
        spending_desc = "\n".join(
            f"- {e.date}: ${e.amount:.2f} [{e.category}] {e.description or ''}"
            for e in context.spending_history[-30:]
        ) or "No spending history provided."

        prompt = f"""{_context_summary(context)}

Recent spending:
{spending_desc}

Analyze spending habits, identify anomalies, and note any life-event-driven patterns.
Respond with JSON matching this schema:
{{
  "top_categories": [{{"category": "<name>", "total": <float>, "pct_of_income": <float>}}, ...],
  "anomalies": ["<description>", ...],
  "life_event_impact": "<description or null>",
  "trend": "<improving|stable|worsening>",
  "recommendations": ["<action>", ...]
}}"""
        data = _structured_call(prompt)
        return SpendingAnalysis(**data)

    async def autonomous_plan(self, context: FinancialContext) -> AutonomousPlan:
        prompt = f"""{_context_summary(context)}

Create an autonomous finance plan for this user's monthly paycheck.
Include emergency fund building, debt paydown, and investment allocation.
Respond with JSON matching this schema:
{{
  "paycheck_split": {{"needs": <float>, "debt_payoff": <float>, "emergency_fund": <float>, "investments": <float>, "discretionary": <float>}},
  "investment_suggestions": [{{"type": "<e.g. index fund, Roth IRA>", "amount": <float>, "rationale": "<reason>"}}],
  "emergency_fund_target": <float>,
  "summary": "<2-3 sentences>"
}}"""
        data = _structured_call(prompt)
        return AutonomousPlan(**data)

    async def chat_stream(
        self, messages: list[Message], context: FinancialContext | None
    ) -> AsyncIterator[str]:
        system = SYSTEM_PROMPT
        if context:
            system += f"\n\nUser's current financial context:\n{_context_summary(context)}"

        # Many local model Jinja templates only support user/assistant roles
        # and require the conversation to start with a user message.
        # Fold the system prompt into the first user message to be safe.
        user_messages = [m for m in messages if m.role in ("user", "assistant")]
        # drop leading assistant turns
        while user_messages and user_messages[0].role != "user":
            user_messages = user_messages[1:]

        if not user_messages:
            return

        api_messages = [
            {"role": m.role, "content": m.content} for m in user_messages
        ]
        # Prepend system context to the first user message
        api_messages[0]["content"] = f"{system}\n\n---\n{api_messages[0]['content']}"

        stream = _client().chat.completions.create(
            model=_model(),
            messages=api_messages,
            stream=True,
            temperature=0.7,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
