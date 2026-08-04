import ApplicantStatusView from './ApplicantStatusView';

export const metadata = {
  title: 'Application Status — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Applicant Portal application status screen, populated with sample data.',
  robots: { index: false, follow: false },
};

export default function ApplicantStatusPage() {
  return <ApplicantStatusView />;
}
