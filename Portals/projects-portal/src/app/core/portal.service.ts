import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { CreateProjectRequest, NotificationItem, PageResponse, Project } from './models';

/** Customer portal API (projects + notifications) via the gateway. */
@Injectable({ providedIn: 'root' })
export class PortalService {
  private http = inject(HttpClient);
  private base = environment.gatewayBase;

  submitBrief(req: CreateProjectRequest): Observable<Project> {
    return this.http.post<Project>(`${this.base}/api/projects`, req);
  }

  listProjects(page = 1, search?: string): Observable<PageResponse<Project>> {
    let params = new HttpParams().set('page', page).set('pageSize', 15);
    if (search) {
      params = params.set('search', search);
    }
    return this.http.get<PageResponse<Project>>(`${this.base}/api/projects`, { params });
  }

  listNotifications(page = 1, employeeId?: string): Observable<PageResponse<NotificationItem>> {
    let params = new HttpParams().set('page', page).set('pageSize', 15);
    if (employeeId) {
      params = params.set('employeeId', employeeId);
    }
    return this.http.get<PageResponse<NotificationItem>>(`${this.base}/api/notifications`, { params });
  }
}
