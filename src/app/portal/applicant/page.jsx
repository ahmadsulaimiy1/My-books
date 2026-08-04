import {
  getApplicantStatus,
  getAdmissionJourneySteps,
  getEntranceAssessmentSections,
} from '@/lib/services/applicantService';
import ApplicantStatusView from './ApplicantStatusView';

export const metadata = {
  title: 'Application Status — Preview | Albalagh Global',
  description: 'Frontend preview of the Albalagh Global Applicant Portal application status screen, populated with sample data.',
  robots: { index: false, follow: false },
};

export default async function ApplicantStatusPage() {
  const [applicant, journeySteps, assessmentSections] = await Promise.all([
    getApplicantStatus(),
    getAdmissionJourneySteps(),
    getEntranceAssessmentSections(),
  ]);

  return (
    <ApplicantStatusView applicant={applicant} journeySteps={journeySteps} assessmentSections={assessmentSections} />
  );
}
