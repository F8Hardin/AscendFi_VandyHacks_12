"""
Market Data Tools
=================
Real-time market data via Yahoo Finance (yfinance) + Capital One API integration.
All functions are registered as Claude tools callable by the specialized agents.

CAPITAL ONE API
---------------
To connect your Capital One account, set these in your .env file:
    CAPITAL_ONE_API_KEY=your_api_key_here
    CAPITAL_ONE_BASE_URL=https://api.capitalone.com

Developer portal: https://developer.capitalone.com
"""

import json
import os
from typing import Any

import requests

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


# ─── Yahoo Finance Tools ──────────────────────────────────────────────────────

def get_stock_quote(symbol: str) -> dict[str, Any]:
    """
    Fetch real-time quote and key stats for a stock or ETF from Yahoo Finance.
    Use for individual securities: stocks (AAPL, MSFT), ETFs (VTI, SPY, BND),
    or indices (^GSPC for S&P 500, ^IXIC for NASDAQ, ^DJI for Dow Jones).
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    try:
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info

        # Pull the most useful fields for financial advice
        result = {
            "symbol": symbol.upper(),
            "name": info.get("longName") or info.get("shortName", symbol),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "previous_close": info.get("previousClose"),
            "day_change_pct": None,
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield_pct": (
                round(info.get("dividendYield", 0) * 100, 2)
                if info.get("dividendYield") else None
            ),
            "ytd_return_pct": (
                round(info.get("ytdReturn", 0) * 100, 2)
                if info.get("ytdReturn") else None
            ),
            "expense_ratio_pct": (
                round(info.get("annualReportExpenseRatio", 0) * 100, 3)
                if info.get("annualReportExpenseRatio") else None
            ),
            "currency": info.get("currency", "USD"),
            "exchange": info.get("exchange"),
            "sector": info.get("sector"),
            "type": info.get("quoteType"),
        }

        # Calculate day change %
        if result["current_price"] and result["previous_close"]:
            result["day_change_pct"] = round(
                (result["current_price"] - result["previous_close"])
                / result["previous_close"] * 100, 2
            )

        # Clean out None values for readability
        return {k: v for k, v in result.items() if v is not None}

    except Exception as e:
        return {"error": f"Could not fetch data for '{symbol}': {e}"}


def get_market_overview() -> dict[str, Any]:
    """
    Fetch a snapshot of major market indices, bond yields, and market sentiment.
    Covers: S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX (fear index),
    10-year Treasury yield, and Gold price.
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    symbols = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI",
        "Russell 2000": "^RUT",
        "VIX (Fear Index)": "^VIX",
        "10-Year Treasury Yield": "^TNX",
        "Gold": "GC=F",
        "Crude Oil": "CL=F",
    }

    overview = {}
    for name, sym in symbols.items():
        try:
            t = yf.Ticker(sym)
            info = t.info
            price = info.get("regularMarketPrice") or info.get("currentPrice")
            prev = info.get("previousClose") or info.get("regularMarketPreviousClose")
            change_pct = round((price - prev) / prev * 100, 2) if price and prev else None

            overview[name] = {
                "value": price,
                "change_pct_today": change_pct,
                "symbol": sym,
            }
        except Exception:
            overview[name] = {"symbol": sym, "error": "unavailable"}

    return {
        "market_snapshot": overview,
        "note": "Real-time data from Yahoo Finance. Values may be delayed 15 minutes.",
    }


def get_current_rates() -> dict[str, Any]:
    """
    Fetch current interest rate environment: Treasury yields, mortgage rates,
    and average credit card / personal loan rates. Critical context for debt
    decisions, refinancing analysis, and bond allocation.
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    rate_symbols = {
        "13-Week Treasury Bill": "^IRX",
        "5-Year Treasury Yield": "^FVX",
        "10-Year Treasury Yield": "^TNX",
        "30-Year Treasury Yield": "^TYX",
    }

    rates = {}
    for name, sym in rate_symbols.items():
        try:
            t = yf.Ticker(sym)
            info = t.info
            val = info.get("regularMarketPrice") or info.get("currentPrice")
            rates[name] = f"{val:.2f}%" if val else "unavailable"
        except Exception:
            rates[name] = "unavailable"

    return {
        "treasury_yields": rates,
        "context": {
            "avg_30yr_mortgage_rate": "See https://www.freddiemac.com/pmms for current rates",
            "avg_credit_card_apr": "Typically 20-28% (varies by credit score)",
            "avg_personal_loan_rate": "Typically 8-36% (varies by credit score)",
            "fed_funds_rate": "See https://www.federalreserve.gov for current Fed rate",
        },
        "note": "Treasury yields from Yahoo Finance. Consumer rates are approximate benchmarks.",
    }


def get_sector_performance() -> dict[str, Any]:
    """
    Fetch YTD and daily performance for all major S&P 500 sectors.
    Useful for portfolio diversification analysis and trend identification.
    """
    if not YFINANCE_AVAILABLE:
        return {"error": "yfinance not installed. Run: pip install yfinance"}

    sector_etfs = {
        "Technology": "XLK",
        "Healthcare": "XLV",
        "Financials": "XLF",
        "Consumer Discretionary": "XLY",
        "Consumer Staples": "XLP",
        "Energy": "XLE",
        "Industrials": "XLI",
        "Utilities": "XLU",
        "Real Estate": "XLRE",
        "Materials": "XLB",
        "Communication Services": "XLC",
    }

    results = {}
    for sector, sym in sector_etfs.items():
        try:
            t = yf.Ticker(sym)
            info = t.info
            price = info.get("regularMarketPrice")
            prev = info.get("previousClose")
            ytd = info.get("ytdReturn")

            results[sector] = {
                "etf": sym,
                "price": price,
                "day_change_pct": round((price - prev) / prev * 100, 2) if price and prev else None,
                "ytd_return_pct": round(ytd * 100, 2) if ytd else None,
            }
        except Exception:
            results[sector] = {"etf": sym, "error": "unavailable"}

    return {
        "sector_performance": results,
        "note": "Based on SPDR sector ETFs. YTD return from Yahoo Finance.",
    }


def search_etf_for_goal(investment_goal: str) -> dict[str, Any]:
    """
    Return a curated list of low-cost ETFs relevant to a stated investment goal.
    Goals: 'broad_market', 'international', 'bonds', 'dividends',
           'real_estate', 'emerging_markets', 'small_cap'.
    """
    etf_map = {
        "broad_market": [
            {"symbol": "VTI",  "name": "Vanguard Total Stock Market ETF",        "expense_ratio": "0.03%"},
            {"symbol": "SPY",  "name": "SPDR S&P 500 ETF Trust",                 "expense_ratio": "0.09%"},
            {"symbol": "IVV",  "name": "iShares Core S&P 500 ETF",               "expense_ratio": "0.03%"},
            {"symbol": "SCHB", "name": "Schwab US Broad Market ETF",             "expense_ratio": "0.03%"},
        ],
        "international": [
            {"symbol": "VXUS", "name": "Vanguard Total International Stock ETF", "expense_ratio": "0.07%"},
            {"symbol": "EFA",  "name": "iShares MSCI EAFE ETF",                  "expense_ratio": "0.32%"},
            {"symbol": "VEA",  "name": "Vanguard FTSE Developed Markets ETF",    "expense_ratio": "0.05%"},
        ],
        "bonds": [
            {"symbol": "BND",  "name": "Vanguard Total Bond Market ETF",         "expense_ratio": "0.03%"},
            {"symbol": "AGG",  "name": "iShares Core US Aggregate Bond ETF",     "expense_ratio": "0.03%"},
            {"symbol": "VGSH", "name": "Vanguard Short-Term Treasury ETF",       "expense_ratio": "0.04%"},
        ],
        "dividends": [
            {"symbol": "VYM",  "name": "Vanguard High Dividend Yield ETF",       "expense_ratio": "0.06%"},
            {"symbol": "SCHD", "name": "Schwab US Dividend Equity ETF",          "expense_ratio": "0.06%"},
            {"symbol": "DVY",  "name": "iShares Select Dividend ETF",            "expense_ratio": "0.38%"},
        ],
        "real_estate": [
            {"symbol": "VNQ",  "name": "Vanguard Real Estate ETF",               "expense_ratio": "0.12%"},
            {"symbol": "SCHH", "name": "Schwab US REIT ETF",                     "expense_ratio": "0.07%"},
        ],
        "emerging_markets": [
            {"symbol": "VWO",  "name": "Vanguard FTSE Emerging Markets ETF",     "expense_ratio": "0.08%"},
            {"symbol": "EEM",  "name": "iShares MSCI Emerging Markets ETF",      "expense_ratio": "0.70%"},
        ],
        "small_cap": [
            {"symbol": "VB",   "name": "Vanguard Small-Cap ETF",                 "expense_ratio": "0.05%"},
            {"symbol": "IJR",  "name": "iShares Core S&P Small-Cap ETF",         "expense_ratio": "0.06%"},
        ],
    }

    goal_key = investment_goal.lower().replace(" ", "_").replace("-", "_")
    options = etf_map.get(goal_key, [])

    if not options:
        available = list(etf_map.keys())
        return {
            "error": f"Unknown goal '{investment_goal}'",
            "available_goals": available,
        }

    # Optionally enrich with live prices
    for etf in options:
        try:
            if YFINANCE_AVAILABLE:
                t = yf.Ticker(etf["symbol"])
                info = t.info
                etf["current_price"] = info.get("regularMarketPrice")
                ytd = info.get("ytdReturn")
                etf["ytd_return_pct"] = round(ytd * 100, 2) if ytd else None
        except Exception:
            pass

    return {
        "goal": investment_goal,
        "recommended_etfs": options,
        "note": "Low-cost index ETFs. Always verify expense ratios on fund provider sites.",
    }


# ─── Capital One API Integration ──────────────────────────────────────────────

class CapitalOneClient:
    """
    Capital One DevExchange API Client.

    Setup:
    1. Register at https://developer.capitalone.com
    2. Obtain your API key from your application dashboard
    3. Add to .env:
       CAPITAL_ONE_API_KEY=your_api_key
       CAPITAL_ONE_BASE_URL=https://api.capitalone.com
    """

    BASE_URL = os.getenv("CAPITAL_ONE_BASE_URL", "https://api.capitalone.com")
    API_KEY = os.getenv("CAPITAL_ONE_API_KEY", "")

    @classmethod
    def is_configured(cls) -> bool:
        return bool(cls.API_KEY)

    @classmethod
    def _auth_params(cls) -> dict[str, str]:
        """Return the API key as a query parameter."""
        return {"key": cls.API_KEY}

    @classmethod
    def get_accounts(cls) -> dict[str, Any]:
        """
        Retrieve all accounts associated with the authenticated user.
        Returns checking, savings, and credit card accounts.
        """
        if not cls.is_configured():
            return _capital_one_not_configured()
        try:
            response = requests.get(
                f"{cls.BASE_URL}/deposits/checking-accounts",
                params=cls._auth_params(),
                headers={"Accept": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Capital One accounts request failed: {e}"}

    @classmethod
    def get_account_balance(cls, account_id: str) -> dict[str, Any]:
        """
        Get current balance and available balance for a specific account.
        """
        if not cls.is_configured():
            return _capital_one_not_configured()
        try:
            response = requests.get(
                f"{cls.BASE_URL}/deposits/checking-accounts/{account_id}",
                params=cls._auth_params(),
                headers={"Accept": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Capital One balance request failed: {e}"}

    @classmethod
    def get_transactions(
        cls,
        account_id: str,
        start_date: str,
        end_date: str,
    ) -> dict[str, Any]:
        """
        Retrieve transaction history for an account.
        Dates in ISO format: YYYY-MM-DD
        """
        if not cls.is_configured():
            return _capital_one_not_configured()
        try:
            params = {**cls._auth_params(), "startDate": start_date, "endDate": end_date}
            response = requests.get(
                f"{cls.BASE_URL}/deposits/checking-accounts/{account_id}/transactions",
                params=params,
                headers={"Accept": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Capital One transactions request failed: {e}"}

    @classmethod
    def get_credit_card_accounts(cls) -> dict[str, Any]:
        """
        Retrieve Capital One credit card accounts including balance, APR, and credit limit.
        """
        if not cls.is_configured():
            return _capital_one_not_configured()
        try:
            response = requests.get(
                f"{cls.BASE_URL}/creditcards",
                params=cls._auth_params(),
                headers={"Accept": "application/json"},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": f"Capital One credit card request failed: {e}"}


def _capital_one_not_configured() -> dict[str, Any]:
    return {
        "status": "Capital One API not connected",
        "message": (
            "To connect your Capital One account:\n"
            "1. Visit https://developer.capitalone.com\n"
            "2. Register and obtain your API key\n"
            "3. Add to .env: CAPITAL_ONE_API_KEY=your_key_here\n"
            "4. Optionally set CAPITAL_ONE_BASE_URL (defaults to https://api.capitalone.com)"
        ),
    }


# ─── Tool-callable wrappers ────────────────────────────────────────────────────
# These are the functions Claude actually calls as tools.

def capital_one_get_account_summary() -> dict[str, Any]:
    """
    Retrieve a summary of all Capital One accounts: balances, credit cards, available credit.
    Uses the CAPITAL_ONE_API_KEY from the environment automatically.
    """
    if not CapitalOneClient.is_configured():
        return _capital_one_not_configured()
    accounts = CapitalOneClient.get_accounts()
    credit = CapitalOneClient.get_credit_card_accounts()
    return {"checking_savings": accounts, "credit_cards": credit}


def capital_one_get_transactions(
    account_id: str,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """
    Retrieve transaction history from a Capital One account for a date range.
    account_id: Capital One account identifier
    start_date / end_date: ISO format YYYY-MM-DD
    """
    if not account_id:
        return _capital_one_not_configured()
    return CapitalOneClient.get_transactions(account_id, start_date, end_date)


# ─── Tool Definitions (JSON Schema for Claude) ────────────────────────────────

MARKET_DATA_TOOL_DEFINITIONS = [
    {
        "name": "get_stock_quote",
        "description": (
            "Fetch a real-time quote and key statistics for any stock, ETF, or index from Yahoo Finance. "
            "Use for: individual stocks (AAPL, MSFT, GOOGL), ETFs (VTI, SPY, BND, QQQ), "
            "or indices (^GSPC = S&P 500, ^IXIC = NASDAQ, ^DJI = Dow Jones). "
            "Returns current price, day change, 52-week range, PE ratio, dividend yield, expense ratio."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Ticker symbol, e.g. 'AAPL', 'VTI', '^GSPC'",
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_market_overview",
        "description": (
            "Fetch a snapshot of major market indices, bond yields, and commodity prices. "
            "Returns S&P 500, NASDAQ, Dow Jones, Russell 2000, VIX fear index, "
            "10-year Treasury yield, Gold, and Crude Oil. Use to provide market context "
            "for investment decisions, economic backdrop for debt advice, or spending trend analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_current_rates",
        "description": (
            "Fetch current Treasury yield curve (13-week, 5-year, 10-year, 30-year yields). "
            "Essential context for debt consolidation rate comparisons, bond allocation decisions, "
            "and mortgage refinancing analysis. Also includes benchmark consumer rate context."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_sector_performance",
        "description": (
            "Fetch daily and YTD performance for all 11 major S&P 500 sectors via SPDR ETFs. "
            "Useful for identifying market trends, portfolio sector exposure analysis, "
            "and understanding which parts of the economy are outperforming."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "search_etf_for_goal",
        "description": (
            "Return a curated list of low-cost ETFs matching a specific investment goal. "
            "Available goals: broad_market, international, bonds, dividends, "
            "real_estate, emerging_markets, small_cap. "
            "Returns ETF names, symbols, expense ratios, and current prices."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "investment_goal": {
                    "type": "string",
                    "enum": [
                        "broad_market", "international", "bonds", "dividends",
                        "real_estate", "emerging_markets", "small_cap",
                    ],
                    "description": "The type of investment goal to find ETFs for",
                },
            },
            "required": ["investment_goal"],
        },
    },
    {
        "name": "capital_one_get_account_summary",
        "description": (
            "Retrieve real account data from Capital One: checking/savings balances and credit card info. "
            "Uses the CAPITAL_ONE_API_KEY from the environment — no token needed. "
            "Use when the user wants to connect their Capital One accounts for real-time balance data."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "capital_one_get_transactions",
        "description": (
            "Retrieve transaction history from a Capital One account for behaviour analysis, "
            "spending tracking, or cash flow assessment. Requires account ID and date range."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "account_id": {
                    "type": "string",
                    "description": "Capital One account identifier",
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format",
                },
            },
            "required": ["account_id", "start_date", "end_date"],
        },
    },
]

# Server-side Claude tools (handled by Anthropic, not executed locally)
WEB_TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209",  "name": "web_fetch"},
]

# ─── Tool executor ────────────────────────────────────────────────────────────

MARKET_TOOL_FUNCTIONS = {
    "get_stock_quote": get_stock_quote,
    "get_market_overview": get_market_overview,
    "get_current_rates": get_current_rates,
    "get_sector_performance": get_sector_performance,
    "search_etf_for_goal": search_etf_for_goal,
    "capital_one_get_account_summary": capital_one_get_account_summary,
    "capital_one_get_transactions": capital_one_get_transactions,
}


def execute_market_tool(name: str, inputs: dict) -> str:
    fn = MARKET_TOOL_FUNCTIONS.get(name)
    if not fn:
        return json.dumps({"error": f"Unknown market tool: {name}"})
    try:
        result = fn(**inputs)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ─── ML Predictor tool registration ──────────────────────────────────────────
# Import after the executor to avoid circular imports.
# This extends MARKET_DATA_TOOL_DEFINITIONS and MARKET_TOOL_FUNCTIONS so that
# any agent that already imports from this module gets the ML tools for free.

try:
    from tools.ml_predictor import ML_PREDICTOR_TOOL_DEFINITIONS, ML_TOOL_FUNCTIONS
    MARKET_DATA_TOOL_DEFINITIONS.extend(ML_PREDICTOR_TOOL_DEFINITIONS)
    MARKET_TOOL_FUNCTIONS.update(ML_TOOL_FUNCTIONS)
except ImportError:
    pass  # ml_predictor optional; agents degrade gracefully
