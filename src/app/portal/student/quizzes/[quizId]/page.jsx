import QuizTakingView from './QuizTakingView';
import { demoQuizzes } from '@/lib/portalDemoData';

export function generateMetadata({ params }) {
  const quiz = demoQuizzes.find((q) => q.id === params.quizId);
  return {
    title: `${quiz ? quiz.title : 'Quiz'} — Preview | Albalagh Global`,
    description: 'Frontend preview of the Albalagh Global Student Portal quiz-taking flow, populated with sample data.',
    robots: { index: false, follow: false },
  };
}

export default function QuizTakingPage({ params }) {
  return <QuizTakingView quizId={params.quizId} />;
}
