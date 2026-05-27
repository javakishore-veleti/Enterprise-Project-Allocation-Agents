"""Hybrid unstructured-text generation.

Default: deterministic templates (offline, free, fast). With ``use_llm=True`` the
brief/bio is (re)written by Bedrock Claude for realism, falling back to the
template if Bedrock is unavailable.
"""
from __future__ import annotations

import json
import logging

from ..config import get_settings
from .structured import EmployeeRec, ProjectRec

log = logging.getLogger(__name__)


# --- Template generators (default) ---

def profile_template(emp: EmployeeRec) -> str:
    top = ", ".join(f"{n} (L{p})" for n, p, _ in sorted(emp.skills, key=lambda s: -s[1])[:5])
    return (
        f"{emp.full_name} is a {emp.seniority} {emp.title} with {emp.years_experience} years of "
        f"experience. Core strengths: {top}. Recent performance rating {emp.performance_score}/100. "
        f"Currently {emp.availability_state.replace('_', ' ')} with ~{emp.capacity_hours_per_week}h/week capacity."
    )


def brief_template(proj: ProjectRec) -> str:
    skills = ", ".join(proj.required_skills)
    return (
        f"{proj.client_name} is launching the \"{proj.name}\". We need a team of about "
        f"{proj.required_headcount} for roughly {proj.duration_weeks} weeks starting {proj.start_date:%b %Y}. "
        f"This is a {proj.priority}-priority, {proj.complexity}-complexity effort. "
        f"Required skills: {skills}. Looking for people who can hit the ground running."
    )


# --- Optional LLM rewrite (Bedrock Claude) ---

def _bedrock_rewrite(kind: str, seed_text: str) -> str | None:
    s = get_settings()
    try:
        import boto3  # lazy

        client = boto3.client("bedrock-runtime", region_name=s.aws_region)
        prompt = (
            f"Rewrite the following {kind} as a natural, realistic enterprise {kind} in 3-4 sentences. "
            f"Keep all skills, numbers, and priorities. Return only the prose.\n\n{seed_text}"
        )
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 400,
            "messages": [{"role": "user", "content": prompt}],
        }
        resp = client.invoke_model(modelId=s.bedrock_model_id, body=json.dumps(body))
        payload = json.loads(resp["body"].read())
        return payload["content"][0]["text"].strip()
    except Exception as exc:  # noqa: BLE001 — any failure → template fallback
        log.warning("Bedrock text rewrite failed (%s); using template.", exc)
        return None


def profile_text(emp: EmployeeRec, use_llm: bool = False) -> str:
    base = profile_template(emp)
    if use_llm and (rewritten := _bedrock_rewrite("employee bio", base)):
        return rewritten
    return base


def brief_text(proj: ProjectRec, use_llm: bool = False) -> str:
    base = brief_template(proj)
    if use_llm and (rewritten := _bedrock_rewrite("project brief", base)):
        return rewritten
    return base
