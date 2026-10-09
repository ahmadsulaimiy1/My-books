# The English counterpart

The atelier stationery, handed the other way: the milled sapphire plate, its
pier, the seal and every piece of furniture move to the binding edge at the
**left**, so that a sheet written in English opens the way an English reader
opens it.

    python3 tools/build-en.py          build the three documents
    python3 tools/build-en.py --pdf    build, then print all three

| | |
|---|---|
| `letterhead-en.html` | the blank first sheet |
| `letterhead-en-continuation.html` | a blank continuation sheet |
| `letter-en-tahniah-dr-adewuyi.html` | the Arabic specimen letter, as this office would have written it in English |

---

## What this adds, and what it does not

`assets/letterhead-en.css` is an **overlay**. It introduces no identity, no
palette, no fount and no ornament. It is loaded after the atelier's three
stylesheets and moves things. `../letterhead-atelier` is sealed by
`MANIFEST-v1.sha256`, is not touched, and still verifies —
`python3 ../letterhead-atelier/tools/verify-v1.py` reports 32 files matching.

The insignia is **moved, never flipped**. It is an Arabic calligraphic mark,
and a mirrored mark is a different mark. Its ring, its 10mm clear zone and its
ground are carried across unchanged.

The root stays `dir="rtl"`. The masthead, the seal's ground and the Bismillah
are Arabic and must shape as Arabic; the English parts declare `ltr` where they
sit. Switching the root to carry an English body would put the whole identity
into a direction it was not set in.

## The mirror is geometric. The light is not.

This is the whole of the difficulty, and the reason the nine-member binding
section is re-derived member by member rather than flipped.

**Light is fixed top-left** over the whole sheet — the stationery's first rule.
Two sheets of one identity cannot be lit from two directions. A mechanical
mirror reverses every gradient, which is the same thing as moving the lamp to
the top right: the two sheets would read as a matched pair until they were laid
side by side, and then one of them would look wrong without the reader being
able to say why.

So the *object* is mirrored and the *lamp* is left where it stands. The member
order and every width are the Arabic section's own — offsets are literally
`7.87 − (left + width)` — and nothing is resized. What changes is which face
each member presents to the light, and every one of them changes:

| member | on the Arabic sheet | on the English sheet |
|---|---|---|
| near wall of the channel (0.19) | turned away — almost black | turns **into** the light — a lit hairline |
| far wall (0.30) | takes the light — pale steel | turned away — in shade |
| gold rail (3.40) | shade down the left, specular right | shade down the **right**, specular left |
| return (0.35) | bright by decision | faces the lamp square-on — bright by physics |
| platinum floor (2.20) | overhung from the left | overhung from the **right**; specular line left of centre |
| sill (0.86) | darkens rightward into the channel | darkens **leftward** into the channel |
| cut line (0.22) | separates, not seen | unchanged — the one member whose tone has no side |

Get the two walls backwards and the channel reads as a ridge. That is the
single most consequential swap in the file.

### And the plate now casts a shadow

With the plate at the right, its shadow fell on its own face and was never
seen. With the plate at the left it falls on open paper, so the arris is built
here as what it actually is on this side: sapphire, an occlusion line, and a
soft cast shadow dying into the pearl. It lies *outside* the assembly and fades
to nothing — the section still has nine members. Without it the plate reads as
printed on the sheet rather than standing proud of it.

> While building this, one thing surfaced in the Arabic sheet worth recording:
> `.edge-arris` there resolves to **x −0.20…0.35mm** — it is anchored to the
> sheet rather than to the edge assembly, so the lit arris falls off the left
> trim and never renders; what is seen at the pearl/plate boundary is the sill.
> It is invisible in practice precisely because that edge is the shadow side on
> the Arabic sheet. v1 is locked and has not been altered.

## One axis, at the right margin

On the Arabic sheet the whole masthead ranges to the margin at 24mm with the
seal opposite it at 116mm. The mirror of that is a masthead ranging to the
margin at 186mm with the seal opposite at 48mm — so the Latin identity ranges
**right** on this sheet. It is the one setting that looks unfamiliar written
down and is obviously correct on the page: ranged left, the wordmark would
begin at 48mm and run straight under the seal, and the clear zone is the fixed
quantity on this page.

The Arabic head keeps its ground, its size, its colour and its flush-right
setting. Arabic set flush left is not a mirror of anything.

## What changed beyond the geometry

Four things, and they are the whole list:

1. **The register is set left to right** and its keys are English, in the Latin
   instrument voice (Inter, gold) that already carries every reference, serial
   and folio on this stationery. The addressee leads at the left and the file
   follows at the right — the Arabic chancery order reflected, not rearranged.
2. **The signature leads with the Latin name**, the Arabic form beneath it —
   the same two lines in the same two founts, in the other order. The principal
   signs at the left.
3. **The red channel's contents and the foot are reversed**, so each keeps the
   side it had relative to the plate.
4. **`.letter--en`** — one setting, for the one thing this sheet does that the
   Arabic sheet does not: carry a body of English prose. EB Garamond, already
   the Latin document voice here, leaded for the 138mm measure.

## Transliteration

The embedded Latin cut is subset. It carries `ā ī ū ō` and the accented
Latin-1 range. It does **not** carry the ayn `ʿ`, the hamza `ʾ`, or the dotted
emphatics `ḥ ṣ ḍ ṭ ẓ`.

The trap is sharper than it looks. v1's supplementary face **declares**
`unicode-range: U+0100-024F, …, U+1E00-1EFF, …` but actually contains only
`Ā ā Ī ī Ō ō Ū ū` (plus space, `A`, `Á`/`Ä`, `†`) — thirteen glyphs. An `ḥ` or
an `ṣ` therefore falls inside a range the sheet claims and finds nothing
there, so it is served by whatever face the renderer has to hand. The ayn
(U+02BF) and hamza (U+02BE) sit outside every declared range and do the same.

**This is now fixed, in the overlay, without touching v1.**
`assets/letterhead-en.css` declares four supplementary faces holding exactly
the twelve codepoints v1 lacks — `ʾ ʿ ḌḍḤḥ ṢṣṬṭ Ẓẓ` — with a `unicode-range`
covering only those, so they can never take a glyph the sealed cut already
serves. `verify-v1.py` still reports 32 files matching.

Two things will bite whoever regenerates them:

1. **Google serves EB Garamond and Inter as variable fonts, and Chrome will
   not embed a variable font in a PDF.** It falls back to Type3 glyph
   procedures, which look correct on screen and are not a real embedded
   fount. Instance to static `wght` with `fontTools.varLib.instancer`
   *before* `pyftsubset`. If a rebuild shows `Type3` in the font list, this
   step was missed.
2. **Pass `updateFontNames=True` when instancing**, or the 600 instance keeps
   the PostScript name `EBGaramond-Regular` and the audit below reports
   semibold text as Regular — hiding nothing, but wasting the next person's
   afternoon.

The faces cover **EB Garamond and Inter only**. Playfair Display's latin-ext
cut does not carry these glyphs at all, and Reem Kufi and Scheherazade New
carry no Latin diacritics whatever — not even the macrons. So nothing set in
the masthead name, the signature line (Playfair), or the recipient's name
(Reem Kufi) and role (Scheherazade) may use them.

Arabic dropped into an English body has the same problem from the other side:
`.letter--en` names `"EB Garamond", serif` and has no Arabic face in the
stack. Wrap it in `<span class="ar">`, which names Scheherazade New and
isolates the run so it cannot drag the surrounding Latin punctuation around.

### Audit every letter

```python
import pymupdf, re
d = pymupdf.open("print/letter-en-sinaah-completion.pdf")
faces = {s["font"] for p in d for b in p.get_text("dict")["blocks"]
         for l in b.get("lines", []) for s in l["spans"]}
assert not [f for f in faces if "Type3" in f], "variable font not instanced"
assert not [f for f in faces if re.search(r"DejaVu|Liberation|Times|Noto", f)]
```

A `Type3` entry means step 1 above was missed. A `DejaVu`, `Liberation` or
`Times` entry is a glyph in no house fount at all.

## The correspondence on this sheet

| file | to | ref | sheets |
|---|---|---|---|
| `letter-en-tahniah-dr-adewuyi.html` | Dr Habibullah Yusuf Adewuyi | `PO/2026/09/0017` | 2 |
| `letter-en-sinaah-completion.html` | Alh. (Dr) Zakariya O. Anofi | `PO/2026/10/0023` | 3 |

Both are emitted by `tools/build-en.py`, which owns the plate, the nine-member
section, the pier, the head and the foot in **one** function each, so no letter
can drift from another. The serial is threaded through `plate()`, `pier()` and
`cont_head()`, so each letter stamps its own reference on the pier and on the
continuation head.

`signature_solo()` is for private correspondence: the office's second
signatory countersigns official correspondence and has no place under a
personal letter, so that block carries the principal's hand alone.

### Pagination

The completion letter is **not** split by hand. `tools/build-en.py` renders
every block once, at the real measure and in the real founts, reads its true
height back out of the browser after `document.fonts.ready`, and packs the
groups onto sheets. Three things that measurement gets right and a guess does
not:

* the **Bismillah and its rule** stand inside sheet one's field above the
  first word and eat 19.8mm of its 98mm. Forget them and the sheet overruns
  by exactly the height of the invocation.
* `.signatures` is pinned at `bottom:28mm` and stands ~40mm tall, so a sheet
  carrying the hand can only run to 229mm, not the field's 240mm.
  Continuations are therefore packed against **185mm**, never 196mm, so
  whichever sheet ends up last always has room for the signature.
* groups are **keep-with-next**: a run-in heading can never be orphaned from
  the list it introduces.

### Two faults worth knowing

1. **The specimen letter overruns its own field.** On sheet 1 of
   `letter-en-tahniah-dr-adewuyi.html` the body ends at 249.3mm against a field
   bottom of 245mm — a 4.3mm overrun, invisible against the blank paper below
   but outside the measure. Moving its fourth paragraph to sheet 2 clears it.
   Left alone because it is already-issued correspondence and the break changes
   how the letter reads across the fold.

2. **A short continuation leaves a void.** `.signatures` is pinned to
   `bottom:28mm` while `.field--continued` starts at 44mm, so a continuation
   carrying only a few paragraphs shows a large gap above the hand — 116mm in
   the specimen, 145mm in the completion letter. This is the stationery
   behaving as built, not a fault in either letter.

## Also using this sheet

`../digital-campus-paper` is written in English and loads this overlay, so the
costing paper carries the plate on the left too. Removing that one `<link>` in
its `tools/build-paper.py` returns it to the Arabic hand.
