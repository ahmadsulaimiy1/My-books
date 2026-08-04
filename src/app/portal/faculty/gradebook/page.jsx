import { getFacultyProfile, getGradebook } from '@/lib/services/facultyService';
import GradebookView from './GradebookView';

export const metadata = {
  title: 'Gradebook — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the Faculty gradebook in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function GradebookPage() {
  const [faculty, gradebook] = await Promise.all([getFacultyProfile(), getGradebook()]);
  return <GradebookView faculty={faculty} gradebook={gradebook} />;
}
