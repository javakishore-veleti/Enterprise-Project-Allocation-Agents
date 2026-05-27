# API contracts

All browser traffic goes through the **api-gateway** (`:8080`, CORS enabled).
Direct service ports are listed for local debugging.

## Gateway routes

| Path | → Service | Port |
|------|-----------|------|
| `/api/employees/**` | employee-service | 8081 |
| `/api/projects/**` | project-service | 8082 |
| `/api/allocations/**` | allocation-service | 8083 |
| `/api/notifications/**` | notification-service | 8084 |
| `/api/reports/**` | reporting-service | 8085 |
| `/agents/**` (StripPrefix) | agents | 8001 |
| `/datalake/**` (StripPrefix) | datalake | 8000 |

## Spring services (Req/Resp DTOs; UUID-string ids; lists paginate 15/page)

**employee-service**
- `POST /api/employees` `CreateEmployeeRequest` → `EmployeeResponse` (201)
- `GET /api/employees/{id}` → `EmployeeResponse`
- `PUT /api/employees/{id}` `UpdateEmployeeRequest` → `EmployeeResponse`
- `DELETE /api/employees/{id}` → 204
- `GET /api/employees?page=&pageSize=&search=` → `PageResponse<EmployeeResponse>`

**project-service** — same shape at `/api/projects` (CreateProjectRequest carries an
optional `briefText`; ProjectResponse returns it).

**allocation-service**
- `POST /api/allocations/run` `{ "projectId": "<uuid>" }` → `AllocationRunResponse`
  (delegates to the Agents service; records an `allocation_requests` audit row).

**notification-service**
- `POST /api/notifications`, `GET /api/notifications/{id}`,
  `POST /api/notifications/{id}/deliver`, `GET /api/notifications?status=&employeeId=`

**reporting-service**
- `POST /api/reports`, `GET /api/reports/{id}`,
  `GET /api/reports/project/{projectId}/latest`, `GET /api/reports?projectId=`

## Agents service (FastAPI, 8001)

- `POST /allocations/run` `{ "project_id": "<uuid>" }` → run summary (run_id, status,
  allocation_time_ms, assignments, report, metrics)
- `GET /agent-runs/{run_id}` → run + ordered step trace
- `GET /reports/{project_id}` → latest managerial report
- `GET /health`

## Datalake service (FastAPI, 8000)

- `POST /synthetic/generate`
  `{ num_employees, num_projects, seed, use_llm, run_async }` →
  async (triggers the `synthetic_data_gen` Airflow DAG) or sync (inline) result
- `GET /synthetic/runs/{dag_run_id}` → DAG run state
- `GET /workflows?wf_type=` → registered workflows (feeds the admin dropdown)
- `GET /workflows/{wf_def_id}/executions?page=&search=` → paginated history (15/page)
- `GET /health`
