#!/usr/bin/env python3
"""The cover artwork of the series: «أثر القلم», the trace of the pen (Bible, ch. 25 §12).

The artwork comes first; the covers are laid out on it (covers.py), and the proofs light it (cover_proofs.py).

The idea is the geometry of Arabic writing itself. The reed pen is cut to a flat edge and held at one angle, and
everything the calligrapher makes is the trace of that edge moving: the dot (نقطة) when it is pressed a nib's
width across itself, the hairline when it runs along its own edge, the full stroke when it sweeps across it.
Drawn large, that trace is a ruled surface: a band made of the positions of the nib, hundreds of straight
hairlines, which turns onto its edge wherever the pen moves along the nib. At a distance it reads as a sculpted
band of gold rising out of the sapphire; nearer, as engraving; nearest, as what it is. No letter is drawn: the
Arabic is in the instrument, in its angle, its dot and its measure (every seventh ruling is cut a little deeper:
the seven dots of the proportioned script).

Each material has one part to play (the production is in covers.py and covers/printer-spec.json):
  sapphire      the substrate: CMYK with a spot sapphire (PANTONE 2728 C) for depth no process blue reaches;
                a raster of tonal architecture, blue-black at the edges, imperial where the stroke turns
  cold foil     the rulings, laid inline and overprinted: champagne where the band meets the light, satin gold,
                antique gold in its shadow; under the soft-touch laminate they read as satin metal
  hot foil      gold on the face of the band (bright, over the laminate); champagne where its back shows; pearl
                along the seam where it stands on its edge; ruby for the one dot
  emboss        the face of the band raised; the title raised under its foil
  blind         earlier strokes pressed without ink, or given gloss alone: found only when the book is tilted

A stroke is authored as knots (position, the nib's half width, its angle, its presence) and sampled into
rulings, edges and patches of body; later parts pass over earlier ones, and whatever is behind is cut from every
plate. All geometry is in mm, y downward.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.ops import unary_union

# ------------------------------------------------------------------------------------------------ colour
# Five printing inks: C, M, Y, K and S (the spot sapphire). Values in [0, 1]. Total coverage stays under 3.2.
BLUE_BLACK = (0.00, 0.10, 0.00, 1.00, 0.60)     # #060A18: lacquer black with blue in it
MIDNIGHT = (0.60, 0.40, 0.05, 0.70, 0.70)       # #0A163F
COBALT = (0.30, 0.40, 0.10, 0.30, 0.90)         # #0F246C
ROYAL = (0.70, 0.50, 0.00, 0.00, 0.70)          # #17399A
IMPERIAL = (0.40, 0.00, 0.00, 0.00, 0.90)       # #1E4DBB
LIGHT = (0.30, 0.00, 0.00, 0.00, 0.70)          # #4F78D0: the light inside the stone
RAMP = [(0.00, BLUE_BLACK), (0.26, MIDNIGHT), (0.52, COBALT), (0.76, ROYAL), (0.92, IMPERIAL), (1.00, LIGHT)]

PEARL_INK = (0.00, 0.00, 0.05, 0.08, 0.00)
PEARL_SOFT = (0.20, 0.10, 0.05, 0.00, 0.00)
CHAMPAGNE_INK = (0.05, 0.18, 0.45, 0.05, 0.00)
ANTIQUE_INK = (0.20, 0.40, 0.90, 0.35, 0.00)
RUBY_INK = (0.10, 1.00, 0.65, 0.30, 0.00)

# overprints on the cold foil (silver base): the tints that make its golds
TINT_CHAMPAGNE = (0.00, 0.10, 0.34, 0.00)
TINT_SATIN = (0.04, 0.22, 0.66, 0.04)
TINT_ANTIQUE = (0.16, 0.42, 0.92, 0.26)


def mix(a, b, f):
    return tuple(x + (y - x) * f for x, y in zip(a, b))


def ramp(t):
    """The sapphire at depth t in [0, 1] (0 blue-black, 1 the light in it): five inks."""
    t = min(1.0, max(0.0, float(t)))
    for (a, ca), (b, cb) in zip(RAMP, RAMP[1:]):
        if t <= b:
            return mix(ca, cb, (t - a) / (b - a))
    return RAMP[-1][1]


def ramp_array(t):
    t = np.clip(t, 0.0, 1.0).astype(np.float32)
    out = np.zeros(t.shape + (5,), dtype=np.float32)
    for (a, ca), (b, cb) in zip(RAMP, RAMP[1:]):
        m = (t >= a) & (t <= b)
        f = ((t - a) / (b - a))[m][:, None]
        out[m] = np.array(ca, dtype=np.float32)[None, :] * (1 - f) + np.array(cb, dtype=np.float32)[None, :] * f
    return out


def tint(t):
    """The cold foil's overprint for a ruling lit at t in [0, 1]: antique in shadow, satin, champagne in light."""
    t = min(1.0, max(0.0, float(t)))
    return mix(TINT_ANTIQUE, TINT_SATIN, t / 0.55) if t < 0.55 else mix(TINT_SATIN, TINT_CHAMPAGNE, (t - 0.55) / 0.45)


# the proofs' print model: Neugebauer primaries of coated offset (close to FOGRA39, in sRGB), averaged in a
# Yule-Nielsen space (n = 2); K and the spot as filters over it. The contract proof decides; this only keeps the
# screen honest about ink on paper.
_NEU = {
    (0, 0, 0): (246, 246, 244), (1, 0, 0): (0, 160, 227), (0, 1, 0): (228, 0, 124), (0, 0, 1): (255, 237, 0),
    (1, 1, 0): (44, 46, 131), (1, 0, 1): (0, 151, 71), (0, 1, 1): (228, 33, 36), (1, 1, 1): (39, 36, 38),
}
SPOT_RGB = (0, 71, 187)          # PANTONE 2728 C, approximately, on coated stock
K_RGB = (30, 29, 32)


def _lin(v):
    v = np.asarray(v, dtype=np.float32) / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def _srgb(v):
    v = np.clip(v, 0.0, 1.0)
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * np.power(v, 1 / 2.4) - 0.055)


def inks_to_linear(c):
    """(..., 4 or 5) inks to linear-light RGB reflectance (..., 3)."""
    c = np.asarray(c, dtype=np.float32)
    C, M, Y, K = c[..., 0], c[..., 1], c[..., 2], c[..., 3]
    S = c[..., 4] if c.shape[-1] > 4 else np.zeros_like(C)
    n = 2.0
    acc = 0.0
    for (ic, im, iy), rgb in _NEU.items():
        w = (C if ic else 1 - C) * (M if im else 1 - M) * (Y if iy else 1 - Y)
        acc = acc + w[..., None] * np.power(_lin(rgb), 1 / n)
    paper = np.power(_lin(_NEU[(0, 0, 0)]), 1 / n)
    # an ink over what is printed filters it: transmittance of the solid, in the same space
    for amount, rgb in ((S, SPOT_RGB), (K, K_RGB)):
        tr = np.power(_lin(rgb), 1 / n) / paper
        acc = acc * (1 - amount[..., None] + amount[..., None] * tr)
    return np.power(acc, n)


def inks_to_rgb(c):
    return _srgb(inks_to_linear(c))


# ------------------------------------------------------------------------------------------------ the nib
@dataclass
class Knot:
    x: float
    y: float
    h: float                 # the nib's half width (mm)
    phi: float = 70.0        # the nib's angle, degrees from the horizontal, counter-clockwise as seen
    p: float = 1.0           # presence: 0 gone, 1 the full stroke
    t: float = 0.0           # tilt: the band leaned toward the light (+) or away from it (-), for its modelling


def _centripetal(pts, samples_per_seg):
    P = [np.asarray(p, dtype=np.float64) for p in pts]
    P = [P[0] + (P[0] - P[1])] + P + [P[-1] + (P[-1] - P[-2])]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]

        def tj(ti, a, b):
            return ti + max(1e-6, float(np.linalg.norm(b[:2] - a[:2]))) ** 0.5
        t0 = 0.0
        t1 = tj(t0, p0, p1)
        t2 = tj(t1, p1, p2)
        t3 = tj(t2, p2, p3)
        for k in range(samples_per_seg):
            t = t1 + (t2 - t1) * k / samples_per_seg
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3
            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3
            out.append((t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2)
    out.append(P[-2])
    return np.array(out)


def sample(knots, step=0.08):
    raw = [np.array([k.x, k.y, k.h, k.phi, k.p, k.t]) for k in knots]
    seg = max(np.hypot(raw[i + 1][0] - raw[i][0], raw[i + 1][1] - raw[i][1]) for i in range(len(raw) - 1))
    dense = _centripetal(raw, max(8, int(seg / step * 1.5)))
    d = np.r_[0, np.cumsum(np.hypot(np.diff(dense[:, 0]), np.diff(dense[:, 1])))]
    s = np.arange(0, d[-1], step)
    x, y, h, phi, p, t = (np.interp(s, d, dense[:, j]) for j in range(6))
    return dict(x=x, y=y, h=np.maximum(h, 0.0), phi=np.radians(phi), p=np.clip(p, 0.0, 1.0), t=t, s=s)


LIGHT_DIR = np.array([-0.46, -0.58, 0.67])
LIGHT_DIR = LIGHT_DIR / np.linalg.norm(LIGHT_DIR)
HALF = LIGHT_DIR + np.array([0.0, 0.0, 1.0])
HALF = HALF / np.linalg.norm(HALF)


def shade(S, roll=0.9):
    """Light on the band: a normal from the nib (in the page) and the path, tilted out of the page where the
    stroke turns (the band rolls into its curves). Returns (face, lit): face > 0 where the front of the band
    shows, and lit in [0, 1]."""
    x, y, h, phi = S["x"], S["y"], S["h"], S["phi"]
    tx, ty = np.gradient(x), np.gradient(y)
    tl = np.hypot(tx, ty)
    tl[tl == 0] = 1e-9
    tx, ty = tx / tl, ty / tl
    ux, uy = np.cos(phi), -np.sin(phi)
    face = tx * uy - ty * ux
    ang = np.unwrap(np.arctan2(ty, tx))
    kappa = np.gradient(ang) / np.maximum(1e-6, np.gradient(S["s"]))
    tau = np.clip(roll * kappa * np.maximum(h, 4.0), -1.4, 1.4)
    # smooth the roll so the light moves along the band as it would along a real one
    k = 25
    tau = np.convolve(np.pad(tau, k, mode="edge"), np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k] + S["t"]
    nx = uy * tau
    ny = -ux * tau
    nz = face
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    nl[nl == 0] = 1
    n3 = np.c_[nx / nl, ny / nl, np.abs(nz) / nl]
    diff = np.clip(n3 @ LIGHT_DIR, 0, 1)
    spec = np.clip(n3 @ HALF, 0, 1) ** 18
    lit = np.clip(0.18 + 0.62 * diff + 0.55 * spec, 0, 1)
    return face, lit, tau


# ------------------------------------------------------------------------------------------------ the stroke
@dataclass
class Style:
    """How a stroke takes the materials; its role in the composition decides it."""
    rule_gap: float = 0.52          # mm between rulings, on the faster edge
    rule_w: float = 0.34            # the widest a ruling swells
    rule_min: float = 0.08          # the thinnest ruling the press holds in cold foil
    seventh: float = 1.45           # every seventh ruling cut deeper: the measure
    edge_w: float = 0.46            # hot foil edge on the face
    edge_back_w: float = 0.28       # champagne edge where the back shows
    seam: bool = True               # pearl along the turn
    emboss: bool = True
    uv: bool = True
    body_face: float = 0.46         # depth on the ramp where the face is lit fully
    body_back: float = 0.06         # the back of the band, in shadow
    kind: str = "gold"              # "gold" the full stroke; "champagne" a second stroke; "ghost" tone on tone;
    #                                 "blind" pressed without ink; "gloss" varnish alone
    ruby_start: bool = False        # the nib's first touch in ruby
    roll: float = 0.9
    edges: bool = True


def poly_list(g):
    if g is None or g.is_empty:
        return []
    if isinstance(g, Polygon):
        return [g]
    if isinstance(g, (MultiPolygon, GeometryCollection)):
        out = []
        for x in g.geoms:
            out += poly_list(x)
        return out
    return []


def valid(g):
    if g is None or g.is_empty:
        return Polygon()
    g = g if g.is_valid else g.buffer(0)
    return unary_union(poly_list(g)) if not isinstance(g, (Polygon, MultiPolygon)) else g


@dataclass
class Layers:
    """The artwork as the plates take it, in mm on the wrap."""
    body: list = field(default_factory=list)          # (geometry, inks): painted in order over the substrate
    cold: list = field(default_factory=list)          # (geometry, overprint tint): cold foil, the rulings
    gold: list = field(default_factory=list)          # hot foil, bright gold
    champagne: list = field(default_factory=list)     # hot foil, champagne
    pearl: list = field(default_factory=list)         # hot foil, pearl
    ruby: list = field(default_factory=list)          # hot foil, ruby
    emboss: list = field(default_factory=list)        # (geometry, level 0..1)
    deboss: list = field(default_factory=list)
    uv: list = field(default_factory=list)
    ink: list = field(default_factory=list)           # (geometry, inks): type and fine printed detail, on top
    glow: list = field(default_factory=list)          # (x, y, radius, strength): light in the substrate

    def extend(self, other):
        for k in self.__dataclass_fields__:
            getattr(self, k).extend(getattr(other, k))

    def cut(self, hole, keep=("glow",)):
        """Remove hole (the halo of the type, the region of another surface) from every material."""
        if hole is None or hole.is_empty:
            return
        for k in self.__dataclass_fields__:
            if k in keep:
                continue
            items = getattr(self, k)
            out = []
            for it in items:
                if isinstance(it, tuple):
                    g = valid(it[0].difference(hole))
                    if not g.is_empty:
                        out.append((g,) + it[1:])
                else:
                    g = valid(it.difference(hole))
                    if not g.is_empty:
                        out.append(g)
            setattr(self, k, out)


def _quad(x, y, h, phi, i, j):
    ax, ay = h[i] * math.cos(phi[i]), -h[i] * math.sin(phi[i])
    bx, by = h[j] * math.cos(phi[j]), -h[j] * math.sin(phi[j])
    return [(x[i] + ax, y[i] + ay), (x[j] + bx, y[j] + by), (x[j] - bx, y[j] - by), (x[i] - ax, y[i] - ay)]


def hairline(a, b, w, swell=0.5):
    """A ruling as an engraver cuts it: pointed at both ends, swelling to w at the fraction swell of its length."""
    (ax, ay), (bx, by) = a, b
    dx, dy = bx - ax, by - ay
    L = math.hypot(dx, dy)
    if L < 1e-6 or w <= 0:
        return None
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    mx, my = ax + dx * swell, ay + dy * swell
    return Polygon([(ax, ay), (mx + nx, my + ny), (bx, by), (mx - nx, my - ny)])


def strip(xs, ys, ws):
    """A line of varying width along the points."""
    pts = np.c_[xs, ys]
    if len(pts) < 2:
        return Polygon()
    d = np.diff(pts, axis=0)
    L = np.hypot(d[:, 0], d[:, 1])
    L[L == 0] = 1e-9
    n = np.c_[-d[:, 1] / L, d[:, 0] / L]
    n = np.r_[n[:1], (n[1:] + n[:-1]) / 2, n[-1:]]
    nl = np.hypot(n[:, 0], n[:, 1])
    nl[nl == 0] = 1
    n = n / nl[:, None]
    ring = np.r_[pts + n * (ws[:, None] / 2), (pts - n * (ws[:, None] / 2))[::-1]]
    return valid(Polygon(ring))


def stroke(knots, style=None, over=None):
    """One stroke of the pen as layers. Later parts of it pass over earlier parts; 'over' (a geometry) lies over
    all of it: a stroke drawn after it, the halo of the type."""
    style = style or Style()
    S = sample(knots)
    x, y, h, phi, p = S["x"], S["y"], S["h"], S["phi"], S["p"]
    n = len(x)
    face, lit, tau = shade(S, style.roll)
    ux, uy = np.cos(phi), -np.sin(phi)
    ax, ay, bx, by = x + h * ux, y + h * uy, x - h * ux, y - h * uy
    L = Layers()
    chunk = 40                                           # 3.2 mm of stroke per patch
    starts = list(range(0, n - 1, chunk))
    patches = []
    for s0 in starts:
        s1 = min(n - 1, s0 + chunk)
        qs = [valid(Polygon(_quad(x, y, h, phi, i, i + 1))) for i in range(s0, s1)]
        patches.append(valid(unary_union([q for q in qs if not q.is_empty])))
    occ_after = [None] * len(starts)
    acc = over if over is not None else Polygon()
    for k in range(len(starts) - 1, -1, -1):
        occ_after[k] = acc
        if k + 1 < len(starts):
            acc = valid(unary_union([acc, patches[k + 1]]))
    # the rulings: one wherever the faster edge has moved rule_gap since the last
    ea = np.r_[0, np.cumsum(np.hypot(np.diff(ax), np.diff(ay)))]
    eb = np.r_[0, np.cumsum(np.hypot(np.diff(bx), np.diff(by)))]
    ec = np.maximum(ea, eb)
    rules = [0]
    for i in range(1, n):
        if ec[i] - ec[rules[-1]] >= style.rule_gap:
            rules.append(i)
    rule_no = {r: j for j, r in enumerate(rules)}
    for k, s0 in enumerate(starts):
        s1 = min(n - 1, s0 + chunk)
        occ = occ_after[k]
        body = patches[k]
        if occ is not None and not occ.is_empty:
            body = valid(body.difference(occ))
        if body.is_empty:
            continue
        pk = float(np.mean(p[s0:s1 + 1]))
        fk = float(np.mean(face[s0:s1 + 1]))
        lk = float(np.mean(lit[s0:s1 + 1]))
        if pk < 0.02:
            continue
        if style.kind in ("ghost", "blind", "gloss"):
            if style.kind == "ghost":
                pass
            elif style.kind == "blind":
                L.emboss.append((body, 0.5 * pk))
            else:
                L.uv.append(body)
        else:
            front = fk > 0
            depth = style.body_back + (style.body_face - style.body_back) * lk if front else style.body_back * (0.6 + 0.8 * lk)
            L.body.append((body, ("depth", depth, pk)))
            if front and pk > 0.6:
                if style.emboss:
                    L.emboss.append((body, 0.35 + 0.65 * lk))
                if style.uv:
                    L.uv.append(body)
        # rulings
        for i in (r for r in rules if s0 <= r < s1):
            pi = float(p[i])
            if pi < 0.05:
                continue
            li = float(lit[i]) if face[i] > 0 else float(lit[i]) * 0.45
            w = style.rule_min + (style.rule_w - style.rule_min) * li
            w *= min(1.0, 0.35 + pi)
            if rule_no[i] % 7 == 0:
                w *= style.seventh
            # where the band rolls toward the light the swell moves to the lit edge
            hl = hairline((ax[i], ay[i]), (bx[i], by[i]), w, swell=float(np.clip(0.5 + 0.30 * np.tanh(tau[i]), 0.18, 0.82)))
            if hl is None:
                continue
            if occ is not None and not occ.is_empty:
                hl = valid(hl.difference(occ))
            if hl.is_empty:
                continue
            if style.kind == "gold":
                L.cold.append((hl, tint(li * min(1.0, 0.4 + pi))))
            elif style.kind == "champagne":
                L.cold.append((hl, tint(0.55 + 0.45 * li)))
            elif style.kind == "ghost":
                L.body.append((hl, ("lift", (0.07 + 0.09 * li) * pi)))
            elif style.kind == "gloss":
                if rule_no[i] % 2 == 0:
                    L.uv.append(hairline((ax[i], ay[i]), (bx[i], by[i]), max(0.22, w)))
        # edges
        if style.edges and style.kind in ("gold", "champagne") and pk > 0.3:
            seg = slice(s0, s1 + 1)
            for ex, ey in ((ax[seg], ay[seg]), (bx[seg], by[seg])):
                front = face[seg] > 0
                ws = np.where(front, style.edge_w, style.edge_back_w) * np.clip(p[seg] * 1.3, 0.45, 1.0)
                e = strip(ex, ey, ws)
                if occ is not None and not occ.is_empty:
                    e = valid(e.difference(occ))
                if e.is_empty:
                    continue
                if style.kind == "gold" and fk > 0:
                    L.gold.append(e)
                else:
                    L.champagne.append(e)
    # the turn: a pearl seam where the band stands on its edge, and the substrate lit behind it
    if style.seam and style.kind in ("gold", "champagne"):
        flips = np.where(np.sign(face[1:]) != np.sign(face[:-1]))[0]
        for i in flips:
            if p[i] < 0.6 or h[i] < 1.5:
                continue
            j0, j1 = max(0, i - 22), min(n - 1, i + 22)
            core = valid(unary_union([valid(Polygon(_quad(x, y, h, phi, j, j + 1))) for j in range(j0, j1)]))
            seam = valid(core.buffer(-0.12))
            k = min(len(starts) - 1, i // chunk)
            if occ_after[k] is not None and not occ_after[k].is_empty:
                seam = valid(seam.difference(occ_after[k]))
            if not seam.is_empty:
                L.pearl.append(seam)
            L.glow.append((float(x[i]), float(y[i]), 30.0 + 2.2 * float(h[i]), 1.0))
    if style.ruby_start:
        L.ruby.append(nuqta(float(x[0]), float(y[0]), max(2.2, 2.0 * float(h[0])), float(np.degrees(phi[0]))))
    L.nib = dict(x=x, y=y, h=h, phi=phi, face=face, lit=lit)
    return L


def nuqta(x, y, size, phi=70.0):
    """The dot the nib makes when it is pressed and pushed a nib's width across itself: a rhombus whose long
    diagonal is the nib, at the nib's angle. size: that diagonal (mm)."""
    a = math.radians(phi)
    ux, uy = math.cos(a) * size / 2, -math.sin(a) * size / 2
    vx, vy = math.sin(a) * size * 0.36, math.cos(a) * size * 0.36
    return Polygon([(x + ux, y + uy), (x + vx, y + vy), (x - ux, y - uy), (x - vx, y - vy)])


def ruled_nuqta(x, y, size, phi=70.0, gap=0.5, w=0.14):
    """The dot as the covers draw it large: the nib's positions as it is pushed across itself, each a ruling."""
    a = math.radians(phi)
    ux, uy = math.cos(a) * size / 2, -math.sin(a) * size / 2
    vx, vy = math.sin(a) * size * 0.36, math.cos(a) * size * 0.36
    out = []
    m = max(3, int(2 * math.hypot(vx, vy) / gap))
    for i in range(m + 1):
        f = -1 + 2 * i / m
        cx, cy = x + vx * f, y + vy * f
        k = 1 - abs(f)
        hl = hairline((cx + ux * k, cy + uy * k), (cx - ux * k, cy - uy * k), w)
        if hl is not None:
            out.append(hl)
    return out


# ------------------------------------------------------------------------------------------------ substrate
def substrate_t(w_mm, h_mm, dpi, glows, base=0.30, seed=7, fields=(), foot=0.26, head=0.10):
    """The sapphire's depth as a raster (rows × cols, on the ramp): lifted where the stroke turns (glows), sinking
    toward the foot and the head, with a slow variation in it like enamel."""
    k = dpi / 25.4
    W, H = int(round(w_mm * k)), int(round(h_mm * k))
    X = (np.arange(W, dtype=np.float32) + 0.5) / k
    Y = (np.arange(H, dtype=np.float32) + 0.5) / k
    XX, YY = np.meshgrid(X, Y)
    t = np.full((H, W), base, dtype=np.float32)
    for (gx, gy, r, s) in glows:
        t += 0.34 * s * np.exp(-((XX - gx) ** 2 + (YY - gy) ** 2) / (r * r))
    t -= foot * (np.clip((YY / h_mm - 0.50) / 0.50, 0, 1) ** 1.5)
    t -= head * (np.clip((0.20 - YY / h_mm) / 0.20, 0, 1) ** 1.3)
    rng = np.random.default_rng(seed)
    for _ in range(11):
        cx, cy = rng.uniform(0, w_mm), rng.uniform(0, h_mm)
        r = rng.uniform(35, 110)
        t += rng.uniform(-0.03, 0.03) * np.exp(-(((XX - cx) ** 2 + (YY - cy) ** 2) / (r * r)))
    for (x0, x1, lift) in fields:
        t += lift * np.clip(np.minimum(XX - x0, x1 - XX) / 4.0, 0, 1)
    return t


def substrate(w_mm, h_mm, dpi, glows, grain=0.0035, seed=7, **kw):
    """The substrate as inks (rows × cols × 5), with a fine grain that only breaks the gradients' banding."""
    t = substrate_t(w_mm, h_mm, dpi, glows, seed=seed, **kw)
    t = t + np.random.default_rng(seed + 1).normal(0, grain, size=t.shape).astype(np.float32)
    return ramp_array(t), t
