# The Digital Campus costing paper

A nineteen-sheet institutional costing and implementation paper, set on the
atelier stationery of the Personal Office, addressed to Sultan Hanafi Royal
Schools.

    python3 tools/build-paper.py          build and paginate
    python3 tools/build-paper.py --pdf    build, then print to PDF
    python3 tools/build-paper.py --map    build, and print what sits on each sheet
    python3 tools/measure-paper.py        verify no sheet is overset

Outputs `digital-campus-paper.html` and `print/digital-campus-paper.pdf`.

---

## The letterhead is not rebuilt here

The plate, the nine-member binding section, the medallion, the pier, the red
channel, the foot and the security layers are loaded unchanged from
`../letterhead-atelier/assets/`. That directory is sealed by `MANIFEST-v1.sha256`
and nothing in it is touched; `python3 ../letterhead-atelier/tools/verify-v1.py`
still passes. Three things on the stationery belong to this document and only
these three:

| | |
|---|---|
| the red channel's legend | `COSTING & IMPLEMENTATION PAPER · ورقة تقدير وتنفيذ`, in place of `OFFICIAL CORRESPONDENCE`. A costing paper is not correspondence and should not claim to be. |
| the register | rebuilt left to right, because the document is written in English. The addressee leads at the left, the file follows at the right — the chancery order of the Arabic register, reflected. |
| the writing field | sheet one opens at 152mm, clear of the register, and closes at 25mm; continuation sheets run 43mm to 25mm. A letter's field is not deep enough for a paper. |

`assets/paper.css` adds the document layer: section heads, editorial tables,
status marks, the arithmetic matrix, the credential chain, the layered model,
notes and the signature block. It adds no identity.

## The page architecture

The 138mm field is divided once — an 18mm rail for the section number, and a
116mm column for everything else, which sets English at about seventy-four
characters. Tables, matrices, point lists and the two diagrams take the field
back at full measure. Narrow argument, wide evidence: that contrast is the
whole layout, and it is why no two sections look alike without anything being
decorated.

Heads are bilingual in one block — the English title with the Arabic beneath it,
right-aligned on the column. The rail carries the number alone. An Arabic title
set in an 18mm rail wraps and collides with whatever follows it.

Every small label is Inter, the instrument voice. Every heading and every word
of argument is EB Garamond. Playfair 700 appears nowhere below the masthead: it
is the identity voice, and the stationery's four-voice rule is not relaxed
because the document is long.

## Pagination is measured, not estimated

`.sheet` is 210×297 with `overflow:hidden`. It clips in silence — a paragraph
pushed past the foot does not warn, does not reflow and does not appear. The
build therefore runs in three passes:

1. **Galley** — every block is emitted once into a single 138mm column.
2. **Measure** — `chrome-headless-shell` renders the galley and reports each
   block's height, *after `document.fonts.ready`*. Measuring at parse time
   measures the fallback face and is wrong by centimetres over a long paper.
   The galley is written beside the document, not into `tools/`, so its
   relative stylesheet links resolve.
3. **Impress** — blocks are packed against the real field extents. A section
   head is marked keep-with-next and is carried forward with the block it
   introduces, so no head is orphaned at a foot.

`tools/measure-paper.py` then checks the built document itself: no field
overset, nothing reaching the microtext or the foot rule, nothing crossing the
binding section, and the register closing above the field rather than into it.
Run it before printing. It exits non-zero on a fault.

## Two glyphs the stationery does not carry

The Latin faces are subset, and the repertoire has no `≈` (U+2248) and no `→`
(U+2192). "Approximately" is therefore set as a word, and the credential
lifecycle and the institutional chain are *drawn* — a spine with nodes, and a
track with stations — rather than typed in arrows. This also fixes the broken
stage name (`Authorisatio / n`) in the source paper, which was an arrow flow
wrapping across the measure.

## What this paper asserts, and what it does not

Everything in the document is traceable to the source costing paper. Where the
source hedges, this paper hedges in the same place and in the same direction.
Two marks run throughout and are defined in Section 01:

* **In place · under refinement** — established on the existing platform.
* **Proposed · subject to approval** — a direction the platform is designed to
  admit; not implemented, and not asserted to exist.

No external vendor's pricing, licensing or renewal terms are asserted anywhere,
because the source asserts none. The $25 / $30 / $35 structure is stated as the
project's own engineering service rate and is explicitly not presented as an
Anthropic, MCP or vendor tariff.

## Metadata to confirm before issue

The source paper carries no reference, no addressee and no Hijri date, so these
are this document's own and are stated in one place at the top of
`tools/build-paper.py`:

| constant | value | note |
|---|---|---|
| `REF` | `PO/SHRS/2026/09/0021` | a reference in the office's own series; replace with the school's registry number if it is to carry one |
| `DATE_AR` | `١٤ ربيع الآخر ١٤٤٨هـ` | derived from the stationery's own anchor (17 Sep 2026 = 3 Rabīʿ al-Ākhir 1448). Confirm against the school's almanac before issue |
| `DATE_EN` | `28 September 2026` | the source paper's date |
| `TO_NAME` / `TO_ROLE` | Sultan Hanafi Royal Schools / The Proprietor and Management | the source names no addressee |

Change any of them and rebuild; nothing else needs editing.

## The signature

The principal signs, with the stationery's own signature treatment. Opposite,
and deliberately quieter, is the space in which the institution records its own
approval — name, designation and date, left blank. A costing paper is an
instrument, and an instrument carries the place where it is accepted. The space
asserts no approval that has not been given.
