# Backend agent (Python)

Python side of AscendFi: shared **Pydantic models**, optional **FastAPI** service, and the **Dockerized LLM agent** the Node backend launches per session.

## Layout

| Path | Role |
|------|------|
| `container/` | **Agent container** — Uvicorn app (`POST /chat/stream`, `GET /health`). Built as the Docker image referenced by `backend/.env` → `AGENT_IMAGE`. |
| `api/` | **REST API (optional)** — FastAPI + shared financial/chat models. Today exposes a minimal app (`/health`); extend here for prediction/debt/spending routes. |

## Build the agent image

```bash
cd container
docker build -t ascendfi-backend-agent:latest .
```

## Run the optional FastAPI service (port 8000)

Used by the agent container as `BACKEND_URL` for any server-side tools that call into your API.

```bash
cd api
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Environment

- `container/.env.example` — keys passed into the container (e.g. `ANTHROPIC_API_KEY`, `BACKEND_URL`).
- `api/.env.example` — FastAPI / local dev.
