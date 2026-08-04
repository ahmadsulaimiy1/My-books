import { getFacultyProfile } from '@/lib/services/facultyService';
import FacultyProfileView from './FacultyProfileView';

export const metadata = {
  title: 'Profile — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the Faculty profile screen in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function FacultyProfilePage() {
  const faculty = await getFacultyProfile();
  return <FacultyProfileView faculty={faculty} />;
}
