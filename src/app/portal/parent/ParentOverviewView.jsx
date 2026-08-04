'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';
import { demoParent, demoStudent, demoResults, demoAttendance } from '@/lib/portalDemoData';

function toneForRate(pct) {
  if (pct >= 90) return 'success';
  if (pct >= 75) return 'gold';
  return 'alert';
}

export default function ParentOverviewView() {
  const attendanceRows = demoAttendance.byCourse.map((c) => ({
    ...c,
    pct: Math.round((c.attended / c.total) * 100),
  }));

  return (
    <PortalShell role="parent" active="dashboard" title={`Welcome, ${demoParent.name}`}>
      <p className="intro">
        A read-only overview of {demoParent.linkedStudent}'s progress, linked to your account. This preview shows
        one sample student — a real Parent Portal would let you switch between multiple linked children where
        applicable.
      </p>

      <StatGrid>
        <StatTile label="Linked student" value={demoStudent.name} hint={demoStudent.studentId} />
        <StatTile label="Programme" value={demoStudent.programme} hint={demoStudent.school} />
        <StatTile label="Status" value={demoStudent.status} />
        <StatTile label="Overall attendance" value={demoAttendance.overall} />
      </StatGrid>

      <div className="grid">
        <Card title="Attendance by course">
          <DataTable
            columns={[
              { key: 'course', label: 'Course' },
              { key: 'sessions', label: 'Sessions attended', render: (row) => `${row.attended} / ${row.total}` },
              { key: 'pct', label: 'Rate', render: (row) => <Badge tone={toneForRate(row.pct)}>{row.pct}%</Badge> },
            ]}
            rows={attendanceRows}
          />
        </Card>

        <Card title="Results by semester">
          {demoResults.map((sem) => (
            <div className="sem-row" key={sem.semester}>
              <span className="sem-name">{sem.semester}</span>
              <span className="sem-gpa">{sem.gpa ? `GPA ${sem.gpa}` : 'Pending'}</span>
              <span className="sem-credits">{sem.credits} CU</span>
            </div>
          ))}
        </Card>
      </div>

      <style jsx>{`
        .intro { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: -8px 0 20px; }
        .grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; }
        @media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }
        .sem-row { display: flex; align-items: center; gap: 12px; padding: 12px 4px; border-bottom: 1px solid var(--border); font-size: 13.5px; }
        .sem-row:last-child { border-bottom: none; }
        .sem-name { flex: 1; color: var(--ink); }
        .sem-gpa { font-weight: 600; color: var(--navy); }
        .sem-credits { color: var(--ink-muted); font-size: 12.5px; }
      `}</style>
    </PortalShell>
  );
}
