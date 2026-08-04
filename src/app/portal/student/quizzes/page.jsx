import QuizzesView from './QuizzesView';

export const metadata = {
  title: 'Quizzes — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal quiz list, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function QuizzesPage() {
  return <QuizzesView />;
}
