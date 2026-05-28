"""Agents API routes."""
from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy import select

from epaa_datalake.db import session_scope
from epaa_datalake.models import Report

from .. import hitl, orchestrator, runner
from .schemas import (
    AgentRunResponse, ApprovalDecisionRequest, ReportResponse,
    RunAllocationRequest, RunAllocationResponse,
)

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/allocations/run", response_model=RunAllocationResponse)
def run_allocation(req: RunAllocationRequest) -> RunAllocationResponse:
    try:
        if req.require_approval:
            result = hitl.run_with_approval(req.project_id)  # parks as awaiting_approval
        else:
            result = runner.run_allocation(req.project_id)
    except orchestrator.ProjectNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return RunAllocationResponse(**result)


@router.post("/allocations/{run_id}/approve", response_model=RunAllocationResponse)
def approve_allocation(run_id: str) -> RunAllocationResponse:
    """Human-in-the-loop: finalize a parked run (proposed → assigned, then notify + report)."""
    try:
        result = hitl.approve(run_id)
    except orchestrator.ProjectNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:  # not awaiting approval
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return RunAllocationResponse(**result)


@router.post("/allocations/{run_id}/reject", response_model=RunAllocationResponse)
def reject_allocation(run_id: str, req: ApprovalDecisionRequest | None = None) -> RunAllocationResponse:
    """Human-in-the-loop: discard a parked run's proposals (proposed → rejected)."""
    try:
        result = hitl.reject(run_id, reason=(req.reason if req else ""))
    except orchestrator.ProjectNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return RunAllocationResponse(**result)


@router.get("/allocations/stream/{project_id}")
def stream_allocation(project_id: str) -> StreamingResponse:
    """Server-Sent Events: run the LangGraph pipeline, emitting one event per
    agent as it finishes (`start` → `step`*N → `done`). Powers the Agent Monitor
    live trace. Requires the langgraph extra (emits an `error` event otherwise)."""
    from .. import orchestrator_langgraph

    def gen():
        try:
            for event in orchestrator_langgraph.run_allocation_stream(project_id):
                yield f"data: {json.dumps(event, default=str)}\n\n"
        except orchestrator.ProjectNotFound as exc:
            yield f"data: {json.dumps({'event': 'error', 'detail': str(exc)})}\n\n"
        except ImportError as exc:
            yield f"data: {json.dumps({'event': 'error', 'detail': f'langgraph not installed: {exc}'})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


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
