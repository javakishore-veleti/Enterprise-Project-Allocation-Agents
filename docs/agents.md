# The six agents

Implemented in `Middleware/Agents/src/epaa/agents/`, run in order by the
orchestrator (`orchestrator.py`). LLM-driven agents use Strands → Bedrock and fall
back to deterministic heuristics so the pipeline runs offline (`LLM_PROVIDER=heuristic`,
`EMBEDDING_PROVIDER=hash`).

| # | Agent | Uses LLM? | Input → Output |
|---|-------|-----------|----------------|
| 1 | Requirement Parsing | yes (fallback heuristic) | `brief_text` → `{required_skills, priority, complexity, duration_weeks, headcount}` |
| 2 | Skill Matching | no (embeddings) | parsed reqs + brief embedding → ranked candidates |
| 3 | Availability Checker | no | candidates → available candidates (drops `unavailable`) |
| 4 | Assignment | no | available candidates → persisted `allocations` |
| 5 | Communication | no | assignments → `notifications` rows |
| 6 | Reporting | yes (fallback template) | run context → `reports` row + metrics |

## 1. Requirement Parsing
Prompts the LLM for strict JSON; the heuristic fallback matches the skill taxonomy
against the brief text and regexes the numbers (`N weeks`, `team of about N`,
priority keyword), backfilling from the project row. Persists `brief.parsed_requirements`.

## 2. Skill Matching
Shortlists the top-K employees by pgvector **cosine distance** between the brief's
`requirements_embedding` and each `employees.profile_embedding`, then blends semantic
similarity (0.7) with required-skill overlap (0.3) into a `relevance` score.

## 3. Availability Checker
DB-only. Drops candidates whose `availability_state` is `unavailable` and annotates an
availability factor (`available`→1.0, `partially_occupied`→0.6). Counts conflicts avoided.

## 4. Assignment
`final_score = w_rel·relevance + w_pri·priority_weight + w_avail·availability_factor`
(weights in `config.py`). Ranks, takes the top `headcount`, writes `allocations`
(status `assigned`, with a human-readable `rationale`).

## 5. Communication
Queues a `notifications` row per assignee (channel `log` locally; `notification-service`
delivers). Links each to its allocation id.

## 6. Reporting
Writes a `reports` row: an LLM (or template) summary plus `metrics_json` holding the
paper's metrics — allocation time (ms), candidates evaluated, conflicts avoided,
headcount requested/assigned, average relevance.

## Trace

Every run creates an `agent_runs` row and one `agent_steps` row per agent (sequence,
output, timing, status), surfaced by `GET /agent-runs/{id}` and the admin Agent Monitor.

## LLM / embedding providers

`LLM_PROVIDER` = `auto` (Strands→Bedrock→heuristic) · `strands` · `bedrock` · `heuristic`.
`EMBEDDING_PROVIDER` = `bedrock` (Titan v2) · `hf` (MiniLM) · `hash` (offline). Failures
degrade gracefully to the offline path.
