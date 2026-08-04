'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';
import { demoStudent, demoResults } from '@/lib/portalDemoData';

export default function ResultsView() {
  return (
    <PortalShell role="student" active="results" title="Results">
      <StatGrid>
        <StatTile label="Programme" value={demoStudent.programme} hint={demoStudent.school} />
        <StatTile
          label="Credits completed"
          value={`${demoStudent.creditsCompleted} / ${demoStudent.creditsRequired}`}
        />
        <StatTile label="Standing" value={demoStudent.status} />
      </StatGrid>

      {demoResults.map((sem) => (
        <Card key={sem.semester} title={sem.semester} className="sem-card">
          <div className="sem-stats">
            <div>
              <span className="label">GPA</span>
              <span className="value">{sem.gpa ?? 'Pending'}</span>
            </div>
            <div>
              <span className="label">Credit units</span>
              <span className="value">{sem.credits}</span>
            </div>
          </div>
          <DataTable
            columns={[
              { key: 'id', label: 'Code' },
              { key: 'title', label: 'Course' },
              { key: 'credits', label: 'CU' },
              {
                key: 'grade',
                label: 'Grade',
                render: (row) => (row.grade ? <Badge tone="gold">{row.grade}</Badge> : <Badge tone="info">In progress</Badge>),
              },
            ]}
            rows={sem.transcript}
          />
        </Card>
      ))}

      <style jsx>{`
        .sem-card { margin-bottom: 20px; }
        .sem-stats { display: flex; gap: 32px; margin-bottom: 18px; }
        .sem-stats .label { display: block; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); margin-bottom: 4px; }
        .sem-stats .value { display: block; font-family: 'Fraunces', serif; font-size: 22px; color: var(--navy); }
      `}</style>
    </PortalShell>
  );
}
