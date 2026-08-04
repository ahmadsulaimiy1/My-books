'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';
import { demoStaffRegistrar, demoApplications, demoLedger, demoRoster } from '@/lib/portalDemoData';

const STAGE_TONE = {
  'Application Review': 'info',
  'Entrance Assessment': 'gold',
  'Admission Decision': 'gold',
  'Accept Admission': 'success',
  'Complete Registration': 'success',
};

export default function StaffDashboardView() {
  const outstandingFees = demoLedger.filter((f) => f.status === 'Outstanding');
  const recentApplications = [...demoApplications].sort((a, b) => b.submitted.localeCompare(a.submitted)).slice(0, 4);

  return (
    <PortalShell role="staff" active="dashboard" title={`Welcome, ${demoStaffRegistrar.name}`}>
      <StatGrid>
        <StatTile label="Office" value={demoStaffRegistrar.office} />
        <StatTile label="Applications in queue" value={demoApplications.length} hint="Sample admissions preview" />
        <StatTile label="Enrolled students (sample)" value={demoRoster.length} />
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
