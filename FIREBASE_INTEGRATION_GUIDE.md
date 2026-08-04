# Firebase Integration Guide

How to turn the portal preview into a real, working backend. This is the guide `src/lib/services/*.js` was built for — every function in that directory is already shaped for this.

## Before you start

You need a real Firebase project (free Spark tier is enough to start). Create one at [console.firebase.google.com](https://console.firebase.google.com), register a web app, and you'll get a config object (`apiKey`, `authDomain`, `projectId`, etc.). That config is safe to be public/client-side — it identifies your project, it doesn't authorise anything by itself. **Security Rules are what actually protect data**, not the config object. Get the rules right before writing a line of the actual integration; see "Security Rules" below before "Phase 0."

`firebase` (10.12.4) is already a `package.json` dependency, unused — added in anticipation of exactly this work.

## The contract you're implementing against

Read `src/lib/services/README.md` first — the rules it states are the ones every `page.jsx` in `src/app/portal/**` was written to. In short:

1. Every service function is already `async` and already awaited by its caller (`page.jsx`, a Server Component). **You are changing function bodies, not call sites.** If you find yourself needing to touch a `page.jsx` or a `*View.jsx` to wire in Firebase, something has gone wrong with the plan — the abstraction boundary exists specifically so that doesn't happen.
2. Function signatures already describe the real query shape (e.g. `getCourses({ studentId })`), even though the mock body ignores the parameter today. Start using the parameter for real instead of ignoring it.
3. Mutation functions (`submitQuiz`, `markAttendance`, `updateUserRole`, `updateSettings`) already return a realistic response shape (`{ success, ... }`) — match that shape from the real Firestore write, don't change it out from under the calling component.

## Recommended stack

- **Firebase Authentication** — email/password to start; add providers later if needed.
- **Cloud Firestore** — the database.
- **Firebase Storage** — file uploads (assignment submissions, future profile photos).
- **Firebase Security Rules** — role-based read/write access enforced server-side. This is the part that actually matters; a portal with only client-side role checks is worse than no portal.
- **Vercel stays the host.** Firebase is called from the existing Next.js app for auth/data/storage; nothing about deployment changes (see `DEPLOYMENT_GUIDE.md`).

## Data model (Firestore, sketch — same one drafted in `albalagh-lms-portal-scoping.md`)

```
users/{uid}          — profile, role, programme (student) / department (staff/faculty)
programmes/{id}       — the 8 published Professional Diploma programmes
courses/{id}          — courses within a programme; credit units per the Credit Unit Policy
enrolments/{id}        — student ↔ programme ↔ intake, status
assignments/{id}       — set by a faculty member for a course
submissions/{id}       — student ↔ assignment, file ref, grade, feedback
grades/{id}            — per-course result
announcements/{id}      — role- or programme-scoped notices
payments/{id}           — tuition/fee ledger entries (Phase 5, see below)
library_items/{id}       — a real digital catalogue
```

Map this onto the existing service function signatures, not the other way around — e.g. `studentService.getCourses({ studentId })` becomes a Firestore query filtering `enrolments` by `studentId` and joining to `courses`, but its return shape should still match what `demoCourses` currently returns (an array of `{ id, title, credits, semester, status, grade }`), so nothing downstream in `CoursesView.jsx` needs to change.

## Phased rollout — each phase is a real, shippable slice

**Phase 0 — Foundations.** Wire the Firebase SDK into the app (a `src/lib/firebase.js` client init), write the Security Rules skeleton, implement `authService.signIn`/`signOut`/`onAuthStateChange` for real (they currently throw a clear "not implemented" error — replace the throw with the real call), and add a route-protection pattern (redirect to a real sign-in if `getCurrentUser()` fails). No visible feature change yet, but everything after depends on this.

**Phase 1 — Student Portal reads.** Replace the bodies of `studentService.js`'s read functions (`getStudentProfile`, `getCourses`, `getAssignments`, etc.) with real Firestore queries, scoped by the authenticated user's `uid`. This alone replaces the current preview with something real. Good place to pause and verify before continuing.

**Phase 2 — Faculty Portal reads**, same pattern against `facultyService.js`.

**Phase 3 — Submissions, grading, and quiz-taking.** Wire `studentService.submitQuiz` to write to Firestore and grade against a server-held (Cloud Function or Firestore-rules-protected) answer key — **do not** ship the answer key to the client before submission; this exact mistake was found and fixed in the mock (`studentService.getQuiz` now strips `correctIndex` before returning) and the real implementation must preserve that boundary. Wire `facultyService.markAttendance` and assignment submission (Firebase Storage) here too.

**Phase 4 — Admin.** `adminService.js`'s user/role management (`getUsers`, `updateUserRole`) and programme/course management.

**Phase 5 — Finance.** Hard external dependency: a real payment gateway account (Paystack or Flutterwave are the standard choices for Naira payments) with real merchant credentials. Recordkeeping (`staffService.getLedger`) can be wired to Firestore without a live gateway; **taking real payment cannot be faked or half-built** — don't wire a payment-looking form to nothing.

**Phase 6 — Examinations & Library.** Lowest priority; the current preview pages already describe these honestly.

## Security Rules — the part that actually matters

Every collection needs rules matching the role model already established in the service layer:

- A student can read their own `enrolments`/`submissions`/`grades`, never another student's.
- A faculty member can read/write `assignments`/`grades` only for courses in their own `coursesTaught`.
- Only `admin`-role users can write `users/{uid}.role`.
- `payments` writes should go through a Cloud Function (server-side), never a direct client write, once Phase 5 exists.

Write the rules before wiring the corresponding service function, and test them (the Firebase emulator suite is the right tool) before deploying — a portal with plausible-looking but unenforced access control is a worse security posture than the current honest, backend-less preview.

## What does not change

- The `page.jsx`/`View.jsx` split, `PortalShell`, and every shared `ui.jsx` component — none of this needs to know Firebase exists.
- `PreviewBanner` should be **removed** from `PortalShell` once Phase 1 genuinely has real data flowing — leaving it up after the backend is real would itself become a false statement.
- The demo/mock data in `src/lib/portalDemoData.js` can stay in the repo as fixture data for tests, but nothing in `src/app/` should still import it once its role's service functions are migrated.
