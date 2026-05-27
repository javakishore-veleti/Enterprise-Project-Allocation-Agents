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
- [Quick start (local)](#quick-start-local)
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
the popular options as of early 2026:

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

## Quick start (local)

> Prerequisites: Docker, Node 20+, Python 3.12, JDK 21. Bedrock (Claude Opus 4.7, `us-east-1`) is
> needed for the agents and for LLM-generated synthetic text; the Spring services default to **H2**, so
> Postgres is only required for the agents/embeddings + Datalake.

```bash
# 1. Configure environment (the start script also auto-creates .env if missing)
cp .env.example .env          # then fill in AWS values

# 2. Bring everything up (infra → airflow → agents → middleware → portals).
#    secrets:gen runs first (prestart) to materialise application-local-secrets.yaml.
npm run start

# 3. Seed synthetic data — triggers the SyntheticDataGen Airflow DAG via the Datalake API
npm run seed

# 4. Open the portals
#    Admin portal     → http://localhost:4200
#    Customer portal  → http://localhost:4201
#    Jaeger UI        → http://localhost:16686
#    Grafana          → http://localhost:3000

# Stop / check status
npm run stop
npm run status
```

> Fastest path: `bash DevOps/Local/smoke-test.sh` runs the paper's core flow
> (Postgres + Datalake + Agents) end-to-end in containers. See [docs/demo.md](docs/demo.md).

## Documentation

- [docs/architecture.md](docs/architecture.md) — components, layers, allocation flow
- [docs/agents.md](docs/agents.md) — the 6 agents, scoring, LLM/embedding providers
- [docs/api-contracts.md](docs/api-contracts.md) — gateway routes + service REST contracts
- [docs/data-model.md](docs/data-model.md) — Postgres schema & ownership
- [docs/adapters.md](docs/adapters.md) — pluggable LLM framework adapters
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
