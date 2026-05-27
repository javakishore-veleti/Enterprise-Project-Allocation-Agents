# Demo & run guide

Prerequisites: Docker, Node 20+, Python 3.12, JDK 21, Maven. Bedrock (Claude Opus 4.7,
`us-east-1`) is optional — everything runs offline with `EMBEDDING_PROVIDER=hash` and
`LLM_PROVIDER=heuristic`.

## Fastest: the core flow (one command)

```bash
bash DevOps/Local/smoke-test.sh
```

This builds + starts **Postgres + Datalake + Agents**, seeds synthetic data, runs the
6-agent pipeline over HTTP, and prints the managerial report. Expected:

```
[smoke] seeding synthetic data (sync)...
[smoke] running allocation pipeline for project <uuid>
{ "run_id": "...", "status": "success", "allocation_time_ms": 17,
  "assignments": [ {"full_name": "...", "rank": 1, "final_score": 0.31}, ... ],
  "report": "Project \"...\": assigned N/N requested — ...",
  "metrics": { "candidates_evaluated": 15, "conflicts_avoided": 0, ... } }
```

Tear down: `bash DevOps/Local/docker-all-down.sh all --volumes`.

## Full stack

```bash
cp .env.example .env          # then set AWS values if using Bedrock
npm run start                 # secrets:gen → docker-all-up all (infra→airflow→datalake→agents→middleware→portals)
npm run status                # container + URL overview
```

Local URLs:

| Service | URL |
|---------|-----|
| Admin portal | http://localhost:4200 |
| Projects portal | http://localhost:4201 |
| API gateway | http://localhost:8080 |
| Agents API | http://localhost:8001 |
| Datalake API | http://localhost:8000 |
| Airflow | http://localhost:8088 (admin/admin) |
| Jaeger | http://localhost:16686 · Grafana :3000 · Prometheus :9090 · Kibana :5601 · pgAdmin :5050 |

> First `npm run start` builds the 6 Spring + 2 Angular images (several minutes). The
> Spring services run on shared Postgres in this mode (`SPRING_DATASOURCE_*`).

## Walkthrough

1. **Projects portal → Submit Brief** — fill the form; it `POST`s `/api/projects`.
2. **Admin portal → Data Management → Synthetic Data → a type** — pick the workflow,
   **Initiate Execution** to generate data (or **History** for past runs, 15/page).
3. Trigger an allocation: `POST /api/allocations/run {projectId}` (gateway →
   allocation-service → agents).
4. **Admin portal → Reports / Agent Monitor** — see the run trace + managerial report.

## Per-layer dev

```bash
npm run start:infra        # postgres + observability
npm run start:datalake     # datalake API only
npm run start:agents       # agents API only
npm run secrets:gen        # regenerate Spring application-local-secrets.yaml from .env
```

Run a service standalone: `cd Middleware/employee-service && mvn spring-boot:run -pl employee-api`
(defaults to H2). Run a portal: `cd Portals/admin-portal && npm start`.
