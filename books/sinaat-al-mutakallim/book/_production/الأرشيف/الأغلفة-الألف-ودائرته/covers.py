#!/usr/bin/env python3
"""The covers of the eleven volumes: «الألف ودائرته» (Bible, ch. 25 §11).

One idea runs through the series: the measure of Arabic writing. The alif, drawn after the Bulaq Naskh
of the Arabic book, is seven qalam dots tall. Its circle (the governing circle of the proportioned script)
has the alif for its diameter. Both stand on one gold line, the سطر, which runs across front, spine and
back:

- the front: the title in the Kufam logotype; the circle pressed blind with one gold hairline; the alif in
  foil. On the ten programme volumes the alif enters its circle a step at a time, from the rim
  (the first volume) to the diameter (the tenth). The reference carries the measure itself: its seven
  dots. Beside the circle the seven dots are raised blind, a measure felt rather than seen, and their seven
  levels run across the front as ruling in gloss, seen only when the book is tilted. There is one crimson
  nuqta, where the alif meets the line.
- the spine: title, the volume number in a gold rhombus, the volume name, the stage in dots, then the alif
  standing on the line. Shelved in order, the spines read as one line of alifs, the calligrapher's first
  exercise, closed by the measure on the reference.
- the back: the book's own words, the series, this volume, and a map of the eleven as a small line of
  alifs with this volume in gold. The ISBN zone is kept clear and nothing is printed in it until the
  publisher issues the number (Bible, ch. 25 §10و).

Each wrap is written as separate plates on one page geometry, in covers/:
  Cover-NN_<Latin>_PRINT.pdf       CMYK artwork for the finished edition (the gold comes from the foil)
  Cover-NN_<Latin>_PRINT-FLAT.pdf  the same with the gold printed as ink: the cover without finishes
  Cover-NN_<Latin>_FOIL.pdf        hot-foil plate (champagne gold), 100% K
  Cover-NN_<Latin>_EMBOSS.pdf      blind emboss (the seven dots of the measure), 100% K
  Cover-NN_<Latin>_DEBOSS.pdf      blind deboss (the circle's band), 100% K
  Cover-NN_<Latin>_SPOT-UV.pdf     spot gloss on the matte laminate (the seven dots; the ruling), 100% K
  Cover-NN_<Latin>_GUIDES.pdf      trim, folds, bleed, safe area, the reserved ISBN zone (not for printing)
and covers/spines.json holds the spine widths (from the final proofs' page counts). The caliper is
provisional until the printer confirms the paper.

    python3 pdf/covers.py            the eleven wraps
    python3 pdf/covers.py 3 7        some volumes
Material proofs, the shelf and the spine close-up: pdf/cover_proofs.py.
Needs reportlab (CMYK and plate output), besides the project's usual tools.
"""
from __future__ import annotations

import json
import math
import re
import sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cover2 as C2  # noqa: E402  (fonts, the Kufam logotype)
import frontmatter as FM  # noqa: E402
import geometry as G  # noqa: E402
import lettering as L  # noqa: E402

OUT = HERE.parent / "covers"
W, H = G.W, G.H                        # 170 × 240 mm
# the physical figures come from the printer: covers/printer-spec.json (provisional until the printer fills it);
# the artwork is drawn on the page (170 × 240) and placed on the wrap the binding makes, so a new board,
# square, joint or caliper moves the panels without redrawing anything
SPEC = json.loads((OUT / "printer-spec.json").read_text(encoding="utf-8"))
CALIPER = SPEC["text_paper"]["caliper_mm_per_leaf"]
BLEED = SPEC["paperback"]["bleed_mm"]
COVER_ALLOW = SPEC["paperback"]["cover_allowance_mm"]
SAFE = 8.0                             # nothing that matters within this of a trim or a fold

LATIN = {1: "Al-Usul", 2: "Al-Lisan", 3: "Al-Ibara", 4: "Al-Bayan", 5: "Al-Maqam", 6: "Al-Adab", 7: "Al-Hiwar",
         8: "Al-Majalis-wal-Minbar", 9: "Al-Muassasa", 10: "Al-Tamkin", 11: "Marji-al-Mutakallim"}
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

# ------------------------------------------------------------------------------------------------ colour (CMYK)
# Built for coated cover stock under matte laminate; to be matched on the printer's contract proof.
SAPPHIRE = (1.00, 0.88, 0.26, 0.38)    # the field
SAPPHIRE_DEEP = (1.00, 0.89, 0.28, 0.44)   # the measure's tone on PRINT-FLAT: barely off the field
SAPPHIRE_GHOST = (0.78, 0.58, 0.10, 0.22)  # the other volumes on the back's map
SAPPHIRE_LINE = (0.92, 0.74, 0.18, 0.30)   # the drafted construction: a hairline a shade off the field
PEARL = (0.04, 0.05, 0.12, 0.00)
PEARL_SOFT = (0.10, 0.10, 0.18, 0.04)
CHAMPAGNE = (0.14, 0.24, 0.55, 0.03)   # printed gold: small type, and every foil element on PRINT-FLAT
CRIMSON = (0.15, 1.00, 0.75, 0.15)
K100 = (0, 0, 0, 1)
WHITE = (0, 0, 0, 0)

PLATES = ("PRINT", "PRINT-FLAT", "FOIL", "EMBOSS", "DEBOSS", "SPOT-UV", "GUIDES")

# ------------------------------------------------------------------------------------------------ the composition
BASE = 198.0                           # the سطر, from the head
A = 112.0                              # the alif, and the circle's diameter
U = A / 7                              # one dot
CX, CY, R = 74.0, BASE - A / 2, A / 2  # the circle on the front
MEASURE_X = 151.0                      # the seven dots, beside it
TITLE_W, TITLE_RIGHT, TITLE_BASE = 118.0, 154.0, 58.0
SUB_BASE = 71.0
SPINE_ALIF = 64.0
ALIF_WIDEN = 0.86                      # the front's alif, a little leaner than the type

# ------------------------------------------------------------------------------------------------ paths
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


def poly(pts):
    return [("M", *pts[0])] + [("L", *q) for q in pts[1:]] + [("Z",)]


def rect(x, y, w, h):
    return poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)])


def circle(cx, cy, r, reverse=False):
    k = 0.5522847498 * r
    pts = [(cx + r, cy), (cx, cy + r), (cx - r, cy), (cx, cy - r)]
    ctrl = [((cx + r, cy + k), (cx + k, cy + r)), ((cx - k, cy + r), (cx - r, cy + k)),
            ((cx - r, cy - k), (cx - k, cy - r)), ((cx + k, cy - r), (cx + r, cy - k))]
    segs = [("M", *pts[0])]
    for i in range(4):
        (c1, c2), q = ctrl[i], pts[(i + 1) % 4]
        segs.append(("C", *c1, *c2, *q))
    segs.append(("Z",))
    if reverse:
        segs = xf(segs, a=-1, e=2 * cx)          # mirrored: runs the other way
    return segs


def ring(cx, cy, r_in, r_out):
    return circle(cx, cy, r_out) + circle(cx, cy, r_in, reverse=True)


def nuqta(x, y, h, w=0.84, s=0.06):
    """The qalam's rhombic dot standing on its vertex: centre (x, y), height h, turned slightly clockwise."""
    w = w * h
    return poly([(x + s * h, y - 0.5 * h), (x + 0.5 * w, y - s * h), (x - s * h, y + 0.5 * h), (x - 0.5 * w, y + s * h)])


def rhombus(x, y, s):
    return poly([(x, y - s), (x + s, y), (x, y + s), (x - s, y)])


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


# ------------------------------------------------------------------------------------------------ the alif
class Alif:
    """The series' alif: the proportioned Naskh alif of the Arabic book (after the Bulaq model as cut in
    Amiri), set as a drawing, not as type. Its foot rests on the line at the given x."""

    def __init__(self, path):
        ln = L.Line("ا", path, 100.0)
        self.segs = parse(ln.d)
        x0, y0, x1, y1 = bbox(self.segs)
        self.h = y1 - y0
        self.y1 = y1
        self.foot_x = self._foot_x(x0, x1, y1)
        self.x0, self.x1 = x0, x1

    def _foot_x(self, x0, x1, y1):
        # the lowest point of the outline: where the stroke touches the line
        pts = [(s[-2], s[-1]) for s in self.segs if s[0] != "Z"]
        return min(pts, key=lambda p: -p[1])[0]

    def at(self, x, base, height, widen=1.0):
        k = height / self.h
        return xf(self.segs, a=k * widen, d=k, e=x - self.foot_x * k * widen, f=base - self.y1 * k)

    def extent(self, height, widen=1.0):
        k = height / self.h
        return (self.x0 - self.foot_x) * k * widen, (self.x1 - self.foot_x) * k * widen


# ------------------------------------------------------------------------------------------------ the scene
class Scene:
    """Items on one wrap, in mm from the top-left of the bleed. Each item names the plates it goes on;
    'ink' is its colour on PRINT, 'flat' its colour on PRINT-FLAT (defaults to ink; foil defaults to
    champagne there)."""

    def __init__(self, w, h):
        self.w, self.h, self.items = w, h, []

    def add(self, segs, plates, ink=None, flat=None, evenodd=False):
        self.items.append(dict(segs=segs, plates=set(plates), ink=ink, flat=flat, evenodd=evenodd))


def pages(n):
    import pymupdf
    p = HERE.parent / f"Volume-{n:02d}_{LATIN[n]}_Final-Proof.pdf"
    return len(pymupdf.open(str(p)))


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
        fb = (m, m, m + bw, m + bh)                           # front board
        sp = (fb[2] + j, m, fb[2] + j + sw, m + bh)          # spine
        bb = (sp[2] + j, m, sp[2] + j + bw, m + bh)          # back board
        return dict(w=bb[2] + m, h=bh + 2 * m, margin=m, front=fb, spine=sp, back=bb, joint=j,
                    front_art=(m + sq, m + sq), back_art=(bb[0] - sb, m + sq), art_top=m + sq)
    b = BLEED
    fb, sp, bb = (b, b, b + W, b + H), (b + W, b, b + W + sw, b + H), (b + W + sw, b, b + 2 * W + sw, b + H)
    return dict(w=2 * W + sw + 2 * b, h=H + 2 * b, margin=b, front=fb, spine=sp, back=bb, joint=0.0,
                front_art=(b, b), back_art=(bb[0], b), art_top=b)


def stage_of(n):
    st = FM.VOLUMES[n - 1][3]
    return FM.STAGE_DOTS.get(st, 0)


def alif_x(n, alif):
    """Where the alif stands on the front: from the circle's rim (1) to its diameter (10)."""
    lft, rgt = alif.extent(A)
    start = CX + 0.80 * R
    return start + (CX - start) * (n - 1) / 9


def build(n, faces=None, sw=None):
    faces = faces or Faces()
    alif = Alif(faces.amiri4.path)
    sw = sw if sw is not None else spine_width(n)
    lay = layout(sw)
    wrap_w, wrap_h = lay["w"], lay["h"]
    sc = Scene(wrap_w, wrap_h)
    sc.layout = lay
    sc.volume = n
    fx, y0 = lay["front_art"]                            # the page-sized artwork of the front, and of the back
    bx = lay["back_art"][0]
    sx = lay["spine"][0]
    ordinal, name = FM.VOLUMES[n - 1][:2]

    # the field, over the whole bleed
    sc.add(rect(0, 0, wrap_w, wrap_h), {"PRINT", "PRINT-FLAT"}, ink=SAPPHIRE)

    # the line: one gold line across front, spine and back
    sc.add(rect(0, y0 + BASE - 0.2, wrap_w, 0.4), {"FOIL"})

    front(sc, n, faces, alif, fx, y0, ordinal, name)
    spine(sc, n, faces, alif, sx, y0, sw, ordinal, name)
    back(sc, n, faces, alif, bx, y0, ordinal, name)
    guides(sc, faces, fx, sx, bx, y0, sw)
    return sc, sw


def front(sc, n, faces, alif, x0, y0, ordinal, name):
    P = lambda segs: move(segs, x0, y0)     # noqa: E731
    # the ruling: the seven lines of the measure carried across the front in gloss on the matte laminate,
    # seen only when the book is tilted to the light (the calligrapher's مسطرة)
    for k in range(1, 8):
        yk = BASE - k * U
        sc.add(P(rect(-BLEED, yk - 0.15, W + BLEED, 0.3)), {"SPOT-UV"})
    # the drafted construction (§10د, the second layer: a structure seen only up close): the square that
    # governs the circle, drawn as a draughtsman draws it, its lines run a little past their meeting, with the
    # rhombic dot where each touches the circle; a hairline a shade off the field, pressed blind as well
    ext, hw = 9.0, 0.09
    for x in (CX - R, CX + R):
        sc.add(P(rect(x - hw, CY - R - ext, 2 * hw, 2 * R + ext)), {"PRINT", "PRINT-FLAT", "DEBOSS-FINE"}, ink=SAPPHIRE_LINE)
    # only the square's own sides: no line through the centre (a crosshair reads as a gauge, §11ب)
    sc.add(P(rect(CX - R - ext, CY - R - hw, 2 * R + 2 * ext, 2 * hw)), {"PRINT", "PRINT-FLAT", "DEBOSS-FINE"}, ink=SAPPHIRE_LINE)
    for (tx, ty) in ((CX, CY - R), (CX - R, CY), (CX + R, CY)):
        sc.add(P(rhombus(tx, ty, 0.9)), {"PRINT", "PRINT-FLAT"}, ink=SAPPHIRE_LINE)
    # the circle: a band at the rim pressed blind, one gold hairline in it
    sc.add(P(ring(CX, CY, R - 1.5, R + 1.5)), {"DEBOSS", "UV-KO"}, evenodd=True)
    sc.add(P(ring(CX, CY, R - 0.18, R + 0.18)), {"FOIL"}, evenodd=True)
    # the measure beside it: seven dots raised blind, to be found by the fingers, with a gloss on them
    for k in range(7):
        d = P(nuqta(MEASURE_X, BASE - U / 2 - k * U, U * 0.9))
        sc.add(d, {"EMBOSS", "SPOT-UV"})
        sc.add(d, {"PRINT-FLAT"}, flat=SAPPHIRE_DEEP)
    if n == 11:
        # the reference: the measure itself stands as the diameter; its first dot, the sound, is solid
        for k in range(7):
            yk = BASE - U / 2 - k * U
            if k == 0:
                sc.add(P(nuqta(CX, yk, U * 0.86)), {"FOIL", "UV-KO"})
            else:
                sc.add(P(nuqta(CX, yk, U * 0.86) + nuqta(CX, yk, U * 0.86 - 1.0)), {"FOIL", "UV-KO"}, evenodd=True)
        s = U * 0.28
        sc.add(P(nuqta(CX - 0.42 * U * 0.86 - 0.42 * s - 1.6, BASE - s / 2 - 0.3, s)), {"PRINT", "PRINT-FLAT"}, ink=CRIMSON)
    else:
        x = alif_x(n, alif)
        sc.add(P(alif.at(x, BASE, A, widen=ALIF_WIDEN)), {"FOIL", "UV-KO"})
        lft, _ = alif.extent(A, widen=ALIF_WIDEN)
        s = U * 0.28
        sc.add(P(nuqta(x + lft - 0.42 * s - 1.4, BASE - s / 2 - 0.3, s)), {"PRINT", "PRINT-FLAT"}, ink=CRIMSON)

    # the title: the Kufam logotype, «صناعة» over «المتكـلّم العربي»
    lg = C2.Logotype(faces.css, width=TITLE_W)
    cb, mb = lg.crown.bounds, lg.main.bounds
    base_m = TITLE_BASE
    base_c = base_m + mb[1] - lg.gap - cb[3]
    sc.add(P(set_right(lg.crown, TITLE_RIGHT, base_c)), {"FOIL"})
    sc.add(P(set_right(lg.main, TITLE_RIGHT, base_m)), {"FOIL"})
    sc.add(P(set_right(line(FM.SUBTITLE, faces.sch4, 5.0), TITLE_RIGHT, SUB_BASE)), {"PRINT", "PRINT-FLAT"}, ink=PEARL)

    # the author and the volume, under the line
    sc.add(P(set_right(line("تأليف", faces.changa4, 2.5), TITLE_RIGHT, BASE + 13.5)), {"PRINT", "PRINT-FLAT"}, ink=CHAMPAGNE)
    sc.add(P(set_right(line(FM.AUTHOR_SHORT, faces.sch6, 4.9), TITLE_RIGHT, BASE + 23.5)), {"PRINT", "PRINT-FLAT"}, ink=PEARL)
    sc.add(P(set_left(line(f"المجلد {ordinal}", faces.changa4, 2.5), 16.0, BASE + 13.5)), {"PRINT", "PRINT-FLAT"}, ink=CHAMPAGNE)
    sc.add(P(set_left(line(name, faces.changa5, 5.0), 16.0, BASE + 23.5)), {"PRINT", "PRINT-FLAT"}, ink=CHAMPAGNE)


def spine(sc, n, faces, alif, x0, y0, sw, ordinal, name):
    P = lambda segs: move(segs, x0, y0)     # noqa: E731
    cx, m = sw / 2, sw - 2 * 2.4
    # the bands of a bound spine: a gold double rule at the head and at the tail, at one height on every
    # volume, so that the eleven on a shelf carry three gold lines across them (head, the سطر, tail)
    for yb in (6.6, 8.0, H - 8.0, H - 6.6):
        sc.add(P(rect(-0.01, yb - 0.14, sw + 0.02, 0.28)), {"FOIL"})
    y = 17.5
    for word in ("صناعة", "المتكلّم", "العربي"):
        sc.add(P(set_centre(fit(word, faces.kufi6, 3.5, m, features=KF), cx, y)), {"FOIL"})
        y += 5.4
    # the volume's number in its rhombus (the reference: an open rhombus)
    ny, s = 51.0, 6.6
    num = fit(str(n), faces.amiri7, 5.2 if n < 10 else 4.3, 9, digits=True)
    num_segs = set_centre(num, cx, ny + (1.9 if n < 10 else 1.6))
    if n == 11:
        sc.add(P(rhombus(cx, ny, s) + rhombus(cx, ny, s - 0.5)), {"FOIL"}, evenodd=True)
        sc.add(P(num_segs), {"FOIL"})
    else:
        sc.add(P(rhombus(cx, ny, s) + num_segs), {"FOIL"}, evenodd=True)
    words = {8: ["المجالس", "والمنبر"], 11: ["مرجع", "المتكلّم", "العربي"]}.get(n, [name])
    y = 71.5
    for w in words:
        sc.add(P(set_centre(fit(w, faces.changa5, 4.4, m), cx, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL)
        y += 6.5
    k = stage_of(n)
    for i in range(k):
        sc.add(P(nuqta(cx + (i - (k - 1) / 2) * 2.4, y - 1.4, 1.6)), {"FOIL"})
    # the alif on the line; on the reference, the measure
    if n == 11:
        u = SPINE_ALIF / 7
        for i in range(7):
            yk = BASE - u / 2 - i * u
            outer = nuqta(cx, yk, u * 0.9)
            if i == 0:
                sc.add(P(outer), {"FOIL"})
            else:
                sc.add(P(outer + nuqta(cx, yk, u * 0.9 - 0.8)), {"FOIL"}, evenodd=True)
    else:
        lft, rgt = alif.extent(SPINE_ALIF, widen=0.9)
        sc.add(P(alif.at(cx - (lft + rgt) / 2, BASE, SPINE_ALIF, widen=0.9)), {"FOIL"})
    # the author, under the line; the publisher's mark at the foot
    y = BASE + 9.0
    for part in ("أحمد بن", "إبراهيم", "السليمي"):
        sc.add(P(set_centre(fit(part, faces.sch6, 3.0, m), cx, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL)
        y += 4.4
    publisher_mark(sc, faces, P, cx, 228.0, small=True)


def seal_segs(faces, cx, base, small=False):
    """The house's device (Bible, ch. 98), as outlines: a colophon seal. «الإحسان» in Kufam inside a frame of two
    hairlines, the qalam's rhombic dot breaking the top rule at its centre; «base» is the word's baseline."""
    size = 2.7 if small else 3.9
    w = line("الإحسان", faces.kufi6, size, features=KF)
    out = [set_centre(w, cx, base)]
    pad_x, pad_top, pad_bot = size * 0.9, size * 1.0, size * 0.8
    x0, x1 = cx - w.width / 2 - pad_x, cx + w.width / 2 + pad_x
    y0, y1 = base - size * 0.95 - pad_top, base + pad_bot
    t_out, t_in, gap = (0.22, 0.12, 0.7) if small else (0.28, 0.14, 0.9)
    dot = size * 0.34
    for (t, d) in ((t_out, 0.0), (t_in, gap)):
        a0, a1, b0, b1 = x0 + d, x1 - d, y0 + d, y1 - d
        hole = dot * 0.9 + 0.5 + d * 0.6
        out.append(rect(a0, b1 - t, a1 - a0, t) + rect(a0, b0, t, b1 - b0) + rect(a1 - t, b0, t, b1 - b0)
                   + rect(a0, b0, cx - hole - a0, t) + rect(cx + hole, b0, a1 - cx - hole, t))
    out.append(rhombus(cx, y0 + t_out / 2, dot))
    return out


def publisher_mark(sc, faces, P, cx, base, small=False):
    for segs in seal_segs(faces, cx, base, small):
        sc.add(P(segs), {"FOIL"})


@lru_cache(maxsize=1)
def _faces():
    return Faces()


def seal_svg(width=16.0, on_dark=False):
    """The seal for a page of the book, drawn from the covers' own outlines, at the given width (mm)."""
    segs = seal_segs(_faces(), 0.0, 0.0)
    allp = [p for s_ in segs for p in s_]
    x0, y0, x1, y1 = bbox(allp)
    k = width / (x1 - x0)
    gold = "#C9A95C" if not on_dark else "#E4CB8C"
    word = "#0C2766" if not on_dark else "#E4CB8C"          # on paper the name reads in sapphire, the frame in gold
    body = "".join(f'<path d="{to_d(xf(s_, a=k, d=k, e=-x0 * k, f=-y0 * k))}" fill="{word if i == 0 else gold}"/>'
                   for i, s_ in enumerate(segs))
    h = (y1 - y0) * k
    return (f'<svg class="seal" viewBox="0 0 {width:.2f} {h:.2f}" style="width:{width:.2f}mm;height:{h:.2f}mm;'
            f'display:block;margin:0 auto" aria-hidden="true">{body}</svg>')




# the book's own words (chapter sixteen, §١), then the series and this volume
LEAD = ("لا يريد هذا الكتاب أن يُخرج متكلّمًا يُبهر الناس بألفاظه،",      # set by sense, a clause a line
        "ولا خطيبًا يُعجب السامعين بنفسه؛",
        "بل يريد متكلّمًا يُفهِم ويُحسن ويؤثّر.")
SERIES = ("كتابٌ في أحد عشر مجلدًا في صناعة الكلام بالعربية الفصحى المعاصرة، لمن يعرف العربية ثم لا يجدها على لسانه "
          "حين يحتاج إليها. يبدأ من سؤالٍ لا بدّ منه: أيّ\u00a0عربيةٍ\u00a0نتكلّم؟ ثم يمضي من صحة الصوت واستقامة الجملة إلى "
          "مراعاة المقام وحسن البيان، جامعًا بين أصول البيان العربي وما انتهى إليه الدرس الحديث في التواصل، ومقيمًا "
          "ذلك كله على النماذج المتدرّجة والحوار والتدريب والتقويم.")


def back(sc, n, faces, alif, x0, y0, ordinal, name):
    P = lambda segs: move(segs, x0, y0)     # noqa: E731
    right, measure = 154.0, 118.0
    # the column the words stand in, drawn as the front's construction is drawn: two hairlines a shade off the
    # field, run past the text a little (the back continues the front's architecture, not a text panel)
    for x in (right - measure - 6.0, right + 6.0):
        sc.add(P(rect(x - 0.09, 20.0, 0.18, BASE - 26.0)), {"PRINT", "PRINT-FLAT"}, ink=SAPPHIRE_LINE)
    y = 38.0
    for ln in (line(t, faces.sch6, 4.7) for t in LEAD):
        sc.add(P(set_right(ln, right, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL)
        y += 8.2
    # a short gold rule, then the series
    y += 2.0
    sc.add(P(rect(right - 14, y - 0.15, 14, 0.3)), {"FOIL"})
    y += 10.0
    for ln in paragraph(SERIES, faces.sch4, 3.5, measure):
        sc.add(P(set_right(ln, right, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL_SOFT)
        y += 6.3
    # this volume
    y += 7.0
    sc.add(P(set_right(line("في هذا المجلد", faces.changa4, 2.6), right, y)), {"PRINT", "PRINT-FLAT"}, ink=CHAMPAGNE)
    y += 8.2
    head = "مرجع المتكلّم العربي" if n == 11 else f"المجلد {ordinal}: {name}"
    sc.add(P(set_right(line(head, faces.changa5, 4.4), right, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL)
    y += 7.6
    what = FM.VOLUMES[n - 1][2]
    if n == 11:
        what = f"{FM.REFERENCE_SUB}: {what}"
    for ln in paragraph(what + ".", faces.sch4, 3.5, measure):
        sc.add(P(set_right(ln, right, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL_SOFT)
        y += 6.3
    stage = FM.VOLUMES[n - 1][3]
    if stage:
        y += 2.2
        babs = re.sub(r"<[^>]+>", "", FM.VOLUMES[n - 1][4])
        label = f"{FM.STAGES[stage]}: {stage} · {babs}"
        sc.add(P(set_right(line(label, faces.changa4, 2.8), right, y)), {"PRINT", "PRINT-FLAT"}, ink=CHAMPAGNE)
        y += 6.4
        for ln in paragraph(FM.STAGE_LINE[stage] + ".", faces.sch4, 3.5, measure):
            sc.add(P(set_right(ln, right, y)), {"PRINT", "PRINT-FLAT"}, ink=PEARL_SOFT)
            y += 6.2
    series_map(sc, n, faces, alif, P, right)
    # the house and the edition, under the line (the ISBN zone stays clear: see guides())
    publisher_mark(sc, faces, P, right - 12.0, 218.0)
    sc.add(P(set_right(line(FM.PUBLISHER_AR, faces.sch4, 3.0), right, 226.5)), {"PRINT", "PRINT-FLAT"}, ink=PEARL_SOFT)
    ed = f"{FM.EDITION}، {FM.YEAR}"
    sc.add(P(set_right(line(ed, faces.sch4, 2.8), right - 34.0, 218.0)), {"PRINT", "PRINT-FLAT"}, ink=PEARL_SOFT)
    isbn_zone(sc, n, faces, P)


# ------------------------------------------------------------------------------------------------ the ISBN zone
ISBN_ZONE = (16.0, 206.0, 46.0, 26.0)   # on the back, from its spine side and its head (mm): Bible, ch. 25 §11و
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
    """The EAN-13 symbol of an ISBN as bars (mm), left quiet zone at x, bars' top at y; guard bars run 5
    modules longer. Returns (bars, width)."""
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
            bars += rect(x0 + i * module, y, (j - i) * module, height + (5 * module if i in guard else 0))
            i = j
        else:
            i += 1
    return bars, (95 + 18) * module


def isbn_zone(sc, n, faces, P):
    zx, zy, zw, zh = ISBN_ZONE
    num, printable = isbn_of(n)
    if not printable:
        return                      # the zone stays clear (the guides show it, and the number's status)
    # a white field (the scanner needs contrast the sapphire and the pearl do not give), the number over the bars
    sc.add(P(rect(zx, zy, zw, zh)), {"PRINT", "PRINT-FLAT"}, ink=WHITE)
    sc.add(P(set_left(line(f"ISBN {num}", faces.serif, 2.3, latin=True), zx + 3.0, zy + 3.4)), {"PRINT", "PRINT-FLAT"}, ink=K100)
    bars, bw = ean13(num, zx + (zw - (95 + 18) * 0.297) / 2, zy + 4.6)
    sc.add(P(bars), {"PRINT", "PRINT-FLAT"}, ink=K100)


def series_map(sc, n, faces, alif, P, right):
    """The eleven as a small line of alifs on the سطر, this volume in gold; the reference is the measure."""
    h, slot = 15.0, 8.2
    for v in range(1, 12):
        cx = right - slot / 2 - (v - 1) * slot
        here = v == n
        plates, ink = ({"FOIL"}, None) if here else ({"PRINT", "PRINT-FLAT"}, SAPPHIRE_GHOST)
        if v == 11:
            u = h / 7
            for i in range(7):
                sc.add(P(nuqta(cx, BASE - u / 2 - i * u, u * 0.9)), plates, ink=ink)
        else:
            lft, rgt = alif.extent(h, widen=0.9)
            sc.add(P(alif.at(cx - (lft + rgt) / 2, BASE, h, widen=0.9)), plates, ink=ink)
        num = line(str(v), faces.amiri7 if here else faces.amiri4, 2.6, digits=True)
        sc.add(P(set_centre(num, cx, BASE + 5.2)), {"PRINT", "PRINT-FLAT"}, ink=PEARL if here else SAPPHIRE_GHOST)


def guides(sc, faces, fx, sx, bx, y0, sw):
    """Not for printing: the boards (or the trim), the joints, the spine folds, the turn-in, the safe area, and
    the ISBN zone kept clear on the back with the state of its number."""
    t = 0.12
    lay = sc.layout
    xs = sorted({lay["front"][0], lay["front"][2], lay["spine"][0], lay["spine"][2], lay["back"][0], lay["back"][2]})
    for x in xs:
        sc.add(rect(x - t / 2, 0, t, sc.h), {"GUIDES"}, ink=(0, 1, 0, 0))
    for y in (lay["front"][1], lay["front"][3]):
        sc.add(rect(0, y - t / 2, sc.w, t), {"GUIDES"}, ink=(0, 1, 0, 0))
    lab = line(f"{SPEC['binding']} binding · spine {sw:.1f} mm · joint {lay['joint']:.1f} mm · margin (turn-in or bleed) "
               f"{lay['margin']:.1f} mm · all provisional: covers/printer-spec.json", faces.serif, 2.2, latin=True)
    sc.add(set_left(lab, lay["front"][0] + 2.0, lay["front"][3] + 3.2), {"GUIDES"}, ink=(0, 1, 0, 0))
    for (x, w) in ((fx, W), (bx, W)):
        for seg in (rect(x + SAFE, y0 + SAFE, W - 2 * SAFE, t), rect(x + SAFE, y0 + H - SAFE, W - 2 * SAFE, t),
                    rect(x + SAFE, y0 + SAFE, t, H - 2 * SAFE), rect(x + W - SAFE, y0 + SAFE, t, H - 2 * SAFE)):
            sc.add(seg, {"GUIDES"}, ink=(1, 0, 0, 0))
    zx, zy, zw, zh = bx + ISBN_ZONE[0], y0 + ISBN_ZONE[1], ISBN_ZONE[2], ISBN_ZONE[3]
    for seg in (rect(zx, zy, zw, t), rect(zx, zy + zh, zw, t), rect(zx, zy, t, zh), rect(zx + zw, zy, t, zh)):
        sc.add(seg, {"GUIDES"}, ink=(0, 1, 0, 0))
    n = sc.volume
    num, printable = isbn_of(n)
    state = "printed" if printable else ("PROVISIONAL, not printed" if isbn_valid(num) else "PROVISIONAL, INVALID check digit, not printed")
    for k, txt in enumerate(("ISBN / barcode zone", f"{num or 'no number'}", state)):
        sc.add(set_left(line(txt, faces.serif, 2.2, latin=True), zx + 1.5, zy + 6.0 + 4.0 * k), {"GUIDES"}, ink=(0, 1, 0, 0))
    if num and isbn_valid(num) and not printable:
        # the symbol as it will stand, drawn on the guides only: for the publisher's approval of the layout
        bars, _ = ean13(num, zx + (zw - (95 + 18) * 0.297) / 2, zy + 16.0, height=8.0)
        sc.add(bars, {"GUIDES"}, ink=(0, 1, 0, 0))


# ------------------------------------------------------------------------------------------------ the device inside
@lru_cache(maxsize=1)
def _alif():
    return Alif(L.arabic_face(C2.fonts(), "Amiri", 400))


def to_d(segs):
    out = []
    for s_ in segs:
        if s_[0] == "Z":
            out.append("Z")
        else:
            out.append(s_[0] + " ".join(f"{v:.3f}" for v in s_[1:]))
    return "".join(out)


def device_svg(n, A=20.0, on_dark=False, ext=None, hair=None):
    """The series' device as it stands on the covers of volume n, drawn at circle diameter A (mm) for a page:
    the circle a hairline, the alif (or, on the reference, the measure), the crimson nuqta, and the line under
    them. On paper the circle is sapphire and the line and the alif gold; on sapphire both are gold."""
    alif = _alif()
    R = A / 2
    ext = R * 1.9 if ext is None else ext
    hair = max(0.16, A * 0.006) if hair is None else hair
    gold = "#C9A95C" if not on_dark else "#E4CB8C"
    ring_col = "#0C2766" if not on_dark else "#C9A95C"
    parts = [f'<path d="{to_d(rect(-ext, -hair / 2, 2 * ext, hair))}" fill="{gold}"/>',
             f'<path d="{to_d(ring(0, -R, R - hair / 2, R + hair / 2))}" fill="{ring_col}" fill-rule="evenodd"/>']
    u = A / 7
    if n == 11:
        for k in range(7):
            yk = -u / 2 - k * u
            d = nuqta(0, yk, u * 0.86) if k == 0 else nuqta(0, yk, u * 0.86) + nuqta(0, yk, u * 0.86 - max(0.35, u * 0.07))
            parts.append(f'<path d="{to_d(d)}" fill="{gold}" fill-rule="evenodd"/>')
        x_n = -0.42 * u * 0.86 - 0.42 * u * 0.28 - u * 0.1
    else:
        x = 0.80 * R * (1 - (n - 1) / 9)
        parts.append(f'<path d="{to_d(alif.at(x, 0, A, widen=ALIF_WIDEN))}" fill="{gold}"/>')
        lft, _ = alif.extent(A, widen=ALIF_WIDEN)
        x_n = x + lft - 0.42 * u * 0.28 - u * 0.09
    s_ = u * 0.28
    parts.append(f'<path d="{to_d(nuqta(x_n, -s_ / 2 - hair, s_))}" fill="#A8172E"/>')
    return (f'<svg class="dev" viewBox="{-ext:.2f} {-A - 0.5:.2f} {2 * ext:.2f} {A + 1:.2f}" '
            f'style="width:{2 * ext:.2f}mm;height:{A + 1:.2f}mm;display:block;margin:0 auto" aria-hidden="true">{"".join(parts)}</svg>')


def house_mark_svg(width=14.0, on_dark=False):
    """The house's sign above its name: one qalam dot on a line (Bible, ch. 98), drawn as on the spines."""
    gold = "#C9A95C" if not on_dark else "#E4CB8C"
    h = width * 0.16
    half = width / 2
    gap = h * 0.62
    line = rect(-half, -0.09, half - gap, 0.18) + rect(gap, -0.09, half - gap, 0.18)
    return (f'<svg class="hm" viewBox="{-half:.2f} {-h / 2 - 0.2:.2f} {width:.2f} {h + 0.4:.2f}" '
            f'style="width:{width:.2f}mm;height:{h + 0.4:.2f}mm;display:block;margin:0 auto" aria-hidden="true">'
            f'<path d="{to_d(line)}" fill="{gold}"/><path d="{to_d(nuqta(0, 0, h))}" fill="{gold}"/></svg>')


# ------------------------------------------------------------------------------------------------ plates


def colour_on(it, plate):
    """The item's colour on this plate, or None if it is not on it. On the gloss plate, what is foiled or
    pressed in the ruling's way is knocked out (painted white): varnish and foil do not share a surface."""
    pl = it["plates"]
    if plate == "SPOT-UV" and "UV-KO" in pl and "SPOT-UV" not in pl:
        return WHITE
    if plate == "PRINT":
        return it["ink"] if "PRINT" in pl else None
    if plate == "PRINT-FLAT":
        if "PRINT-FLAT" in pl:
            return it["flat"] or it["ink"]
        return CHAMPAGNE if "FOIL" in pl else None
    if plate == "GUIDES":
        return it["ink"] if "GUIDES" in pl else None
    if plate == "DEBOSS" and "DEBOSS-FINE" in pl:
        return K100
    return K100 if plate in pl else None


def write(sc, plate, path, title):
    from reportlab.lib.colors import CMYKColor
    from reportlab.pdfgen import canvas
    pt = 72 / 25.4
    c = canvas.Canvas(str(path), pagesize=(sc.w * pt, sc.h * pt))
    c.setTitle(title)
    c.setAuthor(FM.PUBLISHER_EN)
    trim = (BLEED * pt, BLEED * pt, (sc.w - BLEED) * pt, (sc.h - BLEED) * pt)
    c.setTrimBox(trim)
    c.setBleedBox((0, 0, sc.w * pt, sc.h * pt))
    for it in sc.items:
        col = colour_on(it, plate)
        if col is None:
            continue
        c.setFillColor(CMYKColor(*col))
        p = c.beginPath()
        for s in it["segs"]:
            if s[0] == "M":
                p.moveTo(s[1] * pt, (sc.h - s[2]) * pt)
            elif s[0] == "L":
                p.lineTo(s[1] * pt, (sc.h - s[2]) * pt)
            elif s[0] == "C":
                p.curveTo(s[1] * pt, (sc.h - s[2]) * pt, s[3] * pt, (sc.h - s[4]) * pt, s[5] * pt, (sc.h - s[6]) * pt)
            else:
                p.close()
        c.drawPath(p, stroke=0, fill=1, fillMode=0 if it["evenodd"] else 1)
    c.showPage()
    c.save()


def endpapers():
    """The flagship's endpapers (Bible, ch. 25 §5: sapphire, with a pattern of the same colour): one spread
    (2 × 170 × 240 + bleed), the same in every volume. The pattern is the series' own unit, not an ornament: the
    qalam's dot set on the lattice of the measure (a dot's height apart, every other row shifted half a step), a
    shade off the field so that it is found rather than seen; one line of the سطر at the height it has on the
    covers, crossing the gutter."""
    b = BLEED
    w, h = 2 * W + 2 * b, H + 2 * b
    sc = Scene(w, h)
    sc.add(rect(0, 0, w, h), {"PRINT", "PRINT-FLAT"}, ink=SAPPHIRE)
    step = U * 1.5
    row = 0
    y = b + step / 2
    while y < h:
        x = b + (step / 2 if row % 2 else 0.0)
        while x < w:
            sc.add(rect(0, 0, 0, 0) + nuqta(x, y, U * 0.30), {"PRINT", "PRINT-FLAT"}, ink=SAPPHIRE_LINE)
            x += step
        y += step * 0.5
        row += 1
    sc.add(rect(0, b + BASE - 0.12, w, 0.24), {"PRINT", "PRINT-FLAT"}, ink=SAPPHIRE_LINE)
    for plate in ("PRINT",):
        write(sc, plate, OUT / "Endpapers_PRINT.pdf", f"{FM.TITLE} — endpapers (all volumes)")
    return OUT / "Endpapers_PRINT.pdf"


def main(argv):
    vols = [int(a) for a in argv if a.isdigit()] or list(range(1, 12))
    OUT.mkdir(exist_ok=True)
    faces = Faces()
    spines_path = OUT / "spines.json"
    spines = json.loads(spines_path.read_text()) if spines_path.exists() else {}
    for n in vols:
        sc, sw = build(n, faces)
        lay = sc.layout
        spines[str(n)] = dict(pages=pages(n), binding=SPEC["binding"], caliper_mm_per_leaf=CALIPER,
                              block_mm=round(block_mm(n), 1), spine_mm=sw, wrap_mm=[round(sc.w, 1), round(sc.h, 1)],
                              front=[round(v, 2) for v in lay["front"]], spine=[round(v, 2) for v in lay["spine"]],
                              back=[round(v, 2) for v in lay["back"]], margin_mm=lay["margin"], joint_mm=lay["joint"],
                              isbn=isbn_of(n)[0], isbn_printed=isbn_of(n)[1],
                              status="provisional: from covers/printer-spec.json until the printer confirms it")
        for plate in PLATES:
            path = OUT / f"Cover-{n:02d}_{LATIN[n]}_{plate}.pdf"
            write(sc, plate, path, f"{FM.TITLE} — {FM.volume_line(n)} — {plate}")
        print(f"volume {n}: spine {sw} mm, wrap {sc.w:.1f} × {sc.h:.1f} mm")
    spines_path.write_text(json.dumps(dict(sorted(spines.items(), key=lambda kv: int(kv[0]))), ensure_ascii=False, indent=1))
    endpapers()


if __name__ == "__main__":
    main(sys.argv[1:])
