import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  template: `
    <h1 class="page-title">Welcome to EPAA</h1>
    <p class="page-subtitle">
      LLM-driven multi-agent automation for enterprise project allocation.
    </p>
    <div class="grid">
      <a class="card tile" routerLink="/dashboard">
        <i class="pi pi-chart-bar"></i>
        <div><strong>Dashboard</strong><span>Allocation metrics & recent runs</span></div>
      </a>
      <a class="card tile" routerLink="/data-management">
        <i class="pi pi-database"></i>
        <div><strong>Data Management</strong><span>Synthetic data & Airflow workflows</span></div>
      </a>
      <a class="card tile" routerLink="/administration">
        <i class="pi pi-cog"></i>
        <div><strong>Administration</strong><span>Employees, projects & settings</span></div>
      </a>
    </div>
  `,
  styles: [
    `
      .grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 1rem;
        max-width: 900px;
      }
      .tile {
        display: flex;
        align-items: center;
        gap: 1rem;
        text-decoration: none;
        color: inherit;
        transition: box-shadow 0.15s, transform 0.15s;
      }
      .tile:hover {
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.12);
        transform: translateY(-2px);
      }
      .tile i {
        font-size: 1.6rem;
        color: #4f46e5;
      }
      .tile div {
        display: flex;
        flex-direction: column;
      }
      .tile span {
        color: #64748b;
        font-size: 0.85rem;
      }
    `,
  ],
})
export class HomeComponent {}
