"""Kufam, as used in this book: final and isolated ي with its two dots below the bowl.

Kufam draws ي as ى with two dots stacked vertically after the tail, a Kufic convention that many
readers of the book (and every non-Arab reader) take for «ى» followed by a colon. The font's own
«twodotshorizontalbelow_ar» mark is set under the bowl instead. Nothing else is changed. The
patched faces are renamed (SIL OFL 1.1, §3) and used under the family name "Kufam SMA".
"""
from __future__ import annotations

import re
from pathlib import Path
from urllib.request import url2pathname

from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

FAMILY = "Kufam SMA"
TARGETS = {"uniFEF2": "uniFEF0", "uni064A": "uni0649"}   # yeh (final, isolated) -> its dotless body
BELOW, ABOVE_V = "twodotshorizontalbelow_ar", "twodotsverticalabove_ar"


def bounds(gs, name):
    bp = BoundsPen(gs)
    gs[name].draw(bp)
    return bp.bounds


def patch_file(src: Path) -> Path:
    dst = src.with_name(src.stem + "-sma.woff2")
    if dst.exists():
        return dst
    f = TTFont(src)
    gs = f.getGlyphSet()
    glyf = f["glyf"]
    if BELOW not in f.getGlyphOrder() or not any(t in f.getGlyphOrder() for t in TARGETS):
        f.flavor = "woff2"
        f.save(dst)            # a subset without Arabic yeh: copied unchanged under the new name
        return dst
    dx0, dy0, dx1, dy1 = bounds(gs, BELOW)
    for yeh, body in TARGETS.items():
        if yeh not in f.getGlyphOrder():
            continue
        g = glyf[yeh]
        if not g.isComposite():
            continue
        bx0, by0, bx1, by1 = bounds(gs, body)
        # under the bowl: centre on the bowl's lower half, a dot's height below its lowest point
        gap = (dy1 - dy0) * 0.35
        cx = (bx0 + bx1) / 2 - (dx0 + dx1) / 2
        cy = by0 - gap - dy1
        for c in g.components:
            if c.glyphName == ABOVE_V:
                c.glyphName, c.x, c.y = BELOW, int(round(cx)), int(round(cy))
    for rec in f["name"].names:
        if rec.nameID in (1, 3, 4, 6, 16):
            s = rec.toUnicode()
            rec.string = s.replace("Kufam", "Kufam SMA", 1) if "Kufam SMA" not in s else s
    f.flavor = "woff2"
    f.save(dst)
    return dst


def apply(css: str) -> str:
    """Add "Kufam SMA" faces (patched copies of every Kufam face in the stylesheet)."""
    extra = []
    for block in re.findall(r"@font-face\s*{[^}]*}", css):
        if not re.search(r"font-family:\s*'?Kufam'?;", block):
            continue
        url = re.search(r"url\((file://[^)]+)\)", block).group(1)
        src = Path(url2pathname(url[len("file://"):]))
        dst = patch_file(src)
        extra.append(block.replace("'Kufam'", f"'{FAMILY}'").replace("Kufam;", f"'{FAMILY}';").replace(url, dst.as_uri()))
    return css + "\n" + "\n".join(extra)
