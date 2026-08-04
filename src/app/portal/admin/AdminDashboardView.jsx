'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge } from '@/components/portal/ui';
import {
  demoAdmin,
  demoRoster,
  demoCourses,
  demoUsers,
  demoProgrammes,
  demoApplications,
} from '@/lib/portalDemoData';

export default function AdminDashboardView() {
  const staffCount = demoUsers.filter((u) => u.role === 'faculty' || u.role === 'staff').length;

  return (
    <PortalShell role="admin" active="dashboard" title={`Welcome, ${demoAdmin.name}`}>
      <p className="intro">
        Preview counts only — every figure below comes from the sample data in this frontend preview, not a real
        enrolment or staffing database.
      </p>

      <StatGrid>
        <StatTile label="Sample students" value={demoRoster.length} hint="Preview count, not real enrolment" />
        <StatTile label="Sample courses" value={demoCourses.length} hint="Across the AISM programme sample" />
        <StatTile label="Sample staff accounts" value={staffCount} hint="Faculty + Staff roles" />
        <StatTile label="Published programmes" value={demoProgrammes.length} hint="Real programme list" />
      </StatGrid>

      <div className="grid">
        <Card title="Sample accounts by role">
          <ul className="role-list">
            {['student', 'faculty', 'staff', 'admin', 'applicant', 'parent'].map((role) => (
              <li key={role}>
                <Badge tone="info">{role}</Badge>
                <span>{demoUsers.filter((u) => u.role === role).length} account(s)</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card title="Admissions queue snapshot">
          <ul className="role-list">
            {demoApplications.map((a) => (
              <li key={a.id}>
                <Badge tone="gold">{a.stage}</Badge>
                <span>{a.name}</span>
              </li>
            ))}
          </ul>
        </Card>
      </div>

      <style jsx>{`
        .intro { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: -8px 0 20px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } }
        .role-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .role-list li { display: flex; align-items: center; gap: 12px; padding: 10px 4px; border-bottom: 1px solid var(--border); font-size: 13.5px; color: var(--ink); }
        .role-list li:last-child { border-bottom: none; }
      `}</style>
    </PortalShell>
  );
}
