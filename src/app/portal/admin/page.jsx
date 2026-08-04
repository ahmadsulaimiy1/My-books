import AdminDashboardView from './AdminDashboardView';

export const metadata = {
  title: 'Administrator Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Administrator Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function AdminDashboardPage() {
  return <AdminDashboardView />;
}
