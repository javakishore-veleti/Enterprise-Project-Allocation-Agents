"""Run Alembic migrations programmatically (called on app startup)."""
from __future__ import annotations

import logging
from pathlib import Path

from alembic import command
from alembic.config import Config

log = logging.getLogger(__name__)


def _alembic_config() -> Config:
    migrations_dir = Path(__file__).resolve().parent / "migrations"
    cfg = Config()
    cfg.set_main_option("script_location", str(migrations_dir))
    return cfg


def run_migrations() -> None:
    """Apply all pending migrations (`alembic upgrade head`)."""
    log.info("Applying database migrations (upgrade head)…")
    command.upgrade(_alembic_config(), "head")
    log.info("Migrations applied.")
