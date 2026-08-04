'use client';

import Link from 'next/link';
import PortalShell from '@/components/portal/PortalShell';
import { Card, EmptyState } from '@/components/portal/ui';
import CoursePlayer from '@/components/portal/CoursePlayer';

export default function CoursePlayerView({ course, lessons }) {
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
    <PortalShell role="student" active="courses" title={`${course.title} — Course Player`}>
      <p className="breadcrumb">
        <Link href="/portal/student/courses">My Courses</Link> /{' '}
        <Link href={`/portal/student/courses/${course.id}`}>{course.id}</Link> / Player
      </p>

      {lessons.length === 0 ? (
        <Card>
          <EmptyState message="Lesson content for this course hasn't been added to the preview yet." />
        </Card>
      ) : (
        <CoursePlayer lessons={lessons} />
      )}

      <style jsx>{`
        .breadcrumb { font-size: 13px; color: var(--ink-muted); margin: -12px 0 20px; }
        .breadcrumb :global(a) { color: var(--navy); font-weight: 600; }
      `}</style>
    </PortalShell>
  );
}
