# Albalagh Global — LMS & Campus Portal: Scoping Plan

This is a planning document, not a build. Nothing here is implemented yet. Read this, then decide how far to go — see "What I need from you" at the end.

## Where the project actually stands

Today, `student-portal.html`, `lecturer-portal.html`, `staff-portal.html`, and `administrator-portal.html` are honest static marketing pages — they describe what each portal will eventually contain, with no login, no data, no backend. `firebase` (10.12.4) is already a `package.json` dependency but is not imported or used anywhere in `src/` — it looks like it was added in anticipation of exactly this build, then never wired up.

Building the real thing — authentication, role-based dashboards, a gradebook, a finance ledger, an examinations engine, a library catalogue, all "feeling like one platform" — is a genuine multi-phase software project. It is not something a design pass can absorb, and it is not something that should be built in one uncontrolled sweep: the risk of ending up with a half-wired, insecure, or fake-looking "portal" is much worse for trust than the current honest preview pages.

## Recommended stack

- **Firebase Authentication** — email/password + optional Google sign-in, since it's already a dependency and needs zero new infra decisions.
- **Cloud Firestore** — the database (documents/collections below).
- **Firebase Storage** — file uploads (assignment submissions, ID documents at enrolment, profile photos).
- **Firebase Security Rules** — role-based read/write access enforced server-side, not just hidden in the UI (this is the single most important thing to get right — a portal with client-side-only role checks is worse than no portal).
- Hosting stays on **Vercel** as it is now; Firebase is used purely for auth/data/storage, called from the existing Next.js app.

## Roles

`student`, `lecturer`, `staff` (registrar/bursar/librarian-type roles), `admin`. A user document carries exactly one primary role; admin can grant/revoke.

## Data model (Firestore, sketch)

```
users/{uid}                 — profile, role, programme (if student), department (if staff/lecturer)
programmes/{id}              — the 8 existing Professional Diploma programmes
courses/{id}                 — courses within a programme, credit units (ties into the Credit Unit Policy already on the site)
enrolments/{id}               — student ↔ programme ↔ intake, status
assignments/{id}              — set by a lecturer for a course
submissions/{id}              — student ↔ assignment, file ref, grade, feedback
grades/{id}                   — per-course result, feeds the Official Statement of Results already described in the AIPS/APGDM pages
announcements/{id}             — role- or programme-scoped notices
payments/{id}                 — tuition/fee ledger entries (see Finance note below)
library_items/{id}             — a real digital catalogue, or a curated external-link list to start
```

## Phased build (each phase is a real, shippable, reviewable slice)

**Phase 0 — Foundations.** Firebase project wired into the Next.js app, security rules skeleton, auth (sign up/sign in/sign out), one protected route pattern. No visible feature yet, but everything after depends on this being solid.

**Phase 1 — Student Portal MVP.** A logged-in student sees: their programme, enrolment status, course list, and any announcements. Read-only. This alone replaces the current preview page with something real, and is a sensible place to pause and evaluate before going further.

**Phase 2 — Lecturer Portal MVP.** A lecturer sees their assigned courses and enrolled students, can post announcements and assignments.

**Phase 3 — Submissions & Grading.** Students submit work (Firebase Storage), lecturers grade it, grades roll up into a results view — this is where the Credit Unit Policy and the AIPS "Official Statement of Results" language on the live site start being backed by real data instead of description.

**Phase 4 — Admin Portal.** User/role management, programme/course management, oversight views.

**Phase 5 — Finance.** This phase has a hard external dependency: a real payment gateway account (Paystack or Flutterwave are the standard choices for Naira-denominated payments) with real merchant credentials from you. I cannot create or fake this — without it, a "finance module" is either non-functional or misleading. Recordkeeping (a ledger view of fees owed/paid) can be built without a live gateway; taking real payment cannot.

**Phase 6 — Examinations & Library.** A structured exam/quiz engine and a real digital library catalogue. Lowest priority — the current preview pages already describe these accurately and nothing is broken by them staying descriptive for now.

## What I need from you to start Phase 0

1. **A Firebase project.** Create one at [console.firebase.google.com](https://console.firebase.google.com) (the free Spark plan covers this comfortably at MVP scale) and share the web app config (the `apiKey`/`authDomain`/`projectId`/etc. block Firebase gives you when you register a web app — this is safe to be public, it's designed to sit in client-side code; the security rules, not the config, are what actually protects data).
2. **Confirmation of scope** — start at Phase 0 → 1 and pause there for review, or a different entry point.
3. For Phase 5 later: which payment gateway you'd set an account up with, when we get there.

## What stays out of scope regardless

No fabricated "live" data, ever — an empty portal with zero enrolled students should visibly say so, not be padded with placeholder names. No claiming compliance/security certifications this hasn't earned. No building Phase 5's payment flow without real, working merchant credentials.
