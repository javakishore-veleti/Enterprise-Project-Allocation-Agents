"""workflow registry + execution history (wf_def, wf_executions)

Delta migration. Guarded with an inspector check because the baseline 0001
builds the whole current model set via create_all — on a fresh DB the tables
already exist (skip); on a DB created before this revision they are created here.

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-26
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

from epaa_datalake.models import SCHEMA

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def _has(table: str) -> bool:
    return table in inspect(op.get_bind()).get_table_names(schema=SCHEMA)


def upgrade() -> None:
    if not _has("wf_def"):
        op.create_table(
            "wf_def",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True)),
            sa.Column("name", sa.String(150), nullable=False),
            sa.Column("description", sa.String(300)),
            sa.Column("status", sa.String(40), nullable=False, server_default="active"),
            sa.Column("wf_engine", sa.String(60), nullable=False, server_default="Apache Airflow"),
            sa.Column("engine_ref", sa.String(150)),
            sa.Column("wf_type", sa.String(80)),
            schema=SCHEMA,
        )
        op.create_index("ix_wf_def_name", "wf_def", ["name"], schema=SCHEMA)
        op.create_index("ix_wf_def_status", "wf_def", ["status"], schema=SCHEMA)
        op.create_index("ix_wf_def_engine_ref", "wf_def", ["engine_ref"], schema=SCHEMA)
        op.create_index("ix_wf_def_wf_type", "wf_def", ["wf_type"], schema=SCHEMA)

    if not _has("wf_executions"):
        op.create_table(
            "wf_executions",
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("created_at", sa.DateTime(timezone=True)),
            sa.Column("wf_def_id", sa.String(36),
                      sa.ForeignKey(f"{SCHEMA}.wf_def.id", ondelete="CASCADE"), nullable=False),
            sa.Column("exec_created_dt", sa.DateTime(timezone=True)),
            sa.Column("exec_status", sa.String(40), nullable=False, server_default="created"),
            sa.Column("exec_started_at", sa.DateTime(timezone=True)),
            sa.Column("exec_completed_at", sa.DateTime(timezone=True)),
            sa.Column("exec_configs", sa.JSON),
            sa.Column("exec_engine", sa.String(60), nullable=False, server_default="Apache Airflow"),
            sa.Column("exec_results", sa.JSON),
            sa.Column("engine_run_id", sa.String(200)),
            schema=SCHEMA,
        )
        op.create_index("ix_wf_exec_wf_def_id", "wf_executions", ["wf_def_id"], schema=SCHEMA)
        op.create_index("ix_wf_exec_status", "wf_executions", ["exec_status"], schema=SCHEMA)
        op.create_index("ix_wf_exec_created_dt", "wf_executions", ["exec_created_dt"], schema=SCHEMA)
        op.create_index("ix_wf_exec_engine_run_id", "wf_executions", ["engine_run_id"], schema=SCHEMA)


def downgrade() -> None:
    op.drop_table("wf_executions", schema=SCHEMA)
    op.drop_table("wf_def", schema=SCHEMA)
