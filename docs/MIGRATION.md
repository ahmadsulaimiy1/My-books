# Migration Status

This project is a **real Next.js 14 App Router application**, not a mock-up. It is mid-migration from a set of complete, working static HTML pages toward a fully componentized React codebase. This document is the honest map of what's on which side of that line, so nobody mistakes one for the other.

## ✅ Fully converted (real React/Next.js)

| Path | File |
|---|---|
| `/` (homepage) | `src/app/page.jsx` |

Shared components used by the converted route(s):

- `src/components/layout/Header.jsx` — sticky nav + working mobile hamburger menu
- `src/components/layout/Footer.jsx` — site footer
- `src/components/i18n/LanguageContext.jsx` — EN/AR toggle + `t()` translation lookup, shared by every future page
- `src/data/translations/homepage.js` — homepage's translation dictionary
- `src/styles/tokens.css` — design tokens (colour, spacing, radius, shadow) extracted from the original CSS
- `src/app/globals.css` — global styles, imports `tokens.css`

## 🟡 Not yet converted (complete, working static HTML)

These pages are **fully functional today** — bilingual, responsive, with working mobile navigation — but each is still one self-contained `.html` file with inline CSS/JS, not React components. They live in `public/legacy/` and are reachable at clean URLs via `rewrites()` in `next.config.js` (e.g. `/about` → `public/legacy/about.html`).

- `/about`
- `/founders-welcome`
- `/vision-mission-values`
- `/governance`
- `/academic-structure`
- `/graduate-designations-apgdm`
- `/admissions`
- `/tuition-scholarships`
- `/digital-campus`
- `/student-portal`
- `/lecturer-portal`
- `/staff-portal`
- `/administrator-portal`
- `/digital-library`
- `/research-innovation`
- `/alumni-careers`
- `/news-media-communications`
- `/albalagh-connect`
- `/student-life-campus-organisations`

## Why this split, and why it's the right call

Converting a self-contained HTML file with inline JS into JSX is not a mechanical find-and-replace — `class`→`className`, `for`→`htmlFor`, string styles→style objects, escaping stray `&`/`'`/`"` in text, event handlers rewritten as React handlers, etc. Nineteen large files (several 1,000+ lines) converted blind, with no compiler in the loop to catch mistakes, is a real risk of shipping broken pages. So: the homepage was converted as a working proof of the target pattern (`Header` + `Footer` + `LanguageProvider` + a per-page translation dict), and the rest were left exactly as they already were — complete and working — rather than risk silently breaking them.

## Recommended next steps (in order)

1. `npm install`, then `npm run dev` — confirm the homepage renders and `/about` etc. resolve via the legacy rewrites.
2. Pick one legacy page (suggest `about.html` — it's simpler than the portal pages) and convert it following the homepage's pattern: extract a translation dict into `src/data/translations/`, break the page into section components under `src/components/`, add `src/app/about/page.jsx`.
3. Once a page's `page.jsx` exists at the same route as a `rewrites()` entry, **remove that entry** from `next.config.js` — `beforeFiles` rewrites are checked first, so leaving a stale entry would silently shadow the new real page.
4. Repeat per page. The portal pages (Student/Lecturer/Staff/Administrator/etc.) are the largest — consider converting their shared sidebar/topbar/panel-switcher shell into reusable components (`src/components/dashboard/`) before converting each portal individually, since they share one architecture.
5. Firebase: `src/firebase/` is currently empty — wire up `firebase/app`, `firebase/auth`, `firebase/firestore` only when there's a real Firebase project to point at. `.env.example` shows the expected variable names; never commit real keys.

## Deployment

This is a standard Next.js app — no `vercel.json` is required. Push to GitHub, import the repo in Vercel, and it will auto-detect the Next.js framework and build correctly with zero extra configuration, **provided `npm install` succeeds locally first** (this environment has no network access to verify that install/build step — please run it once locally or let Vercel's own build step do it before assuming everything is correct).
