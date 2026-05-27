"""Multi-agent orchestrator: runs the 6-agent pipeline for one project,
persisting a full trace (agent_runs + agent_steps) and the paper's metrics.
"""
from __future__ import annotations

import datetime as dt
import logging
import time

from sqlalchemy import select

from epaa_datalake.db import session_scope
from epaa_datalake.models import AgentRun, AgentStep, ProjectBrief, Project

from .agents import PIPELINE
from .agents.base import PipelineContext

log = logging.getLogger(__name__)


class ProjectNotFound(LookupError):
    pass


def run_allocation(project_id: str) -> dict:
    """Run the full pipeline for a project; returns a run summary."""
    t0 = time.perf_counter()
    with session_scope() as session:
        project = session.get(Project, project_id)
        if project is None:
            raise ProjectNotFound(project_id)
        brief = session.scalar(select(ProjectBrief).where(ProjectBrief.project_id == project_id))
        if brief is None:
            raise ProjectNotFound(f"no brief for project {project_id}")

        run = AgentRun(project_id=project_id, status="running",
                       started_at=dt.datetime.now(dt.UTC))
        session.add(run)
        session.flush()  # get run.id

        ctx = PipelineContext(project_id=project_id, project=project, brief=brief)
        ctx.metrics["run_id"] = run.id

        try:
            for seq, agent_cls in enumerate(PIPELINE, start=1):
                agent = agent_cls()
                s = time.perf_counter()
                # keep a running elapsed so late agents (e.g. Reporting) can cite it
                ctx.metrics["allocation_time_ms"] = int((time.perf_counter() - t0) * 1000)
                output = agent.run(session, ctx)
                session.add(AgentStep(
                    run_id=run.id, agent_name=agent.name, sequence=seq,
                    output=output, status="ok",
                    started_at=dt.datetime.now(dt.UTC),
                    finished_at=dt.datetime.now(dt.UTC),
                ))
                log.info("agent %s done in %.1f ms", agent.name, (time.perf_counter() - s) * 1000)
        except Exception as exc:  # noqa: BLE001
            run.status = "failed"
            run.finished_at = dt.datetime.now(dt.UTC)
            run.metrics = {**ctx.metrics, "error": str(exc)}
            raise

        elapsed_ms = int((time.perf_counter() - t0) * 1000)
        ctx.metrics["allocation_time_ms"] = elapsed_ms
        run.status = "success"
        run.finished_at = dt.datetime.now(dt.UTC)
        run.allocation_time_ms = elapsed_ms
        run.metrics = ctx.metrics

        return {
            "run_id": run.id,
            "project_id": project_id,
            "status": run.status,
            "allocation_time_ms": elapsed_ms,
            "assignments": [
                {"full_name": a["full_name"], "rank": a["rank"], "final_score": a["final_score"]}
                for a in ctx.assignments
            ],
            "metrics": ctx.metrics,
            "report": ctx.report.get("summary"),
        }


def get_run(run_id: str) -> dict | None:
    """Return a run with its ordered step trace."""
    with session_scope() as session:
        run = session.get(AgentRun, run_id)
        if run is None:
            return None
        steps = session.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id).order_by(AgentStep.sequence)
        ).all()
        return {
            "run_id": run.id, "project_id": run.project_id, "status": run.status,
            "allocation_time_ms": run.allocation_time_ms, "metrics": run.metrics,
            "steps": [{"sequence": st.sequence, "agent": st.agent_name,
                       "status": st.status, "output": st.output} for st in steps],
        }
