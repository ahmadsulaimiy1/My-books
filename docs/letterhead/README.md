# المكتب الخاص — Letterhead

**الإمام أحمد بن إبراهيم السليمي (آل سلام)**
Personal Office · Academic Development · Islamic Da‘wah · International Relations · Private & Civic Affairs

A bespoke A4 letterhead for a private executive office: three developed concepts,
one refined into a working stationery set, with a production specification for
foil, emboss and watermark.

---

## The set

| File | What it is |
|---|---|
| `letterhead.html` | **The letterhead.** The blank first sheet. Carries a screen-only **PRODUCTION SPEC** toggle. |
| `letterhead-continuation.html` | The **second sheet**, for letters that run past the first. |
| `letter-congratulation-dr-habib.html` | A **letter set on the stationery** — specimen and working template. |
| `concept-i-imperial-scholar.html` | Concept I — the direction that was chosen and refined. |
| `concept-ii-diplomatic-chancery.html` | Concept II — held for comparison. |
| `concept-iii-heritage-luxe.html` | Concept III — held for comparison. |
| `print/*.pdf` | **Print-ready PDFs**, A4, fonts embedded. Hand these to a printer. |
| `assets/letterhead.css` | The shared stylesheet driving the production set. |
| `assets/letterhead-typography.css` | Generated. Every typeface, subset and embedded. |
| `assets/insignia-logo.png` | The office mark, cut to transparency. |
| `assets/insignia-logo-grey.png` | The same mark desaturated, for the watermark and B/W work. |
| `tools/` | The two build scripts. See **Rebuilding**. |

Open any `.html` in a browser. Print at **A4, 100% scale, margins: none,
background graphics: on** — or simply print the PDFs.

---

## The three concepts, and why Concept I was chosen

**I · IMPERIAL SCHOLAR** — monumental and axial. The insignia crowns the page,
the Arabic name is the single centre of gravity, every rule is struck to the
same axis. The register of a commemorative inscription.

**II · DIPLOMATIC CHANCERY** — asymmetric and bilingual by column. A ruled
chancery frame, corner brackets, a royal ribbon threaded on a gold hairline down
the *right* edge (the Arabic reading order decides the binding edge, not Latin
filing convention), and a three-post footer register.

**III · HERITAGE LUXE** — a charcoal cartouche across the head with a girih
lattice worked faintly into it, the identity reversed out in ivory and gold. The
only one of the three where the gold is *lit* rather than merely printed.

**Concept I was chosen**, because the brief's first requirement is that the
Arabic name read as the visual centre of authority. Concept II's two-column
split gives the name only a share of the page. Concept III is the most
immediately striking, but a dark band at the head makes the sheet look like an
institution's, and heavy ink coverage limits it to offset — it is the wrong
register for a *personal* office and the most expensive to print well.

### What the refinement changed

- The masthead was struck to a single **4mm module** — every gap is a multiple
  of it, so the eye reads one system rather than a stack of decisions.
- The masthead was **compressed from ~145mm to ~114mm**. A masthead that eats
  half the sheet is a poster, not stationery; the writing field now runs
  116–256mm, enough for a full letter and its signature.
- The name is set at **one weight**, the way the insignia lockup sets it. Only
  the house takes gold, and only at the same size.
- The flanking hairlines gained **lozenge terminals**, so they read as drawn
  rules rather than as underscores.
- **Chancery corner ticks** mark the type area — Concept II's discipline without
  caging the page in a box.
- The English scope is set on **two balanced lines** at a readable size instead
  of one cramped line.
- A **continuation sheet** was added. Luxury stationery is a set, not a page.

---

## Identity

### The mark

The supplied insignia — the interlaced **أ / A** and **س / S** in gold strapwork
over a deep royal inlay, with the faceted lozenge above — is used as given. It
was cut off its background by hue rather than by brightness: the inlay is the
only *cool* thing on the sheet and the gold the only *saturated* thing, while
the paper and the drop shadow are both warm and flat. Luminance alone cannot
tell deep navy from deep shadow, which is why a plain threshold leaves a ragged
halo. See `tools/cutout-logo.py`.

### Colour

| | Hex | Where |
|---|---|---|
| Deep charcoal | `#222222` | the name, body copy, the Concept III cartouche |
| Royal gold | `#C5A773` | rules, lozenges, the mark's strapwork |
| Gold, deep | `#9C7F4E` | the house name, small caps, rule terminals |
| Royal blue | `#002FAB` | the thread beneath the register; the Concept II ribbon |
| Warm ivory | `#FCFAF5` → `#F4EFE3` | the sheet |

Royal blue is used **once per sheet**, as a thread. It is an accent that signs
the page, not a colour the design is built on — a full-height blue bar reads as
a highlighter, which is why Concept II's first draft was reworked.

### Typography

| Face | Role |
|---|---|
| **Amiri** | Arabic serif — the scholarly voice and the principal identity |
| **Reem Kufi** | Arabic geometric — structural micro-labels only |
| **Cinzel** | Latin display — the Roman-inscription register |
| **Source Serif 4** | Latin text — body copy, contact block, micro-typography |

Four faces, each with one job. All are embedded in the page as subset WOFF2, so
the stationery renders identically offline, at a print shop, and inside an
exported PDF, with nothing to install.

Two decisions worth keeping if this is ever rebuilt:

- **Faces are pinned to static instances.** Chrome's print-to-PDF will not embed
  a variable font — it substitutes a system serif silently, so a PDF that looks
  perfect on screen reaches the printer set in Liberation Serif.
- **The Arabic faces also carry a Latin cut.** Arabic copy is full of Latin
  codepoints — the parentheses around (آل سلام), the slashes in a reference
  number, an em dash in a folio. Without them those glyphs alone drop to a
  system serif.

Arabic coverage is the **whole Arabic block**, not just the masthead wording, so
the template sets whatever correspondence is written on it.

---

## Production specification

Open `letterhead.html` and press **PRODUCTION SPEC** (screen only; it never
prints) to see these zones marked on the sheet itself.

**Substrate.** 120gsm ivory wove for correspondence; 300gsm for the calling
card. A laid or lightly textured stock suits the design — the page carries a
faint laid tooth that the real thing will simply take over.

| Element | Process | Notes |
|---|---|---|
| The insignia, masthead | **GOLD FOIL** on the strapwork + **BLIND EMBOSS** on the whole mark | Foil first, then emboss into register. The lozenge above takes foil only. |
| The Arabic name | **DEBOSS**, charcoal letterpress | Deep enough to feel; a scholar's name should be felt through the sheet. |
| Rules, lozenges, terminals | **GOLD FOIL** | One die for the head rule and the foot rule together. |
| The royal thread | Letterpress, royal blue | 15 × 0.4mm. A single hit. |
| The insignia, page centre | **WATERMARK in the stock** | A true watermark if the mill will make one; otherwise a second blind emboss. |
| English small caps, contact | Letterpress, charcoal | No foil — the register should recede. |
| Arabic foot line | Letterpress, deep gold | Optional; it may also be foiled with the foot rule. |

**One honest constraint.** The mark as supplied is a **raster image**. It prints
beautifully — it sits on the sheet at roughly 600dpi and the PDFs are ready to
go — but **foil dies and emboss dies are cut from vector artwork**, so a die
cannot be made from this file. Before ordering foil or emboss, have the mark
traced to vector (or supply the original vector if the designer holds it). For
everything that does not involve a die — digital printing, offset, PDF
correspondence, email — the files here are final as they stand.

### The four reproductions

The set is built so the identity survives all four:

1. **Full luxury colour** — as designed.
2. **Premium printed stationery** — foil, emboss and deboss per the table above.
3. **Black and white** — `assets/insignia-logo-grey.png` is contrast-boosted so
   the strapwork still separates on a photocopier or fax.
4. **Digital PDF** — `print/`. A4, fonts embedded, no external dependency.

---

## Writing a letter on it

Copy `letter-congratulation-dr-habib.html`, keep the structure, replace the
field. The structure is:

```html
<div class="field">
  <div class="refline"> الرقم … / التاريخ … </div>
  <p class="addressee"> … </p>
  <div class="letter">
    <p class="salaam"> … </p>
    <p> … </p>
  </div>
  <div class="signature"> … </div>
</div>
```

The field is bounded at **116mm / 40mm**, measured against the printed sheet:
the masthead clears at 114mm and the register begins at 264.6mm. A body longer
than roughly **140mm of set type** belongs on `letterhead-continuation.html`.

---

## Rebuilding

```bash
pip install fonttools brotli pillow numpy

python3 tools/build-typography.py   # → assets/letterhead-typography.css
python3 tools/cutout-logo.py        # → assets/insignia-logo.png
```

`build-typography.py` fetches each face, pins it to a static instance, subsets
it, and embeds it as base64 WOFF2. `cutout-logo.py` cuts the supplied mark off
its background. Neither needs to be re-run unless the faces or the mark change.

To regenerate the PDFs:

```bash
for f in letterhead letterhead-continuation letter-congratulation-dr-habib \
         concept-i-imperial-scholar concept-ii-diplomatic-chancery concept-iii-heritage-luxe; do
  chromium --headless --no-pdf-header-footer --print-to-pdf="print/$f.pdf" "$f.html"
done
```
