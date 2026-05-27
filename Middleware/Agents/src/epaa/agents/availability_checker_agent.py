"""Agent 3 — Availability Checker. DB-only; prevents over-allocation.

Drops candidates who are unavailable and annotates each surviving candidate with
an availability factor used later by the Assignment Agent.
"""
from __future__ import annotations

from ..config import AVAILABILITY_FACTORS
from .base import BaseAgent, PipelineContext


class AvailabilityCheckerAgent(BaseAgent):
    name = "availability_checker"

    def run(self, session, ctx: PipelineContext) -> dict:
        available = []
        dropped = 0
        for c in ctx.candidates:
            factor = AVAILABILITY_FACTORS.get(c["availability_state"], 0.0)
            if factor <= 0.0:
                dropped += 1
                continue
            available.append({**c, "availability_factor": factor})

        ctx.available = available
        ctx.metrics["candidates_evaluated"] = len(ctx.candidates)
        ctx.metrics["conflicts_avoided"] = dropped  # unavailable employees filtered out
        return {"available_count": len(available), "dropped_unavailable": dropped}
