"""Agent 4 — Assignment. Weighted ranking → persisted allocations.

final_score = w_rel·relevance + w_pri·priority + w_avail·availability_factor.
Picks the top `headcount` available candidates and writes Allocation rows.
"""
from __future__ import annotations

import datetime as dt

from epaa_datalake.models import Allocation

from ..config import PRIORITY_WEIGHTS, get_settings
from .base import BaseAgent, PipelineContext


class AssignmentAgent(BaseAgent):
    name = "assignment"

    def run(self, session, ctx: PipelineContext) -> dict:
        s = get_settings()
        priority = ctx.parsed.get("priority", ctx.project.priority)
        pri_w = PRIORITY_WEIGHTS.get(priority, 0.5)
        headcount = int(ctx.parsed.get("headcount", ctx.project.required_headcount) or 1)

        scored = []
        for c in ctx.available:
            final = (s.relevance_weight * c["relevance"]
                     + s.priority_weight * pri_w
                     + s.availability_weight * c["availability_factor"])
            scored.append({**c, "priority_weight": round(pri_w, 4), "final_score": round(final, 4)})
        scored.sort(key=lambda c: c["final_score"], reverse=True)

        chosen = scored[:headcount]
        # Human-in-the-loop: when approval is required the rows are written as
        # "proposed" (a manager approves/rejects before Communication fires).
        status = "proposed" if ctx.approval_required else "assigned"
        assigned_at = None if ctx.approval_required else dt.datetime.now(dt.UTC)
        assignments = []
        for rank, c in enumerate(chosen, start=1):
            rationale = (
                f"Rank {rank}: relevance {c['relevance']} (semantic {c['semantic_similarity']}, "
                f"skill overlap {c['skill_overlap']}, matched {c['matched_skills']}), "
                f"priority '{priority}' (w={pri_w}), availability {c['availability_state']}."
            )
            session.add(Allocation(
                project_id=ctx.project_id, employee_id=c["employee_id"],
                relevance_score=c["relevance"], priority_weight=pri_w,
                final_score=c["final_score"], status=status,
                rationale=rationale, assigned_at=assigned_at,
            ))
            assignments.append({**c, "rank": rank, "rationale": rationale})

        ctx.assignments = assignments
        ctx.metrics["headcount_requested"] = headcount
        ctx.metrics["headcount_assigned"] = len(assignments)
        ctx.metrics["avg_relevance"] = round(
            sum(a["relevance"] for a in assignments) / len(assignments), 4) if assignments else 0.0
        return {"assigned": [{"full_name": a["full_name"], "final_score": a["final_score"],
                              "rank": a["rank"]} for a in assignments]}
