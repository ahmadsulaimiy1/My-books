import { getAttendance } from '@/lib/services/studentService';
import AttendanceView from './AttendanceView';

export const metadata = {
  title: 'Attendance — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal attendance summary, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function AttendancePage() {
  const attendance = await getAttendance();
  return <AttendanceView attendance={attendance} />;
}
