import { getStudentProfile, getResults } from '@/lib/services/studentService';
import ResultsView from './ResultsView';

export const metadata = {
  title: 'Results — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal transcript/results view, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function ResultsPage() {
  const [student, results] = await Promise.all([getStudentProfile(), getResults()]);
  return <ResultsView student={student} results={results} />;
}
