"""Request/Response DTOs for the Datalake API (one Req/Resp pair per use case)."""
from __future__ import annotations

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
