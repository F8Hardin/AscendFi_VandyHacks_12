from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Financial Recovery AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix="/api")


@api.get("/health")
async def api_health():
    return {"status": "ok"}


app.include_router(api)


@app.get("/health")
async def health():
    """Same as /api/health — kept for simple probes and older scripts."""
    return {"status": "ok"}
