import { getQuiz } from '@/lib/services/studentService';
import QuizTakingView from './QuizTakingView';

export async function generateMetadata({ params }) {
  const quiz = await getQuiz({ quizId: params.quizId });
  return {
    title: `${quiz ? quiz.title : 'Quiz'} — Preview | Albalagh Global`,
    description: 'Frontend preview of the Albalagh Global Student Portal quiz-taking flow, populated with sample data.',
    robots: { index: false, follow: false },
  };
}

export default async function QuizTakingPage({ params }) {
  const quiz = await getQuiz({ quizId: params.quizId });
  return <QuizTakingView quiz={quiz} />;
}
