import GradebookView from './GradebookView';

export const metadata = {
  title: 'Gradebook — Faculty Preview | Albalagh Global',
  description: 'Frontend preview of the Faculty gradebook in the Albalagh Global Faculty Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function GradebookPage() {
  return <GradebookView />;
}
