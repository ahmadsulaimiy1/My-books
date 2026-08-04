/*
  studentService — see ./README.md for the service-layer contract.
  Every Student Portal screen (src/app/portal/student/**) reads through
  this file, never portalDemoData.js directly.
*/

import {
  demoStudent,
  demoCourses,
  demoLessons,
  demoAssignments,
  demoQuizzes,
  demoQuizQuestions,
  demoResults,
  demoTimetable,
  demoAttendance,
  demoMessages,
} from '@/lib/portalDemoData';
import { getNotifications as getNotificationsShared } from './notificationService';

export async function getStudentProfile(/* { studentId } */) {
  return demoStudent;
}

export async function getCourses(/* { studentId } */) {
  return demoCourses;
}

export async function getCourse({ courseId }) {
  return demoCourses.find((c) => c.id === courseId) ?? null;
}

export async function getLessons({ courseId }) {
  return demoLessons[courseId] ?? [];
}

export async function getAssignments(/* { studentId } */) {
  return demoAssignments;
}

export async function getQuizzes(/* { studentId } */) {
  return demoQuizzes;
}

export async function getQuiz({ quizId }) {
  const quiz = demoQuizzes.find((q) => q.id === quizId) ?? null;
  if (!quiz) return null;
  // `quiz.questions` is the full-quiz question count (a number, from
  // demoQuizzes) — preserve it as `totalQuestions` rather than clobbering
  // it with the attached sample-question bank.
  //
  // Deliberately strip `correctIndex` from each question before this
  // reaches the client: this is the pre-submission taking view, and a real
  // Firestore-backed quiz-questions read would never return the answer key
  // to a student who hasn't submitted yet — it's a graded assessment, not
  // a study guide. `submitQuiz` below grades against its own independent
  // lookup of the answer key, so nothing downstream needs it here.
  const questions = (demoQuizQuestions[quizId] ?? []).map(({ correctIndex, ...question }) => question);
  return { ...quiz, totalQuestions: quiz.questions, questions };
}

// Mirrors what a real submit-quiz endpoint returns: a score against the
// question bank, not just an acknowledgement. Grading happens against the
// server-held answer key (demoQuizQuestions) — looked up independently of
// whatever getQuiz returned to the client — never trusting a client-sent
// score, the same trust boundary a real backend would need.
export async function submitQuiz({ quizId, answers }) {
  const questions = demoQuizQuestions[quizId] ?? [];
  let correct = 0;
  const review = questions.map((q, i) => {
    const isCorrect = answers[i] === q.correctIndex;
    if (isCorrect) correct += 1;
    return { question: q.prompt, selected: answers[i], correctIndex: q.correctIndex, isCorrect };
  });
  return { success: true, quizId, score: correct, total: questions.length, review };
}

export async function getResults(/* { studentId } */) {
  return demoResults;
}

export async function getTimetable(/* { studentId } */) {
  return demoTimetable;
}

export async function getAttendance(/* { studentId } */) {
  return demoAttendance;
}

export async function getMessages(/* { studentId } */) {
  return demoMessages;
}

export async function getNotifications({ studentId } = {}) {
  return getNotificationsShared({ role: 'student', userId: studentId });
}

// No real persistence yet — see SettingsView.jsx's own on-screen copy,
// which is honest with the user about this rather than implying a save
// that doesn't happen.
export async function updateSettings(settings) {
  return { success: true, settings };
}
