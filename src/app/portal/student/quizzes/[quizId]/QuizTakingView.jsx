'use client';

import Link from 'next/link';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, EmptyState } from '@/components/portal/ui';
import QuizRunner from '@/components/portal/QuizRunner';

export default function QuizTakingView({ quiz }) {
  if (!quiz) {
    return (
      <PortalShell role="student" active="quizzes" title="Quiz not found">
        <Card>
          <EmptyState
            message="We couldn't find that quiz in this preview."
            action={
              <Link href="/portal/student/quizzes" className="back-link">
                Back to Quizzes
              </Link>
            }
          />
        </Card>
        <style jsx>{`
          .back-link { color: var(--navy); font-weight: 600; font-size: 13.5px; }
        `}</style>
      </PortalShell>
    );
  }

  return (
    <PortalShell role="student" active="quizzes" title={quiz.title}>
      <p className="breadcrumb">
        <Link href="/portal/student/quizzes">Quizzes</Link> / {quiz.title}
      </p>

      <div className="meta-row">
        <span>{quiz.course}</span>
        <span>{quiz.totalQuestions} questions in the full quiz</span>
        <span>{quiz.durationMins} min</span>
        {quiz.status === 'Completed' && <Badge tone="success">Previously completed — {quiz.score}</Badge>}
      </div>

      <Card title="Sample quiz">
        {quiz.questions.length === 0 ? (
          <EmptyState message="Sample questions for this quiz haven't been added to the preview yet." />
        ) : (
          <QuizRunner quizId={quiz.id} questions={quiz.questions} />
        )}
      </Card>

      <style jsx>{`
        .breadcrumb { font-size: 13px; color: var(--ink-muted); margin: -12px 0 16px; }
        .breadcrumb :global(a) { color: var(--navy); font-weight: 600; }
        .meta-row { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; font-size: 13px; color: var(--ink-muted); margin-bottom: 20px; }
      `}</style>
    </PortalShell>
  );
}
