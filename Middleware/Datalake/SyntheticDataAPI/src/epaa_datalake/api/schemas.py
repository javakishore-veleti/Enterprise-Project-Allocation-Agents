"""Request/Response DTOs for the Datalake API (one Req/Resp pair per use case)."""
from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    num_employees: int = Field(60, ge=1, le=500)
    num_projects: int = Field(20, ge=1, le=200)
    seed: int = 42
    use_llm: bool = False
    # async (default) triggers the Airflow DAG; sync runs the pipeline inline.
    run_async: bool = True


class GenerateResponse(BaseModel):
    mode: str                      # "async" | "sync"
    dag_run_id: str | None = None  # set when async
    state: str | None = None
    summary: dict | None = None    # set when sync


class RunStatusResponse(BaseModel):
    dag_run_id: str
    state: str | None = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    wf_engine: str
    engine_ref: str | None = None
    wf_type: str | None = None


class WorkflowListResponse(BaseModel):
    items: list[WorkflowResponse]


class ExecutionItem(BaseModel):
    id: str
    exec_status: str
    exec_created_dt: dt.datetime | None = None
    exec_started_at: dt.datetime | None = None
    exec_completed_at: dt.datetime | None = None
    exec_engine: str
    engine_run_id: str | None = None
    exec_configs: dict | None = None
    exec_results: dict | None = None


class ExecutionPageResponse(BaseModel):
    items: list[ExecutionItem]
    page: int
    page_size: int
    total: int
    pages: int
