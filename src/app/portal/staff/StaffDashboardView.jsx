'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';

const STAGE_TONE = {
  'Application Review': 'info',
  'Entrance Assessment': 'gold',
  'Admission Decision': 'gold',
  'Accept Admission': 'success',
  'Complete Registration': 'success',
};

export default function StaffDashboardView({ staff, applications, ledger, students }) {
  const outstandingFees = ledger.filter((f) => f.status === 'Outstanding');
  const recentApplications = [...applications].sort((a, b) => b.submitted.localeCompare(a.submitted)).slice(0, 4);

  return (
    <PortalShell role="staff" active="dashboard" title={`Welcome, ${staff.name}`}>
      <StatGrid>
        <StatTile label="Office" value={staff.office} />
        <StatTile label="Applications in queue" value={applications.length} hint="Sample admissions preview" />
        <StatTile label="Enrolled students (sample)" value={students.length} />
        <StatTile label="Outstanding fee items" value={outstandingFees.length} />
      </StatGrid>

      <Card title="Recent admissions activity">
        <DataTable
          columns={[
            { key: 'name', label: 'Applicant' },
            { key: 'programme', label: 'Programme' },
            { key: 'route', label: 'Route' },
            {
              key: 'stage',
              label: 'Stage',
              render: (row) => <Badge tone={STAGE_TONE[row.stage] ?? 'neutral'}>{row.stage}</Badge>,
            },
            { key: 'submitted', label: 'Submitted' },
          ]}
          rows={recentApplications}
        />
      </Card>
    </PortalShell>
  );
}
