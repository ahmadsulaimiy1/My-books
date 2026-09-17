#!/usr/bin/env python3
"""
Compose the production presentation.

    python3 tools/build-presentation.py

Renders the actual print PDFs at 300dpi and photographs them: a studio surface,
raking light from the top left, the sheets laid at a slight angle with true contact
shadows, and a magnified detail of the binding edge so the metals — engraved
gold, milled stainless, gold hairline — can be counted against the sapphire.

Nothing here is decoration on top of the design. Every pixel comes from the same
PDF a printer would receive; only the lighting and the table are added.
"""
import os, math
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageChops
import pymupdf

HERE   = os.path.dirname(os.path.abspath(__file__))
ROOT   = os.path.dirname(HERE)
PRINT  = os.path.join(ROOT, "print")
OUT    = os.path.join(ROOT, "presentation.jpg")
DPI    = 300


def page(name):
    d = pymupdf.open(os.path.join(PRINT, f"{name}.pdf"))
    pm = d[0].get_pixmap(dpi=DPI)
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples).convert("RGBA")


def studio(w, h):
    """A dark surface with a raking key light from the top left."""
    yy, xx = np.mgrid[0:h, 0:w].astype(float)
    d = np.sqrt(((xx - w*0.24)/(w*0.95))**2 + ((yy - h*0.10)/(h*1.15))**2)
    v = np.clip(1.0 - d*0.92, 0, 1) ** 1.7
    base = np.array([22, 23, 26]); lit = np.array([74, 72, 70])
    img = base + (lit - base) * v[..., None]
    rng = np.random.default_rng(3)
    img += rng.normal(0, 2.0, (h, w, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def sheet(img, angle, scale, light=True):
    """A sheet as a physical object: lit, edged, rotated, with a contact shadow."""
    w = int(img.width * scale)
    im = img.resize((w, int(img.height * scale)), Image.LANCZOS)

    if light:
        # the same key light falls across the paper
        yy, xx = np.mgrid[0:im.height, 0:im.width].astype(float)
        g = 1.0 - 0.30*np.clip((xx/im.width)*0.8 + (yy/im.height)*0.9 - 0.15, 0, 1)
        a = np.asarray(im).astype(float)
        a[..., :3] *= g[..., None]
        im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

    # the cut edge of the stock catches the light along its top and left
    d = ImageDraw.Draw(im)
    d.line([(0, 0), (im.width, 0)], fill=(255, 252, 245, 150), width=2)
    d.line([(0, 0), (0, im.height)], fill=(255, 252, 245, 110), width=2)
    d.line([(im.width-1, 0), (im.width-1, im.height)], fill=(90, 80, 62, 120), width=2)
    d.line([(0, im.height-1), (im.width, im.height-1)], fill=(70, 62, 48, 150), width=2)

    rot = im.rotate(angle, resample=Image.BICUBIC, expand=True)

    # contact shadow: tight and dark where the sheet meets the table, wide and
    # soft further out — one blur cannot do both
    sil = rot.split()[3]
    near = sil.filter(ImageFilter.GaussianBlur(9))
    far  = sil.filter(ImageFilter.GaussianBlur(46))
    sh = Image.new("RGBA", rot.size, (0, 0, 0, 0))
    sh.putalpha(ImageChops.add(near.point(lambda v: int(v*0.45)),
                               far.point(lambda v: int(v*0.42))))
    return rot, sh


def detail(img, box, width):
    """A magnified crop, framed, for counting the plates in the edge.

    The crop is SCALED to the frame rather than cropped to it — cropping after
    magnifying just throws away the part worth showing."""
    c = img.crop(box)
    h = int(round(width * c.height / c.width))
    c = c.resize((width, h), Image.LANCZOS)
    fr = Image.new("RGBA", (width + 4, h + 4), (197, 167, 115, 255))
    fr.paste(c, (2, 2))
    return fr


def page_n(name, n):
    d = pymupdf.open(os.path.join(PRINT, f"{name}.pdf"))
    pm = d[n].get_pixmap(dpi=DPI)
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples).convert("RGBA")


def main():
    letter = page_n("letter-tahniah-dr-adewuyi", 0)
    blank  = page_n("letter-tahniah-dr-adewuyi", 1)

    W, H = 2400, 1600
    canvas = studio(W, H)

    back, back_sh = sheet(blank,  3.4, 0.30)
    canvas.alpha_composite(back_sh, (1245, 250))
    canvas.alpha_composite(back,    (1230, 232))

    front, front_sh = sheet(letter, -2.2, 0.355)
    canvas.alpha_composite(front_sh, (238, 168))
    canvas.alpha_composite(front,    (222, 150))

    # the medallion, magnified: a complete insignia inside a struck gold ring,
    # with its own clear space, sitting on the plate's stepped edge
    px_mm = DPI / 25.4
    box = (int(112*px_mm), int(4*px_mm), int(182*px_mm), int(58*px_mm))
    det = detail(letter, box, 470)
    dsh = Image.new("RGBA", det.size, (0, 0, 0, 0))
    dsh.putalpha(Image.new("L", det.size, 200).filter(ImageFilter.GaussianBlur(24)))
    pos = (1700, 1130)
    canvas.alpha_composite(dsh, (pos[0] + 12, pos[1] + 16))
    canvas.alpha_composite(det, pos)

    d = ImageDraw.Draw(canvas)
    d.line([(pos[0], pos[1] - 26), (pos[0] + 120, pos[1] - 26)],
           fill=(197, 167, 115, 210), width=2)

    canvas.convert("RGB").save(OUT, quality=88, optimize=True, progressive=True)
    print(f"{OUT}  {W}x{H}  {os.path.getsize(OUT)//1024} KB")


if __name__ == "__main__":
    main()
