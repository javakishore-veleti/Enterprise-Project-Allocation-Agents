# Enterprise Project Allocation Agents

A hands-on implementation of the IEEE paper **"MCP-AI: A Multi-Agent Architecture using Large Language Models for Automated Enterprise Project Allocation"** (Bhaskar et al., ICAISS-2026).

> The repo name avoids the "MCP" abbreviation to prevent confusion with Anthropic's Model Context Protocol. The paper's *MCP-AI* branding is preserved in the docs only.

Free-text project briefs go in; an LLM-driven team of six autonomous agents parses requirements, matches them to employee skills via semantic similarity, checks availability, ranks and assigns the team, notifies assignees, and produces a managerial report — with the whole run traceable end to end.

---

## Table of contents

- [The six agents](#the-six-agents)
- [Architecture at a glance](#architecture-at-a-glance)
- [Tech stack](#tech-stack)
- [Multi-agent orchestration frameworks](#multi-agent-orchestration-frameworks)
- [Repository layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Configuration (.env)](#configuration-env)
- [First time running the application](#first-time-running-the-application)
- [Daily running](#daily-running)
- [npm scripts reference](#npm-scripts-reference)
- [Documentation](#documentation)
- [Status](#status)
- [License](#license)

## The six agents

| # | Agent | Responsibility |
|---|-------|----------------|
| 1 | **Requirement Parsing** | Free-text brief → structured (skills, priority, duration, complexity) |
| 2 | **Skill-Matching** | Semantic similarity (pgvector) between requirements and employee profiles |
| 3 | **Availability Checker** | DB-only; prevents over-allocation / scheduling conflicts |
| 4 | **Assignment** | Weighted ranking (relevance × priority × availability) |
| 5 | **Communication** | Notifies the assigned staff |
| 6 | **Reporting** | Managerial summary; powers the Reports page |

## Architecture at a glance

```
 Angular portals  ─►  API Gateway  ─►  Spring Boot microservices  ─►  Postgres + pgvector
 (admin + customer)   (Spring Cloud)    (employee/project/alloc/…)         ▲
                                              │                            │
                                              └──►  Agents service  ───────┘
                                                    (Python · Strands · Bedrock · 6 agents)

 Observability: OpenTelemetry → Jaeger (traces) · Prometheus + Grafana (metrics)
```

Full architecture, folder layout, and the milestone roadmap live in **[DevelopmentPlan.md](./DevelopmentPlan.md)**.

## Tech stack

| Layer | Choice |
|-------|--------|
| Agents | Python 3.12 · **Strands Agents** · FastAPI |
| LLM | **Claude Opus 4.7** on AWS Bedrock (`us-east-1`) |
| Embeddings | Bedrock Titan v2 (cloud) · HF MiniLM (local fallback) |
| Vector store | **pgvector** on Postgres (Qdrant optional) |
| Microservices | Java 21 · Spring Boot 3.3 · Spring Cloud Gateway |
| Portals | Angular 18 — `admin-portal` + `projects-portal` |
| Observability | Prometheus · Grafana · Jaeger · OpenTelemetry |
| Local orchestration | Docker Compose + shell scripts + root `package.json` |
| Cloud (later) | Terraform + GitHub Actions (VPC, Bedrock, RDS, SageMaker, ECS, Cognito, CloudFront) |

## Multi-agent orchestration frameworks

The agents reason through one swappable `complete()` interface, so the framework is a
config switch (`LLM_PROVIDER`). Today the multi-agent *orchestration* is a custom
sequential pipeline; **v2 moves it to LangGraph** (see [Status](#status)). For reference,
the popular options as of early 2026 (fuller writeup in
[docs/agent-frameworks.md](docs/agent-frameworks.md)):

### Code-first frameworks (Python-centric)

| Framework | Owner | Orchestration model | Best for |
|-----------|-------|---------------------|----------|
| **LangGraph** | LangChain | Stateful graph (nodes/edges, cycles, checkpointing) | Complex, controllable multi-agent flows; durable state |
| **CrewAI** | CrewAI | Role-based "crews" + tasks | Quick role-playing agent teams; opinionated |
| **OpenAI Agents SDK** | OpenAI | Lightweight handoffs + guardrails | OpenAI-model apps; simple, production-minded |
| **Microsoft Agent Framework** | Microsoft | AutoGen group-chat + Semantic Kernel | Enterprise .NET/Python |
| **Strands Agents** | AWS | Model-driven agent loop + tools | AWS/Bedrock-native, lightweight (this repo's default) |
| **Google ADK** | Google | Hierarchical agents + A2A | Gemini/Vertex; multi-agent services |
| **LlamaIndex Workflows** | LlamaIndex | Event-driven workflows | RAG-heavy agent apps |
| **Pydantic AI** | Pydantic | Type-safe agents + graphs | Strongly-typed, testable agents |
| **Haystack** | deepset | Pipelines + agents | RAG + production search |
| **Agno**, **Atomic Agents** | community | Lightweight agent teams | Minimal prototyping |

### Managed / platform offerings

- **Amazon Bedrock Agents** (+ multi-agent collaboration) — AWS managed
- **Vertex AI Agent Builder / Agent Engine** — Google managed
- **Azure AI Foundry Agent Service** — Microsoft managed
- **LangGraph Platform** (LangSmith) — hosting/observability for LangGraph

### Cross-cutting protocols (interop, not orchestrators)

- **MCP (Model Context Protocol)** — Anthropic; standardizes tools/context
- **A2A (Agent2Agent)** — Google-led; agent-to-agent communication across frameworks

### How this maps to this project

- **Default**: Strands Agents on Bedrock (designated), with **LangChain**, **OpenAI SDK**, and **Ollama/HF** wired as swappable LLM backends (`docs/adapters.md`).
- **Orchestration today**: a hand-rolled sequential pipeline + custom trace persistence.
- **v2 (in progress)**: a **LangGraph** orchestrator (graph + shared state + conditional routing), selected by an `ORCHESTRATOR` env var, running side-by-side with v1.

## Repository layout

```
.
├── Middleware/                 # ALL backend
│   ├── Agents/                 # Python · Strands · 6 agents · FastAPI
│   ├── Datalake/               # SyntheticDataAPI (FastAPI) + DAGS/SyntheticDataGen (Airflow)
│   ├── employee-service/       # each domain svc = per-service Maven multi-module
│   ├── project-service/  · allocation-service/  · notification-service/
│   ├── reporting-service/  · api-gateway/
├── Portals/                    # admin-portal/ + projects-portal/ (Angular 18)
├── DevOps/
│   ├── Local/                  # docker-all-{up,down,status}.sh, scripts/, per-area compose
│   │   └── Observability/      # Grafana/ · Prometheus/ · Jaeger/ · Kibana/
│   └── AWS/Terraform/          # IaC modules
├── docs/
├── .github/workflows/          # CI + numbered AWS Deploy/Destroy pairs
├── package.json                # root start/stop/status + secrets:gen orchestration
├── DevelopmentPlan.md          # source of truth for scope & progress
└── CLAUDE.md                   # session context for AI-assisted work
```

## Prerequisites

The repo is **local-first** — the whole stack runs in Docker, orchestrated from the
root `package.json`. You need:

- **Docker** + Docker Compose (running)
- **Node.js 20+** and **npm** (to run the root `package.json` scripts)
- Bedrock (Claude Opus 4.7, `us-east-1`) is only needed for *live* LLM/embeddings — the
  agents fall back to an offline heuristic + hash embeddings, and the Spring services
  default to **H2**, so Postgres is only required for the agents/embeddings + Datalake.
- Optional for non-Docker dev only: Python 3.12, JDK 21 (the container images build
  those internally, so you don't need them on the host for `npm start`).

Default ports: `8080` gateway · `4200`/`4201` portals · `5432` Postgres · `8000`
Datalake · `8001` Agents · `8088` Airflow · `16686` Jaeger · `3000` Grafana · `5050` pgAdmin.

## Configuration (`.env`)

`.env` (git-ignored) is created from `.env.example` — the start scripts also auto-create
it if missing. **It runs as-is with no edits**: with no AWS credentials the agents fall
back to an offline heuristic LLM + hash embeddings, and the Spring services default to
in-memory H2. Edit `.env` only to enable live Bedrock or to change a default. The
settings that matter most:

| Variable | Default | What it controls |
|----------|---------|------------------|
| `DB_PROFILE` | `h2` | Spring DB: `h2` (in-memory, no Postgres needed) or `postgres`. Agents/Datalake always use Postgres+pgvector regardless. |
| `LLM_PROVIDER` | `auto` | Reasoning LLM backend: `auto` / `strands` / `bedrock` / `langchain` / `openai` / `ollama` / `heuristic`. Falls back to offline `heuristic` with no AWS. |
| `EMBEDDING_PROVIDER` | `bedrock` | Skill-matching embeddings: `bedrock` (Titan v2), `hf` (MiniLM), or `hash` (offline deterministic). |
| `ORCHESTRATOR` | `custom` | Pipeline engine: `custom` (hand-rolled v1) or `langgraph` (v2 graph; needs the langgraph extra). |
| `AWS_REGION` / `AWS_PROFILE` | `us-east-1` / `default` | AWS region + credentials profile — only needed for live Bedrock. |
| `BEDROCK_MODEL_ID` | Claude Opus 4.7 | Bedrock reasoning model id. |
| `BEDROCK_EMBEDDING_MODEL_ID` | Titan v2 | Bedrock embeddings model id. |
| `POSTGRES_HOST/PORT/DB/USER/PASSWORD` | `localhost`/`5432`/`epaa`/`epaa`/… | Postgres connection (agents/Datalake always; Spring when `DB_PROFILE=postgres`). Set a real password. |
| `*_PORT` (gateway, portals, services, observability, Airflow) | see `.env.example` | Host ports — change any that clash locally. |
| `NOTIFICATION_CHANNEL` | `log` | Communication Agent delivery: `log` (local stub) or SES (AWS). |

> **Fully offline (no AWS):** set `LLM_PROVIDER=heuristic` and `EMBEDDING_PROVIDER=hash`.
> **Live Bedrock:** set `AWS_PROFILE`/`AWS_REGION` (with valid credentials) and keep
> `LLM_PROVIDER=auto` (or `bedrock`) + `EMBEDDING_PROVIDER=bedrock`.

`application-local-secrets.yaml` for the Spring services is generated from `.env` by
`npm run secrets:gen` (run automatically as part of `local:apps:middleware:start-all`).

## First time running the application

Run these **once** to bootstrap, then switch to [Daily running](#daily-running):

```bash
# 1. Create your env file (runs as-is; see "Configuration (.env)" above for what to edit)
cp .env.example .env

# 2. Start the docker backing layer (postgres, observability, airflow, vectordb, datalake, agents)
npm run local:docker:start-all

# 3. Start the apps (middleware + portals; runs secrets:gen first)
npm run local:apps:start-all
#    — shortcut for steps 2 + 3 together: npm start

# 4. Confirm health, then open the portals
npm run status
#    Admin portal     → http://localhost:4200
#    Customer portal  → http://localhost:4201
#    API gateway      → http://localhost:8080
#    Jaeger UI        → http://localhost:16686
#    Grafana          → http://localhost:3000
```

Migrations auto-apply on startup (Liquibase for Spring, Alembic for Python) for both H2
and Postgres, so the stack is usable as soon as it reports healthy.

**Seed synthetic data from the Admin portal** (the intended flow): open
**Data Management → Synthetic Data**, pick the *SyntheticDataGen* workflow from the
searchable dropdown, set your criteria, and click **Initiate Execution** — this triggers
the Airflow DAG via the Datalake API (`POST /synthetic/generate`) and the run appears
under **History**. (Headless shortcut for the same endpoint: `npm run seed`.)

## Daily running

Everything is controlled through the root `package.json` — **one command boots all six
microservices and both portals** (no need to start anything individually):

```bash
npm start            # FULL stack: docker backing layer + apps (all microservices + both portals)
npm run status       # health of every container + handy local URLs
npm stop             # stop & tear down the full stack

# Or control the two layers independently:
npm run local:docker:start-all   # backing services only (postgres, observability, airflow, vectordb, datalake, agents)
npm run local:apps:start-all     # the apps only — runs middleware:start-all then portals:start-all
npm run local:apps:stop-all      # stop just the apps (e.g. to rebuild) while backing services keep running
npm run local:docker:stop-all    # stop just the backing services
```

> Fastest sanity check: `bash DevOps/Local/smoke-test.sh` runs the paper's core flow
> (Postgres + Datalake + Agents) end-to-end in containers. See [docs/demo.md](docs/demo.md).

## npm scripts reference

All scripts run from the repo root and wrap `DevOps/Local/docker-all-{up,down,status}.sh`.
The stack is split into two layers — the **docker** backing services and the **apps** —
so `npm start` = `local:docker:start-all` + `local:apps:start-all`:

| Script | Action |
|--------|--------|
| `npm start` / `npm stop` | **full stack** up / down (`local:docker:*` then `local:apps:*`) |
| `npm run status` | container health + local URLs |
| `npm run seed` | headless shortcut to seed synthetic data — same `POST /synthetic/generate` the Admin portal's **Data Management → Initiate Execution** triggers |
| `npm run secrets:gen` | regenerate `application-local-secrets.yaml` from `.env` |
| **Docker backing layer** | |
| `npm run local:docker:start-all` / `:stop-all` | all backing containers (postgres, observability, airflow, vectordb, datalake, agents) |
| `npm run local:docker:postgres:start` / `:stop` | Postgres + pgvector + pgAdmin |
| `npm run local:docker:observability:start` / `:stop` | Prometheus + Jaeger + Grafana + Kibana |
| `npm run local:docker:airflow:start` / `:stop` | Airflow (Datalake DAG runtime) |
| `npm run local:docker:vectordb:start` / `:stop` | Qdrant (optional, alt to pgvector) |
| `npm run local:docker:datalake:start` / `:stop` | SyntheticDataAPI (FastAPI) |
| `npm run local:docker:agents:start` / `:stop` | Python agents service |
| **Application layer** | |
| `npm run local:apps:start-all` / `:stop-all` | all apps — internally runs middleware then portals |
| `npm run local:apps:middleware:start-all` / `:stop-all` | the 6 Spring Boot services + API gateway (runs `secrets:gen` first) |
| `npm run local:apps:portals:start-all` / `:stop-all` | both Angular portals (admin + customer) |

## Documentation

- [docs/architecture.md](docs/architecture.md) — components, layers, allocation flow
- [docs/agents.md](docs/agents.md) — the 6 agents, scoring, LLM/embedding providers
- [docs/api-contracts.md](docs/api-contracts.md) — gateway routes + service REST contracts
- [docs/data-model.md](docs/data-model.md) — Postgres schema & ownership
- [docs/adapters.md](docs/adapters.md) — pluggable LLM backends + orchestrator (custom vs LangGraph)
- [docs/agent-frameworks.md](docs/agent-frameworks.md) — multi-agent framework landscape & selection guide
- [docs/datalake-design.md](docs/datalake-design.md) — synthetic-data reality vs. target datalake/vector-KB design
- [docs/demo.md](docs/demo.md) — run guide & walkthrough
- [docs/Design/](docs/Design/) — multi-tab draw.io (business + overall + triggers + per-agent diagrams)
- [DevelopmentPlan.md](DevelopmentPlan.md) — full milestone plan & status

## Status

Milestones **M0–M8 complete** — synthetic data, the 6-agent pipeline, 6 Spring Boot
microservices, both Angular portals, the containerized end-to-end smoke test, AWS
Terraform + GitHub Actions, and green CI. Deferred/open: alternate-framework adapters
(M9), UI screenshots, OTel dashboards, and a real AWS apply. Track everything in
**[DevelopmentPlan.md §5](./DevelopmentPlan.md)** — each task carries a `[ ] / [~] / [x] / [-]` marker.

## License

[Apache-2.0](./LICENSE).

## Acknowledgement

This is an educational re-implementation of the cited IEEE paper for hands-on learning. The paper PDF is **not** included in this repository (copyright).
