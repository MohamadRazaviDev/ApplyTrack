"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from applytrack.api.router import api_router
from applytrack.core.config import settings
from applytrack.db.base import Base
from applytrack.db.session import engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup (for quick-start without Alembic)."""
    # Import all models so Base.metadata is populated
    import applytrack.db.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    log.info("Database tables ensured.")
    yield


app = FastAPI(
    title="ApplyTrack API",
    description="Open-source job-application tracker with AI-powered resume tailoring.",
    version="0.2.0",
    lifespan=lifespan,
)

# CORS — configurable via CORS_ORIGINS env var (comma-separated).
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "ai_mode": settings.ai_mode,
    }
