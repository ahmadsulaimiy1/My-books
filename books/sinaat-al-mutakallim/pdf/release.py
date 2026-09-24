#!/usr/bin/env python3
"""After book_build.py: size the four volumes from the finished book, then write the print wraps
and the studio mockup.

The complete book is one PDF (the digital edition). The printed student book is four volumes, one
per part (Bible, Part Six, ch. 25 §4); each volume's spine is sized from its real page count:
front matter goes with volume one, appendices and back matter with volume four.

    python3 release.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import book_build as BB  # noqa: E402
import cover as CVR  # noqa: E402

WRAPS = HERE.parent / "Sinaat-al-Mutakallim-al-Arabi_Cover-Wraps.pdf"


def part_pages(pdf: Path):
    """First page of each part opener, from the bookmarks (titles «الجزء …» at the top level)."""
    r = PdfReader(str(pdf))
    starts = {}
    for it in r.outline:
        if isinstance(it, list):
            continue
        t = it.title
        for n, word in ((1, "الأول"), (2, "الثاني"), (3, "الثالث"), (4, "الرابع")):
            if t.startswith(f"الجزء {word}"):
                starts[n] = r.get_destination_page_number(it) + 1
    total = len(r.pages)
    vols = {}
    for n in (1, 2, 3, 4):
        a = 1 if n == 1 else starts[n]
        b = (starts[n + 1] - 1) if n < 4 else total
        vols[n] = b - a + 1
    return vols, total


def main():
    font_css = B.static_instances(B.ensure_fonts(BB.BOOK_FONT_CSS, "bookfonts"))
    vols, total = part_pages(BB.OUT)
    print("pages per volume:", vols, "total", total)
    spines = CVR.volume_wraps(font_css, vols, WRAPS, dpi=300)
    print("spines (mm):", spines, "->", WRAPS)
    (HERE / ".cache" / "cover" / "spines.json").write_text(json.dumps(spines), encoding="utf-8")
    import shutil
    shutil.copy(WRAPS, HERE / ".cache" / "cover" / "wraps.pdf")
    import mockup
    mockup.main()


if __name__ == "__main__":
    main()
