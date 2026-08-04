import CourseDetailView from './CourseDetailView';
import { demoCourses } from '@/lib/portalDemoData';

export function generateMetadata({ params }) {
  const course = demoCourses.find((c) => c.id === params.courseId);
  return {
    title: `${course ? course.title : 'Course'} — Preview | Albalagh Global`,
    description: 'Frontend preview of an Albalagh Global Student Portal course overview, populated with sample data.',
    robots: { index: false, follow: false },
  };
}

export default function CourseDetailPage({ params }) {
  return <CourseDetailView courseId={params.courseId} />;
}
