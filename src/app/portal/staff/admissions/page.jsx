import AdmissionsView from './AdmissionsView';

export const metadata = {
  title: 'Admissions — Staff Preview | Albalagh Global',
  description: 'Frontend preview of the Staff admissions queue in the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function AdmissionsPage() {
  return <AdmissionsView />;
}
