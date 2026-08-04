'use client';

import PortalShell from '@/components/portal/PortalShell';
import { RecordGrid } from '@/components/portal/ui';

const FIELDS = [
  { label: 'Full name', value: (s) => s.name },
  { label: 'Staff ID', value: (s) => s.staffId },
  { label: 'Office', value: (s) => s.office },
];

export default function StaffProfileView({ staff }) {
  return (
    <PortalShell role="staff" active="profile" title="Profile">
      <RecordGrid title="Staff record" record={staff} fields={FIELDS} />
    </PortalShell>
  );
}
