#!/usr/bin/env python3
"""«عمارة السطر» — the architecture of the Arabic line, the master artwork of the covers (Bible, ch. 25 §13).

Arabic writing is already an architecture: a line that the letters stand on and join along; verticals that rise
from it; small teeth in rhythm; bowls that descend below it; closed knots; breaks where a letter will not join
its neighbour, which are the pauses of the line; the extension (المدّ) that stretches a join in emphasis; and the
dots, floating in exact relation above and below. This module builds each volume's name as that architecture, not
as calligraphy: the verticals become fluted pillars of engraved gold, joined to the line by a curved foot and
crowned by a floating dot; the teeth become denticles; the bowls become arches hung beneath the line; the knots
become rings of pearl; the joins become a gold beam cut at the nib's angle where the word pauses; the dots hang on
plumb lines that show where they belong; and the construction that made it stays visible, as an architect's
drawing keeps its lines: the seven-dot module, the guides, the compass arcs of the bowls.

Read from right to left the line tells الصوت → اللفظ → العبارة → البيان → الأثر: it is born at the spine as
pulses of sound, rises into the word, extends, and leaves its trace in lines that echo toward the fore-edge.

Every element is a set of shapely geometries with their materials (artwork.Layers via coverart.Page).
"""
from __future__ import annotations

import math

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import artwork as AW
import illumination as IL

TAU = 2 * math.pi

# the architecture of each volume's name, letter by letter from the right: (kind, parameters)
#   P h            a pillar h modules high (alif, lam, the upright of kaf, ta, zha); "fin": a floating finial dot
#   L h            a pillar with a lintel to the left (kaf)
#   X              lam-alif: two pillars crossing
#   T n            n denticles (the teeth of ba, ta, nun, ya, sin in the middle of a word)
#   O              a knot: a ring on the line (mim, the medial loops, waw's head, ta marbuta)
#   Q              a raised knot on a short stem (qaf, fa)
#   U w d          a bowl: an arch hung below the line, w wide and d deep (final nun, ya, lam, the tails)
#   S              a strut below the line (ra, za, waw's tail)
#   D              a step: the low angle of dal
#   C              a cup open above the line (initial ain)
#   H              a hook on the line (medial ha, jim)
#   E w            an extension: the beam stretched w modules
#   |              a pause: the line breaks (a letter that will not join, or the space between words)
# dots: (index of the element, "above" | "below", count); ruby: (index, "above" | "below" | "front")
NAMES = {
    1: dict(word="الأصول", els=[("P", 7), ("|",), ("P", 7, "join"), ("E", 1.2), ("P", 7, "hamza"), ("|",), ("O", "long"), ("E", 0.8),
                               ("O",), ("S",), ("|",), ("P", 7), ("U", 3.2, 2.6)],
            dots=[], ruby=[(12, "front")]),
    2: dict(word="اللسان", els=[("P", 7), ("|",), ("P", 7, "join"), ("P", 7, "join"), ("T", 3), ("E", 1.6), ("P", 7), ("|",), ("U", 3.4, 2.8)],
            dots=[(8, "above", 1)], ruby=[(8, "front")]),
    3: dict(word="العبارة", els=[("P", 7), ("|",), ("P", 7, "join"), ("O", "small"), ("T", 1), ("E", 1.2), ("P", 7), ("|",), ("S",), ("|",), ("O",)],
            dots=[(4, "below", 1), (10, "above", 2)], ruby=[(10, "front")]),
    4: dict(word="البيان", els=[("P", 7), ("|",), ("P", 7, "join"), ("T", 1), ("T", 1), ("E", 1.8), ("P", 7), ("|",), ("U", 3.4, 2.8)],
            dots=[(3, "below", 1), (4, "below", 2), (8, "above", 1)], ruby=[(8, "front")]),
    5: dict(word="المقام", els=[("P", 7), ("|",), ("P", 7, "join"), ("O",), ("Q",), ("E", 1.4), ("P", 7), ("|",), ("O",), ("S",)],
            dots=[(4, "above", 2)], ruby=[(8, "front")]),
    6: dict(word="الأدب", els=[("P", 7), ("|",), ("X",), ("|",), ("D",), ("|",), ("T", 1), ("E", 2.6)],
            dots=[(6, "below", 1)], ruby=[(6, "front")]),
    7: dict(word="الحوار", els=[("P", 7), ("|",), ("P", 7, "join"), ("H",), ("E", 1.0), ("O",), ("S",), ("|",), ("P", 7), ("|",), ("S",)],
            dots=[], ruby=[(10, "front")]),
    8: dict(word="المجالس والمنبر", els=[("P", 7), ("|",), ("P", 7, "join"), ("O",), ("H",), ("E", 1.0), ("P", 7), ("|",), ("P", 7, "join"), ("T", 3), ("U", 2.6, 2.0),
                                          ("|", "word"), ("O",), ("S",), ("|",), ("P", 7), ("|",), ("P", 7, "join"), ("O",), ("T", 1), ("T", 1), ("E", 1.0), ("S",)],
            dots=[(4, "below", 1), (19, "above", 1), (20, "below", 1)], ruby=[(22, "front")]),
    9: dict(word="المؤسسة", els=[("P", 7), ("|",), ("P", 7, "join"), ("O",), ("O", "hamza"), ("S",), ("|",), ("T", 3), ("T", 3), ("E", 0.8), ("O",)],
            dots=[(10, "above", 2)], ruby=[(10, "front")]),
    10: dict(word="التمكين", els=[("P", 7), ("|",), ("P", 7, "join"), ("T", 1), ("O",), ("L", 5.5), ("T", 1), ("E", 1.4), ("U", 3.4, 2.8)],
             dots=[(3, "above", 2), (6, "below", 2), (8, "above", 1)], ruby=[(8, "front")]),
    11: dict(word="المرجع", els=[("P", 7), ("|",), ("P", 7, "join"), ("O",), ("S",), ("|",), ("H",), ("E", 1.2), ("C",), ("U", 2.6, 2.4)],
             dots=[(6, "below", 1)], ruby=[(9, "front")]),
}


class Arch:
    """The architecture of one line, built at module u (mm) on the baseline y = base, its right end at x_right."""

    def __init__(self, spec, u, base, x_right, fullness=1.0):
        self.spec, self.u, self.base, self.x_right = spec, u, base, x_right
        self.fullness = fullness             # 0: the drawing only … 1: fully gilded
        self.parts = []                      # (kind, geometry, role) — role picks the material
        self.anchors = []                    # per element: (x_centre, top_y, bottom_y)
        self.beams = []
        self._build()

    # ---- the pieces
    def pillar(self, x, h, join=False, hamza=False):
        u, b = self.u, self.base
        w0, w1 = 0.60 * u, 0.48 * u
        top = b - h * u
        # the shaft with its entasis, its pointed Kufic head, a plinth where it stands and a band under the head
        shaft = Polygon([(x - w0 / 2, b), (x + w0 / 2, b), (x + w1 / 2, top + 0.55 * u), (x + w1 / 2, top + 0.25 * u),
                         (x, top), (x - w1 / 2, top + 0.25 * u), (x - w1 / 2, top + 0.55 * u)])
        plinth = box(x - 0.46 * u, b - 0.32 * u, x + 0.46 * u, b)
        band = box(x - w1 / 2 - 0.09 * u, top + 0.62 * u, x + w1 / 2 + 0.09 * u, top + 0.84 * u)
        parts = [shaft, plinth, band]
        # the foot: a curved fillet into the line toward the left (the join), or a small spur
        r = 0.75 * u if join else 0.35 * u
        foot = Point(x - w0 / 2 - r, b - r).buffer(r, resolution=32)
        fillet = box(x - w0 / 2 - r, b - r, x - w0 / 2, b).difference(foot)
        parts.append(fillet)
        g = AW.valid(unary_union(parts))
        self.parts.append(("pillar", g, h))
        # its head: the finial dot floating above (the tarwis of the Kufic upright made a dot)
        fin = AW.nuqta(x, top - 1.15 * u, 0.78 * u, 70)
        self.parts.append(("finial", fin, None))
        if hamza:
            ring = Point(x - 0.95 * u, top + 1.4 * u).buffer(0.34 * u).difference(Point(x - 0.95 * u, top + 1.4 * u).buffer(0.2 * u))
            self.parts.append(("knot", AW.valid(ring), None))
        return x - w0 / 2 - (r if join else 0.0), top

    def lintel(self, x, h):
        u, b = self.u, self.base
        x_end, top = self.pillar(x, h, join=True)
        lin = box(x - 3.2 * u, top + 0.1 * u, x + 0.2 * u, top + 0.46 * u)
        self.parts.append(("beam", lin, None))
        return x_end, top

    def crossed(self, x):
        """lam-alif: two uprights crossing above the line, their feet joined."""
        u, b = self.u, self.base
        w = 0.40 * u
        top = b - 7 * u
        a = Polygon([(x - 1.9 * u, b), (x - 1.9 * u + w, b), (x + 0.9 * u + w / 2, top), (x + 0.9 * u - w / 2, top)])
        c = Polygon([(x + 0.3 * u, b), (x + 0.3 * u + w, b), (x - 2.3 * u + w / 2, top), (x - 2.3 * u - w / 2, top)])
        self.parts.append(("pillar", AW.valid(unary_union([a, c])), 7))
        self.parts.append(("finial", AW.nuqta(x + 0.9 * u, top - 1.05 * u, 0.62 * u, 70), None))
        self.parts.append(("finial", AW.nuqta(x - 2.3 * u, top - 1.05 * u, 0.62 * u, 70), None))
        return x - 2.4 * u, top

    def teeth(self, x, n):
        u, b = self.u, self.base
        step = 0.95 * u
        xs = [x - 0.35 * u - i * step for i in range(n)]
        for xi in xs:
            t = Polygon([(xi - 0.18 * u, b), (xi + 0.18 * u, b), (xi + 0.14 * u, b - 1.45 * u), (xi, b - 1.7 * u), (xi - 0.14 * u, b - 1.45 * u)])
            self.parts.append(("tooth", t, 1.7))
        return xs[-1] - 0.35 * u, b - 1.7 * u

    def knot(self, x, form=None):
        u, b = self.u, self.base
        rw = 0.95 * u if form != "long" else 1.8 * u
        rh = 0.95 * u
        cx = x - rw - 0.1 * u
        cy = b - rh * 0.95
        outer = affinity.scale(Point(cx, cy).buffer(1.0, resolution=48), rw, rh, origin=(cx, cy))
        inner = affinity.scale(Point(cx, cy).buffer(1.0, resolution=48), rw - 0.34 * u, rh - 0.34 * u, origin=(cx, cy))
        self.parts.append(("knot", AW.valid(outer.difference(inner)), None))
        if form == "hamza":
            h = Point(cx + 0.2 * u, cy - 1.9 * u).buffer(0.3 * u).difference(Point(cx + 0.2 * u, cy - 1.9 * u).buffer(0.17 * u))
            self.parts.append(("knot", AW.valid(h), None))
        return cx - rw, cy - rh

    def raised_knot(self, x):
        u, b = self.u, self.base
        stem = box(x - 0.9 * u, b - 1.3 * u, x - 0.55 * u, b)
        self.parts.append(("tooth", stem, 1.3))
        cx, cy = x - 1.2 * u, b - 2.4 * u
        ring = Point(cx, cy).buffer(0.85 * u, resolution=48).difference(Point(cx, cy).buffer(0.52 * u, resolution=48))
        self.parts.append(("knot", AW.valid(ring), None))
        return x - 2.1 * u, b - 3.3 * u

    def bowl(self, x, w, d):
        """An arch hung below the line: the bowl of a final letter, and its compass circle kept as construction."""
        u, b = self.u, self.base
        cx = x - w * u / 2
        rx, ry = w * u / 2, d * u
        th = np.linspace(0, math.pi, 120)
        outer = [(cx + rx * math.cos(t), b + ry * math.sin(t)) for t in th]
        inner = [(cx + (rx - 0.42 * u) * math.cos(t), b + (ry - 0.42 * u) * math.sin(t)) for t in th[::-1]]
        arch = AW.valid(Polygon(outer + inner))
        self.parts.append(("arch", arch, None))
        # the voussoirs: radial joints across the band, and the keystone at its foot
        joints = []
        for t in np.linspace(0.12, math.pi - 0.12, 11):
            p0 = (cx + (rx - 0.42 * u) * math.cos(t), b + (ry - 0.42 * u) * math.sin(t))
            p1 = (cx + rx * math.cos(t), b + ry * math.sin(t))
            joints.append(LineString([p0, p1]).buffer(0.06))
        self.parts.append(("joints", AW.valid(unary_union(joints)), None))
        self.parts.append(("keystone", AW.nuqta(cx, b + ry + 0.9 * u, 0.7 * u, 90), None))
        circle = affinity.scale(Point(cx, b).buffer(1.0, resolution=96), rx, ry, origin=(cx, b))
        self.parts.append(("compass", AW.valid(circle.exterior.buffer(0.06)), None))
        return x - w * u, b + ry

    def strut(self, x):
        u, b = self.u, self.base
        s = Polygon([(x - 0.2 * u, b - 0.3 * u), (x + 0.25 * u, b - 0.3 * u), (x - 1.1 * u, b + 1.9 * u), (x - 1.5 * u, b + 1.7 * u)])
        self.parts.append(("pillar", AW.valid(s), 2))
        return x - 1.5 * u, b + 1.9 * u

    def step(self, x):
        u, b = self.u, self.base
        s = Polygon([(x, b), (x - 0.35 * u, b - 1.9 * u), (x - 0.05 * u, b - 2.05 * u), (x + 0.35 * u, b - 0.35 * u), (x - 1.6 * u, b - 0.35 * u), (x - 1.6 * u, b)])
        self.parts.append(("pillar", AW.valid(s), 2))
        return x - 1.6 * u, b - 2.05 * u

    def cup(self, x):
        u, b = self.u, self.base
        cx, cy = x - 1.0 * u, b - 1.3 * u
        th = np.linspace(math.pi * 0.15, math.pi * 1.0, 80)
        outer = [(cx + 1.0 * u * math.cos(t), cy - 1.0 * u * math.sin(t)) for t in th]
        inner = [(cx + 0.64 * u * math.cos(t), cy - 0.64 * u * math.sin(t)) for t in th[::-1]]
        self.parts.append(("arch", AW.valid(Polygon(outer + inner)), None))
        return x - 2.0 * u, cy - u

    def hook(self, x):
        u, b = self.u, self.base
        s = Polygon([(x, b - 0.4 * u), (x - 1.8 * u, b - 1.9 * u), (x - 1.5 * u, b - 2.2 * u), (x + 0.3 * u, b - 0.75 * u)])
        self.parts.append(("pillar", AW.valid(s), 2))
        return x - 1.8 * u, b - 2.2 * u

    # ---- the line
    def _build(self):
        u, b = self.u, self.base
        x = self.x_right
        seg_start = x
        self.segments = []            # the beam's runs between pauses: (x_right, x_left)
        for i, el in enumerate(self.spec["els"]):
            k = el[0]
            x0 = x
            if k == "P":
                h = el[1]
                join = len(el) > 2 and el[2] == "join"
                hamza = len(el) > 2 and el[2] == "hamza"
                x_end, top = self.pillar(x - 0.3 * u, h, join=join, hamza=hamza)
                x = x_end - 0.2 * u
                self.anchors.append((x0 - 0.3 * u, top, b))
            elif k == "L":
                x_end, top = self.lintel(x - 0.3 * u, el[1])
                x = x_end - 2.6 * u
                self.anchors.append((x0 - 0.3 * u, top, b))
            elif k == "X":
                x_end, top = self.crossed(x - 0.6 * u)
                x = x_end - 0.4 * u
                self.anchors.append((x0 - 1.2 * u, top, b))
            elif k == "T":
                x_end, top = self.teeth(x, el[1])
                self.anchors.append(((x0 + x_end) / 2, top, b))
                x = x_end
            elif k == "O":
                x_end, top = self.knot(x, el[1] if len(el) > 1 else None)
                self.anchors.append(((x0 + x_end) / 2, top, b))
                x = x_end
            elif k == "Q":
                x_end, top = self.raised_knot(x)
                self.anchors.append(((x0 + x_end) / 2, top, b))
                x = x_end
            elif k == "U":
                x_end, bot = self.bowl(x, el[1], el[2])
                self.anchors.append(((x0 + x_end) / 2, b - 0.4 * u, bot))
                x = x_end
            elif k == "S":
                x_end, bot = self.strut(x)
                self.anchors.append(((x0 + x_end) / 2, b, bot))
                x = x_end
            elif k == "D":
                x_end, top = self.step(x)
                self.anchors.append(((x0 + x_end) / 2, top, b))
                x = x_end
            elif k == "C":
                x_end, top = self.cup(x)
                self.anchors.append(((x0 + x_end) / 2, top, b))
                x = x_end
            elif k == "H":
                x_end, top = self.hook(x)
                self.anchors.append(((x0 + x_end) / 2, top, b))
                x = x_end
            elif k == "E":
                self.anchors.append(((x0 + x0 - el[1] * u) / 2, b, b))
                x = x - el[1] * u
            elif k == "|":
                self.segments.append((seg_start, x))
                gap = 2.2 * u if (len(el) > 1 and el[1] == "word") else 1.1 * u
                self.anchors.append((x - gap / 2, b, b))
                x = x - gap
                seg_start = x
        self.segments.append((seg_start, x))
        self.x_left = x
        # the beam: the joins, each run cut at the nib's angle at its ends
        t = 0.50 * u
        a = math.tan(math.radians(20.0)) * t
        for (xr, xl) in self.segments:
            if xr - xl < 0.8 * u:
                continue
            beam = Polygon([(xr, b), (xr - a, b - t), (xl + 0.0, b - t), (xl - a, b)])
            self.beams.append(AW.valid(beam))
        # dots and ruby
        self.dots = []
        for (idx, where, count) in self.spec.get("dots", []):
            cx, top, bot = self.anchors[idx]
            for j in range(count):
                dx = (j - (count - 1) / 2) * 1.05 * u
                y = (top - 1.3 * u) if where == "above" else (bot + 1.5 * u)
                self.dots.append((cx + dx, y, where))
        self.rubies = []
        for (idx, where) in self.spec.get("ruby", []):
            cx, top, bot = self.anchors[idx]
            if where == "front":
                x_front = min(self.x_left + 0.6 * u, cx - 1.9 * u)
                self.rubies.append((x_front, b - 1.1 * u))
            elif where == "above":
                self.rubies.append((cx, top - 1.6 * u))
            else:
                self.rubies.append((cx, bot + 1.6 * u))

    def geometry(self):
        return AW.valid(unary_union([g for (_, g, _) in self.parts if _ != "compass"] + self.beams))


DEPTH = (-0.95, -0.65)         # the thickness of the gold, seen toward the upper left, where the light is


def extrude(g, d=DEPTH):
    """The sides of a flat piece given thickness: for each edge, the face it sweeps; returned with how much each
    face turns to the light (1 lit, 0 in shadow)."""
    from shapely.geometry.polygon import orient
    faces = []
    for poly in AW.poly_list(g):
        ring = list(orient(poly, 1.0).exterior.coords)
        for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
            q = Polygon([(x0, y0), (x1, y1), (x1 + d[0], y1 + d[1]), (x0 + d[0], y0 + d[1])])
            if q.area < 1e-4:
                continue
            ex, ey = x1 - x0, y1 - y0
            L = math.hypot(ex, ey) or 1
            nx, ny = ey / L, -ex / L
            faces.append((AW.valid(q), max(0.0, min(1.0, 0.5 + 0.5 * (-0.6 * nx - 0.8 * ny)))))
    return faces


def jewel(P, x, y, size, phi=70.0):
    """The nib's dot cut as a jewel: the rhombus in gold, its four facets parted by fine lines, pressed up."""
    d = AW.nuqta(x, y, size, phi)
    a = math.radians(phi)
    ux, uy = math.cos(a) * size / 2, -math.sin(a) * size / 2
    vx, vy = math.sin(a) * size * 0.36, math.cos(a) * size * 0.36
    cuts = unary_union([LineString([(x + ux, y + uy), (x - ux, y - uy)]).buffer(0.05),
                        LineString([(x + vx, y + vy), (x - vx, y - vy)]).buffer(0.05)])
    P.gold(d.difference(cuts))
    P.emboss(d, 1.0)
    return d


def render(P, A, *, field, title_line=None, lead_in=True, echo=True, construction=True, reflect=True):
    """Lay the architecture A onto the page P with its materials. field: the page's area (the construction is
    clipped to it); title_line: the y of the title's baseline, where the guides rise to."""
    u, b = A.u, A.base
    body = A.geometry()
    x0, y0, x1, y1 = body.bounds
    full = A.fullness
    fx0, fy0, fx1, fy1 = field.bounds
    # ---- construction (under everything): the module scale with its numerals, the guides, the compass arcs
    if construction:
        import typeset as T
        F = T.Faces()
        for k in range(0, 8):
            yk = b - k * u
            ln = box(fx0 + 7.5, yk - 0.05, fx1 - 7.5, yk + 0.05)
            P.L.body.append((ln, ("lift", 0.12 if k else 0.0)))
            for xe, al in ((fx0 + 3.6, "c"), (fx1 - 3.6, "c")):
                if k:
                    g, _ = T.text(str(k), F.amiri4, 2.1, cx=xe, base=yk + 0.75, digits=True)
                    P.ink(g, AW.CHAMPAGNE_INK)
                P.cold(box(xe - 1.3 if xe < 85 else xe - 1.3, yk - 0.05, xe + 1.3, yk + 0.05), 0.7)
        top_guides = title_line if title_line is not None else y0 - 12
        for (kind, g, h) in A.parts:
            if kind == "pillar" and h and h >= 5:
                gx0, gy0, gx1, gy1 = g.bounds
                xm = (gx0 + gx1) / 2
                P.cold(box(xm - 0.05, top_guides + 1.5, xm + 0.05, gy0 - 2.2 * u), 0.75)
            if kind == "compass":
                P.cold(g.intersection(field), 0.7)
        for (dx, dy, where) in A.dots:
            if where == "above":
                P.cold(box(dx - 0.045, dy + 0.6 * u, dx + 0.045, b - 0.2 * u), 0.7)
            else:
                P.cold(box(dx - 0.045, b + 0.2 * u, dx + 0.045, dy - 0.6 * u), 0.7)
    elems = [g for (kind, g, _) in A.parts if kind in ("pillar", "tooth", "arch")] + A.beams
    solid = AW.valid(unary_union(elems))
    # ---- the trace (الأثر): the architecture mirrored below the line, engraved in the ground's own tone, fading
    if reflect:
        mirror = affinity.scale(unary_union([g for (kind, g, _) in A.parts if kind in ("pillar", "tooth")]), 1, -0.55, origin=(0, b))
        mirror = affinity.translate(mirror, 0, 1.2 * u)
        lines = []
        for yv in np.arange(b + 1.3 * u, b + 4.6 * u, 0.55):
            f = (yv - b) / (4.6 * u)
            lines.append(box(fx0, yv - 0.07 * (1.1 - f), fx1, yv + 0.07 * (1.1 - f)))
        P.L.body.append((AW.valid(unary_union(lines)).intersection(mirror), ("lift", 0.16)))
    # ---- the prelude: pulses of sound along the line at the spine side, rising toward the word
    if lead_in:
        xs = np.arange(x1 + 1.1 * u, fx1 - 7.5, 0.36 * u)
        for i, xv in enumerate(xs):
            f = 1.0 - i / max(1, len(xs) - 1)
            # the voice before the word: pulses rising and falling in a breath, larger as they reach the word
            hgt = (0.15 + 2.6 * f ** 2.2) * u * (0.55 + 0.45 * abs(math.sin(i * 0.9)))
            w = 0.10 + 0.14 * f
            P.cold(box(xv - w / 2, b - hgt, xv + w / 2, b), 0.85)
            P.cold(box(xv - w / 2, b + 0.35 * u, xv + w / 2, b + 0.35 * u + 0.28 * hgt), 0.6)
    # ---- the extension and its echoes toward the fore-edge
    if echo:
        xl = fx0 + 7.5
        P.gold(box(xl, b - 0.26, x0 - 0.4 * u, b + 0.26))
        for k, off in enumerate((0.9, 1.9, 3.1, 4.5)):
            yy = b + off * u * 0.5
            L = (x0 - xl) * (1.0 - 0.2 * k)
            P.cold(box(x0 - 0.4 * u - L, yy - 0.06, x0 - 0.4 * u, yy + 0.06), 0.8)
    # ---- depth: the gold's thickness, lit toward the light
    for (q, lit) in sorted(extrude(solid), key=lambda f: f[1]):
        if lit > 0.55:
            P.gold(q.difference(solid))
        else:
            P.ink(q.difference(solid), AW.ANTIQUE_INK)
    # ---- the faces: engraved gold (flutes), the lit edge bright
    flutes = []
    for (kind, g, h) in A.parts:
        if kind in ("pillar", "tooth"):
            gx0, gy0, gx1, gy1 = g.bounds
            for xv in np.arange(gx0 + 0.3, gx1 - 0.15, 0.44):
                flutes.append(box(xv - 0.075, gy0 - 1, xv + 0.075, gy1 + 1))
        elif kind == "arch":
            gx0, gy0, gx1, gy1 = g.bounds
            for yv in np.arange(gy0 + 0.3, gy1, 0.44):
                flutes.append(box(gx0 - 1, yv - 0.07, gx1 + 1, yv + 0.07))
    for beam in A.beams:
        bx0, by0, bx1, by1 = beam.bounds
        for yv in np.arange(by0 + 0.28, by1 - 0.1, 0.4):
            flutes.append(box(bx0 - 1, yv - 0.065, bx1 + 1, yv + 0.065))
    if full >= 0.999:
        P.gold(solid)
    else:
        P.panel(solid, 0.08)
        P.cold(AW.valid(unary_union(flutes)).intersection(solid.buffer(-0.14)), 0.8)
    from shapely.geometry.polygon import orient
    lit = []
    for g in AW.poly_list(solid):
        ring = LineString(orient(g, 1.0).exterior.coords)
        n = max(8, int(ring.length / 0.25))
        pts = [ring.interpolate(i * ring.length / n) for i in range(n + 1)]
        for p0, p1 in zip(pts, pts[1:]):
            dx, dy = p1.x - p0.x, p1.y - p0.y
            nx, ny = dy, -dx
            L_ = math.hypot(nx, ny) or 1
            facing = (-0.6 * nx - 0.8 * ny) / L_
            w = 0.44 if facing > 0.25 else 0.14
            lit.append(LineString([(p0.x, p0.y), (p1.x, p1.y)]).buffer(w / 2, cap_style=2))
    P.gold(AW.valid(unary_union(lit)).intersection(solid.buffer(0.3)))
    P.emboss(solid, 0.85)
    # the beam carries the series' thesis, engraved small along it (found only up close)
    import typeset as T
    F = T.Faces()
    for beam in A.beams:
        bx0, by0, bx1, by1 = beam.bounds
        if bx1 - bx0 < 12:
            continue
        txt, g = "من سلامة اللسان إلى حسن البيان", None
        size = (by1 - by0) * 0.46
        ln = T.line(txt, F.sch4, size)
        reps_ = max(1, int((bx1 - bx0 - 3) / (ln.width + 3)))
        pieces = []
        x = bx1 - 1.6
        for _ in range(reps_):
            gg, w = T.text(txt, F.sch4, size, x_right=x, base=by1 - (by1 - by0) * 0.28)
            pieces.append(gg)
            x -= w + 3.0
        ins = AW.valid(unary_union(pieces)).intersection(beam.buffer(-0.2))
        P.pearl(ins)
    for (kind, g, _) in A.parts:
        if kind == "joints":
            P.gold(g)
        elif kind == "keystone":
            c = g.centroid
            jewel(P, c.x, c.y, 0.7 * u, 90)
    for (kind, g, _) in A.parts:
        if kind == "knot":
            for (q, lt) in extrude(g):
                if lt > 0.55:
                    P.gold(q.difference(g))
            P.pearl(g)
            P.emboss(g, 0.9)
        elif kind == "finial":
            c = g.centroid
            jewel(P, c.x, c.y, 0.78 * u)
    for (dx, dy, where) in A.dots:
        jewel(P, dx, dy, 1.0 * u)
    for (rx, ry) in A.rubies:
        P.ruby(Point(rx, ry).buffer(0.36 * u, resolution=32))
    return solid


def palimpsest(P, n, field, keep_out, rule_gap=8.0, first=22.0, size=3.4):
    """The page under the architecture: on every ruling a line of the volume's own opening text, engraved in the
    sapphire's own tone, parting around what stands on the page (keep_out)."""
    import re
    import typeset as T
    from volumes import VOLUMES, unit_files
    F = T.Faces()
    t = unit_files(n, VOLUMES[n - 1]["units"][0])[0].read_text(encoding="utf-8")
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"\[[^\]]*\]", "", t)
    t = re.sub(r"[#>*`_]", "", t)
    words = [w for p in t.split("\n") if len(p.strip()) > 60 and "السؤال الذي يجيب" not in p for w in p.split()]
    fx0, fy0, fx1, fy1 = field.bounds
    x_r, x_l = fx1 - 8.0, fx0 + 8.0
    pieces, rules = [], []
    wi = 0
    y = first
    while y < fy1 - 4:
        rules.append(box(x_l, y - 0.06, x_r, y + 0.06))
        line_words = []
        while wi < len(words):
            trial = " ".join(line_words + [words[wi]])
            if T.line(trial, F.sch4, size).width > (x_r - x_l):
                break
            line_words.append(words[wi])
            wi += 1
        if line_words:
            g, _ = T.text(" ".join(line_words), F.sch4, size, x_right=x_r, base=y - 0.9)
            pieces.append(g)
        y += rule_gap
    text = AW.valid(unary_union(pieces)).difference(keep_out)
    ruled = AW.valid(unary_union(rules)).difference(keep_out)
    P.L.body.insert(0, (text, ("lift", 0.075)))
    P.L.body.insert(0, (ruled, ("lift", 0.05)))
    P.L.deboss.append(ruled)


def rails(A, frame_box, width=1.5, gap=0.55, inset=4.2):
    """The uprights of the word carried on: the outermost pair rise past their heads as rails and turn at right
    angles into two interlaced frames round the title (the braided Kufic), the inner uprights rise to meet the
    frame's foot. Returns (pieces over, pieces under-cut, crossings, centre-lines)."""
    tall = sorted([((g.bounds[0] + g.bounds[2]) / 2, g.bounds[1]) for (k, g, h) in A.parts if k == "pillar" and h and h >= 5],
                  key=lambda p: -p[0])
    if len(tall) < 2:
        return [], [], [], []
    (xr, yr), (xl, yl) = tall[0], tall[-1]
    fx0, fy0, fx1, fy1 = frame_box
    u = A.u
    # rail R: from the rightmost upright up to the frame, round it anticlockwise; rail L mirrors it, offset
    R = [(xr, yr - 2.3 * u), (xr, fy1), (fx0, fy1), (fx0, fy0), (fx1 - inset, fy0), (fx1 - inset, fy1 + inset * 0.0)]
    Lr = [(xl, yl - 2.3 * u), (xl, fy1 - inset), (fx1, fy1 - inset), (fx1, fy0 + inset), (fx0 + inset, fy0 + inset), (fx0 + inset, fy1 - inset)]
    inner = [((g.bounds[0] + g.bounds[2]) / 2, g.bounds[1]) for (k, g, h) in A.parts if k == "pillar" and h and h >= 5][1:-1]
    lines = [LineString(R), LineString(Lr)] + [LineString([(x, y - 2.3 * u), (x, fy1 - inset)]) for (x, y) in inner]
    bands = [ln.buffer(width / 2, cap_style=2, join_style=2) for ln in lines]
    # crossings: alternate over and under along the first rail
    over, under = list(bands), []
    crossings = []
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            x = lines[i].intersection(lines[j])
            pts = [x] if x.geom_type == "Point" else (list(x.geoms) if hasattr(x, "geoms") else [])
            for k, p in enumerate(pts):
                if p.geom_type != "Point":
                    continue
                crossings.append((p.x, p.y, i, j))
    for n_, (px, py, i, j) in enumerate(sorted(crossings, key=lambda c: (c[1], c[0]))):
        top, bot = (i, j) if n_ % 2 == 0 else (j, i)
        hole = bands[top].intersection(Point(px, py).buffer(width * 1.6)).buffer(gap, join_style=2)
        over[bot] = AW.valid(over[bot].difference(hole))
    return over, crossings, lines
