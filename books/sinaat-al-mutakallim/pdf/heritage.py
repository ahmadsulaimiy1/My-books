#!/usr/bin/env python3
"""Edition 1 of the covers, Heritage: «الشمسة وأثر القلم» (Bible, ch. 25 §12 and §14): the illuminated binding.

A tooled and gilded frame with its cornerpieces; the heading panel with the title; the shamsa (the sunburst
medallion of the Arabic binding) carrying the volume's number, growing from the first volume to the tenth, and a
medallion of eleven for the reference; the nib's great stroke laid in gloss behind the architecture; on the
spines the same medallion in small, a banknote band at one height, and one stroke that runs across the eleven
spines as the shelf's single line. Rich by intention: its character is the heritage, the rootedness, the
splendour and the authority of the scholarly book.

The title, the seal and the words of the back are shared with the other editions (coverart.py).
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
from marks import bevel  # noqa: E402
from coverart import AR, ISBN_ZONE, LEAD, Page, SERIES, TAU, faces, floriate, seal, set_title, title_parts, translate  # noqa: F401


W, H = 170.0, 240.0


def frame(P, x0=0.0, y0=0.0, w=W, h=H, corners=((1, 1), (1, 1)), quiet=False):
    """The tooled frame: an outer gold rule, the engraved band between two fine rules, a pearl line, the inner
    rule; jewelled roundels where the band turns, and jewels along it (quiet: without those, for the back)."""
    fr = IL.rounded_rect(x0 + 8.5, y0 + 8.5, x0 + w - 8.5, y0 + h - 8.5, 2.0)
    P.gold(IL.band(fr, 0, -1.0))
    P.pearl(IL.band(fr, -1.75, -1.95))
    mid = IL.rounded_rect(x0 + 13.25, y0 + 13.25, x0 + w - 13.25, y0 + h - 13.25, 2.2)
    P.champagne(IL.band(mid, 2.35, 2.05))       # the band's rules: the second gold
    P.champagne(IL.band(mid, -2.05, -2.35))
    waves = IL.wave_strip(LineString(mid.exterior.coords), 1.25, 5.2, 4, w=0.11)
    P.cold(waves.intersection(IL.band(mid, 1.8, -1.8)), 0.75)
    ext = LineString(mid.exterior.coords)
    nj = int(ext.length / 21.0)
    for i in range(0 if quiet else nj):
        q = ext.interpolate(ext.length * (i + 0.5) / nj)
        if min(abs(q.x - x0 - 13.25), abs(q.x - x0 - w + 13.25)) < 9 and min(abs(q.y - y0 - 13.25), abs(q.y - y0 - h + 13.25)) < 9:
            continue
        P.panel(Point(q.x, q.y).buffer(1.9), 0.02)
        P.champagne(AW.nuqta(q.x, q.y, 3.0, 70))
    inner = IL.rounded_rect(x0 + 18.0, y0 + 18.0, x0 + w - 18.0, y0 + h - 18.0, 1.2)
    P.pearl(IL.band(inner, 1.55, 1.35))
    P.gold(IL.band(inner, 0.6, 0))
    P.arch.append(IL.band(fr, 0.2, -9.9))
    for (cx, cy) in ((x0 + 13.25, y0 + 13.25), (x0 + w - 13.25, y0 + 13.25), (x0 + 13.25, y0 + h - 13.25), (x0 + w - 13.25, y0 + h - 13.25)):
        d = Point(cx, cy).buffer(4.6, resolution=48)
        P.panel(d, 0.02)
        P.champagne(IL.band(d, 0.55, 0))
        P.cold(girih(cx, cy, 1.5, 3.9, 8, strap=0.42)[0], 0.9)
        P.champagne(AW.nuqta(cx, cy, 1.6, 70))
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
        # a quarter of the rosette, the medallion's own geometry, as the corners of a tooled binding echo it
        straps, tips = girih(cx, cy, 9.5, r + 4.0, 10, rot=math.atan2(sy, sx), strap=1.0)
        P.champagne(straps.intersection(q.buffer(-1.5)).difference(Point(cx, cy).buffer(5.6)))
        for (tx, ty) in tips:
            if q.buffer(-2.2).contains(Point(tx, ty)):
                P.champagne(AW.nuqta(tx, ty, 1.5, 90))
        P.gold(IL.band(Point(cx, cy).buffer(4.8).intersection(q), 0, -0.45))
        P.gold(AW.nuqta(cx + 2.4 * sx, cy + 2.4 * sy, 1.9, 45 if sx * sy > 0 else 135))
    if pieces:
        cor = AW.valid(unary_union(pieces))
        P.panel(cor, 0.03)
        P.gold(IL.band(cor, 0.0, -0.55))
        P.pearl(IL.band(cor, -1.05, -1.22))
        P.arch.append(cor.buffer(0.8))


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
    10: dict(s=0.935, lobes=16, rose=(16, 3, 30, 0.55), rays=(112, 26.0), pearl_rays=True, wave=True, chain=True, crown=True),
}


MCX, MCY = 85.0, 148.0


RX10, RY10 = 42.0, 46.0


def girih(cx, cy, a, R, n, squash=1.0, rot=0.0, strap=0.9, cross=0.70):
    """The geometry of the Islamic rosette (khatam) as strapwork: an n-pointed star of two interlocking n/2-gons
    of circumradius a, and from each of its points two straps running out to R, each crossing its neighbour's at
    cross × R to close the ring of petals, then running on to the rim. Returns (the straps, the star's points)."""
    phi = math.pi / n

    def meet(d):                                         # the radius where two neighbouring straps cross
        t = a * math.tan(phi) / (math.sin(d) - math.cos(d) * math.tan(phi))
        return math.hypot(a + t * math.cos(d), t * math.sin(d))
    lo, hi = phi * 1.001, math.pi / 2 - 1e-3
    for _ in range(60):                                  # bisection: meet() falls as the angle opens
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if meet(mid) > cross * R else (lo, mid)
    delta = (lo + hi) / 2
    lines, tips = [], []
    m = n // 2
    for c in range(2):                                   # the two polygons of the star
        pts = [(a * math.cos(rot + TAU * (i + c * 0.5) / m), a * math.sin(rot + TAU * (i + c * 0.5) / m)) for i in range(m)]
        for i in range(m):
            lines.append(LineString([pts[i], pts[(i + 1) % m]]))
    for i in range(n):
        th = rot + TAU * i / n
        p0 = (a * math.cos(th), a * math.sin(th))
        tips.append(p0)
        for sgn in (-1, 1):
            d = th + sgn * delta
            lines.append(LineString([p0, (p0[0] + 3.0 * R * math.cos(d), p0[1] + 3.0 * R * math.sin(d))]))
    straps = AW.valid(unary_union([ln.buffer(strap / 2, cap_style=2) for ln in lines]))
    straps = straps.intersection(Point(0, 0).buffer(R, resolution=96))
    place = lambda g: affinity.translate(affinity.scale(g, 1, squash, origin=(0, 0)), cx, cy)
    return place(straps), [(cx + x, cy + y * squash) for (x, y) in tips]


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
    # (the ring of beads round the rim is gone: the rim, the lattice and the number are enough)
    P.pearl(IL.band(med, 0.3 * scale ** 0.5, 0.1 * scale ** 0.5))
    inner = med
    if g.get("wave"):
        inner = med.buffer(-5.0 * scale)
        P.champagne(IL.band(inner, 0.4 * scale ** 0.5, 0))
        P.pearl(IL.band(inner, -0.8 * scale, -0.95 * scale))
    if g.get("nested"):
        for k in range(1, g["nested"] + 1):
            P.champagne(IL.band(med.buffer(-5.0 * scale - k * 4.2 * scale), 0.22, 0))
    if g.get("chain"):
        smooth = Point(cx, cy).buffer(1.0, resolution=96)
        smooth = affinity.scale(smooth, (rx - 7.2 * scale), (ry - 7.2 * scale), origin=(cx, cy))
        chain, holes = IL.jewel_chain(smooth, 0.0, -2.8 * scale, max(24, lobes * 3))
        P.champagne(chain)
        pass
        inner = smooth.buffer(-2.8 * scale)
    core_r = 14.5 * s
    field_r = min(rx, ry) - (9.5 if g.get("chain") else 6.0) * scale
    R_ = field_r
    straps, tips = girih(cx, cy, max(0.40 * R_, (core_r + 1.2 * scale) / 0.78), R_, lobes, squash=ry / rx,
                         rot=math.pi / 2, strap=0.8 * scale ** 0.5)
    straps = straps.intersection(inner.buffer(-1.0 * scale)).difference(Point(cx, cy).buffer(core_r + 0.6 * scale))
    if engrave:                                          # the straps gilded, as the tooled bindings gild them
        P.gold(straps)
        P.emboss(straps, 0.75)                 # the lattice raised: foil over emboss, the brightest gold
    for (tx, ty) in tips:
        if inner.buffer(-1.5 * scale).contains(Point(tx, ty)):
            P.gold(AW.nuqta(tx, ty, 1.6 * scale ** 0.5, 90))
    if g.get("rings2"):
        for sgn in (-1, 1):
            c = Point(cx + sgn * rx * 0.28, cy).buffer(rx * 0.5, resolution=96)
            P.champagne(IL.band(c, 0.35 * scale ** 0.5, -0.35 * scale ** 0.5).intersection(inner.buffer(-0.5)))
    # the core: the volume's number, and above it the nib's first dot in ruby
    core = Point(cx, cy).buffer(core_r, resolution=64)
    P.panel(core, 0.06)
    P.gold(IL.band(core, 0.9 * scale ** 0.5, 0.2 * scale ** 0.5))
    P.pearl(IL.band(core, -0.55 * scale, -0.72 * scale))
    if numeral:
        F = faces()
        num, _ = T.text(str(n), F.amiri7, 12.5 * s * (0.86 if n >= 10 else 1.0), cx=cx, base=cy + 4.0 * s, digits=True)
        P.pearl(num)
        P.emboss(num, 1.0)
        P.ruby(AW.nuqta(cx, cy - 9.3 * s, 2.4 * s, 70))
    if g.get("crown"):
        # the tenth: a second, outer rim of lobes, the medallion at its fullest
        outer = IL.lobed(cx, cy, rx + 2.5 * scale, ry + 2.5 * scale, lobes * 2, 0.05, point=0.12)
        P.champagne(IL.band(outer, 0.35, 0).difference(med.buffer(0.8)))
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
        (P.cold if engrave else (lambda *a, **k: None))(girih(x, y, r * 0.42, r * 0.86, k if k <= 12 else 8, strap=0.5 * scale)[0].difference(Point(x, y).buffer(r * 0.34)), 0.8)
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


def inscription(P, x0, y0, x1, y1, bracket=9.0, star=True, fill=None, foot=None):
    """The inscription field (كتيبة) of the architecture: not a box but its corners and its two long rules. Gold
    angles at the four corners; a fine gold rule along head and foot, stopping short of the angles; a small
    eight-point khatam, the medallion's own geometry, set into each rule at its middle. The field itself stays
    the sapphire (fill: a panel tint where words must be read on it). foot: a line of type set into the foot rule
    itself, the rule breaking for it, in place of the foot's khatam. Returns the field's area."""
    t, gap = 0.6, 2.2
    for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        P.gold(box(min(cx, cx + sx * bracket), min(cy, cy + sy * t), max(cx, cx + sx * bracket), max(cy, cy + sy * t)))
        P.gold(box(min(cx, cx + sx * t), min(cy, cy + sy * bracket), max(cx, cx + sx * t), max(cy, cy + sy * bracket)))
        # the inner step of the angle, one rule finer
        ix, iy = cx + sx * 1.5, cy + sy * 1.5
        P.cold(box(min(ix, ix + sx * bracket * 0.55), min(iy, iy + sy * 0.14), max(ix, ix + sx * bracket * 0.55), max(iy, iy + sy * 0.14)), 0.85)
        P.cold(box(min(ix, ix + sx * 0.14), min(iy, iy + sy * bracket * 0.55), max(ix, ix + sx * 0.14), max(iy, iy + sy * bracket * 0.55)), 0.85)
    xm = (x0 + x1) / 2
    for yy in (y0, y1):
        if yy == y1 and foot is not None:
            fx0, _, fx1, _ = foot.bounds
            for (a, b) in ((x0 + bracket + gap, fx0 - 3.2), (fx1 + 3.2, x1 - bracket - gap)):
                if b > a:
                    P.gold(box(a, yy - 0.15, b, yy + 0.15))
            for xe in (fx0 - 3.2, fx1 + 3.2):     # the rule ends on a small point where it meets the name
                P.gold(AW.nuqta(xe, yy, 1.1, 90))
            continue
        cut = 4.6 if star else 0.0
        for (a, b) in ((x0 + bracket + gap, xm - cut), (xm + cut, x1 - bracket - gap)):
            if b > a:
                P.gold(box(a, yy - 0.15, b, yy + 0.15))
        if star:
            g, _ = girih(xm, yy, 1.5, 3.3, 8, strap=0.5)
            P.gold(g)
            P.gold(AW.nuqta(xm, yy, 1.2, 90))
    area = box(x0, y0, x1, y1)
    if fill is not None:
        P.panel(area.buffer(-1.0, join_style=2), fill)
    P.arch.append(area.buffer(1.0, join_style=2))
    return area


MED_CY, MED_SCALE = 142.0, 0.84      # the front's medallion: where it stands and at what size
AUTHOR_TOP = 190.0
SUBSTRATE_BASE = 0.215                # a deeper sapphire than the other editions, so that the light pools in it
BY = "تأليف الفقير إلى ربه"             # the author's own wording, never shortened on this edition
AUTHOR_NAME = "أبي عبد الله جلال الدين أحمد بن إبراهيم السليمي"
AUTHOR_LINES = ("أبي عبد الله جلال الدين", "أحمد بن إبراهيم السليمي")   # the same words, broken as a colophon breaks them
PRAYER = "غفر الله له ولوالديه وللمسلمين"


def author(P, F):
    """The colophon of the front, as the scholarly book states its author: a fine gold rule with the khatam at
    its middle; the humble line; the kunya and laqab; the name, the one line of weight; the prayer, quieter.
    The words are the author's own and are never shortened on this edition."""
    y = AUTHOR_TOP
    for (a, b) in ((MCX - 32, MCX - 5.0), (MCX + 5.0, MCX + 32)):
        P.gold(box(a, y - 0.15, b, y + 0.15))
    g, _ = girih(MCX, y, 1.3, 2.9, 8, strap=0.5)
    P.gold(g)
    P.emboss(g, 0.8)
    by, _ = T.text(BY, F.amiri4, 3.6, cx=MCX, base=y + 7.0)
    P.ink(by, AW.CHAMPAGNE_INK)
    k1, _ = T.text(AUTHOR_LINES[0], F.amiri7, 4.3, cx=MCX, base=y + 14.2)
    P.pearl(k1)
    nm, _ = T.text(AUTHOR_LINES[1], F.amiri7, 5.9, cx=MCX, base=y + 22.4)
    P.pearl(nm)
    bevel(P, AW.valid(unary_union([k1, nm])), top=0.8, base=0.35, depth=0.35, steps=3)
    pr, _ = T.text(PRAYER, F.amiri4, 3.3, cx=MCX, base=y + 28.9)
    P.ink(pr, AW.PEARL_SOFT)
    P.arch.append(box(MCX - 49, y - 3.5, MCX + 49, y + 31.0))


BOX_RUBY = True  # the bibliographic box's field: deep ruby ink (True) or the sapphire itself
BOX_RUBY_INK = (0.30, 1.00, 0.70, 0.55, 0.00)   # a deep oxblood ruby: a cut stone, not a printed red


def volume_box(P, n, cx, cy, w=22.0, h=27.0, ruby=None):
    """The book's bibliographic seal, low on the fore-edge side (Bible, ch. 25 §14 ل): the volume, the edition and
    its year in a small box square to the frame, its corners cut; a fine gold border and a finer rule within, a
    tiny khatam on its head and foot. Its field is deep ruby, printed (not foil), or the sapphire itself."""
    F = faces()
    ruby = BOX_RUBY if ruby is None else ruby
    c = 2.0
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    shape = Polygon([(x0 + c, y0), (x1 - c, y0), (x1, y0 + c), (x1, y1 - c), (x1 - c, y1), (x0 + c, y1), (x0, y1 - c), (x0, y0 + c)])
    if ruby:
        P.ink(shape.buffer(-0.2, join_style=2), BOX_RUBY_INK)
    P.gold(IL.band(shape, 0.0, -0.4, join=2))
    P.gold(IL.band(shape, -1.15, -1.3, join=2)) if ruby else P.cold(IL.band(shape, -1.1, -1.24, join=2), 0.85)
    for yy in (y0, y1):
        if not ruby:
            P.panel(Point(cx, yy).buffer(2.4), 0.0)
        g, _ = girih(cx, yy, 0.9, 2.0, 8, strap=0.38)
        P.gold(g)
    ordinal = FM.VOLUMES[n - 1][0]
    vol = f"المجلد {ordinal}"
    size = 3.4
    ln = T.line(vol, F.kufi6, size, features=T.KF)
    size *= min(1.0, (w - 5.0) / ln.width)
    v, _ = T.text(vol, F.kufi6, size, cx=cx, base=cy - 3.2, features=T.KF)
    P.pearl(v)
    ed, _ = T.text(FM.EDITION, F.changa4, 2.5, cx=cx, base=cy + 3.1)
    (P.gold if ruby else (lambda g_: P.ink(g_, AW.CHAMPAGNE_INK)))(ed)
    yr, _ = T.text(FM.YEAR, F.amiri4, 2.6, cx=cx, base=cy + 8.3)
    (P.gold if ruby else (lambda g_: P.ink(g_, AW.CHAMPAGNE_INK)))(yr)
    P.arch.append(shape.buffer(3.5, join_style=2))


def front(n):
    F = faces()
    P = Page()
    inner = frame(P)
    cornerpieces(P, ("tl", "tr", "bl", "br"), r=18.0)
    # the title engraved into the architecture: an inscription field, its title pressed in pearl on the sapphire
    # the front declares (Bible, ch. 25 §14 ي): the title, its subtitle and the volume in the inscription field;
    # the medallion free in the sapphire; and the author, as the scholarly book names him
    TITLE_FIELD = (40.0, 21.0, 130.0, 92.0)
    ordinal, name = FM.VOLUMES[n - 1][:2]
    label = name if n < 11 else "مرجع المتكلّم العربي"
    size = 5.6 if len(label) < 10 else 4.6
    ng, nw = T.text(label, F.kufi6, size, cx=MCX, base=TITLE_FIELD[3] + size * 0.36, features=T.KF)
    inscription(P, *TITLE_FIELD, foot=ng)
    letters = set_title(P, MCX, [("صناعة", 21.0, 44.5), ("المتكـلّم العربي", 12.4, 63.5)])
    bevel(P, letters, top=1.0, base=0.45, depth=0.55, steps=4)      # carved, not laid on: the title chiselled
    sub, _ = T.text(FM.SUBTITLE, F.sch4, 4.3, cx=MCX, base=77.6)
    P.ink(sub, AW.PEARL_SOFT)
    P.pearl(ng)
    P.emboss(ng, 0.8)
    P.arch.append(ng.buffer(3.0))              # the medallion's rays stop short of the name
    P.L.glow.append((MCX, 55.0, 42.0, 0.35))
    author(P, F)                             # first, so that the medallion's rays keep clear of it
    volume_box(P, n, 33.5, 170.5)            # low on the fore-edge side, beside the medallion's foot
    # the medallion
    field = AW.valid(inner.difference(unary_union(P.arch)))
    first = len(P.L.gold)                    # what the medallion draws, and nothing of the frame round it
    if n == 11:
        med = index_medallion(P, cy=MED_CY, scale=MED_SCALE, field=field)
    else:
        med = shamsa(P, n, cy=MED_CY, scale=MED_SCALE, field=field)
    reach = unary_union([med] + P.L.gold[first:])
    if reach.bounds[1] < TITLE_FIELD[3] + 4.5 or reach.bounds[3] > AUTHOR_TOP - 3.5:
        raise SystemExit(f"volume {n}: the medallion ({reach.bounds[1]:.1f}–{reach.bounds[3]:.1f} mm) crowds the "
                         f"title field ({TITLE_FIELD[3]:.0f}) or the author ({AUTHOR_TOP:.0f})")
    # the field: the nib's hatching, tone on tone; and the great stroke, pressed in gloss alone
    field = AW.valid(inner.difference(unary_union(P.arch)))
    P.L.body.insert(0, (IL.hatch(field, spacing=1.15, angle=70, w=0.09), ("lift", 0.035)))
    P.L.glow.append((MCX, MED_CY, 58 + 3 * n, 0.45 + 0.05 * min(n, 10)))
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


def back(n):
    """The back is silent (Bible, ch. 25 §14 ي): the front declares, the spine identifies, the back says nothing.
    The same tooled frame, quieter; the corners' rosettes; in the open sapphire, the volume's own rosette pressed
    blind and varnished, seen only when the book turns in the light, with one gold khatam at its heart; at the
    foot the house alone, and the ISBN zone left clear until its number is issued."""
    F = faces()
    P = Page()
    inner = frame(P, quiet=True)
    cornerpieces(P, ("tl", "tr", "bl", "br"), r=18.0)
    # the echo of the front's medallion: its geometry with the same fold, blind and in gloss, no foil
    folds = GROWTH[n]["lobes"] if n <= 10 else 12
    cy = 112.0
    R = 46.0
    straps, _ = girih(MCX, cy, 0.42 * R, R, folds, squash=1.1, rot=math.pi / 2, strap=1.0)
    ring = IL.band(Point(MCX, cy).buffer(R, resolution=96), 0.0, -1.0)
    ring = affinity.scale(ring, 1.0, 1.1, origin=(MCX, cy))
    echo = AW.valid(unary_union([straps, ring]))
    P.emboss(echo, 0.45)
    P.L.uv.append(echo)
    g, _ = girih(MCX, cy, 1.9, 4.2, 8, strap=0.55)
    P.gold(g)
    P.gold(AW.nuqta(MCX, cy, 1.5, 90))
    P.arch.append(Point(MCX, cy).buffer(R * 1.12))
    # the house, and nothing else; the ISBN zone on the spine side stays clear
    for g in seal(108.0, 200.0):
        P.gold(g)
    pub, _ = T.text(FM.PUBLISHER_AR, F.sch4, 3.0, cx=108.0, base=209.0)
    P.ink(pub, AW.PEARL_SOFT)
    P.arch.append(box(84, 191, 132, 213))
    zx, zy, zw, zh = ISBN_ZONE
    P.arch.append(box(zx - 1, zy - 1, zx + zw + 1, zy + zh + 1))
    field = AW.valid(inner.difference(unary_union(P.arch)))
    P.L.body.insert(0, (IL.hatch(field, spacing=1.15, angle=70, w=0.09), ("lift", 0.035)))
    P.L.glow.append((MCX, cy, 70, 0.35))
    return P, field


# ------------------------------------------------------------------------------------------------ the wrap
def wrap(n, sw, lay, widths):
    """The wrap of volume n in the wrap's coordinates (covers.py lays it on the binding)."""
    set_shelf(widths)
    L = AW.Layers()
    P, _ = front(n)                          # (the great stroke stays on the spines only: on the front it read as a smudge)
    L.extend(translate(P.L, *lay["front_art"]))
    B, _ = back(n)
    L.extend(translate(B.L, *lay["back_art"]))
    x0 = SHELF["x0"][n]
    S = spine(n, sw, x0, shelf_stroke_layers(n, sw, x0))
    L.extend(translate(S.L, lay["spine"][0], lay["art_top"]))
    for (ax, ay) in (lay["front_art"], lay["back_art"]):     # the tooled frames, pressed in
        fr = IL.rounded_rect(ax + 8.5, ay + 8.5, ax + W - 8.5, ay + H - 8.5, 2.0)
        L.deboss.append(IL.band(fr, 0.2, -9.9))
    return L


def endpaper_layers(w, h):
    """The endpapers: the sapphire, the banknote ground of the heading panel in its own tone, and the shelf's one
    stroke crossing the spread. Returns the layers and the light."""
    L = AW.Layers()
    L.body.append((IL.moire(box(0, 0, w, h), spacing=1.4, amp=0.7, wavelength=9.0, angle=0, w=0.12), ("lift", 0.05)))
    L.extend(AW.stroke([AW.Knot(w + 20, 150, 16), AW.Knot(w * 0.7, 110, 24), AW.Knot(w * 0.45, 160, 30),
                        AW.Knot(w * 0.2, 120, 26), AW.Knot(-20, 150, 18)], AW.Style(kind="ghost", rule_gap=1.0)))
    return L, [(w / 2, h * 0.45, 140, 0.25)]
