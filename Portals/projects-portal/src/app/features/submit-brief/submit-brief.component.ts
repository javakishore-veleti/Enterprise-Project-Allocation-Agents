import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TextareaModule } from 'primeng/textarea';
import { PortalService } from '../../core/portal.service';
import { CreateProjectRequest } from '../../core/models';

@Component({
  selector: 'app-submit-brief',
  standalone: true,
  imports: [FormsModule, ButtonModule, InputTextModule, SelectModule, TextareaModule],
  template: `
    <h1 class="page-title">Submit a Project Brief</h1>
    <p class="page-subtitle">Describe the work; the agents parse it and propose a team.</p>

    <div class="card form">
      <div class="form-grid">
        <label class="full">Project name
          <input pInputText [(ngModel)]="form.name" placeholder="e.g. Payments portal revamp" />
        </label>
        <label>Client
          <input pInputText [(ngModel)]="form.clientName" />
        </label>
        <label>Priority
          <p-select [options]="priorities" [(ngModel)]="form.priority" placeholder="Select" />
        </label>
        <label>Complexity
          <p-select [options]="complexities" [(ngModel)]="form.complexity" placeholder="Select" />
        </label>
        <label>Duration (weeks)
          <input type="number" pInputText [(ngModel)]="form.durationWeeks" />
        </label>
        <label>Headcount
          <input type="number" pInputText [(ngModel)]="form.requiredHeadcount" />
        </label>
        <label class="full">Brief
          <textarea
            pTextarea
            rows="5"
            [(ngModel)]="form.briefText"
            placeholder="We need a team to… required skills…"
          ></textarea>
        </label>
      </div>
      <p-button label="Submit brief" icon="pi pi-send" [loading]="submitting" (onClick)="submit()" />
      @if (message) {
        <div class="banner" [class.ok]="ok" [class.error]="!ok">{{ message }}</div>
      }
    </div>
  `,
  styles: [
    `
      .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
      }
      label {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        font-size: 0.85rem;
        color: #475569;
      }
      label.full {
        grid-column: 1 / -1;
      }
      input,
      textarea,
      :host ::ng-deep .p-select {
        width: 100%;
      }
      .banner {
        margin-top: 1rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.9rem;
      }
      .banner.ok {
        background: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
      }
      .banner.error {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
      }
    `,
  ],
})
export class SubmitBriefComponent {
  private portal = inject(PortalService);

  readonly priorities = ['low', 'medium', 'high', 'critical'];
  readonly complexities = ['low', 'medium', 'high'];

  form: CreateProjectRequest = { name: '', priority: 'medium', complexity: 'medium' };
  submitting = false;
  message?: string;
  ok = false;

  submit(): void {
    if (!this.form.name?.trim()) {
      this.ok = false;
      this.message = 'Project name is required.';
      return;
    }
    this.submitting = true;
    this.message = undefined;
    this.portal.submitBrief(this.form).subscribe({
      next: (p) => {
        this.submitting = false;
        this.ok = true;
        this.message = `Brief submitted — project "${p.name}" created (id ${p.id}).`;
        this.form = { name: '', priority: 'medium', complexity: 'medium' };
      },
      error: () => {
        this.submitting = false;
        this.ok = false;
        this.message = 'Could not submit (is the gateway/project-service running?).';
      },
    });
  }
}
