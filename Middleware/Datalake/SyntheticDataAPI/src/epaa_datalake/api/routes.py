"""Datalake API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Query

from .. import airflow_client, workflows
from ..config import get_settings
from ..generators.pipeline import run as run_pipeline
from ..generators.structured import GenSpec
from .schemas import (
    ExecutionPageResponse,
    GenerateRequest,
    GenerateResponse,
    RunStatusResponse,
    WorkflowListResponse,
)

log = logging.getLogger(__name__)
router = APIRouter()

SYNTHETIC_WF_TYPE = "synthetic-data"


def _synthetic_wf_def_id() -> str:
    s = get_settings()
    return workflows.ensure_wf_def(
        name="Synthetic Data Generation", engine_ref=s.synthetic_dag_id,
        wf_type=SYNTHETIC_WF_TYPE,
        description="Generate + load employees, projects, briefs and embeddings.",
    )


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/synthetic/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    conf = req.model_dump()
    wf_def_id = _synthetic_wf_def_id()

    if req.run_async:
        try:
            run = airflow_client.trigger_dag(conf)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"Could not reach Airflow: {exc}") from exc
        workflows.start_execution(wf_def_id, configs=conf, engine_run_id=run["dag_run_id"])
        return GenerateResponse(mode="async", dag_run_id=run["dag_run_id"], state=run["state"])

    exec_id = workflows.start_execution(wf_def_id, configs=conf, engine_run_id=None)
    spec = GenSpec(num_employees=req.num_employees, num_projects=req.num_projects,
                   seed=req.seed, use_llm=req.use_llm)
    summary = run_pipeline(spec, persist=True)
    workflows.complete_execution(exec_id, status="success", results=summary)
    return GenerateResponse(mode="sync", summary=summary)


@router.get("/synthetic/runs/{dag_run_id}", response_model=RunStatusResponse)
def run_status(dag_run_id: str) -> RunStatusResponse:
    try:
        run = airflow_client.get_run(dag_run_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Could not reach Airflow: {exc}") from exc
    return RunStatusResponse(dag_run_id=run["dag_run_id"], state=run["state"])


# --- Workflow registry + history (admin portal Data Management) ---

@router.get("/workflows", response_model=WorkflowListResponse)
def list_workflows(wf_type: str | None = Query(default=None)) -> WorkflowListResponse:
    return WorkflowListResponse(items=workflows.list_workflows(wf_type=wf_type))


@router.get("/workflows/{wf_def_id}/executions", response_model=ExecutionPageResponse)
def workflow_executions(
    wf_def_id: str,
    page: int = Query(default=1, ge=1),
    search: str | None = Query(default=None),
) -> ExecutionPageResponse:
    return ExecutionPageResponse(**workflows.list_executions(wf_def_id, page=page, search=search))
