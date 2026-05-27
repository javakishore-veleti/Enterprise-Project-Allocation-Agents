"""Persist a generated dataset into Postgres."""
from __future__ import annotations

import datetime as dt
import random

from sqlalchemy import select

from ..db import session_scope
from ..models import (
    Allocation,
    Availability,
    Employee,
    EmployeeSkill,
    Project,
    ProjectBrief,
    Skill,
)
from .structured import Dataset


def _upsert_skills(session, dataset: Dataset) -> dict[str, str]:
    """Ensure every skill referenced exists; return name -> id."""
    from . import taxonomy as tax

    existing = {s.name: s.id for s in session.scalars(select(Skill)).all()}
    for name, category in tax.all_skills():
        if name not in existing:
            skill = Skill(name=name, category=category)
            session.add(skill)
            session.flush()
            existing[name] = skill.id
    return existing


def load(dataset: Dataset, emp_embeddings: list[list[float]], brief_embeddings: list[list[float]]) -> dict[str, int]:
    rnd = random.Random(1234)
    counts = {"skills": 0, "employees": 0, "employee_skills": 0, "projects": 0,
              "briefs": 0, "availability": 0, "allocations": 0}

    with session_scope() as session:
        skill_ids = _upsert_skills(session, dataset)
        counts["skills"] = len(skill_ids)

        employee_ids: list[str] = []
        for emp, emb in zip(dataset.employees, emp_embeddings, strict=True):
            e = Employee(
                full_name=emp.full_name, title=emp.title, seniority=emp.seniority,
                years_experience=emp.years_experience, performance_score=emp.performance_score,
                availability_state=emp.availability_state,
                capacity_hours_per_week=emp.capacity_hours_per_week,
                profile_text=emp.profile_text, profile_embedding=emb,
            )
            session.add(e)
            session.flush()
            employee_ids.append(e.id)
            counts["employees"] += 1
            for name, prof, years in emp.skills:
                if name in skill_ids:
                    session.add(EmployeeSkill(employee_id=e.id, skill_id=skill_ids[name],
                                              proficiency=prof, years=years))
                    counts["employee_skills"] += 1
            # Calendar bookings reflecting availability state.
            if emp.availability_state != "available":
                start = dt.date.today()
                session.add(Availability(
                    employee_id=e.id, start_date=start,
                    end_date=start + dt.timedelta(weeks=rnd.randint(2, 8)),
                    status="booked" if emp.availability_state == "unavailable" else "tentative",
                ))
                counts["availability"] += 1

        for proj, emb in zip(dataset.projects, brief_embeddings, strict=True):
            p = Project(
                name=proj.name, client_name=proj.client_name, priority=proj.priority,
                complexity=proj.complexity, duration_weeks=proj.duration_weeks,
                required_headcount=proj.required_headcount, start_date=proj.start_date,
            )
            session.add(p)
            session.flush()
            counts["projects"] += 1
            session.add(ProjectBrief(project_id=p.id, brief_text=proj.brief_text,
                                     requirements_embedding=emb))
            counts["briefs"] += 1
            # Seed a couple of historical allocations so Reports have a baseline.
            for emp_id in rnd.sample(employee_ids, k=min(rnd.randint(0, 2), len(employee_ids))):
                session.add(Allocation(
                    project_id=p.id, employee_id=emp_id,
                    relevance_score=round(rnd.uniform(0.4, 0.95), 3),
                    priority_weight=round(rnd.uniform(0.2, 1.0), 3),
                    final_score=round(rnd.uniform(0.4, 0.95), 3),
                    status="assigned", assigned_at=dt.datetime.now(dt.UTC),
                ))
                counts["allocations"] += 1

    return counts
