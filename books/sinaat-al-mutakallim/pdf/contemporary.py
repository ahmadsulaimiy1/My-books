#!/usr/bin/env python3
"""Edition 3 of the covers, Contemporary: «عمارة السطر», the architecture of the Arabic line (Bible, ch. 25 §14).

The cleanest of the three editions, and deliberately so. On a field of sapphire left open, the volume's name is
built as the architecture of Arabic writing (linearch.py): its verticals are engraved uprights crowned by a
floating gold dot, its teeth and knots stand on one line, its bowls hang below it, and the construction that made
it stays visible as an architect's drawing keeps its lines: the plumb lines from the title's rule to each dot, the
compass of each bowl, the module's scale. One ruby dot, where the nib first touches, and nothing added for show:
the luxury is proportion, scale, precision, material and the open field.

The line the word stands on runs on: from the front across the spine, where it stands at one height on all eleven
so the shelf reads as one line, and onto the back, where the eleven volumes stand on it as eleven uprights and the
line pauses (as Arabic writing pauses at a letter that will not join) to leave the ISBN zone clear.

The title, the seal and the words of the back are shared with the other editions (coverart.py, matn.back_words).
"""
from __future__ import annotations

import math

import numpy as np
from shapely.geometry import box
from shapely.ops import unary_union

import artwork as AW
import coverart as CA
import frontmatter as FM
import illumination as IL
import linearch as LA
import typeset as T

W, H = 170.0, 240.0
BASE = 192.0                 # the line the words stand on, front and spines
TITLE_RULE = 104.0           # the rule under the subtitle, where the plumb lines hang from
MEASURE = 128.0              # the widest a name may be built
U_MAX = 9.2                  # the module of the approved front (vol. 2): the most a name is built at
FRAME = 9.5


def faces():
    return CA.faces()


# ------------------------------------------------------------------------------------------------ the name as architecture
def _split(spec):
    """A name of two words, as two lines: its elements, dots and ruby re-counted for each."""
    els = spec["els"]
    cut = next(i for i, el in enumerate(els) if el[0] == "|" and len(el) > 1 and el[1] == "word")
    out = []
    for lo, hi in ((0, cut), (cut + 1, len(els))):
        out.append(dict(word=spec["word"], els=els[lo:hi],
                        dots=[(i - lo, w, k) for (i, w, k) in spec["dots"] if lo <= i < hi],
                        ruby=[(i - lo, w) for (i, w) in spec["ruby"] if lo <= i < hi]))
    return out


def lines_of(n):
    """The lines of volume n's name, each (spec, module u, baseline): one line set to the measure; the eighth's two
    words on two lines at one module."""
    spec = LA.NAMES[n]
    if any(el[0] == "|" and len(el) > 1 and el[1] == "word" for el in spec["els"]):
        parts = _split(spec)
        wd = max(ink(p, 1.0)[1] for p in parts)
        u = min(U_MAX, MEASURE / wd, 4.4)
        return [(parts[0], u, BASE - 10.4 * u), (parts[1], u, BASE)]
    wd = ink(spec, 1.0)[1]
    return [(spec, min(U_MAX, MEASURE / wd), BASE)]


def ink(spec, u):
    """Where the built name actually reaches, at module u with its right end at 0: (left, width), counting its
    struts, dots and ruby as well as its letters (so it is centred on what the eye sees)."""
    A = LA.Arch(spec, u, 0.0, 0.0)
    xs = [g.bounds[0] for (k, g, _) in A.parts if k in ("pillar", "tooth", "arch", "knot", "finial")]
    xs += [b.bounds[0] for b in A.beams] + [x - 0.6 * u for (x, _, _) in A.dots] + [x - 0.4 * u for (x, _) in A.rubies]
    xr = [g.bounds[2] for (k, g, _) in A.parts if k in ("pillar", "tooth", "arch", "knot", "finial")] + [b.bounds[2] for b in A.beams]
    left, right = min(xs + [A.x_left]), max(xr + [0.0])
    return left, right - left


def frame(P):
    outer = box(FRAME, FRAME, W - FRAME, H - FRAME)
    P.gold(IL.band(outer, 0, -0.7, join=2))
    P.pearl(IL.band(outer, -1.6, -1.78, join=2))
    return outer.buffer(-2.6, join_style=2)


def front(n):
    F = faces()
    P = CA.Page()
    field = frame(P)
    ordinal, name = FM.VOLUMES[n - 1][:2]
    rub, _ = T.text(f"المجلد {ordinal}", F.changa4, 3.0, cx=W / 2, base=31.0)
    P.ink(rub, AW.CHAMPAGNE_INK)
    CA.set_title(P, W / 2, [("صناعة", 20.0, 60.0), ("المتكـلّم العربي", 12.2, 82.0)])
    sub, _ = T.text(FM.SUBTITLE, F.sch4, 4.3, cx=W / 2, base=96.0)
    P.ink(sub, AW.PEARL_SOFT)
    P.gold(box(40, TITLE_RULE - 0.12, W - 40, TITLE_RULE + 0.12))
    lines = lines_of(n)
    for i, (spec, u, base) in enumerate(lines):
        left, wd = ink(spec, u)
        A = LA.Arch(spec, u, base, W / 2 - left - wd / 2, fullness=0.8)
        last = i == len(lines) - 1
        LA.render(P, A, field=field, title_line=TITLE_RULE if i == 0 else lines[0][2] + 3.0 * u,
                  lead_in=last, echo=last, construction=True, reflect=False)
    au, _ = T.text(FM.AUTHOR_SHORT, F.sch6, 4.2, cx=W / 2, base=222.0)
    P.ink(au, AW.PEARL_INK)
    u0, b0 = lines[-1][1], lines[-1][2]
    P.L.glow.append((W / 2, b0 - 3.5 * u0, 70, 0.7))
    return P, field


# ------------------------------------------------------------------------------------------------ the spine
def spine(n, sw):
    """The spine: the title; a floating gold dot on its plumb line over the volume's number and name; the line at
    one height on all eleven, its pulses growing with the volumes; the author and the house."""
    F = faces()
    P = CA.Page()
    cx = sw / 2
    for yb in (FRAME, H - FRAME):
        P.gold(box(-0.2, yb - 0.35, sw + 0.2, yb + 0.35))
        P.pearl(box(-0.2, yb + (1.25 if yb < H / 2 else -1.25) - 0.08, sw + 0.2, yb + (1.25 if yb < H / 2 else -1.25) + 0.08))
    fit = min(1.0, (sw - 7.0) / 26.0)
    CA.set_title(P, cx, [("صناعة", 7.6 * fit, 28.0), ("المتكلّم", 5.0 * fit, 39.0), ("العربي", 5.0 * fit, 48.0)],
                 floriation=False, emboss=True, dot_scale=1.5)
    LA.jewel(P, cx, 66.0, 3.2)
    P.cold(box(cx - 0.05, 68.6, cx + 0.05, 77.0), 0.75)
    ng, _ = T.text(str(n), F.amiri7, 15.0 * fit, cx=cx, base=97.0, digits=True)
    P.pearl(ng)
    P.emboss(ng, 1.0)
    label = {8: "المجالس والمنبر", 11: "المرجع"}.get(n, FM.VOLUMES[n - 1][1])
    ln = T.line(label, F.kufi6, 5.0, features=T.KF)
    size = 5.0 * min(1.0, (sw - 5.0) / ln.width)
    g, _ = T.text(label, F.kufi6, size, cx=cx, base=114.0, features=T.KF)
    P.pearl(g)
    P.cold(box(cx - 0.05, 119.0, cx + 0.05, BASE - 0.4), 0.75)
    line_and_pulses(P, n, 0.0, sw)
    y = 209.0
    for part in ("أحمد بن", "إبراهيم", "السليمي"):
        g, _ = T.text(part, F.sch6, 3.3, cx=cx, base=y)
        P.ink(g, AW.PEARL_INK)
        y += 4.6
    for g in CA.seal(cx, 225.0, small=True):
        P.gold(g)
    return P


def line_and_pulses(P, n, x0, x1):
    """The line at BASE from x0 to x1, its echoes under it, and on it the voice's pulses: sparse on the first
    volume, full on the tenth and the reference (the pulses keep one spacing along the shelf)."""
    P.gold(box(x0 - 0.2, BASE - 0.26, x1 + 0.2, BASE + 0.26))
    for k, off in enumerate((0.9, 1.9, 3.1, 4.5)):         # as the front's echoes run under its word
        yy = BASE + off * 2.3
        P.cold(box(x0 - 0.2, yy - 0.06, x1 + 0.2, yy + 0.06), 0.8 - 0.1 * k)
    share = min(n, 10) / 10.0
    step = 3.3
    for i, xv in enumerate(np.arange(x0 + 1.6, x1 - 1.0, step)):
        phase = (i * 0.9 + n * 1.7)
        if (math.sin(phase * 2.3) * 0.5 + 0.5) > share:
            continue
        hgt = (0.9 + 5.2 * (0.5 + 0.5 * math.sin(phase))) * (0.45 + 0.55 * share)
        w = 0.18
        P.cold(box(xv - w / 2, BASE - 0.3 - hgt, xv + w / 2, BASE - 0.3), 0.85)


# ------------------------------------------------------------------------------------------------ the back
def back(n):
    """The back: the same open field; what the book says; the line coming from the spine, pausing at the ISBN zone,
    and carrying the eleven volumes as eleven uprights, this one crowned; the house."""
    import matn
    F = faces()
    P = CA.Page()
    field = frame(P)
    right = W - 24.0
    y = matn.back_words(P, n, right, W - 48.0, 40.0)
    if y > 160.0:
        raise SystemExit(f"back {n}: the words overrun the field ({y:.1f} mm)")
    zx, zy, zw, zh = CA.ISBN_ZONE
    # the line: from the spine edge to the zone, where it pauses on a dot; and on again past it to the fore-edge
    P.gold(box(-0.2, BASE - 0.26, zx - 3.0, BASE + 0.26))
    P.gold(AW.nuqta(zx - 1.6, BASE, 1.6, 70))
    x_on = zx + zw + 3.0
    P.gold(AW.nuqta(x_on - 1.4, BASE, 1.6, 70))
    P.gold(box(x_on, BASE - 0.26, W - FRAME - 3.0, BASE + 0.26))
    # the eleven, standing on the line from the fore-edge side (the first at the right, as the shelf reads)
    slot = 7.4
    for v in range(1, 12):
        x = W - FRAME - 9.0 - (v - 1) * slot
        h = 10.0 + 1.3 * min(v, 10)
        if v == 11:
            h = 10.0
        up = box(x - 0.9, BASE - 0.3 - h, x + 0.9, BASE - 0.3)
        if v == n:
            P.gold(up)
            LA.jewel(P, x, BASE - h - 3.4, 2.6)
            P.emboss(up, 0.85)
        else:
            P.cold(IL.band(up, 0.0, -0.16, join=2), 0.7)
        g, _ = T.text(str(v), F.amiri4, 2.6, cx=x, base=BASE + 5.0, digits=True)
        P.ink(g, AW.CHAMPAGNE_INK if v != n else AW.PEARL_INK)
    for g in CA.seal(126.0, 207.0):
        P.gold(g)
    pub, _ = T.text(FM.PUBLISHER_AR, F.sch4, 3.2, cx=126.0, base=215.5)
    P.ink(pub, AW.PEARL_SOFT)
    ed, _ = T.text(f"{FM.EDITION}، {FM.YEAR}", F.sch4, 2.9, cx=126.0, base=220.5)
    P.ink(ed, AW.PEARL_SOFT)
    P.arch.append(box(zx - 1, zy - 1, zx + zw + 1, zy + zh + 1))
    P.L.glow.append((W / 2, 90.0, 70.0, 0.55))
    return P, field


# ------------------------------------------------------------------------------------------------ the wrap
def wrap(n, sw, lay, widths=None):
    """The wrap of volume n in the wrap's coordinates (covers.py lays it on the binding)."""
    L = AW.Layers()
    P, _ = front(n)
    L.extend(CA.translate(P.L, *lay["front_art"]))
    B, _ = back(n)
    L.extend(CA.translate(B.L, *lay["back_art"]))
    S = spine(n, sw)
    L.extend(CA.translate(S.L, lay["spine"][0], lay["art_top"]))
    return L


def endpaper_layers(w, h):
    """The endpapers: the open sapphire, and across the spread in its own tone the module's scale, the lines the
    words are built on, with one plumb line and its dot. Returns the layers and the light."""
    L = AW.Layers()
    rules = [box(10.0, y - 0.06, w - 10.0, y + 0.06) for y in np.arange(40.0, h - 30.0, 9.2)]
    L.body.append((AW.valid(unary_union(rules)), ("lift", 0.06)))
    L.body.append((box(w * 0.62 - 0.05, 30.0, w * 0.62 + 0.05, h - 40.0), ("lift", 0.08)))
    L.body.append((AW.nuqta(w * 0.62, 26.0, 3.0, 70), ("lift", 0.1)))
    return L, [(w / 2, h * 0.45, 140, 0.25)]
