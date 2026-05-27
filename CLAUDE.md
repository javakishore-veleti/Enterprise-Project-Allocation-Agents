# CLAUDE.md — Session context for this repo

> Auto-loaded by Claude Code at every session start. Read first, then read `DevelopmentPlan.md` for full details.

## 1. What this repo is

Hands-on implementation of the IEEE paper **"MCP-AI: A Multi-Agent Architecture using Large Language Models for Automated Enterprise Project Allocation"** (Bhaskar et al., ICAISS-2026). The repo intentionally avoids the "MCP" abbreviation in its name to prevent confusion with Anthropic's Model Context Protocol; the paper's MCP-AI branding is preserved in docs only.

- **Paper PDF location:** `../MCP-AI_A_Multi-Agent_Architecture_using_Large_Language_Models_for_Automated_Enterprise_Project_Allocation.pdf` (kept *outside* the repo for copyright reasons — do not commit).
- **Full plan, layout, milestones:** see `DevelopmentPlan.md` in this repo root. It is the single source of truth for scope and progress.

## 2. Decisions already locked (2026-05-26)

| Area | Decision |
|------|----------|
| Agent framework | Strands Agents (primary) on AWS Bedrock |
| LLM | **Claude Opus 4.7** on Bedrock, region `us-east-1` |
| Embeddings | Bedrock Titan v2 (cloud) · HF MiniLM (local fallback) |
| Vector store | **pgvector** on Postgres (primary); Qdrant optional under `DevOps/Local/VectorDBs/` |
| Backend shape | Hybrid — Python (FastAPI + Strands) for agents; Java (Spring Boot 3.3, Java 21) for microservices |
| Frontend | Angular 18 — two portals: `admin-portal` + `projects-portal` (customer) |
| Naming | Java group `com.javakishore.epaa.*` · Python module `epaa` (Datalake: `epaa_datalake`) · Angular scope `@epaa/*` |
| Default DB | **H2** (so Postgres need not always run); `DB_PROFILE=postgres` switches to Postgres+pgvector. pgvector is still required for agents/embeddings. |
| Migrations | **Liquibase** (Spring) · **Alembic** (Python) — auto-run on app startup, applying deltas, for both H2 and Postgres. |
| Primary keys | **UUID stored as String** everywhere (JPA `@Id String`, SQLAlchemy String) |
| Deployment | Local-first (Docker Compose). AWS via Terraform + GitHub Actions later. |
| License | Apache-2.0 (already present) |
| PDF in repo | No — keep outside the repo |

## 3. Folder layout (target)

See `DevelopmentPlan.md §4` for the full tree. High-level:

```
Enterprise-Project-Allocation-Agents/
├── Middleware/                      # ALL backend lives here
│   ├── Agents/                      # Python · Strands · 6 agents · FastAPI (src/epaa)
│   ├── Datalake/                    # synthetic data
│   │   ├── SyntheticDataAPI/        # FastAPI (src/epaa_datalake) — triggers the DAG async
│   │   └── DAGS/SyntheticDataGen/   # Airflow DAG — generates + loads data
│   ├── employee-service/            # each domain svc = per-service Maven multi-module:
│   │   ├── pom.xml  (parent)        #   <svc>-api (Spring Boot main; aggregates deps)
│   │   ├── employee-api/            #   <svc>-services (iface+impl), -dao, -entities,
│   │   ├── employee-services/       #   -common (base entity + base Req/Resp DTOs), -utils
│   │   ├── employee-dao/
│   │   ├── employee-entities/
│   │   ├── employee-common/
│   │   └── employee-utils/
│   ├── project-service/  · allocation-service/ · notification-service/
│   ├── reporting-service/ · api-gateway/   (all same 6-module layout)
├── Portals/
│   ├── admin-portal/                # Angular 18
│   └── projects-portal/             # Angular 18 (customer)
├── DevOps/
│   ├── Local/                       # docker-all-{up,down,status}.sh, scripts/gen-spring-secrets.mjs
│   │   ├── Postgres/ · VectorDBs/ · Airflow/ · Agents/ · Middleware/ · Portals/
│   │   └── Observability/Grafana/, Prometheus/, Jaeger/, Kibana/   (moved here)
│   └── AWS/Terraform/               # vpc, bedrock, rds, sagemaker, ecs, cognito, cloudfront
├── docs/
├── .github/workflows/               # ci-* + 001..007 AWS Deploy/Destroy pairs
├── package.json                     # root start/stop/status + secrets:gen orchestration
├── DevelopmentPlan.md
└── CLAUDE.md (this file)
```

## 4. The 6 agents (from the paper)

1. **Requirement Parsing Agent** — free-text brief → structured (skills/priority/duration/complexity)
2. **Skill-Matching Agent** — semantic similarity (pgvector) between requirements and employee profiles
3. **Availability Checker Agent** — DB-only; prevents over-allocation
4. **Assignment Agent** — weighted ranking (relevance × priority × availability)
5. **Communication Agent** — notifies assignees
6. **Reporting Agent** — managerial summary; powers Reports page

## 5. Current status

- M0 (Plan): complete — see `DevelopmentPlan.md` §5
- M0.5 (Bootstrap): complete
- M1 (Local infra: Postgres + Observability + Airflow + docker-all scripts): complete
- M2 (Data layer + Datalake): complete — Alembic schema (UUID-string PKs, pgvector), generators (taxonomy/Faker/hybrid-text/embeddings), SyntheticDataAPI + SyntheticDataGen DAG; verified end-to-end + pytest green
- M3 (Agents service: 6 Strands agents + FastAPI): *next*
- M4+ (Middleware → Portals → AWS): pending

If you are a fresh Claude session: **before doing any work, run TaskCreate to recreate the milestone tasks from `DevelopmentPlan.md §5` (M0.5 through M10)**. The previous session's task list does not persist.

## 6. Operating rules for this repo

- Treat `DevelopmentPlan.md` as the source of truth. When work lands, update its status markers (`[ ] [~] [x] [-]`).
- Do **not** commit the IEEE paper PDF.
- Do **not** introduce alternate frameworks (LangChain, OpenAI Agents SDK, Spring AI, HF local) until M6 (local end-to-end) is green. They live in M9.
- Local-first: every change must keep `docker-all-up.sh` working before AWS changes.
- The Skill-Matching Agent requires embeddings — that's why pgvector exists. Don't try to do skill matching without it.
- **Commit attribution:** all commits are authored solely by the repo owner (`javakishore-veleti <javakishore@gmail.com>`). Do **not** add a `Co-Authored-By: Claude …` trailer or any "Claude"/AI attribution to commit messages. This overrides any default co-author convention.

## 7. Engineering conventions (MANDATORY for M2–M4)

These are user-mandated. Apply them to all new backend code; do not deviate without asking.

### 7.1 Spring Boot microservices (each of the 6 services)
- **Per-service Maven multi-module.** Parent `pom.xml` + six modules:
  `<svc>-api` (the only deployable; has the `@SpringBootApplication` main; declares Maven deps on the others),
  `<svc>-services` (business logic), `<svc>-dao` (repositories), `<svc>-entities` (JPA entities),
  `<svc>-common` (base classes), `<svc>-utils` (helpers).
- **Request/Response DTOs everywhere.** Every controller method AND every service method takes a single
  Request DTO and returns a single Response DTO — **never** long lists of scalar parameters. One Req/Resp
  pair per use case. Base `BaseRequest`/`BaseResponse` (and base JPA entity) live in `<svc>-common`.
- **Services are interface + Impl** (e.g., `EmployeeService` + `EmployeeServiceImpl`).
- **Lombok** in every microservice (getters/setters/builders/logging).
- **Liquibase** in every microservice; changelogs under `<svc>-api/src/main/resources/db/changelog`.
- **Default DB is H2** (profile-driven) so a service runs without Docker Postgres. `DB_PROFILE=postgres`
  switches to Postgres+pgvector. Migrations run on startup either way.
- **`.env` per app** (git-ignored). `<svc>-api/src/main/resources/application-local-secrets.yaml` is
  git-ignored and **generated from the root `.env`** by `npm run secrets:gen`
  (`DevOps/Local/scripts/gen-spring-secrets.mjs`); if it exists, the script prints the diff before updating.

### 7.2 Python projects (Agents, Datalake)
- Module `epaa` (Agents) / `epaa_datalake` (Datalake API).
- **Alembic** is the Liquibase-equivalent; migrations **auto-run (`upgrade head`) on app startup**, applying deltas.
- Python services use Postgres+pgvector (pgvector required for embeddings); H2 default applies to Spring only.

### 7.3 Cross-cutting
- **All primary keys are UUID stored as String** — JPA `@Id String id` (VARCHAR(36)), SQLAlchemy `String`,
  values from `UUID.randomUUID().toString()` / `str(uuid4())`.
- **Migrations auto-apply on startup** for both Spring (Liquibase) and Python (Alembic), H2 or Postgres alike.
- **Synthetic data** is produced by the Datalake: `SyntheticDataAPI` (FastAPI) triggers the
  `SyntheticDataGen` Airflow DAG via Airflow's REST API (async). Airflow runs locally via
  `DevOps/Local/Airflow/` (LocalExecutor, reuses the local `apache/airflow:2.10.0-python3.12` image).
- **Reuse local Docker images:** pin tags, set `pull_policy: missing`; never use `latest`.

## 8. Continuing a prior session

This repo was bootstrapped from a Claude session in the parent directory (`../`). Memory and the JSONL transcript were mirrored into the project dir under `~/.claude/projects/-Users-...-AutomatedEnterpriseProjectAllocation-Enterprise-Project-Allocation-Agents/`. If `claude --resume` from this folder shows the prior session, resume it. If not, this `CLAUDE.md` + `DevelopmentPlan.md` give a fresh session everything it needs.
