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
  },
  { path: '**', redirectTo: 'dashboard' },
];
