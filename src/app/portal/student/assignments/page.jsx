import { getAssignments } from '@/lib/services/studentService';
import AssignmentsView from './AssignmentsView';

export const metadata = {
  title: 'Assignments — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal assignment list, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function AssignmentsPage() {
  const assignments = await getAssignments();
  return <AssignmentsView assignments={assignments} />;
}
