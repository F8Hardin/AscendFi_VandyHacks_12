"""
Risk Agent — Financial risk prediction specialist.
Covers: overdraft probability, missing payments, credit score forecasting.
Has internet access for live rate context and current credit market news.
"""

from agents.base_agent import OpenAICompatibleAgent
from tools.market_data import MARKET_DATA_TOOL_DEFINITIONS, WEB_TOOLS
from config import GEMINI_API_KEY, GEMINI_BASE_URL, RISK_AGENT_MODEL

RISK_SYSTEM_PROMPT = """You are an elite Financial Risk Analyst with 20 years of experience in
credit risk, personal finance risk management, and predictive analytics.

Your role is to assess and predict financial risks for individuals:
- Overdraft probability based on cash flow patterns
- Risk of missing upcoming bill payments
- Credit score trajectory (increase or decrease)
- Early warning signals before financial distress

You have LIVE internet access. Use it to:
- Check current interest rates (get_current_rates) for accurate debt cost benchmarks
- Search for current average credit card APRs and personal loan rates
- Look up current Federal Reserve policy and its impact on consumer credit
- Browse news about credit market conditions that affect your client

Communication style:
- Be direct and honest about risks — sugarcoating costs people money
- Always quantify risk with numbers/probabilities when possible
- Provide 1-3 clear, actionable steps to mitigate each risk
- Explain WHY a risk exists, not just that it exists
- Anchor your advice to CURRENT market conditions, not historical averages

When given financial data, ALWAYS use the calculation tools first for precise metrics,
then use web/market tools to add current market context. Do not guess — calculate and verify.
"""

# Risk-specific calculation tools
RISK_CALC_TOOLS = [
    {
        "name": "calculate_overdraft_probability",
        "description": "Calculate the probability of an overdraft occurring in the next 30 days based on account balance, income, expenses, and overdraft history.",
        "input_schema": {
            "type": "object",
            "properties": {
                "average_daily_balance": {"type": "number", "description": "Average daily account balance in dollars"},
                "monthly_income": {"type": "number", "description": "Total monthly take-home income"},
                "monthly_expenses": {"type": "number", "description": "Total monthly expenses"},
                "num_overdrafts_last_12m": {"type": "integer", "description": "Number of overdrafts in the past 12 months"},
            },
            "required": ["average_daily_balance", "monthly_income", "monthly_expenses", "num_overdrafts_last_12m"],
        },
    },
    {
        "name": "predict_credit_score_change",
        "description": "Predict whether the user's credit score will increase or decrease over the next 3 months.",
        "input_schema": {
            "type": "object",
            "properties": {
                "current_score": {"type": "integer", "description": "Current credit score (300-850)"},
                "credit_utilization_pct": {"type": "number", "description": "Current credit utilization percentage"},
                "missed_payments_last_6m": {"type": "integer", "description": "Number of missed payments in last 6 months"},
                "new_credit_inquiries": {"type": "integer", "description": "Number of hard inquiries in last 6 months"},
                "account_age_years": {"type": "number", "description": "Average age of credit accounts in years"},
            },
            "required": ["current_score", "credit_utilization_pct", "missed_payments_last_6m", "new_credit_inquiries", "account_age_years"],
        },
    },
    {
        "name": "assess_missing_payment_risk",
        "description": "Identify which upcoming bills are at risk of being missed given the current account balance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "bills": {
                    "type": "array",
                    "description": "List of upcoming bills",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "due_date_days_away": {"type": "integer"},
                            "amount": {"type": "number"},
                            "autopay": {"type": "boolean"},
                        },
                    },
                },
                "current_balance": {"type": "number", "description": "Current account balance"},
            },
            "required": ["bills", "current_balance"],
        },
    },
]

# Market data tools relevant to risk analysis
RISK_MARKET_TOOLS = [
    t for t in MARKET_DATA_TOOL_DEFINITIONS
    if t["name"] in (
        "get_current_rates",
        "capital_one_get_account_summary",
        "capital_one_get_transactions",
        # ML predictor tools — market signals to contextualise risk
        "get_technical_indicators",
        "predict_market_trend",
    )
]

RISK_TOOLS = WEB_TOOLS + RISK_CALC_TOOLS + RISK_MARKET_TOOLS


def create_risk_agent() -> OpenAICompatibleAgent:
    return OpenAICompatibleAgent(
        name="Risk Agent",
        system_prompt=RISK_SYSTEM_PROMPT,
        tools=RISK_TOOLS,
        model=RISK_AGENT_MODEL,
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL,
    )
