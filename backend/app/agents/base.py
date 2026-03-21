"""
FinancialAgentBase — the interface every agent must implement.

To plug in a new agent:
1. Subclass FinancialAgentBase
2. Implement all abstract methods
3. Register it in app/agents/registry.py
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator

from app.models.financial import (
    FinancialContext,
    PredictionResult,
    DebtPlan,
    SpendingAnalysis,
    AutonomousPlan,
)
from app.models.chat import Message


class FinancialAgentBase(ABC):
    """Abstract base class for all financial AI agents."""

    # ── Predictive Risk ────────────────────────────────────────────────────

    @abstractmethod
    async def predict_missing_payments(
        self, context: FinancialContext
    ) -> PredictionResult:
        """Predict probability and risk of missing upcoming bill payments."""
        ...

    @abstractmethod
    async def overdraft_probability(
        self, context: FinancialContext
    ) -> PredictionResult:
        """Estimate likelihood of checking account overdraft in next 30 days."""
        ...

    @abstractmethod
    async def credit_score_shifts(
        self, context: FinancialContext
    ) -> PredictionResult:
        """Forecast significant credit score changes based on current trajectory."""
        ...

    # ── Debt Optimization ─────────────────────────────────────────────────

    @abstractmethod
    async def optimize_debt(self, context: FinancialContext) -> DebtPlan:
        """Return the optimal debt payoff plan given income and debt profile."""
        ...

    # ── Behavioral Analysis ───────────────────────────────────────────────

    @abstractmethod
    async def analyze_spending(self, context: FinancialContext) -> SpendingAnalysis:
        """Identify spending habits, anomalies, and life-event-driven shifts."""
        ...

    # ── Autonomous Finance ────────────────────────────────────────────────

    @abstractmethod
    async def autonomous_plan(self, context: FinancialContext) -> AutonomousPlan:
        """Generate paycheck allocation and investment recommendations."""
        ...

    # ── Conversational Chat (streamed) ────────────────────────────────────

    @abstractmethod
    async def chat_stream(
        self, messages: list[Message], context: FinancialContext | None
    ) -> AsyncIterator[str]:
        """Stream a conversational response grounded in financial context."""
        ...
