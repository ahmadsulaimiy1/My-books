# Canonical Data Model

Written before any Firestore collection is created, per the Phase 0 directive: "avoid creating isolated collections simply because a screen needs one." This is the single source of truth for what the backend's shape will be. If a future screen needs data this model doesn't cover, extend this document and `firestore.rules` together — don't add a collection ad hoc.

Firestore is a document database, not relational — "relationships" below are references (a field holding another document's ID), not foreign keys. Every collection lists: **shape**, **who can read**, **who can write**, and **lifecycle** notes where the data isn't just created-and-left-alone.

## Identity

### `users/{uid}`
The root identity record. `uid` matches the Firebase Auth UID.

```
uid, email, displayName, phone,
role: 'student' | 'faculty' | 'staff' | 'admin' | 'applicant' | 'parent',
status: 'active' | 'suspended',
createdAt, updatedAt
```

**Read:** the user themselves; `admin` role; `staff` role (limited fields — see Security Rules). **Write:** the user can update their own `displayName`/`phone` only. **`role` is never client-writable, under any circumstances** — it's set by a Cloud Function during account creation/role transition (applicant → student, a promotion to staff, etc.) using the Admin SDK, and mirrored into the user's Auth **custom claims** so Security Rules and any server-side check can trust `request.auth.token.role` without an extra document read. This is the control that prevents a user from gaining another role's access by manipulating frontend state — the frontend never decides a role, it only reflects what the token already says.

### `studentProfiles/{uid}`, `applicantProfiles/{uid}`, `staffProfiles/{uid}`
One-to-one extensions of `users/{uid}` for role-specific fields, keyed by the same `uid`. Kept separate from `users` so a role transition (see Lifecycle below) is "create the new profile doc, don't rewrite the identity doc."

```
studentProfiles/{uid}:
  studentId (ALB-YYYY-NNNN), programmeId, schoolId, sessionId (intake),
  status: 'active' | 'on-leave' | 'graduated' | 'withdrawn',
  creditsCompleted, guardianUid (→ users/{parentUid}, optional), dateOfBirth

applicantProfiles/{uid}:
  applicationId, programmeChoiceId, route, stage, submittedAt,
  assessmentDate, decision: 'pending' | 'offered' | 'rejected' | null,
  documentRefs: [Storage paths]

staffProfiles/{uid}:
  staffId, department, jobTitle,
  coursesTaught: [→ courses/{id}]   // faculty only
  office                             // staff/admin only
```

**Read:** the user themselves; `staff`/`admin` for `studentProfiles`/`applicantProfiles`; `admin` for `staffProfiles`. A parent (`guardianUid`) can read their linked student's `studentProfiles` doc — nothing else. **Write:** field-restricted (a student cannot edit their own `studentId` or `status`; only `staff`/`admin` or a Cloud Function can).

## Academic structure

### `schools/{schoolId}`, `programmes/{programmeId}`
The 4 Schools and their programmes, matching the public site exactly (`academic-structure.html` is the source of truth for names — don't let these drift, see `CONTENT_STYLE_GUIDE.md`).

```
programmes/{id}: name, schoolId, creditUnitsRequired (e.g. "66-72"), durationMonths
```

**Read:** public (these mirror published facts, no reason to restrict). **Write:** `admin` only.

### `courses/{courseId}`
```
code (e.g. "AISM-201"), title, programmeId, credits, semester
```
**Read:** public. **Write:** `admin`.

### `academicSessions/{sessionId}`
```
name (e.g. "2026/2027"), startDate, endDate, currentSemester
```
One document represents the institution's current academic calendar state — the thing `demoStudent.intake` currently hardcodes as a string ("September 2026 Intake") becomes a real reference to this. **Read:** public. **Write:** `admin`.

### `classes/{classId}`
A specific *offering* of a course within a session — the distinction the directive draws between "course" (the catalogue entry) and "class" (this semester's actual running instance, with a real timetable and a real lecturer).

```
courseId, sessionId, facultyUid, schedule: [{ day, time, mode: 'live'|'recorded' }]
```
**Read:** enrolled students (via `enrolments`) and the assigned `facultyUid`; `staff`/`admin`. **Write:** `admin`; `facultyUid` can update `schedule` for their own class only.

## Students moving through the system

### `enrolments/{enrolmentId}`
```
studentUid, classId, programmeId, sessionId,
status: 'enrolled' | 'completed' | 'withdrawn',
enrolledAt
```
**Read:** the enrolled student; the class's `facultyUid`; `staff`/`admin`. **Write:** `admin`/`staff` create it (as part of registration, see Lifecycle); a student cannot self-enrol by writing this collection directly — enrolment is a consequence of a registration workflow, not a form submission straight to Firestore.

### `attendance/{attendanceId}`
```
classId, studentUid, sessionDate, status: 'present'|'absent'|'excused',
markedByUid, markedAt
```
**Read:** the student (their own record); `facultyUid` of the class; `staff`/`admin`. **Write:** only the class's `facultyUid` can create/update records for their own class, and only within a reasonable window after `sessionDate` (enforce via a rules-level timestamp check, e.g. ≤72 hours) — a late "correction" past that window should go through an audited edit (see Auditability), not a silent rewrite.

### `assignments/{assignmentId}` → `submissions/{submissionId}`
```
assignments/{id}: classId, title, description, dueDate, createdByUid, maxScore
submissions/{id}: assignmentId, studentUid, fileRef, submittedAt, score, feedback, gradedByUid, gradedAt
```
**Read (assignments):** enrolled students in the class, the `facultyUid`. **Read (submissions):** the submitting student (their own), the `facultyUid`. **Write:** a student can create their own `submission` (once, before `dueDate` unless an extension flag is set) but can **never** write `score`/`feedback`/`gradedByUid` — those fields are faculty/admin-only, enforced at the rules level per-field, not just per-document.

### `quizzes/{quizId}` and `quizzes/{quizId}/questions/{questionId}` (subcollection)
**This is the permanent engineering principle from the V1.0 review, now encoded as a rule, not just a convention:** the `questions` subcollection's `correctIndex` field (or equivalent) must **never** be readable by a `student`-role token, at the Security Rules level — not just omitted by the current mock's response shape. `studentService.getQuiz()`'s current behaviour (strip the answer key before it reaches the client) becomes the *only* way a student's read is even allowed to succeed; grading happens in a Cloud Function that reads the real subcollection with Admin SDK privileges the client never has.

```
quizAttempts/{attemptId}: quizId, studentUid, answers, score, submittedAt
```
`score` is written only by the grading Cloud Function, never by the client — matches `submitQuiz`'s existing contract exactly (see `FIREBASE_INTEGRATION_GUIDE.md` Phase 3).

### `results/{resultId}`
```
studentUid, courseId, sessionId, grade, gpaPoints,
confirmedByUid, confirmedAt   // null until the Academic Board approves
```
**Read:** the student (their own, only once `confirmedAt` is set — a provisional/unconfirmed grade should not be visible to the student, matching the real institutional process the site already describes on `governance.html`); `facultyUid` who taught the course; `staff`/`admin`. **Write:** `faculty` can set `grade` (unconfirmed); only `staff`/`admin` (acting for the Academic Board) can set `confirmedAt`, and once set, the document should become immutable except via an explicitly audited correction (see Auditability) — a confirmed result silently changing is exactly the kind of thing that must never happen invisibly.

## Finance

### `feeSchedule/{feeTypeId}`
**The single canonical source of truth for every fee amount in the system**, per the directive's explicit requirement ("never allow contradictory fee figures to appear in different parts of the system"). This is what both a future CMS-driven tuition page *and* the portal's finance screens read from — there is exactly one place a fee amount is ever set.

```
key (e.g. 'aips', 'application', 'registration'),
label, amount: number | null,   // null = genuinely TBC, matches the current honest convention
currency: 'NGN',
appliesTo: 'all' | programmeId,
effectiveFrom
```
**Read:** public (fees are published information). **Write:** `admin` only, and every write should be audit-logged (a fee change is exactly the kind of consequential operation Auditability covers).

### `invoices/{invoiceId}` → `payments/{paymentId}`
```
invoices/{id}: studentUid, feeTypeId, amount (copied from feeSchedule at issue time,
  so a later fee-schedule change doesn't retroactively alter an already-issued invoice),
  status: 'pending'|'paid'|'overdue'|'refunded', dueDate, issuedAt

payments/{id}: invoiceId, studentUid, amount, gatewayReference, status, paidAt
```
**Read:** the student (their own); `guardianUid` (a parent can see their linked student's invoices, not payment method details); `staff`/`admin`. **Write:** `invoices` created by `staff`/`admin` or a registration Cloud Function; `payments` are written **only** by a server-side webhook handler receiving a confirmed callback from the payment gateway (Paystack/Flutterwave) — never a direct client write, since a client-writable "I paid" field is not a real payment system, it's a trust exploit waiting to happen.

## Communication

### `announcements/{id}`
```
title, body, audience: { role? , programmeId?, classId? }, createdByUid, createdAt
```
**Read:** any user matching `audience`. **Write:** `faculty` (scoped to their own classes), `staff`/`admin` (broader scopes).

### `messageThreads/{threadId}/messages/{messageId}`
```
threadId doc: participantUids: [uid, uid, ...]
messages/{id}: senderUid, body, sentAt, readBy: [uid, ...]
```
**Read/write:** only `participantUids`.

## Library

### `libraryItems/{id}`
```
title, type: 'E-book'|'PDF'|..., courseId, fileRef
```
**Read:** public or enrolled-only depending on licensing (per-item flag, default enrolled-only). **Write:** `staff`/`admin`.

## Auditability

### `auditLog/{id}`
```
action: 'admission_decision' | 'role_change' | 'grade_change' | 'attendance_change' |
        'financial_transaction' | 'refund' | 'profile_change',
actorUid, targetRef (the affected document's path), before, after, timestamp
```
**Read:** `admin` only. **Write:** never from the client — every write to this collection comes from the same Cloud Function that performs the consequential operation it's logging, as part of one atomic transaction. **No update or delete is ever permitted on this collection, by anyone, including `admin`** — an audit log that can be edited isn't one.

## Suggested composite indexes (define once the project exists)

- `enrolments`: `studentUid ASC, status ASC`
- `attendance`: `classId ASC, sessionDate DESC`
- `results`: `studentUid ASC, sessionId DESC`
- `invoices`: `studentUid ASC, status ASC`
- `submissions`: `assignmentId ASC, studentUid ASC`

## Lifecycle: applicant → student (the admissions workflow, data side)

Matches the 13-step journey already published on `admissions.html` and the workflow specified for Phase Admissions:

1. `applicantProfiles/{uid}` created when a `users/{uid}` doc with `role: 'applicant'` is created (real signup, Phase 0 auth).
2. Application data collected into that same document as the applicant progresses (personal info, academic background, programme choice) — one document, updated in place, not a new collection per step.
3. Document uploads go to Firebase Storage under `applicants/{uid}/...`, referenced by `documentRefs`.
4. `stage` transitions (`Application Review` → `Entrance Assessment` → `Admission Decision`) are written by `staff`/`admin` only, each transition audit-logged.
5. On `decision: 'offered'` and the applicant accepting: a Cloud Function performs the **role transition** atomically — creates `studentProfiles/{uid}`, updates `users/{uid}.role` to `'student'` (and the Auth custom claim), creates the first `enrolments` record, and archives (not deletes) the `applicantProfiles` doc for institutional record-keeping. This is the one place "a user gains a new role" happens anywhere in the system, and it never happens from client code.

## Environment separation

Development and staging, where used, should be **separate Firebase projects**, not separate collections in one project — Firestore Security Rules are project-wide, and mixing real/test data in one project risks a test write leaking into what looks like production data. `.firebaserc` supports multiple named project aliases (`default`, `staging`) for exactly this; see `firebase.json`/`.firebaserc` in the repo root.
