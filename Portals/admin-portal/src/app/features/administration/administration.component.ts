import { Component } from '@angular/core';

@Component({
  selector: 'app-administration',
  standalone: true,
  template: `
    <h1 class="page-title">Administration</h1>
    <p class="page-subtitle">Employees, projects and platform settings.</p>
    <div class="card">
      <p>
        Employee &amp; project management screens (CRUD against the gateway) are added next.
        Agent Monitor and Reports also live under this area.
      </p>
    </div>
  `,
})
export class AdministrationComponent {}
