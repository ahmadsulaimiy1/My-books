'use client';

import PortalShell from '@/components/portal/PortalShell';
import { RecordGrid } from '@/components/portal/ui';

const FIELDS = [
  { label: 'Full name', value: (f) => f.name },
  { label: 'Staff ID', value: (f) => f.staffId },
  { label: 'Department', value: (f) => f.department },
  { label: 'Courses taught', value: (f) => f.coursesTaught.join(', ') },
];

export default function FacultyProfileView({ faculty }) {
  return (
    <PortalShell role="faculty" active="profile" title="Profile">
      <RecordGrid title="Faculty record" record={faculty} fields={FIELDS} />
    </PortalShell>
  );
}
