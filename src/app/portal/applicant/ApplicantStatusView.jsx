'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge } from '@/components/portal/ui';
import {
  demoApplicant,
  admissionJourneySteps,
  entranceAssessmentSections,
} from '@/lib/portalDemoData';

export default function ApplicantStatusView() {
  return (
    <PortalShell role="applicant" active="dashboard" title={`Welcome, ${demoApplicant.name}`}>
      <StatGrid>
        <StatTile label="Application ID" value={demoApplicant.applicationId} />
        <StatTile label="Programme choice" value={demoApplicant.programmeChoice} />
        <StatTile label="Admission route" value={demoApplicant.route} />
        <StatTile label="Current stage" value={demoApplicant.stage} hint={`Submitted ${demoApplicant.submittedDate}`} />
      </StatGrid>

      <Card title="Your admission journey so far">
        <p className="intro">
          Every applicant follows the same journey, from first exploring programmes to their first day of class.
          Your application is currently at step {demoApplicant.currentStep} of {admissionJourneySteps.length}.
        </p>
        <ol className="journey">
          {admissionJourneySteps.map((step, i) => {
            const stepNum = i + 1;
            const state =
              stepNum < demoApplicant.currentStep
                ? 'done'
                : stepNum === demoApplicant.currentStep
                ? 'current'
                : 'upcoming';
            return (
              <li key={step} className={`step ${state}`}>
                <span className="num">{stepNum}</span>
                <span className="label">{step}</span>
                {state === 'done' && <Badge tone="success">Complete</Badge>}
                {state === 'current' && <Badge tone="gold">In progress</Badge>}
              </li>
            );
          })}
        </ol>
      </Card>

      <Card title="Mandatory Entrance Assessment" className="assess-card">
        <p className="intro">
          Regardless of entry route, every applicant must complete the Albalagh Admission Assessment — to confirm
          academic readiness, programme suitability, basic knowledge level, and ability to succeed in online
          learning.
          {demoApplicant.assessmentDate && (
            <> Your assessment is scheduled for <strong>{demoApplicant.assessmentDate}</strong>.</>
          )}
        </p>
        <div className="sections">
          {entranceAssessmentSections.map((s) => (
            <div className="section" key={s.name}>
              <h3>{s.name}</h3>
              <p>{s.detail}</p>
            </div>
          ))}
        </div>
      </Card>

      <style jsx>{`
        .intro { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 18px; }
        .journey { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .step { display: flex; align-items: center; gap: 12px; padding: 10px 4px; border-bottom: 1px solid var(--border); }
        .step:last-child { border-bottom: none; }
        .num { width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11.5px; font-weight: 600; flex-shrink: 0; border: 1px solid var(--border); background: var(--manuscript); color: var(--navy); }
        .step.done .num { background: var(--navy); border-color: var(--navy); color: #fff; }
        .step.current .num { background: rgba(188,154,74,0.18); border-color: var(--gold-ink); color: #886828; }
        .label { flex: 1; font-size: 13.5px; color: var(--ink); }
        .step.upcoming .label { color: var(--ink-muted); }

        .assess-card { margin-top: 20px; }
        .sections { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }
        .section { background: var(--manuscript); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 14px 16px; }
        .section h3 { font-family: 'Fraunces', serif; font-size: 14px; color: var(--navy); margin: 0 0 6px; }
        .section p { font-size: 12.5px; color: var(--ink-muted); line-height: 1.6; margin: 0; }
      `}</style>
    </PortalShell>
  );
}
