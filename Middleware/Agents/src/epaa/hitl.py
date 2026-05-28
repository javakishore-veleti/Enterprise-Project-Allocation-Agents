"""Human-in-the-loop (HITL) two-phase allocation.

Phase 1 (`run_with_approval`): runs agents 1-4 (Requirement Parsing → Skill
Matching → Availability → Assignment) with `ctx.approval_required=True`, so the
Assignment Agent writes allocations as **"proposed"** instead of "assigned" and
*does not* fire Communication/Reporting. The run is parked as `awaiting_approval`.

Phase 2: a manager calls `approve(run_id)` or `reject(run_id)`.
  - approve → flip proposed→assigned, then run Communication (5) + Reporting (6).
  - reject  → flip proposed→rejected, run Reporting (6) with a rejected summary.

The same 6 agent classes are reused; nothing about the agents is HITL-aware
except the Assignment Agent honouring `ctx.approval_required`. Works under either
orchestrator and offline (heuristic LLM + hash embeddings).
"""
from __future__ import annotations

import datetime as dt
import logging
import time

from sqlalchemy import select

from epaa_datalake.db import session_scope
from epaa_datalake.models import (
    AgentRun, AgentStep, Allocation, Employee, Project, ProjectBrief,
)

from .agents import (
    AssignmentAgent, AvailabilityCheckerAgent, CommunicationAgent,
    ReportingAgent, RequirementParsingAgent, SkillMatchingAgent,
)
from .agents.base import PipelineContext
from .orchestrator import ProjectNotFound

log = logging.getLogger(__name__)

# Agents 1-4 run before the human gate; 5-6 run after approval.
_PHASE1 = [RequirementParsingAgent, SkillMatchingAgent,
           AvailabilityCheckerAgent, AssignmentAgent]
_COMM_SEQ, _REPORT_SEQ = 5, 6


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _step(run_id: str, agent, seq: int, output: dict) -> AgentStep:
    return AgentStep(run_id=run_id, agent_name=agent.name, sequence=seq,
                     output=output, status="ok",
                     started_at=_now(), finished_at=_now())


def _summary(run, ctx: PipelineContext) -> dict:
    return {
        "run_id": run.id,
        "project_id": run.project_id,
        "status": run.status,
        "orchestrator": "hitl",
        "allocation_time_ms": run.allocation_time_ms,
        "assignments": [
            {"full_name": a["full_name"], "rank": a["rank"], "final_score": a["final_score"]}
            for a in ctx.assignments
        ],
        "metrics": ctx.metrics,
        "report": ctx.report.get("summary"),
    }


def run_with_approval(project_id: str) -> dict:
    """Phase 1: run agents 1-4, park the run as `awaiting_approval`."""
    t0 = time.perf_counter()
    with session_scope() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ProjectNotFound(project_id)
        brief = session.scalar(select(ProjectBrief).where(ProjectBrief.project_id == project_id))
        if brief is None:
            raise ProjectNotFound(f"no brief for project {project_id}")

        run = AgentRun(project_id=project_id, status="running", started_at=_now())
        session.add(run)
        session.flush()  # get run.id

        ctx = PipelineContext(project_id=project_id, project=project, brief=brief)
        ctx.approval_required = True
        ctx.metrics["run_id"] = run.id

        try:
            for seq, agent_cls in enumerate(_PHASE1, start=1):
                agent = agent_cls()
                ctx.metrics["allocation_time_ms"] = int((time.perf_counter() - t0) * 1000)
                output = agent.run(session, ctx)
                session.add(_step(run.id, agent, seq, output))
        except Exception as exc:  # noqa: BLE001
            run.status = "failed"
            run.finished_at = _now()
            run.metrics = {**ctx.metrics, "error": str(exc)}
            raise

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        ctx.metrics["allocation_time_ms"] = elapsed_ms
        ctx.metrics["awaiting_approval"] = True
        run.status = "awaiting_approval"
        run.finished_at = _now()
        run.allocation_time_ms = elapsed_ms
        run.metrics = ctx.metrics
        log.info("run %s parked awaiting approval (%d proposed)", run.id, len(ctx.assignments))
        return _summary(run, ctx)


def _load_for_decision(session, run_id: str, want_status: str) -> tuple[AgentRun, Project, ProjectBrief]:
    run = session.get(AgentRun, run_id)
    if run is None:
        raise ProjectNotFound(f"no run {run_id}")
    if run.status != "awaiting_approval":
        raise ValueError(f"run {run_id} is '{run.status}', not awaiting approval")
    project = session.get(Project, run.project_id)
    brief = session.scalar(select(ProjectBrief).where(ProjectBrief.project_id == run.project_id))
    return run, project, brief


def _proposed_assignments(session, project_id: str) -> list[dict]:
    """Rebuild the assignment dicts the post-approval agents expect, from the
    persisted `proposed` allocation rows (highest final_score first)."""
    rows = session.scalars(
        select(Allocation).where(Allocation.project_id == project_id,
                                  Allocation.status == "proposed")
    ).all()
    rows.sort(key=lambda a: a.final_score or 0.0, reverse=True)
    out = []
    for rank, al in enumerate(rows, start=1):
        emp = session.get(Employee, al.employee_id)
        out.append({
            "employee_id": al.employee_id,
            "full_name": emp.full_name if emp else al.employee_id,
            "title": emp.title if emp else "",
            "relevance": al.relevance_score,
            "final_score": al.final_score,
            "rationale": al.rationale or "",
            "rank": rank,
            "_row": al,
        })
    return out


def approve(run_id: str) -> dict:
    """Phase 2 (approve): proposed→assigned, then Communication + Reporting."""
    with session_scope() as session:
        run, project, brief = _load_for_decision(session, run_id, "approve")
        proposed = _proposed_assignments(session, run.project_id)

        ctx = PipelineContext(project_id=run.project_id, project=project, brief=brief)
        ctx.metrics = dict(run.metrics or {})
        ctx.metrics["run_id"] = run.id
        ctx.assignments = proposed
        for a in proposed:
            a["_row"].status = "assigned"
            a["_row"].assigned_at = _now()
        session.flush()  # Communication Agent queries "assigned" rows

        comm = CommunicationAgent()
        session.add(_step(run.id, comm, _COMM_SEQ, comm.run(session, ctx)))
        ctx.metrics["approved"] = True
        ctx.metrics.pop("awaiting_approval", None)
        rep = ReportingAgent()
        session.add(_step(run.id, rep, _REPORT_SEQ, rep.run(session, ctx)))

        run.status = "success"
        run.finished_at = _now()
        run.metrics = ctx.metrics
        log.info("run %s approved (%d assigned)", run.id, len(proposed))
        return _summary(run, ctx)


def reject(run_id: str, reason: str = "") -> dict:
    """Phase 2 (reject): proposed→rejected, run Reporting with a rejected note."""
    with session_scope() as session:
        run, project, brief = _load_for_decision(session, run_id, "reject")
        proposed = _proposed_assignments(session, run.project_id)
        for a in proposed:
            a["_row"].status = "rejected"

        ctx = PipelineContext(project_id=run.project_id, project=project, brief=brief)
        ctx.metrics = dict(run.metrics or {})
        ctx.metrics["run_id"] = run.id
        ctx.metrics["approved"] = False
        ctx.metrics["rejected_reason"] = reason
        ctx.metrics["headcount_assigned"] = 0
        ctx.metrics.pop("awaiting_approval", None)
        ctx.assignments = []  # nobody assigned → Reporting states 0 assigned

        rep = ReportingAgent()
        session.add(_step(run.id, rep, _REPORT_SEQ, rep.run(session, ctx)))

        run.status = "rejected"
        run.finished_at = _now()
        run.metrics = ctx.metrics
        log.info("run %s rejected (%d proposals dropped)", run.id, len(proposed))
        return _summary(run, ctx)
