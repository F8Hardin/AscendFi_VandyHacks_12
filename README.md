# AscendFi — VandyHacks 12

> AI-powered financial recovery platform that helps users predict risk, eliminate debt, understand spending behavior, and build autonomous finance plans.

---

## Overview

AscendFi is a full-stack web application built for VandyHacks 12. It combines a Python FastAPI backend with a Nuxt 4 frontend to deliver real-time AI-driven financial guidance — from predicting overdrafts to generating personalized debt payoff plans.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Nuxt 4, Vue 3, Tailwind CSS, Chart.js |
| Backend | Python 3.13, FastAPI, SSE streaming |
| AI | Anthropic Claude (swappable via agent registry) |
| Local AI | LM Studio (OpenAI-compatible local server) |
| Auth / DB | Supabase *(coming soon)* |

---

## AI Feature Modules

### 1. Predictive Risk Engine
- **Missing Payment Prediction** — forecasts probability of missing upcoming bills
- **Overdraft Probability** — estimates likelihood of checking account overdraft in the next 30 days
- **Credit Score Shift Detection** — flags major positive or negative credit score changes on the horizon

### 2. Debt Optimization Engine
- Analyzes all debt accounts (balance, APR, minimums)
- Compares avalanche, snowball, and hybrid payoff strategies
- Returns a month-by-month action plan with estimated payoff date and total interest saved

### 3. Behavioral Spending Tracker
- Identifies spending habits and category patterns
- Detects anomalies and situational spending driven by life events (job loss, medical emergency, relocation, divorce, new child)
- Tracks month-over-month spending trends

### 4. Autonomous Finance Planner
- Generates a recommended paycheck split (needs, debt payoff, emergency fund, investments, discretionary)
- Suggests investment vehicles based on current financial state
- Sets emergency fund targets tied to income and risk level

---

## Agent Service — Container Interface

The `agent-service` runs each user session in its own Docker container managed by the orchestrator. To swap in a custom agent, replace `agent/app/main.py` with any HTTP server that implements this contract:

### Required Endpoints

#### `POST /chat/stream`

**Request body:**
```json
{
  "messages": [
    { "role": "user" | "assistant", "content": "string" }
  ],
  "context": {
    "monthly_income": 5000.0,
    "checking_balance": 1200.0,
    "savings_balance": 300.0,
    "bills": [
      { "name": "Rent", "amount": 1200.0, "due_date": "2026-04-01", "category": "Housing" }
    ],
    "debts": [
      { "name": "Visa", "balance": 4500.0, "interest_rate": 0.22, "minimum_payment": 90.0, "type": "credit_card" }
    ],
    "spending_history": [
      { "date": "2026-03-15", "amount": 45.0, "category": "Food", "description": "Grocery run" }
    ],
    "credit_score": 620,
    "life_events": ["job_loss"],
    "extra": {}
  }
}
```

**Response:** Server-Sent Events (SSE) stream. Each line is `data: <json>\n\n`:

| Event | Shape | Description |
|-------|-------|-------------|
| Token chunk | `{"type": "token", "text": "..."}` | Append to chat output |
| Tool activity | `{"type": "tool_start", "name": "..."}` | Shown in "thinking" steps |
| Stream end | `{"type": "done"}` | Stop reading |
| Error | `{"type": "error", "message": "..."}` | Surface to user |

#### `GET /health`
```json
{ "status": "ok" }
```
The orchestrator polls this before routing any traffic to the container. Return `200` once ready.

---

## Pluggable Agent Architecture

All AI logic sits behind a shared `FinancialAgentBase` interface. Swapping AI providers requires no changes to routes or business logic.

```
backend/app/agents/
├── base.py            # Abstract interface — every agent implements this
├── claude_agent.py    # Anthropic Claude implementation
├── lm_studio_agent.py # Local LM Studio implementation
└── registry.py        # AGENT_REGISTRY + get_agent() / set_active_agent()
```

**Switch agents via env var:**
```bash
ACTIVE_AGENT=lm_studio   # use local LM Studio model
ACTIVE_AGENT=claude       # use Anthropic Claude
```

**Or hot-swap at runtime (no restart):**
```bash
curl -X POST http://localhost:8000/api/agents/lm_studio/activate
```

**Add a new agent in 2 steps:**
1. Subclass `FinancialAgentBase` and implement all methods
2. Add it to `AGENT_REGISTRY` in `registry.py`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat/stream` | SSE streaming chat (context-aware) |
| `POST` | `/api/predict/missing-payments` | Predict payment failure risk |
| `POST` | `/api/predict/overdraft` | 30-day overdraft probability |
| `POST` | `/api/predict/credit-score` | Credit score shift forecast |
| `POST` | `/api/debt/optimize` | Debt payoff plan |
| `POST` | `/api/spending/analyze` | Spending habits + life event detection |
| `POST` | `/api/finance/autonomous-plan` | Paycheck split + investment recommendations |
| `GET`  | `/api/agents` | List registered agents |
| `POST` | `/api/agents/{name}/activate` | Hot-swap the active agent |

Interactive docs available at `http://localhost:8000/docs` when the server is running.

---

## Dashboard Features

### Live
- KPI cards — Monthly Income, Checking Balance, Total Debt, Credit Score
- Risk gauges — animated SVG rings for Overdraft, Missing Payments, Credit Score shift
- Spending breakdown donut chart
- Debt payoff projection line chart
- Financial gains chart — net monthly gain + savings growth over 6 months
- Recommended paycheck split donut
- Active debts table with proportional bar indicators
- Recent activity feed

### Planned
| # | Feature | Description |
|---|---------|-------------|
| 1 | **Urgent Alerts Banner** | Dismissable strip — bills due, overdraft warnings, color-coded by severity |
| 2 | **Financial Health Score** | Single 0–100 composite score derived from credit, debt-to-income, risk, and savings |
| 3 | **Quick Actions Row** | Buttons to run Debt Optimizer, Spending Analysis, Paycheck Plan, and AI Chat |
| 4 | **Net Worth Tracker** | Signed net worth with 6-month sparkline showing recovery trajectory |
| 5 | **Monthly Cash Flow Bar** | Income vs Expenses grouped bar chart over last 3–4 months |
| 6 | **Recovery Milestones** | Horizontal progress tracker through key financial goals |
| 7 | **Next Bill Due Widget** | Countdown card to next upcoming payment |
| 8 | **AI Insights Feed** | AI-generated tips tailored to the user's specific financial data |
| 9 | **Savings Rate Gauge** | Progress bar showing savings % toward a target |
| 10 | **Spending Trend Indicator** | Month-over-month badge on the spending chart |

---

## Getting Started

### Prerequisites
- Python 3.13+
- Node 20+
- LM Studio (optional, for local AI)

### Backend

```bash
cd backend
cp .env.example .env
# Add your ANTHROPIC_API_KEY or set ACTIVE_AGENT=lm_studio
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

### Data Toggle

```bash
# frontend/.env
NUXT_PUBLIC_USE_DUMMY_DATA=true   # demo mode with dummy data
NUXT_PUBLIC_USE_DUMMY_DATA=false  # live mode (requires Supabase setup)
```

---

## Project Structure

```
AscendFi_VandyHacks_12/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent interface + implementations
│   │   ├── models/          # Pydantic data models
│   │   ├── routers/         # FastAPI route handlers
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    └── app/
        ├── assets/css/      # Design tokens (CSS custom properties)
        ├── components/
        │   ├── charts/      # Reusable Chart.js wrappers
        │   └── ui/          # StatCard, RiskGauge, etc.
        ├── composables/     # useFinancialData (dummy ↔ Supabase toggle)
        ├── data/            # Dummy financial data
        ├── layouts/         # App shell + sidebar
        └── pages/           # Dashboard + Chat
```

---

## Team

Built at VandyHacks 12.
