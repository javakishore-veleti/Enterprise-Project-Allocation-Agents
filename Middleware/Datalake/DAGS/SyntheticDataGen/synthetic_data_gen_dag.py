"""Airflow DAG: generate + load EPAA synthetic data.

Triggered by the SyntheticDataAPI (or manually). Run-time parameters come from
``dag_run.conf`` (num_employees, num_projects, seed, use_llm).

The generation logic is the same ``epaa_datalake`` package the API uses; it is
available on PYTHONPATH because the Airflow compose mounts the SyntheticDataAPI
``src/`` into the containers.
"""
from __future__ import annotations

import datetime as dt

from airflow.decorators import dag, task

DEFAULT_CONF = {"num_employees": 60, "num_projects": 20, "seed": 42, "use_llm": False}


@dag(
    dag_id="synthetic_data_gen",
    schedule=None,                       # triggered on demand
    start_date=dt.datetime(2026, 1, 1),
    catchup=False,
    tags=["epaa", "datalake", "synthetic"],
    default_args={"retries": 0},
)
def synthetic_data_gen():
    @task
    def migrate() -> str:
        from epaa_datalake.startup import run_migrations

        run_migrations()
        return "migrated"

    @task
    def generate(_upstream: str, **context) -> dict:
        from epaa_datalake.generators.pipeline import run as run_pipeline
        from epaa_datalake.generators.structured import GenSpec

        conf = {**DEFAULT_CONF, **(context["dag_run"].conf or {})}
        spec = GenSpec(
            num_employees=int(conf["num_employees"]),
            num_projects=int(conf["num_projects"]),
            seed=int(conf["seed"]),
            use_llm=bool(conf["use_llm"]),
        )
        summary = run_pipeline(spec, persist=True, reset=bool(conf.get("reset", True)))
        print("Synthetic data load summary:", summary)
        return summary

    generate(migrate())


synthetic_data_gen()
