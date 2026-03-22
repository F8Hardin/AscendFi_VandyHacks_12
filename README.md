# AscendFi — VandyHacks 12

[![AscendFi CI](https://github.com/F8Hardin/AscendFi_VandyHacks_12/actions/workflows/ci.yml/badge.svg)](https://github.com/F8Hardin/AscendFi_VandyHacks_12/actions/workflows/ci.yml)

> AI-powered personal finance platform that predicts risk, eliminates debt, tracks spending behavior, and builds autonomous finance plans — powered by a multi-agent Python system and a real-time Nuxt frontend.

---

## Table of Contents

- [What It Does](#what-it-does)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start (Recommended)](#quick-start-recommended)
- [Manual Setup — macOS / Linux](#manual-setup--macos--linux)
- [Manual Setup — Windows](#manual-setup--windows)
- [Mobile App (iOS & Android)](#mobile-app-ios--android)
- [Environment Variables](#environment-variables)
- [Supabase Setup (Auth + Database)](#supabase-setup-auth--database)
- [Running Without Supabase (Demo Mode)](#running-without-supabase-demo-mode)
- [API Keys](#api-keys)
- [Dashboard Pages](#dashboard-pages)
- [How the Services Connect](#how-the-services-connect)
- [CI / GitHub Actions](#ci--github-actions)
- [Troubleshooting](#troubleshooting)
- [Team](#team)

---

## What It Does

AscendFi is a full-stack AI financial platform with three dashboard tabs:

| Tab | What You Get |
|-----|-------------|
| **Checking & Spending** | AI risk chips (overdraft, missed payments, credit shift), spending donut, behavior insights panel, financial gains sparkline, debt paydown trajectory |
| **Debt & Investments** | Debt payoff accelerator (avalanche vs. snowball), stock watchlist with live prices, interactive charts |
| **Autonomous Finance** | AI behavior profile, AI-recommended next steps, paycheck split, emergency fund tracker, sinking fund goals |

The **Python multi-agent system** (`Hackathon/`) runs as a FastAPI server and powers all AI features: risk prediction, debt optimization, behavioral analysis, and a conversational advisor (ARIA) accessible via the Chat page.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Nuxt 4, Vue 3, Tailwind CSS, Chart.js, lightweight-charts v5 |
| Node Backend | Node.js 20+, Express (auth sessions, finance API proxy) |
| Python Agent | FastAPI, Uvicorn, multi-agent orchestration (Anthropic Claude, OpenAI) |
| AI Models | Anthropic Claude, OpenAI GPT, Google Gemini (configurable) |
| Auth / DB | Supabase (Postgres + Auth) |
| Market Data | stooq.com (free, no API key needed) |

---

## Project Structure

```
AscendFi_VandyHacks_12/
├── start-dev.sh             ← One-command launcher (macOS/Linux)
├── Hackathon/               ← Python multi-agent FastAPI server
│   ├── app/
│   │   └── main.py          ← FastAPI entry point (port 8000)
│   ├── agents/              ← Supervisor, Risk, Debt, Behaviour, Investment agents
│   ├── tools/               ← Financial calculators, market data, ML predictors
│   ├── memory/              ← Conversation store
│   ├── requirements.txt
│   └── .env                 ← Your API keys (never commit this file)
├── backend/                 ← Node.js Express server (port 3001)
│   ├── src/
│   └── .env
├── frontend/                ← Nuxt 4 app (port 3000)
│   ├── app/
│   │   ├── components/
│   │   ├── composables/
│   │   └── pages/
│   │       └── dashboard/   ← index.vue, autonomous.vue, debt.vue
│   ├── server/api/          ← Nuxt server routes (market data proxy)
│   └── .env
└── supabase/                ← SQL schema files
```

---

## Prerequisites

Install these before anything else.

### macOS

```bash
# 1. Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install Node.js 20+ and Python 3.11+
brew install node python@3.11

# 3. Verify
node --version    # should print v20+
python3 --version # should print 3.11+
npm --version
pip3 --version
```

### Windows

1. **Node.js 20+** — download the LTS installer from [nodejs.org](https://nodejs.org) and run it
2. **Python 3.11+** — download from [python.org](https://www.python.org/downloads/)
   - On the first install screen, **check "Add Python to PATH"** before clicking Install
3. **Git** — download from [git-scm.com](https://git-scm.com/download/win)

After installing, open **PowerShell** and verify:

```powershell
node --version    # v20+
python --version  # 3.11+
npm --version
pip --version
```

> All Windows commands below use **PowerShell**. Git Bash also works.

---

## Quick Start (Recommended)

The fastest way to get everything running is with the included launcher script.

### macOS / Linux

```bash
# 1. Clone the repo
git clone https://github.com/F8Hardin/AscendFi_VandyHacks_12.git
cd AscendFi_VandyHacks_12

# 2. Create your Hackathon .env with API keys
cat > Hackathon/.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
EOF

# 3. Create frontend and backend env files
cp frontend/.env.example frontend/.env
cp backend/.env.example backend/.env

# 4. Launch everything
chmod +x start-dev.sh
./start-dev.sh
```

Open **http://localhost:3000** in your browser.

The launcher automatically:
- Installs all Python, Node, and Nuxt dependencies
- Builds the Node backend (TypeScript → `dist/`) and Nuxt frontend
- Starts all three servers simultaneously
- Cleans up all servers when you press `Ctrl+C`

---

## Manual Setup — macOS / Linux

Use this if you want to run each service in a separate terminal tab.

### Step 1 — Clone

```bash
git clone https://github.com/F8Hardin/AscendFi_VandyHacks_12.git
cd AscendFi_VandyHacks_12
```

### Step 2 — Python Agent (port 8000)

```bash
cd Hackathon

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Create your .env with API keys
cat > .env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
EOF

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The agent is live at **http://localhost:8000**.
Swagger docs (API explorer) at **http://localhost:8000/docs**.

### Step 3 — Node.js Backend (port 3001)

Open a **new terminal tab**:

```bash
cd backend
cp .env.example .env
# Optional: add Supabase credentials to backend/.env

npm install
npm run build
npm start
```

### Step 4 — Nuxt Frontend (port 3000)

Open a **new terminal tab**:

```bash
cd frontend
cp .env.example .env

npm install
npm run dev   # hot-reload dev server
```

Open **http://localhost:3000**.

---

## Manual Setup — Windows

### Step 1 — Clone

```powershell
git clone https://github.com/F8Hardin/AscendFi_VandyHacks_12.git
cd AscendFi_VandyHacks_12
```

### Step 2 — Python Agent (port 8000)

```powershell
cd Hackathon

# Create virtual environment
python -m venv venv

# Activate the virtual environment
venv\Scripts\Activate.ps1
```

> If you see an execution policy error, run this first, then try activating again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

```powershell
# Install dependencies
pip install -r requirements.txt

# Create .env with your API keys
# Option A: Use Notepad
notepad .env
# Type the following, save, and close:
#   ANTHROPIC_API_KEY=sk-ant-your-key-here
#   OPENAI_API_KEY=sk-proj-your-key-here

# Option B: From PowerShell directly
@"
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-proj-your-key-here
"@ | Out-File -FilePath .env -Encoding utf8

# Start the FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 3 — Node.js Backend (port 3001)

Open a **new PowerShell window**:

```powershell
cd backend
copy .env.example .env
# Edit backend\.env if you want to add Supabase credentials

npm install
npm run build
npm start
```

### Step 4 — Nuxt Frontend (port 3000)

Open a **new PowerShell window**:

```powershell
cd frontend
copy .env.example .env

npm install
npm run dev
```

Open **http://localhost:3000**.

---

## Mobile App (iOS & Android)

The `mobile/` directory is a full **React Native + Expo** app that mirrors all five dashboard tabs of the web app. You scan a QR code from your terminal with the **Expo Go** app on your phone — no Xcode or Android Studio required for testing.

### What's included

| Screen | Description |
|--------|-------------|
| **Login / Sign up** | Supabase auth + "Continue with demo data" shortcut |
| **Dashboard** | AI risk chips, stat cards, spending pie chart, gains line chart, recent activity |
| **Debt** | Debt paydown trajectory chart, avalanche list, extra-payment accelerator |
| **Planner** | AI behavior profile, AI next steps, paycheck split pie, emergency fund tracker |
| **Invest** | Live stock watchlist (stooq.com), interactive price history charts, symbol search |
| **ARIA Chat** | Real-time streaming AI chat with the Python agent |

### Prerequisites (mobile)

| Tool | macOS | Windows |
|------|-------|---------|
| Node.js 20+ | `brew install node` | [nodejs.org](https://nodejs.org) |
| Expo CLI | `npm install -g expo-cli` | `npm install -g expo-cli` |
| **Expo Go app** | Install from App Store | Install from Google Play |

> Your phone and computer must be on the **same WiFi network**.

### Setup — macOS / Linux

```bash
cd mobile

# Install dependencies
npm install

# Copy env file and add Supabase credentials
cp .env.example .env
# Edit .env — add EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_ANON_KEY

# Start the Expo dev server
npm start
```

A **QR code** appears in your terminal. Open **Expo Go** on your phone and scan it. The app loads instantly over your local network.

### Setup — Windows

```powershell
cd mobile

npm install

copy .env.example .env
# Edit .env in Notepad — add Supabase credentials

npm start
```

A **QR code** appears in the terminal. Scan it with **Expo Go** on your phone.

> **Windows tip:** If you see a network error on your phone, press `w` in the terminal to switch to tunnel mode, which works through Expo's servers and bypasses WiFi restrictions:
> ```
> Press w to open in tunnel mode
> ```

### How the QR code works

When you run `npm start`, Expo:
1. Detects your machine's local IP address (e.g., `192.168.1.42`)
2. Encodes it into a QR code shown in the terminal
3. The **Expo Go** app on your phone scans it, connects to your machine over WiFi, and loads the app

The mobile app **automatically detects your machine's IP** — no manual configuration needed. All API calls (Python agent on port 8000) resolve to your dev machine's LAN address.

### Running the backend for live AI on mobile

The mobile app connects to the same Python agent as the web app. Start both before scanning:

**macOS / Linux (one command):**
```bash
# From the repo root
./start-dev.sh
# Then in mobile/: npm start
```

**Windows (three separate PowerShell windows):**
```powershell
# Window 1 — Python agent
cd Hackathon && venv\Scripts\Activate.ps1 && python -m uvicorn app.main:app --port 8000 --reload

# Window 2 — Node backend
cd backend && npm start

# Window 3 — Mobile
cd mobile && npm start
```

If the Python agent is offline, the app falls back to **demo data** automatically.

### Simulator / Emulator (no phone needed)

```bash
# iOS Simulator (macOS only — requires Xcode)
npm run ios

# Android Emulator (requires Android Studio)
npm run android
```

---

## Environment Variables

### `Hackathon/.env` — Python Agent

This file is **required for all AI features**. It is already in `.gitignore` — never commit it.

```env
ANTHROPIC_API_KEY=sk-ant-...   # Required for ARIA chat + AI dashboard
OPENAI_API_KEY=sk-proj-...     # Optional — fallback model
```

### `frontend/.env` — Nuxt App

```env
NUXT_PUBLIC_USE_DUMMY_DATA=true          # true = demo mode (no DB needed)
NUXT_PUBLIC_API_BASE=http://localhost:8000/api   # Python agent URL
NUXT_PUBLIC_AGENT_BASE=http://localhost:3001     # Node backend for chat

PORT=3000
```

### `backend/.env` — Node.js Backend

```env
PORT=3001
FRONTEND_URL=http://localhost:3000

# Supabase (required for auth + live user data)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Connects Node backend directly to Python agent (bypasses Docker)
DIRECT_AGENT_MODE=1
DIRECT_AGENT_PORT=8000
```

---

## Supabase Setup (Auth + Database)

Skip this section if you just want demo mode (`NUXT_PUBLIC_USE_DUMMY_DATA=true`).

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **Settings → API** and copy your **Project URL** and **anon public key**
3. Add them to `backend/.env`:
   ```env
   SUPABASE_URL=https://xxxxxxxxxxxx.supabase.co
   SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```
4. In the Supabase dashboard, go to **Authentication → URL Configuration**:
   - **Site URL:** `http://localhost:3000`
   - **Redirect URLs:** add `http://localhost:3000/confirm`
5. Open the **SQL Editor** in Supabase and run the SQL files from the `supabase/` folder

---

## Running Without Supabase (Demo Mode)

You can run the entire frontend with realistic pre-built data — no database, no API keys.

In `frontend/.env`:
```env
NUXT_PUBLIC_USE_DUMMY_DATA=true
```

All three dashboard tabs will show demo data. The Chat page and live AI analysis still require `ANTHROPIC_API_KEY` in `Hackathon/.env` and the Python agent running.

---

## API Keys

| Key | Where to Get | Required For |
|-----|-------------|--------------|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com/settings/keys) | ARIA chat, AI dashboard analysis |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | Optional AI fallback |
| Supabase credentials | [supabase.com](https://supabase.com) → Settings → API | Auth + live user data |

**Market data** (stock prices, charts) uses **stooq.com** — completely free, no account or key needed.

---

## Dashboard Pages

| URL | Page | Description |
|-----|------|-------------|
| `/` | Landing | Sign in / sign up |
| `/dashboard` | Checking & Spending | AI risk chips, spending breakdown, behavior insights, sparklines |
| `/dashboard/debt` | Debt & Investments | Debt payoff calculator, live stock watchlist + price charts |
| `/dashboard/autonomous` | Autonomous Finance | AI behavior profile, AI next steps, paycheck split, emergency fund |
| `/chat` | ARIA Chat | Streaming AI financial advisor |
| `/invest` | Invest | Market overview, stock/ETF search, interactive price history |

---

## How the Services Connect

```
Browser (localhost:3000)
    │
    ├──► Nuxt frontend (port 3000)
    │        │
    │        ├── /api/market/* ──────────── stooq.com (free stock data)
    │        └── useFinancialData() ──────► Node backend (port 3001)
    │                                            │
    │                                            ├── Supabase (auth + user profile)
    │                                            └── Python agent (port 8000)
    │                                                    │
    │                                                    └── Anthropic / OpenAI APIs
    │
    └──► Chat page ──► Node backend (port 3001) ──► Python /chat/stream (SSE)
```

All three services must be running for the full experience. You can run just the frontend in demo mode (`NUXT_PUBLIC_USE_DUMMY_DATA=true`) without Node or Python.

---

## CI / GitHub Actions

Every push and pull request to `master` automatically runs three parallel jobs on **fresh Ubuntu virtual machines** — so dependencies are always installed in a clean, conflict-free environment identical to what a new contributor would experience.

### What runs

| Job | VM | What it does |
|-----|----|-------------|
| **Python Agent — Install & Verify** | `ubuntu-latest` | Installs all `Hackathon/requirements.txt` packages (including `catboost`, `xgboost`, `fastapi`, etc.), then imports the FastAPI app and verifies all required routes are registered |
| **Node.js Backend — Install & Build** | `ubuntu-latest` | Runs `npm ci` + `npm run build` (TypeScript → `dist/`), verifies `dist/index.js` exists |
| **Nuxt Frontend — Install & Build** | `ubuntu-latest` | Runs `npm ci` + `npm run build` (Nuxt production build), verifies `.output/` exists |

### Workflow file

Located at `.github/workflows/ci.yml`. Each job:

- Spins up a **brand-new Ubuntu VM** — no state carries over between runs
- Uses **pip/npm caching** to keep re-runs fast
- Fails loudly if any install or build step breaks

### GitHub Secrets (optional)

The CI workflow can inject real API keys if you add them as GitHub repository secrets. Go to **Settings → Secrets and variables → Actions** and add:

| Secret name | Value |
|-------------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `OPENAI_API_KEY` | Your OpenAI API key |

If the secrets are not set, the Python import check still runs with placeholder values — all module imports are verified, but no live API calls are made.

### Viewing results

Go to the **Actions** tab on GitHub to see live logs for every job. The badge at the top of this README shows the current build status.

---

## Troubleshooting

### `uvicorn: command not found`
```bash
# Make sure your venv is active, then:
pip install uvicorn

# Or run as a Python module instead:
python3 -m uvicorn app.main:app --port 8000 --reload   # macOS/Linux
python -m uvicorn app.main:app --port 8000 --reload    # Windows
```

### `pip install` fails on `catboost` or `xgboost` (Windows)
These packages need C++ build tools. Install them from Microsoft:
```
https://visualstudio.microsoft.com/visual-cpp-build-tools/
```
Select "Desktop development with C++" during install, then retry `pip install -r requirements.txt`.

### Port already in use

**macOS / Linux:**
```bash
lsof -ti:8000 | xargs kill -9   # Python agent
lsof -ti:3001 | xargs kill -9   # Node backend
lsof -ti:3000 | xargs kill -9   # Nuxt frontend
```

**Windows (PowerShell):**
```powershell
# Find the PID using the port
netstat -ano | findstr :8000
# Then kill it (replace 1234 with actual PID)
taskkill /PID 1234 /F
```

### Dashboard shows "Demo data · start the Python agent for live AI"
This means the frontend can't reach the Python agent. Make sure:
1. You have `Hackathon/.env` with a valid `ANTHROPIC_API_KEY`
2. The Python agent is running on port 8000 (`uvicorn app.main:app --port 8000`)
3. `frontend/.env` has `NUXT_PUBLIC_API_BASE=http://localhost:8000/api`

### Frontend shows "Demo data" even after setting up Supabase
Set `NUXT_PUBLIC_USE_DUMMY_DATA=false` in `frontend/.env` and restart the frontend server. The app only reads live data when both Supabase and the Python agent are reachable.

### macOS: `./start-dev.sh: Permission denied`
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### Windows: PowerShell execution policy error when activating venv
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### `npm run build` fails in backend (TypeScript errors)
```bash
cd backend
npm install
npm run build
```
If it still fails, check that `node --version` is v20+.

### `npm run dev` fails on Windows with ENOENT / permission errors
Try running PowerShell as Administrator, or use Git Bash instead of PowerShell.

---

## Team

Built at **VandyHacks 12**.
