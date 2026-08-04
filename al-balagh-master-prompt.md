# Albalagh Global Content Integration — Master Prompt

Use this once at the start of a session, then paste raw content in follow-up messages. Claude should integrate it without re-asking for permission on routine edits, but must still ask before anything irreversible, brand-defining, or fact-inventing (see "Stop and ask" below).

---

## Identity

Institution: **Albalagh Global**
Short form in running text: **Albalagh**
Arabic: **البلاغ العالمية** (short form: **البلاغ**)
No acronym — brand is used in full or as "Albalagh", never abbreviated to initials.

## What actually exists (ground truth — do not contradict this)

- A Next.js 14 app at the repo root of `ahmadsulaimiy1/My-books`, deployed to Vercel, building from `main`.
- One real componentized route: the homepage (`src/app/`), bilingual EN/AR via `LanguageProvider`.
- 19 static legacy HTML pages under `public/legacy/`, reached via `next.config.js` rewrites (About, Admissions, Governance, Tuition, four Portal pages, etc.). Each is self-contained bilingual HTML with its own inline translation dictionary.
- **No backend.** No Firebase, no database, no auth, no real Student/Lecturer/Staff/Administrator portal with live data. The "Portal" pages that exist are honest preview/marketing pages describing what a future portal will contain — not working systems.
- No payment processor, no real application pipeline. "Apply" flows are `mailto:` links.

Any content you integrate must fit this reality. Don't wire buttons to systems that don't exist. Don't imply a database or login is live if it isn't.

## Job when content is pasted

1. **Place it.** Decide which existing page(s) the pasted content belongs on, or whether it needs a new page — new pages must slot into the existing rewrite/routing pattern, not a redesign of it.
2. **Merge, don't duplicate.** If pasted content overlaps or repeats something already on the site (this happens — check before writing), reconcile into one version and remove the stale copy.
3. **Resolve contradictions.** Pricing, fee breakdowns, dates, terminology, programme names, admission routes — if two sources disagree, pick the most complete/specific one, note in your summary to me which you dropped and why, and make every page match.
4. **Standardise terminology and mnemonics.** One name per concept, used consistently site-wide (e.g. always "Professional Competency and Practice Programme (PCPP)", never a mix of that and ad hoc alternates). Introduce an abbreviation only where it's used often enough to earn one.
5. **Never fabricate.** No invented accreditation, rankings, partnerships, statistics, staff names, or addresses. Where the pasted content doesn't cover a fact the page needs, use the existing "Institutional Status" callout pattern (already on About/Governance/Founders pages) instead of inventing one.
6. **Match the existing voice.** British English, no hype adjectives, specific numbers over vague superlatives, same navy/gold design system, same bilingual dictionary pattern per page.
7. **Ship it.** Commit with a clear message, push, and tell me in 3–5 sentences what changed and what you deliberately left out or flagged.

## Stop and ask (don't guess on these)

- Renaming the institution anywhere it appears in already-live copy (title tags, footer copyright, legal "Objects" text) — confirm the final name first.
- Any currency/price change that isn't a straightforward duplicate cleanup (i.e. you're choosing between genuinely different figures, not just deduplicating the same one).
- Deleting an existing page or section outright.
- Anything that would require pretending a backend/portal/payment system exists when it doesn't.

Everything else — restructure, merge, tighten copy, fix inconsistent labels, apply mnemonics — do it, then report back.
