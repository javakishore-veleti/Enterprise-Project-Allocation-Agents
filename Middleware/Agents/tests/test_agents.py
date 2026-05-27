"""DB-free unit tests for agent logic (heuristic parse + availability filter)."""
from __future__ import annotations

from types import SimpleNamespace

from epaa.agents.availability_checker_agent import AvailabilityCheckerAgent
from epaa.agents.base import PipelineContext
from epaa.agents.requirement_parsing_agent import _heuristic


def test_requirement_parsing_heuristic_extracts_fields():
    project = SimpleNamespace(priority="medium", complexity="high",
                              duration_weeks=99, required_headcount=99)
    brief = ("Acme is launching the portal. We need a team of about 4 for roughly 12 weeks. "
             "This is a high-priority effort. Required skills: Java, AWS, FastAPI.")
    parsed = _heuristic(brief, project)
    assert parsed["duration_weeks"] == 12
    assert parsed["headcount"] == 4
    assert parsed["priority"] == "high"
    assert "Java" in parsed["required_skills"] and "AWS" in parsed["required_skills"]


def test_availability_checker_drops_unavailable():
    ctx = PipelineContext(project_id="p1")
    ctx.candidates = [
        {"employee_id": "a", "availability_state": "available", "relevance": 0.9,
         "full_name": "A", "title": "Eng", "seniority": "senior",
         "semantic_similarity": 0.9, "skill_overlap": 0.9, "matched_skills": []},
        {"employee_id": "b", "availability_state": "unavailable", "relevance": 0.8,
         "full_name": "B", "title": "Eng", "seniority": "mid",
         "semantic_similarity": 0.8, "skill_overlap": 0.8, "matched_skills": []},
    ]
    out = AvailabilityCheckerAgent().run(None, ctx)
    assert out["available_count"] == 1
    assert out["dropped_unavailable"] == 1
    assert ctx.available[0]["employee_id"] == "a"
    assert ctx.available[0]["availability_factor"] == 1.0
