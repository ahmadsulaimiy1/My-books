'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, DataTable } from '@/components/portal/ui';
import { demoFaculty, demoRoster } from '@/lib/portalDemoData';

export default function GradebookView() {
  const columns = [
    { key: 'name', label: 'Student' },
    { key: 'studentId', label: 'Student ID' },
    ...demoFaculty.coursesTaught.map((code) => ({
      key: code,
      label: code,
      render: (row) =>
        row.grades[code] ? <Badge tone="gold">{row.grades[code]}</Badge> : <Badge tone="info">In progress</Badge>,
    })),
  ];

  return (
    <PortalShell role="faculty" active="gradebook" title="Gradebook">
      <Card
        title={`Sample roster — ${demoFaculty.coursesTaught.join(', ')}`}
        action={<span className="readonly-tag">Read-only preview</span>}
      >
        <p className="intro">
          There is no real class roster yet, so this gradebook shows a small set of clearly placeholder students
          ("Student A", "Student B", …) with sample grades. Nothing here is connected to a real transcript.
        </p>
        <DataTable columns={columns} rows={demoRoster} />
      </Card>

      <style jsx>{`
        .readonly-tag { font-size: 12px; font-weight: 600; color: var(--ink-muted); background: var(--manuscript); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; }
        .intro { font-size: 13px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 16px; }
      `}</style>
    </PortalShell>
  );
}
