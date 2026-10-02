#!/usr/bin/env python3
"""A mark of vocalisation stranded below the text block.

When a page opens on a line whose mark rises above the top of the text block (a shadda over a heading in Changa,
a tanwin over a table's first cell), Chromium paints that mark's ink a second time at the foot of the page before:
the page that carries the line prints it whole, and the page before carries a lone shadda or tanwin just under its
last line, a speck of gold or ink with no letter beneath it. This finds such a mark (a harakah, tanwin, shadda,
sukun or dagger alif with no letter of its own under it) and removes it from the page; it never touches a letter,
and a mark that sits on a letter is never lone. volume.py runs it on every final; preflight.py fails on any left.

    python3 pdf/strays.py N         clean the final of volume N in place (what volume.py does at its last save)
    python3 pdf/strays.py N --list  list them only
"""
from __future__ import annotations

import glob
import sys
from pathlib import Path

import pymupdf

MARKS = set(range(0x064B, 0x0653)) | {0x0670}
ROOT = Path(__file__).resolve().parent.parent


def find(doc):
    """[(page index, the mark, its centre x, its box)] for every mark with no letter beneath it."""
    out = []
    for i, page in enumerate(doc):
        bases, marks = [], []
        for t in page.get_texttrace():
            for c in t["chars"]:
                (marks if c[0] in MARKS else bases).append((c[3], t["size"], c[0]))
        for (x0, y0, x1, y1), size, ch in marks:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if not any(b[0] - 3 <= cx <= b[2] + 3 and abs((b[1] + b[3]) / 2 - cy) < size * 1.2 for b, _, _ in bases):
                out.append((i, chr(ch), cx, pymupdf.Rect(x0, y0, x1, y1)))
    return out


def clean(doc):
    """Remove the lone marks; letters, rules and pictures stay as they are. Returns what was removed."""
    found = find(doc)
    for i, ch, cx, r in found:
        doc[i].add_redact_annot(pymupdf.Rect(cx - 1.5, r.y0, cx + 1.5, r.y1), fill=False)
    for i in sorted({f[0] for f in found}):
        doc[i].apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_NONE, graphics=pymupdf.PDF_REDACT_LINE_ART_NONE,
                                text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    return found


def main(argv):
    n = int(argv[0])
    path = Path(sorted(glob.glob(str(ROOT / f"Volume-{n:02d}_*_Final-Proof.pdf")))[0])
    doc = pymupdf.open(str(path))
    if "--list" in argv:
        for i, ch, cx, r in find(doc):
            print(f"page {i + 1}: {ch!r} at x {cx:.1f}, y {r.y0:.1f}")
        return
    found = clean(doc)
    if found:
        tmp = path.with_suffix(".tmp.pdf")
        doc.save(str(tmp), garbage=4, deflate=True, deflate_fonts=True)
        doc.close()
        tmp.replace(path)
    print(path.name, len(found), "lone marks removed", sorted({i + 1 for i, *_ in found}))


if __name__ == "__main__":
    main(sys.argv[1:])
