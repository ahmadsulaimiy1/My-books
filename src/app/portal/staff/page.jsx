import StaffDashboardView from './StaffDashboardView';

export const metadata = {
  title: 'Staff Dashboard — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function StaffDashboardPage() {
  return <StaffDashboardView />;
}
