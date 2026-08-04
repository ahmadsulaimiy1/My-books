import { getApplications, getAdmissionJourneySteps } from '@/lib/services/staffService';
import AdmissionsView from './AdmissionsView';

export const metadata = {
  title: 'Admissions — Staff Preview | Albalagh Global',
  description: 'Frontend preview of the Staff admissions queue in the Albalagh Global Staff Portal, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function AdmissionsPage() {
  const [applications, journeySteps] = await Promise.all([getApplications(), getAdmissionJourneySteps()]);
  return <AdmissionsView applications={applications} journeySteps={journeySteps} />;
}
