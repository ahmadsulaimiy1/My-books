import { getNotifications } from '@/lib/services/notificationService';
import NotificationsView from './NotificationsView';

export const metadata = {
  title: 'Notifications — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal notifications list, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function NotificationsPage() {
  const notifications = await getNotifications({ role: 'student' });
  return <NotificationsView notifications={notifications} />;
}
