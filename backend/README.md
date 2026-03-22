# Backend (Node.js)

Express service that fronts the product APIs for **agent sessions** and **streaming chat**. It spins up one Docker container per user session (Python agent in `../backend_agent/container`) and proxies `/agent/chat/*` to the right container port.

## Run locally

```bash
cp .env.example .env
# Set SUPABASE_URL + SUPABASE_ANON_KEY (same project as your app)
# Set AGENT_IMAGE to the tag you built from backend_agent/container
npm install
npm run dev
```

- Default URL: `http://localhost:3001`
- Health: `GET /health`
- **Auth (Supabase):** `POST /api/auth/sign-in`, `POST /api/auth/sign-up`, `POST /api/auth/sign-out`, `GET /api/auth/me`, `POST /api/auth/session` (email-confirm tokens → cookies)
- **Finance:** `GET /api/finance/dashboard` (requires session cookies; uses RLS with the user JWT)
- Frontend should set `NUXT_PUBLIC_AGENT_BASE` to this origin (see `frontend/nuxt.config.ts` and `frontend/.env.example`).
- `AGENT_BACKEND_URL` — base URL the **agent container** uses to reach FastAPI (default `http://host.docker.internal:8000`). Must match where `backend_agent/api` listens if the agent calls your API.
- `LM_STUDIO_BASE_URL` / `LM_STUDIO_MODEL` — forwarded into each new agent container.

## Requirements

- Docker (for per-session agent containers)
- Built image: from `backend_agent/container` (see that folder’s README)
