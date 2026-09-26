#!/usr/bin/env python3
"""The covers' marks that the book itself carries (Bible, ch. 25 §13): the page in small (the volume's device, on
its spine, its back and its title page) and the house's seal, with their drawing as SVG for the pages of the book.

They live apart from the covers so that the book depends on them alone: a change to the covers' fronts, spines or
backs leaves the eleven volumes as they are, and a change here rebuilds them (build_all.py fingerprints what each
volume imports).
"""
from __future__ import annotations

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

import artwork as AW
import coverart as CA
import illumination as IL
import typeset as T


def bevel(P, g, top=1.0, base=0.35, depth=1.2, steps=5):
    """A sculpted emboss: the height rising from the edge of g toward its spine."""
    for i in range(steps + 1):
        d = depth * i / steps
        inner = g.buffer(-d, join_style=1) if d > 0 else g
        if inner.is_empty:
            break
        P.emboss(AW.valid(inner), base + (top - base) * i / steps)


def margins(field, m, angles):
    """The four margins between the field and the matn's margin: head, spine side, foot, fore-edge side."""
    fx0, fy0, fx1, fy1 = field.bounds
    mx0, my0, mx1, my1 = m.bounds
    polys = [Polygon([(fx0, fy0), (fx1, fy0), (mx1, my0), (mx0, my0)]),
             Polygon([(fx1, fy0), (fx1, fy1), (mx1, my1), (mx1, my0)]),
             Polygon([(fx0, fy1), (fx1, fy1), (mx1, my1), (mx0, my1)]),
             Polygon([(fx0, fy0), (mx0, my0), (mx0, my1), (fx0, fy1)])]
    return [(AW.valid(p), a) for p, a in zip(polys, angles)]


def device(P, cx, cy, w, h, n=None, lit=1.0, numeral=None):
    """The page in small: a matn ruled in gold, four seams to the corners, the glosses as rulings, jewels at the
    corners; the volume's numeral in the matn. lit: how much of its voice (0..1)."""
    F = CA.faces()
    outer = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    P.gold(IL.band(outer, 0, -0.35, join=2))
    field = outer.buffer(-1.1, join_style=2)
    mw, mh = w * 0.52, h * 0.56
    mb = box(cx - mw / 2, cy - mh / 2, cx + mw / 2, cy + mh / 2)
    m = mb.buffer(0.8, join_style=2)
    fx0, fy0, fx1, fy1 = field.bounds
    mx0, my0, mx1, my1 = m.bounds
    rules = []
    for (poly, ang) in margins(field, m, (0, 45, 0, 45)):
        cxp, cyp = poly.centroid.x, poly.centroid.y
        rr = affinity.rotate(poly, -ang, origin=(cxp, cyp))
        x0, y0, x1, y1 = rr.bounds
        for yy in np.arange(y0 + 0.9, y1, 1.25):
            seg = rr.intersection(box(x0 - 1, yy - 0.06, x1 + 1, yy + 0.06))
            if not seg.is_empty:
                rules.append(affinity.rotate(seg, ang, origin=(cxp, cyp)))
    if rules:
        P.cold(AW.valid(unary_union(rules)).intersection(field.difference(m)), 0.85)
    for (a, b) in (((fx0, fy0), (mx0, my0)), ((fx1, fy0), (mx1, my0)), ((fx0, fy1), (mx0, my1)), ((fx1, fy1), (mx1, my1))):
        P.gold(LineString([a, b]).buffer(0.2, cap_style=2))
    P.panel(mb, 0.14)
    P.gold(IL.band(mb, 0, -0.35, join=2))
    P.pearl(IL.band(mb, -0.7, -0.8, join=2))
    bevel(P, mb, top=0.6, base=0.2, depth=1.2, steps=4)
    if numeral is not None:
        g, _ = T.text(str(numeral), F.amiri7, mh * 0.62, cx=cx, base=cy + mh * 0.22, digits=True)
        P.pearl(g)
        P.emboss(g, 1.0)
    # the voice in small: a scatter of lit dots on the rulings, as far as it has reached
    if lit > 0:
        rng = np.random.default_rng(int(cx * 7 + cy * 13))
        pts = []
        for r in rules:
            c = r.centroid
            if rng.random() < 0.35 + 0.65 * lit:
                pts.append(AW.nuqta(c.x + rng.uniform(-1.0, 1.0), c.y - 0.45, 0.45, 70))
        if pts:
            P.gold(AW.valid(unary_union(pts)).intersection(field.difference(m)))
    return outer


# ------------------------------------------------------------------------------------------------ for the pages of the book
def svg_paths(g, fill, k, ox, oy):
    d = []
    for poly in AW.poly_list(g):
        for ring in [poly.exterior] + list(poly.interiors):
            cs = list(ring.coords)
            if len(cs) < 3:
                continue
            d.append("M" + " L".join(f"{(x - ox) * k:.3f} {(y - oy) * k:.3f}" for (x, y) in cs) + "Z")
    return f'<path d="{"".join(d)}" fill="{fill}" fill-rule="evenodd"/>' if d else ""


def layers_svg(L, width, on_dark, bounds=None):
    x0, y0, x1, y1 = bounds or unary_union([g for g in L.gold + L.pearl] + [b[0] for b in L.body]).bounds
    k = width / (x1 - x0)
    gold = "#C9A95C" if not on_dark else "#E4CB8C"
    pearl = "#0C2766" if not on_dark else "#F1ECE0"
    panel = "#0C2766"
    parts = []
    for (g, spec) in L.body:
        if spec[0] == "depth":
            parts.append(svg_paths(g, panel, k, x0, y0))
    for (g, t) in L.cold:
        parts.append(svg_paths(g, "#B89A5E" if not on_dark else "#CDB27A", k, x0, y0))
    for g in L.gold:
        parts.append(svg_paths(g, gold, k, x0, y0))
    for g in L.pearl:
        parts.append(svg_paths(g, pearl if on_dark else "#F1ECE0", k, x0, y0))
    for g in L.ruby:
        parts.append(svg_paths(g, "#A8172E", k, x0, y0))
    hgt = (y1 - y0) * k
    return (f'<svg viewBox="0 0 {width:.2f} {hgt:.2f}" style="width:{width:.2f}mm;height:{hgt:.2f}mm;display:block;'
            f'margin:0 auto" aria-hidden="true">{"".join(parts)}</svg>')


def seal_svg(width=16.0, on_dark=False):
    """The house's seal for a page of the book, drawn from the covers' outlines, at the given width (mm)."""
    segs = CA.seal(0.0, 0.0)
    word = segs[0]
    b = unary_union(segs).bounds
    k = width / (b[2] - b[0])
    gold = "#C9A95C" if not on_dark else "#E4CB8C"
    ink = "#0C2766" if not on_dark else "#E4CB8C"
    body = svg_paths(word, ink, k, b[0], b[1]) + "".join(svg_paths(g, gold, k, b[0], b[1]) for g in segs[1:])
    hgt = (b[3] - b[1]) * k
    return (f'<svg class="seal" viewBox="0 0 {width:.2f} {hgt:.2f}" style="width:{width:.2f}mm;height:{hgt:.2f}mm;'
            f'display:block;margin:0 auto" aria-hidden="true">{body}</svg>')


def device_svg(n, A=20.0, on_dark=False, ext=None, hair=None):
    """The volume's device for a page of the book (its title page), drawn A mm wide from the covers' own geometry:
    the page in small, the matn with the volume's numeral, its glosses as far as its voice has reached."""
    P = CA.Page()
    device(P, 0.0, 0.0, 30.0, 40.0, n=n, lit=min(n, 10) / 10.0, numeral=n)
    return layers_svg(P.L, A, on_dark)


def house_mark_svg(width=14.0, on_dark=False):
    """The house's sign above its name: one of the nib's dots on a line (Bible, ch. 98)."""
    gold = "#C9A95C" if not on_dark else "#E4CB8C"
    L = AW.Layers()
    h = width * 0.16
    L.gold += [box(-width / 2, -0.09, -h * 0.62, 0.09), box(h * 0.62, -0.09, width / 2, 0.09), AW.nuqta(0, 0, h, 70)]
    return layers_svg(L, width, on_dark, bounds=(-width / 2, -h / 2 - 0.2, width / 2, h / 2 + 0.2)).replace("#C9A95C", gold)
