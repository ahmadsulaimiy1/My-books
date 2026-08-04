import StaffProfileView from './StaffProfileView';

export const metadata = {
  title: 'Profile — Staff Preview | Albalagh Global',
  description: 'Frontend preview of the Staff profile screen in the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function StaffProfilePage() {
  return <StaffProfileView />;
}
