"""
FastMCP server exposing the 6 AscendFi financial analysis tools.
Runs as a subprocess (stdio transport) spawned by the LangChain agent at startup.
"""

import os
import httpx
from fastmcp import FastMCP

mcp = FastMCP("AscendFi Financial Tools")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@mcp.tool()
async def predict_missing_payments(context_json: str) -> str:
    """Predict the risk of missing upcoming bill payments for this user.
    Input must be a JSON string of the user's FinancialContext."""
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(
            f"{BACKEND_URL}/api/predict/missing-payments",
            content=context_json,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
    return r.text


@mcp.tool()
async def predict_overdraft(context_json: str) -> str:
    """Estimate the probability of a checking account overdraft in the next 30 days.
    Input must be a JSON string of the user's FinancialContext."""
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(
            f"{BACKEND_URL}/api/predict/overdraft",
            content=context_json,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
    return r.text


@mcp.tool()
async def predict_credit_score(context_json: str) -> str:
    """Forecast significant credit score shifts over the next 3-6 months.
    Input must be a JSON string of the user's FinancialContext."""
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(
            f"{BACKEND_URL}/api/predict/credit-score",
            content=context_json,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
    return r.text


@mcp.tool()
async def optimize_debt(context_json: str) -> str:
    """Generate the optimal debt payoff plan using avalanche, snowball, or hybrid strategy.
    Input must be a JSON string of the user's FinancialContext."""
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(
            f"{BACKEND_URL}/api/debt/optimize",
            content=context_json,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
    return r.text


@mcp.tool()
async def analyze_spending(context_json: str) -> str:
    """Analyze the user's spending habits, anomalies, and life-event-driven patterns.
    Input must be a JSON string of the user's FinancialContext."""
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(
            f"{BACKEND_URL}/api/spending/analyze",
            content=context_json,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
    return r.text


@mcp.tool()
async def autonomous_plan(context_json: str) -> str:
    """Create an autonomous monthly finance plan: paycheck split, investments, emergency fund.
    Input must be a JSON string of the user's FinancialContext."""
    async with httpx.AsyncClient(timeout=30.0) as c:
        r = await c.post(
            f"{BACKEND_URL}/api/finance/autonomous-plan",
            content=context_json,
            headers={"Content-Type": "application/json"},
        )
        r.raise_for_status()
    return r.text


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
