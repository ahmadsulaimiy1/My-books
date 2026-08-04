'use client';

import Link from 'next/link';
import PortalShell from '@/components/portal/PortalShell';
import { Card, Badge, DataTable } from '@/components/portal/ui';

export default function QuizzesView({ quizzes }) {
  return (
    <PortalShell role="student" active="quizzes" title="Quizzes">
      <Card>
        <DataTable
          columns={[
            {
              key: 'title',
              label: 'Quiz',
              render: (row) => (
                <Link href={`/portal/student/quizzes/${row.id}`} className="quiz-link">
                  {row.title}
                </Link>
              ),
            },
            { key: 'course', label: 'Course' },
            { key: 'questions', label: 'Questions' },
            { key: 'durationMins', label: 'Duration', render: (row) => `${row.durationMins} min` },
            {
              key: 'status',
              label: 'Status',
              render: (row) => (
                <Badge tone={row.status === 'Completed' ? 'success' : 'neutral'}>
                  {row.status}
                  {row.score ? ` — ${row.score}` : ''}
                </Badge>
              ),
            },
          ]}
          rows={quizzes}
        />
      </Card>
      <style jsx>{`
        .quiz-link { color: var(--navy); font-weight: 600; }
        .quiz-link:hover { text-decoration: underline; }
      `}</style>
    </PortalShell>
  );
}
