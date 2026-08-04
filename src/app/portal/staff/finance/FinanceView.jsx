'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable } from '@/components/portal/ui';
import { demoLedger, demoFeeTypes } from '@/lib/portalDemoData';

const STATUS_TONE = {
  Paid: 'success',
  Outstanding: 'alert',
  'Awaiting institutional rate': 'neutral',
};

function feeType(key) {
  return demoFeeTypes.find((f) => f.key === key);
}

function formatNaira(n) {
  return `₦${n.toLocaleString('en-NG')}`;
}

export default function FinanceView() {
  const paidAips = demoLedger.filter((f) => f.feeKey === 'aips' && f.status === 'Paid').length;
  const outstanding = demoLedger.filter((f) => f.status === 'Outstanding').length;

  const rows = demoLedger.map((entry) => ({ ...entry, type: feeType(entry.feeKey) }));

  return (
    <PortalShell role="staff" active="finance" title="Finance">
      <div className="notice">
        <strong>Preview only.</strong> This is a sample fee ledger for demonstration — there is no real payment
        processing, and no card or bank details are collected anywhere in this portal preview.
      </div>

      <StatGrid>
        <StatTile label="AIPS fee — paid (sample)" value={paidAips} />
        <StatTile label="Outstanding items (sample)" value={outstanding} />
        <StatTile label="Fee types tracked" value={demoFeeTypes.length} />
      </StatGrid>

      <Card title="Official fee schedule (published rates)" className="fee-card">
        <ul className="fee-type-list">
          {demoFeeTypes.map((f) => (
            <li key={f.key}>
              <span className="label">{f.label}</span>
              <span className="amount">{f.amount != null ? formatNaira(f.amount) : 'TBC'}</span>
              <span className="note">{f.note}</span>
            </li>
          ))}
        </ul>
      </Card>

      <Card title="Sample fee ledger" action={<span className="readonly-tag">Read-only preview</span>}>
        <DataTable
          columns={[
            { key: 'student', label: 'Student' },
            { key: 'studentId', label: 'Student ID' },
            { key: 'type', label: 'Fee type', render: (row) => row.type.label },
            {
              key: 'amount',
              label: 'Amount',
              render: (row) => (row.type.amount != null ? formatNaira(row.type.amount) : 'TBC'),
            },
            {
              key: 'status',
              label: 'Status',
              render: (row) => <Badge tone={STATUS_TONE[row.status] ?? 'neutral'}>{row.status}</Badge>,
            },
            { key: 'date', label: 'Date' },
          ]}
          rows={rows}
        />
      </Card>

      <style jsx>{`
        .notice { background: rgba(178,58,58,0.06); border: 1px solid rgba(178,58,58,0.25); border-radius: var(--radius-md); padding: 14px 18px; font-size: 13px; color: var(--ink); line-height: 1.6; margin-bottom: 20px; }
        .readonly-tag { font-size: 12px; font-weight: 600; color: var(--ink-muted); background: var(--manuscript); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; }

        .fee-card { margin-bottom: 20px; }
        .fee-type-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .fee-type-list li { display: grid; grid-template-columns: 1.4fr auto 2fr; gap: 12px; align-items: baseline; padding: 12px 4px; border-bottom: 1px solid var(--border); }
        .fee-type-list li:last-child { border-bottom: none; }
        .label { font-size: 13px; font-weight: 600; color: var(--ink); }
        .amount { font-size: 13.5px; font-weight: 600; color: var(--navy); white-space: nowrap; }
        .note { font-size: 12px; color: var(--ink-muted); }
        @media (max-width: 700px) {
          .fee-type-list li { grid-template-columns: 1fr; gap: 4px; }
        }
      `}</style>
    </PortalShell>
  );
}
