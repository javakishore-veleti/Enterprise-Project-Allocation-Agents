import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { AdminApiService } from '../../core/admin-api.service';
import { AgentRun, AllocationRunResponse } from '../../core/admin-models';

@Component({
  selector: 'app-agent-monitor',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule, TableModule],
  template: `
    <h1 class="page-title">Agent Monitor</h1>
    <p class="page-subtitle">Trigger the 6-agent allocation pipeline and inspect the run trace.</p>

    <div class="card">
      <div class="toolbar">
        <input pInputText [(ngModel)]="projectId" placeholder="Project id (uuid)" />
        <p-button label="Run allocation" icon="pi pi-play" [loading]="running" (onClick)="run()" />
      </div>
      @if (error) { <div class="banner error">{{ error }}</div> }
      @if (result) {
        <div class="summary">
          <span class="chip ok">{{ result.status }}</span>
          <span>{{ result.allocationTimeMs }} ms</span>
          <span>{{ result.assignments?.length || 0 }} assigned</span>
          <span class="run">run {{ result.runId }}</span>
        </div>
        <p class="report">{{ result.report }}</p>
      }
    </div>

    @if (run_) {
      <div class="card">
        <h3>Pipeline trace</h3>
        <p-table [value]="run_.steps">
          <ng-template pTemplate="header">
            <tr><th>#</th><th>Agent</th><th>Status</th><th>Output</th></tr>
          </ng-template>
          <ng-template pTemplate="body" let-s>
            <tr>
              <td>{{ s.sequence }}</td><td>{{ s.agent }}</td>
              <td><span class="chip ok">{{ s.status }}</span></td>
              <td class="mono">{{ s.output | json }}</td>
            </tr>
          </ng-template>
        </p-table>
      </div>
    }
  `,
  styles: [
    `
      .toolbar { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
      .toolbar input { min-width: 360px; }
      .summary { display: flex; gap: 1rem; align-items: center; color: #475569; }
      .summary .run { font-family: ui-monospace, monospace; font-size: 0.8rem; color: #94a3b8; }
      .report { margin-top: 0.75rem; color: #334155; }
      .chip { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.78rem; background: #e2e8f0; color: #334155; }
      .chip.ok { background: #dcfce7; color: #166534; }
      .mono { font-family: ui-monospace, monospace; font-size: 0.78rem; max-width: 520px; }
      .banner.error { padding: 0.6rem 1rem; border-radius: 8px; background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
      .card + .card { margin-top: 1rem; }
    `,
  ],
})
export class AgentMonitorComponent {
  private api = inject(AdminApiService);
  projectId = '';
  running = false;
  result?: AllocationRunResponse;
  run_?: AgentRun;
  error?: string;

  run(): void {
    if (!this.projectId.trim()) { this.error = 'Enter a project id.'; return; }
    this.running = true;
    this.error = undefined;
    this.result = undefined;
    this.run_ = undefined;
    this.api.runAllocation(this.projectId.trim()).subscribe({
      next: (res) => {
        this.result = res;
        this.running = false;
        if (res.runId) {
          this.api.getAgentRun(res.runId).subscribe({ next: (r) => (this.run_ = r) });
        }
      },
      error: () => { this.running = false; this.error = 'Allocation failed (is the stack running?).'; },
    });
  }
}
