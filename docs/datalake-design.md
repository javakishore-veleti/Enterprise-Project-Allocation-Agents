# Datalake & Vector Knowledge Base — current reality vs. target design

## Current reality (what's built today)

What the repo calls the **Datalake** is, today, a **Synthetic Data Service** — a
demo data generator, *not* a data lake:

- **No object/file storage** (no S3/MinIO), **no separate database**, **no dedicated
  vector DB**. The only store is **Postgres + pgvector**.
- The "vector DB" = two `pgvector` columns (`employees.profile_embedding`,
  `project_briefs.requirements_embedding`), populated from **synthetic** text
  (Faker, optionally LLM-rewritten) — there is **no external knowledge base**.
- One Airflow DAG (`synthetic_data_gen`) does generate → embed → load. **No
  daily/incremental** refresh; re-running does a full idempotent regenerate.
- Admin portal → Data Management → *Initiate Execution* triggers that one DAG.

This is sufficient to exercise the paper's agents, but it is not a knowledge-base
ingestion pipeline. The draw.io **"Datalake & Vector KB (Target)"** tab and the
plan below describe the real thing.

## Target design (proposed — see DevelopmentPlan M11; not built)

```
sources ──► ingestion (Airflow) ──► object storage ──► embedding ──► vector DB ──► agents
            initial · daily · incr.   S3/MinIO          Airflow        pgvector/    (Skill-
                                       raw + curated     Titan/HF       Qdrant       Matching)
```

### Sources for the knowledge base
- HR / HRIS system (employee records, roles, performance)
- CVs / résumés, certifications (PDF/DOCX)
- Past project documents, statements of work, retrospectives
- Skills catalog / taxonomy (system of record)

### How it's ingested
- **Object storage (S3 / MinIO)** is the datalake: a **raw zone** (source files
  as-is) and a **curated zone** (cleaned/normalised text + metadata).
- **Ingestion is Airflow-orchestrated**, in three modes:
  - **Initial (backfill):** one-off full load of all sources → curated → embed → vector DB.
  - **Daily (batch):** scheduled DAG picks up new/changed source files.
  - **Incremental (CDC/event):** on source change (e.g. a new CV, an HR update),
    re-embed just the affected records (upsert by stable key).
- **Embedding** runs as an Airflow task (Bedrock Titan v2, or HF MiniLM) over the
  curated text; vectors are **upserted** into the vector DB.

### Vector DB choice
- **pgvector** (stay on Postgres — simplest, already used) **or** **Qdrant**
  (dedicated, scales independently — already scaffolded under
  `DevOps/Local/VectorDBs/Qdrant`). A `VECTOR_BACKEND` switch selects it.

### Who triggers what
- The **Admin portal → Data Management** initiates **initial** and **incremental**
  builds (the same workflow-dropdown + Initiate/History UX already built); the
  **daily** build is an Airflow schedule.
- **Airflow manages the vector-DB lifecycle** (build, refresh, re-embed) — not just
  one generate step.

### How the agents use it
- The **Skill-Matching Agent** queries the vector DB for semantic retrieval of
  candidate employees against a parsed brief — exactly today's pgvector path,
  but over a *real* embedded knowledge base instead of synthetic data.

> This is a documented design only. Implementing it is tracked as **M11** in
> `DevelopmentPlan.md`.
