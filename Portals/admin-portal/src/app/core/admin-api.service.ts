import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import {
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

  // Reports
  listReports(page = 1, projectId?: string): Observable<PageResponse<Report>> {
    let p = new HttpParams().set('page', page).set('pageSize', 15);
    if (projectId) p = p.set('projectId', projectId);
    return this.http.get<PageResponse<Report>>(`${this.base}/api/reports`, { params: p });
  }
}
