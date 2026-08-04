# Contributing

The day-to-day playbook for working in this codebase. Read `ARCHITECTURE.md` first if you haven't — this document assumes you know the shape of the repo.

## Before any change

Read the relevant guide:
- Touching the public site's visual design? `DESIGN_SYSTEM.md`.
- Writing or editing any copy? `CONTENT_STYLE_GUIDE.md` — the no-fabrication rule especially.
- Adding a portal screen? `src/app/portal/CONVENTIONS.md` (the exact required pattern) and `src/lib/services/README.md` (the data-fetching contract).
- Shipping anything? `DEPLOYMENT_GUIDE.md`.

## Adding a new public page

1. Add the HTML file under `public/legacy/<page-name>.html`. Copy the `:root` token block, header/footer markup, mobile-nav drawer, and `.reveal` scroll-animation script **verbatim** from an existing page (e.g. `governance.html`) — don't hand-retype this boilerplate; a hand-retyped copy has broken the hamburger menu before (see `RELEASE_REPORT.md`).
2. Add the bilingual `data-i18n` dictionary — every user-facing string needs both `en` and `ar` entries from the start. A page that ships with a language toggle that doesn't actually translate is a real, shipped bug (this happened on three pages this session and had to be fixed retroactively).
3. Add the rewrite in `next.config.js`'s `rewrites().beforeFiles` array: `{ source: '/your-page', destination: '/legacy/your-page.html' }`.
4. Add the URL to `public/sitemap.xml` if it's meant to be indexed (most pages should be). Add `<meta name="robots" content="noindex, nofollow">` on the page itself instead if it shouldn't be — and if you do that, **don't** also add it to the sitemap (a noindex'd URL submitted for indexing is a contradictory signal search engines flag).
5. Run the full pre-commit checklist in `DEPLOYMENT_GUIDE.md`.

## Adding a new portal screen

Follow `src/app/portal/CONVENTIONS.md` exactly — it has the literal file template. In brief:

1. Add the nav entry to the right role's array in `NAV_BY_ROLE` in `src/components/portal/PortalShell.jsx` — this is the single source of truth for the sidebar.
2. Create the two-file pair: `page.jsx` (Server Component, calls a service function, exports `metadata` with `robots: { index: false, follow: false }`) and `<Screen>View.jsx` (`'use client'`, the actual UI, receives data as props).
3. If the data you need doesn't have a matching function in `src/lib/services/<role>Service.js` yet, add one there — following that file's existing style (async, realistic parameter shape, a doc comment if the file's other functions have one). **Never** import `src/lib/portalDemoData.js` directly from a component.
4. Build the UI from `src/components/portal/ui.jsx`'s shared primitives (`Card`, `StatGrid`/`StatTile`, `Badge`, `DataTable`, `RecordGrid`, `EmptyState`) wherever they fit. Only build a new component under `src/components/portal/` for a genuinely novel interaction pattern.
5. Every mutation (a save/submit/update action) needs: a pending state (disable the control, show "Saving…"/"Submitting…" — don't leave a button silently clickable mid-request), a success confirmation announced via `aria-live`/`role="status"` (a screen-reader user needs to know something happened, not just see it), and honest copy if nothing actually persists yet (see `SettingsView.jsx` for the established pattern).
6. Run the full pre-commit checklist.

## Copy and translation changes

- Read `CONTENT_STYLE_GUIDE.md` before writing anything new — the no-fabrication rule, the terminology table, and the "would a prestigious global institution genuinely say this" test all apply.
- Any change to an `en` dictionary entry needs the matching `ar` entry updated too, in the same commit — not as a follow-up.
- Reuse established Arabic terminology for a concept that already has one elsewhere on the site (check `academic-structure.html`/`institute-professional-studies.html` for Schools, AIPS/PCPP, Credit Unit) rather than re-translating from scratch.

## Accessibility checklist for any new interactive UI

- Every form control has a real `<label>` (or `aria-label`) associated with it.
- Keyboard-only operable: can you complete the whole flow with Tab/Enter/Space alone, focus visible at every step?
- Multi-step flows (like the quiz-taking flow) must move focus to the new step's container on each transition — otherwise a keyboard/screen-reader user loses their place. This was a real bug found and fixed this session; the fix pattern (a focus ref, skipping the very first mount) is in `QuizRunner.jsx` if you need a reference.
- Dynamic confirmations (a save succeeded, a score appeared) need `aria-live`/`role="status"` — a visual-only confirmation is invisible to a screen-reader user.
- `prefers-reduced-motion: reduce` guards any transition/animation you add.

## Commit conventions

- Small, reviewable commits grouped by topic — not one giant commit for an unrelated batch of fixes.
- Message: a one-line summary, then (for anything non-trivial) a body explaining *why*, not just *what* — the diff already shows what changed.
- End every commit with:
  ```
  Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
  ```
  (or the equivalent attribution for whichever agent/person made the change, matching this project's established convention).
- Never `--amend` a commit that's already been pushed and might be in someone else's history — create a new commit instead.

## The pre-commit checklist (same one, every time)

```bash
npx next build                                                              # zero errors
npx next lint                                                               # zero errors (one expected warning, see DEPLOYMENT_GUIDE.md)
grep -rn "Al-Balagh" --exclude-dir=.git --exclude-dir=node_modules .        # must return nothing
```

Plus, situationally: tag-balance check on any HTML file touched, `en`/`ar` key-parity check on any translation dictionary touched.

## Where the standing project context lives

- `RELEASE_REPORT.md` — what's already been built, fixed, and verified. Check this before assuming something is broken or missing.
- `albalagh-lms-portal-scoping.md` — the LMS/portal backend's phased plan.
- `al-balagh-master-prompt.md` / `al-balagh-design-master-prompt.md` — the original content and design ground rules that shaped everything in this repo.
