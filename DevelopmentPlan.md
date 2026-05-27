# MCP-AI Development Plan

Hands-on implementation of the IEEE paper **"MCP-AI: A Multi-Agent Architecture using Large Language Models for Automated Enterprise Project Allocation"** (Bhaskar et al., ICAISS-2026).

> **Repo name:** `enterprise-project-allocation-agents`
> **Paper PDF:** `MCP-AI_A_Multi-Agent_Architecture_using_Large_Language_Models_for_Automated_Enterprise_Project_Allocation.pdf`
>
> Note: the repo intentionally avoids the "MCP" abbreviation in its name to prevent confusion with Anthropic's Model Context Protocol. The paper's MCP-AI branding is preserved in docs.

---

## 1. What we are building

The paper proposes 6 autonomous LLM-driven agents that automate the end-to-end project-to-employee allocation process in an enterprise. We are building a working implementation with:

- A Python **Agents** service hosting the 6 agents (Strands Agents + AWS Bedrock).
- A set of Java **Middleware** microservices (Spring Boot 3 / Java 21) for CRUD, gateway, auth, notifications, reporting.
- Two Angular **Portals** — an Admin portal and a Customer (Projects) portal.
- Local-first infra via Docker Compose (Postgres+pgvector, Grafana/Prometheus/Jaeger, optional Qdrant).
- AWS deployment via Terraform + GitHub Actions (VPC, Bedrock model access, SageMaker, RDS, ECS, Cognito, CloudFront).

### 1.1 The 6 agents (from the paper)

| # | Agent | Responsibility |
|---|-------|----------------|
| 1 | Requirement Parsing Agent | Extract required skills, priority, duration, complexity from free-text project briefs. |
| 2 | Skill-Matching Agent | Semantic similarity between project requirements and employee profiles (skills, experience, past performance). |
| 3 | Availability Checker Agent | Check calendars / current load; prevent over-allocation and scheduling conflicts. |
| 4 | Assignment Agent | Rank project-employee mappings using relevance score + project priority + workload. |
| 5 | Communication Agent | Notify assigned staff (email / Slack / in-app). |
| 6 | Reporting Agent | Managerial reports — allocation decisions, skill usage, workload distribution. |

### 1.2 Evaluation metrics (from paper Table 2)

Allocation Time · Resource Utilization · Conflict Reduction · Human Intervention. These will be measurable through the Admin portal's "Agent Monitor" + Reports pages.

### 1.3 Why a Vector DB is required

The Skill-Matching Agent (§III-C of the paper) explicitly uses **semantic embeddings** to match unstructured project requirements to employee profiles. We need vector storage + ANN search. Primary choice: **pgvector** (Postgres extension — zero extra services). Optional alternative: **Qdrant** as a standalone container under `DevOps/Local/VectorDBs/Qdrant/` for hands-on comparison.

---

## 2. Architecture overview

```
                 +-----------------------------+        +--------------------------+
                 |  Admin Portal (Angular 18)  |        |  Projects Portal (Ang18) |
                 +--------------+--------------+        +------------+-------------+
                                |                                    |
                                v                                    v
                       +--------+------------------------------------+--------+
                       |              API Gateway (Spring Cloud Gateway)      |
                       +--+-------------+--------------+--------------+-------+
                          |             |              |              |
                  +-------v-----+ +-----v------+ +-----v------+ +-----v--------+
                  | employee-   | | project-   | | allocation-| | notification-|
                  | service     | | service    | | service    | | service      |
                  +------+------+ +-----+------+ +-----+------+ +------+-------+
                         |              |              |               |
                         +-----+--------+----+---------+---------------+
                               |             |
                               v             v
                       +-------+---+   +-----+---------------------+
                       | Postgres  |   |  Agents Service (FastAPI) |
                       | + pgvector|<--+  Strands Agents +         |
                       +-----------+   |  AWS Bedrock (Claude)     |
                                       |                           |
                                       |  6 agents:                |
                                       |   - Requirement Parsing   |
                                       |   - Skill Matching        |
                                       |   - Availability Checker  |
                                       |   - Assignment            |
                                       |   - Communication         |
                                       |   - Reporting             |
                                       +---------------------------+

   Observability sidecar: Prometheus scrapes services + agents; Jaeger collects traces;
   Grafana dashboards. OpenTelemetry SDK in every service.
```

Allocation request flow:

1. Customer submits a project brief through **Projects Portal** → `project-service` stores brief.
2. `allocation-service` calls **Agents Service** `POST /allocations/run`.
3. Agents Service runs the 6-agent pipeline (Strands orchestrator), reading employees from Postgres and embeddings from pgvector.
4. Result (assigned team + relevance scores + report) written back; `notification-service` notifies assignees.
5. Admin sees the full trace in the Agent Monitor and the report in Reports page.

---

## 3. Tech stack (confirmed)

| Layer | Choice |
|-------|--------|
| Agent framework | **Strands Agents** (primary) — alt adapters for LangChain / OpenAI Agents SDK / Spring AI added in Phase 4 |
| LLM provider | **AWS Bedrock** — Claude Sonnet 4.6 default; Llama 3 / Nova as alternates |
| Embeddings | Bedrock Titan Embeddings v2 (cloud) · HuggingFace `all-MiniLM-L6-v2` (local) |
| Agents runtime | Python 3.12 + FastAPI + Uvicorn |
| Microservices | Java 21 + Spring Boot 3.3 + Spring Cloud Gateway |
| Frontend | Angular 18 (standalone components) + Tailwind |
| Database | Postgres 16 + pgvector |
| Optional vector DB | Qdrant (containerized, optional) |
| Observability | Prometheus + Grafana + Jaeger + OpenTelemetry |
| Local orchestration | Docker Compose + shell scripts + root `package.json` |
| IaC | Terraform (modular) |
| CI/CD | GitHub Actions |

---

## 4. Folder layout

```
AutomatedEnterpriseProjectAllocation/
├── README.md
├── DevelopmentPlan.md                    <-- this file
├── package.json                          # root scripts: start/stop/status everything
├── .env.example
├── .gitignore
├── MCP-AI_..._Allocation.pdf             # the paper
│
├── docs/
│   ├── architecture.md
│   ├── agents.md                         # per-agent contracts & prompts
│   ├── api-contracts.md                  # REST contracts between layers
│   ├── data-model.md
│   └── diagrams/
│
├── Middleware/                           # backend — Java microservices + Python agents
│   ├── pom.xml                           # parent BOM (aggregates the Java modules only)
│   ├── Agents/                           # Python — Strands Agents (the 6 agents) + FastAPI
│   │   ├── pyproject.toml
│   │   ├── Dockerfile
│   │   ├── README.md
│   │   ├── src/epaa/
│   │   │   ├── agents/
│   │   │   │   ├── requirement_parsing_agent.py
│   │   │   │   ├── skill_matching_agent.py
│   │   │   │   ├── availability_checker_agent.py
│   │   │   │   ├── assignment_agent.py
│   │   │   │   ├── communication_agent.py
│   │   │   │   └── reporting_agent.py
│   │   │   ├── orchestrator/             # multi-agent coordination + tracing
│   │   │   ├── providers/                # bedrock.py, openai.py, hf.py, langchain.py
│   │   │   ├── tools/                    # shared tools: db, embeddings, vector store
│   │   │   ├── models/                   # pydantic schemas
│   │   │   ├── api/                      # FastAPI routes
│   │   │   └── observability/            # otel + prometheus instrumentation
│   │   └── tests/
│   ├── Datalake/                         # synthetic data (Python)
│   │   ├── SyntheticDataAPI/             # FastAPI (src/epaa_datalake) — triggers the DAG async
│   │   └── DAGS/SyntheticDataGen/        # Airflow DAG — generate + load employees/projects/briefs
│   ├── employee-service/                 # each domain service = per-service Maven multi-module:
│   │   ├── pom.xml                       #   parent
│   │   ├── employee-api/                 #   Spring Boot main; deps on the modules below
│   │   ├── employee-services/            #   service interfaces + Impl
│   │   ├── employee-dao/                 #   repositories
│   │   ├── employee-entities/            #   JPA entities (UUID-string PKs)
│   │   ├── employee-common/              #   base entity + base Req/Resp DTOs
│   │   └── employee-utils/
│   ├── project-service/                  # (same 6-module layout)
│   ├── allocation-service/               # allocations; calls Agents
│   ├── notification-service/             # email/slack (stub locally)
│   ├── reporting-service/                # report read-models
│   └── api-gateway/                      # Spring Cloud Gateway + JWT
│
├── Portals/
│   ├── admin-portal/                     # Angular 18
│   │   └── src/app/
│   │       ├── employees/
│   │       ├── projects/
│   │       ├── allocations/
│   │       ├── agent-monitor/            # live trace of the 6-agent run
│   │       ├── reports/
│   │       ├── auth/
│   │       └── shared/
│   └── projects-portal/                  # customer-facing Angular 18
│       └── src/app/
│           ├── submit-brief/
│           ├── my-projects/
│           ├── notifications/
│           ├── auth/
│           └── shared/
│
├── DevOps/
│   ├── Local/
│   │   ├── docker-all-up.sh              # up: infra → airflow → agents → middleware → portals
│   │   ├── docker-all-down.sh
│   │   ├── docker-all-status.sh
│   │   ├── scripts/
│   │   │   └── gen-spring-secrets.mjs    # generate application-local-secrets.yaml from .env
│   │   ├── Postgres/
│   │   │   ├── docker-compose.yaml       # pgvector/pgvector:pg16 + pgAdmin
│   │   │   └── init/
│   │   │       ├── 01-extensions.sql     # vector, uuid-ossp, pg_trgm
│   │   │       └── 02-schema.sql         # epaa schema (tables in M2)
│   │   ├── Observability/                # (moved here from repo root)
│   │   │   ├── Prometheus/{docker-compose.yaml, prometheus.yml}
│   │   │   ├── Grafana/{docker-compose.yaml, provisioning/}
│   │   │   ├── Jaeger/docker-compose.yaml
│   │   │   └── Kibana/docker-compose.yaml  # Elasticsearch + Kibana
│   │   ├── Airflow/
│   │   │   └── docker-compose.yaml       # LocalExecutor; reuses apache/airflow:2.10.0-python3.12
│   │   ├── VectorDBs/                    # OPTIONAL alternative to pgvector
│   │   │   └── Qdrant/docker-compose.yaml
│   │   ├── Agents/
│   │   │   └── docker-compose.yaml
│   │   ├── Middleware/
│   │   │   └── docker-compose.yaml       # the 6 Spring Boot services
│   │   └── Portals/
│   │       └── docker-compose.yaml       # nginx + admin + customer portals
│   └── AWS/
│       └── Terraform/
│           ├── modules/
│           │   ├── vpc/  · bedrock/  · sagemaker/  · rds/
│           │   ├── ecs/  · cognito/  · cloudfront/
│           └── environments/dev/
│
└── .github/
    └── workflows/
        ├── ci-agents.yml                 # python lint + tests
        ├── ci-middleware.yml             # mvn verify per service
        ├── ci-portals.yml                # ng build + test for both portals
        ├── 001-AWS-Deploy-VPC.yml
        ├── 001-AWS-Destroy-VPC.yml
        ├── 002-AWS-Deploy-Bedrock.yml
        ├── 002-AWS-Destroy-Bedrock.yml
        ├── 003-AWS-Deploy-RDS.yml
        ├── 003-AWS-Destroy-RDS.yml
        ├── 004-AWS-Deploy-SageMaker.yml
        ├── 004-AWS-Destroy-SageMaker.yml
        ├── 005-AWS-Deploy-ECS.yml
        ├── 005-AWS-Destroy-ECS.yml
        ├── 006-AWS-Deploy-Cognito.yml
        ├── 006-AWS-Destroy-Cognito.yml
        ├── 007-AWS-Deploy-CloudFront.yml
        └── 007-AWS-Destroy-CloudFront.yml
```

### 4.1 Root `package.json` scripts (planned)

```
start                # = start:infra && start:agents && start:middleware && start:portals
stop                 # = reverse order
status               # docker-all-status.sh + curl health endpoints

start:infra          # Postgres + Observability (+ optional Qdrant)
start:postgres
start:observability  # Grafana + Prometheus + Jaeger
start:vectordb       # Qdrant (only if not using pgvector)

start:agents         # python FastAPI
start:middleware     # all Spring Boot services
start:portals        # admin + customer Angular dev servers

stop:*               # mirrors above
status:*
seed                 # run synthetic data generator → Postgres
```

---

## 5. Milestones & tasks

Legend: `[ ]` pending · `[~]` in progress · `[x]` complete · `[-]` deferred

### M0 — Plan & Repo Bootstrap

| # | Task | Status |
|---|------|--------|
| 0.1 | Read paper and lock scope | [x] |
| 0.2 | Confirm tech stack (Strands+Bedrock, hybrid Python/Java, local-first) | [x] |
| 0.3 | Write `DevelopmentPlan.md` (this doc) | [x] |
| 0.4 | User creates the git repo | [x] |
| 0.5 | Add `README.md`, `.gitignore`, `.env.example`, root `package.json` | [x] |

### M1 — Local Infrastructure (Category: DevOps/Local)

| # | Task | Status |
|---|------|--------|
| 1.1 | `DevOps/Local/Postgres/docker-compose.yaml` (pgvector/pgvector:pg16 + pgAdmin) | [x] |
| 1.2 | `init/01-extensions.sql` (vector, uuid-ossp, pg_trgm) + `init/02-schema.sql` (epaa schema) | [x] |
| 1.3 | `DevOps/Local/Observability/Prometheus/` + `prometheus.yml` | [x] |
| 1.4 | `DevOps/Local/Observability/Grafana/` + provisioned datasources (Prometheus + Jaeger) | [x] |
| 1.5 | `DevOps/Local/Observability/Jaeger/docker-compose.yaml` (all-in-one OTLP) | [x] |
| 1.6 | `DevOps/Local/Observability/Kibana/docker-compose.yaml` (Elasticsearch + Kibana) | [x] |
| 1.7 | `DevOps/Local/Airflow/docker-compose.yaml` (LocalExecutor; reuses local airflow image) | [x] |
| 1.8 | `DevOps/Local/scripts/gen-spring-secrets.mjs` (generate secrets yaml from `.env`, diff-aware) | [x] |
| 1.9 | `DevOps/Local/docker-all-up.sh` / `down.sh` / `status.sh` (layer-aware, reuse local images) | [x] |
| 1.10 | Root `package.json` scripts incl. `secrets:gen` + `prestart` hook | [x] |
| 1.11 | `DevOps/Local/VectorDBs/Qdrant/` (optional, alt to pgvector) | [-] |
| 1.12 | Verified: Postgres boots from local image; pgvector 0.8.2 + epaa schema confirmed | [x] |

### M2 — Data Layer & Datalake (Category: Data)

> All under `Middleware/Datalake/`. Schema is created by **Alembic** migrations (auto-run on startup),
> with matching **Liquibase** changelogs for the Spring services. PKs are UUID-as-String.

**Data generated** — both relational and textual:
- *Relational:* `employees`, `skills`, `employee_skills` (M:N, proficiency), `projects`, `availability`
  (calendar bookings), seeded `allocations`.
- *Textual (unstructured):* `project_briefs.brief_text` (NL brief → Requirement Parsing Agent),
  `employees.profile_text` (bio → Skill-Matching Agent).
- *Vectors:* `employees.profile_embedding`, `project_briefs.requirements_embedding` (pgvector).

| # | Task | Status |
|---|------|--------|
| 2.1 | Alembic migrations for schema: employees, skills, employee_skills, projects, project_briefs, availability, allocations, agent_runs, agent_steps, notifications, reports (UUID-string PKs) | [x] |
| 2.2 | pgvector columns: `employees.profile_embedding`, `project_briefs.requirements_embedding` (1024-dim, verified) | [x] |
| 2.3 | Skill taxonomy + structured generators (Faker): 30–100 employees, 10–40 projects, availability | [x] |
| 2.4 | Text generation — hybrid: template/Faker default, `--use-llm` (Bedrock) for realistic briefs/bios | [x] |
| 2.5 | Embeddings: Bedrock Titan / HF MiniLM / hash fallback into pgvector (hash verified offline) | [x] |
| 2.6 | `DAGS/SyntheticDataGen` Airflow DAG: migrate → generate → embed → load into Postgres | [x] |
| 2.7 | `SyntheticDataAPI` FastAPI: `POST /synthetic/generate` (async DAG + sync inline) + `GET /runs/{id}` | [x] |
| 2.8 | Verified end-to-end: migrations + generate loaded 12 tables; pytest 4/4 green | [x] |
| 2.9 | Workflow registry: `wf_def` + `wf_executions` tables (delta migration 0002, conditional) + registry/history API — records DAG triggers; paginated 15/page searchable history. Backs admin Data Management. Verified. | [x] |
| 2.10 | Curated sample fixtures committed under `SyntheticDataAPI/samples/` | [ ] |
| 2.11 | Run the DAG inside the Airflow container (validate `_PIP_ADDITIONAL_REQUIREMENTS` + DAG import) | [ ] |

### M3 — Agents Layer (Category: AI / Agents)

| # | Task | Status |
|---|------|--------|
| 3.1 | `Middleware/Agents/` Python project (`epaa`; reuses `epaa_datalake` schema/db/embeddings) | [x] |
| 3.2 | LLM provider: Strands → Bedrock (Opus 4.7) → heuristic fallback (offline-capable) | [x] |
| 3.3 | Embedding provider — reused from `epaa_datalake.generators.embeddings` | [x] |
| 3.4 | Vector store: pgvector cosine_distance shortlist over `profile_embedding` | [x] |
| 3.5 | Agent 1 — Requirement Parsing (LLM JSON; heuristic fallback parses brief text) | [x] |
| 3.6 | Agent 2 — Skill Matching (pgvector cosine similarity + required-skill overlap) | [x] |
| 3.7 | Agent 3 — Availability Checker (DB-only; drops unavailable, sets factor) | [x] |
| 3.8 | Agent 4 — Assignment (weighted score relevance/priority/availability → allocations) | [x] |
| 3.9 | Agent 5 — Communication (queues a notification row per assignee) | [x] |
| 3.10 | Agent 6 — Reporting (LLM summary; template fallback) + metrics | [x] |
| 3.11 | Orchestrator: sequential pipeline w/ persisted trace (`agent_runs`/`agent_steps`) | [x] |
| 3.12 | FastAPI endpoints: `POST /allocations/run`, `GET /agent-runs/{id}`, `GET /reports/{id}` | [x] |
| 3.13 | OpenTelemetry traces → Jaeger; Prometheus metrics | [ ] |
| 3.14 | Tests + verified end-to-end offline (6-step trace, allocations, report, metrics) | [x] |

### M4 — Middleware / Microservices (Category: Backend)

> **Conventions (mandatory — see CLAUDE.md §7):** each service is a per-service Maven multi-module
> (`<svc>-api` deployable + `-services`/`-dao`/`-entities`/`-common`/`-utils`); every controller and
> service method takes a Request DTO and returns a Response DTO (no scalar param lists); services are
> interface + Impl; Lombok everywhere; Liquibase runs on startup; **H2 default** (Postgres via
> `DB_PROFILE`); UUID-string PKs; `application-local-secrets.yaml` generated from `.env` via
> `npm run secrets:gen`.

| # | Task | Status |
|---|------|--------|
| 4.1 | Per-service module archetype (parent pom + api/services/dao/entities/common/utils) + base `BaseRequest`/`BaseResponse`/`BaseEntity` in `<svc>-common` | [x] |
| 4.2 | Lombok + Liquibase (startup migrations) + H2/Postgres profile wiring (via generated secrets) | [x] |
| 4.3 | `employee-service` (6 modules) — CRUD, Req/Resp DTOs, iface+impl. **Built + runtime-verified** (Liquibase on startup, H2, UUID PKs, paginated/searchable list) | [x] |
| 4.4 | `project-service` (6 modules) — projects + briefs. Built clean. | [x] |
| 4.5 | `allocation-service` (6 modules) — RestClient calls Agents `/allocations/run`, audits requests. Built clean. | [x] |
| 4.6 | `notification-service` (6 modules) — notifications queue + deliver (log stub). Built clean. | [x] |
| 4.7 | `reporting-service` (6 modules) — reports read-model + latest-for-project. Built clean. | [x] |
| 4.8 | `api-gateway` (Spring Cloud Gateway) routing to all services. Built + boots healthy. JWT deferred → M5/M7. | [x] |
| 4.9 | Springdoc OpenAPI on every service [x]; OpenTelemetry wiring → M6 | [~] |
| 4.10 | Per-service Dockerfiles + `DevOps/Local/Middleware/docker-compose.yaml` → M6 (full-stack bring-up) | [ ] |

### M5 — Portals (Category: Frontend)

**Admin portal information architecture (mandated):**
- **Top menu bar:** `Home` · `Dashboard` · `Data Management` · `Administration`.
- **Data Management** opens a **left nav** with `Synthetic Data` and, nested under it, the
  **synthetic-data types** (e.g. Employees, Projects, Briefs, Full Dataset) as sub-levels.
- Selecting a type shows, on the **right**, a **searchable dropdown of the Apache Airflow workflows**
  scoped to that type (sourced from Airflow DAGs, e.g. tagged by type).
- Selecting a workflow reveals two actions:
  - **Initiate Execution** → a workflow-specific **criteria/parameters form** (maps to the DAG's
    `conf`), submits via the Datalake `POST /synthetic/generate` (or the workflow's trigger endpoint).
  - **History** → a **paginated table of past executions, 15 per page, with searchable columns**
    (run id, state, trigger time, duration, params), sourced from the Airflow REST `dagRuns` API.

```
[Home] [Dashboard] [Data Management] [Administration]
 └─ Data Management
    ├─ Synthetic Data
    │   ├─ Employees ─┐
    │   ├─ Projects   │→ right pane: ▸ workflow dropdown (searchable)
    │   ├─ Briefs     │                 └─ <workflow> → [Initiate Execution] [History]
    │   └─ Full Dataset                       Initiate → criteria form (DAG conf)
    │                                          History  → 15/page, searchable columns
```

| # | Task | Status |
|---|------|--------|
| 5.1 | `Portals/admin-portal` — Angular 18 + PrimeNG 18 (Slate+Indigo Aura preset). Builds clean. | [x] |
| 5.2 | Admin shell: top menu bar (Home · Dashboard · Data Management · Administration) + routing | [x] |
| 5.3 | Data Management: dark-slate left nav (Synthetic Data → type sub-levels) | [x] |
| 5.4 | Data Management: per-type searchable Airflow-workflow dropdown (p-select, from Datalake API) | [x] |
| 5.5 | Workflow → Initiate Execution: criteria form → POST /datalake/synthetic/generate | [x] |
| 5.6 | Workflow → History: PrimeNG lazy p-table (15/page) + searchable (status/run-id) | [x] |
| 5.7 | Admin: Employees CRUD page | [ ] |
| 5.8 | Admin: Projects + Briefs page | [ ] |
| 5.9 | Admin: Allocations page (trigger + result view) | [ ] |
| 5.10 | Admin: **Agent Monitor** — live trace of 6 agents (SSE/WebSocket) | [ ] |
| 5.11 | Admin: Reports page (paper's 4 metrics + LLM rationale) | [ ] |
| 5.12 | `Portals/projects-portal` — Angular 18 + PrimeNG (Slate+Indigo). Builds clean. | [x] |
| 5.13 | Customer: Submit Brief page → POST /api/projects | [x] |
| 5.14 | Customer: My Projects + status (lazy table) | [x] |
| 5.15 | Customer: Notifications inbox (lazy table) | [x] |
| 5.16 | Auth wiring (JWT issued by Spring; Cognito in M7) | [ ] |
| 5.17 | Per-portal Dockerfiles + `DevOps/Local/Portals/docker-compose.yaml` (nginx) → M6 | [ ] |

### M6 — End-to-End Local (Category: Integration)

| # | Task | Status |
|---|------|--------|
| 6.1 | `docker-all-up.sh` brings up entire stack in correct order with healthchecks | [ ] |
| 6.2 | Seed → submit brief from customer portal → see allocation + report in admin | [ ] |
| 6.3 | Verify Jaeger traces span Portal → Gateway → Allocation → Agents → Postgres | [ ] |
| 6.4 | Grafana dashboard for the paper's 4 evaluation metrics | [ ] |

### M7 — AWS Deployment (Category: Cloud)

| # | Task | Status |
|---|------|--------|
| 7.1 | Terraform module: `vpc` | [ ] |
| 7.2 | Terraform module: `bedrock` (model invocation IAM + Bedrock model access requests) | [ ] |
| 7.3 | Terraform module: `rds` (Postgres + pgvector parameter group) | [ ] |
| 7.4 | Terraform module: `sagemaker` (Studio + optional endpoint for HF model) | [ ] |
| 7.5 | Terraform module: `ecs` (Fargate cluster + services for Agents + Middleware) | [ ] |
| 7.6 | Terraform module: `cognito` (user pools for admin + customer) | [ ] |
| 7.7 | Terraform module: `cloudfront` (S3-hosted Angular bundles) | [ ] |
| 7.8 | `.github/workflows/001-AWS-Deploy-VPC.yml` + `001-AWS-Destroy-VPC.yml` | [ ] |
| 7.9 | `002-AWS-Deploy-Bedrock.yml` + Destroy | [ ] |
| 7.10 | `003-AWS-Deploy-RDS.yml` + Destroy | [ ] |
| 7.11 | `004-AWS-Deploy-SageMaker.yml` + Destroy | [ ] |
| 7.12 | `005-AWS-Deploy-ECS.yml` + Destroy | [ ] |
| 7.13 | `006-AWS-Deploy-Cognito.yml` + Destroy | [ ] |
| 7.14 | `007-AWS-Deploy-CloudFront.yml` + Destroy | [ ] |
| 7.15 | OIDC trust between GitHub Actions and AWS (no static keys) | [ ] |

### M8 — CI / Quality (Category: CI/CD)

| # | Task | Status |
|---|------|--------|
| 8.1 | `ci-agents.yml` — ruff + pytest + coverage | [ ] |
| 8.2 | `ci-middleware.yml` — mvn verify (per-service matrix) | [ ] |
| 8.3 | `ci-portals.yml` — ng build + ng test (matrix admin/customer) | [ ] |
| 8.4 | Dependabot / Renovate | [-] |
| 8.5 | Security scan (Snyk or `gh codeql`) | [-] |

### M9 — Alternate Framework Adapters (Category: Learning Tracks — deferred)

| # | Task | Status |
|---|------|--------|
| 9.1 | LangChain / LangGraph adapter for orchestrator | [-] |
| 9.2 | OpenAI Agents SDK adapter | [-] |
| 9.3 | Spring AI alternate path (single-language Java agent demo) | [-] |
| 9.4 | HuggingFace local model adapter (Ollama / Transformers) | [-] |
| 9.5 | SageMaker-hosted HF model endpoint as Bedrock alternate | [-] |

### M10 — Documentation & Demo

| # | Task | Status |
|---|------|--------|
| 10.1 | `docs/architecture.md` with rendered diagram | [ ] |
| 10.2 | `docs/agents.md` — per-agent prompts, inputs, outputs | [ ] |
| 10.3 | `docs/api-contracts.md` — REST contracts | [ ] |
| 10.4 | Demo script (`docs/demo.md`) showing end-to-end flow | [ ] |
| 10.5 | Recorded GIF / screenshots in README | [ ] |

---

## 6. AWS workflow numbering convention

Workflows are prefixed `NNN-AWS-Deploy-<resource>.yml` / `NNN-AWS-Destroy-<resource>.yml`. The number reflects **dependency order** (lower must be deployed before higher; destroy runs in reverse):

| # | Resource | Why this order |
|---|----------|----------------|
| 001 | VPC | Network foundation |
| 002 | Bedrock | Model access (no infra dependency, but app needs it) |
| 003 | RDS | Postgres + pgvector for app data |
| 004 | SageMaker | Studio + optional HF endpoint |
| 005 | ECS | Fargate services (Agents + Middleware) — depend on RDS + Bedrock |
| 006 | Cognito | Auth pools — needed before CloudFront origin uses them |
| 007 | CloudFront | Portals hosted on S3 + CloudFront, integrated with Cognito |

Each workflow:
- Triggered manually (`workflow_dispatch`) with `environment` input.
- Assumes role via OIDC (no long-lived AWS keys).
- Calls `terraform -chdir=DevOps/AWS/Terraform/environments/<env>` with the matching module targeted.

---

## 7. Open decisions / risks

| # | Item | Default | Needs your call? |
|---|------|---------|------------------|
| D1 | Bedrock model | Claude Sonnet 4.6 | Yes — confirm model access in your AWS account |
| D2 | Vector store | pgvector (single Postgres) | Yes — or Qdrant standalone for hands-on |
| D3 | Auth in M5 | Spring Security + local JWT first, swap to Cognito in M7 | Confirm |
| D4 | Java/Spring versions | Java 21 + Spring Boot 3.3 | Confirm |
| D5 | Angular version | Angular 18 | Confirm |
| D6 | Package / group names | `com.kishore.mcpai.*` (Java), `mcp_ai` (Python), `@mcp-ai/admin-portal` (Angular) | Confirm |
| D7 | AWS region | `us-east-1` (broadest Bedrock model availability) | Confirm |
| D8 | Notification channel | Console log + SMTP stub locally, SES on AWS | Confirm |
| D9 | Repo style | Monorepo (everything in one git repo) | Confirm |
| D10 | License | None / MIT / Apache-2.0? | Confirm |

---

## 8. Out of scope (explicit)

- Real production identity / SSO (Okta, Azure AD) — Cognito only.
- Multi-tenant isolation beyond schema-level.
- Fine-tuning Bedrock models — use prompt engineering + RAG only.
- Mobile apps — web portals only.
- Slack/MS Teams integrations — stubbed via log lines.
- Cost-control automation (auto-shutdown) beyond the destroy workflows.

---

## 9. What happens next (after you create the repo)

1. You run `git init` (or create on GitHub) at this folder and push the paper + this plan.
2. I begin **M0.5** (README, `.gitignore`, `.env.example`, root `package.json`) and **M1** (Local infra) — these unblock everything else.
3. We iterate milestone by milestone; each completed task gets `[x]` in this file as we go.

> This document is the single source of truth for scope and progress. Edit freely — I will keep the status table in sync as work lands.
