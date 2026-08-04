'use client';

import { useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, DataTable } from '@/components/portal/ui';
import { updateUserRole } from '@/lib/services/adminService';

const ROLE_TONE = {
  student: 'info',
  faculty: 'gold',
  staff: 'success',
  admin: 'alert',
  applicant: 'neutral',
  parent: 'neutral',
};

export default function UsersView({ users, roleOptions }) {
  const [roles, setRoles] = useState(() => Object.fromEntries(users.map((u) => [u.id, u.role])));
  const [note, setNote] = useState('');

  async function handleRoleChange(id, newRole) {
    await updateUserRole({ userId: id, role: newRole });
    setRoles((prev) => ({ ...prev, [id]: newRole }));
    setNote('Role updated for this preview session only — nothing is saved to a server yet.');
  }

  const rows = users.map((u) => ({ ...u, role: roles[u.id] }));

  return (
    <PortalShell role="admin" active="users" title="Users & Roles">
      <Card title="Sample accounts" action={<span className="readonly-tag">Preview — local changes only</span>}>
        <p className="intro">
          A small set of sample accounts, one per role built so far. Changing a role below only updates this
          browser tab — there is no real user database or authentication behind it yet.
        </p>
        <DataTable
          columns={[
            { key: 'name', label: 'Name' },
            { key: 'identifier', label: 'ID' },
            {
              key: 'role',
              label: 'Role',
              render: (row) => (
                <select
                  aria-label={`Change role for ${row.name}`}
                  value={row.role}
                  onChange={(e) => handleRoleChange(row.id, e.target.value)}
                  className="role-select"
                >
                  {roleOptions.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              ),
            },
            {
              key: 'badge',
              label: 'Badge preview',
              render: (row) => <Badge tone={ROLE_TONE[row.role] ?? 'neutral'}>{row.role}</Badge>,
            },
            { key: 'status', label: 'Status' },
          ]}
          rows={rows}
        />
        {note && <p className="note">{note}</p>}
      </Card>

      <style jsx>{`
        .readonly-tag { font-size: 12px; font-weight: 600; color: var(--ink-muted); background: var(--manuscript); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; }
        .intro { font-size: 13px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 16px; }
        .note { font-size: 12.5px; color: var(--emerald); margin: 14px 0 0; }
        .role-select { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 6px 10px; font-size: 13px; color: var(--ink); background: var(--surface); }
      `}</style>
    </PortalShell>
  );
}
