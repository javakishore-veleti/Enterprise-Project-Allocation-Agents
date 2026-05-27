"""initial EPAA core schema

Baseline migration: builds the whole schema from the SQLAlchemy models
(``Base.metadata``). Subsequent changes get hand-written delta migrations.

Revision ID: 0001
Revises:
Create Date: 2026-05-26
"""
from __future__ import annotations

from alembic import op

from epaa_datalake.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgvector extension + schema are ensured in migrations/env.py before this runs.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
