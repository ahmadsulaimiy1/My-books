import CoursesView from './CoursesView';

export const metadata = {
  title: 'My Courses — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal course list, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function CoursesPage() {
  return <CoursesView />;
}
