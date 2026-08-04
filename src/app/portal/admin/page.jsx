import { getAdminProfile, getUsers, getApplications, getOverviewStats } from '@/lib/services/adminService';
import AdminDashboardView from './AdminDashboardView';

export const metadata = {
  title: 'Administrator Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Administrator Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function AdminDashboardPage() {
  const [admin, users, applications, overview] = await Promise.all([
    getAdminProfile(),
    getUsers(),
    getApplications(),
    getOverviewStats(),
  ]);

  return <AdminDashboardView admin={admin} users={users} applications={applications} overview={overview} />;
}
