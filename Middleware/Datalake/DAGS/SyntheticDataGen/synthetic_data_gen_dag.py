"""Airflow DAG: generate + load EPAA synthetic data.

Triggered by the SyntheticDataAPI (or manually). Run-time parameters come from
``dag_run.conf`` (num_employees, num_projects, seed, use_llm, reset).

Version note: Airflow 2.10 pins SQLAlchemy 1.4, but the ``epaa_datalake`` generators
require SQLAlchemy 2.0 (declarative ``mapped_column`` models). To avoid breaking
Airflow core, the migrate/generate steps run in an **isolated virtualenv**
(``@task.virtualenv``) that installs the generator deps and adds the bind-mounted
``epaa_datalake`` source (``/opt/airflow/epaa_src``) to ``sys.path``. The container's
POSTGRES_*/EMBEDDING_* env vars are inherited by the subprocess, so
``epaa_datalake.config`` resolves the same app DB.
"""
from __future__ import annotations

import datetime as dt

from airflow.decorators import dag, task

# Deps for the isolated generation venv (kept off Airflow core, which needs SQLAlchemy 1.4).
GEN_REQUIREMENTS = [
    "faker>=30",
    "sqlalchemy>=2.0",
    "psycopg2-binary>=2.9",
    "pgvector>=0.3",
    "boto3>=1.35",
    "pydantic-settings>=2.5",
    "alembic>=1.13",
]
VENV_CACHE = "/tmp/epaa-gen-venv"  # writable by the airflow user; reused within a container's life


@dag(
    dag_id="synthetic_data_gen",
    schedule=None,                       # triggered on demand
    start_date=dt.datetime(2026, 1, 1),
    catchup=False,
    is_paused_upon_creation=False,       # active on first parse so API-triggered runs execute
    tags=["epaa", "datalake", "synthetic"],
    default_args={"retries": 0},
)
def synthetic_data_gen():
    @task.virtualenv(requirements=GEN_REQUIREMENTS, system_site_packages=False,
                     venv_cache_path=VENV_CACHE)
    def migrate() -> str:
        import sys
        sys.path.insert(0, "/opt/airflow/epaa_src")
        from epaa_datalake.startup import run_migrations

        run_migrations()
        return "migrated"

    @task.virtualenv(requirements=GEN_REQUIREMENTS, system_site_packages=False,
                     venv_cache_path=VENV_CACHE)
    def generate(_upstream: str, conf_json: str) -> dict:
        import json
        import sys
        sys.path.insert(0, "/opt/airflow/epaa_src")
        from epaa_datalake.generators.pipeline import run as run_pipeline
        from epaa_datalake.generators.structured import GenSpec

        defaults = {"num_employees": 60, "num_projects": 20, "seed": 42,
                    "use_llm": False, "reset": True}
        conf = {**defaults, **(json.loads(conf_json) if conf_json else {})}
        spec = GenSpec(
            num_employees=int(conf["num_employees"]),
            num_projects=int(conf["num_projects"]),
            seed=int(conf["seed"]),
            use_llm=bool(conf["use_llm"]),
        )
        summary = run_pipeline(spec, persist=True, reset=bool(conf.get("reset", True)))
        print("Synthetic data load summary:", summary)
        return summary

    # dag_run.conf is passed as a JSON string (templated) so the venv subprocess can parse it.
    generate(migrate(), conf_json="{{ dag_run.conf | tojson }}")


synthetic_data_gen()
