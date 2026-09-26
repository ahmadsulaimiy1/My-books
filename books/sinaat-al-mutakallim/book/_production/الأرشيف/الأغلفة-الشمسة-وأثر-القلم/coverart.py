#!/usr/bin/env python3
"""The composition of the covers (Bible, ch. 25 §12): front, spine and back of each volume, as layers of
material (artwork.Layers), on the page (170 × 240 mm, y downward) and placed on the wrap by covers.py.

One architecture for the eleven, from the Arabic book: a tooled frame with its engraved band and jewelled corners,
cornerpieces, the heading panel with its palmette, and at the centre the شمسة, the sun medallion of the
illuminated opening page, its rays drawn with the nib. The medallion carries the series' narrative: it is born
small and dense on the first volume, turns, interlocks, opens, stands in its context, curves, meets another,
projects, becomes architecture, reaches its fullness on the tenth, and on the reference becomes the index of all
ten. Behind the architecture, pressed in gloss alone, the great stroke of the pen crosses each cover; on the
spines it is one stroke from the first volume to the tenth, written from right to left along the shelf.
"""
from __future__ import annotations

import math
from functools import lru_cache

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import artwork as AW
import frontmatter as FM
import illumination as IL
import typeset as T
from artwork import Knot as K

W, H = 170.0, 240.0
TAU = 2 * math.pi
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


@lru_cache(maxsize=1)
def faces():
    return T.Faces()


# ------------------------------------------------------------------------------------------------ layers on the page
def translate(L, dx, dy):
    out = AW.Layers()
    for k in L.__dataclass_fields__:
        items = getattr(L, k)
        moved = []
        for it in items:
            if k == "glow":
                moved.append((it[0] + dx, it[1] + dy) + tuple(it[2:]))
            elif isinstance(it, tuple):
                moved.append((affinity.translate(it[0], dx, dy),) + it[1:])
            else:
                moved.append(affinity.translate(it, dx, dy))
        setattr(out, k, moved)
    return out


class Page:
    """A surface being composed: its layers, and the areas of its architecture (what the gloss stroke and
    the ground pass behind)."""

    def __init__(self):
        self.L = AW.Layers()
        self.arch = []

    def gold(self, g):
        if g is not None and not g.is_empty:
            self.L.gold.append(AW.valid(g))

    def pearl(self, g):
        if g is not None and not g.is_empty:
            self.L.pearl.append(AW.valid(g))

    def champagne(self, g):
        if g is not None and not g.is_empty:
            self.L.champagne.append(AW.valid(g))

    def ruby(self, g):
        self.L.ruby.append(AW.valid(g))

    def cold(self, g, t):
        if g is not None and not g.is_empty:
            self.L.cold.append((AW.valid(g), AW.tint(t)))

    def panel(self, g, depth=0.02):
        self.L.body.append((AW.valid(g), ("depth", depth, 1.0)))

    def ink(self, g, inks):
        self.L.ink.append((AW.valid(g), inks))

    def emboss(self, g, level=1.0):
        self.L.emboss.append((AW.valid(g), level))


# ------------------------------------------------------------------------------------------------ the title
def title_parts(cx, lines):
    """The title in Kufam as (letters, dots, ascenders): lines = [(text, size, baseline)]. The font's square dots
    are found and returned apart, to be redrawn as the nib's dots."""
    F = faces()
    letters, dots, asc = [], [], []
    for (txt, sz, base) in lines:
        g, w = T.text(txt, F.kufi6, sz, cx=cx, base=base, features=T.KF)
        side = 0.137 * sz
        for c in AW.poly_list(g):
            x0, y0, x1, y1 = c.bounds
            cw, ch = x1 - x0, y1 - y0
            if abs(cw - side) < 0.25 * side and abs(ch - side) < 0.25 * side:
                dots.append(((x0 + x1) / 2, (y0 + y1) / 2, side, base))
            else:
                letters.append(c)
                if ch > 0.7 * sz and cw < 0.3 * sz:
                    asc.append(((x0 + x1) / 2, y0, cw, sz))
    return AW.valid(unary_union(letters)), dots, asc


def floriate(x, top, stem_w, size, side=1):
    """A tendril from the head of an ascender: it leans, curls and ends in a split leaf (floriated Kufic)."""
    g, end = IL.tendril(x, top + 0.4, -math.pi / 2, size * 0.62, -0.03 * side * 12 / size, -0.75 * side * 12 / size,
                        stem_w * 0.62, stem_w * 0.26, nib=70)
    lf = IL.split_leaf(end[0], end[1], end[2] - 0.5 * side, size * 0.26, size * 0.13)
    return AW.valid(unary_union([g, lf]))


def set_title(P, cx, lines, floriation=False, emboss=True, dot_scale=1.5):
    """The title as the covers set it: letters in pearl foil over a registered emboss, the dots redrawn as the
    nib's dots in gold, the nūn's dot (the lone dot of «صناعة») in ruby, and tendrils from the ascenders."""
    letters, dots, asc = title_parts(cx, lines)
    P.pearl(letters)
    if emboss:
        P.emboss(letters, 1.0)
    first_base = lines[0][2]
    for (x, y, s, base) in dots:
        nq = AW.nuqta(x, y, s * dot_scale, 70)
        lone = all(math.hypot(x - x2, y - y2) > 2.2 * s for (x2, y2, s2, b2) in dots if (x2, y2) != (x, y))
        if lone and base == first_base and y < base:
            P.ruby(nq)
        else:
            P.gold(nq)
    if floriation:
        for i, (x, top, w, sz) in enumerate(asc):
            if sz > 15 or i % 2 == 0:
                P.gold(floriate(x, top, w, sz * 0.9))
    return letters


# ------------------------------------------------------------------------------------------------ the frame
def frame(P, x0=0.0, y0=0.0, w=W, h=H, corners=((1, 1), (1, 1))):
    """The tooled frame: an outer gold rule, the engraved band between two fine rules, a pearl line, the inner
    rule; jewelled roundels where the band turns."""
    fr = IL.rounded_rect(x0 + 8.5, y0 + 8.5, x0 + w - 8.5, y0 + h - 8.5, 2.0)
    P.gold(IL.band(fr, 0, -1.0))
    P.pearl(IL.band(fr, -1.75, -1.95))
    mid = IL.rounded_rect(x0 + 13.25, y0 + 13.25, x0 + w - 13.25, y0 + h - 13.25, 2.2)
    P.gold(IL.band(mid, 2.35, 2.05))
    P.gold(IL.band(mid, -2.05, -2.35))
    waves = IL.wave_strip(LineString(mid.exterior.coords), 1.25, 5.2, 4, w=0.11)
    P.cold(waves.intersection(IL.band(mid, 1.8, -1.8)), 0.75)
    ext = LineString(mid.exterior.coords)
    nj = int(ext.length / 21.0)
    for i in range(nj):
        q = ext.interpolate(ext.length * (i + 0.5) / nj)
        if min(abs(q.x - x0 - 13.25), abs(q.x - x0 - w + 13.25)) < 9 and min(abs(q.y - y0 - 13.25), abs(q.y - y0 - h + 13.25)) < 9:
            continue
        P.panel(Point(q.x, q.y).buffer(1.9), 0.02)
        P.gold(AW.nuqta(q.x, q.y, 3.0, 70))
    inner = IL.rounded_rect(x0 + 18.0, y0 + 18.0, x0 + w - 18.0, y0 + h - 18.0, 1.2)
    P.pearl(IL.band(inner, 1.55, 1.35))
    P.gold(IL.band(inner, 0.6, 0))
    P.arch.append(IL.band(fr, 0.2, -9.9))
    for (cx, cy) in ((x0 + 13.25, y0 + 13.25), (x0 + w - 13.25, y0 + 13.25), (x0 + 13.25, y0 + h - 13.25), (x0 + w - 13.25, y0 + h - 13.25)):
        d = Point(cx, cy).buffer(4.6, resolution=48)
        P.panel(d, 0.02)
        P.gold(IL.band(d, 0.55, 0))
        P.cold(IL.rose_field(cx, cy, 0.8, 3.6, 6, 2, 6, w=0.10), 0.9)
        P.gold(AW.nuqta(cx, cy, 1.6, 70))
        P.arch.append(d.buffer(0.6))
    return inner


def cornerpieces(P, which, x0=0.0, y0=0.0, w=W, h=H, r=25.0):
    pieces = []
    spots = {"tl": (x0 + 18, y0 + 18, 1, 1), "tr": (x0 + w - 18, y0 + 18, -1, 1),
             "bl": (x0 + 18, y0 + h - 18, 1, -1), "br": (x0 + w - 18, y0 + h - 18, -1, -1)}
    for key in which:
        cx, cy, sx, sy = spots[key]
        q = IL.lobed(cx, cy, r, r, 10, 0.10)
        q = q.intersection(box(min(cx, cx + 40 * sx), min(cy, cy + 40 * sy), max(cx, cx + 40 * sx), max(cy, cy + 40 * sy)))
        pieces.append(q)
        rose = IL.rose_field(cx, cy, 6, r - 3, 10, 2, 14, w=0.22, twist=0.4)
        P.gold(q.buffer(-1.5).difference(rose).difference(Point(cx, cy).buffer(5.6)))
        P.gold(IL.band(Point(cx, cy).buffer(4.8).intersection(q), 0, -0.45))
        P.gold(AW.nuqta(cx + 2.4 * sx, cy + 2.4 * sy, 1.9, 45 if sx * sy > 0 else 135))
    if pieces:
        cor = AW.valid(unary_union(pieces))
        P.panel(cor, 0.03)
        P.gold(IL.band(cor, 0.0, -0.55))
        P.pearl(IL.band(cor, -1.05, -1.22))
        P.arch.append(cor.buffer(0.8))


# ------------------------------------------------------------------------------------------------ the شمسة
# the medallion's growth through the series: its size, its lobes, its field, its light
GROWTH = {
    1: dict(s=0.608, lobes=10, rose=(6, 2, 18, 0.2), rays=(32, 5.0), wave=False, chain=False),
    2: dict(s=0.684, lobes=10, rose=(6, 2, 16, 1.4), rays=(40, 7.0), wave=True, chain=False),
    3: dict(s=0.722, lobes=12, rose=(8, 2, 16, 0.3), rose2=True, rays=(48, 8.0), wave=True, chain=False),
    4: dict(s=0.760, lobes=12, rose=(10, 2, 18, 0.5), rays=(64, 20.0), pearl_rays=True, wave=True, chain=True),
    5: dict(s=0.779, lobes=12, rose=(12, 2, 18, 0.5), nested=3, rays=(60, 9.0), wave=True, chain=True),
    6: dict(s=0.807, lobes=14, rose=(12, 3, 22, 1.2), rays=(64, 14.0), ray_curve=0.55, wave=True, chain=True),
    7: dict(s=0.836, lobes=14, rose=(14, 2, 20, 0.5), rings2=True, rays=(70, 12.0), wave=True, chain=True),
    8: dict(s=0.874, lobes=16, rose=(16, 2, 22, 0.5), rays=(96, 40.0), wave=True, chain=True),
    9: dict(s=0.893, lobes=8, rose=(8, 2, 20, 0.0), square=True, rays=(72, 12.0), wave=True, chain=True),
    10: dict(s=0.950, lobes=16, rose=(16, 3, 30, 0.55), rays=(112, 26.0), pearl_rays=True, wave=True, chain=True, crown=True),
}
MCX, MCY = 85.0, 148.0
RX10, RY10 = 42.0, 46.0


def shamsa(P, n, cx=MCX, cy=MCY, scale=1.0, field=None, detail=1.0, numeral=True, engrave=True):
    """The sun medallion of volume n (1–10) at (cx, cy); scale shrinks it for the spine. Returns its area."""
    g = GROWTH[n]
    s = g["s"] * scale
    rx, ry = RX10 * s, RY10 * s
    lobes = g["lobes"]
    if g.get("square"):
        med = square_medallion(cx, cy, rx, ry)
    else:
        med = IL.lobed(cx, cy, rx, ry, lobes, 0.075, point=0.13)
    # the rays: hairlines from the rim into the field, alternately long and short (drawn first: under the rim)
    nr, rl = g["rays"]
    rl *= scale
    if nr and field is not None:
        rays = []
        for i in range(int(nr * (0.5 + 0.5 * detail))):
            a = TAU * (i + 0.5) / int(nr * (0.5 + 0.5 * detail))
            L = rl * (1.0 if i % 2 == 0 else 0.55)
            r0x, r0y = rx * 1.08, ry * 1.08
            p0 = (cx + r0x * math.cos(a), cy - r0y * math.sin(a))
            bend = g.get("ray_curve", 0.0)
            a1 = a + bend * (L / max(rx, 1)) * 0.5
            p1 = (cx + (r0x + L) * math.cos(a1), cy - (r0y + L) * math.sin(a1))
            hl = AW.hairline(p0, p1, 0.22 * max(0.6, scale), swell=0.12)
            if hl is not None:
                rays.append(hl)
        rays = AW.valid(unary_union(rays)).intersection(field)
        if g.get("pearl_rays"):
            (P.cold if engrave else (lambda *a, **k: None))(rays, 0.95)
        else:
            (P.cold if engrave else (lambda *a, **k: None))(rays, 0.7)
    P.panel(med, 0.12)
    P.L.uv.append(med)
    P.gold(IL.band(med, 1.4 * scale ** 0.5, 0.6 * scale ** 0.5))
    rim = LineString(med.buffer(2.6 * scale ** 0.5).exterior.coords)
    nb = int(rim.length / (2.1 * scale ** 0.5))
    beads = [Point(rim.interpolate(rim.length * i / nb).coords[0]).buffer(0.55 * scale ** 0.5, resolution=12) for i in range(nb)]
    P.gold(unary_union(beads))
    P.pearl(IL.band(med, 0.3 * scale ** 0.5, 0.1 * scale ** 0.5))
    inner = med
    if g.get("wave"):
        (P.cold if engrave else (lambda *a, **k: None))(IL.wave_ring(cx, cy, rx - 2.5 * scale, ry - 2.5 * scale, 1.25 * scale, max(24, lobes * 3), 4, w=0.09).intersection(med), 0.8)
        inner = med.buffer(-5.0 * scale)
        P.gold(IL.band(inner, 0.4 * scale ** 0.5, 0))
        P.pearl(IL.band(inner, -0.8 * scale, -0.95 * scale))
    if g.get("nested"):
        for k in range(1, g["nested"] + 1):
            P.gold(IL.band(med.buffer(-5.0 * scale - k * 4.2 * scale), 0.22, 0))
    if g.get("chain"):
        smooth = Point(cx, cy).buffer(1.0, resolution=96)
        smooth = affinity.scale(smooth, (rx - 7.2 * scale), (ry - 7.2 * scale), origin=(cx, cy))
        chain, holes = IL.jewel_chain(smooth, 0.0, -2.8 * scale, max(24, lobes * 3))
        P.gold(chain)
        pass
        inner = smooth.buffer(-2.8 * scale)
    k, fam, lines, tw = g["rose"]
    core_r = 14.5 * s
    rose = IL.rose_field(cx, cy, core_r + 1.5 * scale, min(rx, ry) - (9.5 if g.get("chain") else 6.0) * scale,
                         k, fam, max(6, int(lines * detail)), w=0.10, twist=tw, squash=ry / rx)
    (P.cold if engrave else (lambda *a, **k: None))(rose.intersection(inner.buffer(-1.0 * scale)), 0.7)
    if g.get("rose2"):
        rose2 = IL.rose_field(cx, cy, core_r + 1.5 * scale, min(rx, ry) - 6 * scale, k, fam, max(6, int(lines * detail * 0.7)),
                              w=0.10, twist=tw + math.pi / k, squash=ry / rx)
        (P.cold if engrave else (lambda *a, **k: None))(rose2.intersection(inner.buffer(-1.0 * scale)), 0.95)
    if g.get("rings2"):
        for sgn in (-1, 1):
            c = Point(cx + sgn * rx * 0.28, cy).buffer(rx * 0.5, resolution=96)
            P.gold(IL.band(c, 0.35 * scale ** 0.5, -0.35 * scale ** 0.5).intersection(inner.buffer(-0.5)))
    # the core: the volume's number, and above it the nib's first dot in ruby
    core = Point(cx, cy).buffer(core_r, resolution=64)
    P.panel(core, 0.06)
    P.gold(IL.band(core, 0.9 * scale ** 0.5, 0.2 * scale ** 0.5))
    P.pearl(IL.band(core, -0.55 * scale, -0.72 * scale))
    (P.cold if engrave else (lambda *a, **k: None))(IL.rose_field(cx, cy, core_r * 0.62, core_r * 0.92, 8, 2, max(4, int(10 * detail)), w=0.10, twist=0.3), 0.95)
    if numeral:
        F = faces()
        num, _ = T.text(str(n), F.amiri7, 12.5 * s * (0.86 if n >= 10 else 1.0), cx=cx, base=cy + 4.0 * s, digits=True)
        P.pearl(num)
        P.emboss(num, 1.0)
        P.ruby(AW.nuqta(cx, cy - 9.3 * s, 2.4 * s, 70))
    if g.get("crown"):
        # the tenth: a second, outer rim of lobes, the medallion at its fullest
        outer = IL.lobed(cx, cy, rx + 2.5 * scale, ry + 2.5 * scale, lobes * 2, 0.05, point=0.12)
        P.gold(IL.band(outer, 0.35, 0).difference(med.buffer(0.8)))
        (P.cold if engrave else (lambda *a, **k: None))(IL.wave_ring(cx, cy, rx + 1.4 * scale, ry + 1.4 * scale, 0.5 * scale, lobes * 4, 3, w=0.10).difference(med.buffer(0.4)).intersection(outer), 0.9)
        med = outer
    P.arch.append(med.buffer(1.8 * scale))
    P.emboss(med, 0.55)
    return med


def square_medallion(cx, cy, rx, ry):
    """The ninth: an octagon lobed on its sides, the medallion become architecture."""
    th = np.linspace(0, TAU, 1440, endpoint=False)
    # an octagon (superellipse with flat sides) with small lobes along each side
    oct_r = 1 / np.maximum.reduce([np.abs(np.cos(th - k * math.pi / 4)) for k in range(4)])
    oct_r = oct_r / oct_r.max()
    lobe = 1 - 0.035 + 0.035 * np.sqrt(np.clip(1 - (np.angle(np.exp(1j * 24 * th)) / math.pi) ** 2, 0, 1))
    r = oct_r * lobe
    return Polygon(np.c_[cx + rx * 1.05 * r * np.cos(th), cy - ry * 1.05 * r * np.sin(th)])


def index_medallion(P, cx=MCX, cy=MCY, scale=1.0, field=None, engrave=True):
    """The reference: a lobed frame holding the ten medallions in miniature (the index of the system), in three
    rows read from the right; its own number on a jewel at the centre of the frame's foot."""
    rx, ry = RX10 * scale * 0.95, (RY10 + 2) * scale * 0.95
    frame_ = IL.lobed(cx, cy, rx, ry, 20, 0.05, point=0.10)
    P.panel(frame_, 0.12)
    P.L.uv.append(frame_)
    P.gold(IL.band(frame_, 1.4 * scale ** 0.5, 0.6 * scale ** 0.5))
    P.pearl(IL.band(frame_, 0.3 * scale ** 0.5, 0.1 * scale ** 0.5))
    (P.L.body.append if engrave else (lambda *a: None))((IL.moire(frame_.buffer(-1.2 * scale), spacing=1.0 * scale, amp=0.5 * scale, wavelength=6.0 * scale, angle=0, w=0.10), ("lift", 0.08)))
    rows = [(3, -24), (4, 0), (3, 24)]
    v = 1
    step = 18.0 * scale
    centres = []
    for (count, dy) in rows:
        for i in range(count):
            x = cx + ((count - 1) / 2 - i) * step
            y = cy + dy * scale
            centres.append((v, x, y))
            v += 1
    # the index lines: each medallion joined to the next, as the volumes lead one into the other
    path = LineString([(x, y) for (_, x, y) in centres])
    (P.cold if engrave else (lambda *a, **k: None))(path.buffer(0.12 * scale), 0.6)
    for (v, x, y) in centres:
        r = 7.2 * scale
        d = Point(x, y).buffer(r, resolution=48)
        P.panel(d, 0.0)
        P.gold(IL.band(d, 0.45 * scale ** 0.5, 0))
        k = GROWTH[v]["lobes"]
        (P.cold if engrave else (lambda *a, **k: None))(IL.rose_field(x, y, r * 0.25, r * 0.85, max(4, k // 2), 2, 6, w=0.10, twist=0.3), 0.8)
        F = faces()
        num, _ = T.text(str(v), F.amiri7, 5.2 * scale, cx=x, base=y + 1.8 * scale, digits=True)
        P.pearl(num)
    P.gold(AW.nuqta(cx, cy + ry * 0.93, 3.0 * scale, 70))
    if field is not None:
        rays = []
        for i in range(120):
            a = TAU * (i + 0.5) / 120
            L = (22.0 if i % 2 == 0 else 11.0) * scale
            p0 = (cx + rx * 1.08 * math.cos(a), cy - ry * 1.08 * math.sin(a))
            p1 = (cx + (rx * 1.08 + L) * math.cos(a), cy - (ry * 1.08 + L) * math.sin(a))
            hl = AW.hairline(p0, p1, 0.2, swell=0.12)
            if hl is not None:
                rays.append(hl)
        (P.cold if engrave else (lambda *a, **k: None))(AW.valid(unary_union(rays)).intersection(field), 0.8)
    P.arch.append(frame_.buffer(1.8 * scale))
    P.emboss(frame_, 0.55)
    return frame_


# ------------------------------------------------------------------------------------------------ the front
def front(n):
    F = faces()
    P = Page()
    inner = frame(P)
    cornerpieces(P, ("tl", "tr", "bl", "br"))
    # the heading panel, its palmette reaching into the band toward the fore-edge
    cart = IL.cartouche(31, 25, 151, 92, lobes=4, depth=0.08)
    P.panel(cart, 0.13)
    P.L.uv.append(cart)
    P.gold(IL.band(cart, 1.3, 0.6))
    P.pearl(IL.band(cart, 0.28, 0.1))
    P.gold(IL.band(cart, -1.0, -1.25))
    pal = IL.palmette(31.5, 58.5, 25, 21, angle=180)
    P.panel(pal, 0.05)
    P.gold(IL.band(pal, 0.5, 0))
    P.pearl(IL.band(pal, -0.9, -1.05))
    P.cold(IL.rose_field(19.0, 58.5, 0.6, 6.0, 6, 2, 9, w=0.10).intersection(pal.buffer(-1.2)), 0.85)
    P.gold(AW.nuqta(19.0, 58.5, 2.0, 70))
    P.arch += [cart.buffer(1.6), pal.buffer(0.8)]
    letters = set_title(P, 92, [("صناعة", 21.0, 51.0), ("المتكـلّم العربي", 12.6, 72.5)])
    ground = IL.moire(cart.buffer(-1.6), spacing=0.95, amp=0.55, wavelength=6.5, angle=0, w=0.10)
    P.L.body.append((ground.difference(letters.buffer(1.1)), ("lift", 0.065)))
    sub, _ = T.text(FM.SUBTITLE, F.sch4, 4.6, cx=91, base=85.5)
    P.ink(sub, AW.PEARL_SOFT)
    # the medallion, and the plaque of the volume's name under it
    plaque_y = 209.5
    field = AW.valid(inner.difference(unary_union(P.arch)))
    if n == 11:
        med = index_medallion(P, field=field)
    else:
        med = shamsa(P, n, field=field)
    # the medallion keeps its air: clear of the heading panel above and of the plaque below
    reach = unary_union([med] + [g for g in P.L.gold if g.intersects(med.buffer(4.0))])
    if reach.bounds[1] < 92.8 or reach.bounds[3] > 203.0:
        raise SystemExit(f"volume {n}: the medallion ({reach.bounds[1]:.1f}–{reach.bounds[3]:.1f} mm) crowds the "
                         f"heading panel (92) or the plaque (203.5)")
    # a jewel where the medallion meets the heading panel, a stem to the plaque
    top = med.bounds[1]
    bot = med.bounds[3]
    if top > 96:
        P.gold(box(MCX - 0.25, 92.5, MCX + 0.25, top))
    P.gold(AW.nuqta(MCX, 94.6, 3.4, 90))
    if bot < plaque_y - 7.5:
        P.gold(box(MCX - 0.25, bot, MCX + 0.25, plaque_y - 6.0))
    plaque = IL.cartouche(MCX - 38, plaque_y - 6.0, MCX + 38, plaque_y + 6.0, lobes=3, depth=0.1)
    P.panel(plaque, 0.10)
    P.L.uv.append(plaque)
    P.gold(IL.band(plaque, 0.8, 0.25))
    P.pearl(IL.band(plaque, -0.5, -0.65))
    P.arch.append(plaque.buffer(1.2))
    ordinal, name = FM.VOLUMES[n - 1][:2]
    label = name if n < 11 else "المرجع"
    kick = f"المجلد {ordinal}"
    kg, kw = T.text(kick, F.changa4, 2.7, cx=MCX, base=plaque_y - 1.9)
    P.ink(kg, AW.CHAMPAGNE_INK)
    ng, nw = T.text(label, F.kufi6, 5.4 if len(label) < 10 else 4.6, cx=MCX, base=plaque_y + 4.1, features=T.KF)
    P.pearl(ng)
    au, _ = T.text(FM.AUTHOR_SHORT, F.sch6, 4.0, cx=MCX, base=220.4)
    P.ink(au, AW.PEARL_INK)
    # the field: the nib's hatching, tone on tone; and the great stroke, pressed in gloss alone
    field = AW.valid(inner.difference(unary_union(P.arch)))
    P.L.body.insert(0, (IL.hatch(field, spacing=1.15, angle=70, w=0.09), ("lift", 0.035)))
    P.L.glow.append((MCX, MCY, 58 + 3 * n, 0.45 + 0.05 * min(n, 10)))
    return P, field


def front_stroke(n):
    """The great stroke behind each front, a different gesture for each volume (varnish only)."""
    G = {
        1: [K(150, 150, 8, 70), K(110, 160, 11, 70), K(80, 150, 13, 70), K(70, 128, 11, 70), K(84, 116, 7, 70, 0.6)],
        2: [K(190, 120, 12, 70), K(130, 150, 16, 70), K(60, 180, 18, 70), K(-10, 205, 16, 70)],
        3: [K(190, 190, 14, 70), K(120, 170, 18, 70), K(70, 150, 20, 70), K(40, 110, 16, 70), K(70, 80, 10, 70), K(120, 70, 6, 70, 0.6)],
        4: [K(190, 150, 16, 70), K(130, 190, 22, 70), K(60, 205, 26, 70), K(-20, 170, 22, 70)],
        5: [K(190, 100, 14, 70), K(120, 130, 18, 70), K(40, 150, 20, 70), K(10, 200, 18, 70), K(60, 225, 12, 70)],
        6: [K(190, 170, 14, 70), K(140, 200, 18, 70), K(90, 170, 20, 70), K(50, 130, 20, 70), K(-20, 150, 16, 70)],
        7: [K(-20, 120, 18, 70), K(60, 150, 22, 70), K(110, 150, 22, 70), K(190, 120, 18, 70)],
        8: [K(90, 100, 6, 70), K(60, 150, 16, 70), K(30, 205, 24, 70), K(-10, 250, 30, 70)],
        9: [K(190, 115, 16, 70), K(20, 115, 16, 70), K(20, 205, 16, 70), K(190, 205, 16, 70)],
        10: [K(205, 150, 24, 70), K(162, 168, 28, 70), K(120, 198, 31, 70), K(80, 224, 33, 70), K(38, 216, 31, 70),
             K(10, 186, 27, 70), K(0, 140, 21, 70), K(22, 100, 12, 70, 0.9), K(48, 78, 4, 70, 0.4)],
        11: [K(190, 128, 10, 70), K(-20, 128, 10, 70)],
    }
    return AW.stroke(G[n], AW.Style(kind="gloss", rule_gap=0.9))


# ------------------------------------------------------------------------------------------------ the spine
SPINE_BANDS = (6.6, 8.0)
BAND_Y = (121.0, 131.0)          # the engraved band that runs across the eleven spines at one height
STROKE_Y = (135.0, 197.0)        # the compartment of the great stroke


def spine(n, sw, shelf_x0, shelf_stroke):
    """The spine of volume n, sw wide, in spine coordinates (x from its front edge, y from the page's head);
    shelf_x0: where this spine begins on the shelf (from the first volume's back edge, right to left)."""
    F = faces()
    P = Page()
    cx = sw / 2
    m = sw - 2 * 3.0
    # the bands of a bound spine, at one height on every volume
    for yb in SPINE_BANDS + (H - SPINE_BANDS[1], H - SPINE_BANDS[0]):
        P.gold(box(-0.2, yb - 0.16, sw + 0.2, yb + 0.16))
    # compartments: pearl hairline frames between gold rules
    comps = [(11.5, 51.0), (54.0, 102.0), (105.0, 118.0), (BAND_Y[0] - 2.0, BAND_Y[1] + 2.0), STROKE_Y, (200.0, 229.5)]
    for (a, b) in comps:
        r = box(1.9, a, sw - 1.9, b)
        P.pearl(IL.band(r, 0.0, -0.16))
    for (a, b) in comps:
        P.gold(box(0.8, a - 1.05, sw - 0.8, a - 0.75))
        P.gold(box(0.8, b + 0.75, sw - 0.8, b + 1.05))
    # the title
    fit = min(1.0, (m - 1.0) / 26.0)
    set_title(P, cx, [("صناعة", 7.6 * fit, 26.5), ("المتكلّم", 5.0 * fit, 37.0), ("العربي", 5.0 * fit, 46.0)],
              floriation=False, emboss=True, dot_scale=1.5)
    # the medallion of the volume, small; the reference: its index medallion
    area = box(2.2, 54.3, sw - 2.2, 101.7)
    sc = min((sw - 5.0) / (2 * RX10 * 1.12 * (GROWTH[n]["s"] if n < 11 else 1.0)), 0.55)
    if n == 11:
        index_medallion(P, cx, 78.0, scale=min((sw - 5.0) / (2 * RX10 * 1.1), 0.5), field=None)
    else:
        shamsa(P, n, cx, 78.0, scale=sc, field=area, detail=0.55)
    # the name
    ordinal, name = FM.VOLUMES[n - 1][:2]
    label = {8: "المجالس والمنبر", 11: "المرجع"}.get(n, name)
    ln = T.line(label, F.kufi6, 5.0, features=T.KF)
    size = 5.0 * min(1.0, (m - 1.0) / ln.width)
    ng, _ = T.text(label, F.kufi6, size, cx=cx, base=113.8, features=T.KF)
    P.pearl(ng)
    # the engraved band across the shelf: its waves are placed by the shelf, not by the spine, so that they run on
    band_r = box(-0.2, BAND_Y[0], sw + 0.2, BAND_Y[1])
    ymid = (BAND_Y[0] + BAND_Y[1]) / 2
    xs = np.linspace(-1, sw + 1, 400)
    X = shelf_x0 + (sw - xs)               # shelf coordinate of each point (the shelf runs right to left)
    waves = []
    for j in range(4):
        ys = ymid + 2.6 * np.sin(TAU * X / 7.0 + j * math.pi / 4)
        waves.append(LineString(np.c_[xs, ys]).buffer(0.06, cap_style=1))
    P.cold(AW.valid(unary_union(waves)).intersection(band_r), 0.8)
    P.gold(box(-0.2, BAND_Y[0] - 0.2, sw + 0.2, BAND_Y[0] + 0.15))
    P.gold(box(-0.2, BAND_Y[1] - 0.15, sw + 0.2, BAND_Y[1] + 0.2))
    # the jewel on the band: one per volume, ruby on the first and the tenth
    jewel = AW.nuqta(cx, ymid, 3.4, 70)
    (P.ruby if n in (1, 10) else P.gold)(jewel)
    P.panel(Point(cx, ymid).buffer(2.6), 0.0)
    # the great stroke through its compartment, cut from the shelf's one stroke
    if shelf_stroke is not None:
        P.L.extend(shelf_stroke)
    # the author and the house
    y = 207.5
    for part in ("أحمد بن", "إبراهيم", "السليمي"):
        g, w = T.text(part, F.sch6, 3.3, cx=cx, base=y)
        P.ink(g, AW.PEARL_INK)
        y += 4.6
    for g in seal(cx, 225.4, small=True):
        P.gold(g)
    return P


def shelf_stroke_layers(n, sw, shelf_x0):
    """The part of the shelf's one stroke that crosses volume n's spine, in spine coordinates."""
    total = SHELF["total"]
    knots = SHELF["knots"]
    # knots are in shelf coordinates (X from the first volume's back edge, leftward); map to this spine
    local = [K(sw - (k.x - shelf_x0), k.y, k.h, k.phi, k.p, k.t) for k in knots]
    St = AW.stroke(local, AW.Style(kind="gold", rule_gap=0.55, rule_w=0.26, edge_w=0.34, edge_back_w=0.22,
                                   body_face=0.40, seam=True, ruby_start=False))
    clip = box(0.6, STROKE_Y[0] + 0.6, sw - 0.6, STROKE_Y[1] - 0.6)
    St.cut(AW.valid(box(-2000, -2000, 2000, 2000).difference(clip)))
    if n == 1:
        # the stroke is born on the first volume: the nib's first touch, in ruby
        k0 = knots[0]
        St.ruby.append(AW.nuqta(sw - (k0.x - shelf_x0), k0.y, 4.2, 70))
    return St


SHELF = {"total": 0.0, "knots": []}


def set_shelf(widths):
    """The shelf's one stroke, from the widths of the eleven spines (their order on the shelf: the first volume on
    the right). Born on the first, widening, turning, at its fullest on the tenth; on the reference it runs out
    into a ruled line."""
    xs = np.r_[0, np.cumsum([widths[v] for v in range(1, 12)])]
    total = float(xs[-1])
    mid = lambda v, f=0.5: float(xs[v - 1] + f * (xs[v] - xs[v - 1]))   # noqa: E731
    yc = (STROKE_Y[0] + STROKE_Y[1]) / 2
    knots = [K(mid(1, 0.18), yc + 6, 1.2, 70, 1, 0.0),
             K(mid(1, 0.8), yc + 2, 5.0, 70, 1, 0.2),
             K(mid(2), yc - 8, 8.0, 70, 1, 0.4),
             K(mid(3), yc - 2, 11.0, 70, 1, 0.0),
             K(mid(4), yc + 10, 14.0, 70, 1, -0.3),
             K(mid(5), yc + 4, 15.0, 70, 1, 0.2),
             K(mid(6), yc - 10, 17.0, 70, 1, 0.5),
             K(mid(7), yc - 4, 18.0, 70, 1, 0.0),
             K(mid(8), yc + 8, 20.0, 70, 1, -0.4),
             K(mid(9), yc + 2, 21.0, 70, 1, 0.2),
             K(mid(10, 0.35), yc - 12, 25.0, 70, 1, 0.8),
             K(mid(10, 0.8), yc - 2, 27.0, 70, 1, 0.9),
             K(mid(11, 0.3), yc + 6, 12.0, 70, 0.9, 0.2),
             K(mid(11, 0.9), yc + 6, 1.0, 70, 0.4, 0.0)]
    SHELF["total"], SHELF["knots"] = total, knots
    SHELF["x0"] = {v: float(xs[v - 1]) for v in range(1, 12)}


# ------------------------------------------------------------------------------------------------ the house's seal
def seal(cx, base, small=False):
    """The house's device (Bible, ch. 98): «الإحسان» in Kufam in a frame of two rules, broken at the top by the
    nib's dot. Returns geometries (for gold)."""
    F = faces()
    size = 2.7 if small else 3.9
    g, w = T.text("الإحسان", F.kufi6, size, cx=cx, base=base, features=T.KF)
    out = [g]
    pad_x, pad_top, pad_bot = size * 0.9, size * 1.0, size * 0.8
    x0, x1 = cx - w / 2 - pad_x, cx + w / 2 + pad_x
    y0, y1 = base - size * 0.95 - pad_top, base + pad_bot
    t_out, t_in, gap = (0.22, 0.12, 0.7) if small else (0.28, 0.14, 0.9)
    dot = size * 0.34
    for (t, d) in ((t_out, 0.0), (t_in, gap)):
        a0, a1, b0, b1 = x0 + d, x1 - d, y0 + d, y1 - d
        hole = dot * 0.9 + 0.5 + d * 0.6
        out.append(unary_union([box(a0, b1 - t, a1, b1), box(a0, b0, a0 + t, b1), box(a1 - t, b0, a1, b1),
                                box(a0, b0, cx - hole, b0 + t), box(cx + hole, b0, a1, b0 + t)]))
    out.append(AW.nuqta(cx, y0 + t_out / 2, dot * 2.2, 70))
    return out


# ------------------------------------------------------------------------------------------------ the back
LEAD = ("لا يريد هذا الكتاب أن يُخرج متكلّمًا يُبهر الناس بألفاظه،",
        "ولا خطيبًا يُعجب السامعين بنفسه؛",
        "بل يريد متكلّمًا يُفهِم ويُحسن ويؤثّر.")
SERIES = ("كتابٌ في أحد عشر مجلدًا في صناعة الكلام بالعربية الفصحى المعاصرة، لمن يعرف العربية ثم لا يجدها على لسانه "
          "حين يحتاج إليها. يبدأ من سؤالٍ لا بدّ منه: أيّ عربيةٍ نتكلّم؟ ثم يمضي من صحة الصوت واستقامة الجملة إلى "
          "مراعاة المقام وحسن البيان، جامعًا بين أصول البيان العربي وما انتهى إليه الدرس الحديث في التواصل، ومقيمًا "
          "ذلك كله على النماذج المتدرّجة والحوار والتدريب والتقويم.")
ISBN_ZONE = (21.0, 186.0, 46.0, 26.0)      # on the back, from its spine side and its head (mm), inside the frame


def back(n):
    F = faces()
    P = Page()
    inner = frame(P)
    cornerpieces(P, ("tl", "tr"))
    # the panel of the words: tall, its head and foot lobed
    pan = AW.valid(unary_union([box(28, 34, 142, 160), IL.lobed(85, 34, 57, 10, 10, 0.12), IL.lobed(85, 160, 57, 10, 10, 0.12)]))
    P.panel(pan, 0.0)
    P.gold(IL.band(pan, 1.2, 0.55))
    P.pearl(IL.band(pan, 0.25, 0.08))
    P.gold(IL.band(pan, -1.0, -1.22))
    P.arch.append(pan.buffer(1.5))
    right, measure = 136.0, 102.0
    y = 44.5
    for t in LEAD:
        g, _ = T.text(t, F.sch6, 5.0, x_right=right, base=y)
        P.ink(g, AW.PEARL_INK)
        y += 8.4
    y += 1.0
    P.gold(box(right - 16, y - 0.18, right, y + 0.18))
    P.gold(AW.nuqta(right - 17.6, y, 2.0, 70))
    y += 9.5
    for ln in T.paragraph(SERIES, F.sch4, 3.55, measure):
        P.ink(T.segs_to_geom(T.set_right(ln, right, y)), AW.PEARL_SOFT)
        y += 6.2
    y += 5.5
    kick, _ = T.text("في هذا المجلد", F.changa4, 2.6, x_right=right, base=y)
    P.ink(kick, AW.CHAMPAGNE_INK)
    y += 7.6
    head = "مرجع المتكلّم العربي" if n == 11 else FM.volume_line(n)
    hg, _ = T.text(head, F.changa5, 4.3, x_right=right, base=y)
    P.pearl(hg)
    y += 7.2
    what = FM.VOLUMES[n - 1][2]
    if n == 11:
        what = f"{FM.REFERENCE_SUB}: {what}"
    for ln in T.paragraph(what + ".", F.sch4, 3.55, measure):
        P.ink(T.segs_to_geom(T.set_right(ln, right, y)), AW.PEARL_SOFT)
        y += 6.1
    stage = FM.VOLUMES[n - 1][3]
    if stage:
        import re
        y += 2.0
        babs = re.sub(r"<[^>]+>", "", FM.VOLUMES[n - 1][4])
        lab, _ = T.text(f"{FM.STAGES[stage]}: {stage} · {babs}", F.changa4, 2.7, x_right=right, base=y)
        P.ink(lab, AW.CHAMPAGNE_INK)
    # the series: the eleven medallions in a row, this volume's in gold and the others drawn in the ground's tone
    row_y = 176.0
    slot = 11.6
    for v in range(1, 12):
        x = 143.0 - (v - 1) * slot
        d = Point(x, row_y).buffer(4.4, resolution=48)
        if v == n:
            P.panel(d, 0.0)
            P.gold(IL.band(d, 0.5, 0))
            P.cold(IL.rose_field(x, row_y, 1.0, 3.8, 6, 2, 6, w=0.10), 0.9)
            ng, _ = T.text(str(v), F.amiri7, 3.6, cx=x, base=row_y + 1.3, digits=True)
            P.pearl(ng)
        else:
            P.L.body.append((IL.band(d, 0.25, 0), ("lift", 0.18)))
            ng, _ = T.text(str(v), F.amiri4, 3.2, cx=x, base=row_y + 1.2, digits=True)
            P.L.body.append((ng, ("lift", 0.22)))
    P.arch.append(box(10, row_y - 6, 160, row_y + 6))
    # the house and the edition, on the fore-edge side; the ISBN zone on the spine side stays clear
    for g in seal(126.0, 205.0):
        P.gold(g)
    pub, _ = T.text(FM.PUBLISHER_AR, F.sch4, 3.2, cx=126.0, base=214.0)
    P.ink(pub, AW.PEARL_SOFT)
    ed, _ = T.text(f"{FM.EDITION}، {FM.YEAR}", F.sch4, 2.9, cx=126.0, base=219.5)
    P.ink(ed, AW.PEARL_SOFT)
    P.arch.append(box(96, 196, 156, 222))
    zx, zy, zw, zh = ISBN_ZONE
    P.arch.append(box(zx - 1, zy - 1, zx + zw + 1, zy + zh + 1))
    field = AW.valid(inner.difference(unary_union(P.arch)))
    P.L.body.insert(0, (IL.hatch(field, spacing=1.15, angle=70, w=0.09), ("lift", 0.035)))
    P.L.glow.append((85, 90, 70, 0.35))
    return P, field


# ------------------------------------------------------------------------------------------------ the master front
def front_master(n):
    """The front of volume n: «المتن والحاشية» (Bible, ch. 25 §13), composed in matn.py."""
    import matn
    return matn.front(n)
