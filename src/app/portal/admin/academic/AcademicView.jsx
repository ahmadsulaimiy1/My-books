'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, DataTable } from '@/components/portal/ui';

export default function AcademicView({ programmes, creditUnitPolicy }) {
  const schools = new Set(programmes.map((p) => p.school));

  return (
    <PortalShell role="admin" active="academic" title="Academic">
      <StatGrid>
        <StatTile label="Schools" value={schools.size} />
        <StatTile label="Departments / Programmes" value={programmes.length} />
        <StatTile
          label="Semester workload policy"
          value={`${creditUnitPolicy.semesterMin}–${creditUnitPolicy.semesterMax} CU`}
          hint={`Recommended ${creditUnitPolicy.semesterRecommendedLow}–${creditUnitPolicy.semesterRecommendedHigh} CU/semester`}
        />
      </StatGrid>

      <Card title="Programmes across the 4 Schools">
        <p className="intro">
          The 8 Departments/Programmes currently published on the public site, shown here as a management-style
          table. Every Professional Diploma Programme runs 3 semesters over 1 year; the credit-unit range for each
          is computed from the Institutional Credit Unit and Student Workload Policy (Semester Workload:
          {' '}{creditUnitPolicy.semesterMin}–{creditUnitPolicy.semesterMax} CU per semester, recommended{' '}
          {creditUnitPolicy.semesterRecommendedLow}–{creditUnitPolicy.semesterRecommendedHigh} CU) — the Advanced
          Islamic Sciences &amp; Modern Civilization Studies programme is the one with that exact 66–72 CU figure
          explicitly published.
        </p>
        <DataTable
          columns={[
            { key: 'school', label: 'School' },
            { key: 'programme', label: 'Department / Programme' },
            { key: 'duration', label: 'Duration' },
            { key: 'creditUnits', label: 'Credit units' },
          ]}
          rows={programmes}
        />
      </Card>
    </PortalShell>
  );
}
