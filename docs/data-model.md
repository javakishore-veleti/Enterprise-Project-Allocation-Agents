# Data model (Postgres `epaa` schema)

All primary keys are UUID stored as `VARCHAR(36)`; every table has `created_at`.
Owned by the Datalake (Alembic baseline `0001` + delta `0002`).

## Domain

```
employees ──< employee_skills >── skills
employees ──< availability
projects  ──1 project_briefs
projects  ──< allocations >── employees
projects  ──< agent_runs ──< agent_steps
projects  ──< reports
employees ──< notifications >── allocations
```

| Table | Key columns |
|-------|-------------|
| `employees` | full_name, title, seniority, years_experience, performance_score, availability_state, capacity_hours_per_week, profile_text, **profile_embedding** `vector(1024)` |
| `skills` | name (unique), category |
| `employee_skills` | employee_id→, skill_id→, proficiency (1–5), years (unique emp+skill) |
| `projects` | name, client_name, priority, complexity, duration_weeks, required_headcount, start_date, status |
| `project_briefs` | project_id→, brief_text, parsed_requirements `json`, **requirements_embedding** `vector(1024)` |
| `availability` | employee_id→, start_date, end_date, status, project_id→ |
| `allocations` | project_id→, employee_id→, relevance_score, priority_weight, final_score, status, rationale, assigned_at |
| `agent_runs` | project_id→, status, started_at, finished_at, allocation_time_ms, metrics `json` |
| `agent_steps` | run_id→, agent_name, sequence, input/output `json`, status, timing |
| `notifications` | employee_id→, allocation_id→, channel, subject, body, status |
| `reports` | project_id→, run_id→, summary_text, **metrics_json** (text; shared with the Java reporting-service) |

## Workflow registry (backs admin Data Management)

| Table | Key columns |
|-------|-------------|
| `wf_def` | name (150), description (300), status, wf_engine, engine_ref (e.g. Airflow dag_id), wf_type |
| `wf_executions` | wf_def_id→, exec_created_dt, exec_status, exec_started_at, exec_completed_at, exec_configs `json`, exec_engine, exec_results `json`, engine_run_id |

## Java vs Python ownership

The Spring services map only the columns they manage (e.g. employee-service ignores
`profile_embedding`). On shared Postgres their Liquibase changesets `MARK_RAN` the
Alembic-created tables; `allocation_requests` is Spring-owned (allocation-service audit).
