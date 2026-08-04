'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';
import { demoFaculty } from '@/lib/portalDemoData';

const FIELDS = [
  { label: 'Full name', value: (f) => f.name },
  { label: 'Staff ID', value: (f) => f.staffId },
  { label: 'Department', value: (f) => f.department },
  { label: 'Courses taught', value: (f) => f.coursesTaught.join(', ') },
];

export default function FacultyProfileView() {
  return (
    <PortalShell role="faculty" active="profile" title="Profile">
      <Card title="Faculty record" action={<span className="readonly-tag">Read-only preview</span>}>
        <dl className="profile-grid">
          {FIELDS.map((f) => (
            <div className="field" key={f.label}>
              <dt>{f.label}</dt>
              <dd>{f.value(demoFaculty)}</dd>
            </div>
          ))}
        </dl>
      </Card>

      <style jsx>{`
        .readonly-tag { font-size: 12px; font-weight: 600; color: var(--ink-muted); background: var(--manuscript); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; }
        .profile-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 0; }
        .field dt { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); margin-bottom: 4px; }
        .field dd { font-size: 14.5px; color: var(--ink); margin: 0; }
      `}</style>
    </PortalShell>
  );
}
