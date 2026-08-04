/*
  applicantService — see ./README.md for the service-layer contract.
  The single Applicant Portal screen (src/app/portal/applicant/page.jsx)
  reads through this file, never portalDemoData.js directly.
*/

import { demoApplicant, admissionJourneySteps, entranceAssessmentSections } from '@/lib/portalDemoData';

export async function getApplicantStatus(/* { applicationId } */) {
  return demoApplicant;
}

export async function getAdmissionJourneySteps() {
  return admissionJourneySteps;
}

export async function getEntranceAssessmentSections() {
  return entranceAssessmentSections;
}
