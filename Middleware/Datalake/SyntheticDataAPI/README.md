# SyntheticDataAPI

FastAPI service + importable generator package (`epaa_datalake`) that produces the
EPAA synthetic dataset: relational rows, unstructured text, and pgvector embeddings.

## What it generates

- **Relational:** employees, skills, employee_skills (M:N), projects, availability, seeded allocations
- **Unstructured text:** `project_briefs.brief_text`, `employees.profile_text`
- **Embeddings (pgvector, 1024-dim):** `employees.profile_embedding`, `project_briefs.requirements_embedding`

UUID-as-String primary keys throughout. Schema is created/updated by **Alembic**
(auto-run on startup).

## Run it

```bash
# Local (against Postgres from DevOps/Local/Postgres). Reads ../../../.env
pip install -e .

# apply migrations only
epaa-datalake migrate

# generate + load (offline: hash embeddings; add --use-llm for Bedrock-written text)
EMBEDDING_PROVIDER=hash epaa-datalake generate --migrate-first --employees 60 --projects 20
```

### As a service (Docker)

`docker compose -f DevOps/Local/Datalake/docker-compose.yaml up` then:

```bash
# async (triggers the SyntheticDataGen Airflow DAG)
curl -X POST localhost:8000/synthetic/generate -H 'content-type: application/json' \
  -d '{"num_employees":60,"num_projects":20,"run_async":true}'

# sync (runs the pipeline inline, no Airflow)
curl -X POST localhost:8000/synthetic/generate -H 'content-type: application/json' \
  -d '{"num_employees":60,"num_projects":20,"run_async":false}'
```

## Embedding providers

`EMBEDDING_PROVIDER` = `bedrock` (Titan v2) · `hf` (MiniLM, needs the `hf` extra) ·
`hash` (offline deterministic fallback). Failures fall back to `hash` automatically.
`EMBEDDING_DIM` must match the `Vector(...)` column size (1024 for Titan v2).

## Layout

```
src/epaa_datalake/
├── config.py            # settings from env
├── db.py                # SQLAlchemy engine/session
├── models.py            # ORM models = schema source of truth (UUID-string PKs, pgvector)
├── migrations/          # Alembic (baseline 0001 builds schema from models)
├── generators/          # taxonomy · structured (Faker) · text (hybrid) · embeddings · loader · pipeline
├── airflow_client.py    # trigger the DAG via Airflow REST
├── startup.py           # alembic upgrade head
├── cli.py               # `epaa-datalake migrate|generate`
└── api/                 # FastAPI (Req/Resp DTOs)
```
