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
| Naming | Java group `com.javakishore.epaa.*` · Python module `epaa` · Angular scope `@epaa/*` |
| Deployment | Local-first (Docker Compose). AWS via Terraform + GitHub Actions later. |
| License | Apache-2.0 (already present) |
| PDF in repo | No — keep outside the repo |

## 3. Folder layout (target)

See `DevelopmentPlan.md §4` for the full tree. High-level:

```
Enterprise-Project-Allocation-Agents/
├── Agents/             # Python · Strands · 6 agents · FastAPI
├── Middleware/         # Spring Boot microservices (api-gateway, employee-, project-, allocation-, notification-, reporting-service, common-lib)
├── Portals/
│   ├── admin-portal/        # Angular 18
│   └── projects-portal/     # Angular 18 (customer)
├── SyntheticData/
├── DevOps/
│   ├── Local/               # docker-all-{up,down,status}.sh, Postgres/, VectorDBs/, Middleware/, Agents/, Portals/
│   └── AWS/Terraform/       # vpc, bedrock, rds, sagemaker, ecs, cognito, cloudfront modules
├── Observability/Grafana/, Jaeger/, Prometheus/
├── docs/
├── .github/workflows/       # ci-* + 001..007 AWS Deploy/Destroy pairs
├── package.json             # root start/stop/status orchestration
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
- M0.5 (Bootstrap): *next* — README expansion, .gitignore expansion, .env.example, root `package.json`
- M1+ (Local infra → Portals → AWS): pending

If you are a fresh Claude session: **before doing any work, run TaskCreate to recreate the milestone tasks from `DevelopmentPlan.md §5` (M0.5 through M10)**. The previous session's task list does not persist.

## 6. Operating rules for this repo

- Treat `DevelopmentPlan.md` as the source of truth. When work lands, update its status markers (`[ ] [~] [x] [-]`).
- Do **not** commit the IEEE paper PDF.
- Do **not** introduce alternate frameworks (LangChain, OpenAI Agents SDK, Spring AI, HF local) until M6 (local end-to-end) is green. They live in M9.
- Local-first: every change must keep `docker-all-up.sh` working before AWS changes.
- The Skill-Matching Agent requires embeddings — that's why pgvector exists. Don't try to do skill matching without it.

## 7. Continuing a prior session

This repo was bootstrapped from a Claude session in the parent directory (`../`). Memory and the JSONL transcript were mirrored into the project dir under `~/.claude/projects/-Users-...-AutomatedEnterpriseProjectAllocation-Enterprise-Project-Allocation-Agents/`. If `claude --resume` from this folder shows the prior session, resume it. If not, this `CLAUDE.md` + `DevelopmentPlan.md` give a fresh session everything it needs.
