import StudentDashboardView from './StudentDashboardView';

export const metadata = {
  title: 'Student Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function StudentDashboardPage() {
  return <StudentDashboardView />;
}
