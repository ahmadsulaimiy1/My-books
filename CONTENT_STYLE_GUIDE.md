# Content Style Guide

How Albalagh Global writes about itself. Read this before writing or editing any copy — public site or portal.

## The non-negotiable rule: never fabricate

No invented accreditation, rankings, partnerships, statistics, staff names, biographies, or working systems that don't exist. This is the single most important rule in this codebase and it has shaped real decisions throughout the project:

- Where a leadership position has no real appointee, the copy says **"Appointment Pending"** with a biography of **"Biography to be published upon appointment"** — never a placeholder name that could be mistaken for a real person.
- Where a fee or policy figure genuinely isn't set yet, the copy says **"TBC"** (to be confirmed) — never an invented number.
- Every portal screen (Student/Faculty/Staff/Admin/Applicant/Parent) carries an unconditional **"Preview Mode"** banner and uses only sample data with obviously-placeholder identities ("Demo Student," "Student A") — never a realistic-sounding fake person.
- The **"Institutional Status"** callout pattern exists specifically for this: when a page needs to say something about a fact that isn't fully confirmed, state the real status plainly rather than writing around the gap with vague confidence.

If you're editing copy and find yourself wanting to add a specific claim, a number, or a name to make something sound more finished or more impressive — stop. That instinct is exactly the failure mode this rule exists to prevent. Use the existing honesty patterns instead.

## Voice

**British English throughout** — "organise" not "organize," "programme" not "program" (except when referring to software), "centre" not "center."

**Confident, academically credible, welcoming, professional.** The test used throughout the final editorial pass, and the one to keep applying: *"Would a prestigious global institution genuinely say this?"* If not, it needs rewriting — not necessarily softened, often the opposite (over-explaining and hedging reads as less confident, not more careful).

**No hype adjectives.** Specific facts over vague superlatives. "A bilingual, online-first college combining classical Islamic scholarship with the technical and professional skills of the modern world" describes; "a world-leading, cutting-edge institution" claims. The former is this site's actual register.

**No developer language leaking into public copy.** Found and fixed twice during the final review: phrases like "no redesign required" or "not hard-coded into the website" are engineering asides that have no place in front of a prospective student or a parent reading about fees. If a sentence describes how the *website* works rather than how the *institution* works, it's in the wrong register.

**Write for the reader in front of you.** The final review read every major flow from six distinct perspectives — registrar, admissions director, first-time applicant, parent, faculty member, enrolled student — deliberately, because the right register for an internal governance page is not the right register for a nervous first-time applicant's status screen. When writing new copy, identify who's actually reading it before choosing the tone.

## Terminology — use these exact forms, consistently

| Term | Canonical form | Notes |
|---|---|---|
| Institution name | **Albalagh Global** (full), **Albalagh** (short, running text) | Never "Al-Balagh" (old, superseded name) or any other variant. Arabic: **البلاغ العالمية** (full), **البلاغ** (short). |
| The four Schools | School of Islamic Sciences · School of Media, Journalism & Digital Communication · School of AI, Innovation & Technology · School of Business, Entrepreneurship & Financial Management | This exact wording, everywhere — a naming drift on `about.html` was found and fixed during the final review. If you're about to write these names anywhere, copy them from `Header.jsx`/`Footer.jsx` or `academic-structure.html`, don't retype from memory. |
| AIPS | **Albalagh Institute of Professional Studies (AIPS)** | Introduce the full form once per page, then the abbreviation is fine. |
| PCPP | **Professional Competency and Practice Programme (PCPP)** | Same pattern — full form once, then abbreviate. Some older pages spell it out every time rather than using the abbreviation; that's an accepted inconsistency (an older convention, not a contradiction), don't mass-edit it without reason. |
| Credit Unit | **Credit Unit (CU)** | Defined in full in the Institutional Credit Unit and Student Workload Policy (`academic-structure.html`) — reuse that page's exact figures (66–72 CU for the flagship programme, the 1–4 CU framework) rather than restating from memory. |
| Currency | **₦ (Naira)** only | The AIPS fee (₦20,000 = ₦5,000 + ₦15,000) is the one fully confirmed figure — it must read identically everywhere it appears (`institute-professional-studies.html`, `tuition-scholarships.html`, the portal's `staffService`/`portalDemoData` fee data). Everything else in the fee schedule is honestly "TBC" — don't invent a number to fill the gap. |

## Bilingual content rules

- Every public-facing page must be **fully** bilingual — a language toggle that changes `dir`/`lang` without actually translating the content is a real bug, not a cosmetic gap (found and fixed on three pages this session: `admissions.html`, `tuition-scholarships.html`, `digital-campus.html`).
- When translating, **reuse established Arabic terminology** rather than re-translating a concept that already has a canonical Arabic rendering elsewhere on the site (check `academic-structure.html` and `institute-professional-studies.html` for the Schools, AIPS/PCPP, and Credit Unit terms specifically).
- Never let English and Arabic diverge in *meaning* — a fee figure, a date, a route name must mean the same thing in both languages, even where the phrasing naturally differs.
- The **portal preview is English-only**, deliberately, as a documented scope reduction — not an oversight to silently fix. If you're asked to extend it to Arabic, that's a real feature decision requiring the same translation-quality care as the public site, not a quick pass.

## Where to look before writing anything new

- `al-balagh-master-prompt.md` — the original standing content ground rules.
- `al-balagh-design-master-prompt.md` — the design-elegance principles (relevant if new copy is tied to new layout).
- `RELEASE_REPORT.md` — what's already been fixed; don't reintroduce a problem this document says was resolved.
