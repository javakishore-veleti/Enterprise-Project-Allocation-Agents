"""v2 orchestrator — the 6-agent pipeline as a LangGraph graph.

Reuses the exact same agent classes as the custom orchestrator; only the
orchestration changes. Adds a conditional edge: if the Availability Checker
leaves no available candidates, skip Assignment + Communication and go straight
to Reporting. Selected via ORCHESTRATOR=langgraph (see runner.py). Requires the
`langgraph` extra.
"""
from __future__ import annotations

import datetime as dt
import logging
import time
from typing import TypedDict

from sqlalchemy import select

from epaa_datalake.db import session_scope
from epaa_datalake.models import AgentRun, AgentStep, Project, ProjectBrief

from .agents import PIPELINE
from .agents.base import PipelineContext
from .orchestrator import ProjectNotFound, get_run  # reuse trace reader + error

log = logging.getLogger(__name__)


class GraphState(TypedDict, total=False):
    last: str


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def run_allocation(project_id: str) -> dict:
    """Run the pipeline via LangGraph; same summary shape as the custom orchestrator."""
    from langgraph.graph import END, START, StateGraph

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
        session.flush()

        ctx = PipelineContext(project_id=project_id, project=project, brief=brief)
        ctx.metrics["run_id"] = run.id
        seq = {"n": 0}

        def make_node(agent_cls):
            agent = agent_cls()

            def _node(_state: GraphState) -> GraphState:
                seq["n"] += 1
                ctx.metrics["allocation_time_ms"] = int((time.perf_counter() - t0) * 1000)
                output = agent.run(session, ctx)
                session.add(AgentStep(
                    run_id=run.id, agent_name=agent.name, sequence=seq["n"],
                    output=output, status="ok", started_at=_now(), finished_at=_now(),
                ))
                return {"last": agent.name}

            return _node

        graph = StateGraph(GraphState)
        for cls in PIPELINE:
            graph.add_node(cls.name, make_node(cls))

        graph.add_edge(START, "requirement_parsing")
        graph.add_edge("requirement_parsing", "skill_matching")
        graph.add_edge("skill_matching", "availability_checker")
        # conditional: no one available → skip straight to reporting
        graph.add_conditional_edges(
            "availability_checker",
            lambda _s: "assignment" if ctx.available else "reporting",
            {"assignment": "assignment", "reporting": "reporting"},
        )
        graph.add_edge("assignment", "communication")
        graph.add_edge("communication", "reporting")
        graph.add_edge("reporting", END)

        graph.compile().invoke({"last": "start"})

        elapsed = int((time.perf_counter() - t0) * 1000)
        ctx.metrics["allocation_time_ms"] = elapsed
        run.status = "success"
        run.finished_at = _now()
        run.allocation_time_ms = elapsed
        run.metrics = ctx.metrics

        return {
            "run_id": run.id,
            "project_id": project_id,
            "status": run.status,
            "allocation_time_ms": elapsed,
            "orchestrator": "langgraph",
            "assignments": [
                {"full_name": a["full_name"], "rank": a["rank"], "final_score": a["final_score"]}
                for a in ctx.assignments
            ],
            "metrics": ctx.metrics,
            "report": ctx.report.get("summary"),
        }


__all__ = ["run_allocation", "get_run", "ProjectNotFound"]
