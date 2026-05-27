# Design diagrams

`epaa-architecture.drawio` — a multi-tab [draw.io](https://app.diagrams.net)
(diagrams.net) file. Open it in the web app or the VS Code **Draw.io Integration**
extension.

## Tabs

1. **Business Architecture** — personas (Customer, Project/Resource Manager, Employee, Executive, Platform Admin) + the value stream; flags which capabilities the agents fully automate
2. **Overall Architecture** — portals → gateway → microservices → Synthetic Data Service → Postgres + observability (with the Manager/Customer actors)
3. **Agent Triggers** — how the **allocation pipeline** is triggered (manual via Agent Monitor / any API client; synchronous, on-demand)
4. **Data Generation Workflows** — synthetic-data generation (data tooling, **not** an agent): Data Management → Airflow DAG (async) → pgvector
5. **Datalake & Vector KB (Target)** — proposed future design (object storage, initial/daily/incremental ingestion, Airflow-managed) — see [../datalake-design.md](../datalake-design.md)
6. **Agent Pipeline** — the orchestrator running the 6 agents in sequence + persisted trace
7–12. **Agent 1–6** — Requirement Parsing · Skill Matching · Availability Checker · Assignment · Communication · Reporting

Legend: stick figure = persona/actor · blue = input · indigo = agent / AI capability ·
green = output / business capability · grey cylinder = data store · amber = LLM provider
or async trigger · purple = Spring service · yellow = Angular portal · dashed grey = future
(not built) · note = explanation. Dashed amber arrows = asynchronous (Airflow) triggers.

## Regenerate

```bash
python3 docs/Design/generate_diagrams.py   # no dependencies
```

Edit `generate_diagrams.py` (the source of truth) and re-run, or edit the
`.drawio` directly in diagrams.net.
