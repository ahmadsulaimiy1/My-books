import FacultyCoursesView from './FacultyCoursesView';

export const metadata = {
  title: 'My Courses — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the courses taught in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function FacultyCoursesPage() {
  return <FacultyCoursesView />;
}
