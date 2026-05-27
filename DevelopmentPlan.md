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
├── Agents/                               # Python — Strands Agents
│   ├── pyproject.toml
│   ├── Dockerfile
│   ├── README.md
│   ├── src/mcp_ai/
│   │   ├── agents/
│   │   │   ├── requirement_parsing_agent.py
│   │   │   ├── skill_matching_agent.py
│   │   │   ├── availability_checker_agent.py
│   │   │   ├── assignment_agent.py
│   │   │   ├── communication_agent.py
│   │   │   └── reporting_agent.py
│   │   ├── orchestrator/                 # multi-agent coordination + tracing
│   │   ├── providers/                    # bedrock.py, openai.py, hf.py, langchain.py
│   │   ├── tools/                        # shared tools: db, embeddings, vector store
│   │   ├── models/                       # pydantic schemas
│   │   ├── api/                          # FastAPI routes
│   │   ├── synthetic/                    # synthetic data generator (CLI)
│   │   └── observability/                # otel + prometheus instrumentation
│   └── tests/
│
├── Middleware/                           # Spring Boot microservices
│   ├── pom.xml                           # parent BOM + plugin mgmt
│   ├── common-lib/                       # shared DTOs, config, security
│   ├── api-gateway/                      # Spring Cloud Gateway + JWT
│   ├── employee-service/                 # employees, skills, profiles
│   ├── project-service/                  # projects + briefs
│   ├── allocation-service/               # allocations; calls Agents
│   ├── notification-service/             # email/slack (stub locally)
│   └── reporting-service/                # report read-models
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
├── SyntheticData/                        # generated JSON fixtures (gitignored except samples)
│   ├── samples/
│   └── README.md
│
├── DevOps/
│   ├── Local/
│   │   ├── docker-all-up.sh              # brings up Postgres → Observability → Agents → Middleware → Portals
│   │   ├── docker-all-down.sh
│   │   ├── docker-all-status.sh
│   │   ├── Postgres/
│   │   │   ├── docker-compose.yaml       # postgres:16 + pgvector + pgAdmin
│   │   │   └── init/
│   │   │       ├── 01-extensions.sql     # CREATE EXTENSION vector;
│   │   │       └── 02-schema.sql
│   │   ├── VectorDBs/                    # OPTIONAL alternative to pgvector
│   │   │   └── Qdrant/docker-compose.yaml
│   │   ├── Agents/
│   │   │   └── docker-compose.yaml
│   │   ├── Middleware/
│   │   │   └── docker-compose.yaml       # all 6 Spring Boot services
│   │   └── Portals/
│   │       └── docker-compose.yaml       # nginx + admin + customer portals
│   └── AWS/
│       └── Terraform/
│           ├── modules/
│           │   ├── vpc/
│           │   ├── bedrock/              # model-access policies
│           │   ├── sagemaker/            # studio + endpoints
│           │   ├── rds/                  # Postgres + pgvector
│           │   ├── ecs/                  # Fargate services
│           │   ├── cognito/              # auth for portals
│           │   └── cloudfront/           # static hosting for Angular
│           └── environments/dev/
│
├── Observability/
│   ├── Grafana/
│   │   ├── docker-compose.yaml
│   │   └── provisioning/
│   │       ├── datasources/
│   │       └── dashboards/
│   ├── Jaeger/
│   │   └── docker-compose.yaml           # all-in-one for local
│   └── Prometheus/
│       ├── docker-compose.yaml
│       └── prometheus.yml                # scrape targets: agents:9100, gateway:9100, …
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
| 1.1 | `DevOps/Local/Postgres/docker-compose.yaml` (postgres:16 + pgvector + pgAdmin) | [ ] |
| 1.2 | `init/01-extensions.sql` + `init/02-schema.sql` | [ ] |
| 1.3 | `Observability/Prometheus/` + `prometheus.yml` | [ ] |
| 1.4 | `Observability/Grafana/` + provisioned datasources + starter dashboards | [ ] |
| 1.5 | `Observability/Jaeger/docker-compose.yaml` (all-in-one) | [ ] |
| 1.6 | `DevOps/Local/VectorDBs/Qdrant/` (optional, alt to pgvector) | [-] |
| 1.7 | `DevOps/Local/docker-all-up.sh` / `down.sh` / `status.sh` (orchestrate above) | [ ] |
| 1.8 | Root `package.json` with start/stop/status scripts | [ ] |

### M2 — Data Layer & Synthetic Data (Category: Data)

| # | Task | Status |
|---|------|--------|
| 2.1 | Postgres schema: employees, skills, employee_skills, projects, project_briefs, availability, allocations, agent_runs, agent_steps, notifications, reports | [ ] |
| 2.2 | pgvector columns: `employees.profile_embedding`, `project_briefs.requirements_embedding` | [ ] |
| 2.3 | Synthetic data generator (Python CLI): 30–100 employees, 10–40 projects, unstructured briefs, calendars | [ ] |
| 2.4 | Embeddings backfill job (Bedrock Titan or HF MiniLM) | [ ] |
| 2.5 | Sample fixtures committed to `SyntheticData/samples/` | [ ] |

### M3 — Agents Layer (Category: AI / Agents)

| # | Task | Status |
|---|------|--------|
| 3.1 | `Agents/` Python project (`pyproject.toml`, ruff, pytest, otel) | [ ] |
| 3.2 | LLM provider interface + Bedrock impl (Claude Sonnet 4.6) | [ ] |
| 3.3 | Embedding provider interface + Bedrock Titan / HF MiniLM impls | [ ] |
| 3.4 | Vector store adapter (pgvector primary, Qdrant optional) | [ ] |
| 3.5 | Agent 1 — Requirement Parsing (structured JSON output via Strands tool calling) | [ ] |
| 3.6 | Agent 2 — Skill Matching (cosine similarity on pgvector + LLM rerank) | [ ] |
| 3.7 | Agent 3 — Availability Checker (DB-only, no LLM call) | [ ] |
| 3.8 | Agent 4 — Assignment (weighted score: relevance × priority × availability) | [ ] |
| 3.9 | Agent 5 — Communication (template + queue notification rows) | [ ] |
| 3.10 | Agent 6 — Reporting (LLM summarises allocation rationale) | [ ] |
| 3.11 | Orchestrator: sequential pipeline w/ persisted trace (`agent_runs`/`agent_steps`) | [ ] |
| 3.12 | FastAPI endpoints: `POST /allocations/run`, `GET /agent-runs/{id}`, `GET /reports/{id}` | [ ] |
| 3.13 | OpenTelemetry traces → Jaeger; Prometheus metrics | [ ] |
| 3.14 | Tests against synthetic data; measure paper's 4 metrics | [ ] |

### M4 — Middleware / Microservices (Category: Backend)

| # | Task | Status |
|---|------|--------|
| 4.1 | Parent `pom.xml` + `common-lib` (DTOs, security, error model) | [ ] |
| 4.2 | `employee-service` — CRUD + skills | [ ] |
| 4.3 | `project-service` — projects + briefs ingestion | [ ] |
| 4.4 | `allocation-service` — triggers Agents, persists results | [ ] |
| 4.5 | `notification-service` — consumes notification rows (email stub) | [ ] |
| 4.6 | `reporting-service` — read-model for Reports page | [ ] |
| 4.7 | `api-gateway` (Spring Cloud Gateway) + JWT validation | [ ] |
| 4.8 | Springdoc OpenAPI on every service | [ ] |
| 4.9 | OpenTelemetry agent in each Dockerfile | [ ] |
| 4.10 | `DevOps/Local/Middleware/docker-compose.yaml` | [ ] |

### M5 — Portals (Category: Frontend)

| # | Task | Status |
|---|------|--------|
| 5.1 | `Portals/admin-portal` — Angular 18 scaffold + Tailwind | [ ] |
| 5.2 | Admin: Employees CRUD page | [ ] |
| 5.3 | Admin: Projects + Briefs page | [ ] |
| 5.4 | Admin: Allocations page (trigger + result view) | [ ] |
| 5.5 | Admin: **Agent Monitor** — live trace of 6 agents (SSE/WebSocket) | [ ] |
| 5.6 | Admin: Reports page (paper's 4 metrics + LLM rationale) | [ ] |
| 5.7 | `Portals/projects-portal` — Angular 18 scaffold | [ ] |
| 5.8 | Customer: Submit Brief page | [ ] |
| 5.9 | Customer: My Projects + status | [ ] |
| 5.10 | Customer: Notifications inbox | [ ] |
| 5.11 | Auth wiring (JWT issued by Spring; Cognito in M7) | [ ] |
| 5.12 | `DevOps/Local/Portals/docker-compose.yaml` (nginx-served) | [ ] |

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
