import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { PortalService } from '../../core/portal.service';
import { Project } from '../../core/models';

@Component({
  selector: 'app-my-projects',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule, TableModule],
  template: `
    <h1 class="page-title">My Projects</h1>
    <p class="page-subtitle">Projects you've submitted and their allocation status.</p>

    <div class="card">
      <div class="toolbar">
        <input pInputText [(ngModel)]="search" (keyup.enter)="reload()" placeholder="Search name or client…" />
        <p-button label="Search" icon="pi pi-search" severity="secondary" (onClick)="reload()" />
      </div>

      <p-table
        [value]="projects"
        [lazy]="true"
        (onLazyLoad)="load($event)"
        [paginator]="true"
        [rows]="15"
        [totalRecords]="total"
        [loading]="loading"
        [showCurrentPageReport]="true"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
      >
        <ng-template pTemplate="header">
          <tr><th>Name</th><th>Client</th><th>Priority</th><th>Status</th><th>Created</th></tr>
        </ng-template>
        <ng-template pTemplate="body" let-p>
          <tr>
            <td>{{ p.name }}</td>
            <td>{{ p.clientName }}</td>
            <td><span class="chip">{{ p.priority }}</span></td>
            <td>{{ p.status }}</td>
            <td>{{ p.createdAt | date: 'short' }}</td>
          </tr>
        </ng-template>
        <ng-template pTemplate="emptymessage">
          <tr><td colspan="5" class="empty">No projects yet — submit a brief to get started.</td></tr>
        </ng-template>
      </p-table>
    </div>
  `,
  styles: [
    `
      .toolbar {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 1rem;
      }
      .toolbar input {
        min-width: 280px;
      }
      .chip {
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        background: #e0e7ff;
        color: #3730a3;
      }
      .empty {
        color: #94a3b8;
        padding: 1.5rem;
        text-align: center;
      }
    `,
  ],
})
export class MyProjectsComponent {
  private portal = inject(PortalService);
  projects: Project[] = [];
  total = 0;
  loading = false;
  search = '';

  load(event: TableLazyLoadEvent): void {
    const rows = event.rows ?? 15;
    const page = Math.floor((event.first ?? 0) / rows) + 1;
    this.loading = true;
    this.portal.listProjects(page, this.search || undefined).subscribe({
      next: (res) => {
        this.projects = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  reload(): void {
    this.load({ first: 0, rows: 15 });
  }
}
