"""Datalake API routes."""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from .. import airflow_client
from ..generators.pipeline import run as run_pipeline
from ..generators.structured import GenSpec
from .schemas import GenerateRequest, GenerateResponse, RunStatusResponse

log = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/synthetic/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    conf = req.model_dump()
    if req.run_async:
        try:
            run = airflow_client.trigger_dag(conf)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=f"Could not reach Airflow: {exc}") from exc
        return GenerateResponse(mode="async", dag_run_id=run["dag_run_id"], state=run["state"])

    spec = GenSpec(num_employees=req.num_employees, num_projects=req.num_projects,
                   seed=req.seed, use_llm=req.use_llm)
    summary = run_pipeline(spec, persist=True)
    return GenerateResponse(mode="sync", summary=summary)


@router.get("/synthetic/runs/{dag_run_id}", response_model=RunStatusResponse)
def run_status(dag_run_id: str) -> RunStatusResponse:
    try:
        run = airflow_client.get_run(dag_run_id)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Could not reach Airflow: {exc}") from exc
    return RunStatusResponse(dag_run_id=run["dag_run_id"], state=run["state"])
