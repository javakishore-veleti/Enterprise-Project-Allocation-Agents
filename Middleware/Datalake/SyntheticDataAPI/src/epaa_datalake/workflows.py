"""Workflow registry + execution-history service (WfDef / WfExecution).

Backs the admin portal's Data Management views: the per-type workflow dropdown
(WfDef) and the paginated execution History (WfExecution).
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import func, or_, select

from .db import session_scope
from .models import WfDef, WfExecution

PAGE_SIZE = 15


def ensure_wf_def(name: str, engine_ref: str, wf_type: str,
                  description: str = "", wf_engine: str = "Apache Airflow") -> str:
    """Upsert a workflow definition by engine_ref; return its id."""
    with session_scope() as s:
        wf = s.scalar(select(WfDef).where(WfDef.engine_ref == engine_ref))
        if wf is None:
            wf = WfDef(name=name, description=description, status="active",
                       wf_engine=wf_engine, engine_ref=engine_ref, wf_type=wf_type)
            s.add(wf)
            s.flush()
        return wf.id


def start_execution(wf_def_id: str, configs: dict, engine_run_id: str | None,
                    engine: str = "Apache Airflow") -> str:
    with session_scope() as s:
        ex = WfExecution(
            wf_def_id=wf_def_id, exec_status="running",
            exec_started_at=dt.datetime.now(dt.UTC), exec_configs=configs,
            exec_engine=engine, engine_run_id=engine_run_id,
        )
        s.add(ex)
        s.flush()
        return ex.id


def complete_execution(exec_id: str, status: str, results: dict | None = None) -> None:
    with session_scope() as s:
        ex = s.get(WfExecution, exec_id)
        if ex:
            ex.exec_status = status
            ex.exec_completed_at = dt.datetime.now(dt.UTC)
            ex.exec_results = results


def list_workflows(wf_type: str | None = None) -> list[dict]:
    with session_scope() as s:
        stmt = select(WfDef).where(WfDef.status == "active")
        if wf_type:
            stmt = stmt.where(WfDef.wf_type == wf_type)
        return [
            {"id": w.id, "name": w.name, "description": w.description,
             "wf_engine": w.wf_engine, "engine_ref": w.engine_ref, "wf_type": w.wf_type}
            for w in s.scalars(stmt.order_by(WfDef.name)).all()
        ]


def list_executions(wf_def_id: str, page: int = 1, search: str | None = None) -> dict:
    """Paginated execution history (15/page), searchable across status/run-id."""
    page = max(page, 1)
    with session_scope() as s:
        base = select(WfExecution).where(WfExecution.wf_def_id == wf_def_id)
        if search:
            like = f"%{search}%"
            base = base.where(or_(WfExecution.exec_status.ilike(like),
                                  WfExecution.engine_run_id.ilike(like)))
        total = s.scalar(select(func.count()).select_from(base.subquery())) or 0
        rows = s.scalars(
            base.order_by(WfExecution.exec_created_dt.desc())
                .offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
        ).all()
        items = [
            {"id": e.id, "exec_status": e.exec_status, "exec_created_dt": e.exec_created_dt,
             "exec_started_at": e.exec_started_at, "exec_completed_at": e.exec_completed_at,
             "exec_engine": e.exec_engine, "engine_run_id": e.engine_run_id,
             "exec_configs": e.exec_configs, "exec_results": e.exec_results}
            for e in rows
        ]
        return {"items": items, "page": page, "page_size": PAGE_SIZE, "total": total,
                "pages": (total + PAGE_SIZE - 1) // PAGE_SIZE}
