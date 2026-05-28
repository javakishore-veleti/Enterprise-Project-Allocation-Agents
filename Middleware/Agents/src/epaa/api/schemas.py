"""Request/Response DTOs for the Agents API (one Req/Resp pair per use case)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class RunAllocationRequest(BaseModel):
    project_id: str = Field(..., description="Project to allocate a team for")
    require_approval: bool = Field(
        False, description="If true, run agents 1-4 and park as 'awaiting_approval' "
                           "(allocations written as 'proposed') until a human approves.")


class ApprovalDecisionRequest(BaseModel):
    reason: str = Field("", description="Optional note recorded with the decision (esp. rejections)")


class AssignmentDTO(BaseModel):
    full_name: str
    rank: int
    final_score: float


class RunAllocationResponse(BaseModel):
    run_id: str
    project_id: str
    status: str
    allocation_time_ms: int
    assignments: list[AssignmentDTO]
    report: str | None = None
    metrics: dict
    orchestrator: str | None = None


class AgentStepDTO(BaseModel):
    sequence: int
    agent: str
    status: str
    output: dict | None = None


class AgentRunResponse(BaseModel):
    run_id: str
    project_id: str
    status: str
    allocation_time_ms: int | None = None
    metrics: dict | None = None
    steps: list[AgentStepDTO]


class ReportResponse(BaseModel):
    project_id: str
    run_id: str | None = None
    summary_text: str
    metrics: dict | None = None
