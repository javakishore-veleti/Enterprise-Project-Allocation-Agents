import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ExecutionPage, GenerateRequest, GenerateResponse, Workflow } from './models';

/** Calls the Datalake API (workflow registry, history, and DAG triggers). */
@Injectable({ providedIn: 'root' })
export class DatalakeService {
  private http = inject(HttpClient);
  private base = environment.datalakeBase;

  listWorkflows(wfType?: string): Observable<{ items: Workflow[] }> {
    let params = new HttpParams();
    if (wfType) {
      params = params.set('wf_type', wfType);
    }
    return this.http.get<{ items: Workflow[] }>(`${this.base}/workflows`, { params });
  }

  listExecutions(wfDefId: string, page = 1, search?: string): Observable<ExecutionPage> {
    let params = new HttpParams().set('page', page);
    if (search) {
      params = params.set('search', search);
    }
    return this.http.get<ExecutionPage>(`${this.base}/workflows/${wfDefId}/executions`, { params });
  }

  generate(req: GenerateRequest): Observable<GenerateResponse> {
    return this.http.post<GenerateResponse>(`${this.base}/synthetic/generate`, req);
  }
}
