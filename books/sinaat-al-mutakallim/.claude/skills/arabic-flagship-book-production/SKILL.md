---
name: arabic-flagship-book-production
description: The production standard of «صناعة المتكلّم العربي» (11 volumes, 17×24 cm) — typography first, white page field, colour as event, digital-first with no bleed, scholarly verification, cross-references, terminology, voice distinction, and the eleven-pass audit. Use for any work on the interior pages, their design, their text, their verification, or their delivery.
---

# Arabic flagship book production — the standard of this series

The binding rules of the series are in `CLAUDE.md` and the Bible (`bible/`, index `bible/00-…`); where this skill and the
Bible differ, the Bible governs. This skill gathers the publisher's standing directives so that every session applies
the same standard to all eleven volumes.

**The target is not a valid PDF. It is a finished scholarly publication that looks and reads as if typeset by an elite
Arabic book designer and edited by scholars.** Automated validation establishes technical integrity; expert review
establishes publication quality. Both are required, and the series is never declared finished because the checks pass.

## 1. Quality hierarchy

1. Typography
2. Page architecture and hierarchy
3. Arabic readability and line rhythm
4. White space and proportion
5. Scholarly accuracy
6. Figures, tables, visual communication
7. Colour and material accents
8. Decorative elements

Decoration never compensates for weak typography or weak page architecture.

## 2. Typography is the primary design element, not a final formatting step

- **Faces:** Scheherazade New — the body; Changa (Light/Bold) — clean, architectural headings; Kufam / Kufi display —
  major titles and exceptional display moments; Amiri — hadith, poetry, classical quotations; Amiri Quran — the Quran.
  IBM Plex Sans Arabic for navigation only. No system font in any PDF (the build stops).
- **Judged at the level of:** letterform quality, joining, diacritics and mark positioning, kashida, word spacing, line
  spacing, paragraph rhythm, justification, line endings, heading hierarchy, footnote legibility, Quranic, hadith and
  poetry typography, tables, dialogue, running heads, folios, quotation blocks, Arabic-Indic numerals (Amiri figures),
  punctuation, Latin/Arabic coexistence, font embedding, optical (not merely numerical) balance.
- Never accept typography because the PDF renders without errors. Look at the page at 100%.

## 3. The page field: white is the norm, colour is the event

- **The natural page is premium sharp white** — not cream, ivory, beige, warm grey, parchment or yellowish off-white;
  not office-paper white and not blue-white. White is the principal canvas of the whole series.
- **Hierarchy:** WHITE PAGE FIELD → SAPPHIRE STRUCTURE → GOLD DETAIL → RESTRAINED RUBY ACCENT → GRAPHITE TEXT.
- Other colours are designed accents and fields, never a substitute for the page background. Never tint a page for
  atmosphere; preserve generous untouched white space.
- **Colour pages are rare, intentional, hierarchical:** section dividers, major conceptual statements, transitions,
  special quotations, architectural openings. Approved fields: deep sapphire, midnight sapphire, restrained ruby (only
  where red means something — red is never decoration), very pale pearl/sapphire, sophisticated graphite, and
  exceptionally restrained warm pearl only where the content warrants (e.g. a classical source).
- **Rhythm:** white reading → white reading → architectural accent → white reading → major colour statement → white
  reading. If everything becomes sapphire, nothing is special.
- **Not mechanical:** each volume's colour rhythm answers its own intellectual character and structure while remaining
  one recognisable 11-volume system. The per-volume plan is declared in data, not improvised per build.
- **The system as built** (Bible ch. 22 §7; `pdf/opening.py` `:root`): white by absence (nothing painted under the
  text); inks `--ink #1F2329`, `--ink-2 #474B53`, `--ink-3 #6A6F78`; hairlines `#DDE0E5` / `#C9CDD4`; gold-ink
  `#7F5F12`. Events are declared in `pdf/events.py` and checked against the manuscript and the quotation ledger at
  every build: a sapphire door for each bab (graphite for the reference, midnight for the Muqaddima), at most one
  pale-sapphire framework and one warm-pearl heritage field per volume, at most two hinge plates, and verbatim
  midnight statements in V1 and V10 only. The chapter opens on a sapphire lintel at 84 mm; text from 92 mm.
- The Quran («ياقوتيٌّ وحده»: deep ruby `#7B1730`, Bible part 16) is never on a coloured field and never texture;
  ruby belongs to the Quran alone, error and danger take crimson `#A8172E`. The feel: clean, luminous, scholarly, architectural, luxurious — not
  vintage, parchment, rustic, or artificially «Islamic».

## 4. Digital-first page architecture — no bleed by default

- The PDF is the first-class design object: it must look complete and intentional at 100% on screen, tablet, phone and
  desktop, without relying on physical-paper effects.
- **No bleed** is assumed, requested or built into the interior at this stage. No full-bleed backgrounds, no edge-to-edge
  colour, nothing beyond the trim as a default technique. Colour fields sit inside the safe page architecture with
  deliberate margins. A full-page treatment only when demonstrably necessary — and first try to achieve it within the
  trim and safe area.
- No artificial paper texture, grain, parchment, shadow or fake physical page; no simulated foil, emboss or varnish
  inside pages (they belong to the physical covers); no unnecessary transparency — text sits on clean, stable fields.
- Keep generous print-safe margins (the grid: `pdf/geometry.py`), so the PDF adapts to the printer's exact specs later.
- Print: premium bright-white uncoated book paper, neutral, high opacity, approved on a physical proof
  (`covers/printer-spec.json`). Print masters are made only when printer, paper, binding and trim are confirmed; the
  archived bleed masters (`book/_production/الأرشيف/نسخ-المطبعة-بنزف/`) are a record, not a deliverable.
- Frozen: 17×24 cm, eleven volumes. The three approved cover editions are not redesigned.

## 5. Page composition

No orphan headings; no stranded minor heads; no page ending on one isolated word or a broken dialogue; no microscopic
text (footnotes smaller but genuinely readable — preflight enforces a floor); no automatic symmetry everywhere; no
excessive coloured pages; no generic AI decoration (every rule, device and field has a reason); no unnecessary
full-page illustration (visuals serve the intellectual architecture). Fix layout defects in the tools (`pdf/volume.py`,
`pdf/opening.py`, …), never by patching a PDF.

## 6. Scholarly verification and textual fidelity

- Every transmitted quotation — Quran, hadith, athar, a scholar's statement, poetry, proverb, historical report,
  linguistic example, attributed saying — is a textual object that is verified against a primary or authoritative
  source before publication, read from the source itself, not from memory, snippets or secondary quotation.
- Preserve verified wording; never silently modernise, normalise, shorten or «improve» it. If variants exist: identify
  the variant, state the adopted wording and its edition, explain a material difference.
- Never manufacture a quotation from a known meaning; never attribute a saying because it is commonly attributed. If
  attribution cannot be established: verify, drop the attribution, or state it as the author's own analysis (Bible
  ch. 83 §3).
- **Hadith and athar:** takhrīj with the wording, companion/narrator, primary collection, book/chapter or number,
  edition, volume/page where useful, and grading when relevant. Distinguish hadith from athar, marfūʿ from mawqūf, the
  authenticity of a report from that of a wording, a scholar's judgement from an independent one. Never upgrade a
  disputed narration.
- «لا متحقّق إلا ما طوبق على المطبوع نفسه»; a digital copy is «توثيقٌ ناقص». No page number or edition that was not seen.
- Tools and ledgers: `pdf/verify.py`, `pdf/hadith.py`, `pdf/quran.py`, `pdf/shamela.py`, `pdf/ledger.py`,
  `book/_production/التحقيق/سجل-النقول.tsv`, `خريطة-نسب-القول.tsv`, `مواضع-الأحاديث.md`.

## 7. Footnotes are scholarship, not a bibliography

Each note has one job: source · textual verification · explanation · cross-reference · methodological note. Use only
what the passage requires. **Rigour without clutter:** maximum necessary rigour, not maximum visible citation density.
«لا تُجمِّل ما يحتاج إلى تحقيق، ولا تُحقِّق ما لا يحتاج إلى إطالة.» Notes are written in place with the sentence
(`[^n]`, then `python3 pdf/renumber.py <file>`), and are page notes in the layout.

## 8. Voice distinction

The reader always knows whether they read a historical quotation, the author's interpretation, a pedagogical example,
a representative/hypothetical scene, a contemporary pedagogical formulation, a verification note, or an established
scholarly fact. The author's inference is never presented as a quotation or as settled fact.

## 9. Cross-references and terminology

- Every internal reference resolves to المجلد → الباب → الفصل → القسم, is machine-checkable and human-readable, never
  by page number; a bab in another volume names its volume; the four numbers (volume, bab, level, chapter) are never
  mixed. Rerun the audit after any structural, pagination or numbering change: `python3 pdf/xrefs.py`.
- A series-wide terminology ledger (`book/_production/التحقيق/سجل-المصطلحات.tsv`, audit `python3 pdf/termaudit.py`):
  one term, one meaning, one spelling across the eleven; deliberate distinctions between near-synonyms kept.

## 10. The audit — separate passes, never «check everything once»

1. Textual integrity — quotations, Quran, hadith, poetry, Arabic wording.
2. Scholarly verification — sources, attribution, takhrīj, disagreements, claims.
3. Internal architecture — volumes, chapters, sections, appendices, cross-references.
4. Terminology — consistency across all eleven volumes.
5. Pedagogy — objectives, exercises, progression, answer keys, mastery criteria.
6. Arabic language — grammar, morphology, usage, naturalness, register, punctuation.
7. Typography — faces, shaping, diacritics, poetry, quotations, footnotes, tables.
8. Page composition — orphans, widows, stranded headings, awkward breaks, excess white, crowded pages.
9. Visual system — white/sapphire/gold/ruby architecture, hierarchy, colour restraint, figures, diagrams.
10. Production — 17×24 cm, margins, embedded fonts, PDF integrity, bookmarks, metadata, numbering, file names, covers.
11. Human editorial reading — representative pages read as a scholar, a teacher, a university student and a serious
    general reader.

Findings are verified adversarially before any change; a change to a verified quotation is never made to improve it;
every substantive text change is logged in `book/_production/هندسة-السلسلة/سجل-التصحيحات-البنيوية.tsv`.

## 11. After any change

`python3 pdf/premove.py --strict` (structure and text), `python3 pdf/closure.py`, `python3 pdf/build_all.py` (rebuilds
what changed, regenerates covers from page counts, runs preflight on all eleven), then look at the pages
(`python3 pdf/spreads.py`). Then `python3 pdf/manifest.py` for the delivery list.
