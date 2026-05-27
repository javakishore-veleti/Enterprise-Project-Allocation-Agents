export interface Workflow {
  id: string;
  name: string;
  description?: string;
  wf_engine: string;
  engine_ref?: string;
  wf_type?: string;
}

export interface Execution {
  id: string;
  exec_status: string;
  exec_created_dt?: string;
  exec_started_at?: string;
  exec_completed_at?: string;
  exec_engine: string;
  engine_run_id?: string;
  exec_configs?: Record<string, unknown>;
  exec_results?: Record<string, unknown>;
}

export interface ExecutionPage {
  items: Execution[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}

export interface GenerateRequest {
  num_employees: number;
  num_projects: number;
  seed: number;
  use_llm: boolean;
  run_async: boolean;
}

export interface GenerateResponse {
  mode: string;
  dag_run_id?: string;
  state?: string;
  summary?: Record<string, unknown>;
}

/** Synthetic-data "types" shown in the Data Management left nav. */
export interface SyntheticType {
  key: string;
  label: string;
  wfType: string;
}
