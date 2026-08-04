# Architecture

How Albalagh Global's codebase is put together, and why. Read this before making a structural change — most of the decisions here were made deliberately, in response to a real constraint, not by default.

## The two halves of the site

The repository serves two genuinely different things through one Next.js app:

1. **The public marketing site** — bilingual (EN/AR), mostly static content, SEO-critical, must work with zero JavaScript failures for a search crawler or a slow connection.
2. **The portal preview** — a real, interactive React application (dashboards, a course player, a quiz engine, forms) with no backend yet.

They're built differently on purpose. Trying to force them into one pattern would have made both worse.

## Public site: the static-HTML-behind-a-rewrite bridge

Only the homepage (`/`, `src/app/page.jsx`) and the 404 page are real, componentised Next.js routes. Every other public page — About, Governance, Admissions, Tuition, and 15 more — is a **complete, self-contained static HTML file** under `public/legacy/*.html`: its own `<style>` block with a duplicated copy of the design tokens, its own inline JavaScript (mobile nav, language toggle, scroll-reveal, FAQ accordions), its own `en`/`ar` translation dictionary.

`next.config.js`'s `rewrites()` maps each one to a clean URL:

```js
{ source: '/about', destination: '/legacy/about.html' }
```

**Why this exists, and why it hasn't been "fixed":** these pages were built this way originally, and converting all 19 to real React components is a real, multi-day project of its own — not a quick refactor, because each one carries real content, working bilingual JS, and its own careful accessibility/SEO markup that would all need to be re-verified after conversion. The rewrite bridge means `/about` genuinely serves `public/legacy/about.html` as a static file — nothing is faked or hidden, it's an honest interim architecture, not a hack pretending to be something else. `beforeFiles` is used specifically so that if a page is later converted to a real `src/app/about/page.jsx`, Next's own routing takes over automatically without touching the rewrite config.

**Consequence you need to know:** because each legacy page duplicates its own `:root` CSS block, a design-token change (e.g. the `--gold-ink` accessibility fix) has to be applied to every file's `:root`, not just `src/styles/tokens.css`. This is real, known friction — see `DESIGN_SYSTEM.md`.

## The portal: Server Components fetch, Client Components render

Every screen under `src/app/portal/**` is a **two-file pair**:

```
src/app/portal/<role>/<screen>/page.jsx        — Server Component
src/app/portal/<role>/<screen>/<Screen>View.jsx — Client Component ('use client')
```

`page.jsx` is `async`, calls one or more functions from `src/lib/services/*Service.js`, and passes the plain-object result as props to the View component, which is purely presentational for its initial data (local interactive state — filters, form inputs, the quiz's question-by-question progression — stays in the Client Component exactly as you'd expect).

**Why the split is mandatory, not stylistic:** a `page.jsx` needs to stay a Server Component to export `metadata`. But most View components pass callback props into the shared `ui.jsx` primitives (`DataTable`'s `render(row)` per column, `RecordGrid`'s `fields[].value(record)`) — and a Server Component **cannot pass a function as a prop to a Client Component**. This isn't a style preference; it fails the build. This was empirically verified during the master-craftsmanship review (see git history around commit `1613e2d`) after an earlier version of this doc gave the wrong reason (styled-jsx) — the styled-jsx requirement is real too, but the function-prop constraint is the harder, non-negotiable one.

Full detail and the exact template to copy: `src/app/portal/CONVENTIONS.md`.

## The service layer — the Firebase-readiness boundary

`src/lib/services/*Service.js` (one file per portal role, plus `authService`, `libraryService`, `notificationService`) is the **only** place any component is allowed to read portal data from. No component imports `src/lib/portalDemoData.js` directly.

Every exported function is `async` and returns a Promise, even though the mock body resolves instantly against an in-memory array — this is deliberate, not decorative. When Firebase replaces the mock, the function's *body* changes; its signature and the fact that callers already `await` it does not. See `FIREBASE_INTEGRATION_GUIDE.md` for the actual wiring work.

## i18n: a custom LanguageProvider, not Next.js's built-in i18n routing

The public site's language switch is instant client-side (no route change, no `/en`/`/ar` URL prefix) — the user's scroll position and interaction state shouldn't reset when they tap the toggle. `src/components/i18n/LanguageContext.jsx` implements this: a `LanguageProvider` takes a `dict` prop (`{ key: { en, ar } }`), and `useLanguage()` exposes `t(key)`, `lang`, and `toggleLang()`. Legacy HTML pages implement the same idea by hand, per-file, with `data-i18n` attributes and an inline `applyLang()` function — same concept, no shared code, because they predate the React component and were never migrated onto it.

The portal preview is **English-only by deliberate scope decision** — `dir="ltr"` stays fixed, `LanguageProvider` is not used there. This is documented, not accidental; see `CONTENT_STYLE_GUIDE.md`.

## Directory map

```
src/
  app/
    page.jsx, layout.jsx, not-found.jsx    — the only "real" public routes
    portal/
      CONVENTIONS.md                        — required reading before adding a screen
      <role>/<screen>/{page,View}.jsx        — 32 routes across 6 roles
      loading.jsx                            — shared portal loading fallback
  components/
    layout/           — Header.jsx, Footer.jsx (shared by the real homepage route)
    i18n/              — LanguageContext.jsx
    portal/            — PortalShell, PreviewBanner, ui.jsx primitives, and the few
                          genuinely novel components (CoursePlayer, QuizRunner,
                          WeeklyTimetable, AttendanceMarker, AdmissionsPipeline,
                          MessageInbox)
  lib/
    services/          — the Firebase-readiness boundary, see above
    portalDemoData.js  — the only file allowed to hold sample data
  styles/tokens.css     — canonical design tokens for the React side
  data/translations/    — dictionaries for the two real React routes (homepage, 404)
public/
  legacy/*.html         — the 19 static marketing pages
  sitemap.xml, robots.txt
next.config.js          — rewrites (routing bridge) + security headers
```

## Documents to read next

- `DESIGN_SYSTEM.md` — tokens, components, the dark/light rule, responsive/motion conventions.
- `CONTENT_STYLE_GUIDE.md` — voice, terminology, the no-fabrication policy.
- `FIREBASE_INTEGRATION_GUIDE.md` — what changes, file by file, when the real backend lands.
- `DEPLOYMENT_GUIDE.md` — how this actually ships to Vercel.
- `CONTRIBUTING.md` — the day-to-day workflow: adding a page, adding a portal screen, commit conventions.
