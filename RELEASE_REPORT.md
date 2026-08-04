# Albalagh Global — Release Report

Prepared at the conclusion of this session's platform-wide upgrade pass. Covers the public website and the six-role portal preview ecosystem (Student, Faculty, Staff, Admin, Applicant, Parent).

## 1. Improvements made

**Design & accessibility**
- Rebalanced dark/light section ratio sitewide to a hero/footer-only "bookend" pattern (previously several pages were 50%+ dark-navy blocks).
- Fixed a sitewide WCAG AA contrast failure: gold text/icons on light backgrounds measured ~2.7:1; retuned to a dedicated `--gold-ink` token (~135 instances) with a verified ≥4.6:1 margin against every background it's actually used on, including closing a marginal edge case found during verification. Gold-on-dark and gold-fill buttons (already compliant) were left untouched — brand identity preserved, not diluted.
- Fixed a genuinely broken mobile navigation menu on three pages (hamburger button wired to nothing), missing `<h1>` landmarks on ten pages, missing skip-links/focus-visible states/SEO metadata on one page, and stale footer content drift on four pages.
- Replaced placeholder stock-image slots with hand-authored SVG illustrations built from the site's own design language (external image sourcing is blocked by this environment's network policy — documented below, not worked around).

**Content integrity**
- Brought three pages' non-functional language toggle (button worked, translated nothing) up to full bilingual parity with the rest of the site — ~630 translation keys added, verified for key-parity and fact-fidelity (every fee figure, route name, and credit-unit number checked byte-identical between languages).
- Integrated real institutional content the site owner supplied: the AIPS/PCPP professional-development programme (new dedicated page), the 13-clause Objects of the College, the Institutional Credit Unit and Student Workload Policy, and the mandatory entrance assessment structure.
- Cross-checked pricing consistency: the AIPS fee (₦20,000) agrees exactly across all three places it appears (public page, tuition page, portal finance data). No other figures found duplicated inconsistently.

**Portal ecosystem (new)**
- Built all 32 routes across six roles — dashboards, a working course player, a scored quiz-taking flow, gradebook, attendance marking, an admissions pipeline, a fee ledger, timetable, messaging, notifications, settings — on a shared component system (`Card`/`StatGrid`/`Badge`/`DataTable`/`EmptyState`).
- Every screen renders behind an unconditional "Preview Mode" banner and uses only clearly-placeholder sample data — no invented student/staff identities, no fabricated institutional facts.
- **Firebase-readiness refactor**: every route now fetches through `src/lib/services/*Service.js` (one file per role, async function signatures matching real Firestore/Auth/Storage call shapes) instead of importing sample data directly. `page.jsx` (server) fetches and passes props; the client view is purely presentational. Wiring Firebase in later means rewriting the inside of ~40 small functions, not touching a single page.

**Code quality**
- Fixed 8 dead links, a self-referencing canonical/OG/breadcrumb URL bug on 6 pages (search engines were being told the wrong authoritative URL), two sets of duplicate components (collapsed into shared primitives), and several dead exports left over from refactoring.
- Added ESLint configuration (had been silently not running) and fixed the errors it surfaced.
- `npx next build` and `npx next lint` both pass cleanly across every pass in this session.

## 2. Remaining external dependencies

Nothing further is blocked on anything within this session's control except:

| Dependency | Blocks | Status |
|---|---|---|
| **A real Firebase project** (console.firebase.google.com, free tier is sufficient) | Phase 0 of the LMS/portal backend | Not started — needs your project config |
| **A payment gateway account** (Paystack or Flutterwave, standard for Naira payments) | Real fee collection (Finance module, Phase 5) | Not started — needs your merchant credentials |
| **This environment's network policy** | Real photography (currently substituted with illustrations) | Environment-level setting, adjustable in your Claude Code environment settings if you want to revisit |

## 3. Overall production readiness

**The public marketing site is production-ready.** Bilingual, accessible (AA), SEO-complete, fast (static generation throughout), no known broken links or console/hydration errors, honest about what's confirmed vs. pending (fee TBCs, appointment-pending leadership) rather than padded with placeholders.

**The portal ecosystem is a complete, polished frontend, explicitly not a production backend.** Every screen works, looks premium, and is architecturally ready for Firebase — but there is no real authentication, no data persistence, no real payment processing. This is by design (documented on every screen via the Preview Mode banner) and is the correct state for this stage: building fake persistence would have been worse than being honest about the gap.

## 4. Recommendations before public launch

1. **Provision Firebase and start Phase 0** (auth) whenever ready — the abstraction layer is waiting for it.
2. **Decide the 8 department "Learn More" links on the Academic Structure page** — currently honest placeholders; build dedicated programme pages only if that's an intentional scope addition, not a default.
3. **Real photography**, when available (a widened network policy, or images you supply directly) — the current illustrations are a deliberate stand-in, not a final design decision.
4. **Portal bilingual coverage** — the portal preview is English-first by deliberate scope reduction; extend to Arabic before treating it as a public-facing feature rather than an internal preview.
5. **Payment gateway selection**, whenever Finance (Phase 5) becomes a priority — needed before any real fee collection can go live.

Nothing above is a blocker to continuing to use or show the site as it stands today — they're the known, honestly-stated boundary between "excellent preview" and "fully live platform."
