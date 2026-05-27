import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  template: `
    <h1 class="page-title">Your projects, intelligently staffed</h1>
    <p class="page-subtitle">
      Submit a project brief and our multi-agent system assembles the right team.
    </p>
    <div class="grid">
      <a class="card tile" routerLink="/submit-brief">
        <i class="pi pi-send"></i>
        <div><strong>Submit a Brief</strong><span>Describe your project in plain language</span></div>
      </a>
      <a class="card tile" routerLink="/my-projects">
        <i class="pi pi-folder"></i>
        <div><strong>My Projects</strong><span>Track status and assigned teams</span></div>
      </a>
      <a class="card tile" routerLink="/notifications">
        <i class="pi pi-bell"></i>
        <div><strong>Notifications</strong><span>Updates on your allocations</span></div>
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
