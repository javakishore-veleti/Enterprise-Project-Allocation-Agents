"""Curated skill taxonomy and controlled vocabularies for generation."""
from __future__ import annotations

SKILLS: dict[str, list[str]] = {
    "language": ["Java", "Python", "TypeScript", "Go", "C#", "Kotlin", "SQL", "Rust"],
    "framework": ["Spring Boot", "FastAPI", "Angular", "React", "Django", "Quarkus", ".NET"],
    "cloud": ["AWS", "Azure", "GCP", "Kubernetes", "Terraform", "Docker", "Lambda"],
    "data": ["PostgreSQL", "Kafka", "Spark", "Airflow", "dbt", "Snowflake", "pgvector"],
    "ai_ml": ["LLMs", "RAG", "PyTorch", "Bedrock", "Embeddings", "Prompt Engineering"],
    "domain": ["Payments", "Healthcare", "Logistics", "E-commerce", "FinTech", "Telecom"],
    "soft": ["Leadership", "Mentoring", "Stakeholder Mgmt", "Agile", "Communication"],
}

SENIORITY = ["junior", "mid", "senior", "lead", "principal"]
SENIORITY_YEARS = {"junior": (0, 2), "mid": (3, 5), "senior": (6, 9), "lead": (9, 13), "principal": (12, 20)}

TITLES = [
    "Software Engineer", "Backend Engineer", "Frontend Engineer", "Full-Stack Engineer",
    "Data Engineer", "ML Engineer", "DevOps Engineer", "Solutions Architect",
    "Engineering Manager", "QA Engineer", "UX Designer", "Product Analyst",
]

AVAILABILITY_STATES = ["available", "partially_occupied", "unavailable"]
PRIORITIES = ["low", "medium", "high", "critical"]
COMPLEXITIES = ["low", "medium", "high"]


def all_skills() -> list[tuple[str, str]]:
    """Return (name, category) pairs for every skill."""
    return [(name, category) for category, names in SKILLS.items() for name in names]
