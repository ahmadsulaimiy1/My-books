import {
  getFacultyProfile,
  getCoursesTaught,
  getTimetable,
  getAssignments,
  getFacultyMessages,
} from '@/lib/services/facultyService';
import FacultyDashboardView from './FacultyDashboardView';

export const metadata = {
  title: 'Faculty Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function FacultyDashboardPage() {
  const [faculty, courses, timetable, assignments, messages] = await Promise.all([
    getFacultyProfile(),
    getCoursesTaught(),
    getTimetable(),
    getAssignments(),
    getFacultyMessages(),
  ]);

  return (
    <FacultyDashboardView
      faculty={faculty}
      courses={courses}
      timetable={timetable}
      assignments={assignments}
      messages={messages}
    />
  );
}
