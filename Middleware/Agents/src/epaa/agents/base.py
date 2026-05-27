"""Shared agent context + base class."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PipelineContext:
    """Carried through the 6-agent pipeline; each agent reads/augments it."""

    project_id: str
    project: Any = None                 # epaa_datalake.models.Project
    brief: Any = None                   # epaa_datalake.models.ProjectBrief
    parsed: dict = field(default_factory=dict)        # Requirement Parsing output
    candidates: list[dict] = field(default_factory=list)   # Skill Matching output
    available: list[dict] = field(default_factory=list)    # Availability output
    assignments: list[dict] = field(default_factory=list)  # Assignment output
    notifications: int = 0              # Communication output
    report: dict = field(default_factory=dict)        # Reporting output
    metrics: dict = field(default_factory=dict)


class BaseAgent:
    """An agent: reads/writes the DB through `session`, augments `ctx`,
    returns a JSON-serialisable output dict (persisted as the step output)."""

    name: str = "agent"

    def run(self, session, ctx: PipelineContext) -> dict:  # pragma: no cover - interface
        raise NotImplementedError
