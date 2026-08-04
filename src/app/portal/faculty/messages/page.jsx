import { getFacultyMessages } from '@/lib/services/facultyService';
import FacultyMessagesView from './FacultyMessagesView';

export const metadata = {
  title: 'Messages — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the Faculty messages inbox in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function FacultyMessagesPage() {
  const messages = await getFacultyMessages();
  return <FacultyMessagesView messages={messages} />;
}
