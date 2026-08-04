/*
  facultyService — see ./README.md for the service-layer contract.
  Every Faculty Portal screen (src/app/portal/faculty/**) reads through
  this file, never portalDemoData.js directly.
*/

import { demoFaculty, demoCourses, demoRoster, demoFacultyMessages } from '@/lib/portalDemoData';

export async function getFacultyProfile(/* { staffId } */) {
  return demoFaculty;
}

export async function getCoursesTaught(/* { staffId } */) {
  return demoCourses.filter((c) => demoFaculty.coursesTaught.includes(c.id));
}

export async function getRoster(/* { courseId } — the mock roster isn't split per course yet */) {
  return demoRoster;
}

export async function getGradebook(/* { courseId } */) {
  return demoRoster.map((s) => ({ studentId: s.studentId, name: s.name, grades: s.grades }));
}

export async function getFacultyMessages(/* { staffId } */) {
  return demoFacultyMessages;
}

// No real persistence yet — components using this must say so on-screen
// (see AttendanceMarker.jsx's existing "not saved" copy), same honesty
// convention as studentService.updateSettings.
export async function markAttendance({ courseId, records }) {
  return { success: true, courseId, records };
}
