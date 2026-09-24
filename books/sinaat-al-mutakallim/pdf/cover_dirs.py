#!/usr/bin/env python3
"""Art-direction study for the cover: three radically different directions, front panels only.

    A  Arabic Architectural Luxury   sapphire book cloth, blind-debossed title panel with engineered
                                     corners, calligraphic Naskh title in gold foil, measure bands
    B  Contemporary Manuscript Luxury  pearl paper with laid lines, gold-and-sapphire جدول frame,
                                     sapphire calligraphic title, a sapphire foot band for the author
    C  Royal Editorial               the construction drawing (cover.py): dot, alif, line and ring

    python3 cover_dirs.py      renders .cache/dir-A.pdf, dir-B.pdf, dir-C.pdf and a comparison board
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cover_kit as CV  # noqa: E402
import lettering as L  # noqa: E402

W, H = CV.W, CV.H


# --------------------------------------------------------------------------- surfaces

def cloth(size, dpi, base_top, base_bot, seed=3, relief=None, deboss=True, weave=0.035):
    """Book cloth: a fine woven grain over a jewel field, relief lit from the upper left."""
    w, h = size
    arr = CV.field(size, dpi, seed=seed, relief=relief, deboss=deboss)
    # re-tint to the requested field while keeping the lighting and relief
    top = np.array(base_top, np.float32) / 255
    bot = np.array(base_bot, np.float32) / 255
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    tgt = top * (1 - yy) + bot * yy
    ref = np.array(CV.FIELD_TOP, np.float32) / 255 * (1 - yy) + np.array(CV.FIELD_BOT, np.float32) / 255 * yy
    arr = np.clip(arr / np.maximum(ref, 1e-3) * tgt, 0, 1)
    if weave:
        rng = np.random.default_rng(seed + 1)
        pitch = dpi / 25.4 * 0.42           # ~0.4 mm threads
        xs = np.arange(w, dtype=np.float32)[None, :]
        ys = np.arange(h, dtype=np.float32)[:, None]
        warp = np.sin(xs / pitch * 2 * math.pi + rng.normal(0, .35, (1, w)).astype(np.float32).cumsum(axis=1) * 0.02)
        weft = np.sin(ys / pitch * 2 * math.pi + rng.normal(0, .35, (h, 1)).astype(np.float32).cumsum(axis=0) * 0.02)
        slub = rng.normal(0, 1, (h // 6 + 1, w // 40 + 1)).astype(np.float32)
        slub = np.asarray(Image.fromarray(((slub * 40) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255 - .5
        tex = 0.5 * warp * weft + 0.35 * slub
        arr = np.clip(arr * (1 + weave * tex[..., None]), 0, 1)
    return arr


def paper(size, dpi, seed=9, relief=None):
    """Warm pearl paper: fibres, faint laid and chain lines, relief lit from the upper left."""
    w, h = size
    rng = np.random.default_rng(seed)
    base = np.ones((h, w, 3), np.float32) * (np.array([244, 239, 227], np.float32) / 255)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    base = base * (1.0 - 0.035 * yy)
    fib = rng.normal(0, 1, (h, w)).astype(np.float32)
    fib = np.asarray(Image.fromarray(((fib * 22) + 128).clip(0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1)), np.float32) / 255 - .5
    ys = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)[None, :]
    laid = (np.sin(ys / (dpi / 25.4 * 0.9) * 2 * math.pi) > 0.92).astype(np.float32)
    chain = (np.abs(((xs / (dpi / 25.4)) % 25.0) - 12.5) < 0.12).astype(np.float32)
    base = base * (1 + 0.035 * fib[..., None] - 0.012 * laid[..., None] - 0.02 * chain[..., None])
    if relief is not None:
        hmap = np.asarray(Image.fromarray((relief * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(dpi / 300 * 1.1)), np.float32) / 255
        gy, gx = np.gradient(-hmap * dpi / 300 * 3.0)
        lx, ly, lz = -0.55, -0.62, 0.55
        n = np.sqrt(gx * gx + gy * gy + 1)
        norm = math.sqrt(lx * lx + ly * ly + lz * lz)
        shade = ((-gx * lx - gy * ly + lz) / n) / norm - lz / norm
        base = base * (1 + 0.5 * shade[..., None]) - 0.02 * hmap[..., None]
    return np.clip(base, 0, 1)


# --------------------------------------------------------------------------- lettering

def title_paths(font_css, family="Amiri", weight=700, s1=19.0, s2=29.0, cx=100.0, base2=118.0, gap=2.0,
                fill="url(#foil)", shadow=True, rim=True, center=True, x_right=None):
    face = L.arabic_face(font_css, family, weight)
    l1 = L.Line(CV.TITLE_1, face, s1)
    l2 = L.Line(CV.TITLE_2, face, s2)
    # line one sits above line two; gap measured between line one's lowest ink and line two's highest ink
    top2 = base2 + l2.bounds[1]
    base1 = top2 - gap - l1.bounds[3]
    if center:
        x1, x2 = cx - l1.width / 2, cx - l2.width / 2
    else:
        x1, x2 = x_right - l1.width, x_right - l2.width
    out = []
    for ln, x, b in ((l1, x1, base1), (l2, x2, base2)):
        if shadow:
            out.append(L.svg_path(ln, x + 0.16, b + 0.22, fill="#020A20", fill_opacity="0.55"))
        if rim:
            out.append(L.svg_path(ln, x - 0.06, b - 0.1, fill="#FFF3D6", fill_opacity="0.3"))
        out.append(L.svg_path(ln, x, b, fill=fill))
    box = (min(x1, x2) + l2.bounds[0] * 0, base1 + l1.bounds[1], max(x1 + l1.width, x2 + l2.width), base2 + l2.bounds[3])
    return "".join(out), box


# --------------------------------------------------------------------------- ornament

def measure_band(x1, x2, y, gold="url(#foil)", ticks=True, center_ring=True, blind=None):
    """The book's measure: a hairline with nuqta nodes at the ends and a ring-and-dot at the centre."""
    cx = (x1 + x2) / 2
    out = [f'<rect x="{x1:.2f}" y="{y - 0.14:.2f}" width="{x2 - x1:.2f}" height="0.28" fill="{gold}"/>']
    for x in (x1, x2):
        out.append(CV.foil_rhomb(x, y, 1.25))
    if center_ring:
        out.append(f'<circle cx="{cx:.2f}" cy="{y:.2f}" r="2.9" fill="#0A2156" stroke="{gold}" stroke-width="0.3"/>')
        out.append(CV.foil_rhomb(cx, y, 1.05))
    if ticks:
        n = 14
        for k in range(1, n):
            x = x1 + (x2 - x1) * k / n
            if abs(x - cx) < 5:
                continue
            out.append(f'<rect x="{x - 0.09:.2f}" y="{y - 1.1:.2f}" width="0.18" height="2.2" fill="{gold}" fill-opacity="0.8"/>')
    return "".join(out)


def panel_frame(x1, y1, x2, y2, gold="url(#foil)", inset=2.2, ext=3.6):
    """Double rule with construction extensions past the corners and a nuqta at each crossing."""
    out = []
    t = 0.5
    for (ax, ay, bx, by) in ((x1 - ext, y1, x2 + ext, y1), (x1 - ext, y2, x2 + ext, y2)):
        out.append(f'<rect x="{ax:.2f}" y="{ay - t / 2:.2f}" width="{bx - ax:.2f}" height="{t}" fill="{gold}"/>')
    for (ax, ay, bx, by) in ((x1, y1 - ext, x1, y2 + ext), (x2, y1 - ext, x2, y2 + ext)):
        out.append(f'<rect x="{ax - t / 2:.2f}" y="{ay:.2f}" width="{t}" height="{by - ay:.2f}" fill="{gold}"/>')
    i = inset
    out.append(f'<rect x="{x1 + i:.2f}" y="{y1 + i:.2f}" width="{x2 - x1 - 2 * i:.2f}" height="{y2 - y1 - 2 * i:.2f}" '
               f'fill="none" stroke="{gold}" stroke-width="0.2"/>')
    for (x, y) in ((x1, y1), (x2, y1), (x1, y2), (x2, y2)):
        out.append(CV.foil_rhomb(x, y, 1.5))
    return "".join(out)


def jewel(x, y):
    """The one crimson accent: a ruby set in a gold rhombus."""
    return (f'<path d="{CV.rhomb_path(x, y, 3.2)}" fill="#0A2156" stroke="url(#foil)" stroke-width="0.45"/>'
            + CV.crimson_rhomb(x, y, 1.6))


# --------------------------------------------------------------------------- pages

PAGE_CSS = """
@page { size: 200mm 260mm; margin: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; }
.cvr { position: relative; width: 200mm; height: 260mm; overflow: hidden; }
.cvr > img, .cvr > svg { position: absolute; left: 0; top: 0; width: 200mm; height: 260mm; }
.tx { position: absolute; margin: 0; white-space: nowrap; }
"""


def page(font_css, tex, svg, texts, name):
    body = "".join(f'<p class="tx" style="{style}">{txt}</p>' for txt, style in texts)
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{name}</title>
<style>{font_css}</style><style>{PAGE_CSS}</style></head><body><section class="cvr">
<img src="{tex.as_uri()}" alt=""><svg viewBox="0 0 200 260" xmlns="http://www.w3.org/2000/svg"><defs>{CV.gold_defs()}</defs>{svg}</svg>
{body}</section></body></html>"""


def centered(y_mm, css):
    return f"top:{y_mm}mm; left:0; right:0; text-align:center; {css}"


def lattice(x1, y1, x2, y2, pitch=6.0, sw=0.22, depth=0.32):
    """Blind rhombic lattice: two families of diagonals, clipped to the panel."""
    prims = []
    h = y2 - y1
    c = x1 - h
    while c < x2:
        a0, b0 = c, y1
        a1, b1 = c + h, y2
        # clip the segment to x1..x2
        if a0 < x1:
            b0 += (x1 - a0); a0 = x1
        if a1 > x2:
            b1 -= (a1 - x2); a1 = x2
        if a1 > a0:
            prims.append(("line", a0, b0, a1, b1, sw, depth))
        a0, b0 = c + h, y1
        a1, b1 = c, y2
        if a0 > x2:
            b0 += (a0 - x2); a0 = x2
        if a1 < x1:
            b1 -= (x1 - a1); a1 = x1
        if a0 > a1:
            prims.append(("line", a0, b0, a1, b1, sw, depth))
        c += pitch
    return prims


def direction_a(font_css, dpi, s1=21.0, s2=33.0, t1=None, lat=True, panel=(24.0, 46.0, 176.0, 144.0), tag=""):
    px1, py1, px2, py2 = panel
    size = (round(CV.mm(W, dpi)), round(CV.mm(H, dpi)))
    prims = lattice(px1 + 3.4, py1 + 3.4, px2 - 3.4, py2 - 3.4) if lat else []
    rel = CV.draw_relief(size, prims, dpi)
    k = dpi / 25.4
    step = np.zeros_like(rel)
    step[int((py1 + 0.6) * k):int((py2 - 0.6) * k), int((px1 + 0.6) * k):int((px2 - 0.6) * k)] = 0.5
    title_l1 = t1 or CV.TITLE_1
    # knock the lattice out behind the lettering
    face = L.arabic_face(font_css, "Amiri", 700)
    l1 = L.Line(title_l1, face, s1)
    l2 = L.Line(CV.TITLE_2, face, s2)
    mid = (py1 + py2) / 2
    block_h = (l1.bounds[3] - l1.bounds[1]) + 1.2 + (l2.bounds[3] - l2.bounds[1])
    base2 = mid - 3.0 + block_h / 2 - l2.bounds[3]
    rel = np.maximum(rel, step)
    arr = cloth(size, dpi, (13, 38, 98), (7, 23, 64), relief=rel)
    tex = CV.save_jpeg(arr, CV.CACHE / f"dirA{tag}-{dpi}.jpg", dpi)
    saved = CV.TITLE_1
    CV.TITLE_1 = title_l1
    title, box = title_paths(font_css, "Amiri", 700, s1=s1, s2=s2, cx=100, base2=base2, gap=1.2)
    CV.TITLE_1 = saved
    svg = (measure_band(28, 172, 22) + panel_frame(px1, py1, px2, py2) + jewel(100, py1) + title
           + measure_band(28, 172, 234, ticks=False, center_ring=False))
    sub_css = ("display:flex; align-items:center; justify-content:center; gap:4.2mm; font-family: Amiri; font-size: 18.5pt; color: #F4EFE3;")
    rule = "<i style='display:block; width:16mm; height:.28mm; background:linear-gradient(90deg,#A7884B,#F3E6C0,#B79859)'></i>"
    texts = [
        (f"{rule}<span>{CV.SUBTITLE}</span>{rule}", centered(py2 + 12.5, sub_css)),
        ("تأليف", centered(186, "font-family: 'Noto Kufi Arabic'; font-weight: 600; font-size: 7.6pt; color: #C9AE6B;")),
        (CV.AUTHOR, centered(191.5, "font-family: Amiri; font-weight: 700; font-size: 20pt; color: #F4EFE3; text-shadow: 0 .4pt 0 rgba(2,10,32,.6);")),
        (CV.DUA, centered(239.5, "font-family: Amiri; font-size: 8.8pt; color: #93A2CB;")),
    ]
    return page(font_css, tex, svg, texts, "A")


def direction_b(font_css, dpi):
    fx1, fy1, fx2, fy2 = 22.0, 26.0, 178.0, 160.0
    size = (round(CV.mm(W, dpi)), round(CV.mm(H, dpi)))
    arr = paper(size, dpi)
    # sapphire foot band like a leather wrapper
    k = dpi / 25.4
    band_y = int(176 * k)
    band = cloth((size[0], size[1] - band_y), dpi, (12, 36, 94), (7, 22, 62), weave=0.03)
    arr[band_y:, :, :] = band
    tex = CV.save_jpeg(arr, CV.CACHE / f"dirB-{dpi}.jpg", dpi)
    title, box = title_paths(font_css, "Amiri", 700, s1=19.0, s2=30.0, cx=100, base2=112.0, gap=1.4,
                             fill="#0B2A6E", shadow=False, rim=False)
    jadwal = (f'<rect x="{fx1}" y="{fy1}" width="{fx2 - fx1}" height="{fy2 - fy1}" fill="none" stroke="#0B2A6E" stroke-width="0.35"/>'
              f'<rect x="{fx1 + 1.2}" y="{fy1 + 1.2}" width="{fx2 - fx1 - 2.4}" height="{fy2 - fy1 - 2.4}" fill="none" stroke="url(#foil)" stroke-width="1.5"/>'
              f'<rect x="{fx1 + 2.4}" y="{fy1 + 2.4}" width="{fx2 - fx1 - 4.8}" height="{fy2 - fy1 - 4.8}" fill="none" stroke="#0B2A6E" stroke-width="0.25"/>')
    head = (f'<rect x="40" y="46" width="120" height="0.3" fill="#B8995A"/>' + CV.foil_rhomb(100, 46.15, 2.1)
            + f'<path d="{CV.rhomb_path(100, 46.15, 0.9)}" fill="#A8172E"/>')
    svg = (jadwal + head + title
           + f'<rect x="0" y="175.6" width="200" height="0.8" fill="url(#foil)"/>'
           + measure_band(40, 160, 229, ticks=False, center_ring=True))
    texts = [
        (CV.SUBTITLE, centered(127, 'font-family: Amiri; font-size: 18pt; color: #7F5F12;')),
        ("منهج شامل في النطق والتعبير والخطاب وآداب التواصل والملكة الشفهية",
         centered(142, 'font-family: Amiri; font-size: 10.6pt; color: #4A4540;')),
        ("تأليف", centered(188, "font-family: 'Noto Kufi Arabic'; font-weight: 600; font-size: 7.6pt; color: #C9AE6B;")),
        (CV.AUTHOR, centered(193.5, 'font-family: Amiri; font-weight: 700; font-size: 20pt; color: #F4EFE3;')),
        (CV.DUA, centered(240, 'font-family: Amiri; font-size: 8.8pt; color: #93A2CB;')),
    ]
    return page(font_css, tex, svg, texts, "B")


def main():
    import build as B
    import book_build as K
    font_css = B.static_instances(B.ensure_fonts(K.BOOK_FONT_CSS, "bookfonts"))
    dpi = 200
    if "--a" in sys.argv:
        outs = [B.render(direction_a(font_css, dpi, tag="1"), "dir-A1"),
                B.render(direction_a(font_css, dpi, t1="صنـاعة", tag="2"), "dir-A2"),
                B.render(direction_a(font_css, dpi, s1=23.0, s2=36.0, panel=(22.0, 44.0, 178.0, 146.0), tag="3"), "dir-A3")]
    else:
        outs = [B.render(direction_a(font_css, dpi), "dir-A"), B.render(direction_b(font_css, dpi), "dir-B")]
        html, _ = CV.build_front(font_css, dpi=dpi)
        outs.append(B.render(html, "dir-C"))
    import pypdfium2 as pdfium
    ims = [pdfium.PdfDocument(str(p))[0].render(scale=1.6).to_pil() for p in outs]
    w, h = ims[0].size
    board = Image.new("RGB", (3 * w + 80, h + 40), (226, 222, 214))
    for i, im in enumerate(ims):
        board.paste(im, (20 + i * (w + 20), 20))
    board.save(CV.CACHE / "directions.png")
    thumbs = [im.resize((w // 9, h // 9), Image.LANCZOS) for im in ims]
    tb = Image.new("RGB", (3 * (w // 9) + 40, h // 9 + 20), (226, 222, 214))
    for i, im in enumerate(thumbs):
        tb.paste(im, (10 + i * (w // 9 + 10), 10))
    tb.save(CV.CACHE / "directions-thumb.png")
    print(CV.CACHE / "directions.png")


if __name__ == "__main__":
    main()
