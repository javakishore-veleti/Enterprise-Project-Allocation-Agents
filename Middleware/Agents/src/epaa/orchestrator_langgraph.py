"""v2 orchestrator — the 6-agent pipeline as a LangGraph graph.

Reuses the exact same agent classes as the custom orchestrator; only the
orchestration changes. Adds a conditional edge: if the Availability Checker
leaves no available candidates, skip Assignment + Communication and go straight
to Reporting. Selected via ORCHESTRATOR=langgraph (see runner.py). Requires the
`langgraph` extra.

Two entry points share one graph builder:
  - `run_allocation`        — `.invoke()`, returns the run summary (batch).
  - `run_allocation_stream` — `.stream(stream_mode="updates")`, *yields* one
    event per agent as it finishes (powers the Agent Monitor's live trace via SSE).
"""
from __future__ import annotations

import datetime as dt
import logging
import time
from collections.abc import Iterator
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
    agent: str
    seq: int
    output: dict


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


def _load(session, project_id: str) -> tuple[AgentRun, PipelineContext, float]:
    """Look up project+brief, create the run row, build the shared context."""
    t0 = time.perf_counter()
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
    ctx.metrics["run_id"] = run.id
    return run, ctx, t0


def _build_graph(session, run: AgentRun, ctx: PipelineContext, t0: float):
    """Compile the StateGraph. Each node runs its agent, persists an AgentStep,
    and returns its output in the state so `.stream()` can surface it live."""
    from langgraph.graph import END, START, StateGraph

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
            return {"last": agent.name, "agent": agent.name, "seq": seq["n"], "output": output}

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
    return graph.compile()


def _finalize(run: AgentRun, ctx: PipelineContext, t0: float) -> dict:
    elapsed = int((time.perf_counter() - t0) * 1000)
    ctx.metrics["allocation_time_ms"] = elapsed
    run.status = "success"
    run.finished_at = _now()
    run.allocation_time_ms = elapsed
    run.metrics = ctx.metrics
    return {
        "run_id": run.id,
        "project_id": run.project_id,
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


def run_allocation(project_id: str) -> dict:
    """Run the pipeline via LangGraph; same summary shape as the custom orchestrator."""
    with session_scope() as session:
        run, ctx, t0 = _load(session, project_id)
        _build_graph(session, run, ctx, t0).invoke({"last": "start"})
        return _finalize(run, ctx, t0)


def run_allocation_stream(project_id: str) -> Iterator[dict]:
    """Run the pipeline via LangGraph, yielding one event per agent as it
    finishes, then a final `done` event with the full summary. The DB session
    stays open for the life of the generator (commits when it is exhausted)."""
    with session_scope() as session:
        run, ctx, t0 = _load(session, project_id)
        app = _build_graph(session, run, ctx, t0)
        yield {"event": "start", "run_id": run.id, "project_id": project_id,
               "orchestrator": "langgraph"}
        for chunk in app.stream({"last": "start"}, stream_mode="updates"):
            # stream_mode="updates" → {node_name: state_returned_by_node}
            for _node, upd in chunk.items():
                yield {
                    "event": "step",
                    "sequence": upd.get("seq"),
                    "agent": upd.get("agent"),
                    "output": upd.get("output"),
                    "elapsed_ms": int((time.perf_counter() - t0) * 1000),
                }
        yield {"event": "done", "summary": _finalize(run, ctx, t0)}


__all__ = ["run_allocation", "run_allocation_stream", "get_run", "ProjectNotFound"]
