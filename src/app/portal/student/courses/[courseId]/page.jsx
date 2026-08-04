import { getCourse, getLessons } from '@/lib/services/studentService';
import CourseDetailView from './CourseDetailView';

export async function generateMetadata({ params }) {
  const course = await getCourse({ courseId: params.courseId });
  return {
    title: `${course ? course.title : 'Course'} — Preview | Albalagh Global`,
    description: 'Frontend preview of an Albalagh Global Student Portal course overview, populated with sample data.',
    robots: { index: false, follow: false },
  };
}

export default async function CourseDetailPage({ params }) {
  const [course, lessons] = await Promise.all([
    getCourse({ courseId: params.courseId }),
    getLessons({ courseId: params.courseId }),
  ]);

  return <CourseDetailView course={course} lessons={lessons} />;
}
