import StudentsView from './StudentsView';

export const metadata = {
  title: 'Students — Staff Preview | Albalagh Global',
  description: 'Frontend preview of the Staff student directory in the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function StudentsPage() {
  return <StudentsView />;
}
