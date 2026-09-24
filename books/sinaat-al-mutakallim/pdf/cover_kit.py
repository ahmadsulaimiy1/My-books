#!/usr/bin/env python3
"""Cover toolkit (surfaces, relief, foil) and the study of direction C, «Royal Editorial».

The production cover is direction A in cover.py; this module keeps the shared machinery and
the editorial direction that was studied and set aside (see cover_dirs.py).

Original notes on direction C:

Concept «هندسة البيان» (Bible, Part Six, ch. 25 §10): the units of measure of Arabic
letter geometry read as a ladder of speech:
    النقطة (the rhombic dot)  -> الصوت    the smallest unit of speech
    الألف  (a measured stroke) -> الكلمة   the first upright construction
    السطر  (the baseline)      -> الجملة   speech when it is ordered
    الدائرة (the governing circle, its diameter the alif) -> البيان  speech when complete

Layers: (1) a deep sapphire soft-touch field and (2) the blind-debossed construction are one
300 dpi raster made here with numpy (height map -> lit relief); (3) the title, (4) the gold foil
(nuqta, baseline, title) and (5) pearl and crimson accents are vector on top; (6) micro
annotations reward close inspection. Nothing factual is invented: no publisher, ISBN, praise
or credentials appear anywhere on the wrap.

    python3 cover.py            write the print wrap PDF (front + spine + back, 3 mm bleed)
    python3 cover.py --proof    also write PNG proofs of the front, the wrap and a thumbnail
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
CACHE = HERE / ".cache" / "cover"

TITLE_1 = "صناعة"
TITLE_2 = "المتكلّم العربي"
SUBTITLE = "من سلامة اللسان إلى حسن البيان"
AUTHOR = "أحمد بن إبراهيم السليمي"
DUA = "غفر الله له ولوالديه ولجميع المسلمين"

W, H = 200.0, 260.0          # trim, mm
BLEED = 3.0

# sapphire field and metals (Bible, Part Six, ch. 22)
FIELD_TOP = (12, 40, 104)     # deep jewel sapphire
FIELD_BOT = (6, 24, 66)       # midnight sapphire toward the foot
PEARL = "#F4EFE3"

# construction of the front, in front-panel millimetres (origin: top-left of the trim)
GEO = dict(
    base_y=174.0,             # السطر: the gold baseline, runs across the whole wrap
    ring_cx=84.0, ring_r=66.0,  # الدائرة: stands on the baseline, diameter = alif
    alif_x=184.0,             # الألف: at the start side (right), measured in seven dots
    dots=7,
)
MISTARA = 0.0                 # pitch of the blind ruling (0 = none)
TITLE_RIGHT = 25.0            # the title block's start edge, measured from the right trim


def mm(v, dpi):
    return v * dpi / 25.4


# --------------------------------------------------------------------------- relief raster

def construction_front(x0=0.0):
    """Primitives of the blind construction for a front panel whose trim starts at x0 (mm)."""
    g = GEO
    by, r, cx, ax = g["base_y"], g["ring_r"], x0 + g["ring_cx"], x0 + g["alif_x"]
    cy = by - r
    top = by - 2 * r
    step = (2 * r) / g["dots"]
    prims = [("ring", cx, cy, r, 0.9, 1.0)]
    prims.append(("line", ax, top + step * 0.5, ax, by, 0.55, 0.9))          # the alif stroke
    for k in range(1, g["dots"]):                                              # its measure
        y = top + step * (k + 0.5)
        prims.append(("rhomb", ax, y, 2.0, 0.5, 0.9))
    # measure ticks on the baseline under the ring: seven dots of the alif laid flat
    for k in range(g["dots"] + 1):
        x = cx - r + k * step
        prims.append(("line", x, by + 1.6, x, by + 4.2, 0.35, 0.7))
    if MISTARA:
        y = by - MISTARA
        while y > 30:
            prims.append(("line", x0 + 18.0, y, x0 + 168.0, y, 0.22, 0.28))
            y -= MISTARA
    return prims


def draw_relief(size_px, prims, dpi, ss=2):
    w, h = size_px
    img = Image.new("L", (w * ss, h * ss), 0)
    d = ImageDraw.Draw(img)
    k = dpi / 25.4 * ss
    for p in prims:
        kind = p[0]
        if kind == "ring":
            _, cx, cy, r, sw, depth = p
            v = int(255 * depth)
            d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], outline=v, width=max(1, int(sw * k)))
        elif kind == "line":
            _, x1, y1, x2, y2, sw, depth = p
            d.line([(x1 * k, y1 * k), (x2 * k, y2 * k)], fill=int(255 * depth), width=max(1, int(sw * k)))
        elif kind == "rhomb":
            _, x, y, s, sw, depth = p
            pts = [(x * k, (y - s) * k), ((x + s) * k, y * k), (x * k, (y + s) * k), ((x - s) * k, y * k), (x * k, (y - s) * k)]
            d.line(pts, fill=int(255 * depth), width=max(1, int(sw * k)), joint="curve")
        elif kind == "rhombfill":
            _, x, y, s, depth = p
            pts = [(x * k, (y - s) * k), ((x + s) * k, y * k), (x * k, (y + s) * k), ((x - s) * k, y * k)]
            d.polygon(pts, fill=int(255 * depth))
    img = img.resize((w, h), Image.LANCZOS)
    return np.asarray(img, dtype=np.float32) / 255.0


def field(size_px, dpi, seed=7, relief=None, deboss=True, light=(-0.55, -0.62)):
    """Sapphire soft-touch field with the relief lit from the upper left."""
    w, h = size_px
    rng = np.random.default_rng(seed)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    xx = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    top = np.array(FIELD_TOP, np.float32) / 255
    bot = np.array(FIELD_BOT, np.float32) / 255
    t = np.clip(yy * 1.05, 0, 1) ** 1.2
    base = top[None, None, :] * (1 - t[..., None]) + bot[None, None, :] * t[..., None]
    # soft studio light: a broad, barely visible pool from the upper right (start side)
    pool = np.exp(-(((xx - 0.78) / 0.75) ** 2 + ((yy - 0.18) / 0.6) ** 2))
    base = base * (0.93 + 0.12 * pool[..., None])
    # soft-touch lamination: fine grain + low-frequency mottling
    grain = rng.normal(0, 1, (h, w)).astype(np.float32)
    grain = np.asarray(Image.fromarray(((grain * 18) + 128).clip(0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.7)), np.float32) / 255 - 0.5
    mott = rng.normal(0, 1, (max(4, h // 90), max(4, w // 90))).astype(np.float32)
    mott = np.asarray(Image.fromarray(((mott * 30) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC).filter(
        ImageFilter.GaussianBlur(dpi / 10)), np.float32) / 255 - 0.5
    base = base * (1 + 0.030 * grain[..., None] + 0.018 * mott[..., None])
    if relief is not None:
        hmap = np.asarray(Image.fromarray((relief * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(dpi / 300 * 1.1)), np.float32) / 255
        z = -hmap if deboss else hmap
        depth = dpi / 300 * 3.2
        gy, gx = np.gradient(z * depth)
        lx, ly = light
        lz = 0.55
        n = np.sqrt(gx * gx + gy * gy + 1)
        shade = ((-gx * lx - gy * ly + lz) / n) / math.sqrt(lx * lx + ly * ly + lz * lz) - lz / math.sqrt(lx * lx + ly * ly + lz * lz)
        base = base * (1 + 0.85 * shade[..., None]) - 0.035 * hmap[..., None]
    return np.clip(base, 0, 1)


def save_jpeg(arr, path, dpi):
    Image.fromarray((arr * 255 + 0.5).astype(np.uint8), "RGB").save(path, quality=93, dpi=(dpi, dpi), subsampling=0)
    return path


def knockout(rel, boxes, dpi, pad=2.2):
    """Break the construction where type stands in front of it, like a dimension line
    interrupted by its label."""
    if not boxes:
        return rel
    m = np.ones_like(rel)
    k = dpi / 25.4
    for x1, y1, x2, y2 in boxes:
        a, b = max(0, int((x1 - pad) * k)), max(0, int((y1 - pad) * k))
        c, d = int((x2 + pad) * k), int((y2 + pad) * k)
        m[b:d, a:c] = 0
    return rel * m


def front_texture(dpi=300, bleed=0.0, boxes=(), tag=""):
    """The front panel on its own (the book's first page): trim size, or trim + bleed."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"front-{dpi}-{int(bleed * 10)}{tag}.jpg"
    wmm, hmm = W + 2 * bleed, H + 2 * bleed
    size = (round(mm(wmm, dpi)), round(mm(hmm, dpi)))
    prims = [shift(p, bleed, bleed) for p in construction_front()]
    rel = knockout(draw_relief(size, prims, dpi), boxes, dpi)
    return save_jpeg(field(size, dpi, relief=rel), path, dpi)


def shift(p, dx, dy):
    kind = p[0]
    if kind == "ring":
        return (kind, p[1] + dx, p[2] + dy, *p[3:])
    if kind == "line":
        return (kind, p[1] + dx, p[2] + dy, p[3] + dx, p[4] + dy, *p[5:])
    return (kind, p[1] + dx, p[2] + dy, *p[3:])


# --------------------------------------------------------------------------- vector layers

# champagne foil under a soft studio light: mostly bright, with narrow cooler reflections
GOLD_STOPS = [(0, "#A7884B"), (0.14, "#D8BF88"), (0.28, "#F3E6C0"), (0.40, "#D2B67D"), (0.52, "#9E7F44"),
              (0.63, "#C9AC6E"), (0.76, "#EEDDB0"), (0.88, "#F7EDCF"), (1, "#B79859")]
GOLD_CSS = "linear-gradient(118deg, " + ", ".join(f"{c} {o * 100:.0f}%" for o, c in GOLD_STOPS) + ")"


def gold_defs(gid="foil", angle=118):
    rad = math.radians(angle)
    x2, y2 = 0.5 + 0.5 * math.cos(rad), 0.5 + 0.5 * math.sin(rad)
    stops = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in GOLD_STOPS)
    return (f'<linearGradient id="{gid}" x1="{1 - x2:.3f}" y1="{1 - y2:.3f}" x2="{x2:.3f}" y2="{y2:.3f}">{stops}</linearGradient>')


def rhomb_path(x, y, s):
    return f"M{x:.2f} {y - s:.2f} L{x + s:.2f} {y:.2f} L{x:.2f} {y + s:.2f} L{x - s:.2f} {y:.2f} Z"


def foil_rhomb(x, y, s, gid="foil"):
    """A hot-foil nuqta: stamped shadow, foil face, lit upper edges."""
    return (f'<path d="{rhomb_path(x + 0.26, y + 0.34, s)}" fill="#020A20" fill-opacity="0.55"/>'
            f'<path d="{rhomb_path(x, y, s)}" fill="url(#{gid})"/>'
            f'<path d="M{x - s:.2f} {y:.2f} L{x:.2f} {y - s:.2f} L{x + s:.2f} {y:.2f}" fill="none" stroke="#FFF6DC" stroke-width="0.2" stroke-opacity="0.75"/>')


def crimson_rhomb(x, y, s):
    return (f'<path d="{rhomb_path(x + 0.2, y + 0.26, s)}" fill="#020A20" fill-opacity="0.5"/>'
            f'<path d="{rhomb_path(x, y, s)}" fill="#A8172E"/>'
            f'<path d="M{x - s:.2f} {y:.2f} L{x:.2f} {y - s:.2f} L{x + s:.2f} {y:.2f}" fill="none" stroke="#E0707E" stroke-width="0.16" stroke-opacity="0.8"/>')


def baseline_svg(x_from, x_to, y, gid="foil"):
    return (f'<rect x="{x_from:.2f}" y="{y + 0.2:.2f}" width="{x_to - x_from:.2f}" height="0.46" fill="#020A20" fill-opacity="0.5"/>'
            f'<rect x="{x_from:.2f}" y="{y - 0.26:.2f}" width="{x_to - x_from:.2f}" height="0.52" fill="url(#{gid})"/>')


TITLE_SIZES = (16.9, 24.7)     # mm: 48 pt and 70 pt
TITLE_GAP = 4.6                # mm between the two title lines (baseline to top of line two)


def title_svg(x_right, base2, measure=False, gid="foil"):
    """The title as foil: stamped shadow, lit rim, foil face; two lines, the second on the سطر."""
    s1, s2 = TITLE_SIZES
    base1 = base2 - s2 * 0.98 - TITLE_GAP
    out = []
    for i, (txt, size, base) in enumerate(((TITLE_1, s1, base1), (TITLE_2, s2, base2)), start=1):
        common = (f'x="{x_right:.2f}" y="{base:.2f}" font-family="Reem Kufi" font-weight="700" font-size="{size}" '
                  f'direction="rtl" text-anchor="start" word-spacing="-0.6"')
        out.append(f'<text {common} dx="0.14" dy="0.2" fill="#020A20" fill-opacity="0.6">{txt}</text>')
        out.append(f'<text {common} dx="-0.05" dy="-0.09" fill="#FFF3D6" fill-opacity="0.35">{txt}</text>')
        dm = f' data-measure="t{i}"' if measure else ""
        out.append(f'<text {common} fill="url(#{gid})"{dm}>{txt}</text>')
    return "".join(out)


def front_gold(x0=0.0, y0=0.0):
    g = GEO
    by, r, ax = g["base_y"] + y0, g["ring_r"], x0 + g["alif_x"]
    top = by - 2 * r
    step = (2 * r) / g["dots"]
    return (foil_rhomb(ax, top + step * 0.5, 3.0)       # the nuqta: the sound
            + crimson_rhomb(ax, by, 1.9))                # where the alif meets the line: the speaker


# --------------------------------------------------------------------------- pages

CSS = """
@page { size: %(w)smm %(h)smm; margin: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; }
.cvr { position: relative; width: %(w)smm; height: %(h)smm; overflow: hidden; background: #0A2156; color: #F4EFE3; }
.cvr > img.fld { position: absolute; left: 0; top: 0; width: %(w)smm; height: %(h)smm; }
.cvr > svg.gold { position: absolute; left: 0; top: 0; width: %(w)smm; height: %(h)smm; }
"""

FRONT_CSS = """
.fr { position: absolute; width: 200mm; height: 260mm; }
.fr .micro { position: absolute; top: 15mm; right: %(tr)smm; left: 18mm; margin: 0; display: flex; justify-content: space-between; align-items: baseline;
  font-family: "IBM Plex Sans"; font-weight: 500; font-size: 5.4pt; letter-spacing: .34em; color: #7F90BC; direction: ltr; }
.fr .micro .ar { font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 6.6pt; letter-spacing: 0; color: #BFA66B; direction: rtl; }
.fr .sub { position: absolute; right: %(tr)smm; top: %(st)smm; margin: 0; font-family: "Amiri"; font-size: 17.5pt; line-height: 1.3; color: #F4EFE3; white-space: nowrap; }
.fr .auth { position: absolute; right: %(tr)smm; top: 213mm; margin: 0; text-align: right; }
.fr .auth .by { display: flex; align-items: center; gap: 2.4mm; font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 7.4pt; color: #C9AE6B; margin: 0 0 1.4mm; }
.fr .auth .by::after { content: ""; width: 14mm; height: .5pt; background: #B8995A; }
.fr .auth .n { display: block; font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 14.5pt; line-height: 1.45; color: #F4EFE3;
  text-shadow: 0 .35pt 0 rgba(2, 10, 32, .6); }
.fr .dua { position: absolute; right: %(tr)smm; bottom: 15mm; margin: 0; font-family: "Amiri"; font-size: 8.6pt; line-height: 1.4; color: #8E9DC6; }
.fr .ann { position: absolute; margin: 0; font-family: "Noto Kufi Arabic"; font-weight: 500; font-size: 5pt; line-height: 1; color: #5C72AC; white-space: nowrap; }
"""


def front_block(x0=0.0, y0=0.0, measure=False):
    g = GEO
    by, r, cx, ax = g["base_y"], g["ring_r"], g["ring_cx"], g["alif_x"]
    top = by - 2 * r
    step = (2 * r) / g["dots"]
    ann = [  # annotations, like an architect's drawing: the ladder of speech
        ("النقطة: الصوت", ax - 5.6, top + step * 0.5 - 1.1, "r"),
        ("الألف: الكلمة", ax - 3.4, top + step * 2.5 - 1.1, "r"),
        ("الدائرة: البيان", cx - 13, top - 4.6, "l"),
        ("السطر: الجملة", 18.0, by + 5.4, "l"),
    ]
    anns = "".join(f'<p class="ann" style="top:{y:.2f}mm;{"right" if s == "r" else "left"}:{(200 - x) if s == "r" else x:.2f}mm">{txt}</p>'
                   for txt, x, y, s in ann)
    dm = (lambda k: f' data-measure="{k}"') if measure else (lambda k: "")
    return f"""<div class="fr" style="left:{x0}mm; top:{y0}mm">
<p class="micro"><span>ṢINĀʿAT AL-MUTAKALLIM AL-ʿARABĪ</span><span class="ar">الطبعة الأولى</span></p>
{anns}
<p class="sub"{dm("sub")}>{SUBTITLE}</p>
<div class="auth"><p class="by">تأليف</p><span class="n"{dm("auth")}>{AUTHOR}</span></div>
<p class="dua">{DUA}</p>
</div>"""


def front_css():
    by = GEO["base_y"]
    return FRONT_CSS % dict(tr=TITLE_RIGHT, st=by + 7.0)


def front_page_html(font_css, tex=None, bleed=0.0, measure=False):
    wmm, hmm = W + 2 * bleed, H + 2 * bleed
    svg = (f'<defs>{gold_defs()}</defs>' + front_gold(bleed, bleed)
           + baseline_svg(0, wmm, GEO["base_y"] + bleed)
           + title_svg(bleed + W - TITLE_RIGHT, bleed + GEO["base_y"] - 9.4, measure))
    img = f'<img class="fld" src="{tex.as_uri()}" alt="">' if tex else ""
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{TITLE_1} {TITLE_2}</title>
<style>{font_css}</style><style>{CSS % dict(w=wmm, h=hmm)}{front_css()}</style></head><body>
<section class="cvr">{img}
<svg class="gold" viewBox="0 0 {wmm} {hmm}" xmlns="http://www.w3.org/2000/svg">{svg}</svg>
{front_block(bleed, bleed, measure)}
</section></body></html>"""


def measure(html, wmm, hmm):
    import json
    import os
    import subprocess
    CACHE.mkdir(parents=True, exist_ok=True)
    src = CACHE / "measure.html"
    src.write_text(html, encoding="utf-8")
    env = dict(os.environ)
    gnm = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    env["NODE_PATH"] = os.pathsep.join(filter(None, [env.get("NODE_PATH", ""), gnm]))
    out = subprocess.run(["node", str(HERE / "measure.js"), str(src), str(wmm), str(hmm)],
                         check=True, capture_output=True, text=True, env=env).stdout
    return json.loads(out)


def build_front(font_css, dpi=300, bleed=0.0):
    """Measure the type, cut the construction where the type stands, then compose."""
    wmm, hmm = W + 2 * bleed, H + 2 * bleed
    boxes = measure(front_page_html(font_css, None, bleed, measure=True), wmm, hmm)
    knock = [boxes[k] for k in ("t1", "t2", "sub")]
    tex = front_texture(dpi, bleed, knock)
    return front_page_html(font_css, tex, bleed), boxes


# --------------------------------------------------------------------------- back and spine

BACK = dict(motif_cx=150.0, motif_r=20.0, motif_base=64.0, alif_x=184.0)

BACK_HEAD = "أن تعرف العربية شيء، وأن تتكلّمها كما ينبغي شيء آخر."
BACK_TEXT = ("هذا الكتاب منهج في صناعة الكلام بالعربية الفصيحة. لا يقف عند صحة الجملة، بل يعلّمك أن تقولها "
             "للشخص المناسب، في الوقت المناسب، بالأسلوب والنبرة والقدر والأدب المناسبة؛ فينقلك من معرفة القاعدة "
             "إلى امتلاك الملكة الشفهية، حتى ترتجل الكلام الناجح في موقف لم تستعد له.")
LADDER = [
    ("rh", "الصوت", ["سلامة النطق", "الطلاقة"]),
    ("alif", "الكلمة", ["اختيار الألفاظ", "فهم المقام"]),
    ("line", "الجملة", ["الحوار", "السؤال والجواب", "الخطاب الأكاديمي", "الخطاب المهني", "الخطاب الإعلامي", "التخاطب الاجتماعي"]),
    ("ring", "البيان", ["الإقناع", "حسن البيان", "الارتجال"]),
]
METHOD = "في كل مهارة ثلاثة نماذج للمعنى الواحد: غير الناجح، والمقبول، والناجح؛ ثم تحليل، فتدريب، فمحاكاة، فتقويم."
EDITION = "الطبعة الأولى، ١٤٤٨هـ / ٢٠٢٦م"


def construction_back(x0=0.0, y0=0.0):
    """The signature at small scale: ring, alif and dot standing on a short line."""
    b = BACK
    cx, r, by, ax = x0 + b["motif_cx"], b["motif_r"], y0 + b["motif_base"], x0 + b["alif_x"]
    top = by - 2 * r
    step = 2 * r / GEO["dots"]
    prims = [("ring", cx, by - r, r, 0.7, 1.0), ("line", ax, top + step * 0.5, ax, by, 0.45, 0.9),
             ("line", cx - r - 6, by, ax, by, 0.4, 0.8)]
    for k in range(1, GEO["dots"]):
        prims.append(("rhomb", ax, top + step * (k + 0.5), 1.2, 0.4, 0.9))
    return prims


def back_gold(x0=0.0, y0=0.0):
    b = BACK
    top = y0 + b["motif_base"] - 2 * b["motif_r"]
    step = 2 * b["motif_r"] / GEO["dots"]
    return foil_rhomb(x0 + b["alif_x"], top + step * 0.5, 1.9)


BACK_CSS = """
.bk { position: absolute; width: 200mm; height: 260mm; }
.bk .ttl { position: absolute; top: 15mm; right: 20mm; margin: 0; font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 6.6pt; color: #BFA66B; }
.bk .head { position: absolute; top: 76mm; right: 20mm; width: 150mm; margin: 0; font-family: "Reem Kufi"; font-weight: 600; font-size: 19pt;
  line-height: 1.45; color: #F4EFE3; text-align: right; text-wrap: balance; }
.bk .txt { position: absolute; top: 101mm; right: 20mm; width: 146mm; margin: 0; font-family: "Amiri"; font-size: 12.2pt; line-height: 1.95;
  color: #CBD4EA; text-align: justify; }
.bk .lad { position: absolute; top: 133mm; right: 20mm; width: 162mm; margin: 0; padding: 0; list-style: none; }
.bk .lad li { display: grid; grid-template-columns: 7mm 15mm minmax(0, 1fr); align-items: baseline; gap: 1.6mm; padding: 1.35mm 0;
  border-bottom: .4pt solid #1E3A7A; }
.bk .lad li:last-child { border-bottom: 0; }
.bk .lad .g { align-self: center; justify-self: center; }
.bk .lad .k { font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 8pt; color: #C9AE6B; }
.bk .lad .v { font-family: "Amiri"; font-size: 11.2pt; line-height: 1.5; color: #F4EFE3; }
.bk .lad .v i { display: inline-block; width: 1.3mm; height: 1.3mm; margin: 0 2.1mm; background: #B8995A; transform: rotate(45deg); vertical-align: .25em; }
.bk .meth { position: absolute; top: 180.5mm; right: 20mm; width: 158mm; margin: 0; display: flex; align-items: baseline; gap: 3mm;
  font-family: "Amiri"; font-size: 10.4pt; line-height: 1.6; color: #A9B6DA; }
.bk .meth .tiers { flex: none; display: inline-flex; gap: 2.4mm; direction: rtl; }
.bk .meth .tiers b { display: inline-flex; gap: .7mm; }
.bk .meth .tiers b i { width: 1.35mm; height: 1.35mm; transform: rotate(45deg); border: .5pt solid currentColor; }
.bk .meth .tiers b i.on { background: currentColor; }
.bk .foot { position: absolute; bottom: 15mm; right: 20mm; margin: 0; text-align: right; }
.bk .foot .t { display: block; font-family: "Reem Kufi"; font-weight: 700; font-size: 11pt; line-height: 1.3; color: #D9C08A; }
.bk .foot .a { display: block; font-family: "Noto Kufi Arabic"; font-weight: 500; font-size: 7.6pt; line-height: 1.6; color: #E9E3D5; }
.bk .foot .e { display: block; font-family: "IBM Plex Sans Arabic"; font-size: 6.6pt; color: #7F90BC; margin-top: .6mm; }
"""


def ladder_glyph(kind):
    if kind == "rh":
        return '<svg class="g" width="2.6mm" height="2.6mm" viewBox="0 0 10 10"><path d="M5 0 L10 5 L5 10 L0 5 Z" fill="#C9AE6B"/></svg>'
    if kind == "alif":
        return '<svg class="g" width="2.6mm" height="4mm" viewBox="0 0 10 16"><rect x="4.1" y="0" width="1.8" height="16" fill="#C9AE6B"/></svg>'
    if kind == "line":
        return '<svg class="g" width="5mm" height="2mm" viewBox="0 0 20 8"><rect x="0" y="3.2" width="20" height="1.6" fill="#C9AE6B"/></svg>'
    return '<svg class="g" width="3.6mm" height="3.6mm" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5.1" fill="none" stroke="#C9AE6B" stroke-width="1.3"/></svg>'


def tiers_html():
    rows = []
    for n, col in ((1, "#C9546A"), (2, "#A9B6DA"), (3, "#E9E3D5")):
        dots = "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
        rows.append(f'<b style="color:{col}">{dots}</b>')
    return f'<span class="tiers">{"".join(rows)}</span>'


def back_block(x0=0.0, y0=0.0):
    rows = "".join(f'<li>{ladder_glyph(g)}<span class="k">{k}</span><span class="v">{"<i></i>".join(v)}</span></li>'
                   for g, k, v in LADDER)
    return f"""<div class="bk" style="left:{x0}mm; top:{y0}mm">
<p class="ttl">صناعة المتكلّم العربي</p>
<p class="head">{BACK_HEAD}</p>
<p class="txt">{BACK_TEXT}</p>
<ul class="lad">{rows}</ul>
<p class="meth">{tiers_html()}<span>{METHOD}</span></p>
<p class="foot"><span class="t">{TITLE_1} {TITLE_2}</span><span class="a">{AUTHOR}</span><span class="e">{EDITION}</span></p>
</div>"""


def spine_svg(sx, sw, y0=0.0):
    """Spine elements (gold and pearl), reading top to bottom with the letter tops toward the front."""
    cx = sx + sw / 2
    tsize = min(15.0, sw * 0.36)
    asize = min(6.2, sw * 0.16)
    by = y0 + GEO["base_y"]
    t_mid = y0 + 26 + (by - 8 - (y0 + 26)) / 2
    a_mid = by + (y0 + H - 22 - by) / 2
    tx = cx + tsize * 0.30
    ax = cx + asize * 0.36
    title = TITLE_1 + " " + TITLE_2
    common = f'font-family="Reem Kufi" font-weight="700" font-size="{tsize:.2f}" direction="rtl" text-anchor="middle"'
    out = [foil_rhomb(cx, y0 + 16.0, min(2.4, sw * 0.07)),
           f'<text transform="translate({tx + 0.16:.2f},{t_mid + 0.12:.2f}) rotate(-90)" {common} fill="#020A20" fill-opacity="0.6">{title}</text>',
           f'<text transform="translate({tx:.2f},{t_mid:.2f}) rotate(-90)" {common} fill="url(#foil)">{title}</text>',
           f'<text transform="translate({ax:.2f},{a_mid:.2f}) rotate(-90)" font-family="Noto Kufi Arabic" font-weight="600" '
           f'font-size="{asize:.2f}" direction="rtl" text-anchor="middle" fill="#F4EFE3">{AUTHOR}</text>',
           crimson_rhomb(cx, y0 + H - 13.0, min(1.7, sw * 0.05))]
    return "".join(out)


def spine_width(pages, caliper=0.1, cover=1.0):
    """Perfect-bound spine: half the page count in leaves x paper caliper (mm), plus the cover."""
    return round(pages / 2 * caliper + cover, 1)


def back_texture(dpi=300, bleed=0.0, tag=""):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"back-{dpi}-{int(bleed * 10)}{tag}.jpg"
    size = (round(mm(W + 2 * bleed, dpi)), round(mm(H + 2 * bleed, dpi)))
    rel = draw_relief(size, construction_back(bleed, bleed), dpi)
    return save_jpeg(field(size, dpi, relief=rel, seed=11), path, dpi)


def back_page_html(font_css, tex, bleed=0.0):
    wmm, hmm = W + 2 * bleed, H + 2 * bleed
    svg = f'<defs>{gold_defs()}</defs>' + back_gold(bleed, bleed) + baseline_svg(0, wmm, GEO["base_y"] + bleed)
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{TITLE_1} {TITLE_2}</title>
<style>{font_css}</style><style>{CSS % dict(w=wmm, h=hmm)}{BACK_CSS}</style></head><body>
<section class="cvr"><img class="fld" src="{tex.as_uri()}" alt="">
<svg class="gold" viewBox="0 0 {wmm} {hmm}" xmlns="http://www.w3.org/2000/svg">{svg}</svg>
{back_block(bleed, bleed)}
</section></body></html>"""


def wrap_html(font_css, spine, dpi=300, bleed=BLEED):
    """Front | spine | back, left to right as the flat wrap lies (an Arabic book opens from the right)."""
    wmm, hmm = 2 * W + spine + 2 * bleed, H + 2 * bleed
    fx, sx, bx = bleed, bleed + W, bleed + W + spine
    boxes = measure(front_page_html(font_css, None, 0.0, measure=True), W, H)
    knock = [[b[0] + fx, b[1] + bleed, b[2] + fx, b[3] + bleed] for b in (boxes["t1"], boxes["t2"], boxes["sub"])]
    size = (round(mm(wmm, dpi)), round(mm(hmm, dpi)))
    prims = [shift(p, fx, bleed) for p in construction_front()] + construction_back(bx, bleed)
    rel = knockout(draw_relief(size, prims, dpi), knock, dpi)
    CACHE.mkdir(parents=True, exist_ok=True)
    tex = save_jpeg(field(size, dpi, relief=rel, seed=5), CACHE / f"wrap-{dpi}-{spine}.jpg", dpi)
    svg = (f'<defs>{gold_defs()}</defs>' + front_gold(fx, bleed) + back_gold(bx, bleed)
           + baseline_svg(0, wmm, GEO["base_y"] + bleed)
           + title_svg(fx + W - TITLE_RIGHT, bleed + GEO["base_y"] - 9.4)
           + spine_svg(sx, spine, bleed))
    guides = (f'<div class="fold" style="left:{sx}mm"></div><div class="fold" style="left:{bx}mm"></div>')
    return f"""<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{TITLE_1} {TITLE_2}: الغلاف الكامل</title>
<style>{font_css}</style><style>{CSS % dict(w=wmm, h=hmm)}{front_css()}{BACK_CSS}
.fold {{ position: absolute; top: 0; width: 0; height: 2.2mm; border-left: .25pt solid #8C9BC4; }}</style></head><body>
<section class="cvr"><img class="fld" src="{tex.as_uri()}" alt="">
<svg class="gold" viewBox="0 0 {wmm} {hmm}" xmlns="http://www.w3.org/2000/svg">{svg}</svg>
{front_block(fx, bleed)}{back_block(bx, bleed)}{guides}
</section></body></html>"""


def main():
    sys.path.insert(0, str(HERE))
    import build as B
    import book_build as K
    font_css = B.static_instances(B.ensure_fonts(K.BOOK_FONT_CSS, "bookfonts"))
    dpi = 200 if "--draft" in sys.argv else 300
    html, boxes = build_front(font_css, dpi=dpi)
    print(B.render(html, "cover-front"))
    print(B.render(back_page_html(font_css, back_texture(dpi)), "cover-back"))
    pages = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--pages=")), 1200)
    spine = spine_width(pages)
    print("spine", spine, "mm for", pages, "pages")
    print(B.render(wrap_html(font_css, spine, dpi), "cover-wrap"))


if __name__ == "__main__":
    main()
