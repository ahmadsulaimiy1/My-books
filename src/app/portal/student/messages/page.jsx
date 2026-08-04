import MessagesView from './MessagesView';

export const metadata = {
  title: 'Messages — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal inbox, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function MessagesPage() {
  return <MessagesView />;
}
