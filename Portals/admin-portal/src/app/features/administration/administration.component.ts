import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-administration',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="admin">
      <aside class="admin-nav">
        <div class="admin-nav-head"><i class="pi pi-cog"></i> Administration</div>
        <ul>
          <li><a routerLink="employees" routerLinkActive="active"><i class="pi pi-users"></i> Employees</a></li>
          <li><a routerLink="projects" routerLinkActive="active"><i class="pi pi-folder"></i> Projects</a></li>
          <li><a routerLink="agent-monitor" routerLinkActive="active"><i class="pi pi-sitemap"></i> Agent Monitor</a></li>
          <li><a routerLink="reports" routerLinkActive="active"><i class="pi pi-chart-line"></i> Reports</a></li>
        </ul>
      </aside>
      <section class="admin-main"><router-outlet /></section>
    </div>
  `,
  styles: [
    `
      .admin {
        display: grid;
        grid-template-columns: 220px 1fr;
        gap: 1.25rem;
        align-items: start;
      }
      .admin-nav {
        background: #1e293b;
        border-radius: 12px;
        padding: 1rem 0.75rem;
        min-height: 70vh;
      }
      .admin-nav-head {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        color: #f8fafc;
        padding: 0.5rem 0.5rem 0.75rem;
        border-bottom: 1px solid #334155;
        margin-bottom: 0.5rem;
      }
      .admin-nav ul {
        list-style: none;
        margin: 0;
        padding: 0;
      }
      .admin-nav a {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.55rem 0.75rem;
        border-radius: 8px;
        color: #cbd5e1;
        text-decoration: none;
        font-size: 0.92rem;
      }
      .admin-nav a:hover {
        background: #334155;
        color: #fff;
      }
      .admin-nav a.active {
        background: #4f46e5;
        color: #fff;
        font-weight: 600;
      }
      .admin-main {
        min-width: 0;
      }
    `,
  ],
})
export class AdministrationComponent {}
