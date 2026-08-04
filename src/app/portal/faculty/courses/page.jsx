import { getFacultyProfile, getCoursesTaught, getRoster, getLessons } from '@/lib/services/facultyService';
import FacultyCoursesView from './FacultyCoursesView';

export const metadata = {
  title: 'My Courses — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the courses taught in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function FacultyCoursesPage() {
  const [faculty, courses, roster] = await Promise.all([
    getFacultyProfile(),
    getCoursesTaught(),
    getRoster(),
  ]);

  const lessonsByCourse = Object.fromEntries(
    await Promise.all(courses.map(async (c) => [c.id, await getLessons({ courseId: c.id })]))
  );

  return (
    <FacultyCoursesView faculty={faculty} courses={courses} roster={roster} lessonsByCourse={lessonsByCourse} />
  );
}
