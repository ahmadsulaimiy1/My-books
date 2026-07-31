# Al-Balagh International Premium College — Digital Campus

Official website and Digital Campus platform, built with Next.js 14 (App Router).

## Status

Mid-migration from static HTML to componentized React. See **[docs/MIGRATION.md](./docs/MIGRATION.md)** for exactly what's converted vs. still static — please read that before assuming any given page is "real Next.js."

## Getting started

```bash
npm install
npm run dev
```

Open http://localhost:3000. The homepage (`/`) is a real Next.js route; every other listed page (`/about`, `/admissions`, etc.) resolves via a rewrite to a complete, working static HTML file in `public/legacy/`.

## Project structure

```
src/
  app/                  Next.js App Router routes
    layout.jsx          Root layout (fonts, metadata)
    page.jsx            Homepage ("/") — real converted route
    globals.css         Global styles (imports tokens.css)
  components/
    layout/              Header.jsx, Footer.jsx — shared across all pages
    i18n/                 LanguageContext.jsx — EN/AR toggle, used by every page
    common/ navigation/ cards/ forms/ tables/ dashboard/
                          Empty, reserved for components extracted during
                          the ongoing legacy → React conversion
  data/
    translations/         Per-page translation dictionaries (homepage.js so far)
  firebase/               Reserved for Firebase config once a real project exists
  lib/                    Reserved for shared utilities
  styles/
    tokens.css            Design tokens (colour, spacing, radius, shadow)
public/
  legacy/                 19 complete, working static HTML pages, pending
                           conversion — see docs/MIGRATION.md
docs/
  MIGRATION.md            Conversion status and next steps
```

## Environment variables

Copy `.env.example` to `.env.local` and fill in real values when a Firebase project exists. Nothing in this repo depends on real credentials yet — the site works fully without them.

```bash
cp .env.example .env.local
```

## Deployment

Standard Next.js app, no special configuration needed. Push to GitHub, import into Vercel, it auto-detects and builds. This repo's `npm install`/`npm run build` has **not** been run or verified in the environment that produced it (no network access there) — please run it once locally (or let your CI/Vercel do it) before relying on it.

## Design system

Colours, typography, spacing, and component patterns are documented as CSS custom properties in `src/styles/tokens.css`, carried over exactly from the original design system (navy `#173A63`, gold `#BC9A4A`, emerald `#1E4C43`, manuscript `#F6F2E7`; Fraunces/Inter for English, Amiri/IBM Plex Sans Arabic for Arabic).
