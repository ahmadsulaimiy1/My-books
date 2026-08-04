import { getStaffProfile, getApplications, getLedger, getStudents } from '@/lib/services/staffService';
import StaffDashboardView from './StaffDashboardView';

export const metadata = {
  title: 'Staff Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function StaffDashboardPage() {
  const [staff, applications, ledger, students] = await Promise.all([
    getStaffProfile(),
    getApplications(),
    getLedger(),
    getStudents(),
  ]);

  return (
    <StaffDashboardView staff={staff} applications={applications} ledger={ledger} students={students} />
  );
}
