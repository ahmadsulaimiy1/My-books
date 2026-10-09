# The stationery — two versions, one identity

المكتب الخاص · الإمام أحمد بن إبراهيم السليمي (آل سلام)
PERSONAL OFFICE · IMAM AHMAD IBROHIM SULAIMIY · ĀL-ES-SALAM

Same design, same palette, same seal, same four type voices. They differ in one
thing: which edge the milled sapphire plate binds on. Save Arabic
correspondence against the Arabic version and English correspondence against
the English version; they are not alternatives to choose between, they are the
two hands of one letterhead.

| | version | plate binds | use it for |
|---|---|---|---|
| **AR** | [`letterhead-atelier/`](letterhead-atelier/) | **right** edge | Arabic letters — Arabic reads right to left, so the binding is at the right |
| **EN** | [`letterhead-en/`](letterhead-en/) | **left** edge | English letters and English documents |

---

## The Arabic version — `letterhead-atelier/`

The master. Released and **sealed as `letterhead v1.0`**: `SPEC-v1.md` freezes
the specification, `MANIFEST-v1.sha256` hashes all 32 released files, and
`tools/verify-v1.py` fails by name if anything moves.

    cd letterhead-atelier && python3 tools/verify-v1.py
      ✓ letterhead v1.0 — locked, and this tree matches it.

Its files keep their original names — `letterhead.html`, not
`letterhead-ar.html` — because renaming them would break the manifest. This
index is here so the absence of an `-ar` suffix is never read as ambiguity: if
a file is in `letterhead-atelier/`, it is the Arabic version.

| | |
|---|---|
| `print/letterhead.pdf` | blank first sheet |
| `print/letterhead-continuation.pdf` | blank continuation sheet |
| `print/letter-tahniah-dr-adewuyi.pdf` | two-sheet specimen letter |

Rebuild with `python3 tools/build-pages.py`.

## The English version — `letterhead-en/`

The counterpart. Every file carries `-en`. It adds no identity, no palette, no
fount and no ornament — `assets/letterhead-en.css` is an overlay loaded after
the atelier's own stylesheets, which are read from `letterhead-atelier/` and
never modified.

| | |
|---|---|
| `print/letterhead-en.pdf` | blank first sheet |
| `print/letterhead-en-continuation.pdf` | blank continuation sheet |
| `print/letter-en-tahniah-dr-adewuyi.pdf` | the same specimen letter, in English |

Rebuild with `python3 tools/build-en.py --pdf`.

**The mirror is geometric; the light is not.** Light stays fixed at the top
left on both sheets — two sheets of one identity cannot be lit from two
directions — so the nine-member binding section is re-derived member by member
rather than flipped. The full reasoning is in that directory's README.

## Documents set on the stationery

| | language | sheet | |
|---|---|---|---|
| [`digital-campus-paper/`](digital-campus-paper/) | English | EN — plate at the left | Sultan Hanafi Royal Schools Digital Campus costing and implementation paper, 19 sheets |

An English document goes on the English sheet. If one should ever carry the
Arabic hand instead, drop the `letterhead-en.css` link from its build script.

## The earlier explorations

`letterhead/`, `letterhead-flagship/` and `letterhead-instrument/` are the
three directions explored before v1, kept unchanged as the record of how it was
arrived at. Neither version is built from them.
