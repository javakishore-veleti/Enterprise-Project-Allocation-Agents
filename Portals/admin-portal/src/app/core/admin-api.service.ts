import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
  AgentAllocationResult,
  AgentRun,
  AllocationRunResponse,
  Employee,
  PageResponse,
  Project,
  Report,
} from './admin-models';

/** Admin CRUD + allocation/agent calls, all via the API gateway. */
@Injectable({ providedIn: 'root' })
export class AdminApiService {
  private http = inject(HttpClient);
  private base = environment.gatewayBase;

  // Employees
  listEmployees(page = 1, search?: string): Observable<PageResponse<Employee>> {
    let p = new HttpParams().set('page', page).set('pageSize', 15);
    if (search) p = p.set('search', search);
    return this.http.get<PageResponse<Employee>>(`${this.base}/api/employees`, { params: p });
  }
  createEmployee(e: Employee): Observable<Employee> {
    return this.http.post<Employee>(`${this.base}/api/employees`, e);
  }
  updateEmployee(id: string, e: Employee): Observable<Employee> {
    return this.http.put<Employee>(`${this.base}/api/employees/${id}`, e);
  }
  deleteEmployee(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/api/employees/${id}`);
  }

  // Projects
  listProjects(page = 1, search?: string): Observable<PageResponse<Project>> {
    let p = new HttpParams().set('page', page).set('pageSize', 15);
    if (search) p = p.set('search', search);
    return this.http.get<PageResponse<Project>>(`${this.base}/api/projects`, { params: p });
  }

  // Allocation + agent trace
  runAllocation(projectId: string): Observable<AllocationRunResponse> {
    return this.http.post<AllocationRunResponse>(`${this.base}/api/allocations/run`, { projectId });
  }
  getAgentRun(runId: string): Observable<AgentRun> {
    return this.http.get<AgentRun>(`${this.base}/agents/agent-runs/${runId}`);
  }

  // --- Human-in-the-loop (calls the Python agents service directly via /agents/**) ---
  /** Phase 1: run agents 1-4 and park the run as awaiting_approval (proposed). */
  runWithApproval(projectId: string): Observable<AgentAllocationResult> {
    return this.http.post<AgentAllocationResult>(
      `${this.base}/agents/allocations/run`, { project_id: projectId, require_approval: true });
  }
  /** Phase 2 (approve): proposed → assigned, then notify + report. */
  approveAllocation(runId: string): Observable<AgentAllocationResult> {
    return this.http.post<AgentAllocationResult>(`${this.base}/agents/allocations/${runId}/approve`, {});
  }
  /** Phase 2 (reject): proposed → rejected. */
  rejectAllocation(runId: string, reason: string): Observable<AgentAllocationResult> {
    return this.http.post<AgentAllocationResult>(
      `${this.base}/agents/allocations/${runId}/reject`, { reason });
  }
  /** SSE endpoint for the live LangGraph trace (consume with EventSource). */
  allocationStreamUrl(projectId: string): string {
    return `${this.base}/agents/allocations/stream/${projectId}`;
  }

  // Reports
  listReports(page = 1, projectId?: string): Observable<PageResponse<Report>> {
    let p = new HttpParams().set('page', page).set('pageSize', 15);
    if (projectId) p = p.set('projectId', projectId);
    return this.http.get<PageResponse<Report>>(`${this.base}/api/reports`, { params: p });
  }
}
