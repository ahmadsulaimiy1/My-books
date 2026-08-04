/*
  facultyService — see ./README.md for the service-layer contract.
  Every Faculty Portal screen (src/app/portal/faculty/**) reads through
  this file, never portalDemoData.js directly.
*/

import {
  demoFaculty,
  demoCourses,
  demoRoster,
  demoFacultyMessages,
  demoTimetable,
  demoAssignments,
  demoLessons,
} from '@/lib/portalDemoData';

export async function getFacultyProfile(/* { staffId } */) {
  return demoFaculty;
}

export async function getCoursesTaught(/* { staffId } */) {
  return demoCourses.filter((c) => demoFaculty.coursesTaught.includes(c.id));
}

export async function getLessons({ courseId }) {
  return demoLessons[courseId] ?? [];
}

export async function getRoster(/* { courseId } — the mock roster isn't split per course yet */) {
  return demoRoster;
}

export async function getGradebook(/* { courseId } */) {
  return demoRoster.map((s) => ({ studentId: s.studentId, name: s.name, grades: s.grades }));
}

// Full timetable — the dashboard screen filters this down to the sessions
// for this faculty member's own courses.
export async function getTimetable(/* { staffId } */) {
  return demoTimetable;
}

// Full assignment set — the dashboard screen filters this down to the
// items awaiting grading for this faculty member's own courses.
export async function getAssignments(/* { staffId } */) {
  return demoAssignments;
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
