import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'dashboard' },
  {
    path: 'home',
    loadComponent: () => import('./features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./features/dashboard/dashboard.component').then((m) => m.DashboardComponent),
  },
  {
    path: 'data-management',
    loadComponent: () =>
      import('./features/data-management/data-management.component').then(
        (m) => m.DataManagementComponent,
      ),
  },
  {
    path: 'administration',
    loadComponent: () =>
      import('./features/administration/administration.component').then(
        (m) => m.AdministrationComponent,
      ),
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'employees' },
      {
        path: 'employees',
        loadComponent: () =>
          import('./features/administration/employees.component').then((m) => m.EmployeesComponent),
      },
      {
        path: 'projects',
        loadComponent: () =>
          import('./features/administration/projects.component').then((m) => m.ProjectsComponent),
      },
      {
        path: 'agent-monitor',
        loadComponent: () =>
          import('./features/administration/agent-monitor.component').then(
            (m) => m.AgentMonitorComponent,
          ),
      },
      {
        path: 'reports',
        loadComponent: () =>
          import('./features/administration/reports.component').then((m) => m.ReportsComponent),
      },
    ],
  },
  { path: '**', redirectTo: 'dashboard' },
];
