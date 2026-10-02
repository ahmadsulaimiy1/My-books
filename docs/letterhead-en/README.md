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
Latin-1 range; it does **not** carry the ayn `ʿ`, the turned comma `ʻ`, or the
dotted emphatics `ḥ ṣ ḍ`. Anything outside the repertoire silently falls back
to a system serif in the PDF, so the transliteration is set without them rather
than letting that happen. Check a new letter with:

```python
import pymupdf
d = pymupdf.open("print/letter-en-tahniah-dr-adewuyi.pdf")
{s["font"] for p in d for b in p.get_text("dict")["blocks"]
          for l in b.get("lines", []) for s in l["spans"]}
```

Any `DejaVu`, `Liberation` or `Times` in that set is a glyph that is not in the
subset.

## Also using this sheet

`../digital-campus-paper` is written in English and loads this overlay, so the
costing paper carries the plate on the left too. Removing that one `<link>` in
its `tools/build-paper.py` returns it to the Arabic hand.
