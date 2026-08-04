/*
  adminService — see ./README.md for the service-layer contract.
  Every Admin Portal screen (src/app/portal/admin/**) reads through this
  file, never portalDemoData.js directly.
*/

import {
  demoAdmin,
  demoUsers,
  ROLE_OPTIONS,
  demoProgrammes,
  creditUnitPolicy,
  demoRoster,
  demoCourses,
  demoApplications,
} from '@/lib/portalDemoData';

export async function getAdminProfile() {
  return demoAdmin;
}

export async function getUsers() {
  return demoUsers;
}

// The dashboard's admissions-queue snapshot reuses the same sample queue
// staffService exposes to the registrar's own Admissions screen.
export async function getApplications() {
  return demoApplications;
}

export async function getRoleOptions() {
  return ROLE_OPTIONS;
}

// No real persistence yet — the mock accepts and echoes the change so the
// UI can update local state optimistically, same honesty convention as
// the rest of this layer.
export async function updateUserRole({ userId, role }) {
  if (!ROLE_OPTIONS.includes(role)) throw new Error(`adminService.updateUserRole: invalid role "${role}"`);
  return { success: true, userId, role };
}

export async function getProgrammes() {
  return demoProgrammes;
}

export async function getCreditUnitPolicy() {
  return creditUnitPolicy;
}

export async function getOverviewStats() {
  return {
    sampleStudents: demoRoster.length,
    sampleCourses: demoCourses.length,
    programmes: demoProgrammes.length,
  };
}
