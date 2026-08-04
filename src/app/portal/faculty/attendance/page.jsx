import { getFacultyProfile, getRoster } from '@/lib/services/facultyService';
import FacultyAttendanceView from './FacultyAttendanceView';

export const metadata = {
  title: 'Attendance — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the Faculty attendance-marking screen in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function FacultyAttendancePage() {
  const [faculty, roster] = await Promise.all([getFacultyProfile(), getRoster()]);
  return <FacultyAttendanceView faculty={faculty} roster={roster} />;
}
