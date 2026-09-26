#!/usr/bin/env python3
"""The press masters of the eleven volumes: the final proofs made ready for the printing press.

The final proofs (volume.py) are built for the screen as much as for the press: every colour in RGB, the paper's
cream drawn as a tint over each page, and the page cut exactly at its trim. A press needs otherwise, and this is
what a prepress house does to them:

  * the colour into CMYK through one map of the book's own small palette (38 colours), so that every build is
    deliberate: the text's near-black and every near-neutral dark becomes black alone (the body 100K, so that
    small type never rests on four registered plates); the other colours by grey-component replacement
    (gold, ruby, sapphire and their tints); the gradients likewise;
  * the paper's cream removed: the stock gives the tone, not a flat screen over every page;
  * 3 mm of bleed round every page, the trim and bleed boxes set, and whatever runs to the trim carried on
    into the bleed, so that the guillotine leaves no hairline of white.

    python3 pdf/printmaster.py           the eleven, into print/
    python3 pdf/printmaster.py 3 7       some volumes

Writes print/Volume-NN_<Latin>_Press-Master.pdf and print/colour-map.tsv (every RGB colour of the book and the
CMYK it prints as, for the printer to confirm). The printer's preflight (PDF/X certification against their
press profile) remains theirs; this makes the files ready for it.
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "print"
BLEED_MM = 3.0
PT = 72 / 25.4
PAPER = (0.973, 0.965, 0.945)             # the screen's paper tint: the stock gives it on press
NUM = r"(-?\d*\.?\d+)"
RGB_OP = re.compile(r"(?<![\w.])" + NUM + r"\s+" + NUM + r"\s+" + NUM + r"\s+(rg|RG)(?![\w])")
USED = {}


def cmyk(r, g, b):
    """One RGB colour of the book as it prints."""
    if max(abs(r - PAPER[0]), abs(g - PAPER[1]), abs(b - PAPER[2])) < 0.004:
        return (0.0, 0.0, 0.0, 0.0)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    chroma = max(r, g, b) - min(r, g, b)
    if lum < 0.16 and chroma < 0.06:                 # the text's black: black alone, full
        return (0.0, 0.0, 0.0, 1.0)
    if chroma < (0.15 if lum < 0.65 else 0.035):     # a neutral: black alone, so small type holds registration (the
        # running heads' slate, 7.8pt on every page, is one: the Bible 22 §6.4 keeps small type off built colour)
        return (0.0, 0.0, 0.0, round(1.0 - lum, 3))
    k = 1.0 - max(r, g, b)                            # a colour: grey-component replacement
    c, m, y = ((1.0 - v - k) / (1.0 - k) for v in (r, g, b))
    return tuple(round(max(0.0, v), 3) for v in (c, m, y, k))


def _fmt(v):
    s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def convert_stream(data: bytes) -> bytes:
    s = data.decode("latin-1")

    def sub(m):
        rgb = tuple(float(m.group(i)) for i in (1, 2, 3))
        c = cmyk(*rgb)
        USED[tuple(round(v, 3) for v in rgb)] = c
        op = "k" if m.group(4) == "rg" else "K"
        return " ".join(_fmt(v) for v in c) + " " + op
    return RGB_OP.sub(sub, s).encode("latin-1")


def convert_shading(obj: str) -> str:
    def arr(m):
        vals = [float(v) for v in m.group(2).split()]
        if len(vals) != 3:
            return m.group(0)
        return f"/{m.group(1)}[" + " ".join(_fmt(v) for v in cmyk(*vals)) + "]"
    obj = re.sub(r"/(C0|C1|Background)\s*\[([^\]]*)\]", arr, obj)
    return obj.replace("/DeviceRGB", "/DeviceCMYK")


def to_cmyk(doc):
    forms = set()
    for x in range(1, doc.xref_length()):
        try:
            o = doc.xref_object(x, compressed=True)
        except Exception:
            continue
        if "/ShadingType" in o:
            doc.update_object(x, convert_shading(o))
        if doc.xref_is_stream(x) and "/Subtype/Form" in o.replace(" ", ""):
            forms.add(x)
    for pg in doc:
        for x in pg.get_contents():
            forms.add(x)
    for x in forms:
        doc.update_stream(x, convert_stream(doc.xref_stream(x)))


def with_bleed(src, orig):
    """The pages on sheets 3 mm larger each way, the trim and bleed boxes set, what touches the trim carried on
    (its colour read from the original page, where it is still the book's RGB, and mapped like the rest)."""
    b = BLEED_MM * PT
    out = pymupdf.open()
    for i, pg in enumerate(src):
        w, h = pg.rect.width, pg.rect.height
        np_ = out.new_page(width=w + 2 * b, height=h + 2 * b)
        for d in orig[i].get_drawings():
            f = d.get("fill")
            if not f or len(f) != 3:
                continue
            f = cmyk(*f)
            if not any(f):
                continue
            r = d["rect"]
            ext = []
            if r.x0 <= 0.6:
                ext.append(pymupdf.Rect(0, r.y0 + b, b + 0.5, r.y1 + b))
            if r.x1 >= w - 0.6:
                ext.append(pymupdf.Rect(w + b - 0.5, r.y0 + b, w + 2 * b, r.y1 + b))
            if r.y0 <= 0.6:
                ext.append(pymupdf.Rect(r.x0 + b, 0, r.x1 + b, b + 0.5))
            if r.y1 >= h - 0.6:
                ext.append(pymupdf.Rect(r.x0 + b, h + b - 0.5, r.x1 + b, h + 2 * b))
            for e in ext:
                np_.draw_rect(e, color=None, fill=f, width=0, overlay=False)
        np_.show_pdf_page(pymupdf.Rect(b, b, b + w, b + h), src, i)
        np_.set_bleedbox(np_.rect)
        np_.set_trimbox(pymupdf.Rect(b, b, b + w, b + h))
    return out


def make(n):
    src = sorted(glob.glob(str(ROOT / f"Volume-{n:02d}_*_Final-Proof.pdf")))[0]
    name = Path(src).name.replace("_Final-Proof.pdf", "_Press-Master.pdf")
    doc = pymupdf.open(src)
    to_cmyk(doc)
    out = with_bleed(doc, pymupdf.open(src))
    meta = dict(doc.metadata or {})
    meta.update(subject="Press master: CMYK (palette map in colour-map.tsv), 3 mm bleed, trim and bleed boxes set",
                producer="pdf/printmaster.py")
    out.set_metadata({k: v for k, v in meta.items() if k in ("title", "author", "subject", "keywords", "creator", "producer")})
    OUT.mkdir(exist_ok=True)
    out.save(str(OUT / name), garbage=3, deflate=True)
    return name, len(out)


def main(argv):
    vols = [int(a) for a in argv if a.isdigit()] or list(range(1, 12))
    for n in vols:
        name, pages = make(n)
        print(f"volume {n}: {name}, {pages} pages")
    rows = ["rgb\tcmyk\tas"]
    for rgb, c in sorted(USED.items(), key=lambda kv: -sum(kv[0])):
        kind = "removed (the stock's tone)" if not any(c) else ("black alone" if c[:3] == (0.0, 0.0, 0.0) else "process")
        rows.append(f"{' '.join(_fmt(v) for v in rgb)}\t{' '.join(str(round(v * 100)) for v in c)}\t{kind}")
    (OUT / "colour-map.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
