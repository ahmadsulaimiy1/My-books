#!/usr/bin/env python3
"""The covers of the eleven volumes: «المتن والحاشية», the architecture of the scholar's page (Bible, ch. 25 §13).

The artwork is made first (artwork.py: the sapphire and its inks; illumination.py and typeset.py: the rules and
the type; matn.py: front, spine and back of each volume, the page with its matn and its glosses; coverart.py: the
title, the house's seal, the words of the back). This file lays it on the wrap that the binding makes
(covers/printer-spec.json) and writes one plate for each process, all from one painter's list, so that every
plate agrees with every other:

  Cover-NN_<Latin>_PRINT.pdf          CMYK: the sapphire as a raster, panels, type, and the knock-outs under the
                                      cold foil
  Cover-NN_<Latin>_SPOT-SAPPHIRE.pdf  the spot sapphire (PANTONE 2728 C), density as black
  Cover-NN_<Latin>_COLD-FOIL.pdf      gold cold foil laid inline: the glosses' rulings, the device's rulings, the
                                      satin rule within each frame
  Cover-NN_<Latin>_FOIL-GOLD.pdf      hot foil, bright gold: the lit dots of the glosses, the seams and their
                                      jewels, the rules of the frame and the matn, the seal
  Cover-NN_<Latin>_FOIL-PEARL.pdf     hot foil, pearl: the title, the numerals, the names, fine rules
  Cover-NN_<Latin>_FOIL-RUBY.pdf      hot foil, ruby: the lit vowels of the glosses and the nūn's dot, nothing else
  Cover-NN_<Latin>_EMBOSS.pdf         sculpted emboss, depth as grey (black the highest): the matn, the title,
                                      the seams, the jewels, the lit dots
  Cover-NN_<Latin>_DEBOSS.pdf         blind deboss: the matn's own rulings
  Cover-NN_<Latin>_SPOT-UV.pdf        gloss on the soft-touch laminate: the glosses' letters and their unlit dots,
                                      a whisper seen only when the book is tilted; never over foil
  Cover-NN_<Latin>_PRINT-FLAT.pdf     the same cover in CMYK alone, the foils as inks: a paperback or a proof
  Cover-NN_<Latin>_GUIDES.pdf         boards, joints, folds, turn-in, safe areas, the ISBN zone (not for printing)

covers/spines.json keeps the geometry of each wrap (from the final proofs' page counts and printer-spec.json).

    python3 pdf/covers.py            the eleven wraps and the endpapers
    python3 pdf/covers.py 3 7        some volumes
Needs reportlab, shapely, numpy and Pillow. Material proofs and the presentation: pdf/cover_proofs.py.
"""
from __future__ import annotations

import io
import json
import math
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artwork as AW  # noqa: E402
import coverart as CA  # noqa: E402
import frontmatter as FM  # noqa: E402
import geometry as G  # noqa: E402
import illumination as IL  # noqa: E402
import matn as MT  # noqa: E402
from marks import device_svg, house_mark_svg, seal_svg  # noqa: E402,F401  (the book's marks, used by its pages)
import typeset as T  # noqa: E402

OUT = HERE.parent / "covers"
W, H = G.W, G.H                        # 170 × 240 mm
SPEC = json.loads((OUT / "printer-spec.json").read_text(encoding="utf-8"))
CALIPER = SPEC["text_paper"]["caliper_mm_per_leaf"]
BLEED = SPEC["paperback"]["bleed_mm"]
COVER_ALLOW = SPEC["paperback"]["cover_allowance_mm"]
SAFE = 8.0
DPI = 240                               # the substrate's raster (a smooth field); everything else is vector
SIMPLIFY = 0.006                        # mm: far under what any process holds

LATIN = {1: "Al-Usul", 2: "Al-Lisan", 3: "Al-Ibara", 4: "Al-Bayan", 5: "Al-Maqam", 6: "Al-Adab", 7: "Al-Hiwar",
         8: "Al-Majalis-wal-Minbar", 9: "Al-Muassasa", 10: "Al-Tamkin", 11: "Marji-al-Mutakallim"}
PLATES = ("PRINT", "SPOT-SAPPHIRE", "COLD-FOIL", "FOIL-GOLD", "FOIL-PEARL", "FOIL-RUBY", "EMBOSS", "DEBOSS", "SPOT-UV",
          "PRINT-FLAT", "GUIDES")
SPOT_NAME = "PANTONE 2728 C"
SPOT_CMYK = (0.96, 0.69, 0.00, 0.00)    # its process build, for PRINT-FLAT only
FLAT_GOLD = (0.05, 0.22, 0.60, 0.06)
FLAT_COLD = (0.10, 0.28, 0.66, 0.14)
WHITE = (0.0, 0.0, 0.0, 0.0)


# ------------------------------------------------------------------------------------------------ the wrap
def pages(n):
    import pymupdf
    return len(pymupdf.open(str(HERE.parent / f"Volume-{n:02d}_{LATIN[n]}_Final-Proof.pdf")))


def block_mm(n):
    return pages(n) / 2 * CALIPER + (SPEC["endpapers"]["thickness_mm"] if SPEC["binding"] == "case" else 0.0)


def spine_width(n):
    if SPEC["binding"] == "case":
        c = SPEC["case"]
        return round(block_mm(n) + 2 * c["board_mm"] + c["spine_allowance_mm"], 1)
    return round(block_mm(n) + COVER_ALLOW, 1)


def layout(sw):
    """The wrap the binding makes, in mm from its top-left: the margin round it (bleed, or the case's turn-in),
    the boards, the joints, the spine; and where the page-sized artwork of front and back lies on it.
    front | spine | back, as the Arabic book opens."""
    if SPEC["binding"] == "case":
        c = SPEC["case"]
        m, sq, j, sb = c["turn_in_mm"], c["square_mm"], c["joint_mm"], c["board_set_back_mm"]
        bw, bh = W + sq - sb, H + 2 * sq
        fb = (m, m, m + bw, m + bh)
        sp = (fb[2] + j, m, fb[2] + j + sw, m + bh)
        bb = (sp[2] + j, m, sp[2] + j + bw, m + bh)
        return dict(w=bb[2] + m, h=bh + 2 * m, margin=m, front=fb, spine=sp, back=bb, joint=j,
                    front_art=(m + sq, m + sq), back_art=(bb[0] - sb, m + sq), art_top=m + sq)
    b = BLEED
    fb, sp, bb = (b, b, b + W, b + H), (b + W, b, b + W + sw, b + H), (b + W + sw, b, b + 2 * W + sw, b + H)
    return dict(w=2 * W + sw + 2 * b, h=H + 2 * b, margin=b, front=fb, spine=sp, back=bb, joint=0.0,
                front_art=(b, b), back_art=(bb[0], b), art_top=b)


@lru_cache(maxsize=1)
def widths():
    return {v: spine_width(v) for v in range(1, 12)}


def build(n):
    """The wrap of volume n: its layers, its layout and its spine width."""
    sw = widths()[n]
    lay = layout(sw)
    L = AW.Layers()
    P, field = MT.front(n)
    fx, fy = lay["front_art"]
    L.extend(CA.translate(P.L, fx, fy))
    B, bfield = MT.back(n)
    bx, by = lay["back_art"]
    L.extend(CA.translate(B.L, bx, by))
    S = MT.spine(n, sw)
    L.extend(CA.translate(S.L, lay["spine"][0], lay["art_top"]))
    return dict(layers=L, lay=lay, sw=sw, n=n)


# ------------------------------------------------------------------------------------------------ the substrate
def substrate(wrap):
    lay = wrap["lay"]
    L = wrap["layers"]
    sp = lay["spine"]
    inks, t = AW.substrate(lay["w"], lay["h"], DPI, list(L.glow), base=0.26, fields=[(sp[0], sp[2], 0.03)])
    return inks, t


def t_sampler(t, dpi=DPI):
    k = dpi / 25.4
    Hh, Ww = t.shape

    def at(x, y):
        return float(t[min(Hh - 1, max(0, int(y * k))), min(Ww - 1, max(0, int(x * k)))])
    return at


def split_cells(g, cell=6.0):
    """A long thin geometry (a hatch, a ghost ruling) cut into cells, so that each piece can take the colour of the
    sapphire under it."""
    x0, y0, x1, y1 = g.bounds
    if x1 - x0 <= cell and y1 - y0 <= cell:
        return [g]
    out = []
    for gx in np.arange(x0, x1, cell):
        for gy in np.arange(y0, y1, cell):
            piece = g.intersection(box(gx, gy, gx + cell, gy + cell))
            if not piece.is_empty:
                out.append(piece)
    return out


def ops(wrap, at):
    """The painter's list: (geometry, {plate: colour}) in the order they are laid. A colour is a CMYK tuple (for
    PRINT, PRINT-FLAT), a density (for SPOT-SAPPHIRE, the finishing plates), or None (not on that plate)."""
    L = wrap["layers"]
    out = []

    def flat(inks):
        c, m, y, k = inks[:4]
        s = inks[4] if len(inks) > 4 else 0.0
        return tuple(min(1.0, v + s * sv) for v, sv in zip((c, m, y, k), SPOT_CMYK))
    for (g, spec) in L.body:
        if g is None or g.is_empty:
            continue
        if spec[0] == "lift":
            for piece in split_cells(g):
                c = piece.representative_point()
                inks = AW.ramp(at(c.x, c.y) + spec[1])
                out.append((piece, {"PRINT": inks[:4], "SPOT-SAPPHIRE": inks[4], "PRINT-FLAT": flat(inks)}))
        else:
            d, pres = spec[1], spec[2]
            c = g.representative_point()
            inks = AW.ramp(at(c.x, c.y) * (1 - pres) + d * pres)
            out.append((g, {"PRINT": inks[:4], "SPOT-SAPPHIRE": inks[4], "PRINT-FLAT": flat(inks)}))
    for (g, tint) in L.cold:
        out.append((g, {"PRINT": WHITE, "SPOT-SAPPHIRE": 0.0, "COLD-FOIL": 1.0, "PRINT-FLAT": FLAT_COLD}))
    for (g, inks) in L.ink:
        out.append((g, {"PRINT": inks[:4], "SPOT-SAPPHIRE": inks[4], "PRINT-FLAT": flat(inks)}))
    for g in L.champagne:
        out.append((g, {"FOIL-GOLD": 1.0, "PRINT-FLAT": FLAT_GOLD}))
    for g in L.gold:
        out.append((g, {"FOIL-GOLD": 1.0, "PRINT-FLAT": FLAT_GOLD}))
    for g in L.pearl:
        out.append((g, {"FOIL-PEARL": 1.0, "PRINT-FLAT": AW.PEARL_INK[:4]}))
    for g in L.ruby:
        out.append((g, {"FOIL-RUBY": 1.0, "PRINT-FLAT": AW.RUBY_INK[:4]}))
    for (g, lvl) in L.emboss:
        out.append((g, {"EMBOSS": float(lvl)}))
    for g in L.deboss:
        out.append((g, {"DEBOSS": 1.0}))
    for g in L.uv:
        out.append((g, {"SPOT-UV": 1.0}))
    # no varnish over foil
    for g in L.gold + L.champagne + L.pearl + L.ruby:
        out.append((g, {"SPOT-UV": 0.0}))
    return out


# ------------------------------------------------------------------------------------------------ writing
def _path(c, g, h, pt):
    p = c.beginPath()
    n = 0
    for poly in AW.poly_list(g):
        for ring in [poly.exterior] + list(poly.interiors):
            coords = list(ring.coords)
            if len(coords) < 3:
                continue
            p.moveTo(coords[0][0] * pt, (h - coords[0][1]) * pt)
            for (x, y) in coords[1:]:
                p.lineTo(x * pt, (h - y) * pt)
            p.close()
            n += 1
    return p if n else None


def write(wrap, plate, path, title, raster=None):
    from reportlab.lib.colors import CMYKColor
    from reportlab.pdfgen import canvas
    lay = wrap["lay"]
    w, h = lay["w"], lay["h"]
    pt = 72 / 25.4
    c = canvas.Canvas(str(path), pagesize=(w * pt, h * pt), pageCompression=1)
    c.setTitle(title)
    c.setAuthor(FM.PUBLISHER_EN)
    m = lay["margin"]
    c.setTrimBox((m * pt, m * pt, (w - m) * pt, (h - m) * pt))
    c.setBleedBox((0, 0, w * pt, h * pt))
    if raster is not None:
        c.drawImage(raster, 0, 0, w * pt, h * pt)
    for (g, cols) in wrap["ops"]:
        col = cols.get(plate)
        if col is None:
            continue
        if isinstance(col, tuple):
            c.setFillColor(CMYKColor(*col))
        else:
            c.setFillColor(CMYKColor(0, 0, 0, max(0.0, min(1.0, col))))
        p = _path(c, g, h, pt)
        if p is not None:
            c.drawPath(p, stroke=0, fill=1, fillMode=0)
    if plate == "GUIDES":
        guides(c, wrap, pt)
    c.showPage()
    c.save()


def raster_images(inks):
    """The substrate as JPEG images: CMYK for PRINT, the spot as grey, and the process build for PRINT-FLAT."""
    from reportlab.lib.utils import ImageReader
    cmyk = np.clip(inks[..., :4] * 255 + 0.5, 0, 255).astype(np.uint8)
    spot = np.clip((1 - inks[..., 4]) * 255 + 0.5, 0, 255).astype(np.uint8)
    flat = np.clip(inks[..., :4] + inks[..., 4:5] * np.array(SPOT_CMYK, dtype=np.float32), 0, 1)
    flat = np.clip(flat * 255 + 0.5, 0, 255).astype(np.uint8)
    out = {}
    for key, arr, mode in (("PRINT", cmyk, "CMYK"), ("SPOT-SAPPHIRE", spot, "L"), ("PRINT-FLAT", flat, "CMYK")):
        buf = io.BytesIO()
        Image.fromarray(arr, mode).save(buf, "JPEG", quality=90, subsampling=0, dpi=(DPI, DPI))
        buf.seek(0)
        out[key] = ImageReader(buf)
    return out


# ------------------------------------------------------------------------------------------------ the ISBN zone
ISBN = json.loads((OUT / "isbn.json").read_text(encoding="utf-8"))


def isbn_valid(num):
    d = [int(c) for c in num if c.isdigit()]
    return len(d) == 13 and (10 - sum(x * (1 if i % 2 == 0 else 3) for i, x in enumerate(d[:12])) % 10) % 10 == d[12]


def isbn_of(n):
    """(number, printable): printed only once issued (status «official») and with a valid check digit."""
    num = ISBN["volumes"].get(str(n), "")
    return num, bool(num) and ISBN.get("status") == "official" and isbn_valid(num)


_EAN_L = ["0001101", "0011001", "0010011", "0111101", "0100011", "0110001", "0101111", "0111011", "0110111", "0001011"]
_EAN_G = ["0100111", "0110011", "0011011", "0100001", "0011101", "0111001", "0000101", "0010001", "0001001", "0010111"]
_EAN_R = ["1110010", "1100110", "1101100", "1000010", "1011100", "1001110", "1010000", "1000100", "1001000", "1110100"]
_EAN_P = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG", "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13(num, x, y, module=0.33 * 0.9, height=22.85 * 0.9):
    """The EAN-13 symbol of an ISBN as bars (shapely), left quiet zone at x, bars' top at y."""
    d = [int(c) for c in num if c.isdigit()]
    bits = "101" + "".join((_EAN_L if p == "L" else _EAN_G)[v] for p, v in zip(_EAN_P[d[0]], d[1:7])) + "01010" + \
        "".join(_EAN_R[v] for v in d[7:]) + "101"
    guard = set(range(3)) | set(range(45, 50)) | set(range(92, 95))
    bars, i, x0 = [], 0, x + 11 * module
    while i < len(bits):
        if bits[i] == "1":
            j = i
            while j < len(bits) and bits[j] == "1" and ((j in guard) == (i in guard)):
                j += 1
            bars.append(box(x0 + i * module, y, x0 + j * module, y + height + (5 * module if i in guard else 0)))
            i = j
        else:
            i += 1
    return unary_union(bars), (95 + 18) * module


def isbn_zone(wrap):
    """Once the number is issued: a white field, the number, the bars (added to the painter's list)."""
    n = wrap["n"]
    num, printable = isbn_of(n)
    if not printable:
        return
    bx, by = wrap["lay"]["back_art"]
    zx, zy, zw, zh = CA.ISBN_ZONE
    zx, zy = bx + zx, by + zy
    F = CA.faces()
    K100 = (0, 0, 0, 1)
    wrap["ops"].append((box(zx, zy, zx + zw, zy + zh), {"PRINT": WHITE, "SPOT-SAPPHIRE": 0.0, "PRINT-FLAT": WHITE, "SPOT-UV": 0.0}))
    g, _ = T.text(f"ISBN {num}", F.serif, 2.3, x_left=zx + 3.0, base=zy + 3.4, latin=True)
    wrap["ops"].append((g, {"PRINT": K100, "PRINT-FLAT": K100}))
    bars, bw = ean13(num, zx + (zw - (95 + 18) * 0.297) / 2, zy + 4.6)
    wrap["ops"].append((bars, {"PRINT": K100, "PRINT-FLAT": K100}))


def guides(c, wrap, pt):
    """Not for printing: the boards (or the trim), the joints, the spine folds, the turn-in, the safe areas, and
    the ISBN zone kept clear on the back with the state of its number."""
    from reportlab.lib.colors import CMYKColor
    lay = wrap["lay"]
    h = lay["h"]
    c.setStrokeColor(CMYKColor(0, 1, 0, 0))
    c.setLineWidth(0.25)
    xs = sorted({lay["front"][0], lay["front"][2], lay["spine"][0], lay["spine"][2], lay["back"][0], lay["back"][2]})
    for x in xs:
        c.line(x * pt, 0, x * pt, h * pt)
    for y in (lay["front"][1], lay["front"][3]):
        c.line(0, (h - y) * pt, lay["w"] * pt, (h - y) * pt)
    c.setStrokeColor(CMYKColor(1, 0, 0, 0))
    for (ax, ay) in (lay["front_art"], lay["back_art"]):
        c.rect((ax + SAFE) * pt, (h - ay - H + SAFE) * pt, (W - 2 * SAFE) * pt, (H - 2 * SAFE) * pt, stroke=1, fill=0)
    bx, by = lay["back_art"]
    zx, zy, zw, zh = CA.ISBN_ZONE
    c.setStrokeColor(CMYKColor(0, 1, 0, 0))
    c.rect((bx + zx) * pt, (h - by - zy - zh) * pt, zw * pt, zh * pt, stroke=1, fill=0)
    c.setFillColor(CMYKColor(0, 1, 0, 0))
    c.setFont("Helvetica", 5.5)
    n = wrap["n"]
    num, printable = isbn_of(n)
    state = "printed" if printable else ("PROVISIONAL, not printed" if isbn_valid(num) else "PROVISIONAL, INVALID check digit, not printed")
    for k, txt in enumerate(("ISBN / barcode zone", num or "no number", state)):
        c.drawString((bx + zx + 1.5) * pt, (h - by - zy - 6.0 - 4.0 * k) * pt, txt)
    c.drawString((lay["front"][0] + 2) * pt, (h - lay["front"][3] - 4) * pt,
                 f"{SPEC['binding']} binding - spine {wrap['sw']:.1f} mm - joint {lay['joint']:.1f} mm - margin {lay['margin']:.1f} mm"
                 f" - all provisional: covers/printer-spec.json - spot: {SPOT_NAME}")
    if num and isbn_valid(num) and not printable:
        bars, _ = ean13(num, bx + zx + (zw - (95 + 18) * 0.297) / 2, by + zy + 14.0, height=9.0)
        p = _path(c, bars, h, pt)
        if p is not None:
            c.drawPath(p, stroke=0, fill=1)


# ------------------------------------------------------------------------------------------------ the endpapers
def endpapers():
    """The flagship's endpapers (Bible, ch. 25 §5): the sapphire, and on it in its own tone the page of the covers:
    its rulings across the spread, and on them the words of the series, as a text pressed into the colour.
    One spread, the same in every volume."""
    b = BLEED
    w, h = 2 * W + 2 * b, H + 2 * b
    wrap = dict(lay=dict(w=w, h=h, margin=b), n=0, sw=0.0)
    L = AW.Layers()
    F = CA.faces()
    rules, lines = [], []
    words = MT.Words([CA.SERIES] + list(CA.LEAD))
    for y in np.arange(14.0, h - 8.0, MT.GLOSS_LEAD * 1.5):
        rules.append(box(8.0, y + 0.55 - 0.06, w - 8.0, y + 0.55 + 0.06))
        lw = []
        while True:
            w_ = words.take()
            if w_ is None:
                break
            if T.line(" ".join(lw + [w_]), F.amiri4, 3.4).width > w - 16.0:
                words.back()
                break
            lw.append(w_)
        if lw:
            g, _ = T.text(" ".join(lw), F.amiri4, 3.4, x_right=w - 8.0, base=y)
            lines.append(g)
    L.body.append((AW.valid(unary_union(rules)), ("lift", 0.05)))
    L.body.append((AW.valid(unary_union(lines)), ("lift", 0.035)))
    wrap["layers"] = L
    inks, t = AW.substrate(w, h, DPI, [(w / 2, h * 0.45, 140, 0.25)], base=0.24)
    wrap["ops"] = ops(wrap, t_sampler(t))
    ras = raster_images(inks)
    write(wrap, "PRINT", OUT / "Endpapers_PRINT.pdf", f"{FM.TITLE}: endpapers (all volumes)", raster=ras["PRINT"])
    write(wrap, "SPOT-SAPPHIRE", OUT / "Endpapers_SPOT-SAPPHIRE.pdf", f"{FM.TITLE}: endpapers, {SPOT_NAME}", raster=ras["SPOT-SAPPHIRE"])
    return OUT / "Endpapers_PRINT.pdf"


# ------------------------------------------------------------------------------------------------ inside the book
# ------------------------------------------------------------------------------------------------ main
def make(n):
    T.LOG.clear()
    wrap = build(n)
    bad = T.check()
    if bad and not bad[0].startswith("typeset.check: skia"):
        raise SystemExit(f"volume {n}: the cover's type does not match its font:\n  " + "\n  ".join(bad))
    if bad:
        print(bad[0])
    inks, t = substrate(wrap)
    for key in ("layers",):
        pass
    L = wrap["layers"]
    # simplify every geometry once: far under what any plate holds, and the files stay light
    for k in L.__dataclass_fields__:
        if k == "glow":
            continue
        items = getattr(L, k)
        setattr(L, k, [((it[0].simplify(SIMPLIFY, preserve_topology=True),) + it[1:]) if isinstance(it, tuple)
                       else it.simplify(SIMPLIFY, preserve_topology=True) for it in items])
    wrap["ops"] = ops(wrap, t_sampler(t))
    isbn_zone(wrap)
    ras = raster_images(inks)
    for plate in PLATES:
        path = OUT / f"Cover-{n:02d}_{LATIN[n]}_{plate}.pdf"
        write(wrap, plate, path, f"{FM.TITLE}: {FM.volume_line(n)}: {plate}", raster=ras.get(plate))
    lay = wrap["lay"]
    rec = dict(pages=pages(n), binding=SPEC["binding"], caliper_mm_per_leaf=CALIPER, block_mm=round(block_mm(n), 1),
               spine_mm=wrap["sw"], wrap_mm=[round(lay["w"], 1), round(lay["h"], 1)],
               front=[round(v, 2) for v in lay["front"]], spine=[round(v, 2) for v in lay["spine"]],
               back=[round(v, 2) for v in lay["back"]], margin_mm=lay["margin"], joint_mm=lay["joint"],
               shelf_x0=round(sum(widths()[v] for v in range(1, n)), 2), isbn=isbn_of(n)[0], isbn_printed=isbn_of(n)[1],
               plates=list(PLATES), spot=SPOT_NAME,
               status="provisional: from covers/printer-spec.json until the printer confirms it")
    return n, rec


def main(argv):
    vols = [int(a) for a in argv if a.isdigit()] or list(range(1, 12))
    OUT.mkdir(exist_ok=True)
    spines_path = OUT / "spines.json"
    spines = json.loads(spines_path.read_text()) if spines_path.exists() else {}
    lanes = 4 if "--serial" not in argv else 1
    if lanes > 1 and len(vols) > 1:
        from multiprocessing import Pool
        with Pool(min(lanes, len(vols))) as pool:
            results = pool.map(make, vols)
    else:
        results = [make(n) for n in vols]
    for n, rec in results:
        spines[str(n)] = rec
        print(f"volume {n}: spine {rec['spine_mm']} mm, wrap {rec['wrap_mm'][0]} × {rec['wrap_mm'][1]} mm")
    spines_path.write_text(json.dumps(dict(sorted(spines.items(), key=lambda kv: int(kv[0]))), ensure_ascii=False, indent=1))
    if "--no-endpapers" not in argv:
        endpapers()


if __name__ == "__main__":
    main(sys.argv[1:])
