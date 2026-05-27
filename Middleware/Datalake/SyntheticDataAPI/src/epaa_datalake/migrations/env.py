"""Alembic environment — online migrations against Postgres+pgvector."""
from __future__ import annotations

from alembic import context
from sqlalchemy import text

from epaa_datalake.config import get_settings
from epaa_datalake.db import engine
from epaa_datalake.models import SCHEMA, Base

target_metadata = Base.metadata


def _ensure_prereqs(connection) -> None:
    # pgvector extension + the application schema must exist before tables.
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))


def run_migrations_online() -> None:
    connectable = engine()
    with connectable.connect() as connection:
        _ensure_prereqs(connection)
        connection.commit()
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=SCHEMA,
            include_schemas=True,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


# Offline mode is unused (we always have a live DB); guard anyway.
if context.is_offline_mode():
    context.configure(url=get_settings().sqlalchemy_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
