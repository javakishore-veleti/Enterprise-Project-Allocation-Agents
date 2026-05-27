"""FastAPI entrypoint for the Datalake SyntheticDataAPI.

On startup it applies DB migrations (Alembic upgrade head) so the schema is
always current — per the project convention that migrations auto-run on startup.
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..observability import setup_tracing
from ..startup import run_migrations
from .routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        run_migrations()
    except Exception as exc:  # noqa: BLE001 — log but don't crash if DB is briefly unavailable
        log.error("Startup migrations failed: %s", exc)
    yield


app = FastAPI(title="EPAA Datalake — SyntheticDataAPI", version="0.1.0", lifespan=lifespan)
setup_tracing(app, "datalake-api")
app.include_router(router)
