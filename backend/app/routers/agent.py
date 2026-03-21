import os
from fastapi import APIRouter
from app.agents.claude_agent import ClaudeAgent
from app.agents.lm_studio_agent import LMStudioAgent
from app.agents.base import FinancialAgentBase
from app.models.financial import FinancialContext

router = APIRouter()

_agent: FinancialAgentBase | None = None


def _get_agent() -> FinancialAgentBase:
    global _agent
    if _agent is None:
        name = os.getenv("ACTIVE_AGENT", "claude")
        _agent = LMStudioAgent() if name == "lm_studio" else ClaudeAgent()
    return _agent


# ── Predictive risk ───────────────────────────────────────────────────────

@router.post("/predict/missing-payments")
async def predict_missing_payments(context: FinancialContext):
    return await _get_agent().predict_missing_payments(context)


@router.post("/predict/overdraft")
async def predict_overdraft(context: FinancialContext):
    return await _get_agent().overdraft_probability(context)


@router.post("/predict/credit-score")
async def predict_credit_score(context: FinancialContext):
    return await _get_agent().credit_score_shifts(context)


# ── Debt optimization ─────────────────────────────────────────────────────

@router.post("/debt/optimize")
async def optimize_debt(context: FinancialContext):
    return await _get_agent().optimize_debt(context)


# ── Behavioral spending ───────────────────────────────────────────────────

@router.post("/spending/analyze")
async def analyze_spending(context: FinancialContext):
    return await _get_agent().analyze_spending(context)


# ── Autonomous finance ────────────────────────────────────────────────────

@router.post("/finance/autonomous-plan")
async def autonomous_plan(context: FinancialContext):
    return await _get_agent().autonomous_plan(context)
