"""Structured (relational) data generation with Faker — deterministic per seed."""
from __future__ import annotations

import datetime as dt
import random
from dataclasses import dataclass, field

from faker import Faker

from . import taxonomy as tax


@dataclass
class GenSpec:
    num_employees: int = 60
    num_projects: int = 20
    seed: int = 42
    use_llm: bool = False


@dataclass
class EmployeeRec:
    full_name: str
    title: str
    seniority: str
    years_experience: int
    performance_score: float
    availability_state: str
    capacity_hours_per_week: int
    skills: list[tuple[str, int, int]]  # (skill_name, proficiency, years)
    profile_text: str = ""


@dataclass
class ProjectRec:
    name: str
    client_name: str
    priority: str
    complexity: str
    duration_weeks: int
    required_headcount: int
    start_date: dt.date
    required_skills: list[str]
    brief_text: str = ""


@dataclass
class Dataset:
    employees: list[EmployeeRec] = field(default_factory=list)
    projects: list[ProjectRec] = field(default_factory=list)


def _rng(seed: int) -> tuple[Faker, random.Random]:
    fake = Faker()
    Faker.seed(seed)
    return fake, random.Random(seed)


def generate_employees(spec: GenSpec, fake: Faker, rnd: random.Random) -> list[EmployeeRec]:
    skills_pool = tax.all_skills()
    out: list[EmployeeRec] = []
    for _ in range(spec.num_employees):
        seniority = rnd.choice(tax.SENIORITY)
        lo, hi = tax.SENIORITY_YEARS[seniority]
        years = rnd.randint(lo, hi)
        n_skills = rnd.randint(3, 8)
        chosen = rnd.sample(skills_pool, k=min(n_skills, len(skills_pool)))
        emp_skills = [
            (name, rnd.randint(2, 5), max(1, min(years, rnd.randint(1, years or 1))))
            for name, _cat in chosen
        ]
        out.append(
            EmployeeRec(
                full_name=fake.name(),
                title=rnd.choice(tax.TITLES),
                seniority=seniority,
                years_experience=years,
                performance_score=round(rnd.uniform(55, 99), 1),
                availability_state=rnd.choices(
                    tax.AVAILABILITY_STATES, weights=[0.5, 0.3, 0.2]
                )[0],
                capacity_hours_per_week=rnd.choice([20, 30, 40, 40, 40]),
                skills=emp_skills,
            )
        )
    return out


def generate_projects(spec: GenSpec, fake: Faker, rnd: random.Random) -> list[ProjectRec]:
    skills_pool = [name for name, _ in tax.all_skills()]
    out: list[ProjectRec] = []
    today = dt.date.today()
    for _ in range(spec.num_projects):
        n_req = rnd.randint(3, 7)
        out.append(
            ProjectRec(
                name=f"{fake.bs().title()} Initiative",
                client_name=fake.company(),
                priority=rnd.choices(tax.PRIORITIES, weights=[0.2, 0.4, 0.3, 0.1])[0],
                complexity=rnd.choice(tax.COMPLEXITIES),
                duration_weeks=rnd.choice([4, 6, 8, 12, 16, 24]),
                required_headcount=rnd.randint(2, 6),
                start_date=today + dt.timedelta(days=rnd.randint(0, 60)),
                required_skills=rnd.sample(skills_pool, k=min(n_req, len(skills_pool))),
            )
        )
    return out


def generate_dataset(spec: GenSpec) -> Dataset:
    fake, rnd = _rng(spec.seed)
    return Dataset(
        employees=generate_employees(spec, fake, rnd),
        projects=generate_projects(spec, fake, rnd),
    )
