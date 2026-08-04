'use client';

import PortalShell from '@/components/portal/PortalShell';
import { RecordGrid } from '@/components/portal/ui';

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

export default function ProfileView({ student }) {
  return (
    <PortalShell role="student" active="profile" title="Profile">
      <RecordGrid title="Student record" record={student} fields={FIELDS} />
    </PortalShell>
  );
}
