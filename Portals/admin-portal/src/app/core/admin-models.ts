export interface PageResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  pages: number;
}

export interface Employee {
  id?: string;
  fullName: string;
  title?: string;
  seniority?: string;
  yearsExperience?: number;
  performanceScore?: number;
  availabilityState?: string;
  capacityHoursPerWeek?: number;
  profileText?: string;
  createdAt?: string;
}

export interface Project {
  id: string;
  name: string;
  clientName?: string;
  priority?: string;
  complexity?: string;
  durationWeeks?: number;
  requiredHeadcount?: number;
  status?: string;
  briefText?: string;
  createdAt?: string;
}

export interface Report {
  id: string;
  projectId: string;
  runId?: string;
  summaryText: string;
  metricsJson?: string;
  createdAt?: string;
}

export interface AllocationRunResponse {
  requestId?: string;
  runId: string;
  projectId: string;
  status: string;
  allocationTimeMs?: number;
  assignments?: { fullName: string; rank: number; finalScore: number }[];
  report?: string;
}

export interface AgentStep {
  sequence: number;
  agent: string;
  status: string;
  output?: Record<string, unknown>;
}

/** Snake_case result from the Python agents service (HITL + LangGraph paths). */
export interface AgentAllocationResult {
  run_id: string;
  project_id: string;
  status: string; // success | awaiting_approval | rejected | failed
  allocation_time_ms?: number;
  orchestrator?: string;
  assignments?: { full_name: string; rank: number; final_score: number }[];
  report?: string | null;
  metrics?: Record<string, unknown>;
}

/** One Server-Sent Event from GET /agents/allocations/stream/{projectId}. */
export interface AllocationStreamEvent {
  event: 'start' | 'step' | 'done' | 'error';
  run_id?: string;
  project_id?: string;
  orchestrator?: string;
  sequence?: number;
  agent?: string;
  output?: Record<string, unknown>;
  elapsed_ms?: number;
  summary?: AgentAllocationResult;
  detail?: string;
}

export interface AgentRun {
  run_id: string;
  project_id: string;
  status: string;
  allocation_time_ms?: number;
  metrics?: Record<string, unknown>;
  steps: AgentStep[];
}
