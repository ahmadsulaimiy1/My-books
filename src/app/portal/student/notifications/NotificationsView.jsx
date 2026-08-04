'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, EmptyState } from '@/components/portal/ui';
import { demoNotifications } from '@/lib/portalDemoData';

const TYPE_FILTERS = ['All', 'alert', 'info', 'success'];
const TYPE_LABEL = { alert: 'Alerts', info: 'Info', success: 'Success' };
const TYPE_TONE = { alert: 'alert', info: 'info', success: 'success' };

export default function NotificationsView() {
  const [filter, setFilter] = useState('All');
  const rows = demoNotifications.filter((n) => filter === 'All' || n.type === filter);

  return (
    <PortalShell role="student" active="notifications" title="Notifications">
      <div className="filters" role="group" aria-label="Filter notifications by type">
        {TYPE_FILTERS.map((t) => (
          <button
            key={t}
            type="button"
            className={t === filter ? 'chip active' : 'chip'}
            aria-pressed={t === filter}
            onClick={() => setFilter(t)}
          >
            {t === 'All' ? 'All' : TYPE_LABEL[t]}
          </button>
        ))}
      </div>

      <Card className="notif-card">
        {rows.length === 0 ? (
          <EmptyState message="No notifications match this filter." />
        ) : (
          <ul className="notif-list">
            {rows.map((n) => (
              <li key={n.id}>
                <Badge tone={TYPE_TONE[n.type] ?? 'neutral'}>{n.type}</Badge>
                <span>{n.text}</span>
                <span className="date">{n.date}</span>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <style jsx>{`
        .filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
        .chip { background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 7px 16px; font-size: 13px; font-weight: 600; color: var(--ink-muted); cursor: pointer; }
        .chip:hover { background: var(--manuscript); }
        .chip.active { background: var(--navy); border-color: var(--navy); color: #fff; }

        .notif-card :global(.pcard-body) { padding: 0; }
        .notif-list { list-style: none; margin: 0; padding: 0; }
        .notif-list li { display: flex; align-items: center; gap: 12px; padding: 14px 22px; border-bottom: 1px solid var(--border); font-size: 13.5px; color: var(--ink); }
        .notif-list li:last-child { border-bottom: none; }
        .notif-list .date { margin-inline-start: auto; color: var(--ink-muted); font-size: 12px; flex-shrink: 0; }
      `}</style>
    </PortalShell>
  );
}
