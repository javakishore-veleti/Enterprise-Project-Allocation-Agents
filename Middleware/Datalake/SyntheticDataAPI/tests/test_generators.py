"""Offline tests for the generators (no DB, no AWS)."""
from __future__ import annotations

from epaa_datalake.generators import embeddings, text
from epaa_datalake.generators.structured import GenSpec, generate_dataset


def test_dataset_is_deterministic_per_seed():
    a = generate_dataset(GenSpec(num_employees=10, num_projects=5, seed=1))
    b = generate_dataset(GenSpec(num_employees=10, num_projects=5, seed=1))
    assert [e.full_name for e in a.employees] == [e.full_name for e in b.employees]
    assert len(a.employees) == 10 and len(a.projects) == 5


def test_employees_have_skills_and_valid_states():
    ds = generate_dataset(GenSpec(num_employees=20, num_projects=5, seed=2))
    for e in ds.employees:
        assert e.skills, "every employee should have at least one skill"
        assert e.availability_state in {"available", "partially_occupied", "unavailable"}
        assert 0 <= e.performance_score <= 100


def test_text_templates_mention_key_fields():
    ds = generate_dataset(GenSpec(num_employees=3, num_projects=3, seed=3))
    emp = ds.employees[0]
    bio = text.profile_text(emp, use_llm=False)
    assert emp.full_name in bio and emp.seniority in bio
    brief = text.brief_text(ds.projects[0], use_llm=False)
    assert ds.projects[0].client_name in brief


def test_hash_embeddings_dim_and_normalised():
    vecs = embeddings.embed_texts(["hello world", "another"])  # provider falls back to hash offline
    assert len(vecs) == 2
    assert all(len(v) == 1024 for v in vecs)
    norm = sum(x * x for x in vecs[0]) ** 0.5
    assert abs(norm - 1.0) < 1e-6
