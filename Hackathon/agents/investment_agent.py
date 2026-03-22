"""
Investment Agent — Investment strategist with live market data and simulation capabilities.
Has full internet and market data access for real-time portfolio analysis.
"""

from agents.base_agent import OpenAICompatibleAgent
from tools.market_data import MARKET_DATA_TOOL_DEFINITIONS, WEB_TOOLS
from tools.dashboard_generator import DASHBOARD_TOOL_DEFINITIONS
from config import GEMINI_API_KEY, GEMINI_BASE_URL, INVESTMENT_AGENT_MODEL

INVESTMENT_SYSTEM_PROMPT = """You are a Certified Financial Planner and Investment Strategist
with 18 years of experience in personal investing, portfolio construction, and retirement planning.

Your expertise:
- Asset allocation across equities, bonds, and alternative assets
- Index fund investing and passive strategies
- Compound interest and long-term growth modelling
- Tax-advantaged accounts (401k, IRA, Roth IRA, HSA)
- Retirement planning and Financial Independence calculations
- Risk-adjusted return analysis
- Comprehensive Financial Planning
- Investment Strategy and Management
- Fiduciary Duty
- Tax Planning and Strategy
- Monitoring and Adjusting



You have LIVE market data access. Use it proactively:
- Always call get_market_overview() to give current market context before simulations
- Use get_stock_quote() to look up specific stocks or ETFs the user mentions
- Use get_current_rates() to benchmark bond yields against equity expected returns
- Use get_sector_performance() to identify where market strength/weakness is
- Use search_etf_for_goal() to recommend specific ETFs for their allocation
- Use web_search for: current Fed policy impact, recent market events, specific fund research
- Use web_fetch to read Yahoo Finance, Morningstar, or Vanguard fund pages directly

Your investment philosophy:
- Diversification is the only free lunch in investing
- Time in market beats timing the market
- Low-cost index funds outperform most active funds over 10+ years
- Asset allocation should match both risk tolerance AND risk capacity
- Always fund emergency reserves before investing aggressively

Simulation approach:
- Run THREE scenarios: pessimistic (5%), base case (7%), optimistic (10% annual return)
- Show both nominal and inflation-adjusted (real) values
- Always compare "invest now" vs "wait 1 year" to illustrate the cost of delay

Important: Past returns don't guarantee future results. You provide educational information,
not personalized regulated financial advice. Recommend a fiduciary CFP for complex situations.
"""

# Investment-specific calculation tools
INVESTMENT_CALC_TOOLS = [
    {
        "name": "run_investment_simulation",
        "description": "Simulate compound investment growth over time with monthly contributions. Use multiple times with different return rates to show best/base/worst case scenarios.",
        "input_schema": {
            "type": "object",
            "properties": {
                "initial_amount": {"type": "number", "description": "Initial investment amount in dollars"},
                "monthly_contribution": {"type": "number", "description": "Monthly contribution amount"},
                "annual_return_pct": {"type": "number", "description": "Expected annual return percentage (e.g. 7.0 for 7%)"},
                "years": {"type": "integer", "description": "Investment time horizon in years"},
                "inflation_pct": {"type": "number", "description": "Annual inflation rate, default 2.5", "default": 2.5},
            },
            "required": ["initial_amount", "monthly_contribution", "annual_return_pct", "years"],
        },
    },
    {
        "name": "portfolio_allocation_recommendation",
        "description": "Recommend an asset allocation (stocks/bonds/cash) based on age, risk tolerance, investment horizon, and emergency fund status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "description": "User's current age"},
                "risk_tolerance": {"type": "string", "enum": ["conservative", "moderate", "aggressive"], "description": "Risk tolerance level"},
                "investment_horizon_years": {"type": "integer", "description": "Years until the money is needed"},
                "emergency_fund_months": {"type": "number", "description": "Months of expenses currently in emergency fund"},
            },
            "required": ["age", "risk_tolerance", "investment_horizon_years", "emergency_fund_months"],
        },
    },
]

# Full suite of market data tools for Investment Agent
INVESTMENT_MARKET_TOOLS = [
    t for t in MARKET_DATA_TOOL_DEFINITIONS
    if t["name"] in (
        "get_stock_quote",
        "get_market_overview",
        "get_current_rates",
        "get_sector_performance",
        "search_etf_for_goal",
        "capital_one_get_account_summary",
        # All 4 ML predictor tools — full suite for investment decisions
        "get_technical_indicators",
        "predict_market_trend",
        "predict_stock_momentum",
        "predict_portfolio_volatility",
    )
]

# Dashboard tools for investment visualisation
INVESTMENT_DASHBOARD_TOOLS = [
    t for t in DASHBOARD_TOOL_DEFINITIONS
    if t["name"] == "generate_investment_dashboard"
]

INVESTMENT_TOOLS = WEB_TOOLS + INVESTMENT_CALC_TOOLS + INVESTMENT_MARKET_TOOLS + INVESTMENT_DASHBOARD_TOOLS


def create_investment_agent() -> OpenAICompatibleAgent:
    return OpenAICompatibleAgent(
        name="Investment Agent",
        system_prompt=INVESTMENT_SYSTEM_PROMPT,
        tools=INVESTMENT_TOOLS,
        model=INVESTMENT_AGENT_MODEL,
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL,
    )
