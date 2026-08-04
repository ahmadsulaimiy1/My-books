'use client';

import Link from 'next/link';
import PortalShell from '@/components/portal/PortalShell';
import { Card, StatGrid, StatTile, Badge, EmptyState } from '@/components/portal/ui';

const STATUS_TONE = { Completed: 'success', 'In Progress': 'info', Upcoming: 'neutral' };

export default function CourseDetailView({ course, lessons }) {
  if (!course) {
    return (
      <PortalShell role="student" active="courses" title="Course not found">
        <Card>
          <EmptyState
            message="We couldn't find that course in this preview."
            action={
              <Link href="/portal/student/courses" className="back-link">
                Back to My Courses
              </Link>
            }
          />
        </Card>
        <style jsx>{`
          .back-link { color: var(--navy); font-weight: 600; font-size: 13.5px; }
        `}</style>
      </PortalShell>
    );
  }

  return (
    <PortalShell role="student" active="courses" title={course.title}>
      <p className="breadcrumb">
        <Link href="/portal/student/courses">My Courses</Link> / {course.id}
      </p>

      <StatGrid>
        <StatTile label="Course code" value={course.id} />
        <StatTile label="Credit units" value={`${course.credits} CU`} />
        <StatTile label="Semester" value={`Semester ${course.semester}`} />
        <StatTile
          label="Status"
          value={<Badge tone={STATUS_TONE[course.status] ?? 'neutral'}>{course.status}</Badge>}
          hint={course.grade ? `Grade: ${course.grade}` : undefined}
        />
      </StatGrid>

      <Card
        title="Syllabus overview"
        action={
          <Link href={`/portal/student/courses/${course.id}/player`} className="player-link">
            Open course player
          </Link>
        }
      >
        <p className="intro">
          This course is organised into the following lessons. Open the course player to work through them and
          track your progress.
        </p>
        {lessons.length === 0 ? (
          <EmptyState message="Lesson content for this course hasn't been added to the preview yet." />
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

      <style jsx>{`
        .breadcrumb { font-size: 13px; color: var(--ink-muted); margin: -12px 0 20px; }
        .breadcrumb :global(a) { color: var(--navy); font-weight: 600; }
        .player-link { background: var(--navy); color: #fff; border-radius: var(--radius-sm); padding: 8px 16px; font-size: 13px; font-weight: 600; white-space: nowrap; }
        .player-link:hover { background: var(--navy-dark); }
        .intro { font-size: 13.5px; color: var(--ink-muted); line-height: 1.6; margin: 0 0 16px; }
        .lesson-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 2px; }
        .lesson-list li { display: flex; align-items: center; gap: 14px; padding: 12px 4px; border-bottom: 1px solid var(--border); }
        .lesson-list li:last-child { border-bottom: none; }
        .num { width: 24px; height: 24px; border-radius: 50%; background: var(--manuscript); border: 1px solid var(--border); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: var(--navy); flex-shrink: 0; }
        .lesson-list .title { flex: 1; font-size: 13.5px; color: var(--ink); }
        .duration { font-size: 12px; color: var(--ink-muted); flex-shrink: 0; }
      `}</style>
    </PortalShell>
  );
}
