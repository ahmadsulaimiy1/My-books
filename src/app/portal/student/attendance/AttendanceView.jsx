'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';
import { demoAttendance } from '@/lib/portalDemoData';

function toneForRate(pct) {
  if (pct >= 90) return 'success';
  if (pct >= 75) return 'gold';
  return 'alert';
}

export default function AttendanceView() {
  const rows = demoAttendance.byCourse.map((c) => ({
    ...c,
    pct: Math.round((c.attended / c.total) * 100),
  }));

  return (
    <PortalShell role="student" active="attendance" title="Attendance">
      <StatGrid>
        <StatTile label="Overall attendance" value={demoAttendance.overall} />
        <StatTile label="Courses tracked" value={demoAttendance.byCourse.length} />
      </StatGrid>

      <Card title="Attendance by course">
        <DataTable
          columns={[
            { key: 'course', label: 'Course' },
            {
              key: 'sessions',
              label: 'Sessions attended',
              render: (row) => `${row.attended} / ${row.total}`,
            },
            {
              key: 'pct',
              label: 'Rate',
              render: (row) => <Badge tone={toneForRate(row.pct)}>{row.pct}%</Badge>,
            },
          ]}
          rows={rows}
        />
      </Card>
    </PortalShell>
  );
}
