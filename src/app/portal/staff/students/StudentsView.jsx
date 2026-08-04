'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, DataTable } from '@/components/portal/ui';

const FILTERS = ['All', 'Enrolled', 'Applicant'];
const KIND_TONE = { Enrolled: 'success', Applicant: 'info' };

export default function StudentsView({ students, applications }) {
  const [filter, setFilter] = useState('All');

  const directory = [
    ...students.map((s) => ({
      id: s.id,
      name: s.name,
      identifier: s.studentId,
      programme: s.programme,
      kind: 'Enrolled',
    })),
    ...applications.map((a) => ({
      id: a.id,
      name: a.name,
      identifier: a.applicationId,
      programme: a.programme,
      kind: 'Applicant',
    })),
  ];

  const rows = directory.filter((d) => filter === 'All' || d.kind === filter);

  return (
    <PortalShell role="staff" active="students" title="Students">
      <p className="intro">
        A combined directory of the sample enrolled roster and the sample admissions queue — a preview of what a
        real student directory will look like once the two are backed by real records.
      </p>

      <div className="filters" role="group" aria-label="Filter directory by type">
        {FILTERS.map((f) => (
          <button
            key={f}
            type="button"
            className={f === filter ? 'chip active' : 'chip'}
            aria-pressed={f === filter}
            onClick={() => setFilter(f)}
          >
            {f}
          </button>
        ))}
      </div>

      <Card>
        <DataTable
          columns={[
            { key: 'name', label: 'Name' },
            { key: 'identifier', label: 'ID' },
            { key: 'programme', label: 'Programme' },
            {
              key: 'kind',
              label: 'Type',
              render: (row) => <Badge tone={KIND_TONE[row.kind] ?? 'neutral'}>{row.kind}</Badge>,
            },
          ]}
          rows={rows}
          emptyLabel="No directory entries match this filter."
        />
      </Card>

      <style jsx>{`
        .intro { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: -8px 0 18px; }
        .filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 18px; }
        .chip { background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 7px 16px; font-size: 13px; font-weight: 600; color: var(--ink-muted); cursor: pointer; }
        .chip:hover { background: var(--manuscript); }
        .chip.active { background: var(--navy); border-color: var(--navy); color: #fff; }
      `}</style>
    </PortalShell>
  );
}
