"""FastAPI entrypoint for the Agents service.

The Datalake owns the schema (Alembic), so this service does NOT run migrations;
it reads employees/briefs and writes allocations/agent_runs/steps/reports.
"""
from __future__ import annotations

import logging

from fastapi import FastAPI

from .routes import router

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(title="EPAA Agents — MCP-AI orchestrator", version="0.1.0")
app.include_router(router)
