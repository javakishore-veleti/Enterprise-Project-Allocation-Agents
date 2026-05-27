"""Agents API routes."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from sqlalchemy import select

from epaa_datalake.db import session_scope
from epaa_datalake.models import Report

from .. import orchestrator, runner
from .schemas import AgentRunResponse, ReportResponse, RunAllocationRequest, RunAllocationResponse

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/allocations/run", response_model=RunAllocationResponse)
def run_allocation(req: RunAllocationRequest) -> RunAllocationResponse:
    try:
        result = runner.run_allocation(req.project_id)
    except orchestrator.ProjectNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunAllocationResponse(**result)


@router.get("/agent-runs/{run_id}", response_model=AgentRunResponse)
def get_agent_run(run_id: str) -> AgentRunResponse:
    run = orchestrator.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"run {run_id} not found")
    return AgentRunResponse(**run)


@router.get("/reports/{project_id}", response_model=ReportResponse)
def get_report(project_id: str) -> ReportResponse:
    with session_scope() as session:
        report = session.scalar(
            select(Report).where(Report.project_id == project_id).order_by(Report.created_at.desc())
        )
        if report is None:
            raise HTTPException(status_code=404, detail=f"no report for project {project_id}")
        metrics = json.loads(report.metrics_json) if report.metrics_json else None
        return ReportResponse(project_id=report.project_id, run_id=report.run_id,
                              summary_text=report.summary_text, metrics=metrics)
