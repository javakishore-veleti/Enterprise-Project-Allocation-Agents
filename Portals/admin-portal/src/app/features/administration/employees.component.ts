import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { AdminApiService } from '../../core/admin-api.service';
import { Employee } from '../../core/admin-models';

@Component({
  selector: 'app-employees',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule, SelectModule, TableModule],
  template: `
    <div class="head">
      <div>
        <h1 class="page-title">Employees</h1>
        <p class="page-subtitle">Manage employee profiles (CRUD via the gateway).</p>
      </div>
      <p-button label="New employee" icon="pi pi-plus" (onClick)="startCreate()" />
    </div>

    @if (editing) {
      <div class="card form">
        <h3>{{ form.id ? 'Edit' : 'New' }} employee</h3>
        <div class="grid">
          <label>Full name <input pInputText [(ngModel)]="form.fullName" /></label>
          <label>Title <input pInputText [(ngModel)]="form.title" /></label>
          <label>Seniority
            <p-select [options]="seniorities" [(ngModel)]="form.seniority" placeholder="Select" />
          </label>
          <label>Availability
            <p-select [options]="states" [(ngModel)]="form.availabilityState" placeholder="Select" />
          </label>
          <label>Years exp <input type="number" pInputText [(ngModel)]="form.yearsExperience" /></label>
          <label>Performance <input type="number" pInputText [(ngModel)]="form.performanceScore" /></label>
          <label>Capacity h/wk <input type="number" pInputText [(ngModel)]="form.capacityHoursPerWeek" /></label>
          <label class="full">Profile <input pInputText [(ngModel)]="form.profileText" /></label>
        </div>
        <div class="actions">
          <p-button label="Save" icon="pi pi-check" (onClick)="save()" [loading]="saving" />
          <p-button label="Cancel" severity="secondary" (onClick)="editing = false" />
        </div>
        @if (error) { <div class="banner error">{{ error }}</div> }
      </div>
    }

    <div class="card">
      <div class="toolbar">
        <input pInputText [(ngModel)]="search" (keyup.enter)="reload()" placeholder="Search name or title…" />
        <p-button label="Search" icon="pi pi-search" severity="secondary" (onClick)="reload()" />
      </div>
      <p-table [value]="employees" [lazy]="true" (onLazyLoad)="load($event)" [paginator]="true"
               [rows]="15" [totalRecords]="total" [loading]="loading">
        <ng-template pTemplate="header">
          <tr><th>Name</th><th>Title</th><th>Seniority</th><th>Availability</th><th>Perf</th><th></th></tr>
        </ng-template>
        <ng-template pTemplate="body" let-e>
          <tr>
            <td>{{ e.fullName }}</td><td>{{ e.title }}</td><td>{{ e.seniority }}</td>
            <td><span class="chip">{{ e.availabilityState }}</span></td><td>{{ e.performanceScore }}</td>
            <td class="row-actions">
              <p-button icon="pi pi-pencil" severity="secondary" [text]="true" (onClick)="startEdit(e)" />
              <p-button icon="pi pi-trash" severity="danger" [text]="true" (onClick)="remove(e)" />
            </td>
          </tr>
        </ng-template>
        <ng-template pTemplate="emptymessage"><tr><td colspan="6" class="empty">No employees.</td></tr></ng-template>
      </p-table>
    </div>
  `,
  styles: [
    `
      .head { display: flex; justify-content: space-between; align-items: flex-start; }
      .form .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0; }
      .form label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.85rem; color: #475569; }
      .form label.full { grid-column: 1 / -1; }
      .form input, :host ::ng-deep .p-select { width: 100%; }
      .actions { display: flex; gap: 0.5rem; }
      .toolbar { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
      .toolbar input { min-width: 260px; }
      .row-actions { display: flex; gap: 0.25rem; }
      .chip { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.78rem; background: #e2e8f0; color: #334155; }
      .empty { color: #94a3b8; padding: 1.5rem; text-align: center; }
      .banner.error { margin-top: 1rem; padding: 0.6rem 1rem; border-radius: 8px; background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
      .card + .card { margin-top: 1rem; }
    `,
  ],
})
export class EmployeesComponent {
  private api = inject(AdminApiService);
  readonly seniorities = ['junior', 'mid', 'senior', 'lead', 'principal'];
  readonly states = ['available', 'partially_occupied', 'unavailable'];

  employees: Employee[] = [];
  total = 0;
  loading = false;
  search = '';
  editing = false;
  saving = false;
  error?: string;
  form: Employee = { fullName: '' };

  load(event: TableLazyLoadEvent): void {
    const rows = event.rows ?? 15;
    const page = Math.floor((event.first ?? 0) / rows) + 1;
    this.loading = true;
    this.api.listEmployees(page, this.search || undefined).subscribe({
      next: (r) => { this.employees = r.items; this.total = r.total; this.loading = false; },
      error: () => (this.loading = false),
    });
  }
  reload(): void { this.load({ first: 0, rows: 15 }); }
  startCreate(): void { this.form = { fullName: '' }; this.editing = true; this.error = undefined; }
  startEdit(e: Employee): void { this.form = { ...e }; this.editing = true; this.error = undefined; }

  save(): void {
    if (!this.form.fullName?.trim()) { this.error = 'Full name is required.'; return; }
    this.saving = true;
    const done = () => { this.saving = false; this.editing = false; this.reload(); };
    const fail = () => { this.saving = false; this.error = 'Save failed.'; };
    if (this.form.id) this.api.updateEmployee(this.form.id, this.form).subscribe({ next: done, error: fail });
    else this.api.createEmployee(this.form).subscribe({ next: done, error: fail });
  }
  remove(e: Employee): void {
    if (e.id) this.api.deleteEmployee(e.id).subscribe({ next: () => this.reload() });
  }
}
