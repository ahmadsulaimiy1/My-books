/*
  authService — see ./README.md for the service-layer contract.

  There is no real authentication yet (albalagh-lms-portal-scoping.md
  Phase 0). Portal routes are reached by direct navigation per role, not a
  login flow — each role's page.jsx currently calls that role's own
  get*Profile() function (e.g. getStudentProfile()) directly rather than
  going through getCurrentUser(role) here. Nothing in this file is called
  from anywhere yet; every export — including getCurrentUser — is written
  against the shape a real login flow will need, and signIn/signOut/
  onAuthStateChange throw clearly rather than silently pretending to work.
*/

import {
  demoStudent,
  demoFaculty,
  demoStaffRegistrar,
  demoAdmin,
  demoApplicant,
  demoParent,
} from '@/lib/portalDemoData';

const PERSONA_BY_ROLE = {
  student: demoStudent,
  faculty: demoFaculty,
  staff: demoStaffRegistrar,
  admin: demoAdmin,
  applicant: demoApplicant,
  parent: demoParent,
};

export async function getCurrentUser(role) {
  const persona = PERSONA_BY_ROLE[role];
  if (!persona) throw new Error(`authService.getCurrentUser: unknown role "${role}"`);
  return { role, ...persona };
}

export async function signIn(/* { email, password } */) {
  throw new Error(
    'authService.signIn: not implemented — no real authentication exists yet. Wire this to Firebase Auth (signInWithEmailAndPassword) when Phase 0 lands.'
  );
}

export async function signOut() {
  throw new Error(
    'authService.signOut: not implemented — no real authentication exists yet. Wire this to Firebase Auth (signOut) when Phase 0 lands.'
  );
}

export function onAuthStateChange(/* callback */) {
  throw new Error(
    'authService.onAuthStateChange: not implemented — wire this to Firebase Auth (onAuthStateChanged) when Phase 0 lands.'
  );
}
