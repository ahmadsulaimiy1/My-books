#!/usr/bin/env python3
"""Material proofs of the covers: what the plates of covers.py look like once printed and finished.

The PRINT plate gives the colour; FOIL, EMBOSS, DEBOSS and SPOT-UV are read as surfaces and lit: the
emboss raised and the deboss pressed (a height field, its normals, one soft key light from the upper
left), the foil a champagne metal that takes the light across its face and on the edges of its relief, the
spot gloss a sharper sheen on the matte laminate. No reflections that the object would not make, no
glow, no smoke (Bible, ch. 25 §9 and §10ز).

    python3 pdf/cover_proofs.py          the eleven wrap proofs, the fronts, the shelf, the spine close-up
    python3 pdf/cover_proofs.py 5        one volume's wrap proof

Writes into covers/: Cover-NN_<Latin>_Proof.jpg (the flat wrap), and Series_Fronts.jpg, Series_Shelf.jpg,
Series_Spine-Closeup.jpg. The proofs simulate; the printer's wet proof and a finished sample decide.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import covers as CV  # noqa: E402

OUT = CV.OUT
LIGHT = np.array([-0.52, -0.58, 0.63])          # from the upper left (x right, y down, z toward the viewer)
LIGHT = LIGHT / np.linalg.norm(LIGHT)
FOIL_DARK, FOIL_MID, FOIL_LIGHT = np.array([118, 94, 56]), np.array([196, 170, 116]), np.array([246, 234, 198])


def plate(n, name, dpi, clip=None, rgb=False):
    doc = pymupdf.open(str(OUT / f"Cover-{n:02d}_{CV.LATIN[n]}_{name}.pdf"))
    page = doc[0]
    kw = dict(dpi=dpi, colorspace=pymupdf.csRGB if rgb else pymupdf.csGRAY)
    if clip is not None:
        kw["clip"] = pymupdf.Rect(*[v * 72 / 25.4 for v in clip])
    pm = page.get_pixmap(**kw)
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n).astype(np.float32) / 255.0
    return a if rgb else 1.0 - a[..., 0]


def blur(a, r):
    """Three box passes: close to a gaussian of radius r (pixels)."""
    r = max(1, int(round(r)))
    out = a.astype(np.float32)
    for axis in (0, 1):
        for _ in range(3):
            pad = [(0, 0)] * out.ndim
            pad[axis] = (r + 1, r)
            c = np.cumsum(np.pad(out, pad, mode="edge"), axis=axis)
            hi = np.take(c, np.arange(2 * r + 1, c.shape[axis]), axis=axis)
            lo = np.take(c, np.arange(0, c.shape[axis] - 2 * r - 1), axis=axis)
            out = (hi - lo) / (2 * r + 1)
    return out


def grain(shape, seed, scale=1.0):
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, shape).astype(np.float32)
    return blur(g, 1) * scale


def render(n, dpi=150, clip=None, seed=3, raking=1.0):
    """The finished cover (or a clip of it, in mm of the wrap) as an RGB array in 0..255."""
    base = plate(n, "PRINT", dpi, clip, rgb=True)
    foil = plate(n, "FOIL", dpi, clip)
    emb = plate(n, "EMBOSS", dpi, clip)
    deb = plate(n, "DEBOSS", dpi, clip)
    uv = plate(n, "SPOT-UV", dpi, clip)
    px = dpi / 25.4                                     # pixels a millimetre
    # the surface: raised emboss, pressed deboss, and foil pressed a hair into the laminate
    h = 0.8 * blur(emb, 0.30 * px) - 0.7 * blur(deb, 0.30 * px) - 0.10 * blur(foil, 0.10 * px)
    h = h * px * 0.22 * raking
    gy, gx = np.gradient(h)
    nrm = np.dstack([-gx, -gy, np.ones_like(h)])
    nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    ndl = np.clip(nrm @ LIGHT, 0, 1)
    flat = LIGHT[2]
    shade = (0.58 + 0.42 * ndl) / (0.58 + 0.42 * flat)
    H, W = h.shape
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # soft studio fall-off across the object
    fall = 1.0 - 0.10 * ((xx / W - 0.35) ** 2 + (yy / H - 0.3) ** 2)
    # matte soft-touch laminate: a fine grain and a very broad sheen
    lam = 1.0 + grain((H, W), seed, 0.018)
    col = base * (shade * fall * lam)[..., None]
    # the pressed areas look a touch denser
    col *= (1.0 - 0.05 * blur(deb, 0.2 * px))[..., None]
    # spot gloss: deeper colour and a sharper sheen where the light meets it
    half = LIGHT + np.array([0, 0, 1.0])
    half /= np.linalg.norm(half)
    spec_uv = np.clip(nrm @ half, 0, 1) ** 60
    band = 0.5 + 0.5 * np.cos((xx * 0.8 + yy * 0.6) / (W * 0.9) * np.pi * 2 - 1.1)
    uvm = blur(uv, 0.1 * px)
    col = col * (1 - 0.06 * uvm[..., None]) + (uvm * (0.07 * band ** 3 + 0.45 * spec_uv))[..., None]
    # foil: champagne metal; a broad reflection across its face, light on the edges of its relief
    fm = blur(foil, 0.08 * px)
    refl = 0.5 + 0.5 * np.sin((xx * 0.62 - yy * 0.78) / (W * 0.55) * np.pi * 2 + 0.7)
    edge = np.clip(nrm @ LIGHT - flat, -1, 1) * 3.0
    t = np.clip(0.42 + 0.38 * refl + edge + grain((H, W), seed + 1, 0.035), 0, 1.25)
    lo = np.clip(t * 2, 0, 1)[..., None]
    hi = np.clip(t * 2 - 1, 0, 1)[..., None]
    metal = (FOIL_DARK + (FOIL_MID - FOIL_DARK) * lo + (FOIL_LIGHT - FOIL_MID) * hi) / 255.0
    metal *= (0.9 + 0.1 * shade)[..., None]
    col = col * (1 - fm[..., None]) + metal * fm[..., None]
    return np.clip(col * 255, 0, 255).astype(np.uint8)


def save(arr, path, quality=90, dpi=150):
    Image.fromarray(arr).save(path, quality=quality, dpi=(dpi, dpi), optimize=True)
    return path


def wrap_proof(n, dpi=150):
    arr = render(n, dpi)
    return save(arr, OUT / f"Cover-{n:02d}_{CV.LATIN[n]}_Proof.jpg", dpi=dpi)


def spines():
    return json.loads((OUT / "spines.json").read_text())


def front_clip(n):
    b = CV.BLEED
    return (b, b, b + CV.W, b + CV.H)


def spine_clip(n):
    sw = spines()[str(n)]["spine_mm"]
    b = CV.BLEED
    return (b + CV.W, b, b + CV.W + sw, b + CV.H)


# ------------------------------------------------------------------------------------------------ the set
def backdrop(w, h, top=(214, 209, 200), bottom=(188, 182, 172), seed=11):
    """A neutral plaster wall under daylight: warm grey, a slow gradient, a faint grain."""
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    g = np.array(top, np.float32) * (1 - yy[..., None]) + np.array(bottom, np.float32) * yy[..., None]
    g = g * (1 - 0.10 * ((xx - 0.5) ** 2 * 2))[..., None]
    g += grain((h, w), seed, 2.2)[..., None]
    return g


def shadow(canvas, x0, y0, w, h, px, strength=0.35, soft=4.0, dx=2.0, dy=3.0):
    m = np.zeros(canvas.shape[:2], np.float32)
    X0, Y0 = int(x0 + dx * px), int(y0 + dy * px)
    m[max(Y0, 0):Y0 + int(h), max(X0, 0):X0 + int(w)] = 1.0
    m = blur(m, soft * px)
    canvas *= (1 - strength * m)[..., None]


def fronts_sheet(dpi=60):
    """The eleven fronts in a row: the alif entering its circle, and the reference."""
    px = dpi / 25.4
    tiles = [render(n, dpi, clip=front_clip(n), seed=n) for n in range(1, 12)]
    th, tw = tiles[0].shape[:2]
    gap, margin = int(8 * px), int(16 * px)
    cols = 6
    rows = 2
    W = margin * 2 + cols * tw + (cols - 1) * gap
    H = margin * 2 + rows * th + (rows - 1) * gap
    cv = backdrop(W, H)
    # the Arabic order: the first volume at the right
    for i, t in enumerate(tiles):
        r, c = divmod(i, cols)
        x = W - margin - (c + 1) * tw - c * gap
        y = margin + r * (th + gap)
        shadow(cv, x, y, tw, th, px, strength=0.30, soft=3.0)
        cv[y:y + th, x:x + tw] = t
    return save(np.clip(cv, 0, 255).astype(np.uint8), OUT / "Series_Fronts.jpg", dpi=dpi)


def spine_strip(n, dpi, rounded=True):
    """The spine as it stands on the shelf: its strip of the finished cover, turned by the book's round back."""
    t = render(n, dpi, clip=spine_clip(n), seed=20 + n).astype(np.float32)
    w = t.shape[1]
    x = np.linspace(-1, 1, w, dtype=np.float32)
    if rounded:
        # a rounded back seen from the front, lit from the upper left: brighter left of centre, darker at the joints
        prof = 0.80 + 0.26 * np.cos((x + 0.25) * np.pi / 2.2) - 0.10 * np.abs(x) ** 6
        t *= prof[None, :, None]
    return t


def wood(h, w, seed, base=(120, 86, 58), streak=10.0):
    """A plain walnut board: a straight grain along its length, a faint pore."""
    rng = np.random.default_rng(seed)
    lines = blur(rng.normal(0, 1, (h, 1)).astype(np.float32), 2)[:, 0] * streak
    g = np.array(base, np.float32)[None, None, :] + lines[:, None, None] + grain((h, w), seed + 1, 2.0)[..., None]
    return g


def shelf(dpi=160):
    """The eleven on one shelf of a plain bookcase, first volume at the right; daylight from the upper left."""
    px = dpi / 25.4
    strips = [spine_strip(n, dpi) for n in range(1, 12)]
    gap = max(1, int(0.35 * px))
    books_w = sum(s.shape[1] for s in strips) + gap * 10
    bh = strips[0].shape[0]
    upright, side, above = int(20 * px), int(34 * px), int(26 * px)
    top_band, board, deck = int(20 * px), int(24 * px), int(9 * px)
    W = books_w + 2 * (side + upright)
    H = top_band + above + bh + deck + board + int(26 * px)
    cv = backdrop(W, H, top=(206, 200, 190), bottom=(184, 177, 166))
    # the case: the shelf above, the two uprights, the board the books stand on (its top seen a little)
    cv[:top_band] = wood(top_band, W, 1, base=(96, 68, 46))
    cv[top_band:top_band + int(6 * px)] *= np.linspace(0.55, 1.0, int(6 * px))[:, None, None]
    for x0 in (0, W - upright):
        cv[:, x0:x0 + upright] = wood(upright, H, 2 + x0, base=(112, 80, 54)).transpose(1, 0, 2)   # grain upright
    # the uprights shade the wall next to them
    near = np.zeros((H, W), np.float32)
    near[:, :upright] = 1
    near[:, W - upright:] = 1
    wall = np.ones((H, W), np.float32)
    wall[:, :upright] = 0
    wall[:, W - upright:] = 0
    cv *= (1 - 0.25 * blur(near, 7 * px) * wall)[..., None]
    by = top_band + above + bh
    cv[by:by + deck] = wood(deck, W, 3, base=(134, 98, 66)) * np.linspace(0.92, 1.05, deck)[:, None, None]
    cv[by + deck:by + deck + board] = wood(board, W, 4, base=(118, 84, 56))
    cv[by + deck:by + deck + int(1.0 * px)] *= 1.18                   # the lit front edge
    cv[by + deck + board:] *= 0.58
    # the books, the first at the right
    x = W - upright - side
    shadow(cv, upright + side, top_band + above, books_w, bh, px, strength=0.42, soft=6.0, dx=4.0, dy=0.0)
    for s in strips:
        w = s.shape[1]
        x -= w
        cv[top_band + above:top_band + above + bh, x:x + w] = s
        cv[top_band + above:top_band + above + int(0.6 * px), x:x + w] *= 1.25     # the cover's top edge in the light
        cv[top_band + above:top_band + above + bh, x - gap:x] *= 0.22               # the joint between two books
        x -= gap
    # the books' shadow on the deck, and the light falling off toward the floor
    cs = np.zeros((H, W), np.float32)
    cs[by:by + int(4 * px), upright + side:W - upright - side] = 1.0
    cv *= (1 - 0.45 * blur(cs, 2.0 * px))[..., None]
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    cv *= (1.02 - 0.10 * yy - 0.06 * xx)[..., None]
    return save(np.clip(cv, 0, 255).astype(np.uint8), OUT / "Series_Shelf.jpg", dpi=dpi)


def closeup(n=5, dpi=420):
    """One spine, head to tail, at close range: the foil, the rhombus, the alif on its line, the neighbours'
    edges on either side so the line is seen to run on."""
    s = spine_strip(n, dpi)
    px = dpi / 25.4
    left = spine_strip(n + 1, dpi)[:, -int(7 * px):]
    right = spine_strip(n - 1, dpi)[:, :int(7 * px)]
    gap = max(1, int(0.35 * px))
    dark = np.zeros((s.shape[0], gap, 3), np.float32) + 16
    row = np.concatenate([left * 0.8, dark, s, dark, right * 0.8], axis=1)
    H, W = row.shape[:2]
    pad = int(10 * px)
    cv = backdrop(W + 2 * pad, H + 2 * pad, top=(206, 200, 190), bottom=(186, 179, 168))
    shadow(cv, pad, pad, W, H, px, strength=0.4, soft=3.0, dx=2.0, dy=1.0)
    cv[pad:pad + H, pad:pad + W] = row
    yy = np.linspace(0, 1, cv.shape[0], dtype=np.float32)[:, None]
    cv *= (1.03 - 0.10 * yy)[..., None]
    return save(np.clip(cv, 0, 255).astype(np.uint8), OUT / "Series_Spine-Closeup.jpg", dpi=dpi)


def main(argv):
    vols = [int(a) for a in argv if a.isdigit()]
    if vols:
        for n in vols:
            print(wrap_proof(n))
        return
    for n in range(1, 12):
        print(wrap_proof(n))
    print(fronts_sheet())
    print(shelf())
    print(closeup())


if __name__ == "__main__":
    main(sys.argv[1:])
