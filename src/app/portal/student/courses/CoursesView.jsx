'use client';

import { useState } from 'react';
import Link from 'next/link';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, EmptyState } from '@/components/portal/ui';
import { demoCourses } from '@/lib/portalDemoData';

const STATUS_FILTERS = ['All', 'In Progress', 'Completed', 'Upcoming'];
const STATUS_TONE = { Completed: 'success', 'In Progress': 'info', Upcoming: 'neutral' };

export default function CoursesView() {
  const [statusFilter, setStatusFilter] = useState('All');

  const filtered = demoCourses.filter((c) => statusFilter === 'All' || c.status === statusFilter);
  const semesters = [...new Set(filtered.map((c) => c.semester))].sort((a, b) => a - b);

  return (
    <PortalShell role="student" active="courses" title="My Courses">
      <div className="filters" role="group" aria-label="Filter courses by status">
        {STATUS_FILTERS.map((s) => (
          <button
            key={s}
            type="button"
            className={s === statusFilter ? 'chip active' : 'chip'}
            aria-pressed={s === statusFilter}
            onClick={() => setStatusFilter(s)}
          >
            {s}
          </button>
        ))}
      </div>

      {semesters.length === 0 ? (
        <Card>
          <EmptyState message="No courses match this filter." />
        </Card>
      ) : (
        semesters.map((sem) => (
          <Card title={`Semester ${sem}`} key={sem} className="sem-card">
            <ul className="course-list">
              {filtered
                .filter((c) => c.semester === sem)
                .map((course) => (
                  <li key={course.id}>
                    <Link href={`/portal/student/courses/${course.id}`} className="course-row">
                      <span className="code">{course.id}</span>
                      <span className="title">{course.title}</span>
                      <span className="credits">{course.credits} CU</span>
                      <Badge tone={STATUS_TONE[course.status] ?? 'neutral'}>{course.status}</Badge>
                      {course.grade && <Badge tone="gold">{course.grade}</Badge>}
                    </Link>
                  </li>
                ))}
            </ul>
          </Card>
        ))
      )}

      <style jsx>{`
        .filters { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
        .chip { background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 7px 16px; font-size: 13px; font-weight: 600; color: var(--ink-muted); cursor: pointer; }
        .chip:hover { background: var(--manuscript); }
        .chip.active { background: var(--navy); border-color: var(--navy); color: #fff; }

        .sem-card { margin-bottom: 20px; }
        .sem-card :global(.pcard-body) { padding: 0; }
        .course-list { list-style: none; margin: 0; padding: 0; }
        .course-list li { border-bottom: 1px solid var(--border); }
        .course-list li:last-child { border-bottom: none; }
        .course-row { display: flex; align-items: center; gap: 14px; padding: 14px 22px; color: var(--ink); }
        .course-row:hover { background: var(--manuscript); }
        .code { font-size: 12.5px; font-weight: 600; color: var(--navy); flex-shrink: 0; width: 78px; }
        .title { flex: 1; min-width: 160px; font-size: 14px; }
        .credits { font-size: 12.5px; color: var(--ink-muted); flex-shrink: 0; }
        @media (max-width: 560px) {
          .course-row { flex-wrap: wrap; }
          .title { width: 100%; order: 1; }
        }
      `}</style>
    </PortalShell>
  );
}
