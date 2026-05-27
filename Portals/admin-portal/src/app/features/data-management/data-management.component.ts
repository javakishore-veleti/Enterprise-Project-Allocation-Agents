import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { SelectModule } from 'primeng/select';
import { TableModule, TableLazyLoadEvent } from 'primeng/table';

import { DatalakeService } from '../../core/datalake.service';
import { Execution, GenerateRequest, SyntheticType, Workflow } from '../../core/models';

@Component({
  selector: 'app-data-management',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, InputTextModule, SelectModule, TableModule],
  templateUrl: './data-management.component.html',
  styleUrl: './data-management.component.scss',
})
export class DataManagementComponent {
  private datalake = inject(DatalakeService);

  readonly PAGE_SIZE = 15;

  // Left-nav synthetic-data types (all currently backed by the same DAG).
  readonly types: SyntheticType[] = [
    { key: 'employees', label: 'Employees', wfType: 'synthetic-data' },
    { key: 'projects', label: 'Projects', wfType: 'synthetic-data' },
    { key: 'briefs', label: 'Briefs', wfType: 'synthetic-data' },
    { key: 'full', label: 'Full Dataset', wfType: 'synthetic-data' },
  ];

  selectedType?: SyntheticType;
  workflows: Workflow[] = [];
  selectedWorkflow?: Workflow;
  mode: 'initiate' | 'history' = 'initiate';
  error?: string;

  // Initiate Execution criteria (DAG conf)
  criteria: GenerateRequest = {
    num_employees: 60,
    num_projects: 20,
    seed: 42,
    use_llm: false,
    run_async: true,
  };
  submitting = false;
  generateResult?: string;

  // History
  executions: Execution[] = [];
  total = 0;
  loading = false;
  search = '';

  selectType(type: SyntheticType): void {
    this.selectedType = type;
    this.selectedWorkflow = undefined;
    this.error = undefined;
    this.generateResult = undefined;
    this.datalake.listWorkflows(type.wfType).subscribe({
      next: (res) => (this.workflows = res.items),
      error: () => (this.error = 'Could not load workflows (is the gateway/Datalake API running?)'),
    });
  }

  onWorkflowChange(): void {
    this.mode = 'initiate';
    this.generateResult = undefined;
    this.executions = [];
    this.total = 0;
  }

  setMode(mode: 'initiate' | 'history'): void {
    this.mode = mode;
    if (mode === 'history') {
      this.loadExecutions({ first: 0, rows: this.PAGE_SIZE });
    }
  }

  runGenerate(): void {
    if (!this.selectedWorkflow) {
      return;
    }
    this.submitting = true;
    this.generateResult = undefined;
    this.error = undefined;
    this.datalake.generate(this.criteria).subscribe({
      next: (res) => {
        this.submitting = false;
        this.generateResult =
          res.mode === 'async'
            ? `Triggered DAG run ${res.dag_run_id} (state: ${res.state}).`
            : `Completed inline: ${JSON.stringify(res.summary)}`;
      },
      error: () => {
        this.submitting = false;
        this.error = 'Failed to trigger the workflow.';
      },
    });
  }

  loadExecutions(event: TableLazyLoadEvent): void {
    if (!this.selectedWorkflow) {
      return;
    }
    const rows = event.rows ?? this.PAGE_SIZE;
    const page = Math.floor((event.first ?? 0) / rows) + 1;
    this.loading = true;
    this.datalake.listExecutions(this.selectedWorkflow.id, page, this.search || undefined).subscribe({
      next: (res) => {
        this.executions = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.error = 'Could not load execution history.';
      },
    });
  }

  onSearch(): void {
    this.loadExecutions({ first: 0, rows: this.PAGE_SIZE });
  }
}
