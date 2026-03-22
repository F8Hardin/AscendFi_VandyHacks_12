# FinanceAI — Multi-Agent Financial Intelligence System
### Complete Project History & Documentation
**Date:** March 21, 2026 | **Hackathon Project** | **Built with Claude claude-opus-4-6**
**Latest additions:** Persistent Conversation Memory · Mandatory Supervisor Delegation · Interactive Dashboards · Capital One API Key Auth

---

## Table of Contents
1. [Project Vision](#1-project-vision)
2. [System Architecture](#2-system-architecture)
3. [Agent Roster](#3-agent-roster)
4. [Internet & Market Data Access](#4-internet--market-data-access)
5. [ML Prediction Engine](#5-ml-prediction-engine)
6. [Agent Communication Bus](#6-agent-communication-bus)
7. [Persistent Conversation Memory](#7-persistent-conversation-memory)
8. [Capital One API Integration](#8-capital-one-api-integration)
9. [Multi-LLM API Configuration](#9-multi-llm-api-configuration)
10. [Financial Tools & Calculators](#10-financial-tools--calculators)
11. [How It Works — Data Flow](#11-how-it-works--data-flow)
12. [Complete Source Code](#12-complete-source-code)
13. [Setup & Run Instructions](#13-setup--run-instructions)
14. [Demo Scenarios](#14-demo-scenarios)
15. [Design Decisions](#15-design-decisions)
16. [Project File Structure](#16-project-file-structure)
17. [Interactive Dashboard Generation](#17-interactive-dashboard-generation)

---

## 1. Project Vision

FinanceAI is a multi-agent AI system that gives everyone access to the kind of comprehensive
financial intelligence previously reserved for wealthy clients of private banks.

**Four pillars of the system:**

| Pillar | What it does |
|--------|-------------|
| **Financial Risk Prediction** | ML-trained overdraft probability, missing payments, credit score trajectory |
| **Debt Optimization Engine** | Calculates the mathematically optimal path out of debt (avalanche/snowball/consolidation) |
| **Behavioural AI** | Tracks spending habits, identifies emotional triggers, coaches behaviour change |
| **Automated Financial Planning** | Paycheck splitting, investment simulations, portfolio analysis, wealth building roadmaps |

**The key innovation:** A Supervisor Agent with 50 years of simulated financial experience orchestrates
five specialist agents — each an expert in their domain — connected to live internet, real market data,
a machine learning prediction engine trained on Yahoo Finance, and a shared inter-agent communication
bus so each agent builds on what others have already found.

---

## 2. System Architecture

```
User
  │
  ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SUPERVISOR AGENT (ARIA)                       │
│   "50 years of finance experience"                               │
│   • Mandatory delegation — ALWAYS calls ≥1 agent (tool_choice)  │
│   • Routes questions to the right specialist(s)                  │
│   • Synthesises multi-agent findings via bus                     │
│   • Persistent memory — loads/saves history across sessions      │
│   • Resets AgentBus between sessions                             │
│   Model: claude-opus-4-6 + adaptive thinking                     │
└──────────┬──────────────────────────────────────────────────────┘
           │  Tool Use — delegates to agents
    ┌──────┴──────────────────────────────────────────────────┐
    │                                                         │
    ▼                                                         ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  RISK    │  │  DEBT    │  │BEHAVIOUR │  │INVESTMENT│  │ WEALTH   │
│  AGENT   │  │  AGENT   │  │  AGENT   │  │  AGENT   │  │  AGENT   │
│          │  │          │  │          │  │          │  │          │
│ +WEB     │  │ +WEB     │  │ +WEB     │  │ +WEB     │  │ +WEB     │
│ +RATES   │  │ +RATES   │  │ +MARKET  │  │ +QUOTES  │  │ +MARKET  │
│ +CAP ONE │  │ +CAP ONE │  │ +CAP ONE │  │ +SECTORS │  │ +RATES   │
│ +ML(2)   │  │ +ML(2)   │  │ +ML(1)   │  │ +ML(4)   │  │ +ML(2)   │
│          │  │ +DASH(1) │  │          │  │ +DASH(1) │  │ +DASH(1) │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │              │              │              │              │
     └──────────────┴──────┬───────┴──────────────┴─────────────┘
                           │
               ┌───────────┴───────────┐
               │    AGENT BUS          │
               │  (singleton shared    │
               │   memory — findings   │
               │   auto-published,     │
               │   peer context        │
               │   auto-injected)      │
               └───────────────────────┘
                           │
         ┌─────────────────┴──────────────────────────┐
         │                                            │
         ▼                                            ▼
┌─────────────────────┐           ┌──────────────────────────────────┐
│  ANTHROPIC SERVERS  │           │   LOCAL PYTHON TOOLS             │
│  (auto-handled)     │           │                                  │
│                     │           │  financial_calculators.py        │
│  • web_search       │           │  • overdraft_probability         │
│  • web_fetch        │           │  • credit_score_change           │
│  → Any website      │           │  • missing_payment_risk          │
│  → Yahoo Finance    │           │  • debt_payoff_plan              │
│  → Freddie Mac      │           │  • debt_consolidation            │
│  → Fed Reserve      │           │  • investment_simulation         │
│  → Morningstar      │           │  • portfolio_allocation          │
└─────────────────────┘           │  • paycheck_split                │
                                  │  • net_worth_tracker             │
                                  │  • spending_patterns             │
                                  │                                  │
                                  │  market_data.py                  │
                                  │  • get_stock_quote               │
                                  │  • get_market_overview           │
                                  │  • get_current_rates             │
                                  │  • get_sector_performance        │
                                  │  • search_etf_for_goal           │
                                  │  • capital_one_accounts          │
                                  │  • capital_one_transactions      │
                                  │                                  │
                                  │  ml_predictor.py (NEW)           │
                                  │  • get_technical_indicators      │
                                  │  • predict_market_trend  [RF]    │
                                  │  • predict_stock_momentum        │
                                  │  • predict_portfolio_volatility  │
                                  │                                  │
                                  │  dashboard_generator.py (NEW)    │
                                  │  • generate_debt_payoff_dashboard│
                                  │  • generate_investment_dashboard │
                                  │  • generate_budget_dashboard     │
                                  │  • generate_financial_plan_dash  │
                                  │    → plotly HTML → browser       │
                                  └──────────────────────────────────┘
```

**Six-tier architecture:**
1. **Supervisor → Agents** — mandatory delegation via `tool_choice="any"` + Claude tool use
2. **Supervisor ↔ ConversationMemory** — persists all exchanges to `~/.financeai/` for cross-session continuity
3. **Agents ↔ AgentBus** — peer context published after each run, injected before next
4. **Agents → Web** — server-side `web_search` / `web_fetch` (Anthropic handles)
5. **Agents → Local Functions** — calculators + live market data + ML predictions (Python)
6. **Agents/Supervisor → Dashboards** — plotly interactive HTML charts, auto-opened in browser

---

## 3. Agent Roster

### ARIA — The Supervisor (Chief Financial Intelligence Officer)
- **Experience:** 50 years across Wall Street, retail banking, wealth management, personal finance
- **Role:** Routes every question to specialist agent(s), synthesises output — never answers directly
- **No internet access** — delegates data gathering to specialist agents
- **Mandatory delegation:** `tool_choice={"type": "any"}` on the first API call of every user turn forces ARIA to consult at least one specialist agent before synthesising. After agents respond, `tool_choice` switches to `"auto"` for synthesis.
- **Persistent memory:** `ConversationMemory` loads prior conversation history from `~/.financeai/history.json` on startup. Every exchange is saved to disk so ARIA remembers past sessions automatically. Injects known user profile into system prompt.
- **Bus integration:** Calls `bus.reset()` between sessions; reads `get_agent_insights()` for synthesis
- **Dashboard:** `generate_financial_plan_dashboard` — comprehensive 6-panel plan chart synthesising debt, investments, savings, net worth, cash flow, and milestones. Called directly by ARIA after agents report.
- **Routing logic:**
  - Risk questions → Risk Agent
  - Debt questions → Debt Agent
  - Spending habits → Behaviour Agent
  - Investments/growth → Investment Agent
  - Income/budgeting/net worth → Wealth Agent
  - Full financial plan with time period → specialist agents + `generate_financial_plan_dashboard`
  - Complex situations → Multiple agents in sequence

---

### 🔴 Risk Agent — Financial Risk Analyst (20 yrs experience)
**Covers:** Overdraft probability, credit score prediction, missing payment risk

**Internet access — uses it to:**
- Check current interest rates (`get_current_rates`) for debt cost benchmarks
- Search current average credit card APRs and personal loan rates
- Look up Federal Reserve policy and its impact on consumer credit
- Browse current credit market conditions

**ML tools:**
- `get_technical_indicators` — market signal context for risk calibration
- `predict_market_trend` — identify whether broader market stress amplifies user risk

**Tools (10 total):** `web_search`, `web_fetch`, `calculate_overdraft_probability`,
`predict_credit_score_change`, `assess_missing_payment_risk`, `get_current_rates`,
`capital_one_get_account_summary`, `capital_one_get_transactions`,
`get_technical_indicators`, `predict_market_trend`

---

### 🟠 Debt Agent — Debt Freedom Strategist (15 yrs experience)
**Covers:** Avalanche/snowball payoff plans, consolidation analysis, refinancing

**Internet access — uses it to:**
- Check live Treasury yields and consumer rate benchmarks (`get_current_rates`)
- Search for current personal loan rates and 0% balance transfer offers
- Look up whether the Fed recently changed rates (affects variable-rate debt)
- Browse current debt relief program availability

**ML tools:**
- `get_technical_indicators` — rate environment signals for refinancing timing
- `predict_market_trend` — trend context for variable-rate debt risk

**Dashboard:** `generate_debt_payoff_dashboard` — 4-panel interactive chart: balance decline over time, per-debt stacked area, interest vs principal donut, monthly payment composition.

**Tools (9 total):** `web_search`, `web_fetch`, `debt_payoff_plan`, `debt_consolidation_analysis`,
`get_current_rates`, `capital_one_get_account_summary`,
`get_technical_indicators`, `predict_market_trend`,
`generate_debt_payoff_dashboard`

---

### 🟡 Behaviour Agent — Behavioural Finance Coach
**Covers:** Spending pattern analysis, emotional trigger detection, habit coaching

**Internet access — uses it to:**
- Benchmark user spending against current national averages
- Search consumer spending trends and inflation impact by category
- Look up food/gas/housing inflation for budget pressure context
- Pull Capital One transaction data when user connects their account

**ML tools:**
- `predict_stock_momentum` — market momentum context (e.g. "while you were stress-spending, markets dropped 8%")

**Tools (7 total):** `web_search`, `web_fetch`, `analyse_spending_patterns`, `get_market_overview`,
`capital_one_get_account_summary`, `capital_one_get_transactions`, `predict_stock_momentum`

---

### 🟢 Investment Agent — Certified Financial Planner (18 yrs experience)
**Covers:** Portfolio allocation, compound growth simulations, retirement planning

**Internet access — uses it to:**
- Fetch live stock/ETF quotes for any ticker (`get_stock_quote`)
- Get current market context before simulations (`get_market_overview`)
- Check sector performance for diversification analysis (`get_sector_performance`)
- Match ETFs to investment goals (`search_etf_for_goal`)
- Browse Morningstar, Vanguard fund pages, current market news

**ML tools (full suite):**
- `get_technical_indicators` — entry/exit timing signals
- `predict_market_trend` — 5/10/20-day directional forecast for investment timing
- `predict_stock_momentum` — composite score for ranking holdings
- `predict_portfolio_volatility` — risk, beta, Sharpe, correlation analysis

**Dashboard:** `generate_investment_dashboard` — 4-panel interactive chart: 3 growth scenarios (5%/7%/10%), contributions vs compounding area, year-by-year bar, scenario comparison.

**Tools (15 total):** `web_search`, `web_fetch`, `run_investment_simulation`,
`portfolio_allocation_recommendation`, `get_stock_quote`, `get_market_overview`,
`get_current_rates`, `get_sector_performance`, `search_etf_for_goal`,
`capital_one_get_account_summary`, `get_technical_indicators`, `predict_market_trend`,
`predict_stock_momentum`, `predict_portfolio_volatility`,
`generate_investment_dashboard`

---

### 🔵 Wealth Agent — Wealth Building Coach (25 yrs experience)
**Covers:** Paycheck splits, net worth tracking, wealth building roadmaps

**Internet access — uses it to:**
- Get current market context for wealth-building decisions (`get_market_overview`)
- Check current high-yield savings account rates (`get_current_rates`)
- Search current 401k/IRA/HSA contribution limits (change annually)
- Look up FIRE benchmarks and housing market data

**ML tools:**
- `predict_portfolio_volatility` — portfolio risk assessment for wealth strategy
- `predict_stock_momentum` — timing context for wealth building entries

**Dashboard:** `generate_budget_dashboard` — 4-panel interactive chart: income allocation donut, expense categories bar, cumulative savings line, monthly cash flow bar.

**Tools (10 total):** `web_search`, `web_fetch`, `paycheck_split_recommendation`,
`net_worth_tracker`, `get_market_overview`, `get_current_rates`,
`capital_one_get_account_summary`, `predict_portfolio_volatility`, `predict_stock_momentum`,
`generate_budget_dashboard`

---

## 4. Internet & Market Data Access

### Web Search & Fetch (Server-Side — Anthropic)
All five specialist agents have `web_search_20260209` and `web_fetch_20260209` built in.
These are executed automatically by Anthropic's servers — no API key needed beyond
the main `ANTHROPIC_API_KEY`. Claude can browse any financial website in real time.

Example sites agents browse:
- `finance.yahoo.com` — stock quotes, market data, financial news
- `freddiemac.com/pmms` — current mortgage rates
- `federalreserve.gov` — Fed funds rate, monetary policy
- `morningstar.com` — fund analysis and ratings
- `bankrate.com` — current savings, CD, and loan rates
- `bls.gov` — CPI and inflation data

### Yahoo Finance Python Tools (`tools/market_data.py`)

| Function | Returns | Used by |
|----------|---------|---------|
| `get_stock_quote(symbol)` | Price, PE, yield, 52-wk range, day change | Investment |
| `get_market_overview()` | S&P 500, NASDAQ, Dow, VIX, 10-yr Treasury, Gold, Oil | All |
| `get_current_rates()` | 13-wk, 5-yr, 10-yr, 30-yr Treasury yields | Risk, Debt, Wealth |
| `get_sector_performance()` | All 11 S&P sectors, daily + YTD via SPDR ETFs | Investment |
| `search_etf_for_goal(goal)` | Curated low-cost ETFs with live prices | Investment |

**Live data verified:** SPY $648.57, 10-yr Treasury 4.39%, SPY RSI 25.8 (oversold) — March 21, 2026

### `pause_turn` Handling
When web search/fetch uses more than 10 server-side iterations, Claude returns
`stop_reason: "pause_turn"`. `base_agent.py` catches this and re-sends the conversation
automatically (up to 10 continuations) so complex research tasks complete without errors.

---

## 5. ML Prediction Engine

### Overview (`tools/ml_predictor.py`)

A self-contained machine learning prediction engine built on `scikit-learn` and Yahoo Finance
historical data. Requires no external ML data source — all training data comes from `yfinance`.

**All four tools are available to specialist agents (Investment Agent has all four; others
receive the tools most relevant to their domain).**

### Tool 1: `get_technical_indicators(symbol)`
Computes classic TA signals from 6 months of Yahoo Finance daily OHLCV data.

| Indicator | Details |
|-----------|---------|
| **RSI (14-day)** | Values <30 = oversold (buy signal), >70 = overbought (sell signal) |
| **MACD** | Line, signal line, histogram. Above signal = bullish momentum |
| **Bollinger Bands** | 20-day, 2σ. Band position 0–100% shows where price sits in the band |
| **Moving Averages** | 20d, 50d, 200d. Golden cross (50d > 200d) = long-term bullish |
| **Volume** | Ratio vs 20-day average. High volume confirms trend, low volume = caution |
| **52-week range** | Where current price sits in the annual high/low range |
| **Overall bias** | Counts bullish vs bearish signals → BULLISH / BEARISH / MIXED/NEUTRAL |

### Tool 2: `predict_market_trend(symbol, horizon_days=5)`
Trains a `RandomForestClassifier` on 2 years of OHLCV data. Labels: up >1% in N days = +1 (BULLISH),
down >1% = -1 (BEARISH), flat = 0 (NEUTRAL). Trains on first 80%, predicts on current features.

**Features used:** 5d/10d/20d price momentum, RSI(14), RSI(7), MACD histogram, MACD line,
Bollinger band position, MA ratio (20d/50d), volume ratio, daily range %, 20d rolling volatility

**Returns:** prediction, confidence (0–1), confidence label (high/moderate/low),
probabilities for all 3 classes, model test accuracy, top 5 feature importances,
recent actual 5d/20d returns

**Live result:** SPY → BEARISH (confidence 0.538 moderate), vol_20d top driver — March 21, 2026

### Tool 3: `predict_stock_momentum(symbol)`
Composite momentum score from **-100** (strong downtrend) to **+100** (strong uptrend).

**Signal scale:**

| Score | Signal | Meaning |
|-------|--------|---------|
| ≥ 40 | BUY | Strong positive momentum across timeframes |
| 15–39 | ACCUMULATE | Positive momentum building |
| -14 to +14 | HOLD/WAIT | Mixed signals — no clear edge |
| -15 to -39 | REDUCE | Negative momentum developing |
| ≤ -40 | SELL/AVOID | Strong negative momentum |

**Components:** 5d/10d/20d/60d/90d price returns + RSI(14) centred at 50 + MACD histogram + MA alignment

**Live result:** QQQ → score -48.2 (MODERATE), signal SELL/AVOID, 5d: -1.96% — March 21, 2026

### Tool 4: `predict_portfolio_volatility(symbols, weights)`
Portfolio risk analytics from 1 year of Yahoo Finance daily returns.

**Returns:**
- Annualised portfolio volatility (%) + risk classification
- Beta vs S&P 500
- Estimated 1-year return (from trailing 1yr)
- Sharpe ratio estimate (risk-free rate: 5%)
- Individual asset volatilities
- Pairwise correlation matrix
- SPY benchmark comparison

**Risk classification:** <8% LOW | 8–15% MODERATE | 15–22% HIGH | >22% VERY HIGH

**Live result:** VTI/BND/GLD at 60/30/10 → vol 12.1% MODERATE, beta 0.615, Sharpe 0.882,
correlations VTI-BND: 0.129, VTI-GLD: 0.074 — March 21, 2026

### Integration with `market_data.py`
`ml_predictor.py` exports `ML_PREDICTOR_TOOL_DEFINITIONS` and `ML_TOOL_FUNCTIONS`.
`market_data.py` imports and extends its registries automatically:

```python
# At bottom of market_data.py:
from tools.ml_predictor import ML_PREDICTOR_TOOL_DEFINITIONS, ML_TOOL_FUNCTIONS
MARKET_DATA_TOOL_DEFINITIONS.extend(ML_PREDICTOR_TOOL_DEFINITIONS)
MARKET_TOOL_FUNCTIONS.update(ML_TOOL_FUNCTIONS)
```

Agents already filtering `MARKET_DATA_TOOL_DEFINITIONS` by name pick up ML tools with no
further changes to their tool routing code.

### Tool routing in `base_agent.py`
```
_execute_custom_tool(name, inputs):
  1. Check TOOL_FUNCTIONS          (financial_calculators.py)
  2. Check ML_TOOL_FUNCTIONS       (ml_predictor.py)
  3. Check MARKET_TOOL_FUNCTIONS   (market_data.py)
  4. Check DASHBOARD_TOOL_FUNCTIONS (dashboard_generator.py)  ← NEW
```

---

## 6. Agent Communication Bus

### Overview (`agents/agent_bus.py`)

A thread-safe singleton shared-memory bus so agents inform each other's analysis.
Without this, if the Risk Agent detects high overdraft risk but the Investment Agent runs next,
it has no idea — potentially recommending aggressive investing to someone about to overdraft.
With the bus, the Investment Agent automatically knows the risk context before it starts.

### How It Works

```
1. User asks a complex question
         │
2. Supervisor calls Risk Agent
         │
3. Risk Agent runs analysis:
   - Bus receives no peer context (no agents have run yet)
   - Risk Agent completes analysis
   - BASE AGENT AUTO-PUBLISHES: "67% overdraft risk in 30 days"
         │
4. Supervisor calls Debt Agent
         │
5. Debt Agent's message is automatically enriched:
   ┌──────────────────────────────────────────────────┐
   │ [original user message]                          │
   │                                                  │
   │ ---                                              │
   │ Context from peer agents:                        │
   │ • Risk Agent: 67% overdraft risk in 30 days      │
   │ ---                                              │
   └──────────────────────────────────────────────────┘
   Debt Agent now knows the risk context → adjusts
   recommendations (more conservative cash cushion)
         │
6. Debt Agent completes → publishes: "Avalanche saves $800"
         │
7. Supervisor calls Investment Agent
         │
8. Investment Agent message enriched with BOTH:
   • Risk Agent: 67% overdraft risk in 30 days
   • Debt Agent: Avalanche saves $800 vs snowball
   → Investment Agent recommends lower risk allocation
     AND references the debt payoff timeline
```

### API

```python
from agents.agent_bus import bus   # global singleton

# Publish (called automatically by BaseFinancialAgent after each run)
bus.publish(sender="Risk Agent", topic="risk_assessment",
            data={...}, summary="67% overdraft risk in 30 days")

# Build peer context block for injection (auto-called by BaseFinancialAgent)
block = bus.get_peer_context_block("Investment Agent")
# Returns formatted text excluding Investment Agent's own context

# Read a specific agent's latest findings
ctx = bus.get_agent_context("Risk Agent")
# → {"summary": "...", "topic": "...", "timestamp": 1742566000}

# Read all agents (used by Supervisor for synthesis)
all_ctx = bus.get_all_agent_contexts()

# Session key-value store (user profile, preferences)
bus.set_session_data("monthly_income", 5200)
income = bus.get_session_data("monthly_income")

# Clear between user sessions (called by SupervisorAgent.reset_conversation())
bus.reset()

# Debug current state
print(bus.status())
```

### BaseFinancialAgent Integration
`base_agent.py` wires the bus automatically — no changes needed in individual agent files:

```python
def run(self, user_message, stream_callback=None):
    # 1. Inject peer context before running
    enriched = self._inject_peer_context(user_message)
    messages = [{"role": "user", "content": enriched}]

    # ... streaming + tool loop (unchanged) ...

    # 2. Publish findings after run completes
    self._publish_result(full_response)   # → bus.publish(self.name, ...)
    return full_response
```

Summary extraction: first ~300 characters up to a sentence boundary.
Per-topic inbox: capped at 20 messages to prevent memory bloat.

---

## 7. Persistent Conversation Memory

### Overview (`memory/conversation_store.py`)

ARIA remembers every conversation across sessions. When you close and re-open the app,
ARIA picks up exactly where the previous session ended — referencing past goals, noting
progress, and recalling the financial details you shared before.

**Storage location:** `~/.financeai/`
| File | Contents |
|------|----------|
| `history.json` | All conversation messages with timestamps |
| `profile.json` | Extracted user financial profile (income, goals, debts, etc.) |

### How It Works

```
Session 1 — March 15:
  User: "My income is $5,200, I have $4,200 on a Visa at 24.99%"
  ARIA: [delegates to Debt + Wealth agents, synthesises]
  ↓ SAVED to ~/.financeai/history.json

Session 2 — March 21 (new process launch):
  ConversationMemory loads history.json on __init__
  supervisor.conversation_history restored from disk
  System prompt includes KNOWN USER PROFILE block
  ↓
  User: "How am I doing with my debt?"
  ARIA: "Last time we spoke, your Visa had $4,200 at 24.99% APR.
         Let me check your current trajectory..."
  [delegates to Debt Agent with prior context]
```

### Context Window Management

Storing thousands of messages would blow up Claude's context window. `ConversationMemory`
keeps the last `MAX_CONTEXT_MESSAGES = 60` messages (30 exchanges) in the live context
sent to Claude. Older messages remain on disk but are not sent — preventing token overflow
while preserving history for display and profile extraction.

### API

```python
from memory.conversation_store import ConversationMemory

mem = ConversationMemory()   # loads ~/.financeai/history.json automatically

# Writing (called by SupervisorAgent after each exchange)
mem.add_message("user", "My income is $5,200/month")
mem.add_message("assistant", "Understood. Let me analyse your budget...")

# Reading for Claude context (role + content only, last 60 messages)
messages = mem.get_context_messages()

# User profile injection into system prompt
mem.update_profile("monthly_income", 5200)
mem.update_profile("primary_goal", "pay off Visa by December")
block = mem.get_profile_block()
# → "KNOWN USER PROFILE (from prior conversations):\n  • monthly_income: 5200\n  • primary_goal: ..."

# Status display
print(mem.get_summary_line())
# → "12 prior exchanges remembered (last active: 2026-03-21)."

# Recent history for 'history' command
recent = mem.get_recent_user_messages(n=5)

# Clear all (called by supervisor.reset_conversation())
mem.clear()
```

### Mandatory Delegation Enforcement

In `supervisor.py`, `chat()` tracks whether the current turn has made its first API
call. `tool_choice` is set accordingly:

```python
first_api_call = True

while True:
    # Force delegation on first call — switch to auto for synthesis pass
    tool_choice = {"type": "any"} if first_api_call else {"type": "auto"}
    first_api_call = False

    with self.client.messages.stream(
        ...
        tool_choice=tool_choice,
    ) as stream:
        ...
```

`tool_choice="any"` tells Claude it MUST call at least one of the `SUPERVISOR_TOOLS`
(the five agent tools) — it cannot skip directly to a text response. After the agents
have reported back and tool results are in the messages, `tool_choice` switches to
`"auto"` so ARIA can synthesise without being forced into more tool calls.

### Banner Display

`main.py` shows the memory status at startup:

```
💾 Memory: 12 prior exchanges remembered (last active: 2026-03-21).
```

If no history exists: `💾 Memory: No prior conversations found.`

### In-Session Commands (updated)

| Command | Action |
|---------|--------|
| `history` | Show last 5 questions you asked ARIA with timestamps |
| `reset` / `new` | Clear ALL persistent memory and start fresh |

---

## 8. Capital One API Integration

### Connection Points
Capital One's DevExchange REST API provides real account data when connected.

**Setup:**
1. Register at [developer.capitalone.com](https://developer.capitalone.com)
2. Obtain your API key from your application dashboard
3. Add to `.env`:
   ```
   CAPITAL_ONE_API_KEY=your_api_key_here
   CAPITAL_ONE_BASE_URL=https://api.capitalone.com
   ```

**Available methods (`tools/market_data.py → CapitalOneClient`):**

| Method | Endpoint | Returns |
|--------|----------|---------|
| `get_accounts()` | `GET /deposits/checking-accounts` | All checking/savings accounts |
| `get_account_balance(id)` | `GET /deposits/checking-accounts/{id}` | Current + available balance |
| `get_transactions(id, from, to)` | `GET /deposits/checking-accounts/{id}/transactions` | Transaction history |
| `get_credit_card_accounts()` | `GET /creditcards` | Credit cards, APR, limits |

The API key is automatically attached as a `?key=` query parameter on every request — no OAuth token flow, no `access_token` parameter exposed to agents or Claude.

**Graceful degradation:** When not configured, every Capital One tool call returns
clear setup instructions instead of an error — agents still work fully with manually provided data.

**Which agents use it:**
- Risk Agent — real balance for overdraft/payment risk
- Debt Agent — real credit card APR and balance data
- Behaviour Agent — real transaction history for spending analysis
- Investment Agent — real cash balance for investment capacity
- Wealth Agent — real account data for net worth calculation

---

## 9. Multi-LLM API Configuration

The project is pre-wired for four AI providers. Currently all agents run on Claude claude-opus-4-6
(Anthropic). The other API keys are registered in `config.py` for future agent specialization
or model comparison use cases.

### Configured Providers

| Provider | Env Variable | Dashboard | Status |
|----------|-------------|-----------|--------|
| **Anthropic** | `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | **Active — all agents** |
| **Google Gemini** | `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Registered — ready |
| **OpenAI** | `OPEN_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | Registered — ready |
| **Alibaba / Qwen** | `ALIBABA_API_KEY` | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com) | Registered — ready |

### `.env` File
```env
# AI Providers
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_api_key_here
OPEN_API_KEY=your_api_key_here
ALIBABA_API_KEY=your_api_key_here

# Capital One DevExchange API
CAPITAL_ONE_API_KEY=your_capital_one_api_key_here
CAPITAL_ONE_BASE_URL=https://api.capitalone.com
```

### `config.py`
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic (primary LLM — all agents)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-opus-4-6"
MAX_TOKENS = 16000
STREAM_MAX_TOKENS = 64000

# Google Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# OpenAI API
OPENAI_API_KEY = os.getenv("OPEN_API_KEY", "")

# Alibaba Cloud / Qwen API (DashScope)
ALIBABA_API_KEY = os.getenv("ALIBABA_API_KEY", "")

# Capital One DevExchange API
CAPITAL_ONE_API_KEY  = os.getenv("CAPITAL_ONE_API_KEY", "")
CAPITAL_ONE_BASE_URL = os.getenv("CAPITAL_ONE_BASE_URL", "https://api.capitalone.com")
```

---

## 10. Financial Tools & Calculators

### Risk Calculators (`tools/financial_calculators.py`)

**`calculate_overdraft_probability`**
- Inputs: `average_daily_balance`, `monthly_income`, `monthly_expenses`, `num_overdrafts_last_12m`
- Algorithm: Logistic-style score combining expense ratio, cash buffer days, overdraft history
- Returns: `probability` (0–1), `risk_level` (LOW/MEDIUM/HIGH), `buffer_days`, `recommendation`

**`predict_credit_score_change`**
- Inputs: `current_score`, `credit_utilization_pct`, `missed_payments_last_6m`, `new_credit_inquiries`, `account_age_years`
- Algorithm: Factor-based delta (utilization penalty, payment history, inquiry cost, age bonus)
- Returns: `projected_score_3m`, `expected_change`, `direction`, `key_factors`, `priority_action`

**`assess_missing_payment_risk`**
- Inputs: `bills` list (name/due_date/amount/autopay), `current_balance`
- Algorithm: Chronological running balance simulation per bill
- Returns: `at_risk_bills`, all bills with status (OK / WARNING / RISK)

### Debt Calculators

**`debt_payoff_plan`**
- Inputs: `debts` (name/balance/apr/min_payment), `extra_monthly_payment`, `strategy` (avalanche|snowball)
- Algorithm: Month-by-month simulation applying extra payment to priority debt
- Returns: `payoff_months`, `payoff_years`, `total_interest_paid`, `total_paid`, `priority_order`

**`debt_consolidation_analysis`**
- Inputs: `debts`, `consolidation_rate`, `consolidation_term_months`
- Algorithm: Weighted average rate comparison + annuity payment formula
- Returns: current weighted APR vs consolidation APR, monthly payment, saves_interest, recommendation

### Investment Calculators

**`run_investment_simulation`**
- Inputs: `initial_amount`, `monthly_contribution`, `annual_return_pct`, `years`, `inflation_pct`
- Algorithm: Month-by-month compound growth with inflation-adjusted real value + yearly snapshots
- Returns: `final_balance`, `total_contributed`, `total_gain`, `return_multiple`, `real_value`, `yearly_snapshots`

**`portfolio_allocation_recommendation`**
- Inputs: `age`, `risk_tolerance` (conservative|moderate|aggressive), `investment_horizon_years`, `emergency_fund_months`
- Algorithm: Age-based equity formula (110−age) with risk tolerance adjustments and horizon caps
- Returns: allocation (equities/bonds/cash), equity breakdown (US/intl/REITs), rationale

### Wealth Calculators

**`paycheck_split_recommendation`**
- Inputs: `net_monthly_income`, `current_rent`, `current_debt_payments`, `has_emergency_fund`, `retirement_contribution_pct`
- Algorithm: 50/30/20 framework with emergency fund and retirement priority overlay
- Returns: full allocation breakdown by needs/wants/savings with sub-categories

**`net_worth_tracker`**
- Inputs: `assets` (dict name→value), `liabilities` (dict name→value)
- Returns: `net_worth`, `liquid_assets`, `debt_to_asset_ratio`, full breakdowns, status

### Behaviour Calculators

**`analyse_spending_patterns`**
- Inputs: `transactions` (list: category/amount/date_label/merchant)
- Algorithm: Category aggregation, merchant frequency, time-bucket analysis, emotional trigger detection
- Returns: `top_5_categories`, `top_merchants`, `spending_by_time`, `behavioural_insights`

### Market Data Tools (`tools/market_data.py`)

**`get_stock_quote(symbol)`** — Yahoo Finance live quote for any stock/ETF/index
**`get_market_overview()`** — S&P 500, NASDAQ, Dow, VIX, 10-yr Treasury, Gold, Oil
**`get_current_rates()`** — 13-wk, 5-yr, 10-yr, 30-yr Treasury yields + consumer rate context
**`get_sector_performance()`** — All 11 S&P sectors via SPDR ETFs (daily + YTD)
**`search_etf_for_goal(goal)`** — Curated ETF list by goal with live prices and expense ratios
**`capital_one_get_account_summary()`** — Real checking/savings/credit card data (API key from env)
**`capital_one_get_transactions(acct_id, start, end)`** — Real transaction history

### ML Prediction Tools (`tools/ml_predictor.py`)

**`get_technical_indicators(symbol)`** — RSI, MACD, Bollinger Bands, MAs, volume, 52-wk range, overall bias
**`predict_market_trend(symbol, horizon_days)`** — RandomForest ML: BULLISH/BEARISH/NEUTRAL + confidence
**`predict_stock_momentum(symbol)`** — Composite -100 to +100 score, signal (BUY/ACCUMULATE/HOLD/REDUCE/SELL)
**`predict_portfolio_volatility(symbols, weights)`** — Annualised vol, beta, Sharpe, correlations vs SPY

---

## 11. How It Works — Data Flow

**Example: "Should I invest or pay off debt first?" (multi-agent + bus + ML + memory)**

```
1. User types message
        │
2. SupervisorAgent.chat():
   - appends to in-memory conversation_history
   - sets first_api_call = True → tool_choice will be "any"
        │
3. Supervisor streams from Claude claude-opus-4-6 with adaptive thinking
   tool_choice="any" FORCES at least one agent call
   Decides: call Debt Agent THEN Investment Agent
        │
4. ── Debt Agent run ─────────────────────────────────────────────
   │ Bus: no peer context yet — clean run
   │ Claude calls get_current_rates()     → Treasury yields
   │ Claude calls web_search              → current loan rates
   │ Claude calls predict_market_trend()  → rate direction signal
   │ Claude calls debt_payoff_plan(...)   → month-by-month simulation
   │ Debt Agent responds with analysis
   │ BUS AUTO-PUBLISHES: "Avalanche saves $800; payoff in 34 months"
        │
5. ── Investment Agent run ───────────────────────────────────────
   │ Bus injects peer context:
   │   "• Debt Agent: Avalanche saves $800; payoff in 34 months"
   │ Investment Agent knows debt situation BEFORE starting
   │ Claude calls get_market_overview()       → S&P 500, rates
   │ Claude calls get_technical_indicators()  → SPY RSI 25.8 (oversold)
   │ Claude calls predict_market_trend()      → BEARISH (mod confidence)
   │ Claude calls predict_portfolio_volatility() → risk profile
   │ Claude calls run_investment_simulation() × 3 scenarios
   │ Claude calls search_etf_for_goal()       → ETF options
   │ Investment Agent responds with CONTEXT-AWARE advice:
   │   "Given your debt payoff timeline (34 months) and current
   │    market bearishness (SPY RSI 25.8), I'd recommend..."
   │ BUS AUTO-PUBLISHES: "Dollar-cost average during bear market"
        │
6. Supervisor reads both agent responses + bus context
   tool_choice now "auto" — synthesis pass
   Synthesises integrated recommendation:
   "Pay the card (guaranteed 25% return beats volatile market).
    Meanwhile, dollar-cost average $200/month into VTI at this
    oversold level — SPY at 52-week low is historically good entry."
        │
7. Final response streamed token-by-token to user
        │
8. memory.add_message("user", user_message)    ← PERSISTED TO DISK
   memory.add_message("assistant", final_resp) ← PERSISTED TO DISK
   conversation_history updated for next turn
   Next session launch will restore this exchange automatically
```

### AgentBus Flow
```
Agent A runs → publishes summary to bus
Agent B runs → bus injects Agent A's summary into Agent B's message
Agent C runs → bus injects Agent A + Agent B summaries
Supervisor   → reads all agent summaries via get_agent_insights()
                for final synthesis
session ends → supervisor.reset_conversation() calls bus.reset()
```

### `pause_turn` Re-send Flow
```
Agent → web_search (iteration 1)
     → web_search (iteration 2)
     ...
     → web_search (iteration 10)  ← Anthropic returns pause_turn
     → base_agent appends content
     → re-sends (continuation 1)
     → web_search (iteration 11+)
     → end_turn  ← research complete
     → bus.publish(summary)      ← findings shared with peers
```

---

## 12. Complete Source Code

### `requirements.txt`
```
anthropic>=0.40.0
python-dotenv>=1.0.0
rich>=13.0.0
numpy>=1.24.0
pandas>=2.0.0
yfinance>=0.2.40
requests>=2.31.0
scikit-learn>=1.3.0
plotly>=5.0.0
```

---

### `memory/conversation_store.py` (new)
```python
"""
Persistent Conversation Memory — stores exchanges to ~/.financeai/ across sessions.
Loads automatically on SupervisorAgent.__init__ so ARIA always remembers past conversations.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

MEMORY_DIR = Path.home() / ".financeai"
HISTORY_FILE = MEMORY_DIR / "history.json"
PROFILE_FILE = MEMORY_DIR / "profile.json"
MAX_CONTEXT_MESSAGES = 60   # last 30 exchanges in active Claude context

class ConversationMemory:
    def __init__(self):
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        self._messages: list[dict] = []        # [{role, content, timestamp}]
        self.user_profile: dict[str, Any] = {}
        self._load()   # ← loads from disk on construction

    def _load(self):   # reads history.json + profile.json
    def _save_history(self):   # writes history.json (non-fatal on OSError)
    def _save_profile(self):   # writes profile.json

    def add_message(self, role: str, content: str):
        # Appends + saves immediately — every turn persisted to disk
        self._messages.append({"role": role, "content": content,
                                "timestamp": datetime.now().isoformat()})
        self._save_history()

    def update_profile(self, key: str, value: Any):
        # Store extracted user profile field
        self.user_profile[key] = value
        self._save_profile()

    def get_context_messages(self) -> list[dict]:
        # Returns last MAX_CONTEXT_MESSAGES as [{role, content}] for Claude API
        return [{"role": m["role"], "content": m["content"]}
                for m in self._messages[-MAX_CONTEXT_MESSAGES:]]

    def get_profile_block(self) -> str:
        # Returns "KNOWN USER PROFILE:\n  • key: value\n..." for system prompt injection
        if not self.user_profile: return ""
        lines = ["KNOWN USER PROFILE (remembered from prior conversations):"]
        for k, v in self.user_profile.items():
            lines.append(f"  • {k}: {v}")
        return "\n".join(lines)

    def total_exchanges(self) -> int: ...   # count of user turns
    def last_seen(self) -> str: ...         # ISO date of last message
    def is_empty(self) -> bool: ...
    def get_summary_line(self) -> str: ...  # "12 prior exchanges (last: 2026-03-21)."
    def get_recent_user_messages(self, n=5) -> list[dict]: ...  # for 'history' command
    def clear(self): ...                    # erases disk + in-memory state
```

---

### `agents/agent_bus.py` (new)
```python
"""
Agent Communication Bus — thread-safe singleton for inter-agent context sharing.
Agents auto-publish findings after each run; peers auto-receive context before running.
"""
import threading, time
from typing import Any, Optional

class AgentBus:
    _instance: "Optional[AgentBus]" = None
    _class_lock = threading.Lock()

    def __new__(cls):
        with cls._class_lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._initialized = False
                cls._instance = instance
            return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._messages: dict[str, list[dict]] = {}
        self._agent_context: dict[str, dict] = {}
        self._session_data: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._initialized = True

    def publish(self, sender, topic, data=None, summary=""):
        with self._lock:
            self._messages.setdefault(topic, []).append(
                {"sender": sender, "topic": topic, "summary": summary,
                 "data": data, "timestamp": time.time()})
            if len(self._messages[topic]) > 20:
                self._messages[topic] = self._messages[topic][-20:]
            self._agent_context[sender] = {
                "summary": summary, "topic": topic, "timestamp": time.time()}

    def get_peer_context_block(self, requesting_agent):
        peers = {n: c for n, c in self.get_all_agent_contexts().items()
                 if n != requesting_agent and c.get("summary")}
        if not peers:
            return ""
        lines = ["---", "Context from peer agents (incorporate into your analysis):"]
        for name, ctx in peers.items():
            lines.append(f"• {name}: {ctx['summary']}")
        lines.append("---")
        return "\n".join(lines)

    def get_agent_context(self, agent_name) -> Optional[dict]:
        return self._agent_context.get(agent_name)

    def get_all_agent_contexts(self):
        with self._lock:
            return dict(self._agent_context)

    def set_session_data(self, key, value):
        with self._lock:
            self._session_data[key] = value

    def get_session_data(self, key, default=None):
        return self._session_data.get(key, default)

    def reset(self):
        with self._lock:
            self._messages.clear()
            self._agent_context.clear()
            self._session_data.clear()

    def status(self):
        with self._lock:
            return {"agents_with_context": list(self._agent_context.keys()),
                    "topics": list(self._messages.keys()),
                    "message_counts": {t: len(m) for t, m in self._messages.items()}}

bus = AgentBus()  # global singleton — import this everywhere
```

---

### `agents/base_agent.py` (updated)
```python
"""
Base agent class — all specialized agents extend this.
Handles: streaming tool-use loop, AgentBus peer context injection,
ML tool routing, and post-run bus publishing.

Tool routing priority:
  1. financial_calculators.py  (TOOL_FUNCTIONS)
  2. ml_predictor.py           (ML_TOOL_FUNCTIONS)        ← NEW
  3. market_data.py            (MARKET_TOOL_FUNCTIONS)
  Server-side tools (web_search, web_fetch) are never executed locally.

AgentBus integration:
  Before run: peer summaries injected into user message
  After run:  response summary published to bus for other agents
"""

import anthropic
from config import MODEL, STREAM_MAX_TOKENS
from tools.financial_calculators import execute_tool
from tools.market_data import execute_market_tool
from tools.ml_predictor import execute_ml_tool          # ← NEW
from agents.agent_bus import bus                         # ← NEW

SERVER_SIDE_TOOLS = {"web_search", "web_fetch"}


class BaseFinancialAgent:
    def __init__(self, name, system_prompt, tools):
        self.name = name
        self.system_prompt = system_prompt
        self.tools = tools
        self.client = anthropic.Anthropic()

    def _execute_custom_tool(self, name, inputs):
        from tools.financial_calculators import TOOL_FUNCTIONS
        from tools.market_data import MARKET_TOOL_FUNCTIONS
        from tools.ml_predictor import ML_TOOL_FUNCTIONS
        from tools.dashboard_generator import DASHBOARD_TOOL_FUNCTIONS, execute_dashboard_tool  # ← NEW
        if name in TOOL_FUNCTIONS:         return execute_tool(name, inputs)
        if name in ML_TOOL_FUNCTIONS:      return execute_ml_tool(name, inputs)
        if name in MARKET_TOOL_FUNCTIONS:  return execute_market_tool(name, inputs)
        if name in DASHBOARD_TOOL_FUNCTIONS: return execute_dashboard_tool(name, inputs)         # ← NEW
        import json
        return json.dumps({"error": f"Unknown tool: {name}"})

    def _inject_peer_context(self, user_message):
        block = bus.get_peer_context_block(self.name)
        return f"{user_message}\n\n{block}" if block else user_message

    def _extract_summary(self, response):
        text = response.strip()[:500]
        for sep in (". ", ".\n", "! ", "? "):
            idx = text.rfind(sep)
            if idx > 60:
                return text[:idx + 1].strip()
        return text.strip()

    def _publish_result(self, response, topic=""):
        if not response: return
        if not topic:
            topic = self.name.lower().replace(" ", "_") + "_finding"
        bus.publish(sender=self.name, topic=topic,
                    data=response[:2000], summary=self._extract_summary(response))

    def run(self, user_message, stream_callback=None):
        enriched = self._inject_peer_context(user_message)   # ← peer context
        messages = [{"role": "user", "content": enriched}]
        full_response = ""
        MAX_CONTINUATIONS = 10
        continuations = 0

        while continuations < MAX_CONTINUATIONS:
            with self.client.messages.stream(
                model=MODEL, max_tokens=STREAM_MAX_TOKENS,
                system=self.system_prompt, thinking={"type": "adaptive"},
                tools=self.tools if self.tools else None, messages=messages,
            ) as stream:
                for event in stream:
                    if (event.type == "content_block_delta"
                            and event.delta.type == "text_delta"):
                        token = event.delta.text
                        full_response += token
                        if stream_callback: stream_callback(token)
                response = stream.get_final_message()

            if response.stop_reason == "end_turn": break
            if response.stop_reason == "pause_turn":
                continuations += 1
                messages.append({"role": "assistant", "content": response.content})
                full_response = ""
                continue
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use" and block.name not in SERVER_SIDE_TOOLS:
                        result = self._execute_custom_tool(block.name, block.input)
                        tool_results.append({"type": "tool_result",
                                             "tool_use_id": block.id, "content": result})
                messages.append({"role": "user", "content": tool_results})
                full_response = ""
                continue
            break

        self._publish_result(full_response)   # ← publish to bus
        return full_response
```

---

### `tools/ml_predictor.py` (new — key structure)
```python
"""
ML Prediction Engine — trained on Yahoo Finance historical data.
Requires: yfinance, scikit-learn, pandas, numpy
"""
import numpy as np
import yfinance as yf
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score

# ── Internal helpers ──────────────────────────────────────────────────────────
def _rsi(prices, period=14):  ...   # RSI without external TA library
def _macd(prices, fast=12, slow=26, signal=9):  ...   # (line, signal, histogram)
def _bollinger(prices, period=20, std_dev=2):  ...    # (upper, mid, lower, position)
def _feature_matrix(df):  ...       # mom_5d/10d/20d, rsi_7/14, macd_hist/line,
                                    # bb_position, ma_ratio_20_50, vol_ratio,
                                    # daily_range_pct, vol_20d

# ── Public tool functions ─────────────────────────────────────────────────────
def get_technical_indicators(symbol):  ...
    # 6mo daily data → RSI, MACD, Bollinger, MAs, volume, 52wk range, bias

def predict_market_trend(symbol, horizon_days=5):  ...
    # 2y data → RandomForest on 80% train → predict current features
    # Returns: prediction, confidence, model_test_accuracy, top_signal_drivers

def predict_stock_momentum(symbol):  ...
    # 1y data → composite -100 to +100 score from 5 timeframes + RSI + MACD
    # Returns: score, strength, signal (BUY/ACCUMULATE/HOLD/REDUCE/SELL)

def predict_portfolio_volatility(symbols, weights):  ...
    # 1y daily returns → ann. vol, beta, Sharpe, correlations, SPY benchmark

# ── Registration ─────────────────────────────────────────────────────────────
ML_PREDICTOR_TOOL_DEFINITIONS = [...]   # 4 JSON schemas for Claude
ML_TOOL_FUNCTIONS = {                   # dispatcher dict
    "get_technical_indicators":   get_technical_indicators,
    "predict_market_trend":       predict_market_trend,
    "predict_stock_momentum":     predict_stock_momentum,
    "predict_portfolio_volatility": predict_portfolio_volatility,
}

def execute_ml_tool(name, inputs) -> str:  ...   # JSON-wrapping dispatcher
```

---

### `agents/supervisor.py` (updated — mandatory delegation + persistent memory)
```python
from agents.agent_bus import bus
from memory.conversation_store import ConversationMemory          # ← NEW
from tools.dashboard_generator import (                           # ← NEW
    DASHBOARD_TOOL_DEFINITIONS, execute_dashboard_tool,
    DASHBOARD_TOOL_FUNCTIONS,
)

# SUPERVISOR_TOOLS = [...5 agent delegation tools..., _PLAN_DASHBOARD_TOOL]
# _PLAN_DASHBOARD_TOOL = generate_financial_plan_dashboard schema from DASHBOARD_TOOL_DEFINITIONS

class SupervisorAgent:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.agents = {
            "call_risk_agent":       create_risk_agent(),
            "call_debt_agent":       create_debt_agent(),
            "call_behaviour_agent":  create_behaviour_agent(),
            "call_investment_agent": create_investment_agent(),
            "call_wealth_agent":     create_wealth_agent(),
        }
        # Load persistent memory — restores prior conversation from ~/.financeai/
        self.memory = ConversationMemory()                          # ← NEW
        self.conversation_history = self.memory.get_context_messages()  # ← restored

    def _build_system_prompt(self) -> str:
        # Appends KNOWN USER PROFILE block from memory to base prompt
        prompt = SUPERVISOR_SYSTEM_PROMPT
        profile_block = self.memory.get_profile_block()
        if profile_block:
            prompt += f"\n\n{profile_block}"
        return prompt

    def chat(self, user_message, stream_callback=None):
        self.conversation_history.append({"role": "user", "content": user_message})
        messages = list(self.conversation_history)
        first_api_call = True   # ← NEW: tracks delegation enforcement

        while True:
            # Mandatory delegation: "any" forces ≥1 agent call; "auto" for synthesis
            tool_choice = {"type": "any"} if first_api_call else {"type": "auto"}  # ← NEW
            first_api_call = False

            with self.client.messages.stream(
                model=MODEL, max_tokens=STREAM_MAX_TOKENS,
                system=self._build_system_prompt(),    # ← includes profile
                thinking={"type": "adaptive"},
                tools=SUPERVISOR_TOOLS,
                tool_choice=tool_choice,               # ← NEW
                messages=messages,
            ) as stream:
                ...

        # After loop: persist both turns to disk
        self.memory.add_message("user", user_message)        # ← NEW
        self.memory.add_message("assistant", final_response) # ← NEW
        return final_response

    # Inside the tool_use handling loop:
    # Dashboard tools (generate_financial_plan_dashboard) are executed directly;
    # agent tools are delegated via _call_agent().
    # if block.name in DASHBOARD_TOOL_FUNCTIONS:
    #     result = execute_dashboard_tool(block.name, block.input)
    # else:
    #     result = self._call_agent(block.name, block.input["message"], ...)

    def reset_conversation(self):
        self.conversation_history = []
        self.memory.clear()    # ← clears ~/.financeai/ as well as in-memory state
        bus.reset()

    def get_agent_insights(self):
        return bus.get_all_agent_contexts()

    @property
    def memory_summary(self) -> str:
        return self.memory.get_summary_line()   # ← "12 prior exchanges remembered..."
```

---

### Agent files — ML tool additions
```python
# risk_agent.py — added to RISK_MARKET_TOOLS filter:
"get_technical_indicators", "predict_market_trend"

# debt_agent.py — added to DEBT_MARKET_TOOLS filter:
"get_technical_indicators", "predict_market_trend"
# + DEBT_DASHBOARD_TOOLS: "generate_debt_payoff_dashboard"            ← NEW

# behaviour_agent.py — added to BEHAVIOUR_MARKET_TOOLS filter:
"predict_stock_momentum"

# investment_agent.py — added to INVESTMENT_MARKET_TOOLS filter:
"get_technical_indicators", "predict_market_trend",
"predict_stock_momentum", "predict_portfolio_volatility"
# + INVESTMENT_DASHBOARD_TOOLS: "generate_investment_dashboard"       ← NEW

# wealth_agent.py — added to WEALTH_MARKET_TOOLS filter:
"predict_portfolio_volatility", "predict_stock_momentum"
# + WEALTH_DASHBOARD_TOOLS: "generate_budget_dashboard"               ← NEW
```

---

## 13. Setup & Run Instructions

### Prerequisites
- Python 3.9+
- Anthropic API key (required)
- Gemini, OpenAI, Alibaba keys (optional — registered, not yet wired to agents)
- Capital One API key (optional — for real account data; set `CAPITAL_ONE_API_KEY` in `.env`)

### Installation
```bash
cd /path/to/Hackathon

# Install all dependencies (includes scikit-learn + pandas for ML)
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env   # Fill in your API keys
```

### Running
```bash
python3 main.py              # Interactive chat with ARIA
python3 main.py --demo       # Pick a built-in demo scenario
```

### In-app commands
| Command | Action |
|---------|--------|
| `quit` / `exit` / `q` | Exit |
| `reset` / `new` | Clear ALL persistent memory + bus (wipes `~/.financeai/`) |
| `history` | Show last 5 questions asked with timestamps |
| `demo` | Run a demo scenario |
| `Ctrl+C` | Interrupt current response |

---

## 14. Demo Scenarios

### Demo 1 — Full Financial Check-Up
All agents + web + market data + bus. User is 31, $5,200/mo income, $4,800 expenses,
$340 avg balance, 648 credit score at 72% utilization, $25,500 in debt, $800 emergency fund.

Expected: Risk + Debt + Wealth agents called. Bus propagates risk findings to subsequent agents.
Web searches for current APRs. ML trend prediction for context. Integrated recommendation produced.

### Demo 2 — Investment Simulation
Investment Agent with live market data + ML. User is 28, $500/month to invest, $3,000 initial.
Expects: `get_market_overview()` + `get_technical_indicators()` called first, ML trend prediction
for entry timing, three scenarios (5%/7%/10%), `predict_portfolio_volatility()` for risk profile,
ETF recommendations via `search_etf_for_goal()`.

### Demo 3 — Debt Freedom Plan
Debt Agent with live rate data + ML. $29,100 across 4 debts, $400 extra/month.
Expects: `get_current_rates()` called, `predict_market_trend()` for rate environment signal,
avalanche vs snowball compared with real numbers, web search for current balance transfer offers.

---

## 15. Design Decisions

### Why enforce mandatory delegation with `tool_choice="any"` instead of relying on the system prompt?
System prompts are instructions — Claude can still decide not to follow them if it "thinks"
the answer is obvious. `tool_choice={"type": "any"}` is an API-level constraint enforced before
Claude generates any text. It is impossible for ARIA to respond without calling at least one agent
tool when this is set. The system prompt reinforces the rule; the API parameter enforces it.
`tool_choice` is only set to `"any"` on the **first** API call per user turn. After tool results
are returned, it switches to `"auto"` — otherwise Claude would be forced into infinite tool loops
instead of being able to synthesise the agents' findings.

### Why store conversation history in `~/.financeai/` instead of the project directory?
User data (past conversations, financial profile) should not live in the code directory — it
could accidentally be committed to version control, copied with the project, or deleted on a
reinstall. `~/.financeai/` is user-specific, persists across project updates, and follows the
Unix convention for application data stored in the home directory.

### Why limit the active context to `MAX_CONTEXT_MESSAGES = 60`?
Claude's 200K context window is generous but not infinite. A long-running financial advisor
relationship could easily accumulate hundreds of exchanges. Feeding all of them into every API
call would inflate costs and latency significantly. 60 messages (30 exchanges) is enough for
meaningful conversational continuity within a session and for ARIA to reference recent goals —
while the full history remains searchable on disk for the `history` command.

### Why a Communication Bus instead of passing context through the Supervisor?
The Supervisor orchestrates but shouldn't parse agent outputs — it's a routing and synthesis layer,
not a data pipeline. The bus lets agents share raw findings directly without the Supervisor
needing to understand the content. The Investment Agent gets the Risk Agent's findings verbatim,
in the context of its own reasoning — not filtered through a middle layer.

### Why inject peer context automatically in `base_agent.py` rather than making it optional?
Agents that are unaware of peer findings give inconsistent advice. Automatic injection via
`BaseFinancialAgent.run()` ensures every agent always has the latest context without requiring
each agent file to implement the bus interaction separately. One change to `base_agent.py`
benefits all five agents immediately.

### Why train the ML model fresh each run instead of persisting it?
For a hackathon, model persistence (pickle files, versioning, staleness detection) adds
complexity with minimal benefit. Training a RandomForest on 2 years of daily data takes
~1-2 seconds. It's always trained on the most recent data — no stale model problem.

### Why `scikit-learn` RandomForest for trend prediction?
Random forests handle the small-data regime well (hundreds to low-thousands of samples),
are resistant to overfitting with `max_depth` and `min_samples_leaf` constraints, return
class probabilities naturally for confidence scoring, and give feature importances for explainability.
They outperform simpler models on non-linear price patterns without requiring neural network
data volumes.

### Why compute technical indicators from scratch without a TA library?
`ta-lib` requires C compilation which breaks on many systems. `ta` (pandas-ta) adds a heavy
dependency. RSI, MACD, and Bollinger Bands are simple enough to implement correctly in ~30 lines
of pandas/numpy — and doing so means zero extra dependencies beyond pandas and numpy.

### Why web_search + web_fetch on specialist agents, not the Supervisor?
The Supervisor's job is to think and synthesise — it delegates data gathering.
Giving web access to specialist agents means web searches happen in the right context:
the Risk Agent knows what financial risk data to look for; the Investment Agent knows
which market data matters. A single Supervisor with web access would mix all domains.

### Why keep Python calculators alongside ML predictions?
Financial calculations must be precise and deterministic. The avalanche vs snowball difference
must be exact to the dollar. Python functions guarantee correct math. ML predictions add
*probabilistic context* (which direction is the market likely heading?) while Python adds
*precision* (exactly how many months to pay off this debt?). Neither alone is sufficient.

### Why `pause_turn` with 10 continuation limit?
Web research can legitimately require many searches. 10 continuations × 10 server iterations
= up to 100 web lookups per agent call — more than enough for thorough research.
The limit prevents infinite loops on edge cases.

### Why Capital One API with graceful degradation?
Hackathon demos must work even without every API connected. `CapitalOneClient.is_configured()`
checks for `CAPITAL_ONE_API_KEY` at runtime. Every tool call returns helpful setup instructions when
not connected — agents work fully with manually provided data either way.

### Why four AI provider API keys registered?
Future-proofing: different agents could be specialized to different models.
Example: Gemini for real-time data access, Qwen for multilingual users,
GPT-4o for users preferring OpenAI. All keys are in `config.py` ready to be wired.

---

## 16. Project File Structure

```
Hackathon/
├── .env.example              ← Template: 4 AI providers + Capital One keys
├── .env                      ← Your actual keys (never commit this)
├── requirements.txt          ← anthropic, dotenv, rich, numpy, pandas,
│                                yfinance, requests, scikit-learn
├── config.py                 ← All API keys + model settings
├── main.py                   ← Entry point, CLI, 3 demo scenarios
│                                Shows memory status in banner
│                                'history' command: last 5 questions
│                                'reset'/'new': clears persistent memory
├── history.md                ← This complete documentation file
│
├── agents/
│   ├── __init__.py
│   ├── agent_bus.py          ← AgentBus singleton (NEW):
│   │                            • Thread-safe inter-agent communication
│   │                            • publish(sender, topic, data, summary)
│   │                            • get_peer_context_block(agent_name)
│   │                            • get_all_agent_contexts() for Supervisor
│   │                            • set/get_session_data() for user profile
│   │                            • reset() called between user sessions
│   ├── base_agent.py         ← BaseFinancialAgent (UPDATED):
│   │                            • Streaming + tool-use agentic loop
│   │                            • pause_turn handler (web search continuation)
│   │                            • Tool routing: calculators → ML → market data → dashboards
│   │                            • Skips server_tool_use (Anthropic handles)
│   │                            • _inject_peer_context() → bus integration
│   │                            • _publish_result() → bus integration
│   ├── supervisor.py         ← SupervisorAgent (UPDATED):
│   │                            • Mandatory delegation via tool_choice="any"
│   │                            • Persistent memory via ConversationMemory
│   │                            • _build_system_prompt() injects user profile
│   │                            • Conversation history restored from disk on init
│   │                            • reset_conversation() clears disk + bus
│   │                            • get_agent_insights() reads bus context
│   │                            • memory_summary property for banner display
│   │                            • Executes generate_financial_plan_dashboard
│   │                            •   directly (not via agent delegation)
│   ├── risk_agent.py         ← Risk Agent (10 tools):
│   │                            web_search, web_fetch,
│   │                            overdraft_probability, credit_score_change,
│   │                            missing_payment_risk, get_current_rates,
│   │                            capital_one_account, capital_one_transactions,
│   │                            get_technical_indicators, predict_market_trend
│   ├── debt_agent.py         ← Debt Agent (9 tools):
│   │                            web_search, web_fetch,
│   │                            debt_payoff_plan, debt_consolidation,
│   │                            get_current_rates, capital_one_account,
│   │                            get_technical_indicators, predict_market_trend,
│   │                            generate_debt_payoff_dashboard
│   ├── behaviour_agent.py    ← Behaviour Agent (7 tools):
│   │                            web_search, web_fetch,
│   │                            analyse_spending_patterns, get_market_overview,
│   │                            capital_one_account, capital_one_transactions,
│   │                            predict_stock_momentum
│   ├── investment_agent.py   ← Investment Agent (15 tools):
│   │                            web_search, web_fetch,
│   │                            run_investment_simulation, portfolio_allocation,
│   │                            get_stock_quote, get_market_overview,
│   │                            get_current_rates, get_sector_performance,
│   │                            search_etf_for_goal, capital_one_account,
│   │                            get_technical_indicators, predict_market_trend,
│   │                            predict_stock_momentum, predict_portfolio_volatility,
│   │                            generate_investment_dashboard
│   └── wealth_agent.py       ← Wealth Agent (10 tools):
│                                web_search, web_fetch,
│                                paycheck_split, net_worth_tracker,
│                                get_market_overview, get_current_rates,
│                                capital_one_account,
│                                predict_portfolio_volatility, predict_stock_momentum,
│                                generate_budget_dashboard
│
├── tools/
│   ├── __init__.py
│   ├── financial_calculators.py  ← 10 deterministic calculation functions
│   │                                + execute_tool() dispatcher
│   │                                + TOOL_FUNCTIONS registry
│   ├── market_data.py            ← Yahoo Finance (yfinance) tools
│   │                                Capital One API client + wrappers
│   │                                execute_market_tool() dispatcher
│   │                                MARKET_DATA_TOOL_DEFINITIONS (JSON schemas)
│   │                                WEB_TOOLS (server-side tool declarations)
│   │                                Imports + extends ML registries at bottom
│   ├── ml_predictor.py           ← ML Prediction Engine (NEW):
│   │                                • get_technical_indicators() — RSI/MACD/BB
│   │                                • predict_market_trend()     — RandomForest
│   │                                • predict_stock_momentum()   — composite score
│   │                                • predict_portfolio_volatility() — risk/Sharpe
│   │                                • ML_PREDICTOR_TOOL_DEFINITIONS (JSON schemas)
│   │                                • ML_TOOL_FUNCTIONS registry
│   │                                • execute_ml_tool() dispatcher
│   └── dashboard_generator.py    ← Interactive Dashboard Engine (NEW):
│                                    • generate_debt_payoff_dashboard()
│                                    • generate_investment_dashboard()
│                                    • generate_budget_dashboard()
│                                    • generate_financial_plan_dashboard()
│                                    • _simulate_debts_monthly() — month-by-month data
│                                    • _simulate_investment_yearly() — year data
│                                    • _save_and_open() — saves HTML, opens browser
│                                    • DASHBOARD_TOOL_DEFINITIONS (JSON schemas)
│                                    • DASHBOARD_TOOL_FUNCTIONS registry
│                                    • execute_dashboard_tool() dispatcher
│
├── memory/
│   ├── __init__.py
│   └── conversation_store.py     ← ConversationMemory (NEW):
│                                    • Persists all exchanges to ~/.financeai/
│                                    • Loads prior history on init (cross-session)
│                                    • get_context_messages() → last 60 msgs for Claude
│                                    • get_profile_block() → system prompt injection
│                                    • get_recent_user_messages() → 'history' command
│                                    • clear() → wipes disk (called by reset)
│
└── utils/
    └── __init__.py               ← Reserved for future utilities

~/.financeai/                     ← User data directory (outside project)
    ├── history.json              ← Full conversation history with timestamps
    ├── profile.json              ← Extracted user financial profile
    └── dashboards/               ← Generated HTML dashboard files
        └── financial_plan_20260321_143022.html  ← Example
```

**Total:** ~2,800 lines of Python across 17 source files

---

### Tool Count Summary

| Agent | Web | Market Data | ML Predictor | Calculators | Capital One | Dashboard | Total |
|-------|-----|-------------|--------------|-------------|-------------|-----------|-------|
| Risk | 2 | 1 | 2 | 3 | 2 | — | **10** |
| Debt | 2 | 1 | 2 | 2 | 1 | 1 | **9** |
| Behaviour | 2 | 1 | 1 | 1 | 2 | — | **7** |
| Investment | 2 | 4 | 4 | 2 | 1 | 1 | **15** |
| Wealth | 2 | 2 | 2 | 2 | 1 | 1 | **10** |
| Supervisor | — | — | — | — | — | 1 (plan) | **6** (5 agent + 1 dash) |

---

---

## 17. Interactive Dashboard Generation

### Overview (`tools/dashboard_generator.py`)

When a user asks for a financial plan with a time period, any specialist agent (or ARIA directly)
can call a dashboard tool to generate an interactive HTML chart that opens automatically in the
user's default browser. Dashboards are saved to `~/.financeai/dashboards/` with a timestamp.

**Powered by:** `plotly` (install: `pip install plotly>=5.0.0`)
**Output:** Self-contained HTML with CDN-hosted Plotly JS — no server required, works offline

### Four Dashboard Types

#### 1. `generate_debt_payoff_dashboard` (Debt Agent)
**Triggered when:** user asks for a debt plan with a timeline/time period

**4-panel layout:**
| Panel | Shows |
|-------|-------|
| Total Balance Over Time | Line chart — total debt declining month by month |
| Per-Debt Breakdown | Stacked area — which debts remain when |
| Interest vs Principal | Donut — total interest cost vs principal paid |
| Monthly Payment Composition | Bar (first 24 months) — minimum + extra payments |

**Inputs:** `debts` (name/balance/apr/min_payment), `extra_monthly_payment`, `strategy` (avalanche/snowball), optional `time_period_months`, `title`

---

#### 2. `generate_investment_dashboard` (Investment Agent)
**Triggered when:** user asks for an investment projection or retirement simulation with a time period

**4-panel layout:**
| Panel | Shows |
|-------|-------|
| Growth Scenarios | 3 lines: pessimistic (5%), base (7%), optimistic (10%) |
| Contributions vs Compounding | Stacked area — your money vs market growth |
| Year-by-Year Balance | Bar chart per year for the base scenario |
| Scenario Comparison | Side-by-side bar — final values at each return rate |

**Inputs:** `initial_amount`, `monthly_contribution`, `time_period_years`, `risk_tolerance`, `title`

---

#### 3. `generate_budget_dashboard` (Wealth Agent)
**Triggered when:** user asks for a budget plan or savings projection with a time period

**4-panel layout:**
| Panel | Shows |
|-------|-------|
| Income Allocation | Donut — needs vs wants vs savings |
| Expense Categories | Horizontal bar — top spending categories |
| Cumulative Savings | Line — how savings accumulate over the period |
| Monthly Cash Flow | Bar — income, expenses, and net each month |

**Inputs:** `net_monthly_income`, `expenses` (dict), `time_period_months`, `title`

---

#### 4. `generate_financial_plan_dashboard` (Supervisor / ARIA)
**Triggered when:** user asks for a full financial plan or roadmap with a time period

**6-panel comprehensive layout:**
| Panel | Shows |
|-------|-------|
| Net Worth Trajectory | Combined savings + investments − debts over time |
| Debt Elimination | Total debt declining (shaded when debt-free) |
| Investment Growth | Conservative vs optimistic scenarios |
| Monthly Cash Flow | Income, expenses, debt payments, and free cash flow |
| Savings Accumulation | Emergency fund and liquid savings over time |
| Key Financial Milestones | Annotated timeline of debt-free date, savings targets |

**Inputs:** `time_period_months` (required), plus any of: `net_monthly_income`, `monthly_expenses`, `debts`, `extra_debt_payment`, `debt_strategy`, `initial_investment`, `monthly_investment`, `current_savings`, `title`

All non-`time_period_months` inputs are optional — the dashboard renders gracefully with partial data.

---

### Internal Architecture

```python
# dashboard_generator.py

def _simulate_debts_monthly(debts, extra_monthly_payment, strategy, cap_months=360):
    # Returns: [{"month": 1, "total": 12000, "Visa": 4000, "Car": 8000}, ...]
    # Month-by-month: apply interest, pay minimums, put extra to priority debt

def _simulate_investment_yearly(initial, monthly, annual_return_pct, years):
    # Returns: [{"year": 1, "balance": 8100, "contributed": 7500, "growth": 600}, ...]

def _save_and_open(fig, name: str) -> str:
    # Saves: ~/.financeai/dashboards/{name}_{timestamp}.html
    # Opens: webbrowser.open(path)
    # Returns: file path string

DASHBOARD_TOOL_DEFINITIONS = [...]   # 4 JSON schemas for Claude tool use
DASHBOARD_TOOL_FUNCTIONS = {         # dispatcher dict
    "generate_debt_payoff_dashboard":    generate_debt_payoff_dashboard,
    "generate_investment_dashboard":     generate_investment_dashboard,
    "generate_budget_dashboard":         generate_budget_dashboard,
    "generate_financial_plan_dashboard": generate_financial_plan_dashboard,
}

def execute_dashboard_tool(name: str, inputs: dict) -> str:
    fn = DASHBOARD_TOOL_FUNCTIONS.get(name)
    result = fn(**inputs)   # returns {"status": "opened", "path": "...", ...}
    return json.dumps(result)
```

### Integration Points

| Location | How dashboard tools are registered |
|----------|------------------------------------|
| `agents/base_agent.py` | Priority 4 in `_execute_custom_tool()` — checks `DASHBOARD_TOOL_FUNCTIONS` |
| `agents/debt_agent.py` | `DEBT_DASHBOARD_TOOLS` filter → `generate_debt_payoff_dashboard` |
| `agents/investment_agent.py` | `INVESTMENT_DASHBOARD_TOOLS` filter → `generate_investment_dashboard` |
| `agents/wealth_agent.py` | `WEALTH_DASHBOARD_TOOLS` filter → `generate_budget_dashboard` |
| `agents/supervisor.py` | `_PLAN_DASHBOARD_TOOL` appended to `SUPERVISOR_TOOLS`; executed directly (not via agent) |

### Example User Triggers

| User says... | Which dashboard opens |
|--------------|-----------------------|
| "Give me a 2-year debt payoff plan" | `generate_debt_payoff_dashboard` (via Debt Agent) |
| "Show my investment growth over 30 years" | `generate_investment_dashboard` (via Investment Agent) |
| "Create a 12-month budget plan" | `generate_budget_dashboard` (via Wealth Agent) |
| "I need a full 5-year financial plan" | `generate_financial_plan_dashboard` (via Supervisor) |

---

*FinanceAI — Built at Hackathon, March 21, 2026*
*Powered by Claude claude-opus-4-6 (Anthropic) | Multi-Agent Architecture*
*Internet-connected | Yahoo Finance | ML Prediction (RandomForest) | Agent Communication Bus*
*Persistent Conversation Memory | Mandatory Supervisor Delegation | Interactive Dashboards*
*Capital One API | Gemini · OpenAI · Alibaba ready*
