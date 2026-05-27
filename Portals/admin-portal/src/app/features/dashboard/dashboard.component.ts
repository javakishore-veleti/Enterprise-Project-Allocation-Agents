import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  template: `
    <h1 class="page-title">Dashboard</h1>
    <p class="page-subtitle">Allocation efficiency at a glance (live metrics wired in M6).</p>
    <div class="stats">
      @for (s of stats; track s.label) {
        <div class="card stat">
          <span class="stat-label">{{ s.label }}</span>
          <span class="stat-value">{{ s.value }}</span>
          <span class="stat-hint">{{ s.hint }}</span>
        </div>
      }
    </div>
  `,
  styles: [
    `
      .stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
      }
      .stat {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
      }
      .stat-label {
        color: #64748b;
        font-size: 0.85rem;
      }
      .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #4f46e5;
      }
      .stat-hint {
        color: #94a3b8;
        font-size: 0.75rem;
      }
    `,
  ],
})
export class DashboardComponent {
  readonly stats = [
    { label: 'Avg allocation time', value: '—', hint: 'ms per run' },
    { label: 'Resource utilization', value: '—', hint: 'assigned vs available' },
    { label: 'Conflicts avoided', value: '—', hint: 'unavailable filtered' },
    { label: 'Human intervention', value: '0%', hint: 'fully automated' },
  ];
}
