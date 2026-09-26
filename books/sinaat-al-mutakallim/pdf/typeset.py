#!/usr/bin/env python3
"""Arabic type as outlines for the covers: shaped with HarfBuzz (lettering.py), drawn from the font's outlines,
returned as path segments and as shapely geometry (mm, y downward), so that the covers carry no fonts and the
type can be cut, embossed and foiled like any other part of the artwork."""
from __future__ import annotations

import re

from shapely.geometry import Polygon

import cover2 as C2
import lettering as L

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


_TOK = re.compile(r"[MLHVQCZmlhvqcz]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def parse(d):
    """SVG path data (absolute commands, as fontTools and this module write them) as segments:
    ('M', x, y), ('L', x, y), ('C', x1, y1, x2, y2, x, y), ('Z',). Quadratics become cubics."""
    toks = _TOK.findall(d)
    out, i, cmd = [], 0, None
    cx = cy = sx = sy = 0.0

    def num():
        nonlocal i
        v = float(toks[i])
        i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if t.isalpha():
            cmd = t
            i += 1
            if cmd in "Zz":
                out.append(("Z",))
                cx, cy = sx, sy
                continue
        elif cmd is None:
            raise ValueError(d[:40])
        if cmd == "M":
            cx, cy = num(), num()
            sx, sy = cx, cy
            out.append(("M", cx, cy))
            cmd = "L"
        elif cmd == "L":
            cx, cy = num(), num()
            out.append(("L", cx, cy))
        elif cmd == "H":
            cx = num()
            out.append(("L", cx, cy))
        elif cmd == "V":
            cy = num()
            out.append(("L", cx, cy))
        elif cmd == "Q":
            qx, qy, x, y = num(), num(), num(), num()
            out.append(("C", cx + 2 / 3 * (qx - cx), cy + 2 / 3 * (qy - cy), x + 2 / 3 * (qx - x), y + 2 / 3 * (qy - y), x, y))
            cx, cy = x, y
        elif cmd == "C":
            x1, y1, x2, y2, x, y = (num() for _ in range(6))
            out.append(("C", x1, y1, x2, y2, x, y))
            cx, cy = x, y
        else:
            raise ValueError(f"unsupported command {cmd}")
    return out


def xf(segs, a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
    """Apply the affine map (x, y) -> (a x + c y + e, b x + d y + f)."""
    def p(x, y):
        return a * x + c * y + e, b * x + d * y + f
    out = []
    for s in segs:
        if s[0] == "Z":
            out.append(s)
        elif s[0] == "C":
            out.append(("C", *p(s[1], s[2]), *p(s[3], s[4]), *p(s[5], s[6])))
        else:
            out.append((s[0], *p(s[1], s[2])))
    return out


def move(segs, dx, dy):
    return xf(segs, e=dx, f=dy)


def bbox(segs):
    xs = [v for s in segs if s[0] != "Z" for v in s[1::2]]
    ys = [v for s in segs if s[0] != "Z" for v in s[2::2]]
    return min(xs), min(ys), max(xs), max(ys)


# ------------------------------------------------------------------------------------------------ type
class Face:
    """One family and weight across its subset files (Google Fonts splits a face by unicode-range): each
    character is set from the first file that has it, the Arabic file first."""

    def __init__(self, css, family, weight):
        self.files = family_files(css, family, weight)
        self.path = self.files[0]
        self.cmaps = [set(L.load(f)[1].getBestCmap()) for f in self.files]

    def which(self, ch):
        o = ord(ch)
        for i, cm in enumerate(self.cmaps):
            if o in cm:
                return i
        return 0


def family_files(css, family, weight):
    from urllib.request import url2pathname
    arabic, rest = [], []
    for block in re.findall(r"@font-face\s*{(.*?)}", css, flags=re.S):
        fam = re.search(r"font-family:\s*'?\"?([^;'\"]+)", block).group(1).strip()
        wt = re.search(r"font-weight:\s*(\d+)", block)
        if fam != family or (wt and int(wt.group(1)) != weight):
            continue
        rng = re.search(r"unicode-range:\s*([^;]+);", block)
        path = url2pathname(re.search(r"url\(file://([^)]+)\)", block).group(1))
        (arabic if rng and ("U+0600" in rng.group(1) or "U+600" in rng.group(1)) else rest).append(path)
    if not arabic + rest:
        raise KeyError(f"{family} {weight}")
    return arabic + rest


class Faces:
    def __init__(self):
        self.css = C2.fonts()
        f = lambda fam, w: Face(self.css, fam, w)   # noqa: E731
        self.kufi6, self.kufi5 = f("Kufam SMA", 600), f("Kufam SMA", 500)
        self.changa4, self.changa5 = f("Changa", 400), f("Changa", 500)
        self.sch4, self.sch6 = f("Scheherazade New", 400), f("Scheherazade New", 600)
        self.amiri4, self.amiri7 = f("Amiri", 400), f("Amiri", 700)
        self.serif = Face(self.css, "Source Serif 4", 400)


KF = {"kern": True, "calt": True, "liga": False}
FIG = {"kern": True, "liga": True, "calt": True, "pnum": True}   # numerals for display: the font's proportional figures


_DIGITS = re.compile(r"[0-9٠-٩](?:[0-9٠-٩–/.]*[0-9٠-٩])?")


class Composite:
    """Runs set from different files of one face, laid in reading order."""

    def __init__(self, parts, width):
        self.segs = [seg for part in parts for seg in part]
        self.width = width
        self.bounds = bbox(self.segs) if self.segs else (0, 0, width, 0)


def line(text, face, size, features=None, digits=False, latin=False, tracking=0.0):
    if digits:
        text = text.translate(AR)
        features = features or FIG           # «١١» set as figures, not as a table's columns
    elif not latin:
        # the line is shaped right to left: a run of digits is laid in reverse first, so that it reads left
        # to right as the bidi algorithm would set it
        text = _DIGITS.sub(lambda m: m.group(0)[::-1], text)
    direction = "ltr" if (digits or latin) else "rtl"
    if isinstance(face, str):
        return L.Line(text, face, size, features=features, tracking_mm=tracking, direction=direction)
    runs = []                               # (file index, chars); a space goes with the run it sits in
    for ch in text:
        i = runs[-1][0] if (ch == " " and runs) else face.which(ch)
        if runs and runs[-1][0] == i:
            runs[-1][1].append(ch)
        else:
            runs.append((i, [ch]))
    if len(runs) == 1:
        return L.Line(text, face.files[runs[0][0]], size, features=features, tracking_mm=tracking, direction=direction)
    shaped = [L.Line("".join(t), face.files[i], size, features=features, tracking_mm=tracking, direction=direction)
              for i, t in runs]
    total = sum(ln.width for ln in shaped)
    parts, x = [], (total if direction == "rtl" else 0.0)
    for ln in shaped:
        if direction == "rtl":
            x -= ln.width
            parts.append(move(parse(ln.d), x, 0))
        else:
            parts.append(move(parse(ln.d), x, 0))
            x += ln.width
    return Composite(parts, total)


def segs_of(ln):
    return ln.segs if isinstance(ln, Composite) else parse(ln.d)


def set_right(ln, x_right, base):
    return move(segs_of(ln), x_right - ln.width, base)


def set_left(ln, x_left, base):
    return move(segs_of(ln), x_left, base)


def set_centre(ln, cx, base):
    return move(segs_of(ln), cx - ln.width / 2, base)


def fit(text, face, size, maxw, **kw):
    ln = line(text, face, size, **kw)
    return ln if ln.width <= maxw else line(text, face, size * maxw / ln.width, **kw)


def paragraph(text, face, size, measure, **kw):
    """Break text into lines no wider than measure (flush right, ragged left); returns shaped lines."""
    words, lines, cur = text.split(" "), [], []          # a no-break space holds its words together
    for w in words:
        trial = " ".join(cur + [w])
        if cur and line(trial, face, size, **kw).width > measure:
            lines.append(" ".join(cur))
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(" ".join(cur))
    # no widow: a last line of one short word pulls one word down
    if len(lines) > 1 and len(lines[-1].split()) == 1:
        prev = lines[-2].split()
        if len(prev) > 2:
            lines[-2], lines[-1] = " ".join(prev[:-1]), prev[-1] + " " + lines[-1]
    return [line(t, face, size, **kw) for t in lines]




def segs_to_geom(segs, steps=10):
    """Path segments (as parse() returns them) to a shapely geometry, filled even-odd."""
    rings, cur = [], []
    x = y = 0.0
    for s in segs:
        if s[0] == "M":
            if len(cur) > 2:
                rings.append(cur)
            cur = [(s[1], s[2])]
            x, y = s[1], s[2]
        elif s[0] == "L":
            cur.append((s[1], s[2]))
            x, y = s[1], s[2]
        elif s[0] == "C":
            x0, y0 = x, y
            x1, y1, x2, y2, x3, y3 = s[1:]
            for i in range(1, steps + 1):
                t = i / steps
                a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                cur.append((a * x0 + b * x1 + c * x2 + d * x3, a * y0 + b * y1 + c * y2 + d * y3))
            x, y = x3, y3
        elif s[0] == "Z":
            if len(cur) > 2:
                rings.append(cur)
            cur = []
    if len(cur) > 2:
        rings.append(cur)
    # fonts overlap their contours (a join laid over a letter) and do not agree on their direction: a contour
    # wholly inside another is a counter, contours that merely overlap are one shape (nesting, not orientation)
    from shapely.ops import unary_union
    polys = []
    for r in rings:
        p = Polygon(r)
        if not p.is_valid:
            p = p.buffer(0)
        if not p.is_empty:
            polys.append(p)
    if not polys:
        return Polygon()
    depth = []
    for i, a in enumerate(polys):
        d = 0
        for j, b in enumerate(polys):
            if i != j and b.area > a.area and b.buffer(1e-4).contains(a):
                d += 1
        depth.append(d)
    g = Polygon()
    for level in range(max(depth) + 1):
        layer = unary_union([p for p, d in zip(polys, depth) if d == level])
        g = g.union(layer) if level % 2 == 0 else g.difference(layer)
    return g if g.is_valid else g.buffer(0)


LOG = []          # every line set, with its outlines, for check()


def text(t, face, size, x_right=None, x_left=None, cx=None, base=0.0, **kw):
    """A line of type as geometry, set right, left or centred on the baseline; returns (geometry, width)."""
    ln = line(t, face, size, **kw)
    if x_right is not None:
        segs = set_right(ln, x_right, base)
    elif x_left is not None:
        segs = set_left(ln, x_left, base)
    else:
        segs = set_centre(ln, cx, base)
    g = segs_to_geom(segs)
    LOG.append((t, segs, g))
    return g, ln.width


def check(tolerance=0.005, px_per_mm=24.0):
    """Every line set so far, drawn twice: from the geometry the covers print, and from the font's own outlines
    by the non-zero winding rule the font was drawn for. A word that loses a letter, or gains a slit where two
    contours overlap, differs; the covers are not written. Needs skia-python; without it the check says so."""
    try:
        import numpy as np
        import skia
    except ImportError:
        return ["typeset.check: skia-python is not installed; the type was not verified"]
    import artwork as AW
    bad = []
    for (t, segs, g) in LOG:
        if g.is_empty:
            bad.append(f"{t}: empty")
            continue
        x0, y0, x1, y1 = g.bounds
        w, h = int((x1 - x0) * px_per_mm) + 8, int((y1 - y0) * px_per_mm) + 8

        def draw(fill_segs=None, geom=None):
            surf = skia.Surface(w, h)
            with surf as c:
                c.clear(skia.ColorWHITE)
                path = skia.Path()
                if fill_segs is not None:
                    path.setFillType(skia.PathFillType.kWinding)
                    for sg in fill_segs:
                        X = lambda v: (v - x0) * px_per_mm + 4          # noqa: E731
                        Y = lambda v: (v - y0) * px_per_mm + 4          # noqa: E731
                        if sg[0] == "M":
                            path.moveTo(X(sg[1]), Y(sg[2]))
                        elif sg[0] == "L":
                            path.lineTo(X(sg[1]), Y(sg[2]))
                        elif sg[0] == "C":
                            path.cubicTo(X(sg[1]), Y(sg[2]), X(sg[3]), Y(sg[4]), X(sg[5]), Y(sg[6]))
                        else:
                            path.close()
                else:
                    path.setFillType(skia.PathFillType.kEvenOdd)
                    for poly in AW.poly_list(geom):
                        for ring in [poly.exterior] + list(poly.interiors):
                            cs = list(ring.coords)
                            path.moveTo((cs[0][0] - x0) * px_per_mm + 4, (cs[0][1] - y0) * px_per_mm + 4)
                            for (x, y) in cs[1:]:
                                path.lineTo((x - x0) * px_per_mm + 4, (y - y0) * px_per_mm + 4)
                            path.close()
                c.drawPath(path, skia.Paint(AntiAlias=False, Color=skia.ColorBLACK))
            a = surf.makeImageSnapshot().toarray()[..., 0] < 128
            return a
        ref, got = draw(fill_segs=segs), draw(geom=g)
        # only what differs away from the letters' edges counts: the flattening of a curve moves an edge by a
        # pixel; a lost letter or a slit is inside
        from scipy import ndimage
        edge = ndimage.binary_dilation(ref, iterations=2) & ~ndimage.binary_erosion(ref, iterations=2)
        diff = (np.logical_xor(ref, got) & ~edge).sum() / max(1, ref.sum())
        if diff > tolerance:
            bad.append(f"{t}: {diff:.1%} of the letters differ from the font")
    return bad


def glyph_runs(t, path, size, features=None, tracking=0.0):
    """A line shaped right to left, returned glyph by glyph: [(cluster, segs, mark)], cluster being the index in t
    of the character the glyph sets, and mark whether the font classes the glyph as a mark (GDEF class 3: the
    vowels, the shadda, the sukun, the tanween). The line's left end is at x = 0 on the baseline y = 0 (mm, y
    downward)."""
    import uharfbuzz as hb
    from fontTools.pens.recordingPen import DecomposingRecordingPen, RecordingPen
    from fontTools.pens.transformPen import TransformPen
    data, font = L.load(path)
    face = hb.Face(data)
    hbfont = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(t)
    buf.guess_segment_properties()
    buf.direction, buf.script, buf.language = "rtl", "Arab", "ar"
    hb.shape(hbfont, buf, features or {"kern": True, "liga": False, "calt": True})
    gs = font.getGlyphSet()
    order = font.getGlyphOrder()
    classes = font["GDEF"].table.GlyphClassDef.classDefs if "GDEF" in font else {}
    k = size / face.upem
    x = 0.0
    out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        # composite glyphs (a base and its dots, as Amiri draws them) are drawn through their components
        dec = DecomposingRecordingPen(gs)
        gs[order[info.codepoint]].draw(dec)
        rec = RecordingPen()
        dec.replay(TransformPen(rec, (k, 0, 0, -k, x + pos.x_offset * k, -pos.y_offset * k)))
        segs = []
        for op, pts in rec.value:
            if op == "moveTo":
                segs.append(("M",) + tuple(pts[0]))
            elif op == "lineTo":
                segs.append(("L",) + tuple(pts[0]))
            elif op == "curveTo":
                p = [q for pt in pts for q in pt]
                segs.append(("C",) + tuple(p))
            elif op == "qCurveTo":
                # quadratic runs: expand the implied on-curve points, then raise each to a cubic
                cur = segs[-1][-2:] if segs else (0.0, 0.0)
                ctrl = list(pts[:-1])
                end = pts[-1]
                for i, c in enumerate(ctrl):
                    nxt = end if i == len(ctrl) - 1 else ((c[0] + ctrl[i + 1][0]) / 2, (c[1] + ctrl[i + 1][1]) / 2)
                    x0, y0 = cur
                    segs.append(("C", x0 + 2 / 3 * (c[0] - x0), y0 + 2 / 3 * (c[1] - y0),
                                 nxt[0] + 2 / 3 * (c[0] - nxt[0]), nxt[1] + 2 / 3 * (c[1] - nxt[1]), nxt[0], nxt[1]))
                    cur = nxt
            elif op in ("closePath", "endPath"):
                segs.append(("Z",))
        out.append((info.cluster, segs, classes.get(order[info.codepoint]) == 3))
        x += pos.x_advance * k + tracking
    return out, x - tracking


def advance(t, path, size, features=None):
    """The width of a line as glyph_runs sets it, shaped but not drawn (mm)."""
    import uharfbuzz as hb
    data, _ = L.load(path)
    face = hb.Face(data)
    buf = hb.Buffer()
    buf.add_str(t)
    buf.guess_segment_properties()
    buf.direction, buf.script, buf.language = "rtl", "Arab", "ar"
    hb.shape(hb.Font(face), buf, features or {"kern": True, "liga": False, "calt": True})
    return sum(p.x_advance for p in buf.glyph_positions) * size / face.upem
