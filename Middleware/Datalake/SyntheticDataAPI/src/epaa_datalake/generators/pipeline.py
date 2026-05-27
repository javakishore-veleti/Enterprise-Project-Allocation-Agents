"""End-to-end generation pipeline: structured → text → embeddings → load."""
from __future__ import annotations

import logging

from ..config import get_settings
from . import embeddings, loader, text
from .structured import GenSpec, generate_dataset

log = logging.getLogger(__name__)


def run(spec: GenSpec, persist: bool = True, reset: bool = True) -> dict:
    """Generate a dataset and (optionally) load it into Postgres.

    ``reset`` (default) truncates the domain tables first so re-seeding is
    idempotent. Returns a summary dict with generated counts (and DB counts if
    persisted).
    """
    log.info("Generating dataset: %s employees, %s projects (seed=%s, use_llm=%s)",
             spec.num_employees, spec.num_projects, spec.seed, spec.use_llm)
    dataset = generate_dataset(spec)

    for emp in dataset.employees:
        emp.profile_text = text.profile_text(emp, use_llm=spec.use_llm)
    for proj in dataset.projects:
        proj.brief_text = text.brief_text(proj, use_llm=spec.use_llm)

    emp_emb = embeddings.embed_texts([e.profile_text for e in dataset.employees])
    brief_emb = embeddings.embed_texts([p.brief_text for p in dataset.projects])

    summary = {
        "generated": {"employees": len(dataset.employees), "projects": len(dataset.projects)},
        "embedding_provider": get_settings().embedding_provider,
        "use_llm": spec.use_llm,
        "persisted": False,
    }
    if persist:
        summary["counts"] = loader.load(dataset, emp_emb, brief_emb, reset=reset)
        summary["persisted"] = True
        summary["reset"] = reset
    return summary
