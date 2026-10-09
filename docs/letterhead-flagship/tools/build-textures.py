#!/usr/bin/env python3
"""
Generate the tileable material textures.

    python3 tools/build-textures.py

Flat CSS gradients read as screen artwork. Real stationery reads as paper
because of what happens at 1-3 px: cotton fibre, the tooth of the sheet, and
the slight cloudiness of a mould-made stock. These are generated rather than
photographed so they tile seamlessly and stay tiny.

  paper-cotton.png   the sheet itself - fibre fleck + long fibres + cloud
  foil-grain.png     the brushed directional grain inside a foil block
"""
import numpy as np, os
from PIL import Image, ImageFilter

HERE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
N = 256
rng = np.random.default_rng(7)


def wrap_blur(a, r):
    """Blur with wrap-around, so the tile stays seamless at its edges."""
    t = np.tile(a, (3, 3))
    im = Image.fromarray(np.clip(t, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im).astype(float)[N:2*N, N:2*N]


def cotton():
    # 1. fine fleck — the tooth of the sheet
    fleck = rng.normal(128, 16, (N, N))
    fleck = wrap_blur(fleck, 0.6)

    # 2. long fibres — a cotton sheet has visible strands, mostly lying flat
    fib = np.zeros((N, N))
    for _ in range(180):
        y, x = rng.integers(0, N, 2)
        ln = rng.integers(10, 48)
        ang = rng.normal(0.0, 0.45)                      # mostly horizontal
        dy, dx = np.sin(ang), np.cos(ang)
        v = rng.normal(0, 9)
        for t in range(ln):
            fib[int(y + dy*t) % N, int(x + dx*t) % N] += v
    fib = wrap_blur(fib + 128, 0.8) - 128

    # 3. cloud — mould-made stock is never perfectly even
    cloud = wrap_blur(rng.normal(128, 40, (N, N)), 15) - 128

    a = 128 + (fleck - 128) * 1.0 + fib * 0.55 + cloud * 0.9
    # The texture is laid over the sheet at a few percent, so its full dynamic
    # range is never seen. Compressing it here, and quantising to a handful of
    # levels, costs nothing visible and takes the file from 160 KB to ~20 KB —
    # PNG cannot compress broadband noise, but it compresses few levels well.
    a = np.clip(128 + (a - 128) * 0.34, 0, 255)
    a = (np.round(a / 3) * 3).astype(np.uint8)
    Image.fromarray(a, "L").save(os.path.join(ASSETS, "paper-cotton.png"), optimize=True)
    return "paper-cotton.png"


def foil_grain():
    # brushed metal: strong directional streaking, almost no cross-grain
    g = rng.normal(128, 30, (N, N))
    g = np.asarray(Image.fromarray(np.clip(np.tile(g, (3, 3)), 0, 255).astype(np.uint8))
                   .filter(ImageFilter.GaussianBlur(0.4))).astype(float)[N:2*N, N:2*N]
    # smear along x by averaging a run of columns, with wrap
    k = 14
    sm = sum(np.roll(g, s, axis=1) for s in range(-k, k + 1)) / (2 * k + 1)
    a = np.clip(128 + (sm - 128) * 3.4 * 0.5, 0, 255)
    a = (np.round(a / 3) * 3).astype(np.uint8)
    Image.fromarray(a, "L").save(os.path.join(ASSETS, "foil-grain.png"), optimize=True)
    return "foil-grain.png"


if __name__ == "__main__":
    for f in (cotton(), foil_grain()):
        p = os.path.join(ASSETS, f)
        print(f"{f:20s} {N}x{N}  {os.path.getsize(p)//1024} KB")
