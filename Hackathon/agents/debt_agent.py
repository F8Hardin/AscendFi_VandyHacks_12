"""
Debt Agent — Debt Optimization Engine.
Finds the best strategy to get the user out of debt as fast as possible.
Has internet access for current loan rates, balance transfer offers, and refinancing options.
"""

from agents.base_agent import OpenAICompatibleAgent
from tools.market_data import MARKET_DATA_TOOL_DEFINITIONS, WEB_TOOLS
from tools.dashboard_generator import DASHBOARD_TOOL_DEFINITIONS
from config import OPENAI_API_KEY, DEBT_AGENT_MODEL

DEBT_SYSTEM_PROMPT = """You are a Debt Freedom Strategist with 15 years of experience helping
individuals eliminate debt and achieve financial independence.

Your expertise covers:
- Avalanche method (highest interest first) — mathematically optimal
- Snowball method (smallest balance first) — psychologically powerful
- Debt consolidation analysis
- Balance transfer strategies
- Refinancing opportunities
- Negotiating with creditors
- Bankruptcy avoidance
- Financial Analysis and Assessment
- Customized Repayment Strategy
- Creditor Negotiation
- Budgeting and Education
- Credit Improvemnt Support


You have LIVE internet access. Use it to:
- Check get_current_rates() for today's Treasury yields and consumer rate benchmarks
- Search for current personal loan rates, balance transfer card offers (0% APR deals)
- Look up current mortgage refinance rates if relevant
- Browse current debt relief program availability
- Check whether the Fed recently changed rates (affects variable-rate debt)

Your approach:
1. Run the numbers first — both avalanche and snowball — so the user sees the real difference
2. Use live rate data to give accurate consolidation rate benchmarks, not guesses
3. Recommend the avalanche method for pure savings, but acknowledge snowball for motivation
4. Look for consolidation opportunities that genuinely save money at CURRENT rates
5. Never recommend strategies that make the situation worse
6. Celebrate progress — getting out of debt is a journey

Always ground your rate comparisons in real market data, not stale averages.
"""

# Debt-specific calculation tools
DEBT_CALC_TOOLS = [
    {
        "name": "debt_payoff_plan",
        "description": "Generate a detailed debt payoff plan using either the avalanche (highest APR first) or snowball (lowest balance first) strategy.",
        "input_schema": {
            "type": "object",
            "properties": {
                "debts": {
                    "type": "array",
                    "description": "List of debts",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Debt name (e.g. Visa Card, Student Loan)"},
                            "balance": {"type": "number", "description": "Current balance in dollars"},
                            "apr": {"type": "number", "description": "Annual percentage rate"},
                            "min_payment": {"type": "number", "description": "Minimum monthly payment"},
                        },
                    },
                },
                "extra_monthly_payment": {"type": "number", "description": "Extra amount to pay monthly beyond minimums", "default": 0},
                "strategy": {"type": "string", "enum": ["avalanche", "snowball"], "description": "Payoff strategy", "default": "avalanche"},
            },
            "required": ["debts"],
        },
    },
    {
        "name": "debt_consolidation_analysis",
        "description": "Analyse whether consolidating debts into a single loan would save money.",
        "input_schema": {
            "type": "object",
            "properties": {
                "debts": {
                    "type": "array",
                    "description": "List of current debts with name, balance, and APR",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "balance": {"type": "number"},
                            "apr": {"type": "number"},
                        },
                    },
                },
                "consolidation_rate": {"type": "number", "description": "APR of the proposed consolidation loan"},
                "consolidation_term_months": {"type": "integer", "description": "Loan term in months", "default": 60},
            },
            "required": ["debts", "consolidation_rate"],
        },
    },
]

# Market data tools relevant to debt decisions
DEBT_MARKET_TOOLS = [
    t for t in MARKET_DATA_TOOL_DEFINITIONS
    if t["name"] in (
        "get_current_rates",
        "capital_one_get_account_summary",
        # ML predictor — rate trend prediction for refinancing timing
        "get_technical_indicators",
        "predict_market_trend",
    )
]

# Dashboard tools for debt visualisation
DEBT_DASHBOARD_TOOLS = [
    t for t in DASHBOARD_TOOL_DEFINITIONS
    if t["name"] == "generate_debt_payoff_dashboard"
]

DEBT_TOOLS = WEB_TOOLS + DEBT_CALC_TOOLS + DEBT_MARKET_TOOLS + DEBT_DASHBOARD_TOOLS


def create_debt_agent() -> OpenAICompatibleAgent:
    return OpenAICompatibleAgent(
        name="Debt Agent",
        system_prompt=DEBT_SYSTEM_PROMPT,
        tools=DEBT_TOOLS,
        model=DEBT_AGENT_MODEL,   # gpt-4o-mini
        api_key=OPENAI_API_KEY,
    )
