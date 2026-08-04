# Portal service layer

Every portal screen reads data through a function in this directory, never by
importing `portalDemoData.js` directly. That's the whole point: swapping the
mock backend for real Firebase later means rewriting the *inside* of these
functions, not touching a single page/component.

## Rules

1. **Every exported function is `async`**, even though today it just returns
   a plain object/array synchronously wrapped in a resolved Promise. This
   isn't decorative — a real Firestore read is asynchronous, and Server
   Components (`page.jsx` files) already `await` data before rendering, so
   making the mock async now means zero call-site changes when the real
   implementation lands.
2. **Function signatures describe the real query, not the mock's shortcuts.**
   e.g. `getCourses({ studentId })` not `getCourses()` — even though the mock
   ignores `studentId` and always returns the one demo student's courses,
   the shape is what a real multi-student Firestore query would need.
3. **No component ever imports `portalDemoData.js` directly.** If you need a
   new piece of demo data, add it to `portalDemoData.js` as before, then
   expose it through a service function here.
4. **Where a service function will eventually *write* data** (submit a quiz,
   mark attendance, send a message), the mock still validates its inputs and
   returns a realistic response shape (e.g. `{ success: true, id }`) — it
   should behave like a real API call that happens to always succeed against
   in-memory data, not a no-op stub.
5. **Server Components fetch, Client Components render.** The established
   pattern (see `src/app/portal/CONVENTIONS.md`) is `page.jsx` (server) calls
   the service and passes the result as props to `<XView data={...} />`
   (client, `'use client'`, owns interactivity/local state). Don't fetch
   inside a Client Component with `useEffect` — there's no reason to here,
   and it would create a loading-flash the Server Component pattern avoids.

## Files

- `authService.js` — `getCurrentUser(role)`, plus documented (unimplemented)
  `signIn`/`signOut`/`onAuthStateChange` stubs — there's no real
  authentication yet (see `albalagh-lms-portal-scoping.md` Phase 0), portal
  routes are reached by direct navigation per role, not a login flow.
- `studentService.js`, `facultyService.js`, `staffService.js`,
  `adminService.js`, `applicantService.js`, `parentService.js` — one per
  portal role, covering every screen that role has.
- `libraryService.js` — shared across roles.
- `notificationService.js` — notification reads. Only the Student Portal
  has a notifications screen today, but it lives as its own service (not
  folded into `studentService.js`) because notifications are a cross-role
  concern other roles will need the same shape for once they grow
  notification screens.

## When Firebase actually lands

Replace each function body with the equivalent Firebase Auth / Firestore /
Storage call. Keep the signature and return shape identical wherever
possible — that's the contract every `page.jsx` in `src/app/portal/**` was
written against.
