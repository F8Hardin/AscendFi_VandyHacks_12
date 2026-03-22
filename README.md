# AscendFi — VandyHacks 12

> AI-powered financial recovery platform that helps users predict risk, eliminate debt, understand spending behavior, and build autonomous finance plans.

---

## Overview

AscendFi is a full-stack web application built for VandyHacks 12. A **Nuxt 4** frontend talks to a **Node.js backend** (sessions, routing, Docker orchestration) and **Python agent containers** (streaming LLM chat). An optional **FastAPI** service in `backend_agent/api` holds shared models and can grow into prediction and planning APIs.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Nuxt 4, Vue 3, Tailwind CSS, Chart.js |
| Backend | Node.js, Express (agent sessions + chat proxy) |
| Backend agent | Python 3.11+ (Dockerized Uvicorn agent; optional FastAPI in `backend_agent/api`) |
| AI | Anthropic Claude / LM Studio (OpenAI-compatible) |
| Auth / DB | Supabase (via **Node `backend`**, `@supabase/supabase-js`) |

---

## How services connect

| From | To | Purpose |
|------|-----|--------|
| **Browser** (`localhost:3000`) | **Nuxt** | UI; auth + DB via **Node backend** cookies; Turnstile → Nuxt `/api/turnstile` |
| **Browser** | **Node `backend`** (`NUXT_PUBLIC_AGENT_BASE`, default `:3001`) | `POST /agent/session`, `POST /agent/chat/:id` (SSE) |
| **Node `backend`** | **Docker agent** (`backend_agent/container`) | Starts one container per session; proxies `/chat/stream` to dynamic `localhost:8100–8200` |
| **Agent container** | **LM Studio** (host) | `LM_STUDIO_*` env from `backend/.env` at container create time |
| **Agent container** | **FastAPI** (optional, `:8000`) | `BACKEND_URL` / `AGENT_BACKEND_URL` for future tool calls |
| **Browser / future composables** | **FastAPI** (`NUXT_PUBLIC_API_BASE`, default `…/api`) | REST + `/api/health`; Swagger at `/docs` |

Chat requests include **financial `context`** when the user is logged in and dashboard data exists (dummy or future Supabase), matching `ChatRequest` in the Python agent.

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

## Backend agent — container contract

The **Node `backend`** runs each chat session in its own Docker container (image built from `backend_agent/container`). To swap in a custom agent, replace `backend_agent/container/app/main.py` (or the whole `app/` package) with any HTTP server that implements this contract:

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
The Node backend polls this before routing traffic to the container. Return `200` once ready.

---

## Roadmap: FastAPI + pluggable agents

Shared Pydantic types live under `backend_agent/api/app/models/`. The **FastAPI** app (`backend_agent/api`) is the natural place to add REST routes (risk, debt, spending, agent registry) and to match the feature table below. The **container** under `backend_agent/container` focuses on **streaming chat** (`/chat/stream`) and can call into that API via `BACKEND_URL`.

Planned shape (not all implemented yet):

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

When those routes exist, interactive docs will be at `http://localhost:8000/docs` with `uvicorn` running from `backend_agent/api`.

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
- Python 3.11+ (agent container + optional FastAPI)
- Node 20+
- Docker (for per-session agent containers)
- LM Studio (optional, for local AI)

### 1. Backend (Node.js) — port `3001`

```bash
cd backend
cp .env.example .env
npm install
npm run dev
```

Build the agent image first (step 3) or set `AGENT_IMAGE` to your tag.

### 2. Backend agent — FastAPI (optional) — port `8000`

```bash
cd backend_agent/api
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Backend agent — Docker image

```bash
cd backend_agent/container
docker build -t ascendfi-backend-agent:latest .
```

Match the tag to `AGENT_IMAGE` in `backend/.env`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`

### Data toggle

```bash
# frontend/.env
NUXT_PUBLIC_USE_DUMMY_DATA=true   # demo dashboard data (no DB reads)
NUXT_PUBLIC_USE_DUMMY_DATA=false  # live dashboard from GET /api/finance/dashboard (needs Supabase + schema)
NUXT_PUBLIC_AGENT_BASE=http://localhost:3001   # same origin as Node backend (auth cookies)
```

**Supabase:** add `SUPABASE_URL` and `SUPABASE_ANON_KEY` to **`backend/.env`** (not the Nuxt app). In the Supabase dashboard, set **Site URL** to `http://localhost:3000` and add **Redirect URL** `http://localhost:3000/confirm` for email confirmation.

---

## Project structure

```
AscendFi_VandyHacks_12/
├── backend/                 # Node.js — Express, session + chat proxy, Docker orchestration
│   ├── src/
│   └── package.json
├── backend_agent/           # Python — agent container + optional FastAPI
│   ├── container/           # Dockerized Uvicorn agent (/chat/stream, /health)
│   └── api/                 # FastAPI + Pydantic models (extend for REST features)
├── frontend/                # Nuxt 4 app
│   └── app/
│       ├── assets/css/
│       ├── components/
│       ├── composables/
│       ├── data/
│       ├── layouts/
│       └── pages/
└── supabase/                # SQL schema (profiles, financial tables, RLS)
```

---

## Team

Built at VandyHacks 12.
