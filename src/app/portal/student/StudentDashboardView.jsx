'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';
import {
  demoStudent,
  demoCourses,
  demoAssignments,
  demoNotifications,
} from '@/lib/portalDemoData';

export default function StudentDashboardView() {
  const inProgress = demoCourses.filter((c) => c.status === 'In Progress');
  const openAssignments = demoAssignments.filter((a) => a.status !== 'Submitted');

  return (
    <PortalShell role="student" active="dashboard" title={`Welcome, ${demoStudent.name}`}>
      <StatGrid>
        <StatTile label="Programme" value={demoStudent.programme} hint={demoStudent.school} />
        <StatTile label="Status" value={demoStudent.status} />
        <StatTile
          label="Credits Completed"
          value={`${demoStudent.creditsCompleted} / ${demoStudent.creditsRequired}`}
          hint="Institutional Credit Unit Policy"
        />
        <StatTile label="Intake" value={demoStudent.intake} />
      </StatGrid>

      <div className="grid">
        <Card title="Courses in progress">
          <DataTable
            columns={[
              { key: 'id', label: 'Code' },
              { key: 'title', label: 'Course' },
              { key: 'credits', label: 'CU' },
              {
                key: 'status',
                label: 'Status',
                render: () => <Badge tone="info">In Progress</Badge>,
              },
            ]}
            rows={inProgress}
          />
        </Card>

        <Card title="Assignments due">
          <DataTable
            columns={[
              { key: 'title', label: 'Assignment' },
              { key: 'course', label: 'Course' },
              { key: 'due', label: 'Due' },
              {
                key: 'status',
                label: 'Status',
                render: (row) => (
                  <Badge tone={row.status === 'Overdue' ? 'alert' : 'gold'}>{row.status}</Badge>
                ),
              },
            ]}
            rows={openAssignments}
            emptyLabel="No open assignments — you're all caught up."
          />
        </Card>
      </div>

      <Card title="Recent notifications" className="notif-card">
        <ul className="notif-list">
          {demoNotifications.map((n) => (
            <li key={n.id}>
              <Badge tone={n.type === 'alert' ? 'alert' : n.type === 'success' ? 'success' : 'info'}>
                {n.type}
              </Badge>
              <span>{n.text}</span>
              <span className="date">{n.date}</span>
            </li>
          ))}
        </ul>
      </Card>

      <style jsx>{`
        .grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; margin-bottom: 20px; }
        @media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }
        .notif-card :global(.pcard-body) { padding: 0; }
        .notif-list { list-style: none; margin: 0; padding: 0; }
        .notif-list li { display: flex; align-items: center; gap: 12px; padding: 14px 22px; border-bottom: 1px solid var(--border); font-size: 13.5px; color: var(--ink); }
        .notif-list li:last-child { border-bottom: none; }
        .notif-list .date { margin-inline-start: auto; color: var(--ink-muted); font-size: 12px; flex-shrink: 0; }
      `}</style>
    </PortalShell>
  );
}
