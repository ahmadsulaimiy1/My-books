import TimetableView from './TimetableView';

export const metadata = {
  title: 'Timetable — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Student Portal weekly timetable, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function TimetablePage() {
  return <TimetableView />;
}
