# Portal build conventions

Read this before adding any screen under `src/app/portal/**`. It exists so five different build passes (Student, Faculty, Staff, Admin, Applicant/Parent) end up looking like one product, not five.

## File pattern (required — avoids a real Next.js App Router gotcha)

A route's `page.jsx` must stay a **Server Component** so it can export `metadata`. But `PortalShell`/`ui.jsx` use `styled-jsx`, which only works in Client Components. So every screen is two files:

```
src/app/portal/<role>/<screen>/page.jsx        — server component, just metadata + renders the view
src/app/portal/<role>/<screen>/<Screen>View.jsx — 'use client', the actual UI
```

`page.jsx` template:

```jsx
import <Screen>View from './<Screen>View';

export const metadata = {
  title: '<Screen title> — Preview | Albalagh Global',
  description: '...',
  robots: { index: false, follow: false }, // every portal page — these are previews, keep out of search results
};

export default function <Screen>Page() {
  return <<Screen>View />;
}
```

## Shared components — use these, don't rebuild them

- `@/components/portal/PortalShell` — wraps every screen. Handles the sidebar nav, topbar, and (critically) always renders `PreviewBanner`. Pass `role`, `active` (must match a `key` in `PortalShell.jsx`'s `NAV_BY_ROLE[role]`), and `title`.
- `@/components/portal/ui` — `Card`, `StatGrid`/`StatTile`, `Badge` (tones: neutral/gold/success/alert/info), `DataTable` (pass `columns`+`rows`, handles its own empty state), `EmptyState`.

If a screen genuinely needs a component these don't cover (e.g. a course player, a quiz-taking UI, a calendar grid), build it as a new file under `src/components/portal/`, matching the same token-based styling approach — not a one-off inline style in the page.

## Adding a new route

1. Add the nav entry to the right array in `NAV_BY_ROLE` inside `src/components/portal/PortalShell.jsx` — this is the single source of truth for the sidebar; don't hand-roll nav links elsewhere.
2. Create the two-file page/view pair above.

## Demo data

Lives in `@/lib/portalDemoData`. Extend it there rather than inlining new fake records in a page component, so it stays one auditable source. Rules (already stated at the top of that file, repeated because they matter): real programme/course/policy facts only (must match what's already published on the public site), fictional people must read as obviously placeholder (no realistic full identity), and every screen must sit inside `PortalShell` so the preview banner is unmissable.

## Bilingual

The public site is fully bilingual EN/AR via `LanguageProvider`/`useLanguage`. The portal preview is English-first for now — this is a known, deliberate scope reduction (flag it in your summary if you touch this decision, don't silently change it). Do not remove or fight the `dir="ltr"`/RTL plumbing already in the root layout; just don't block on full AR portal translation to ship a screen.

## Build check

Always run `npx next build` before committing — App Router server/client mistakes fail the build immediately and loudly (see the file-pattern section above for the specific mistake this is guarding against).
