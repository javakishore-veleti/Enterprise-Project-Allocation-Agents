import { CommonModule } from '@angular/common';
import { Component, NgZone, OnDestroy, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { TableModule } from 'primeng/table';
import { AdminApiService } from '../../core/admin-api.service';
import {
  AgentAllocationResult,
  AgentRun,
  AllocationRunResponse,
  AllocationStreamEvent,
} from '../../core/admin-models';

interface LiveStep {
  sequence: number;
  agent: string;
  output?: Record<string, unknown>;
  elapsedMs?: number;
}

@Component({
  selector: 'app-agent-monitor',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule, TableModule],
  template: `
    <h1 class="page-title">Agent Monitor</h1>
    <p class="page-subtitle">
      Trigger the 6-agent allocation pipeline three ways: a plain batch run, a
      <strong>live-streamed</strong> LangGraph run, or a
      <strong>human-in-the-loop</strong> run you approve or reject.
    </p>

    <div class="card">
      <div class="toolbar">
        <input pInputText [(ngModel)]="projectId" placeholder="Project id (uuid)" />
        <p-button label="Run" icon="pi pi-play" [loading]="running" (onClick)="run()" />
        <p-button
          label="Run (live stream)"
          icon="pi pi-bolt"
          severity="secondary"
          [loading]="streaming"
          (onClick)="runStream()"
        />
        <p-button
          label="Run with approval"
          icon="pi pi-user-edit"
          severity="warn"
          [loading]="proposing"
          (onClick)="runWithApproval()"
        />
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

    <!-- Live streamed trace (SSE from the LangGraph orchestrator) -->
    @if (streaming || liveSteps.length) {
      <div class="card">
        <h3>
          Live trace
          @if (streaming) { <span class="chip live">streaming…</span> }
          @else if (streamSummary) { <span class="chip ok">done · {{ streamSummary.allocation_time_ms }} ms</span> }
        </h3>
        <ul class="timeline">
          @for (s of liveSteps; track s.sequence) {
            <li>
              <span class="seq">{{ s.sequence }}</span>
              <span class="agent">{{ s.agent }}</span>
              <span class="elapsed">+{{ s.elapsedMs }} ms</span>
              <span class="mono out">{{ s.output | json }}</span>
            </li>
          }
        </ul>
        @if (streamSummary?.report) { <p class="report">{{ streamSummary?.report }}</p> }
      </div>
    }

    <!-- Human-in-the-loop approval gate -->
    @if (proposal) {
      <div class="card hitl">
        <h3>
          Awaiting approval
          <span class="chip warn">{{ proposal.assignments?.length || 0 }} proposed</span>
          <span class="run">run {{ proposal.run_id }}</span>
        </h3>
        <p class="muted">
          The pipeline ran Requirement Parsing → Skill Matching → Availability → Assignment
          and parked these proposals. Approve to notify assignees &amp; generate the report,
          or reject to discard.
        </p>
        <p-table [value]="proposal.assignments || []">
          <ng-template pTemplate="header">
            <tr><th>Rank</th><th>Name</th><th>Final score</th></tr>
          </ng-template>
          <ng-template pTemplate="body" let-a>
            <tr><td>{{ a.rank }}</td><td>{{ a.full_name }}</td><td>{{ a.final_score }}</td></tr>
          </ng-template>
        </p-table>
        <div class="toolbar decide">
          <input pInputText [(ngModel)]="rejectReason" placeholder="Reason (for rejection)" />
          <p-button label="Approve" icon="pi pi-check" severity="success"
            [loading]="deciding" (onClick)="approve()" />
          <p-button label="Reject" icon="pi pi-times" severity="danger"
            [loading]="deciding" (onClick)="reject()" />
        </div>
      </div>
    }

    @if (decision) {
      <div class="card">
        <div class="summary">
          <span class="chip" [class.ok]="decision.status === 'success'"
            [class.rej]="decision.status === 'rejected'">{{ decision.status }}</span>
          <span>{{ decision.assignments?.length || 0 }} assigned</span>
          <span class="run">run {{ decision.run_id }}</span>
        </div>
        @if (decision.report) { <p class="report">{{ decision.report }}</p> }
      </div>
    }

    <!-- Batch run trace -->
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
      .toolbar { display: flex; gap: 0.5rem; margin-bottom: 1rem; flex-wrap: wrap; align-items: center; }
      .toolbar input { min-width: 360px; }
      .toolbar.decide { margin-top: 1rem; margin-bottom: 0; }
      .summary { display: flex; gap: 1rem; align-items: center; color: #475569; }
      .summary .run, h3 .run { font-family: ui-monospace, monospace; font-size: 0.8rem; color: #94a3b8; }
      .report { margin-top: 0.75rem; color: #334155; }
      .muted { color: #64748b; font-size: 0.9rem; }
      .chip { padding: 0.15rem 0.6rem; border-radius: 999px; font-size: 0.78rem; background: #e2e8f0; color: #334155; margin-left: 0.5rem; }
      .chip.ok { background: #dcfce7; color: #166534; }
      .chip.warn { background: #fef9c3; color: #854d0e; }
      .chip.rej { background: #fee2e2; color: #991b1b; }
      .chip.live { background: #dbeafe; color: #1e40af; animation: pulse 1.2s infinite; }
      @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.45; } }
      .mono { font-family: ui-monospace, monospace; font-size: 0.78rem; max-width: 520px; }
      .banner.error { padding: 0.6rem 1rem; border-radius: 8px; background: #fef2f2; color: #991b1b; border: 1px solid #fecaca; }
      .card + .card { margin-top: 1rem; }
      .card.hitl { border: 1px solid #fde68a; background: #fffbeb; }
      .timeline { list-style: none; margin: 0; padding: 0; }
      .timeline li { display: flex; gap: 0.75rem; align-items: baseline; padding: 0.4rem 0; border-bottom: 1px dashed #e2e8f0; }
      .timeline .seq { width: 1.4rem; height: 1.4rem; line-height: 1.4rem; text-align: center; border-radius: 999px; background: #6366f1; color: #fff; font-size: 0.75rem; flex: none; }
      .timeline .agent { font-weight: 600; color: #1e293b; min-width: 170px; }
      .timeline .elapsed { color: #94a3b8; font-size: 0.78rem; min-width: 70px; }
      .timeline .out { color: #475569; }
    `,
  ],
})
export class AgentMonitorComponent implements OnDestroy {
  private api = inject(AdminApiService);
  private zone = inject(NgZone);

  projectId = '';
  error?: string;

  // batch run
  running = false;
  result?: AllocationRunResponse;
  run_?: AgentRun;

  // live stream
  streaming = false;
  liveSteps: LiveStep[] = [];
  streamSummary?: AgentAllocationResult;
  private es?: EventSource;
  private streamDone = false;

  // human-in-the-loop
  proposing = false;
  deciding = false;
  proposal?: AgentAllocationResult;
  decision?: AgentAllocationResult;
  rejectReason = '';

  private reset(): void {
    this.error = undefined;
    this.result = undefined;
    this.run_ = undefined;
    this.liveSteps = [];
    this.streamSummary = undefined;
    this.proposal = undefined;
    this.decision = undefined;
    this.closeStream();
  }

  private pid(): string | undefined {
    const p = this.projectId.trim();
    if (!p) { this.error = 'Enter a project id.'; return undefined; }
    return p;
  }

  run(): void {
    const p = this.pid();
    if (!p) return;
    this.reset();
    this.running = true;
    this.api.runAllocation(p).subscribe({
      next: (res) => {
        this.result = res;
        this.running = false;
        if (res.runId) this.api.getAgentRun(res.runId).subscribe({ next: (r) => (this.run_ = r) });
      },
      error: () => { this.running = false; this.error = 'Allocation failed (is the stack running?).'; },
    });
  }

  runStream(): void {
    const p = this.pid();
    if (!p) return;
    this.reset();
    this.streaming = true;
    this.streamDone = false;
    // EventSource callbacks fire outside Angular's zone — re-enter so the view updates.
    const es = new EventSource(this.api.allocationStreamUrl(p));
    this.es = es;
    es.onmessage = (e: MessageEvent) => {
      let ev: AllocationStreamEvent;
      try { ev = JSON.parse(e.data); } catch { return; }
      this.zone.run(() => this.onStreamEvent(ev));
    };
    es.onerror = () => {
      this.zone.run(() => {
        if (this.streamDone) return; // normal close after 'done'
        this.streaming = false;
        if (!this.liveSteps.length) this.error = 'Stream failed (is the agents service running?).';
        this.closeStream();
      });
    };
  }

  private onStreamEvent(ev: AllocationStreamEvent): void {
    switch (ev.event) {
      case 'step':
        this.liveSteps = [...this.liveSteps, {
          sequence: ev.sequence ?? this.liveSteps.length + 1,
          agent: ev.agent ?? '?',
          output: ev.output,
          elapsedMs: ev.elapsed_ms,
        }];
        break;
      case 'done':
        this.streamSummary = ev.summary;
        this.streamDone = true;
        this.streaming = false;
        this.closeStream();
        break;
      case 'error':
        this.error = ev.detail ?? 'Stream error.';
        this.streamDone = true;
        this.streaming = false;
        this.closeStream();
        break;
    }
  }

  private closeStream(): void {
    this.es?.close();
    this.es = undefined;
  }

  runWithApproval(): void {
    const p = this.pid();
    if (!p) return;
    this.reset();
    this.proposing = true;
    this.api.runWithApproval(p).subscribe({
      next: (res) => { this.proposal = res; this.proposing = false; },
      error: () => { this.proposing = false; this.error = 'Run failed (is the agents service running?).'; },
    });
  }

  approve(): void {
    if (!this.proposal) return;
    this.deciding = true;
    this.api.approveAllocation(this.proposal.run_id).subscribe({
      next: (res) => this.afterDecision(res),
      error: () => { this.deciding = false; this.error = 'Approve failed.'; },
    });
  }

  reject(): void {
    if (!this.proposal) return;
    this.deciding = true;
    this.api.rejectAllocation(this.proposal.run_id, this.rejectReason.trim()).subscribe({
      next: (res) => this.afterDecision(res),
      error: () => { this.deciding = false; this.error = 'Reject failed.'; },
    });
  }

  private afterDecision(res: AgentAllocationResult): void {
    this.decision = res;
    this.deciding = false;
    this.proposal = undefined;
    this.api.getAgentRun(res.run_id).subscribe({ next: (r) => (this.run_ = r) });
  }

  ngOnDestroy(): void {
    this.closeStream();
  }
}
