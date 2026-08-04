import { getMessages } from '@/lib/services/studentService';
import MessagesView from './MessagesView';

export const metadata = {
  title: 'Messages — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal inbox, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function MessagesPage() {
  const messages = await getMessages();
  return <MessagesView messages={messages} />;
}
