# Design System

The visual language shared across the public site and the portal preview. If you're adding UI anywhere in this repo, everything you need is here — don't invent a new pattern before checking this document.

## Brand mark

An 8-pointed star/compass rose, used at every scale from the 26px sidebar logo to full-section watermark illustrations:

```html
<svg viewBox="0 0 48 48" fill="none" aria-hidden="true">
  <path d="M24 4 L30 14 L42 14 L33 22 L37 34 L24 27 L11 34 L15 22 L6 14 L18 14 Z"
        stroke="var(--gold)" stroke-width="1.6" fill="none" />
</svg>
```

It's the closest thing this institution has to a visual identity beyond typography. When a section needs an illustrative accent and no photography is available (see `RELEASE_REPORT.md` — external image sourcing is currently blocked by this environment's network policy), echo this mark — scaled, repeated, outlined as a watermark — rather than inventing an unrelated motif.

## Colour tokens

Canonical values live in `src/styles/tokens.css`. **Every legacy HTML page under `public/legacy/` duplicates the same block in its own `<style>`** — this is the one significant piece of technical debt in the design system (see `ARCHITECTURE.md`): a token value change means editing 20 files, not one. Always grep for the token name across `public/legacy/*.html` before assuming a change to `tokens.css` alone is enough.

| Token | Value | Use |
|---|---|---|
| `--navy` | `#173A63` | Primary text/heading colour on light backgrounds, primary UI chrome |
| `--navy-dark` | `#0F2847` | Hero/header/footer/mobile-nav backgrounds — see "the dark/light rule" below |
| `--gold` | `#BC9A4A` | Brand accent — **only** for gold-on-dark text/icons, or as a solid fill behind dark text (e.g. `.btn-primary`). Never as text/icon colour on a light background — fails WCAG AA (~2.77:1). |
| `--gold-light` | `#D8C58C` | Lighter gold-on-dark variant (hover states on dark chrome) |
| `--gold-ink` | `#886828` | The accessible substitute for gold text/icons/borders **on light backgrounds** (`--surface`/`--manuscript`). Verified ≥4.6:1 against both. Use this, not `--gold`, for eyebrow labels, stat accents, icon strokes, and state borders that sit on a light section. |
| `--manuscript` | `#F6F2E7` | The site's "cream/paper" light background — the default for content sections outside the hero/footer |
| `--surface` | `#FFFFFF` | Cards, the lightest background layer |
| `--ink` | `#1C2430` | Body text |
| `--ink-muted` | `#4B5568` | Secondary/supporting text |
| `--border` / `--border-dark` | `#E1DACB` / `#2A3E5C` | Hairline borders on light / dark backgrounds respectively |
| `--emerald` | `#1E4C43` | A single secondary accent — used sparingly (success states, one or two icon accents), never as a primary colour |

**The gold-contrast rule, precisely:** `--gold` is fine as text/icon colour only when the immediate background is dark (`--navy-dark` or an explicitly dark section), or as a solid fill with dark text on top (`.btn-primary`: navy-dark text on a gold button). Anywhere gold text/icon/border sits on `--surface` or `--manuscript`, use `--gold-ink` instead. This was a real, sitewide WCAG AA failure found and fixed this session (~135 instances) — don't reintroduce it.

## Typography

| Font | Use |
|---|---|
| **Fraunces** (serif) | All headings, English |
| **Amiri** (serif) | All headings, Arabic |
| **Inter** (sans) | Body text, English |
| **IBM Plex Sans Arabic** (sans) | Body text, Arabic |

Loaded once via Google Fonts `<link>` in `src/app/layout.jsx` (real routes) and duplicated per-file in each legacy page's `<head>` (same friction as the colour tokens — see above). Font selection switches automatically with `[dir="rtl"]` — every component that sets `font-family` should have an `:global([dir='rtl'])` (React) or `[dir="rtl"]` (legacy HTML) override, never assume English typography.

Scale is set contextually per component (no single global type-scale variable exists) — match the nearest existing heading/label of the same semantic weight rather than picking an arbitrary `font-size`.

## Spacing & radius

```css
--space-1: 8px;  --space-2: 16px; --space-3: 24px;
--space-4: 32px; --space-5: 48px; --space-6: 64px;

--radius-sm: 6px;   /* small buttons, chips, badges, portal "app controls" */
--radius-md: 8px;   /* cards, most containers */
--radius-lg: 16px;  /* large feature panels, CTA bands */
```

Public-site marketing CTAs (`.btn-primary`, gold) use `--radius-md`. Portal "app controls" (the `.lang-toggle`-style navy chrome buttons `PortalShell` and its screens use) use `--radius-sm` — this is a deliberate, established distinction between a marketing call-to-action and a functional in-app control, not an inconsistency to "fix." If you're building a new button, ask which category it is before picking a radius.

## Shadows

```css
--shadow-1: 0 1px 3px rgba(15,40,71,0.08);   /* resting card elevation */
--shadow-2: 0 8px 24px rgba(15,40,71,0.12);   /* hover-lift, modals */
--shadow-3: 0 16px 48px rgba(15,40,71,0.18);  /* the strongest — mobile nav overlay only */
```

## Motion

- **Interactive-lift hovers only** (cards, tiles that move/gain shadow on hover) get an eased transition, `0.15s ease` sitewide.
- **Plain colour/background hovers** (nav links, small buttons) snap instantly — no transition. This was verified deliberately during the design review, not an oversight: adding transitions here would introduce a pattern that doesn't actually exist elsewhere in the system.
- **Every** transition/animation must respect `prefers-reduced-motion: reduce` — wrap it in the media query, matching the existing `.reveal` scroll-in pattern and the portal sidebar slide. This has been a real, repeatedly-found bug source (added to 10+ files at different points this session) — check it explicitly for any new animated element.

## The dark/light "bookend" rule

The single most important layout rule on the public site, established in `al-balagh-design-master-prompt.md` after an early version of the site alternated dark and light sections almost 1:1 (heavy, corporate-feeling):

1. **Hero and footer get the dark treatment by default.** Everything else defaults to `--manuscript`/`--surface`.
2. **At most one deliberate dark accent band per page**, beyond hero/footer — and only where it earns its place (an org chart, a timeline, a calculator result panel), never as decoration.
3. Any text left on a dark section must be white or `--gold-light` — never `--ink`/`--ink-muted`/`--gold-ink` on dark, which is illegible or fails contrast the other direction.

## Portal component primitives

`src/components/portal/ui.jsx` — every portal screen should build from these rather than hand-rolling equivalent markup:

- **`Card`** — the base container (`title`, optional `action` slot, children).
- **`StatGrid`/`StatTile`** — dashboard stat rows.
- **`Badge`** — status pills, five tones (`neutral`/`gold`/`success`/`alert`/`info`), each pre-tuned for contrast (the `gold` tone already uses `--gold-ink`).
- **`DataTable`** — `columns` + `rows`, with `emptyLabel` handling the empty state automatically. Don't build a bespoke `<table>` if this covers the shape.
- **`RecordGrid`** — the read-only key/value profile layout, shared across Student/Faculty/Staff profile screens (this used to be duplicated three times — collapsed into one component during the master-craftsmanship review; don't reintroduce the duplication).
- **`EmptyState`** — the standard "nothing here yet" panel, used automatically by `DataTable` and directly by any screen with a list that could legitimately be empty.

`PortalShell` wraps every screen: sidebar nav (single source of truth is `NAV_BY_ROLE` inside `PortalShell.jsx` — add new routes there, don't hand-roll nav links elsewhere), topbar, and the unconditional `PreviewBanner`.

For a genuinely novel interaction (a course player, a quiz-taking flow, a weekly timetable grid, an attendance-marking grid, a Kanban-style pipeline), build a new component under `src/components/portal/` using the same token-based styling — never inline a one-off style object for something reusable.

## Responsive breakpoints

No single global breakpoint variable — components set their own `@media` queries, but converge in practice around:

- **~960px** — public-site desktop nav collapses to the hamburger menu.
- **~860px** — portal sidebar collapses to the mobile slide-in drawer.
- **~700px** — wide tables/grids restack to a single column.

Any new wide table or grid should wrap in `overflow-x: auto` with a sensible `minmax()` track width rather than assuming it will simply reflow — this is the established, verified-working pattern (`DataTable`, `WeeklyTimetable`, `AdmissionsPipeline`).

## Icons

Hand-authored inline SVG throughout — no icon library dependency. Stroke-width scales with the icon's rendered size: `~1.5` for small inline glyphs, `~1.6–1.8` for the brand mark at typical sizes, thinner (`~0.35`) only for the oversized decorative watermark use. Match the nearest existing icon at a similar size rather than picking an arbitrary stroke-width.
