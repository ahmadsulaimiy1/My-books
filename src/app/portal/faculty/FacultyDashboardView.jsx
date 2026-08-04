'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, DataTable, EmptyState } from '@/components/portal/ui';
import {
  demoFaculty,
  demoCourses,
  demoTimetable,
  demoAssignments,
  demoFacultyMessages,
} from '@/lib/portalDemoData';

export default function FacultyDashboardView() {
  const myCourses = demoCourses.filter((c) => demoFaculty.coursesTaught.includes(c.id));

  const todaysClasses = demoTimetable
    .flatMap((day) => day.slots.map((slot) => ({ ...slot, day: day.day })))
    .filter((slot) => demoFaculty.coursesTaught.some((code) => slot.course.startsWith(code)));

  const pendingGrading = demoAssignments.filter(
    (a) => demoFaculty.coursesTaught.includes(a.course) && a.status === 'Submitted'
  );

  const unreadMessages = demoFacultyMessages.filter((m) => m.unread).length;

  return (
    <PortalShell role="faculty" active="dashboard" title={`Welcome, ${demoFaculty.name}`}>
      <StatGrid>
        <StatTile label="Department" value={demoFaculty.department} />
        <StatTile label="Courses taught" value={myCourses.length} hint={demoFaculty.coursesTaught.join(', ')} />
        <StatTile label="Assignments pending grading" value={pendingGrading.length} />
        <StatTile label="Unread messages" value={unreadMessages} />
      </StatGrid>

      <div className="grid">
        <Card title="Upcoming class sessions this week">
          {todaysClasses.length === 0 ? (
            <EmptyState message="No scheduled sessions for your courses this week in this preview." />
          ) : (
            <ul className="class-list">
              {todaysClasses.map((slot, i) => (
                <li key={i}>
                  <span className="day">{slot.day}</span>
                  <span className="time">{slot.time}</span>
                  <span className="course">{slot.course}</span>
                  <Badge tone={slot.mode === 'Live' ? 'info' : 'neutral'}>{slot.mode}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>

        <Card title="Pending grading">
          <DataTable
            columns={[
              { key: 'title', label: 'Assignment' },
              { key: 'course', label: 'Course' },
              { key: 'due', label: 'Due' },
            ]}
            rows={pendingGrading}
            emptyLabel="Nothing awaiting grading right now."
          />
        </Card>
      </div>

      <Card title="Recent messages" className="msg-card">
        <ul className="msg-list">
          {demoFacultyMessages.map((m) => (
            <li key={m.id}>
              {m.unread && <span className="dot" aria-label="Unread" />}
              <span className="from">{m.from}</span>
              <span className="subject">{m.subject}</span>
              <span className="date">{m.date}</span>
            </li>
          ))}
        </ul>
      </Card>

      <style jsx>{`
        .grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 20px; margin-bottom: 20px; }
        @media (max-width: 960px) { .grid { grid-template-columns: 1fr; } }

        .class-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .class-list li { display: flex; align-items: center; gap: 12px; padding: 10px 4px; border-bottom: 1px solid var(--border); font-size: 13px; flex-wrap: wrap; }
        .class-list li:last-child { border-bottom: none; }
        .class-list .day { font-weight: 600; color: var(--navy); width: 76px; flex-shrink: 0; }
        .class-list .time { color: var(--ink-muted); flex-shrink: 0; }
        .class-list .course { flex: 1; min-width: 140px; color: var(--ink); }

        .msg-card :global(.pcard-body) { padding: 0; }
        .msg-list { list-style: none; margin: 0; padding: 0; }
        .msg-list li { display: flex; align-items: center; gap: 12px; padding: 14px 22px; border-bottom: 1px solid var(--border); font-size: 13.5px; color: var(--ink); }
        .msg-list li:last-child { border-bottom: none; }
        .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--gold); flex-shrink: 0; }
        .from { font-weight: 600; color: var(--navy); flex-shrink: 0; }
        .subject { flex: 1; min-width: 140px; }
        .date { color: var(--ink-muted); font-size: 12px; flex-shrink: 0; }
      `}</style>
    </PortalShell>
  );
}
