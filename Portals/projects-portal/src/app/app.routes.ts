import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'home' },
  {
    path: 'home',
    loadComponent: () => import('./features/home/home.component').then((m) => m.HomeComponent),
  },
  {
    path: 'submit-brief',
    loadComponent: () =>
      import('./features/submit-brief/submit-brief.component').then((m) => m.SubmitBriefComponent),
  },
  {
    path: 'my-projects',
    loadComponent: () =>
      import('./features/my-projects/my-projects.component').then((m) => m.MyProjectsComponent),
  },
  {
    path: 'notifications',
    loadComponent: () =>
      import('./features/notifications/notifications.component').then(
        (m) => m.NotificationsComponent,
      ),
  },
  { path: '**', redirectTo: 'home' },
];
