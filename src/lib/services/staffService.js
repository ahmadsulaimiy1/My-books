/*
  staffService — see ./README.md for the service-layer contract.
  Every Staff Portal screen (src/app/portal/staff/**) reads through this
  file, never portalDemoData.js directly.
*/

import { demoStaffRegistrar, demoApplications, demoFeeTypes, demoLedger, demoRoster } from '@/lib/portalDemoData';

export async function getStaffProfile(/* { staffId } */) {
  return demoStaffRegistrar;
}

export async function getApplications() {
  return demoApplications;
}

export async function getFeeTypes() {
  return demoFeeTypes;
}

export async function getLedger() {
  return demoLedger.map((entry) => ({
    ...entry,
    feeType: demoFeeTypes.find((f) => f.key === entry.feeKey) ?? null,
  }));
}

export async function getStudents() {
  return demoRoster;
}
