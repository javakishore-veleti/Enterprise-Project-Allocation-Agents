# Enterprise Project Allocation Agents

A hands-on implementation of the IEEE paper **"MCP-AI: A Multi-Agent Architecture using Large Language Models for Automated Enterprise Project Allocation"** (Bhaskar et al., ICAISS-2026).

> The repo name avoids the "MCP" abbreviation to prevent confusion with Anthropic's Model Context Protocol. The paper's *MCP-AI* branding is preserved in the docs only.

Free-text project briefs go in; an LLM-driven team of six autonomous agents parses requirements, matches them to employee skills via semantic similarity, checks availability, ranks and assigns the team, notifies assignees, and produces a managerial report — with the whole run traceable end to end.

---

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
- [docs/demo.md](docs/demo.md) — run guide & walkthrough
- [docs/Design/](docs/Design/) — multi-tab draw.io (overall + per-agent diagrams)
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
