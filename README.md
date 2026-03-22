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

There are two runtime modes controlled by `DIRECT_AGENT_MODE` in `backend/.env`.

### Dev mode (`DIRECT_AGENT_MODE=1`) — no Docker required

```
Browser (port 3000)
    │
    │  page load / auth
    ▼
Nuxt frontend ──────────────────────────────────────── Supabase (auth + DB)
    │
    │  POST /agent/session
    │  POST /agent/chat/:id  (SSE)
    ▼
Node backend (port 3001)
    │  validates session, proxies SSE
    │
    │  POST /chat/stream  (SSE)
    ▼
Python Uvicorn agent (port 8080)          ← backend_agent/api/
    │  spawned by Node on startup via
    │  DIRECT_AGENT_PATH; all sessions
    │  share this single process
    │
    │  POST /v1/chat/completions  (SSE)
    ▼
LM Studio (port 1234)
    model: qwen/qwen3.5-9b
```

### Server mode (`DIRECT_AGENT_MODE=0`) — one Docker container per session

```
Browser (port 3000)
    │
    ▼
Nuxt frontend ──────────────────────────────────────── Supabase (auth + DB)
    │
    │  POST /agent/session
    │  POST /agent/chat/:id  (SSE)
    ▼
Node backend (port 3001)
    │  validates session, proxies SSE
    │  spins up / tears down containers
    │  via Docker / distrobox
    │
    │  POST /chat/stream  (SSE)
    ▼
Docker agent container (ports 8100–8200)  ← backend_agent/container/
    │  one container per user session
    │  (pool pre-warms up to POOL_DEFAULT_SIZE)
    │
    │  POST /v1/chat/completions  (SSE)
    ▼
LM Studio (host.docker.internal:1234)
    model: set via LM_STUDIO_MODEL env
```

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
- Python 3.11+
- Node 20+
- LM Studio with a model loaded (dev mode)
- Docker / distrobox (server mode only)

---

### Dev mode — no Docker

> Uses `DIRECT_AGENT_MODE=1`. Node spawns a single shared Uvicorn process. Fastest for local development.

**1. LM Studio** — open LM Studio, load a model (e.g. `qwen/qwen3.5-9b`), and start the local server on port 1234.

**2. Python agent** — install deps once:
```bash
cd backend_agent/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Create `backend_agent/api/.env` (gitignored):
```env
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=qwen/qwen3.5-9b
```

**3. Node backend** — port `3001`:
```bash
cd backend
cp .env.example .env   # then set DIRECT_AGENT_MODE=1, DIRECT_AGENT_PATH=../backend_agent/api
npm install
npm run dev
```
Node auto-starts the Uvicorn agent on startup. If you change agent code, kill port 8080 and restart Node.

**4. Frontend** — port `3000`:
```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

---

### Server mode — Docker per session

> Uses `DIRECT_AGENT_MODE=0` (or unset). Node spins up one Docker container per user session (pool pre-warms containers).

**1.** Build the agent image:
```bash
cd backend_agent/container
docker build -t ascendfi-agent:latest .
```

**2.** In `backend/.env` set:
```env
DIRECT_AGENT_MODE=0
AGENT_IMAGE=ascendfi-agent:latest
LM_STUDIO_BASE_URL=http://host.docker.internal:1234/v1
LM_STUDIO_MODEL=qwen/qwen3.5-9b
```

**3.** Start Node backend and frontend as above. Docker containers are managed automatically.

---

### Data toggle

```env
# frontend/.env
NUXT_PUBLIC_USE_DUMMY_DATA=true   # demo dashboard (no DB reads)
NUXT_PUBLIC_USE_DUMMY_DATA=false  # live data from Supabase
NUXT_PUBLIC_AGENT_BASE=http://localhost:3001
```

**Supabase:** add `SUPABASE_URL` and `SUPABASE_ANON_KEY` to **`backend/.env`**. In the Supabase dashboard set **Site URL** to `http://localhost:3000` and **Redirect URL** to `http://localhost:3000/confirm`.

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
