"""SQLAlchemy ORM models — the EPAA core schema.

Conventions (see CLAUDE.md §7):
  * All primary keys are UUID stored as String (VARCHAR(36)).
  * Embedding columns use pgvector. EMBEDDING_DIM must match the column size.

This module is the single source of truth for the schema; the baseline Alembic
migration creates it via ``Base.metadata``.
"""
from __future__ import annotations

import datetime as dt
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

EMBEDDING_DIM = 1024  # Titan v2; keep in sync with Settings.embedding_dim
SCHEMA = "epaa"


def _uuid() -> str:
    return str(uuid4())


def _now() -> dt.datetime:
    return dt.datetime.now(dt.UTC)


class Base(DeclarativeBase):
    metadata = __import__("sqlalchemy").MetaData(schema=SCHEMA)


class Pk:
    """Mixin: UUID-as-String primary key + created_at."""

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Skill(Pk, Base):
    __tablename__ = "skills"
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(60), index=True)


class Employee(Pk, Base):
    __tablename__ = "employees"
    full_name: Mapped[str] = mapped_column(String(160))
    title: Mapped[str] = mapped_column(String(120))
    seniority: Mapped[str] = mapped_column(String(40))  # junior|mid|senior|lead|principal
    years_experience: Mapped[int] = mapped_column(Integer)
    performance_score: Mapped[float] = mapped_column(Float)  # 0..100
    availability_state: Mapped[str] = mapped_column(String(40), index=True)
    capacity_hours_per_week: Mapped[int] = mapped_column(Integer, default=40)
    profile_text: Mapped[str] = mapped_column(Text)  # unstructured bio
    profile_embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    skills: Mapped[list["EmployeeSkill"]] = relationship(back_populates="employee")


class EmployeeSkill(Pk, Base):
    __tablename__ = "employee_skills"
    __table_args__ = (UniqueConstraint("employee_id", "skill_id", name="uq_emp_skill"),)
    employee_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.employees.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.skills.id", ondelete="CASCADE"), index=True)
    proficiency: Mapped[int] = mapped_column(Integer)  # 1..5
    years: Mapped[int] = mapped_column(Integer)

    employee: Mapped[Employee] = relationship(back_populates="skills")
    skill: Mapped[Skill] = relationship()


class Project(Pk, Base):
    __tablename__ = "projects"
    name: Mapped[str] = mapped_column(String(200))
    client_name: Mapped[str] = mapped_column(String(160))
    priority: Mapped[str] = mapped_column(String(20), index=True)  # low|medium|high|critical
    complexity: Mapped[str] = mapped_column(String(20))  # low|medium|high
    duration_weeks: Mapped[int] = mapped_column(Integer)
    required_headcount: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[dt.date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30), default="open", index=True)


class ProjectBrief(Pk, Base):
    __tablename__ = "project_briefs"
    project_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.projects.id", ondelete="CASCADE"), index=True)
    brief_text: Mapped[str] = mapped_column(Text)  # unstructured NL brief
    parsed_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # filled by Requirement Parsing Agent
    requirements_embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)


class Availability(Pk, Base):
    __tablename__ = "availability"
    employee_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.employees.id", ondelete="CASCADE"), index=True)
    start_date: Mapped[dt.date] = mapped_column(Date)
    end_date: Mapped[dt.date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(30))  # booked|tentative|pto
    project_id: Mapped[str | None] = mapped_column(ForeignKey(f"{SCHEMA}.projects.id", ondelete="SET NULL"), nullable=True)


class Allocation(Pk, Base):
    __tablename__ = "allocations"
    project_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.projects.id", ondelete="CASCADE"), index=True)
    employee_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.employees.id", ondelete="CASCADE"), index=True)
    relevance_score: Mapped[float] = mapped_column(Float, default=0.0)
    priority_weight: Mapped[float] = mapped_column(Float, default=0.0)
    final_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(30), default="proposed")  # proposed|assigned|rejected
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# --- Runtime tables (created now, populated by the agents in M3) ---

class AgentRun(Pk, Base):
    __tablename__ = "agent_runs"
    project_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.projects.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(30), default="running")
    started_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    allocation_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class AgentStep(Pk, Base):
    __tablename__ = "agent_steps"
    run_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.agent_runs.id", ondelete="CASCADE"), index=True)
    agent_name: Mapped[str] = mapped_column(String(60))
    sequence: Mapped[int] = mapped_column(Integer)
    input: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    output: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="ok")
    started_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Notification(Pk, Base):
    __tablename__ = "notifications"
    employee_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.employees.id", ondelete="CASCADE"), index=True)
    allocation_id: Mapped[str | None] = mapped_column(ForeignKey(f"{SCHEMA}.allocations.id", ondelete="SET NULL"), nullable=True)
    channel: Mapped[str] = mapped_column(String(30), default="log")
    subject: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="queued")


class Report(Pk, Base):
    __tablename__ = "reports"
    project_id: Mapped[str] = mapped_column(ForeignKey(f"{SCHEMA}.projects.id", ondelete="CASCADE"), index=True)
    run_id: Mapped[str | None] = mapped_column(ForeignKey(f"{SCHEMA}.agent_runs.id", ondelete="SET NULL"), nullable=True)
    summary_text: Mapped[str] = mapped_column(Text)
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
