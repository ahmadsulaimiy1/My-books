'use client';

import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, EmptyState } from '@/components/portal/ui';
import { demoFaculty, demoCourses, demoLessons, demoRoster } from '@/lib/portalDemoData';

export default function FacultyCoursesView() {
  const myCourses = demoCourses.filter((c) => demoFaculty.coursesTaught.includes(c.id));

  return (
    <PortalShell role="faculty" active="courses" title="My Courses">
      <p className="intro">
        The two courses currently assigned to {demoFaculty.name} in this preview. Enrolment figures use the sample
        roster — there is no real class list behind this yet.
      </p>

      {myCourses.map((course) => {
        const lessons = demoLessons[course.id] ?? [];
        return (
          <Card key={course.id} title={`${course.id} — ${course.title}`} className="course-card">
            <StatGrid>
              <StatTile label="Credit units" value={`${course.credits} CU`} />
              <StatTile label="Semester" value={`Semester ${course.semester}`} />
              <StatTile label="Status" value={<Badge tone="info">{course.status}</Badge>} />
              <StatTile label="Enrolled (sample roster)" value={demoRoster.length} />
            </StatGrid>

            <h3 className="lessons-head">Published lesson content</h3>
            {lessons.length === 0 ? (
              <EmptyState message="No lesson content published for this course in the preview yet." />
            ) : (
              <ol className="lesson-list">
                {lessons.map((lesson, i) => (
                  <li key={lesson.id}>
                    <span className="num">{i + 1}</span>
                    <span className="title">{lesson.title}</span>
                    <span className="duration">{lesson.durationMins} min</span>
                  </li>
                ))}
              </ol>
            )}
          </Card>
        );
      })}

      <style jsx>{`
        .intro { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: -8px 0 20px; }
        .course-card { margin-bottom: 20px; }
        .lessons-head { font-family: 'Fraunces', serif; font-size: 15px; color: var(--navy); margin: 4px 0 10px; }
        .lesson-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .lesson-list li { display: flex; align-items: center; gap: 14px; padding: 10px 4px; border-bottom: 1px solid var(--border); }
        .lesson-list li:last-child { border-bottom: none; }
        .num { width: 22px; height: 22px; border-radius: 50%; background: var(--manuscript); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 11.5px; font-weight: 600; color: var(--navy); flex-shrink: 0; }
        .lesson-list .title { flex: 1; font-size: 13.5px; color: var(--ink); }
        .duration { font-size: 12px; color: var(--ink-muted); flex-shrink: 0; }
      `}</style>
    </PortalShell>
  );
}
