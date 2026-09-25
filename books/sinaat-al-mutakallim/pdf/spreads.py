#!/usr/bin/env python3
"""The printed-book test (Bible, ch. 102): the volume laid out as facing pages, as it opens in the hand.

The book is bound on the right. Page 1 stands alone on the left; after it each spread shows an even page on the
right and the odd page after it on the left. The case wrap, if the PDF carries one, is left out.

    python3 spreads.py ../Volume-01_Al-Usul_Final-Proof.pdf      writes ../book/_production/الإخراج/<name>_Spreads.pdf
"""
import sys
from pathlib import Path

import pymupdf

src = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "Volume-01_Al-Usul_Final-Proof.pdf")
out_dir = Path(__file__).resolve().parent.parent / "book" / "_production" / "الإخراج"
out_dir.mkdir(parents=True, exist_ok=True)
d = pymupdf.open(str(src))
# a volume printed with its case wrap has a first page wider than the rest: it is left out; a proof has none
wrap = len(d) > 1 and d[0].rect.width > 1.3 * d[1].rect.width
pages = list(range(1 if wrap else 0, len(d)))
w, h = d[pages[0]].rect.width, d[pages[0]].rect.height
gap = 14
o = pymupdf.open()
spreads = [(None, pages[0])] + [(pages[i], pages[i + 1] if i + 1 < len(pages) else None) for i in range(1, len(pages), 2)]
for right, left in spreads:          # right-hand page first, as the reader meets it
    pg = o.new_page(width=2 * w + gap, height=h)
    pg.draw_rect(pg.rect, color=None, fill=(0.62, 0.62, 0.6))
    if left is not None:
        pg.show_pdf_page(pymupdf.Rect(0, 0, w, h), d, left)
    if right is not None:
        pg.show_pdf_page(pymupdf.Rect(w + gap, 0, 2 * w + gap, h), d, right)
dest = out_dir / (src.stem + "_Spreads.pdf")
o.save(str(dest), garbage=3, deflate=True)
print(dest, len(o), "spreads")
