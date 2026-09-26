#!/usr/bin/env python3
"""The illumination of the covers: the grammar of the Arabic book (Bible, ch. 25 §12).

The classical Arabic book gave its covers and its opening pages one architecture, tooled in gold and pressed
blind on leather, painted in gold and lapis on the page: a frame (إطار) with its band of interlace, cornerpieces
(كوشات), a central medallion (شمسة، ترنج) with its pendants, and the heading panel (سرلوح) with a palmette that
reaches into the margin. The covers keep that architecture and draw every part of it with the series' own
instrument: the braids are pen strokes, the scrolls are written with the nib at its angle, the dots are the
nib's dots. So the ornament is not borrowed pattern; it is the same geometry as the great stroke behind it
(artwork.py), at the scale of a border.

All geometry is shapely, in mm, y downward.
"""
from __future__ import annotations

import math

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import artwork as AW

TAU = 2 * math.pi


# ------------------------------------------------------------------------------------------------ outlines
def lobed(cx, cy, rx, ry, n, depth=0.055, rot=0.0, point=0.0, point_w=0.16, samples=1440):
    """A polylobed outline: an ellipse scalloped into n round lobes that meet in cusps; point > 0 draws the
    top and the foot out into points (the ترنج)."""
    th = np.linspace(0, TAU, samples, endpoint=False)
    base = 1.0 / np.sqrt((np.cos(th) / rx) ** 2 + (np.sin(th) / ry) ** 2)
    ph = np.angle(np.exp(1j * n * (th - rot))) / math.pi          # -1..1 across each lobe, 0 at its crown
    lobe = 1.0 - depth + depth * np.sqrt(np.clip(1.0 - ph * ph, 0, 1))
    r = base * lobe
    if point:
        for c in (math.pi / 2, 3 * math.pi / 2):
            d = np.angle(np.exp(1j * (th - c)))
            r = r * (1 + point * np.exp(-(d / point_w) ** 2))
    return Polygon(np.c_[cx + r * np.cos(th), cy - r * np.sin(th)])


def band(shape, d_out, d_in, join=2):
    """The ring between two offsets of a shape (d > 0 outward): a rule of the frame."""
    outer = shape.buffer(d_out, join_style=join, mitre_limit=10) if d_out else shape
    inner = shape.buffer(d_in, join_style=join, mitre_limit=10) if d_in else shape
    return AW.valid(outer.difference(inner))


def rounded_rect(x0, y0, x1, y1, r):
    return box(x0 + r, y0 + r, x1 - r, y1 - r).buffer(r, resolution=32)


def cartouche(x0, y0, x1, y1, lobes=5, depth=0.10):
    """The heading panel: a rectangle whose two ends are lobed half-medallions."""
    h = y1 - y0
    cy = (y0 + y1) / 2
    body = box(x0 + h * 0.45, y0, x1 - h * 0.45, y1)
    ends = [lobed(x0 + h * 0.5, cy, h * 0.52, h * 0.5, lobes * 2, depth, rot=math.pi / 2),
            lobed(x1 - h * 0.5, cy, h * 0.52, h * 0.5, lobes * 2, depth, rot=math.pi / 2)]
    return AW.valid(unary_union([body] + ends))


# ------------------------------------------------------------------------------------------------ the pen's ornament
def pen_band(knots, face_gold=True):
    """A solid pen stroke at ornament scale: the band the nib sweeps, filled (no rulings)."""
    S = AW.sample(knots, step=0.05)
    x, y, h, phi = S["x"], S["y"], S["h"], S["phi"]
    quads = [Polygon(AW._quad(x, y, h, phi, i, i + 1)) for i in range(len(x) - 1)]
    return AW.valid(unary_union([q if q.is_valid else q.buffer(0) for q in quads]))


def spiral_knots(cx, cy, r0, r1, turns, h0, h1, phi=70.0, start=0.0, cw=True, n=None):
    """Knots along a logarithmic spiral from radius r0 (inside) to r1: the scroll of the arabesque."""
    n = n or max(8, int(turns * 14))
    out = []
    for i in range(n + 1):
        f = i / n
        a = start + (1 if cw else -1) * turns * TAU * f
        r = r0 * (r1 / r0) ** f
        out.append(AW.Knot(cx + r * math.cos(a), cy - r * math.sin(a), h0 + (h1 - h0) * f, phi, 1.0))
    return out


def braid(path, amp, wavelength, strand_w, gap=0.35, strands=2):
    """An interlace along a path: strands weaving over and under one another. Returns (over, under) lists of
    strand pieces: the pieces that pass over at a crossing, and those cut to pass under."""
    L = path.length
    n = max(4, int(round(L / wavelength)))
    lam = L / n
    s = np.linspace(0, L, max(200, int(L / 0.12)))
    pts = np.array([path.interpolate(v).coords[0] for v in s])
    d = np.gradient(pts, axis=0)
    dl = np.hypot(d[:, 0], d[:, 1])
    dl[dl == 0] = 1
    nrm = np.c_[-d[:, 1] / dl, d[:, 0] / dl]
    pieces = []            # (strand, k, polygon) for each half-wave
    for j in range(strands):
        ph = j * math.pi if strands == 2 else j * TAU / strands
        off = amp * np.sin(TAU * s / lam + ph)
        line = pts + nrm * off[:, None]
        # cut into half-waves between crossings (where the offset passes zero)
        idx = np.where(np.sign(off[1:]) != np.sign(off[:-1]))[0]
        cuts = [0] + list(idx + 1) + [len(s) - 1]
        for k in range(len(cuts) - 1):
            a, b = cuts[k], cuts[k + 1]
            if b - a < 2:
                continue
            seg = LineString(line[a:b + 1])
            pieces.append((j, k, seg.buffer(strand_w / 2, cap_style=2, join_style=1)))
    # at each crossing one strand goes over: alternate along the path
    over, under = [], []
    for (j, k, g) in pieces:
        (over if (j + k) % 2 == 0 else under).append(g)
    ov = AW.valid(unary_union(over))
    under = [AW.valid(g.difference(ov.buffer(gap))) for g in under]
    return [AW.valid(g) for g in over], [g for g in under if not g.is_empty]


def palmette(cx, cy, length, width, angle=0.0):
    """The vignette of a heading panel: a pointed, lobed leaf pointing along angle (degrees; 0 to the right)."""
    t = np.linspace(0, 1, 240)
    # a leaf profile: round at the root, drawn to a point
    half = width / 2 * np.sin(np.pi * t) ** 0.9 * (1 - 0.45 * t)
    xs = np.r_[t * length, (t * length)[::-1]]
    ys = np.r_[half, -half[::-1]]
    leaf = Polygon(np.c_[xs, ys])
    scal = [Point(length * f, 0).buffer(width * 0.18 * (1 - f)) for f in (0.2, 0.42, 0.62)]
    shape = AW.valid(unary_union([leaf] + scal))
    shape = affinity.rotate(shape, -angle, origin=(0, 0))
    return affinity.translate(shape, cx, cy)


def rosette(cx, cy, r, n, phi=70.0):
    """A rosette of the nib's dots: n dots set round a centre, each at its angle to the radius."""
    out = []
    for i in range(n):
        a = TAU * i / n
        px, py = cx + r * 0.55 * math.cos(a), cy - r * 0.55 * math.sin(a)
        out.append(AW.nuqta(px, py, r * 0.9, math.degrees(a)))
    return AW.valid(unary_union(out))


# ------------------------------------------------------------------------------------------------ the arabesque
def euler(x0, y0, th0, length, k0, k1, n=60):
    """A curve whose curvature runs evenly from k0 to k1 (per mm) along its length: the scroll a draughtsman
    draws with a French curve, opening or winding into a spiral. th0 in radians, y downward (a positive
    curvature turns clockwise as seen)."""
    s = np.linspace(0, length, n)
    k = k0 + (k1 - k0) * s / length
    th = th0 + np.r_[0, np.cumsum((k[1:] + k[:-1]) / 2 * np.diff(s))]
    x = x0 + np.r_[0, np.cumsum(np.cos((th[1:] + th[:-1]) / 2) * np.diff(s))]
    y = y0 + np.r_[0, np.cumsum(np.sin((th[1:] + th[:-1]) / 2) * np.diff(s))]
    return x, y, th


def tendril(x0, y0, th0, length, k0, k1, w0, w1, n=80, nib=None):
    """A tendril of the arabesque drawn with the pen: an Euler curve, its width tapering from w0 to w1 (the
    stroke thickens and thins with the nib's angle to the path when nib is given, in degrees)."""
    x, y, th = euler(x0, y0, th0, length, k0, k1, n)
    w = np.linspace(w0, w1, n)
    if nib is not None:
        a = math.radians(nib)
        w = w * (0.45 + 0.55 * np.abs(np.sin(th + a)))
    g = AW.strip(x, y, np.maximum(w, 0.05))
    return g, (x[-1], y[-1], th[-1])


def leaf(x, y, th, length, width, bend=0.0):
    """A pointed leaf from (x, y) along th (radians): two arcs meeting in a point; bend curls it."""
    t = np.linspace(0, 1, 60)
    half = width / 2 * np.sin(np.pi * t) ** 0.8
    cx = t * length
    cy = bend * length * t * t
    pts = np.r_[np.c_[cx, cy + half], np.c_[cx[::-1], (cy - half)[::-1]]]
    c, s = math.cos(th), math.sin(th)
    R = np.array([[c, -s], [s, c]])
    pts = pts @ R.T + np.array([x, y])
    return AW.valid(Polygon(pts))


def split_leaf(x, y, th, length, width):
    """The split palmette (رومي): two curled lobes parting from one root."""
    a = leaf(x, y, th - 0.38, length, width, bend=-0.35)
    b = leaf(x, y, th + 0.38, length * 0.78, width * 0.85, bend=0.35)
    return AW.valid(unary_union([a, b]))


def trefoil(x, y, th, size):
    """A small palmette: a middle leaf and two side leaves."""
    return AW.valid(unary_union([leaf(x, y, th, size, size * 0.42),
                                 leaf(x, y, th - 0.75, size * 0.66, size * 0.34, bend=-0.3),
                                 leaf(x, y, th + 0.75, size * 0.66, size * 0.34, bend=0.3)]))


def mirror_y(g):
    return affinity.scale(g, 1, -1, origin=(0, 0))


def sector_motif(R0, R1, n, scale=1.0, variant=0):
    """One sector of a medallion's arabesque, in local coordinates (the sector's centre-line along +x from the
    centre, half-angle pi/n), mirrored about the centre-line. Returns (gold, jewels): the tendrils and leaves,
    and the points where a dot belongs."""
    half = math.pi / n
    parts, jewels = [], []
    span = R1 - R0
    w = 0.55 * scale
    # the stem: out along the centre-line, then parting into a scroll on each side
    stem_len = span * 0.34
    stem = AW.strip(np.linspace(R0, R0 + stem_len, 30), np.zeros(30), np.linspace(w * 1.5, w * 1.1, 30))
    parts.append(stem)
    sx = R0 + stem_len
    for side in (1,):
        g, end = tendril(sx, 0, -0.55, span * 0.52, 0.02 / scale, 0.34 / scale, w * 1.1, w * 0.45)
        parts.append(g)
        parts.append(split_leaf(end[0], end[1], end[2] + 0.4, 3.2 * scale, 1.8 * scale))
        # a second scroll that turns back toward the stem
        g2, e2 = tendril(sx + span * 0.12, -span * 0.10, -1.2, span * 0.30, -0.05 / scale, -0.42 / scale, w * 0.8, w * 0.35)
        parts.append(g2)
        parts.append(leaf(e2[0], e2[1], e2[2] - 0.3, 2.2 * scale, 1.1 * scale, bend=-0.3))
        # the outer tendril reaching to the rim
        g3, e3 = tendril(sx + span * 0.22, -span * 0.22, -0.2, span * 0.46, 0.08 / scale, 0.30 / scale, w * 0.7, w * 0.3)
        parts.append(g3)
        parts.append(trefoil(e3[0], e3[1], e3[2], 2.6 * scale))
        jewels.append((sx + span * 0.12, -span * 0.10))
    # the palmette at the head of the stem, on the centre-line
    parts.append(trefoil(R0 + span * 0.62, 0, 0.0, span * 0.26))
    jewels.append((R0 + span * 0.36, 0.0))
    g = AW.valid(unary_union(parts))
    # keep inside the sector's half, then mirror to the other half
    wedge = Polygon([(0, 0), (R1 * 2 * math.cos(half), -R1 * 2 * math.sin(half)), (R1 * 2, 0)])
    g = AW.valid(g.intersection(wedge.buffer(0.001)))
    g = AW.valid(unary_union([g, mirror_y(g)]))
    return g, jewels


def rosace(cx, cy, R0, R1, n, scale=1.0, rot=0.0, squash=1.0):
    """A medallion's field: the sector motif turned n times round the centre (squash stretches it upright)."""
    g, jewels = sector_motif(R0, R1, n, scale)
    out, pts = [], []
    for i in range(n):
        a = rot + TAU * i / n
        gi = affinity.rotate(g, -math.degrees(a), origin=(0, 0))
        out.append(gi)
        for (jx, jy) in jewels:
            for sgn in ((1, -1) if jy else (1,)):
                c, s = math.cos(-a), math.sin(-a)
                px, py = jx * c - (jy * sgn) * s, jx * s + (jy * sgn) * c
                pts.append((px, py))
    field = AW.valid(unary_union(out))
    field = affinity.scale(field, 1, squash, origin=(0, 0))
    field = affinity.translate(field, cx, cy)
    pts = [(cx + px, cy + py * squash) for (px, py) in pts]
    return field, pts


# ------------------------------------------------------------------------------------------------ engraving (guilloché)
def polyline(pts, w, closed=True):
    """A fine engraved line along the points (width w, mm)."""
    pts = np.asarray(pts)
    if closed:
        pts = np.r_[pts, pts[:1]]
    return LineString(pts).buffer(w / 2, cap_style=1, join_style=1, resolution=4)


def wave_ring(cx, cy, rx, ry, amp, cycles, families, w=0.10, phase=0.0, squash_amp=True, samples=2400):
    """A ring of engraved waves: 'families' sinusoids round an ellipse, each shifted, crossing one another."""
    th = np.linspace(0, TAU, samples, endpoint=False)
    base = 1.0 / np.sqrt((np.cos(th) / rx) ** 2 + (np.sin(th) / ry) ** 2)
    out = []
    for j in range(families):
        r = base + amp * np.sin(cycles * th + phase + j * TAU / families / 2)
        out.append(polyline(np.c_[cx + r * np.cos(th), cy - r * np.sin(th)], w))
    return AW.valid(unary_union(out))


def rose_field(cx, cy, R0, R1, k, families, lines, w=0.09, twist=0.0, squash=1.0, samples=3000):
    """The engraved rosette: 'lines' curves between radii R0 and R1, each r(θ) = mid + amp·cos(kθ + shift),
    their shifts turning through the families; the crossings make the petals."""
    th = np.linspace(0, TAU, samples, endpoint=False)
    out = []
    for i in range(lines):
        f = i / max(1, lines - 1)
        mid = R0 + (R1 - R0) * (0.25 + 0.5 * f)
        amp = (R1 - R0) * 0.25 * (0.6 + 0.4 * math.sin(math.pi * f))
        shift = twist * f + (i % families) * TAU / families / k
        r = mid + amp * np.cos(k * (th + shift))
        out.append(polyline(np.c_[cx + r * np.cos(th), cy - squash * r * np.sin(th)], w))
    return AW.valid(unary_union(out))


def wave_strip(path, amp, wavelength, families, w=0.10, phase=0.0):
    """Engraved waves along a path (a border): 'families' sinusoids about it, crossing."""
    L = path.length
    n = max(4, int(round(L / wavelength)))
    lam = L / n
    s = np.linspace(0, L, max(400, int(L / 0.1)))
    pts = np.array([path.interpolate(v).coords[0] for v in s])
    d = np.gradient(pts, axis=0)
    dl = np.hypot(d[:, 0], d[:, 1])
    dl[dl == 0] = 1
    nrm = np.c_[-d[:, 1] / dl, d[:, 0] / dl]
    out = []
    for j in range(families):
        off = amp * np.sin(TAU * s / lam + phase + j * math.pi / families)
        out.append(LineString(pts + nrm * off[:, None]).buffer(w / 2, cap_style=1, join_style=1, resolution=4))
    return AW.valid(unary_union(out))


def moire(region, spacing=0.9, amp=0.6, wavelength=7.0, angle=0.0, w=0.07, families=2):
    """A banknote ground: families of parallel waved lines across a region, crossing one another."""
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + 2
    out = []
    xs = np.linspace(-R, R, int(2 * R / 0.12))
    for j in range(families):
        ph = j * math.pi
        y = -R
        while y <= R:
            ys = y + amp * np.sin(TAU * xs / wavelength + ph + y * 0.9)
            out.append(LineString(np.c_[xs, ys]).buffer(w / 2, cap_style=1, resolution=3))
            y += spacing
    g = AW.valid(unary_union(out))
    g = affinity.rotate(g, angle, origin=(0, 0))
    g = affinity.translate(g, cx, cy)
    return AW.valid(g.intersection(region))


def hatch(region, spacing=1.1, angle=70.0, w=0.08):
    """Straight engraved lines at the nib's angle across a region (the ground of the field)."""
    x0, y0, x1, y1 = region.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    R = math.hypot(x1 - x0, y1 - y0) / 2 + 2
    lines = [LineString([(-R, y), (R, y)]).buffer(w / 2, cap_style=2) for y in np.arange(-R, R, spacing)]
    g = affinity.rotate(unary_union(lines), angle, origin=(0, 0))
    return AW.valid(affinity.translate(g, cx, cy).intersection(region))


def jewel_chain(shape, d_out, d_in, n, phi=70.0):
    """A band of solid gold between two offsets of a shape, with n of the nib's dots knocked out of it: gold
    ground, sapphire motif (the counterchange of the illuminator)."""
    ring = band(shape, d_out, d_in)
    mid = shape.buffer((d_out + d_in) / 2)
    ext = LineString(mid.exterior.coords)
    holes = []
    size = abs(d_out - d_in) * 0.78
    for i in range(n):
        p = ext.interpolate(ext.length * (i + 0.5) / n)
        q = ext.interpolate(ext.length * (i + 0.5) / n + 0.5)
        a = math.degrees(math.atan2(-(q.y - p.y), q.x - p.x))
        holes.append(AW.nuqta(p.x, p.y, size, a + 90))
    return AW.valid(ring.difference(unary_union(holes))), holes
