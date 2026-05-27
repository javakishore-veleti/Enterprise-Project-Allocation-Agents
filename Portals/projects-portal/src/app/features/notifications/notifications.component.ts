import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TableLazyLoadEvent, TableModule } from 'primeng/table';
import { PortalService } from '../../core/portal.service';
import { NotificationItem } from '../../core/models';

@Component({
  selector: 'app-notifications',
  standalone: true,
  imports: [CommonModule, TableModule],
  template: `
    <h1 class="page-title">Notifications</h1>
    <p class="page-subtitle">Allocation updates from the Communication agent.</p>

    <div class="card">
      <p-table
        [value]="items"
        [lazy]="true"
        (onLazyLoad)="load($event)"
        [paginator]="true"
        [rows]="15"
        [totalRecords]="total"
        [loading]="loading"
        [showCurrentPageReport]="true"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
      >
        <ng-template pTemplate="header">
          <tr><th>Received</th><th>Subject</th><th>Status</th><th>Message</th></tr>
        </ng-template>
        <ng-template pTemplate="body" let-n>
          <tr>
            <td>{{ n.createdAt | date: 'short' }}</td>
            <td>{{ n.subject }}</td>
            <td><span class="chip" [class.delivered]="n.status === 'delivered'">{{ n.status }}</span></td>
            <td class="msg">{{ n.body }}</td>
          </tr>
        </ng-template>
        <ng-template pTemplate="emptymessage">
          <tr><td colspan="4" class="empty">No notifications.</td></tr>
        </ng-template>
      </p-table>
    </div>
  `,
  styles: [
    `
      .chip {
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        background: #e2e8f0;
        color: #334155;
      }
      .chip.delivered {
        background: #dcfce7;
        color: #166534;
      }
      .msg {
        max-width: 480px;
        color: #475569;
        font-size: 0.85rem;
      }
      .empty {
        color: #94a3b8;
        padding: 1.5rem;
        text-align: center;
      }
    `,
  ],
})
export class NotificationsComponent {
  private portal = inject(PortalService);
  items: NotificationItem[] = [];
  total = 0;
  loading = false;

  load(event: TableLazyLoadEvent): void {
    const rows = event.rows ?? 15;
    const page = Math.floor((event.first ?? 0) / rows) + 1;
    this.loading = true;
    this.portal.listNotifications(page).subscribe({
      next: (res) => {
        this.items = res.items;
        this.total = res.total;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }
}
