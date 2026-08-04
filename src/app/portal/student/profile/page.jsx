import ProfileView from './ProfileView';

export const metadata = {
  title: 'Profile — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal profile view, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function ProfilePage() {
  return <ProfileView />;
}
