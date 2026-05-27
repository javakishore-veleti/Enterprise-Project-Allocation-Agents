# Datalake

Synthetic-data generation for the EPAA platform, structured as a FastAPI front
door over an Apache Airflow DAG.

```
Middleware/Datalake/
├── SyntheticDataAPI/        # FastAPI — POST /synthetic/generate triggers the DAG async
│   └── src/epaa_datalake/
│       ├── api/             # FastAPI routes
│       └── airflow_client/  # calls the Airflow REST API
└── DAGS/
    └── SyntheticDataGen/    # Airflow DAG: generate employees/projects/briefs/calendars
        ├── synthetic_data_gen_dag.py
        └── tasks/           # generation + load steps → Postgres + pgvector
```

## How it works (target, M2)

1. A client (or the Admin portal) calls `POST /synthetic/generate` on **SyntheticDataAPI**
   with parameters (number of employees, projects, seed).
2. The API triggers the **SyntheticDataGen** Airflow DAG via the Airflow REST API and
   returns a run id immediately (async).
3. The DAG generates the dataset (Faker-based), computes embeddings, and loads
   employees / skills / projects / briefs / availability into Postgres + pgvector.
4. The API exposes `GET /synthetic/runs/{id}` to poll DAG run status.

## Runtime

Airflow runs locally via `DevOps/Local/Airflow/docker-compose.yaml` (LocalExecutor,
reuses your `apache/airflow:2.10.0-python3.12` image). This `DAGS/` folder is
bind-mounted into the Airflow containers at `/opt/airflow/dags`.

> Status: skeleton only. The DAG and API are implemented in milestone **M2** —
> see `DevelopmentPlan.md §5`.
