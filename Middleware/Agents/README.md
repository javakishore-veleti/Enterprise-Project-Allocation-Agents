# Agents

The six MCP-AI autonomous agents (Strands + Bedrock) and the FastAPI orchestrator.

| # | Agent | LLM? | What it does |
|---|-------|------|--------------|
| 1 | Requirement Parsing | yes (fallback: heuristic) | brief text → `{skills, priority, complexity, duration, headcount}` |
| 2 | Skill Matching | no (embeddings) | pgvector cosine similarity + required-skill overlap → ranked candidates |
| 3 | Availability Checker | no | drops unavailable; annotates availability factor |
| 4 | Assignment | no | `w_rel·relevance + w_pri·priority + w_avail·availability` → writes allocations |
| 5 | Communication | no | queues a notification per assignee |
| 6 | Reporting | yes (fallback: template) | managerial summary + the paper's metrics |

The orchestrator runs them in order and persists a full trace to `agent_runs` /
`agent_steps`, plus `allocations`, `notifications`, and a `reports` row.

## LLM resolution

`LLM_PROVIDER` = `auto` (Strands → Bedrock → heuristic) · `strands` · `bedrock` · `heuristic`.
With nothing configured the pipeline runs fully offline (heuristic parse + hash
embeddings), so it works with no AWS. Install the `strands` extra for real LLM use.

## Run

```bash
# install the shared data layer + this package
pip install ../Datalake/SyntheticDataAPI .

# seed data first (see Datalake), then run the pipeline for a project
epaa-agents run --any            # pick any project that has a brief
epaa-agents run --project-id <uuid>
```

## API

- `POST /allocations/run` `{ "project_id": "<uuid>" }` → run summary + assignments + report
- `GET /agent-runs/{run_id}` → full step-by-step trace
- `GET /reports/{project_id}` → latest managerial report

## Notes

- Shares the schema with `epaa_datalake`; this service does **not** run migrations
  (the Datalake owns them). It reads employees/briefs and writes allocations/runs/reports.
- Embeddings come from `epaa_datalake.generators.embeddings` (same provider selection).
