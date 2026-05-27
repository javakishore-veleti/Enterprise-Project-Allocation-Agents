# Architecture

EPAA implements the MCP-AI paper: free-text project briefs are turned into staffed
teams by six LLM-driven agents, wrapped in an enterprise platform (microservices +
portals + observability + IaC).

## Components

```
            ┌─────────────────────┐      ┌──────────────────────┐
            │  admin-portal (Ng)  │      │ projects-portal (Ng) │
            └──────────┬──────────┘      └───────────┬──────────┘
                       │  http (CORS)                │
                       └──────────────┬──────────────┘
                                      ▼
                        ┌──────────────────────────┐
                        │  api-gateway (Spring CG)  │   /api/* , /agents/*, /datalake/*
                        └─────┬───────────────┬─────┘
            ┌─────────────────┼───────────────┼──────────────────┐
            ▼                 ▼               ▼                  ▼
   employee-service   project-service   allocation-service   notification- /
   (CRUD)             (projects+briefs) (calls Agents)        reporting-service
            └─────────────────┴───────┬───────┴──────────────────┘
                                       ▼
                          ┌────────────────────────┐
                          │   Agents (FastAPI)     │  6-agent pipeline (Strands+Bedrock)
                          │   Datalake (FastAPI)   │  synthetic data + Airflow DAG
                          └───────────┬────────────┘
                                      ▼
                       ┌───────────────────────────┐
                       │  Postgres + pgvector       │  shared schema (Alembic-owned)
                       └───────────────────────────┘

  Observability: OpenTelemetry → Jaeger (traces) · Prometheus + Grafana (metrics) · Kibana (logs)
  Orchestration: Airflow (LocalExecutor) runs the synthetic-data DAG
```

## Layers

| Layer | Tech | Location |
|-------|------|----------|
| Agents | Python · Strands · Bedrock (Claude Opus 4.7) · FastAPI | `Middleware/Agents` (`epaa`) |
| Datalake | Python · FastAPI · Airflow DAG · Faker · pgvector | `Middleware/Datalake` (`epaa_datalake`) |
| Microservices | Java 21 · Spring Boot 3.3 · Spring Cloud Gateway | `Middleware/*-service`, `Middleware/api-gateway` |
| Portals | Angular 18 · PrimeNG (Slate+Indigo) | `Portals/admin-portal`, `Portals/projects-portal` |
| Data | Postgres 16 + pgvector | `DevOps/Local/Postgres` |
| Observability | Prometheus · Grafana · Jaeger · Kibana/Elasticsearch | `DevOps/Local/Observability` |
| Cloud | Terraform (7 modules) + GitHub Actions | `DevOps/AWS/Terraform`, `.github/workflows` |

## Allocation flow (the paper's claim)

1. A customer submits a brief in **projects-portal** → `project-service` stores the
   project + brief in Postgres.
2. **allocation-service** `POST /api/allocations/run` calls the **Agents** service.
3. The orchestrator runs the six agents in order, persisting a trace to
   `agent_runs` / `agent_steps` and writing `allocations`, `notifications`, a `reports`
   row, and the paper's metrics (allocation time, conflicts avoided, utilization).
4. **admin-portal** shows the run trace, assignments, and the managerial report.

## Schema ownership

The Datalake (Alembic) owns the shared Postgres schema. On shared Postgres the Spring
services' Liquibase changesets `MARK_RAN` pre-existing tables and create only what
they own (e.g. `allocation_requests`). By default the Spring services run on H2
(self-contained); `DB_PROFILE=postgres` (or `SPRING_DATASOURCE_*`) switches them to the
shared database used by the agents.

## Data model (Postgres `epaa` schema)

`employees`, `skills`, `employee_skills`, `projects`, `project_briefs`, `availability`,
`allocations`, `agent_runs`, `agent_steps`, `notifications`, `reports`, plus the
workflow registry `wf_def` / `wf_executions`. All PKs are UUID stored as String;
`employees.profile_embedding` and `project_briefs.requirements_embedding` are pgvector
columns (1024-dim).

See also: [agents.md](agents.md) · [api-contracts.md](api-contracts.md) · [demo.md](demo.md).
