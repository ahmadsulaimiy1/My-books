import { getCourse, getLessons } from '@/lib/services/studentService';
import CoursePlayerView from './CoursePlayerView';

export async function generateMetadata({ params }) {
  const course = await getCourse({ courseId: params.courseId });
  return {
    title: `${course ? course.title : 'Course'} — Player Preview | Albalagh Global`,
    description: 'Frontend preview of the Albalagh Global Student Portal course player, populated with sample data.',
    robots: { index: false, follow: false },
  };
}

export default async function CoursePlayerPage({ params }) {
  const [course, lessons] = await Promise.all([
    getCourse({ courseId: params.courseId }),
    getLessons({ courseId: params.courseId }),
  ]);

  return <CoursePlayerView course={course} lessons={lessons} />;
}
