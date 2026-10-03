#!/usr/bin/env python3
"""Cut a signature off its white ground.

    python3 tools/cutout-signature.py <source> <out.png>

Blue ink on white paper separates cleanly on blueness, not on darkness — a
darkness threshold eats the thin, fast strokes at the ends of a signature,
which are exactly the parts that make it look handwritten. The ink is kept at
its own colour so it can be recoloured in CSS if the office ever changes ink.
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter

def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__.strip())
    src, out = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    a = np.asarray(im).astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]

    # ink = decisively blue. Paper is neutral, so B - mean(R,G) is near zero on it.
    blueness = B - (R + G) / 2
    alpha = np.clip((blueness - 12) / 55, 0, 1)
    # the thinnest strokes are anti-aliased down to a few percent; lift them
    alpha = np.clip(alpha * 1.45, 0, 1)

    al = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.4))
    aa = np.asarray(al)
    ys, xs = np.where(aa > 6)
    P = 6
    box = (max(xs.min()-P, 0), max(ys.min()-P, 0), xs.max()+P+1, ys.max()+P+1)

    ink = np.zeros(a.shape, np.uint8)
    ink[..., 0], ink[..., 1], ink[..., 2] = 16, 38, 122     # a settled ink blue
    sig = Image.fromarray(np.dstack([ink, aa]), "RGBA").crop(box)
    sig.save(out, optimize=True)
    print(f"{out}  {sig.size[0]}x{sig.size[1]}  {os.path.getsize(out)//1024} KB")

if __name__ == "__main__":
    main()
