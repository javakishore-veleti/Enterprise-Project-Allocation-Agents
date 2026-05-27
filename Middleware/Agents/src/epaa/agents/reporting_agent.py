"""Agent 6 — Reporting. Managerial summary + metrics (powers the Reports page).

Summary text is written by the LLM when available, otherwise a clear template.
"""
from __future__ import annotations

from epaa_datalake.models import Report

from ..providers import llm
from .base import BaseAgent, PipelineContext

_SYSTEM = (
    "You are a staffing manager. Write a concise 3-4 sentence summary of an automated "
    "project allocation: who was assigned, why, and the efficiency outcome. Plain prose."
)


def _template_summary(ctx: PipelineContext) -> str:
    m = ctx.metrics
    names = ", ".join(a["full_name"] for a in ctx.assignments) or "no one (no available match)"
    return (
        f"Project \"{ctx.project.name}\" for {ctx.project.client_name}: assigned "
        f"{m.get('headcount_assigned', 0)}/{m.get('headcount_requested', 0)} requested — {names}. "
        f"Evaluated {m.get('candidates_evaluated', 0)} candidates, avoided "
        f"{m.get('conflicts_avoided', 0)} scheduling conflicts, average relevance "
        f"{m.get('avg_relevance', 0)}. Completed in {m.get('allocation_time_ms', 0)} ms."
    )


class ReportingAgent(BaseAgent):
    name = "reporting"

    def run(self, session, ctx: PipelineContext) -> dict:
        template = _template_summary(ctx)
        try:
            prompt = f"Allocation facts:\n{template}\n\nAssignments: {ctx.assignments}"
            summary = llm.complete(_SYSTEM, prompt)
            source = "llm"
        except llm.LLMUnavailable:
            summary, source = template, "template"

        report = Report(project_id=ctx.project_id, run_id=ctx.metrics.get("run_id"),
                        summary_text=summary, metrics=ctx.metrics)
        session.add(report)
        ctx.report = {"summary": summary, "source": source, "metrics": ctx.metrics}
        return ctx.report
