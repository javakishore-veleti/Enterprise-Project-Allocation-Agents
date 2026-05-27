"""Agent 2 — Skill Matching. Semantic similarity (pgvector) + skill overlap.

Ranks employees by a blend of cosine similarity (brief requirements_embedding vs
employee profile_embedding) and explicit required-skill overlap.
"""
from __future__ import annotations

from sqlalchemy import select

from epaa_datalake.models import Employee, EmployeeSkill, Skill

from ..config import get_settings
from .base import BaseAgent, PipelineContext

SEMANTIC_W = 0.7
OVERLAP_W = 0.3


def _skill_names_by_employee(session, employee_ids: list[str]) -> dict[str, set[str]]:
    if not employee_ids:
        return {}
    rows = session.execute(
        select(EmployeeSkill.employee_id, Skill.name)
        .join(Skill, Skill.id == EmployeeSkill.skill_id)
        .where(EmployeeSkill.employee_id.in_(employee_ids))
    ).all()
    out: dict[str, set[str]] = {}
    for emp_id, name in rows:
        out.setdefault(emp_id, set()).add(name)
    return out


class SkillMatchingAgent(BaseAgent):
    name = "skill_matching"

    def run(self, session, ctx: PipelineContext) -> dict:
        s = get_settings()
        required = {r.lower() for r in ctx.parsed.get("required_skills", [])}
        emb = ctx.brief.requirements_embedding

        # Semantic shortlist via pgvector cosine distance (if we have an embedding).
        if emb is not None:
            rows = session.execute(
                select(Employee, Employee.profile_embedding.cosine_distance(emb).label("dist"))
                .where(Employee.profile_embedding.is_not(None))
                .order_by("dist")
                .limit(s.candidate_top_k)
            ).all()
            shortlist = [(e, float(dist)) for e, dist in rows]
        else:
            shortlist = [(e, 1.0) for e in session.scalars(select(Employee).limit(s.candidate_top_k)).all()]

        skills_by_emp = _skill_names_by_employee(session, [e.id for e, _ in shortlist])

        candidates = []
        for emp, dist in shortlist:
            semantic = max(0.0, 1.0 - dist)  # cosine distance → similarity
            emp_skills = {n.lower() for n in skills_by_emp.get(emp.id, set())}
            overlap = len(required & emp_skills) / len(required) if required else 0.0
            relevance = round(SEMANTIC_W * semantic + OVERLAP_W * overlap, 4)
            candidates.append({
                "employee_id": emp.id,
                "full_name": emp.full_name,
                "title": emp.title,
                "seniority": emp.seniority,
                "availability_state": emp.availability_state,
                "semantic_similarity": round(semantic, 4),
                "skill_overlap": round(overlap, 4),
                "matched_skills": sorted(required & emp_skills),
                "relevance": relevance,
            })

        candidates.sort(key=lambda c: c["relevance"], reverse=True)
        ctx.candidates = candidates
        return {"required_skills": sorted(required), "candidate_count": len(candidates),
                "top": candidates[:5]}
