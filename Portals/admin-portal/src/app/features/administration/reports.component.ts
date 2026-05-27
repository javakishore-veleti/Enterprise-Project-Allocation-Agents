import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { AdminApiService } from '../../core/admin-api.service';
import { Report } from '../../core/admin-models';

@Component({
  selector: 'app-reports',
  standalone: true,
  imports: [CommonModule, TableModule],
  template: `
    <h1 class="page-title">Reports</h1>
    <p class="page-subtitle">Managerial allocation reports + the paper's metrics.</p>
    <div class="card">
      <p-table [value]="reports" [lazy]="true" (onLazyLoad)="load($event)" [paginator]="true"
               [rows]="15" [totalRecords]="total" [loading]="loading" dataKey="id"
               [expandedRowKeys]="expanded">
        <ng-template pTemplate="header">
          <tr><th style="width:3rem"></th><th>Created</th><th>Summary</th></tr>
        </ng-template>
        <ng-template pTemplate="body" let-r let-expanded="expanded">
          <tr>
            <td><button type="button" class="exp" [pRowToggler]="r">
              <i class="pi" [class.pi-chevron-right]="!expanded" [class.pi-chevron-down]="expanded"></i>
            </button></td>
            <td>{{ r.createdAt | date: 'short' }}</td>
            <td class="summary">{{ r.summaryText }}</td>
          </tr>
        </ng-template>
        <ng-template pTemplate="rowexpansion" let-r>
          <tr><td colspan="3"><pre class="metrics">{{ pretty(r.metricsJson) }}</pre></td></tr>
        </ng-template>
        <ng-template pTemplate="emptymessage"><tr><td colspan="3" class="empty">No reports yet.</td></tr></ng-template>
      </p-table>
    </div>
  `,
  styles: [
    `
      .summary { color: #334155; }
      .exp { background: none; border: 0; cursor: pointer; color: #4f46e5; }
      .metrics { margin: 0; padding: 0.75rem; background: #f8fafc; border-radius: 8px; font-size: 0.8rem; color: #334155; white-space: pre-wrap; }
      .empty { color: #94a3b8; padding: 1.5rem; text-align: center; }
    `,
  ],
})
export class ReportsComponent {
  private api = inject(AdminApiService);
  reports: Report[] = [];
  total = 0;
  loading = false;
  expanded: Record<string, boolean> = {};

  load(event: TableLazyLoadEvent): void {
    const rows = event.rows ?? 15;
    const page = Math.floor((event.first ?? 0) / rows) + 1;
    this.loading = true;
    this.api.listReports(page).subscribe({
      next: (r) => { this.reports = r.items; this.total = r.total; this.loading = false; },
      error: () => (this.loading = false),
    });
  }

  pretty(json?: string): string {
    if (!json) return '(no metrics)';
    try { return JSON.stringify(JSON.parse(json), null, 2); } catch { return json; }
  }
}
