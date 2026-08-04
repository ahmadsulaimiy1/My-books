import { getStudentProfile, getCourses, getAssignments } from '@/lib/services/studentService';
import { getNotifications } from '@/lib/services/notificationService';
import StudentDashboardView from './StudentDashboardView';

export const metadata = {
  title: 'Student Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function StudentDashboardPage() {
  const [student, courses, assignments, notifications] = await Promise.all([
    getStudentProfile(),
    getCourses(),
    getAssignments(),
    getNotifications({ role: 'student' }),
  ]);

  return (
    <StudentDashboardView
      student={student}
      courses={courses}
      assignments={assignments}
      notifications={notifications}
    />
  );
}
