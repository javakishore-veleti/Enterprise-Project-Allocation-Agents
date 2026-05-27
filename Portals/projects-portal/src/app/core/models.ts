export interface Project {
  id: string;
  name: string;
  clientName?: string;
  priority?: string;
  complexity?: string;
  durationWeeks?: number;
  requiredHeadcount?: number;
  startDate?: string;
  status?: string;
  briefText?: string;
  createdAt?: string;
}

export interface CreateProjectRequest {
  name: string;
  clientName?: string;
  priority?: string;
  complexity?: string;
  durationWeeks?: number;
  requiredHeadcount?: number;
  startDate?: string;
  status?: string;
  briefText?: string;
}

export interface NotificationItem {
  id: string;
  employeeId: string;
  allocationId?: string;
  channel?: string;
  subject?: string;
  body?: string;
  status?: string;
  createdAt?: string;
}

export interface PageResponse<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  pages: number;
}
