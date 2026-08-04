/*
  Portal demo data
  ----------------
  The Student/Faculty/Staff/Applicant/Parent portals have no backend yet
  (see /albalagh-lms-portal-scoping.md — Phase 0 needs a real Firebase
  project before any of this becomes live). Every screen under
  src/app/portal/** is a frontend preview: real interface, sample data.

  Rules for this file (do not violate when extending it):
  - Programme names, School names, credit-unit figures, and the AIPS/PCPP
    structure MUST match what's already published on the public site
    (public/legacy/academic-structure.html, institute-professional-studies.html)
    — reuse real facts, don't invent new institutional claims.
  - People (students, lecturers, staff) are clearly fictional placeholders —
    generic enough that nobody could mistake them for a real person. Never
    give a demo person a realistic-sounding full identity (photo, precise
    biography, etc.) that could pass as genuine.
  - Every screen that reads this data must sit inside <PortalShell> so the
    "Preview Mode" banner is always visible alongside it.
*/

export const demoStudent = {
  name: 'Demo Student',
  studentId: 'ALB-DEMO-0001',
  programme: 'Advanced Islamic Sciences & Modern Civilization Studies',
  school: 'School of Islamic Sciences',
  intake: 'September 2026 Intake',
  status: 'Active — Semester 2 of 3',
  creditsCompleted: 24,
  creditsRequired: 69, // midpoint of the published 66–72 CU range
  email: 'demo.student@example.com',
  phone: '+000 000 0000',
  dateOfBirth: '2000-01-01',
};

export const demoCourses = [
  { id: 'AISM-101', title: 'Qurʼanic Sciences I', credits: 3, semester: 1, status: 'Completed', grade: 'A' },
  { id: 'AISM-102', title: 'Foundations of Fiqh', credits: 3, semester: 1, status: 'Completed', grade: 'B+' },
  { id: 'AISM-110', title: 'Arabic Language I', credits: 4, semester: 1, status: 'Completed', grade: 'A-' },
  { id: 'AISM-120', title: 'Digital Literacy for Islamic Studies', credits: 2, semester: 1, status: 'Completed', grade: 'A' },
  { id: 'AISM-201', title: 'Hadith Sciences', credits: 3, semester: 2, status: 'In Progress', grade: null },
  { id: 'AISM-210', title: 'Arabic Language II', credits: 4, semester: 2, status: 'In Progress', grade: null },
  { id: 'AISM-220', title: 'Comparative Religion', credits: 3, semester: 2, status: 'In Progress', grade: null },
  { id: 'AISM-230', title: 'Islamic Civilisation & Modern Thought', credits: 3, semester: 2, status: 'Upcoming', grade: null },
];

export const demoAssignments = [
  { id: 'a1', course: 'AISM-201', title: 'Hadith Chain Analysis — Essay', due: '2026-08-14', status: 'Submitted' },
  { id: 'a2', course: 'AISM-210', title: 'Arabic Composition: Descriptive Paragraph', due: '2026-08-18', status: 'Not started' },
  { id: 'a3', course: 'AISM-220', title: 'Comparative Religion — Discussion Response', due: '2026-08-11', status: 'Overdue' },
  { id: 'a4', course: 'AISM-201', title: 'Hadith Sciences — Weekly Reflection', due: '2026-08-21', status: 'Not started' },
  { id: 'a5', course: 'AISM-230', title: 'Islamic Civilisation — Reading Summary', due: '2026-08-25', status: 'Not started' },
  { id: 'a6', course: 'AISM-102', title: 'Foundations of Fiqh — Case Study', due: '2026-06-02', status: 'Submitted' },
];

export const demoQuizzes = [
  { id: 'q1', course: 'AISM-201', title: 'Week 4 Knowledge Check', questions: 10, durationMins: 15, status: 'Not attempted' },
  { id: 'q2', course: 'AISM-220', title: 'Comparative Religion — Midterm Quiz', questions: 20, durationMins: 30, status: 'Completed', score: '17/20' },
];

export const demoResults = [
  { semester: 'Semester 1', gpa: '3.71', credits: 12, transcript: demoCourses.filter((c) => c.semester === 1) },
  { semester: 'Semester 2 (in progress)', gpa: null, credits: 12, transcript: demoCourses.filter((c) => c.semester === 2) },
];

export const demoTimetable = [
  { day: 'Sunday', slots: [{ time: '10:00–11:30', course: 'AISM-201 Hadith Sciences', mode: 'Live' }] },
  { day: 'Monday', slots: [{ time: '13:00–14:30', course: 'AISM-210 Arabic Language II', mode: 'Live' }] },
  { day: 'Tuesday', slots: [{ time: '10:00–11:00', course: 'AISM-220 Comparative Religion', mode: 'Recorded' }] },
  { day: 'Wednesday', slots: [] },
  { day: 'Thursday', slots: [{ time: '13:00–14:00', course: 'AISM-230 Islamic Civilisation & Modern Thought', mode: 'Live' }] },
];

export const demoAttendance = {
  overall: '92%',
  byCourse: [
    { course: 'AISM-201', attended: 6, total: 7 },
    { course: 'AISM-210', attended: 7, total: 7 },
    { course: 'AISM-220', attended: 6, total: 7 },
  ],
};

export const demoMessages = [
  {
    id: 'm1',
    from: 'Course Coordinator',
    subject: 'Semester 2 orientation recording available',
    date: '2026-08-01',
    unread: true,
    body: 'The recording for the Semester 2 orientation session is now available in the course library. It covers the revised timetable, assessment structure, and how to reach your course coordinators.',
  },
  {
    id: 'm2',
    from: 'Registrar',
    subject: 'Statement of Results — Semester 1 confirmed',
    date: '2026-07-28',
    unread: false,
    body: 'Your Semester 1 results have been confirmed by the Academic Board and are now available under Results. Please contact the Registrar’s Office if you have any queries about your transcript.',
  },
  {
    id: 'm3',
    from: 'Library Services',
    subject: 'New titles added to your reading list',
    date: '2026-07-20',
    unread: false,
    body: 'A number of new e-books and reference titles have been added to the Library relevant to your current courses. You can browse them from the Library section of your portal.',
  },
];

export const demoNotifications = [
  { id: 'n1', text: 'Assignment "Comparative Religion — Discussion Response" is overdue.', date: '2026-08-03', type: 'alert' },
  { id: 'n2', text: 'New quiz available: Week 4 Knowledge Check.', date: '2026-08-01', type: 'info' },
  { id: 'n3', text: 'Semester 1 results have been confirmed by the Academic Board.', date: '2026-07-28', type: 'success' },
];

// Lesson lists for the course player preview — a handful of generic,
// subject-appropriate lesson titles per course, not a full curriculum.
export const demoLessons = {
  'AISM-101': [
    { id: 'l1', title: 'Introduction to the Qur’anic Sciences', durationMins: 20 },
    { id: 'l2', title: 'Makki and Madani Revelations', durationMins: 30 },
    { id: 'l3', title: 'Principles of Tafsir', durationMins: 35 },
    { id: 'l4', title: 'Review & Assessment Preparation', durationMins: 25 },
  ],
  'AISM-102': [
    { id: 'l1', title: 'Foundations of Islamic Jurisprudence', durationMins: 25 },
    { id: 'l2', title: 'Sources of Fiqh', durationMins: 30 },
    { id: 'l3', title: 'Schools of Islamic Law — Overview', durationMins: 30 },
    { id: 'l4', title: 'Case Study Workshop', durationMins: 20 },
  ],
  'AISM-110': [
    { id: 'l1', title: 'Arabic Alphabet & Pronunciation', durationMins: 20 },
    { id: 'l2', title: 'Basic Sentence Structure', durationMins: 25 },
    { id: 'l3', title: 'Everyday Vocabulary', durationMins: 25 },
    { id: 'l4', title: 'Reading Practice', durationMins: 20 },
  ],
  'AISM-120': [
    { id: 'l1', title: 'Digital Research Tools for Islamic Studies', durationMins: 20 },
    { id: 'l2', title: 'Evaluating Online Sources', durationMins: 20 },
    { id: 'l3', title: 'Academic Writing with Digital Tools', durationMins: 25 },
  ],
  'AISM-201': [
    { id: 'l1', title: 'Introduction to Hadith Sciences', durationMins: 20 },
    { id: 'l2', title: 'Isnad and Matn Explained', durationMins: 30 },
    { id: 'l3', title: 'Classifications of Hadith', durationMins: 30 },
    { id: 'l4', title: 'Review & Assessment Preparation', durationMins: 25 },
  ],
  'AISM-210': [
    { id: 'l1', title: 'Descriptive Writing in Arabic', durationMins: 25 },
    { id: 'l2', title: 'Grammar Review — Level 2', durationMins: 30 },
    { id: 'l3', title: 'Conversational Practice', durationMins: 20 },
    { id: 'l4', title: 'Composition Workshop', durationMins: 25 },
  ],
  'AISM-220': [
    { id: 'l1', title: 'Introduction to Comparative Religion', durationMins: 25 },
    { id: 'l2', title: 'Abrahamic Traditions — Overview', durationMins: 30 },
    { id: 'l3', title: 'Eastern Religious Traditions — Overview', durationMins: 30 },
    { id: 'l4', title: 'Midterm Review', durationMins: 20 },
  ],
  'AISM-230': [
    { id: 'l1', title: 'Islamic Civilisation — Historical Overview', durationMins: 30 },
    { id: 'l2', title: 'Encounters with Modern Thought', durationMins: 30 },
    { id: 'l3', title: 'Contemporary Case Studies', durationMins: 25 },
  ],
};

// Sample multiple-choice questions for the quiz-taking preview — a short,
// clearly-labelled subset, not the full quiz described in demoQuizzes.
export const demoQuizQuestions = {
  q1: [
    {
      id: 'q1-1',
      prompt: 'What is the Arabic term for the chain of narrators of a Hadith?',
      options: ['Isnad', 'Matn', 'Tafsir', 'Fiqh'],
      correctIndex: 0,
    },
    {
      id: 'q1-2',
      prompt: 'A Hadith with an unbroken, reliable chain of narration is classified as:',
      options: ['Da’if', 'Mawdu’', 'Sahih', 'Gharib'],
      correctIndex: 2,
    },
    {
      id: 'q1-3',
      prompt: 'The main text or content of a Hadith, as opposed to its chain of narrators, is called the:',
      options: ['Isnad', 'Sanad', 'Rawi', 'Matn'],
      correctIndex: 3,
    },
    {
      id: 'q1-4',
      prompt: 'A "Mutawatir" Hadith is one narrated by:',
      options: [
        'A single narrator in each generation',
        'So many narrators at each stage that collusion on a lie is implausible',
        'An unknown narrator',
        'Only the closest companions of the Prophet',
      ],
      correctIndex: 1,
    },
  ],
  q2: [
    {
      id: 'q2-1',
      prompt: 'Which of the following religions is classified as Abrahamic?',
      options: ['Buddhism', 'Christianity', 'Hinduism', 'Shinto'],
      correctIndex: 1,
    },
    {
      id: 'q2-2',
      prompt: 'Buddhism is generally understood to have originated in which region?',
      options: ['The Indian subcontinent', 'The Arabian Peninsula', 'East Africa', 'Scandinavia'],
      correctIndex: 0,
    },
    {
      id: 'q2-3',
      prompt: 'The Torah is the central text of which religion?',
      options: ['Christianity', 'Islam', 'Judaism', 'Sikhism'],
      correctIndex: 2,
    },
    {
      id: 'q2-4',
      prompt: 'Which term describes belief in a single God?',
      options: ['Polytheism', 'Monotheism', 'Animism', 'Atheism'],
      correctIndex: 1,
    },
  ],
};

export const demoLibrary = [
  { id: 'l1', title: 'Introduction to Hadith Terminology', type: 'E-book', course: 'AISM-201' },
  { id: 'l2', title: 'Arabic Grammar Reference — Level 2', type: 'PDF', course: 'AISM-210' },
  { id: 'l3', title: 'World Religions: A Comparative Survey', type: 'E-book', course: 'AISM-220' },
];

export const demoFaculty = {
  name: 'Demo Lecturer',
  staffId: 'ALB-DEMO-L01',
  department: 'School of Islamic Sciences',
  coursesTaught: ['AISM-201', 'AISM-220'],
};

export const demoStaffRegistrar = {
  name: 'Demo Registrar',
  staffId: 'ALB-DEMO-S01',
  office: 'Registrar’s Office',
};

export const demoApplicant = {
  name: 'Demo Applicant',
  applicationId: 'ALB-APP-DEMO-0001',
  programmeChoice: 'Advanced Islamic Sciences & Modern Civilization Studies',
  route: 'Route A — Senior Secondary Education Qualification',
  stage: 'Entrance Assessment Scheduled',
};
