'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card } from '@/components/portal/ui';
import { demoStudent } from '@/lib/portalDemoData';

const FIELDS = [
  { label: 'Full name', value: (s) => s.name },
  { label: 'Student ID', value: (s) => s.studentId },
  { label: 'Programme', value: (s) => s.programme },
  { label: 'School', value: (s) => s.school },
  { label: 'Intake', value: (s) => s.intake },
  { label: 'Status', value: (s) => s.status },
  { label: 'Credits completed', value: (s) => `${s.creditsCompleted} / ${s.creditsRequired}` },
  { label: 'Email', value: (s) => s.email },
  { label: 'Phone', value: (s) => s.phone },
  { label: 'Date of birth', value: (s) => s.dateOfBirth },
];

export default function ProfileView() {
  return (
    <PortalShell role="student" active="profile" title="Profile">
      <Card title="Student record" action={<span className="readonly-tag">Read-only preview</span>}>
        <dl className="profile-grid">
          {FIELDS.map((f) => (
            <div className="field" key={f.label}>
              <dt>{f.label}</dt>
              <dd>{f.value(demoStudent)}</dd>
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
