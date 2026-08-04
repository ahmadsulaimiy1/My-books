'use client';

/*
  AdmissionsPipeline
  -------------------
  Groups demoApplications by their current stage in the real 13-step
  admission journey (see admissionJourneySteps in portalDemoData.js) and
  renders them as a kanban-style board, one column per stage that has at
  least one applicant in this preview. Read-only — this is a queue view,
  not a workflow tool.
*/

import { Badge } from './ui';

export default function AdmissionsPipeline({ applications, stages }) {
  const activeStages = stages.filter((stage) =>
    applications.some((a) => a.stage === stage)
  );

  return (
    <div className="pipeline">
      {activeStages.map((stage) => {
        const items = applications.filter((a) => a.stage === stage);
        return (
          <div className="column" key={stage}>
            <div className="column-head">
              <span>{stage}</span>
              <Badge tone="neutral">{items.length}</Badge>
            </div>
            <div className="column-body">
              {items.map((app) => (
                <div className="app-card" key={app.id}>
                  <div className="app-top">
                    <span className="name">{app.name}</span>
                    <span className="id">{app.applicationId}</span>
                  </div>
                  <p className="programme">{app.programme}</p>
                  <p className="route">{app.route}</p>
                  <p className="submitted">Submitted {app.submitted}</p>
                </div>
              ))}
            </div>
          </div>
        );
      })}

      <style jsx>{`
        .pipeline { display: grid; grid-auto-flow: column; grid-auto-columns: minmax(230px, 1fr); gap: 14px; overflow-x: auto; padding-bottom: 4px; }
        .column { background: var(--manuscript); border: 1px solid var(--border); border-radius: var(--radius-md); display: flex; flex-direction: column; min-width: 230px; }
        .column-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; font-size: 12.5px; font-weight: 600; color: var(--navy); border-bottom: 1px solid var(--border); }
        .column-body { padding: 10px; display: flex; flex-direction: column; gap: 10px; }
        .app-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 12px; display: flex; flex-direction: column; gap: 4px; }
        .app-top { display: flex; justify-content: space-between; gap: 8px; }
        .name { font-size: 13px; font-weight: 600; color: var(--ink); }
        .id { font-size: 11px; color: var(--ink-muted); flex-shrink: 0; }
        .programme { font-size: 12px; color: var(--ink); margin: 0; line-height: 1.4; }
        .route { font-size: 11.5px; color: var(--ink-muted); margin: 0; }
        .submitted { font-size: 11px; color: var(--ink-muted); margin: 2px 0 0; }
      `}</style>
    </div>
  );
}
