'use client';

import { useMemo, useState } from 'react';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, DataTable } from '@/components/portal/ui';

const STATUS_TONE = { Submitted: 'success', 'Not started': 'neutral', Overdue: 'alert' };

export default function AssignmentsView({ assignments }) {
  const [courseFilter, setCourseFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [sortBy, setSortBy] = useState('due');

  const courses = useMemo(
    () => ['All', ...new Set(assignments.map((a) => a.course))],
    [assignments]
  );
  const statuses = ['All', 'Not started', 'Submitted', 'Overdue'];

  const rows = useMemo(() => {
    let list = assignments.filter(
      (a) =>
        (courseFilter === 'All' || a.course === courseFilter) &&
        (statusFilter === 'All' || a.status === statusFilter)
    );
    list = [...list].sort((a, b) => {
      if (sortBy === 'due') return a.due.localeCompare(b.due);
      if (sortBy === 'course') return a.course.localeCompare(b.course);
      return a.status.localeCompare(b.status);
    });
    return list;
  }, [assignments, courseFilter, statusFilter, sortBy]);

  return (
    <PortalShell role="student" active="assignments" title="Assignments">
      <Card>
        <div className="controls">
          <div className="field">
            <label htmlFor="course-filter">Course</label>
            <select id="course-filter" value={courseFilter} onChange={(e) => setCourseFilter(e.target.value)}>
              {courses.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="status-filter">Status</label>
            <select id="status-filter" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              {statuses.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label htmlFor="sort-by">Sort by</label>
            <select id="sort-by" value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="due">Due date</option>
              <option value="course">Course</option>
              <option value="status">Status</option>
            </select>
          </div>
        </div>

        <DataTable
          columns={[
            { key: 'title', label: 'Assignment' },
            { key: 'course', label: 'Course' },
            { key: 'due', label: 'Due' },
            {
              key: 'status',
              label: 'Status',
              render: (row) => <Badge tone={STATUS_TONE[row.status] ?? 'neutral'}>{row.status}</Badge>,
            },
          ]}
          rows={rows}
          emptyLabel="No assignments match these filters."
        />
      </Card>

      <style jsx>{`
        .controls { display: flex; flex-wrap: wrap; gap: 16px; margin-bottom: 18px; }
        .field { display: flex; flex-direction: column; gap: 6px; }
        .field label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); }
        .field select { border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 8px 12px; font-size: 13.5px; color: var(--ink); background: var(--surface); min-width: 160px; }
      `}</style>
    </PortalShell>
  );
}
