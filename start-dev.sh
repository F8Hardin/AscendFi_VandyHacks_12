#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# AscendFi — Full-stack dev launcher
#
# Each run:
#   - Installs / updates all dependencies
#   - Builds the Node.js backend (TypeScript → dist/)
#   - Builds the Nuxt frontend (nuxt build → .output/)
#   - Starts all three servers:
#       1. Python FastAPI agent   → http://localhost:8000
#       2. Node.js backend        → http://localhost:3001
#       3. Nuxt frontend          → http://localhost:3000
#
# Usage:
#   chmod +x start-dev.sh
#   ./start-dev.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HACKATHON_DIR="$SCRIPT_DIR/Hackathon"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

echo "═══════════════════════════════════════════"
echo "  AscendFi Dev Launcher"
echo "═══════════════════════════════════════════"

# ── 1. Python FastAPI — install deps ─────────────────────────────────────────
echo ""
echo "▶ [1/3] Setting up Python agent..."

PYTHON="python3"
PIP="pip3"
if [ -f "$HACKATHON_DIR/venv/bin/python" ]; then
  PYTHON="$HACKATHON_DIR/venv/bin/python"
  PIP="$HACKATHON_DIR/venv/bin/pip"
fi

echo "  Installing Python dependencies..."
"$PIP" install -r "$HACKATHON_DIR/requirements.txt" -q
echo "  Python deps ready."

# ── 2. Node.js backend — install + build ─────────────────────────────────────
echo ""
echo "▶ [2/3] Building Node.js backend..."

(
  cd "$BACKEND_DIR"
  echo "  npm install..."
  npm install --silent
  echo "  npm run build..."
  npm run build
)
echo "  Backend build complete."

# ── 3. Nuxt frontend — install + build ───────────────────────────────────────
echo ""
echo "▶ [3/3] Building Nuxt frontend..."

(
  cd "$FRONTEND_DIR"
  echo "  npm install..."
  npm install --silent
  echo "  nuxt build..."
  npm run build
)
echo "  Frontend build complete."

# ── Start all servers ─────────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  Starting servers…"
echo "═══════════════════════════════════════════"

# Python agent (--reload for live code changes)
echo ""
echo "▶ Python FastAPI agent → http://localhost:8000"
(cd "$HACKATHON_DIR" && "$PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
AGENT_PID=$!

# Node backend (serve the compiled dist/)
echo "▶ Node.js backend      → http://localhost:3001"
(cd "$BACKEND_DIR" && npm start) &
NODE_PID=$!

# Nuxt (serve the built .output/ — uses node server)
echo "▶ Nuxt frontend        → http://localhost:3000"
(cd "$FRONTEND_DIR" && PORT=3000 npm run preview) &
NUXT_PID=$!

echo ""
echo "═══════════════════════════════════════════"
echo "  All servers running."
echo ""
echo "  Python agent  →  http://localhost:8000"
echo "  Node backend  →  http://localhost:3001"
echo "  Frontend      →  http://localhost:3000"
echo ""
echo "  Press Ctrl+C to stop all servers."
echo "═══════════════════════════════════════════"

cleanup() {
  echo ""
  echo "Stopping all servers…"
  kill $AGENT_PID $NODE_PID $NUXT_PID 2>/dev/null
  wait 2>/dev/null
  echo "Done."
}

trap cleanup EXIT INT TERM
wait
