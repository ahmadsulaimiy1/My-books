'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile } from '@/components/portal/ui';
import AdmissionsPipeline from '@/components/portal/AdmissionsPipeline';
import { demoApplications, admissionJourneySteps } from '@/lib/portalDemoData';

export default function AdmissionsView() {
  return (
    <PortalShell role="staff" active="admissions" title="Admissions">
      <StatGrid>
        <StatTile label="Applications in this preview" value={demoApplications.length} />
        <StatTile label="Admission journey steps" value={admissionJourneySteps.length} hint="Published admission journey" />
      </StatGrid>

      <Card
        title="Applications by stage"
        action={<span className="readonly-tag">Read-only preview</span>}
      >
        <p className="intro">
          A small, clearly placeholder queue of sample applicants ("Applicant A" etc.), grouped by their stage in the
          real 13-step admission journey published on the public site. There is no real applications database behind
          this yet.
        </p>
        <AdmissionsPipeline applications={demoApplications} stages={admissionJourneySteps} />
      </Card>

      <style jsx>{`
        .readonly-tag { font-size: 12px; font-weight: 600; color: var(--ink-muted); background: var(--manuscript); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; }
        .intro { font-size: 13px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 18px; }
      `}</style>
    </PortalShell>
  );
}
