import CoursePlayerView from './CoursePlayerView';
import { demoCourses } from '@/lib/portalDemoData';

export function generateMetadata({ params }) {
  const course = demoCourses.find((c) => c.id === params.courseId);
  return {
    title: `${course ? course.title : 'Course'} — Player Preview | Albalagh Global`,
    description: 'Frontend preview of the Albalagh Global Student Portal course player, populated with sample data.',
    robots: { index: false, follow: false },
  };
}

export default function CoursePlayerPage({ params }) {
  return <CoursePlayerView courseId={params.courseId} />;
}
