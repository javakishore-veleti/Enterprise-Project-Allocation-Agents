"""Agent 1 — Requirement Parsing. Free-text brief → structured requirements.

LLM path extracts JSON; heuristic fallback matches the skill taxonomy and a few
regexes, backfilling from the project row. Persists onto ``brief.parsed_requirements``.
"""
from __future__ import annotations

import re

from epaa_datalake.generators.taxonomy import all_skills

from ..providers import llm
from .base import BaseAgent, PipelineContext

_SYSTEM = (
    "You extract structured staffing requirements from an enterprise project brief. "
    "Return ONLY JSON with keys: required_skills (array of strings), priority "
    "(low|medium|high|critical), complexity (low|medium|high), duration_weeks (int), "
    "headcount (int)."
)
_SKILL_NAMES = [name for name, _ in all_skills()]


def _heuristic(brief_text: str, project) -> dict:
    text = brief_text.lower()
    skills = [s for s in _SKILL_NAMES if s.lower() in text]
    weeks = re.search(r"(\d+)\s*weeks", text)
    head = re.search(r"team of about\s*(\d+)", text)
    priority = next((p for p in ("critical", "high", "medium", "low") if p in text), project.priority)
    return {
        "required_skills": skills or [],
        "priority": priority,
        "complexity": project.complexity,
        "duration_weeks": int(weeks.group(1)) if weeks else project.duration_weeks,
        "headcount": int(head.group(1)) if head else project.required_headcount,
    }


class RequirementParsingAgent(BaseAgent):
    name = "requirement_parsing"

    def run(self, session, ctx: PipelineContext) -> dict:
        brief_text = ctx.brief.brief_text
        try:
            parsed = llm.complete_json(_SYSTEM, brief_text)
            # normalise / guard required fields
            parsed.setdefault("required_skills", [])
            parsed.setdefault("priority", ctx.project.priority)
            parsed.setdefault("complexity", ctx.project.complexity)
            parsed.setdefault("duration_weeks", ctx.project.duration_weeks)
            parsed.setdefault("headcount", ctx.project.required_headcount)
            source = "llm"
        except llm.LLMUnavailable:
            parsed = _heuristic(brief_text, ctx.project)
            source = "heuristic"

        ctx.parsed = parsed
        ctx.brief.parsed_requirements = parsed  # persisted on session commit
        return {"source": source, **parsed}
