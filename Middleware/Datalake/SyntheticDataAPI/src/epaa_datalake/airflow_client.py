"""Thin client over the Airflow stable REST API (v1) to trigger the DAG."""
from __future__ import annotations

import datetime as dt
import uuid

import httpx

from .config import get_settings


def _client() -> httpx.Client:
    s = get_settings()
    return httpx.Client(base_url=s.airflow_base_url, auth=(s.airflow_user, s.airflow_password), timeout=15)


def trigger_dag(conf: dict) -> dict:
    """POST a new DAG run; returns {dag_run_id, state}."""
    s = get_settings()
    run_id = f"epaa__{dt.datetime.now(dt.UTC):%Y%m%dT%H%M%S}__{uuid.uuid4().hex[:8]}"
    with _client() as c:
        r = c.post(f"/api/v1/dags/{s.synthetic_dag_id}/dagRuns",
                   json={"dag_run_id": run_id, "conf": conf})
        r.raise_for_status()
        data = r.json()
    return {"dag_run_id": data["dag_run_id"], "state": data.get("state", "queued")}


def get_run(dag_run_id: str) -> dict:
    s = get_settings()
    with _client() as c:
        r = c.get(f"/api/v1/dags/{s.synthetic_dag_id}/dagRuns/{dag_run_id}")
        r.raise_for_status()
        data = r.json()
    return {"dag_run_id": data["dag_run_id"], "state": data.get("state")}
