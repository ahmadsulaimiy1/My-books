/*
  parentService — see ./README.md for the service-layer contract.
  The single Parent Portal screen (src/app/portal/parent/page.jsx) reads
  through this file, never portalDemoData.js directly.

  A Parent account's whole job is "view a linked student's progress" — so
  this service composes the same student-facing data studentService
  exposes, filtered/shaped for a read-only guardian view, rather than
  duplicating it.
*/

import { demoParent, demoStudent, demoResults, demoAttendance } from '@/lib/portalDemoData';

export async function getParentProfile(/* { parentId } */) {
  return demoParent;
}

export async function getLinkedStudentOverview(/* { parentId } */) {
  return {
    student: demoStudent,
    results: demoResults,
    attendance: demoAttendance,
  };
}
