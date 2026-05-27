"""Selects the orchestrator implementation at runtime.

ORCHESTRATOR=custom (default) → the hand-rolled sequential pipeline (v1).
ORCHESTRATOR=langgraph        → the LangGraph graph (v2; requires the langgraph extra).

`get_run` is orchestrator-agnostic (reads agent_runs/agent_steps), so v1's is reused.
"""
from __future__ import annotations

import logging

from .config import get_settings
from .orchestrator import ProjectNotFound, get_run  # noqa: F401 (re-exported)

log = logging.getLogger(__name__)


def run_allocation(project_id: str) -> dict:
    if get_settings().orchestrator.lower() == "langgraph":
        try:
            from . import orchestrator_langgraph as impl
            return impl.run_allocation(project_id)
        except ImportError as exc:
            log.warning("langgraph not installed (%s); falling back to custom orchestrator.", exc)
    from . import orchestrator as impl
    return impl.run_allocation(project_id)
