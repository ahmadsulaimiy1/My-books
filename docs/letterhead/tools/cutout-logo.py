#!/usr/bin/env python3
"""Cut the supplied office mark off its background.

    python3 tools/cutout-logo.py <source-image> [out.png]

The mark separates from the paper on two signals the drop shadow does not
share: the inlay is COOL (B > R) where the paper and its shadow are always
warm (R > B), and the gold is SATURATED where neither of them is. Luminance
alone is the wrong axis — it cannot tell a deep navy from a deep shadow, which
is why a plain brightness threshold leaves a ragged halo around the mark.

Writes the colour cutout and, beside it, the desaturated companion used for
the watermark and for black-and-white reproduction.

The two row crops below are tuned to the supplied 1079x1080 artwork — the
letterbox bar at the top, and the typography below the mark. Adjust them for a
different source.
"""
from PIL import Image, ImageFilter, ImageOps, ImageEnhance
import numpy as np, sys, os

HERE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")

CROP_TOP    = 11    # first row below the letterbox bar
CROP_BOTTOM = 612   # first row of the typography beneath the mark

def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__.strip())
    src = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ASSETS, "insignia-logo.png")

    im = Image.open(src).convert("RGB")
    a  = np.asarray(im).astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    sat = a.max(axis=2) - a.min(axis=2)
    lum = 0.299 * R + 0.587 * G + 0.114 * B

    gold = sat >= 34                        # the paper tops out near 29, even beside the mark
    navy = ((B - R) >= 10) & (lum <= 145)   # the only cool thing on the page
    m = gold | navy
    m[:CROP_TOP]     = False
    m[CROP_BOTTOM:]  = False

    alpha = Image.fromarray((m * 255).astype(np.uint8))
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))  # open: kill specks
    alpha = alpha.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.MinFilter(7))  # close: bridge the seams
    alpha = alpha.filter(ImageFilter.MinFilter(5))                                   # erode: shed the shadow ring
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))                              # feather the cut

    aa = np.asarray(alpha)
    ys, xs = np.where(aa > 8)
    P = 10
    box = (xs.min() - P, ys.min() - P, xs.max() + P + 1, ys.max() + P + 1)
    out = im.copy(); out.putalpha(alpha); out = out.crop(box)
    out.save(out_path, optimize=True)
    print(f"{out_path}  {out.size[0]}x{out.size[1]}  {os.path.getsize(out_path)//1024} KB")

    # the desaturated companion, contrast-boosted so the strapwork still
    # separates on a photocopier, a fax, and behind the watermark's 4% opacity
    grey_path = os.path.join(os.path.dirname(out_path), "insignia-logo-grey.png")
    a8 = out.split()[3]
    g = ImageEnhance.Contrast(ImageOps.grayscale(out.convert("RGB"))).enhance(1.35)
    Image.merge("RGBA", (g, g, g, a8)).save(grey_path, optimize=True)
    print(f"{grey_path}  {os.path.getsize(grey_path)//1024} KB")

if __name__ == "__main__":
    main()
