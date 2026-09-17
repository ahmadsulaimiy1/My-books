#!/usr/bin/env python3
"""
Render the office mark as each production process would actually produce it.

    python3 tools/build-mark-variants.py

A foil die and an emboss die cut a SILHOUETTE — they cannot reproduce the
mark's navy inlay or its modelling. So each variant is built from the mark's
alpha channel alone:

    insignia-foil.png     champagne hot foil, with its brushed grain
    insignia-emboss.png   blind emboss  — raised out of the sheet, no ink
    insignia-deboss.png   deboss        — pressed into the sheet, no ink

These are baked here rather than composed in CSS because `mask-image` does not
survive Chrome's print-to-PDF: the mark comes out of the PDF as a plain gold
rectangle. Baking also gives control of the shadow ring that a CSS
drop-shadow filter cannot.

Light is fixed at top-left for the whole stationery set, so emboss and deboss
stay physically consistent with the type treatments in materials.css.
"""
import numpy as np, os
from PIL import Image, ImageFilter, ImageChops

HERE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

# the champagne foil ramp — the same eleven stops as --foil in materials.css
FOIL_STOPS = [
    (0.00, "#8B6F3E"), (0.09, "#C2A570"), (0.19, "#EEDFB8"), (0.27, "#C8AC78"),
    (0.38, "#9A7C47"), (0.50, "#E4D2A6"), (0.60, "#B99A63"), (0.72, "#F3E7C9"),
    (0.82, "#C0A26C"), (0.92, "#8E7343"), (1.00, "#D6BF90"),
]
FOIL_ANGLE_DEG = 104.0
PAPER          = (243, 239, 229)
SHADOW         = (112,  94,  64)


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def foil_field(w, h):
    """The foil gradient, projected across the box at FOIL_ANGLE_DEG."""
    th = np.deg2rad(FOIL_ANGLE_DEG)
    ux, uy = np.cos(th), np.sin(th)
    xx, yy = np.meshgrid(np.arange(w), np.arange(h))
    t = xx * ux + yy * uy
    t = (t - t.min()) / max(np.ptp(t), 1e-6)

    pos = np.array([s[0] for s in FOIL_STOPS])
    cols = np.array([hex_rgb(s[1]) for s in FOIL_STOPS], float)
    out = np.zeros((h, w, 3))
    for c in range(3):
        out[..., c] = np.interp(t, pos, cols[:, c])

    # brushed grain, soft-light, so the foil turns the light rather than
    # sitting flat — this is most of what separates foil from yellow ink
    gp = os.path.join(ASSETS, "foil-grain.png")
    if os.path.exists(gp):
        g = Image.open(gp).convert("L")
        reps = (w // g.width + 2, h // g.height + 2)
        g = np.asarray(Image.fromarray(np.tile(np.asarray(g), reps[::-1]))
                       .crop((0, 0, w, h))).astype(float) / 255.0
        b = out / 255.0
        soft = np.where(g[..., None] <= 0.5,
                        2 * b * g[..., None] + b**2 * (1 - 2 * g[..., None]),
                        2 * b * (1 - g[..., None]) + np.sqrt(np.clip(b, 0, 1)) * (2 * g[..., None] - 1))
        out = (b * 0.45 + soft * 0.55) * 255.0
    return np.clip(out, 0, 255)


def over(dst, src):
    """src OVER dst, both float RGBA in 0..1."""
    sa = src[..., 3:4]; da = dst[..., 3:4]
    oa = sa + da * (1 - sa)
    rgb = np.divide(src[..., :3] * sa + dst[..., :3] * da * (1 - sa),
                    np.where(oa == 0, 1, oa))
    return np.concatenate([rgb, oa], axis=-1)


def relief(alpha, face, pressed):
    """Build a blind emboss (pressed=False) or a deboss (pressed=True).

    The face is the paper itself — no ink. All that is visible is the ring of
    light and shadow the die leaves, so that ring is what we actually draw."""
    A = Image.fromarray((alpha * 255).astype(np.uint8))
    dx, dy = (2.6, 3.2)
    if pressed:
        dx, dy = -dx, -dy                       # same light source, inverted relief

    sh = ImageChops.offset(A, int(round(dx)), int(round(dy))).filter(ImageFilter.GaussianBlur(2.4))
    hi = ImageChops.offset(A, int(round(-dx)), int(round(-dy))).filter(ImageFilter.GaussianBlur(2.4))
    sh = np.clip(np.asarray(sh).astype(float) / 255 - alpha, 0, 1) * (0.52 if not pressed else 0.60)
    hi = np.clip(np.asarray(hi).astype(float) / 255 - alpha, 0, 1) * 0.92

    h, w = alpha.shape
    out = np.zeros((h, w, 4))
    out = over(out, np.concatenate([np.full((h, w, 3), np.array(SHADOW) / 255), sh[..., None]], -1))
    out = over(out, np.concatenate([np.ones((h, w, 3)),                          hi[..., None]], -1))
    out = over(out, np.concatenate([np.full((h, w, 3), np.array(face) / 255),
                                    (alpha * 0.96)[..., None]], -1))
    return (np.clip(out, 0, 1) * 255).astype(np.uint8)


def split_mark(canvas):
    """Separate the mark into its GOLD strapwork and its INLAY.

    A die cut from the silhouette alone comes out a solid blob — the strapwork
    that makes the mark legible is exactly the boundary between these two. So
    the foil is cut to the strapwork only, and the inlay is left unfoiled: on a
    sapphire field it reads as sapphire, on the sheet it reads as paper, which
    is what a single-colour foil on a coloured ground actually does."""
    a = np.asarray(canvas).astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    A = a[..., 3].astype(float) / 255.0
    sat = a[..., :3].max(axis=2) - a[..., :3].min(axis=2)
    lum = 0.299 * R + 0.587 * G + 0.114 * B
    inlay = ((B - R) >= 10) & (lum <= 150) & (A > 0.35)
    gold = (A > 0.35) & ~inlay
    soften = lambda m: np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                                  .filter(ImageFilter.GaussianBlur(0.7))).astype(float) / 255.0
    return soften(gold) * A, soften(inlay) * A, A


def main():
    src = Image.open(os.path.join(ASSETS, "insignia-logo.png")).convert("RGBA")
    # a margin, so the relief ring is not clipped by the artwork's own bounds
    pad = 10
    w, h = src.width + 2 * pad, src.height + 2 * pad
    canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    canvas.paste(src, (pad, pad))
    gold, inlay, full = split_mark(canvas)

    # ── foil: cut to the strapwork ──────────────────────────────────────────
    rgb = foil_field(w, h)
    rgb = (np.round(rgb / 2) * 2).astype(np.uint8)   # fewer levels; PNG halves
    Image.fromarray(np.dstack([rgb, (gold * 255).astype(np.uint8)]), "RGBA").save(
        os.path.join(ASSETS, "insignia-foil.png"), optimize=True)

    # ── relief: a sculpted die, the strapwork standing above the inlay ──────
    for name, pressed in (("insignia-emboss.png", False), ("insignia-deboss.png", True)):
        base = relief(full, PAPER, pressed=pressed).astype(float) / 255
        detail = relief(gold, PAPER, pressed=pressed).astype(float) / 255
        Image.fromarray((np.clip(over(base, detail), 0, 1) * 255).astype(np.uint8), "RGBA").save(
            os.path.join(ASSETS, name), optimize=True)

    for f in ("insignia-foil.png", "insignia-emboss.png", "insignia-deboss.png"):
        print(f"{f:24s} {w}x{h}  {os.path.getsize(os.path.join(ASSETS, f))//1024} KB")


if __name__ == "__main__":
    main()
