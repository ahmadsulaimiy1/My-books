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

export const demoAdmin = {
  name: 'Demo Administrator',
  staffId: 'ALB-DEMO-A01',
  office: "Office of the Registrar & Administration",
};

export const demoParent = {
  name: 'Demo Parent/Guardian',
  parentId: 'ALB-DEMO-P01',
  linkedStudent: demoStudent.name,
  linkedStudentId: demoStudent.studentId,
};

// The 13-step "first click to first day of class" admission journey, as
// published on public/legacy/admissions.html#journey. Reused by the
// Applicant status page and the Staff admissions queue so both screens
// describe the same real pipeline.
export const admissionJourneySteps = [
  'Explore Programmes',
  'Create Applicant Account',
  'Complete Application',
  'Upload Documents',
  'Submit Statement of Purpose',
  'Pay Application Fee',
  'Application Review',
  'Entrance Assessment',
  'Admission Decision',
  'Accept Admission',
  'Complete Registration',
  'Student Account Activation',
  'Begin Studies',
];

// The six admission routes published on public/legacy/admissions.html#routes.
export const admissionRoutes = [
  'Route 01 — Standard Secondary Qualifications',
  'Route 02 — Islamic Education Route',
  'Route 03 — Awaiting Results',
  'Route 04 — Certificate Progression',
  'Route 05 — Mature Learner Route',
  'Route 06 — Recognition of Prior Learning (RPL)',
];

// The Mandatory Entrance Assessment sections, from
// public/legacy/admissions.html#entrance-assessment.
export const entranceAssessmentSections = [
  {
    name: 'General Section (All Applicants)',
    detail: 'English Language and Communication, Basic Mathematics / Numeracy, Logical Reasoning, Digital Literacy, General Knowledge.',
  },
  {
    name: 'Islamic Sciences Applicants',
    detail: "May include basic Islamic knowledge, Qur'an understanding, Arabic foundation, and Islamic terminology. Applicants with strong Islamic qualifications such as Thanawiyyah or NBAIS may be assessed differently according to their background.",
  },
  {
    name: 'Technology Applicants',
    detail: 'May include computer awareness, logical thinking, and problem-solving.',
  },
  {
    name: 'Business Applicants',
    detail: 'May include basic numeracy, business awareness, and communication ability.',
  },
];

export const demoApplicant = {
  name: 'Demo Applicant',
  applicationId: 'ALB-APP-DEMO-0001',
  programmeChoice: 'Advanced Islamic Sciences & Modern Civilization Studies',
  route: admissionRoutes[0],
  stage: 'Entrance Assessment',
  currentStep: 8, // matches admissionJourneySteps[7], 1-indexed for display
  submittedDate: '2026-07-18',
  assessmentDate: '2026-08-12',
};

// Faculty gradebook / attendance roster. There is no real student directory
// yet, so this is a small set of obviously-placeholder rows ("Student A",
// "Student B", ...) — not real names — used for the Faculty gradebook and
// attendance-marking preview, and reused by the Staff student directory.
export const demoRoster = [
  {
    id: 'r1',
    name: 'Student A',
    studentId: 'ALB-DEMO-1001',
    programme: demoStudent.programme,
    grades: { 'AISM-201': 'A-', 'AISM-220': 'B+' },
  },
  {
    id: 'r2',
    name: 'Student B',
    studentId: 'ALB-DEMO-1002',
    programme: demoStudent.programme,
    grades: { 'AISM-201': 'B', 'AISM-220': 'A' },
  },
  {
    id: 'r3',
    name: 'Student C',
    studentId: 'ALB-DEMO-1003',
    programme: demoStudent.programme,
    grades: { 'AISM-201': 'B+', 'AISM-220': 'B' },
  },
  {
    id: 'r4',
    name: 'Student D',
    studentId: 'ALB-DEMO-1004',
    programme: demoStudent.programme,
    grades: { 'AISM-201': 'A', 'AISM-220': 'A-' },
  },
  {
    id: 'r5',
    name: 'Student E',
    studentId: 'ALB-DEMO-1005',
    programme: demoStudent.programme,
    grades: { 'AISM-201': null, 'AISM-220': 'C+' },
  },
];

// Sample admissions queue for the Staff Admissions screen. Applicant
// identities are clearly placeholder ("Applicant A" etc.); the routes,
// programmes, and stage names are the real ones published on
// public/legacy/admissions.html.
export const demoApplications = [
  {
    id: 'app1',
    name: 'Applicant A',
    applicationId: 'ALB-APP-DEMO-1001',
    programme: 'Advanced Islamic Sciences and Modern Civilization Studies',
    route: admissionRoutes[0],
    stage: 'Application Review',
    submitted: '2026-07-22',
  },
  {
    id: 'app2',
    name: 'Applicant B',
    applicationId: 'ALB-APP-DEMO-1002',
    programme: "Islamic Law (Shari'ah)",
    route: admissionRoutes[1],
    stage: 'Entrance Assessment',
    submitted: '2026-07-15',
  },
  {
    id: 'app3',
    name: 'Applicant C',
    applicationId: 'ALB-APP-DEMO-1003',
    programme: 'Artificial Intelligence and Data Science',
    route: admissionRoutes[4],
    stage: 'Admission Decision',
    submitted: '2026-06-30',
  },
  {
    id: 'app4',
    name: 'Applicant D',
    applicationId: 'ALB-APP-DEMO-1004',
    programme: 'Business Administration and Entrepreneurship',
    route: admissionRoutes[2],
    stage: 'Accept Admission',
    submitted: '2026-06-18',
  },
  {
    id: 'app5',
    name: 'Applicant E',
    applicationId: 'ALB-APP-DEMO-1005',
    programme: 'Journalism and Mass Communication',
    route: admissionRoutes[5],
    stage: 'Complete Registration',
    submitted: '2026-06-02',
  },
];

// Fee types on the Staff Finance ledger. Only the AIPS Professional
// Competency Programme Fee has a published amount
// (public/legacy/institute-professional-studies.html#fees — ₦5,000
// Institute Registration Fee + ₦15,000 Professional Practice and Training
// Fee = ₦20,000 total). Every other institutional fee type is listed on
// public/legacy/tuition-scholarships.html#fee-schedule as "TBC" — amount
// not yet set by the Governing Council's Finance & Audit Committee — so
// this preview carries that TBC status forward rather than inventing a
// figure.
export const demoFeeTypes = [
  {
    key: 'aips',
    label: 'AIPS Professional Competency Programme Fee',
    amount: 20000,
    note: 'Institute Registration Fee ₦5,000 + Professional Practice and Training Fee ₦15,000.',
  },
  {
    key: 'application',
    label: 'Application Fee',
    amount: null,
    note: 'Amount to be confirmed — listed as TBC on the official fee schedule.',
  },
  {
    key: 'registration',
    label: 'Registration Fee',
    amount: null,
    note: 'Amount to be confirmed — listed as TBC on the official fee schedule.',
  },
  {
    key: 'attachment',
    label: 'Industrial Attachment Administration Fee',
    amount: null,
    note: 'Where applicable; amount TBC on the official fee schedule.',
  },
  {
    key: 'convocation',
    label: 'Convocation & Certification Fee',
    amount: null,
    note: 'Amount to be confirmed — listed as TBC on the official fee schedule.',
  },
];

// Sample fee ledger line items against the placeholder roster — a preview
// only, no real payment processing. Amounts are pulled from demoFeeTypes
// above (null = TBC, matching the published fee schedule).
export const demoLedger = [
  { id: 'f1', studentId: 'ALB-DEMO-1001', student: 'Student A', feeKey: 'aips', status: 'Paid', date: '2026-06-20' },
  { id: 'f2', studentId: 'ALB-DEMO-1002', student: 'Student B', feeKey: 'application', status: 'Awaiting institutional rate', date: '2026-07-02' },
  { id: 'f3', studentId: 'ALB-DEMO-1003', student: 'Student C', feeKey: 'aips', status: 'Outstanding', date: '2026-08-01' },
  { id: 'f4', studentId: 'ALB-DEMO-1001', student: 'Student A', feeKey: 'registration', status: 'Awaiting institutional rate', date: '2026-06-01' },
  { id: 'f5', studentId: 'ALB-DEMO-1004', student: 'Student D', feeKey: 'aips', status: 'Paid', date: '2026-07-28' },
  { id: 'f6', studentId: 'ALB-DEMO-1005', student: 'Student E', feeKey: 'aips', status: 'Outstanding', date: '2026-08-03' },
];

// Sample accounts across every portal role, for the Admin "Users & Roles"
// screen. Identifiers reuse the demo records already defined above rather
// than inventing new identities.
export const demoUsers = [
  { id: 'u1', name: demoStudent.name, identifier: demoStudent.studentId, role: 'student', status: 'Active' },
  { id: 'u2', name: 'Student B (preview)', identifier: 'ALB-DEMO-1002', role: 'student', status: 'Active' },
  { id: 'u3', name: demoFaculty.name, identifier: demoFaculty.staffId, role: 'faculty', status: 'Active' },
  { id: 'u4', name: demoStaffRegistrar.name, identifier: demoStaffRegistrar.staffId, role: 'staff', status: 'Active' },
  { id: 'u5', name: demoAdmin.name, identifier: demoAdmin.staffId, role: 'admin', status: 'Active' },
  { id: 'u6', name: demoApplicant.name, identifier: demoApplicant.applicationId, role: 'applicant', status: 'Pending' },
  { id: 'u7', name: demoParent.name, identifier: demoParent.parentId, role: 'parent', status: 'Active' },
];

export const ROLE_OPTIONS = ['student', 'faculty', 'staff', 'admin', 'applicant', 'parent'];

// Institutional Credit Unit Policy figures, as published on
// public/legacy/academic-structure.html#academic-structure (Semester
// Workload: min 20 / recommended 22–24 / max 26 CU per semester). Every
// Professional Diploma Programme runs 3 semesters over one year, so the
// recommended-workload total (22–24 × 3) is 66–72 CU — the same range
// already published specifically for the Advanced Islamic Sciences &
// Modern Civilization Studies programme — and the min/max-workload total
// (20–26 × 3) is 60–78 CU. These are used as the typical range for every
// programme below; only AISM has that exact 66–72 CU figure explicitly
// published on the public site.
export const creditUnitPolicy = {
  semesterMin: 20,
  semesterRecommendedLow: 22,
  semesterRecommendedHigh: 24,
  semesterMax: 26,
  semesters: 3,
};

// The 8 published Departments/Programmes, grouped by their 4 Schools, from
// public/legacy/academic-structure.html#schools. Every Professional Diploma
// Programme runs 3 semesters over 1 year (Academic Structure page), plus a
// 6-week industrial attachment and the 5-week AIPS Professional Competency
// and Practice Programme.
export const demoProgrammes = [
  {
    id: 'p1',
    school: 'School of Islamic Sciences',
    programme: 'Advanced Islamic Sciences and Modern Civilization Studies',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (published programme figure)',
  },
  {
    id: 'p2',
    school: 'School of Islamic Sciences',
    programme: "Islamic Law (Shari'ah)",
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
  {
    id: 'p3',
    school: 'School of Media, Journalism and Digital Communication',
    programme: 'Journalism and Mass Communication',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
  {
    id: 'p4',
    school: 'School of Media, Journalism and Digital Communication',
    programme: 'Multimedia and Digital Media Technology',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
  {
    id: 'p5',
    school: 'School of Artificial Intelligence, Innovation and Technology',
    programme: 'Artificial Intelligence and Data Science',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
  {
    id: 'p6',
    school: 'School of Artificial Intelligence, Innovation and Technology',
    programme: 'Software Development and Digital Innovation',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
  {
    id: 'p7',
    school: 'School of Business, Entrepreneurship and Financial Management',
    programme: 'Business Administration and Entrepreneurship',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
  {
    id: 'p8',
    school: 'School of Business, Entrepreneurship and Financial Management',
    programme: 'Accounting, Finance and Digital Marketing',
    duration: 'Professional Diploma — 1 Year (3 Semesters)',
    creditUnits: '66–72 CU (typical, per Credit Unit Policy)',
  },
];

// Faculty inbox — same shape as demoMessages, addressed to the Demo
// Lecturer instead of the Demo Student.
export const demoFacultyMessages = [
  {
    id: 'fm1',
    from: 'Academic Board Secretariat',
    subject: 'Semester 2 grade submission window opens Monday',
    date: '2026-08-02',
    unread: true,
    body: 'The grade submission window for Semester 2 continuous assessment opens Monday. Please submit gradebook entries for AISM-201 and AISM-220 through the Faculty Portal before the deadline in the academic calendar.',
  },
  {
    id: 'fm2',
    from: 'Demo Registrar',
    subject: 'Updated roster for AISM-220',
    date: '2026-07-29',
    unread: false,
    body: 'A short note to confirm the current roster for AISM-220 Comparative Religion. Let the Registrar’s Office know if any enrolment changes need reflecting before the next attendance cycle.',
  },
  {
    id: 'fm3',
    from: 'Course Coordinator',
    subject: 'Reminder: lesson content review for AISM-201',
    date: '2026-07-24',
    unread: false,
    body: 'Please review the published lesson content for AISM-201 Hadith Sciences ahead of the midterm review week, and flag any updates needed to the Course Coordinator.',
  },
];
