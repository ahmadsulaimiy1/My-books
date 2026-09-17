# المكتب الخاص — The Atelier Sheet

**الإمام أحمد بن إبراهيم السليمي (آل سلام)**
PERSONAL OFFICE · IMAM AHMAD IBROHIM SULAIMIY · ĀL-ES-SALAM

**SAPPHIRE · RED · PEARL · GOLD · PLATINUM · STAINLESS**

> ### 🔒 LOCKED AS `letterhead v1.0`
>
> This design is **released**. The frozen specification is [`SPEC-v1.md`](SPEC-v1.md);
> every released file is sealed in `MANIFEST-v1.sha256`.
>
> ```bash
> python3 tools/verify-v1.py      # → ✓ locked, and this tree matches it
> ```
>
> The verifier checks two things: that every dimension, colour and type size
> the design depends on is still in the stylesheets **by name**, and that no
> released file has changed.
>
> Release point: the commit titled **`letterhead: lock the atelier sheet as
> v1.0`** on `claude/luxury-executive-letterhead-5vyoye`, tagged
> **`letterhead-v1`**.
>
> **Changing anything in `SPEC-v1.md` is a change to the design, not a fix.**
> It belongs in v2: bump `VERSION` in `tools/verify-v1.py`, update the
> constant, re-seal with `--seal`, tag. The *content* of a letter — addressee,
> reference, date, subject, body, signatures — is free and is not part of v1.

![the stationery, photographed](presentation.jpg)

> Earlier letterheads in `docs/letterhead/`, `docs/letterhead-flagship/` and
> `docs/letterhead-instrument/` are untouched. This folder is the released one.

---

## Four metals, one job each, one light

| Metal | Job | Where |
|---|---|---|
| **GOLD** | the **proud** metal | the rail of the binding section · the medallion's outer ring · the insignia · the keyline along the plate's lower silhouette · the rule under the name · the **lower** wall of the red channel · the register hairline · the QR frame · the signature and foot rules |
| **PLATINUM** | the **recessed** metal | the floor of the binding channel, and nowhere else |
| **STAINLESS** | instrument | the medallion's inner bezel · the **upper** wall of the red channel · microtext · latent geometry |
| **SAPPHIRE** | ruling and ground | the plate itself, and the hairline above the Latin wordmark |
| **RED** | *not a metal, and not architecture* | the classification channel · the reference · the contact pips · the folio. It marks what must be **read**. |

Platinum is deliberately **not a second stainless**. It lies on the floor of a
channel that the gold rail overhangs, so it receives less light than anything
else on the sheet: the ramp is cooler, a stop darker throughout, and its
brightest turn is a pale grey-blue rather than white. *A recessed metal cannot
out-shine a proud one* — that single rule is why the two read as one assembly
instead of two competing lines.

**Light is fixed top-left over the whole sheet and every member obeys it.** For
a vertical channel that means the near (left) wall falls into shade and the far
(right) wall takes the light. For a horizontal one — the red — the upper wall is
shaded and the lower wall is lit. There is one lighting model, so there is one
object.

---

## The binding edge — a section, not a set of lines

The complaint that produced this version was exact: gold line, then grey line,
then dark line, then sapphire, reading as four unrelated strips laid beside one
another. The cause was not the colours. It was that **sapphire kept reappearing
between the metals**, which is what makes parallel strokes out of what should be
an assembly.

The edge is now **one channel milled into the plate**, and it is emitted from a
single function in `tools/build-pages.py` so it cannot drift:

```
 PEARL │ crevice · arris │ SILL │ cut │ GOLD RAIL │ return │ PLATINUM │ far wall │ cut line │ SAPPHIRE FIELD
       │       .55       │  .86 │ .19 │   3.40    │   .35  │   2.20   │   .30    │   .22    │
       │  the plate's    │ LIT  │dark │  PROUD    │  LIT   │ RECESSED │   LIT    │  the cut │
       │   own edge      │      │     │           │        │          │          │          │
```

Nine members, **no two the same width**, and **no sapphire anywhere between
them**. Reading it as construction rather than as decoration:

1. **The crevice and the arris.** The plate stands proud of the paper. Where it
   meets the sheet there is a tight warm occlusion line, and immediately inside
   it the plate's own top-left edge catches the key light. That half-millimetre
   is the entire transition from pearl into metal, and it is why the sapphire
   column now reads as a physical plate laid on the sheet rather than as an area
   of blue ink.
2. **The sill is LIT, not dark.** Getting this wrong is what made the previous
   edge look like stripes: a *dark* sapphire band between the paper and the gold
   reads as an outline drawn around the rail, where a *lit* one reads as the
   material the channel was cut into.
3. **The cut, then the gold rail.** 3.4mm — wider than the platinum beside it,
   four times any other member. Gold is the principal metal on this sheet and
   now measures like it.
4. **The return is the whole trick.** The step down from the gold onto the
   platinum floor faces the light square-on, so it is the brightest thing in the
   section. It is **not a gap** — it is a lit chamfer, and it is what welds two
   metals into one assembly. Remove it and you have two lines again.
5. **The platinum floor**, recessed and shaded at its near side by the rail that
   overhangs it, with one off-centre specular line — the only bright thing
   platinum is allowed.
6. **The far wall and the cut line.** The channel rises back to the plate's
   surface and lands on a 0.22mm near-black rule: the finest member in the
   section, and the only one whose job is to separate rather than to be seen.

**There is no gold keyline down the binding edge any more.** The plate's gold
keyline now follows the lower silhouette only. One gold per edge; two would be
the parallel-strokes problem the section exists to solve.

**The channel runs the full height of the plate — through the head as well.**
That is what makes the head and the pier read as one milled object instead of a
banner with a sidebar beside it.

---

## The red channel — the same detail, turned 90°

The red is not a banner laid across the page. It is **the binding section
rotated through a right angle**: a channel let into the sheet, 5.6mm deep, with
a **stainless wall above** (turned away from the light, so it is the darker of
the two) and a **gold wall below** (square to it, so it is the brighter). It
runs from the left trim and **dies against the plate**, where the vertical
section takes over — a cross-member meeting a post.

Under it hangs the register, so announcing the instrument and opening the
correspondence are one gesture. The sheet has **one edge vocabulary used twice**,
not two decorative treatments that happen to share a palette.

---

## The corrections, answered first

**1 · The insignia is never trimmed, and now it is never crowded either.** A
**gold-ringed sapphire medallion**, 46mm across, sits astride the plate's lower
edge. The mark is centred inside it at 19mm with 7mm of clear space and a second
hairline ring within its own bezel, and the medallion in turn holds **10mm of
clear ground to everything around it** — see *The architecture* for the measured
table. When the mark and the layout conflict, **the layout moves**; that rule is
written into the stylesheet beside the measurements, and this round it was
enforced by re-setting the Latin wordmark rather than by nudging the seal.

**2 · `IBROHIM`, not `IBRAHIM`.** My error, in the Latin transliteration only —
it had propagated into this folder and into `docs/letterhead-instrument/`. Fixed
in the sources, the generated pages, the PDFs and the documentation of both. The
**Arabic is unchanged**: `إبراهيم` is the correct Arabic spelling of the name and
the transliteration does not alter it.

**3 · Both hands now sign.** The signature supplied for **الإمام أحمد** is cut
to transparency and set above the principal's gold rule, with Abdullah
Sulaimiy's beneath a finer rule and a narrower block — hierarchy by weight and
width, not by position. Both were matted on **blueness rather than darkness**,
because a darkness threshold eats the fast thin strokes at the ends of a
signature, which is exactly what makes it read as handwritten.

**4 · The Latin wordmark has prominence, and an axis.** `IMAM AHMAD IBROHIM
SULAIMIY` is set on **one line at 13.6pt**, under a sapphire rule, on
**x=24mm** — the same left axis as the register, the field, the
signatures and the foot. The previous sheet put it 4mm off that axis, which is
most of why it read as floating rather than as the Latin half of the identity.

**5 · The gold is back, and it is fresh.** The last gold was a champagne so
restrained it read as warm grey. This ramp is **eleven stops with real white in
it** (`#FFFCE9`, `#FDF4CE`) — struck foil turns the light several times across a
single letter, and its brightest turn is nearly white; three-stop "gold" is just
a yellow gradient. It is placed like jewellery, not spread:

> the medallion's double ring · the insignia itself · the keyline that follows
> the whole plate silhouette · the rule under the name · the two hairlines
> flanking the red inlay · the register hairlines · the QR frame · the signature
> rule · the foot rule

The mark is restruck in the **same ramp** as the page, so the insignia and the
rules are one metal rather than two golds that nearly match.

---

## The architecture

**One plate, one channel, one seal.**

The sapphire is a single milled plate: a **head 56mm deep across the full
sheet** and a **pier 38mm wide down the binding edge** — the *right* edge,
because Arabic decides the binding. They are one shape, cut in one operation,
and the channel that runs through both is what says so. The stepped, chamfered
silhouette of the previous version is gone: it was a flourish competing with the
seal for the job of making the plate interesting, and the seal does that job
better.

**The seal's clear zone is the fixed quantity on this page.** The medallion is
46mm across, centred at (139mm, 56mm), astride the plate's lower edge. Measured
from its circumference:

| to the milled edge section | **10.0mm** |
| to the Latin wordmark | **10.1mm** |
| to the Latin scope line | **10.0mm** |
| to the Arabic name | 26.5mm |

Those are not coincidences — the Latin wordmark was reduced from 14.2pt to
13.6pt and re-tracked, and the identity block moved a millimetre, specifically
to hold the 10mm. **The clear zone is fixed and the typography moves, never the
mark.** Inside its own bezel the insignia has a further 7mm of clear space and a
hairline ring; nothing on the page crosses either.

**Sapphire is layered, not flat** — a radial flood from `#11418F` to `#020B1E`
with the cotton texture in overlay, because printed ink on cotton is never even,
and that unevenness is most of why it reads as ink.

---

## Typography — four voices, and a rule for each

Every line on the sheet belongs to one of three layers, and each layer has
**exactly one fount per script**. Nothing crosses.

| | ARABIC | LATIN |
|---|---|---|
| **IDENTITY** — the office's name and standing | **Reem Kufi** | **Playfair Display 700** |
| **DOCUMENT** — what is written, and to whom | **Scheherazade New** | **EB Garamond** |
| **INSTRUMENT** — references, serials, microtext | Reem Kufi, small | **Inter** |

That table is the answer to a masthead carrying too many competing voices. The
office name, the personal name, the house and the scope are now **one statement
in one voice on one ground**; the Latin identity is its mirror below, in its own
voice on its own ground.

**SAPPHIRE CARRIES THE ARABIC. PEARL CARRIES THE LATIN.** The Arabic identity —
`المكتب الخاص`, the name, `(آل سلام)`, the gold rule and the Arabic scope — is
reversed out of the plate as a single lockup. The Latin identity sits beneath
it on the pearl: `PERSONAL OFFICE` and `ĀL · ES · SALAM` set at the *same* size
and tracking so they bracket the name symmetrically, and the Latin scope closing
the block. One script, one ground, one voice, each.

### The body face was replaced outright

**Amiri is gone.** Set against the alternatives at matched optical size it reads
as a competent *screen* Naskh: even colour, shallow modulation, shallow
descenders — the look of a document produced in an office. Seven faces were set
as full paragraphs of the actual letter, at actual size, on the actual 138mm
measure, and rasterised from the PDF rather than judged on screen.

**Scheherazade New** won, and not narrowly. It is a classical Naskh in the
tradition of the great Cairo and Beirut book founts: pronounced thick/thin
modulation, deep generous bowls, long confident descenders, and a rhythm that
wants air around it. It is the fount of Qur'anic and scholarly Arabic
publishing, and it is what a letter from a scholar's office should be set in.

It carries a large body for its point size, so it is set at **13.4pt, leaded
1.78**, where Amiri sat at 11.2pt — the same apparent size, considerably more
presence. *(Also tried and rejected: Markazi Text — contemporary but flat;
Noto Naskh Arabic — correct and characterless; Lateef — plain; Harmattan — too
light; Alkalami — its connected forms break in this renderer.)*

**The Latin wordmark is Playfair Display 700, not EB Garamond.** A book face's
capitals are narrow and old-style *by design*, and at identity size they read as
reticent — the difference between a name set in a book and a name on a door.
EB Garamond keeps Latin passages inside the letter, where its reticence is
exactly right. **Inter is deliberately impersonal**: that layer of the page is
machinery, not voice.

---

## Correspondence control — a file head, not a form

A form is a column of field names with ruled boxes against them. This is **two
islands on one baseline**, the way a chancery letter is actually laid out:

```
  رقم      PA/2026/09/0017                       إلى
  التاريخ  ٣ ربيع الآخر ١٤٤٨هـ                    سعادة الدكتور حبيب الله يوسف أديوي المحترم
           الموافق ١٧ سبتمبر ٢٠٢٦م                 مدير كلية منار الهدى العالمية
  ──────────────────────── gold hairline ────────────────────────
                    الموضوع   تهنئة بمناسبة نيل درجة الدكتوراه
```

- **The file** sits at the left, flush to 72mm, its labels in a fixed column so
  the reference and the two date lines align. It is dropped by one label line so
  the reference sits **level with the addressee's name** rather than one step
  above it — the two islands share a baseline.
- **The addressee** sits at the right, flush to 162mm, under a small gold `إلى`.
- **No rules between rows.** One gold hairline closes the head; the subject is
  centred beneath it in Kufi.
- `من · FROM` drops in as one more row and nothing else moves.

**A blank sheet is writable; a letter shows no rules at all.** On the template —
and only there — each value sits on a sapphire writing hairline at 42%. The same
register, set with a letter in it, has none.

### The opening is a sequence, not a pile

The register closes on a gold hairline → **9mm** → the **Bismillah** alone,
centred, under a short gold rule of its own → **8mm** → the salutation →
**5mm** → the letter. Each interval is smaller than the last, so the page
visibly settles into the text.

**The responsible-person line was restyled, not translated.** `SP:` and `FOR:`
were office shorthand rather than international convention, so the block now
simply identifies the person and the function, and in an Arabic letter the
**Arabic form leads**:

```
أ. عبد الله السليمي (SMPr · MMJ · Op-Ed)
للعلاقات والاتصالات الداخلية
COMMUNICATIONS & INTERNAL RELATIONS
```

set smaller than the principal's block, as a private office requires — one
office, one function, no invented divisions. An English letter takes
`Abdullah Sulaimiy (SMPr, MMJ, Op-Ed) / For: Communications & Internal
Relations`.

---

## The correspondence itself

The Arabic was rewritten for register, not merely for grammar. **Every
construction in which the writer asked leave to address the recipient is gone.**

| Before | After |
|---|---|
| `أرجو أن تتكرَّموا بالإذن لي بزيارتكم` | `ويطيبُ لي أن أتشرَّف بزيارتكم في موعدٍ يوافق ارتباطاتكم الكريمة` |
| `فإنه ليَسُرُّني ويُشرِّفني` | `فيطيبُ لي` |
| `ولذلك فإننا إذ نهنّئ` | `وأغتنمُ هذه المناسبة لأرفع التهنئة` |

A senior office does not petition for permission to congratulate a colleague.
The warmth and humility proper to Islamic scholarly correspondence are kept; the
subordination is not. The meaning and the facts are unchanged.

**One thing to verify.** The Hijri date `٣ ربيع الآخر ١٤٤٨هـ` is computed from
the *tabular* Islamic calendar and can differ by a day from a sighting
convention. Confirm it against the office's practice before issuing.

---

## Pagination

The continuation sheet is **not** a copy of page one with the same strip pasted
onto it. The pier and the **whole edge section** — channel, rail, return,
platinum floor, cut line — are emitted by the same function at the same
coordinates, so the two sheets are literally the same construction; what page
two drops is the head, not the architecture. A **26mm medallion** keeps the mark
present and complete; the name clears it by 8mm. `REF.` and `CONTINUATION` sit in the
opposite corner. The field opens at **44mm**, so a continuation sheet carries
about **200mm of set type** against the first sheet's **100mm**.

A **blank** sheet cannot know how long a letter will run, so it carries only its
own number (`صفحة ١ · PAGE 1`); the `of N` appears when a letter is set. The
specimen runs to two sheets; the same pattern takes as many as a letter needs.

---

## Security

- **QR** — real, and subordinate. Version 10, 57×57 modules, ECC Q, four-module
  quiet zone: **0.368 mm per module at the 21mm it prints**. It carries a MECARD,
  so a phone gets the office into its contacts. `tools/build-qr.py` prints the
  module size on every build and **decodes its own output at print resolution**.
- **Microtext** at 2.4pt along the foot — a grey rule to the eye, legible under
  a loupe, mush to a photocopier.
- **Latent geometry** — an octagram construction pressed into the field, found
  in raking light rather than seen.
- **Guilloché** — engine-turned line-work inside the sapphire.
- **Watermark** — the insignia, debossed, struck at **86mm** across the optical
  centre of the writing field. On stationery of this class the empty lower half
  of a short letter is not a gap to be closed — it is the most expensive thing
  on the page. It is made deliberate rather than accidental by **occupying** it:
  the latent geometry is centred on the field and the watermark sits at its
  centre, so a reader sees a watermarked panel, not a blank one.
- **Serial** — the reference repeated at the foot of the pier.

No domain is invented anywhere.

---

## Production

Press **PRODUCTION SPEC** on `letterhead.html` (screen only, never prints).

**Substrate.** 120gsm pearl-white cotton; 300gsm for cards.

| Element | Process |
|---|---|
| The plate | **SAPPHIRE FLOOD**, offset |
| The keyline, medallion outer ring, name rule, signature rule, QR frame | **GOLD FOIL** |
| The insignia | **GOLD FOIL**, cut to the strapwork, complete |
| The medallion bezel, the red channel's upper wall | **STAINLESS FOIL** |
| The binding channel's **platinum floor** | **PLATINUM / SILVER FOIL** — a third foil, and it must be visibly cooler and darker than the gold; substituting the stainless here collapses the section back into two competing lines |
| The binding channel's **gold rail** | **GOLD FOIL + BLIND DEBOSS**, in register — 3.4mm, struck into a channel rather than laid flat |
| The classification channel, reference, pips, folio | **RED**, offset — clean and unmuddied; it is a solid, so it wants a full-strength hit, not a screen |
| The register hairlines | **SAPPHIRE**, printed with the flood |
| Guilloché, microtext, latent geometry | Fine-line, *printed* — foil cannot hold a 2.4pt letterform |
| The insignia, page centre | **WATERMARK in the stock**, else blind emboss |
| Body, register, addresses | Letterpress |

**Three foils, and a deboss in register.** Gold, stainless and platinum are
separate passes. A single-die job can have the gold or the silver but not both,
and the binding edge is the place the difference is most visible — the whole
section depends on the platinum reading *darker* than the gold, which a second
strike of the same silver foil will not give you. The gold rail then wants a
**blind deboss in register with its foil**, so the metal genuinely sits below
the plate surface rather than merely being drawn to look as if it does. Quote it
as **four hits on the binding edge**, and ask for the deboss die to be cut
0.05mm inside the foil die so no unstruck paper shows at the channel lip.

**Ink coverage ≈ 26%.** Offset or letterpress, not office digital — a toner
device will band across the plate and drop the microtext. Ask for a wet-proof on
the real stock.

**The standing constraint.** The mark is a raster image at roughly 600dpi at the
size used. **Foil and emboss dies are cut from vector**, so a die cannot be made
from this file — have it traced before ordering foil. Everything not needing a
die is final.

---

## Rebuilding

```bash
pip install fonttools brotli pillow numpy pymupdf qrcode opencv-python-headless

python3 tools/build-typography.py      python3 tools/build-textures.py
python3 tools/cutout-logo.py <src>     python3 tools/build-mark-variants.py
python3 tools/cutout-signature.py <src> <out.png>
python3 tools/build-qr.py              python3 tools/build-pages.py
python3 tools/build-presentation.py
```

Then, always:

```bash
python3 tools/verify-v1.py        # must print ✓ before anything ships
```

### Cutting a v2

A rebuild that changes a released file — even a re-run of
`build-presentation.py`, which re-encodes the JPEG — will fail the manifest.
That is the point: it means *this tree no longer is v1*. Either restore it
(`git checkout docs/letterhead-atelier`) or cut the next version deliberately:

```bash
# 1 · bump VERSION and the changed CONSTANTS in tools/verify-v1.py
python3 tools/verify-v1.py --spec --seal
git commit -am "letterhead v2.0: …"   &&   git tag -a letterhead-v2
```

All three documents are generated from one source — the only way the masthead on
correspondence cannot drift from the masthead on the blank.

### Print bugs found by rasterising the PDFs

1. **`background-clip:text` leaks** — a sliver of unclipped background prints as
   a faint metallic rule under every line. Metallic *type* is a solid with a
   micro-bevel; the eleven-stop ramp is for *blocks*.
2. **Variable fonts are not embedded** — Chrome substitutes a system serif
   silently. Every face is pinned to a static instance before subsetting.
3. **A Latin-only font stack carrying Arabic falls back silently** and embeds
   DejaVu Sans. It recurred here in the signature role line and the folio; every
   mixed-script element now carries an Arabic fallback.
4. **`rotate(-90deg)` with `transform-origin:0 0`** sends the run up and its
   depth to the *right* of the anchor, so a vertical column is placed with
   `left`, never `right`.
