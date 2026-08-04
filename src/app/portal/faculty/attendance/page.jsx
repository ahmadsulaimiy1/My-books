import FacultyAttendanceView from './FacultyAttendanceView';

export const metadata = {
  title: 'Attendance — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the Faculty attendance-marking screen in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function FacultyAttendancePage() {
  return <FacultyAttendanceView />;
}
