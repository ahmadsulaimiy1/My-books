# Firebase Integration Guide

How to turn the portal preview into a real, working backend. This is the guide `src/lib/services/*.js` was built for — every function in that directory is already shaped for this.

## What's already prepared, ahead of a real project

The following exist in the repo **now**, written and reviewed before any Firebase project was available, so the data model and its access control were designed together rather than bolted on after collections already existed. None of these are wired into the running app yet — nothing imports `src/lib/firebase.js`, nothing has been deployed:

- **`DATA_MODEL.md`** — the canonical collection-by-collection data model (read this before `firestore.rules`, it explains the *why* behind every rule).
- **`firestore.rules`** / **`storage.rules`** — the Security Rules enforcing that model. Not yet deployed to anything (there's no project to deploy them to) — review and adjust before the first `firebase deploy --only firestore:rules,storage`.
- **`firebase.json`** / **`firestore.indexes.json`** — project config and the composite indexes the data model's common queries will need.
- **`.firebaserc.example`** — copy to `.firebaserc` and fill in your real project ID once one exists (`.firebaserc` is gitignored, since project association is developer/environment-specific).
- **`src/lib/firebase.js`** — the client SDK init, reading config from `NEXT_PUBLIC_FIREBASE_*` env vars (see `.env.example`). Throws a clear, actionable error if called before those env vars exist, rather than silently failing — this is intentional, not a bug to fix.

## Before you start

You need a real Firebase project (free Spark tier is enough to start). Create one at [console.firebase.google.com](https://console.firebase.google.com), register a web app, and you'll get a config object (`apiKey`, `authDomain`, `projectId`, etc.). That config is safe to be public/client-side — it identifies your project, it doesn't authorise anything by itself. **Security Rules are what actually protect data**, not the config object — which is why `firestore.rules`/`storage.rules` above were written before any project existed, not as an afterthought.

`firebase` (10.12.4) is already a `package.json` dependency, unused until `src/lib/firebase.js` is actually imported somewhere.

Once you have a project: fill in `.env.local` (copy from `.env.example`) with the real config, copy `.firebaserc.example` to `.firebaserc` with the real project ID, then `firebase deploy --only firestore:rules,firestore:indexes,storage` to push the prepared rules and indexes before writing any application code against them.

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

## Data model

Superseded by the full, standalone **`DATA_MODEL.md`** — read that document for the real collection-by-collection shape, ownership, and lifecycle (it supersedes the earlier sketch that used to live in this section; keeping one canonical copy rather than two that could drift, per the documentation-freshness rule in `CONTRIBUTING.md`).

Map the real model onto the existing service function signatures, not the other way around — e.g. `studentService.getCourses({ studentId })` becomes a Firestore query filtering `enrolments` by `studentId` and joining to `courses`, but its return shape should still match what `demoCourses` currently returns (an array of `{ id, title, credits, semester, status, grade }`), so nothing downstream in `CoursesView.jsx` needs to change.

## Phased rollout — each phase is a real, shippable slice

**Phase 0 — Foundations.** Wire the Firebase SDK into the app (a `src/lib/firebase.js` client init), write the Security Rules skeleton, implement `authService.signIn`/`signOut`/`onAuthStateChange` for real (they currently throw a clear "not implemented" error — replace the throw with the real call), and add a route-protection pattern (redirect to a real sign-in if `getCurrentUser()` fails). No visible feature change yet, but everything after depends on this.

**Phase 1 — Student Portal reads.** Replace the bodies of `studentService.js`'s read functions (`getStudentProfile`, `getCourses`, `getAssignments`, etc.) with real Firestore queries, scoped by the authenticated user's `uid`. This alone replaces the current preview with something real. Good place to pause and verify before continuing.

**Phase 2 — Faculty Portal reads**, same pattern against `facultyService.js`.

**Phase 3 — Submissions, grading, and quiz-taking.** Wire `studentService.submitQuiz` to write to Firestore and grade against a server-held (Cloud Function or Firestore-rules-protected) answer key — **do not** ship the answer key to the client before submission; this exact mistake was found and fixed in the mock (`studentService.getQuiz` now strips `correctIndex` before returning) and the real implementation must preserve that boundary. Wire `facultyService.markAttendance` and assignment submission (Firebase Storage) here too.

**Phase 4 — Admin.** `adminService.js`'s user/role management (`getUsers`, `updateUserRole`) and programme/course management.

**Phase 5 — Finance.** Hard external dependency: a real payment gateway account (Paystack or Flutterwave are the standard choices for Naira payments) with real merchant credentials. Recordkeeping (`staffService.getLedger`) can be wired to Firestore without a live gateway; **taking real payment cannot be faked or half-built** — don't wire a payment-looking form to nothing.

**Phase 6 — Examinations & Library.** Lowest priority; the current preview pages already describe these honestly.

## Security Rules — the part that actually matters

Already written: `firestore.rules` and `storage.rules`, in full, matching the role model established in `DATA_MODEL.md` (a student can read their own `enrolments`/`submissions`/`results`, never another student's; only a Cloud Function via the Admin SDK ever sets `users/{uid}.role`; `payments` are never client-writable, only a gateway webhook handler; quiz answer keys are unreadable to a `student`-role token at the rules level, not just omitted from a mock's response). Review them against your actual project before deploying — they're a starting point written carefully, not a substitute for your own review.

Test with the Firebase emulator suite (`firebase emulators:start`, config already in `firebase.json`) before deploying to a real project — a portal with plausible-looking but unenforced access control is a worse security posture than the current honest, backend-less preview.

## What does not change

- The `page.jsx`/`View.jsx` split, `PortalShell`, and every shared `ui.jsx` component — none of this needs to know Firebase exists.
- `PreviewBanner` should be **removed** from `PortalShell` once Phase 1 genuinely has real data flowing — leaving it up after the backend is real would itself become a false statement.
- The demo/mock data in `src/lib/portalDemoData.js` can stay in the repo as fixture data for tests, but nothing in `src/app/` should still import it once its role's service functions are migrated.
