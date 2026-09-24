#!/usr/bin/env python3
"""The cover of «صناعة المتكلّم العربي»: direction A, «Arabic Architectural Luxury».

Chosen after a study of three directions (cover_dirs.py; Bible, Part Six, ch. 25 §10):
A architectural luxury, B manuscript luxury, C royal editorial. A carries the register of the
Arabic commissioned book (calligraphic title, gold on deep sapphire, architectural framing, a
hardcover spine built in panels) with the book's own signature: the units of Arabic letter
geometry read as a ladder of speech, النقطة (sound), الألف (word), السطر (sentence), الدائرة
(البيان). They appear as the measure bands, the nuqta nodes at every crossing, the construction
extensions of the rules, the spine ornament, and the ladder of domains on the back.

Layers: (1) a deep sapphire book cloth and (2) the blind-debossed panel recess and rhombic
micro-lattice are one raster made with numpy (height map lit from the upper left); (3) the
title is engineered lettering (HarfBuzz-shaped Amiri outlines, word spacing set by hand);
(4) gold foil with a stamped shadow and a lit rim; (5) pearl type and one ruby; (6) a lattice
and measure ticks that only show up close. Nothing factual is invented: no publisher, ISBN,
praise or credentials appear anywhere on the wrap.

    python3 cover.py [--pages=N] [--draft]   write the print wrap and the front/back proofs
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cover_kit as K  # noqa: E402
import lettering as L  # noqa: E402

TITLE_1 = "صناعة"
TITLE_2 = "المتكلّم العربي"
SUBTITLE = "من سلامة اللسان إلى حسن البيان"
AUTHOR = "أحمد بن إبراهيم السليمي"
DUA = "غفر الله له ولوالديه ولجميع المسلمين"
EDITION = "الطبعة الأولى، ١٤٤٨هـ / ٢٠٢٦م"

W, H = 200.0, 260.0
BLEED = 3.0
CLOTH_TOP, CLOTH_BOT = (13, 38, 98), (7, 23, 64)
BAND_TOP, BAND_BOT = 22.0, 231.0          # the two gold measures that run across the whole wrap
PANEL = (22.0, 44.0, 178.0, 146.0)        # the front title panel
BACK_PANEL = (22.0, 44.0, 178.0, 163.0)
PEARL = "#F4EFE3"
GOLD_TEXT = "#C9AE6B"
CACHE = K.CACHE


# --------------------------------------------------------------------------- surfaces

def cloth(size, dpi, relief=None, seed=3, weave=0.035):
    """Deep sapphire book cloth: jewel field, fine woven grain, relief lit from the upper left."""
    w, h = size
    arr = K.field(size, dpi, seed=seed, relief=relief, deboss=True)
    yy = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    tgt = np.array(CLOTH_TOP, np.float32) / 255 * (1 - yy) + np.array(CLOTH_BOT, np.float32) / 255 * yy
    ref = np.array(K.FIELD_TOP, np.float32) / 255 * (1 - yy) + np.array(K.FIELD_BOT, np.float32) / 255 * yy
    arr = np.clip(arr / np.maximum(ref, 1e-3) * tgt, 0, 1)
    if weave:
        rng = np.random.default_rng(seed + 1)
        pitch = dpi / 25.4 * 0.42
        xs = np.arange(w, dtype=np.float32)[None, :]
        ys = np.arange(h, dtype=np.float32)[:, None]
        warp = np.sin(xs / pitch * 2 * math.pi + rng.normal(0, .35, (1, w)).astype(np.float32).cumsum(axis=1) * 0.02)
        weft = np.sin(ys / pitch * 2 * math.pi + rng.normal(0, .35, (h, 1)).astype(np.float32).cumsum(axis=0) * 0.02)
        slub = rng.normal(0, 1, (h // 6 + 1, w // 40 + 1)).astype(np.float32)
        slub = np.asarray(Image.fromarray(((slub * 40) + 128).clip(0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                          np.float32) / 255 - .5
        arr = np.clip(arr * (1 + weave * (0.5 * warp * weft + 0.35 * slub)[..., None]), 0, 1)
    return arr


def lattice(x1, y1, x2, y2, pitch=6.0, sw=0.2, depth=0.22):
    """Blind rhombic micro-lattice (the Bible's الشبكة المعيّنية), clipped to a rectangle."""
    prims, h, c = [], y2 - y1, x1 - (y2 - y1)
    while c < x2:
        for (a0, b0, a1, b1) in ((c, y1, c + h, y2), (c + h, y1, c, y2)):
            # clip the diagonal to x1..x2
            if a1 != a0:
                slope = (b1 - b0) / (a1 - a0)
                lo, hi = sorted((a0, a1))
                xa, xb = max(lo, x1), min(hi, x2)
                if xb > xa:
                    prims.append(("line", xa, b0 + (xa - a0) * slope, xb, b0 + (xb - a0) * slope, sw, depth))
        c += pitch
    return prims


def recess(rel, dpi, box, level=0.45):
    """Sink a rectangle (blind deboss): add depth so any relief inside it keeps its own."""
    k = dpi / 25.4
    x1, y1, x2, y2 = box
    r = rel.copy()
    sl = (slice(int((y1 + 0.6) * k), int((y2 - 0.6) * k)), slice(int((x1 + 0.6) * k), int((x2 - 0.6) * k)))
    r[sl] = np.clip(r[sl] * 0.6 + level, 0, 1)
    return r


# --------------------------------------------------------------------------- vector gold

GOLD = "url(#foil)"


def hairline(x1, x2, y, t=0.28):
    return f'<rect x="{x1:.2f}" y="{y - t / 2:.2f}" width="{x2 - x1:.2f}" height="{t}" fill="{GOLD}"/>'


def measure_band(x1, x2, y, ticks=True, centre=True, n=14):
    """The book's measure: a hairline with nuqta nodes at the ends, ticks at alif intervals and a
    ring holding a nuqta at the centre."""
    cx = (x1 + x2) / 2
    out = [hairline(x1, x2, y), K.foil_rhomb(x1, y, 1.25), K.foil_rhomb(x2, y, 1.25)]
    if centre:
        out.append(f'<circle cx="{cx:.2f}" cy="{y:.2f}" r="2.9" fill="#0B2461" stroke="{GOLD}" stroke-width="0.3"/>')
        out.append(K.foil_rhomb(cx, y, 1.05))
    if ticks:
        for k in range(1, n):
            x = x1 + (x2 - x1) * k / n
            if abs(x - cx) > 5:
                out.append(f'<rect x="{x - 0.09:.2f}" y="{y - 1.1:.2f}" width="0.18" height="2.2" fill="{GOLD}"/>')
    return "".join(out)


def panel_frame(x1, y1, x2, y2, inset=2.2, ext=3.6, node=1.5, t=0.5):
    """Double rule whose outer lines run on past the corners, as a draughtsman's construction
    does, with a nuqta at every crossing."""
    out = [f'<rect x="{x1 - ext:.2f}" y="{y - t / 2:.2f}" width="{x2 - x1 + 2 * ext:.2f}" height="{t}" fill="{GOLD}"/>' for y in (y1, y2)]
    out += [f'<rect x="{x - t / 2:.2f}" y="{y1 - ext:.2f}" width="{t}" height="{y2 - y1 + 2 * ext:.2f}" fill="{GOLD}"/>' for x in (x1, x2)]
    out.append(f'<rect x="{x1 + inset:.2f}" y="{y1 + inset:.2f}" width="{x2 - x1 - 2 * inset:.2f}" height="{y2 - y1 - 2 * inset:.2f}" '
               f'fill="none" stroke="{GOLD}" stroke-width="0.2"/>')
    out += [K.foil_rhomb(x, y, node) for x in (x1, x2) for y in (y1, y2)]
    return "".join(out)


def jewel(x, y, s=3.2):
    """The single ruby of the identity, set in a gold rhombus."""
    return (f'<path d="{K.rhomb_path(x, y, s)}" fill="#0B2461" stroke="{GOLD}" stroke-width="0.45"/>'
            + K.crimson_rhomb(x, y, s / 2))


def signature(cx, top, height):
    """The signature at spine scale, in gold hairlines: the ring (البيان) whose diameter is the
    alif, the alif (الكلمة) measured in dots with the nuqta (الصوت) at its head, both standing on
    the line (الجملة)."""
    r = height * 0.3
    base = top + height
    ax = cx + r * 0.95
    rx = cx - r * 0.45
    out = [f'<circle cx="{rx:.2f}" cy="{base - r:.2f}" r="{r:.2f}" fill="none" stroke="{GOLD}" stroke-width="0.3"/>',
           hairline(rx - r - 3.0, ax + 3.0, base, 0.26),
           f'<rect x="{ax - 0.13:.2f}" y="{base - 2 * r:.2f}" width="0.26" height="{2 * r:.2f}" fill="{GOLD}"/>']
    for k in range(1, 4):
        out.append(f'<path d="{K.rhomb_path(ax, base - 2 * r * k / 4, 0.62)}" fill="#0B2461" stroke="{GOLD}" stroke-width="0.2"/>')
    out.append(K.foil_rhomb(ax, base - 2 * r - 1.5, 1.2))
    return "".join(out)


# --------------------------------------------------------------------------- lettering

class Lettering:
    """«صناعة» over «المتكلّم العربي»: Amiri Bold outlines, word space set by hand, centred."""

    def __init__(self, font_css, s1=23.0, s2=36.0, word_gap=0.62, line_gap=4.0, face=("Amiri", 700)):
        path = L.arabic_face(font_css, *face)
        self.l1 = L.Line(TITLE_1, path, s1)
        w1, w2 = TITLE_2.split(" ")
        self.w1 = L.Line(w1, path, s2)          # المتكلّم (read first: the right-hand word)
        self.w2 = L.Line(w2, path, s2)          # العربي
        self.gap = s2 * 0.26 * word_gap          # a calligrapher's word space, tighter than the font's
        self.line_gap = line_gap
        self.s2 = s2
        self.width2 = self.w1.width + self.gap + self.w2.width
        b1 = self.l1.bounds
        b2 = (min(self.w1.bounds[1], self.w2.bounds[1]), max(self.w1.bounds[3], self.w2.bounds[3]))
        self.h1 = b1[3] - b1[1]
        self.h2 = b2[1] - b2[0]
        self.top2, self.bot2 = b2

    def height(self):
        return self.h1 + self.line_gap + self.h2

    def svg(self, cx, top, scale=1.0, shadow=True, rim=True, fill=GOLD):
        """Title block with its highest ink at `top`, centred on cx; returns (svg, [boxes])."""
        base2 = top + (self.h1 + self.line_gap) * scale - self.top2 * scale
        base1 = top - self.l1.bounds[1] * scale
        right2 = cx + self.width2 * scale / 2
        x_w1 = right2 - self.w1.width * scale
        x_w2 = x_w1 - self.gap * scale - self.w2.width * scale
        x_l1 = cx - self.l1.width * scale / 2
        parts, boxes = [], []
        for ln, x, b in ((self.l1, x_l1, base1), (self.w1, x_w1, base2), (self.w2, x_w2, base2)):
            tr = f"translate({x:.3f} {b:.3f}) scale({scale:.4f})"
            if shadow:
                parts.append(f'<path transform="translate({0.16 * scale:.3f} {0.22 * scale:.3f}) {tr}" d="{ln.d}" fill="#020A20" fill-opacity="0.55"/>')
            if rim:
                parts.append(f'<path transform="translate({-0.06 * scale:.3f} {-0.1 * scale:.3f}) {tr}" d="{ln.d}" fill="#FFF3D6" fill-opacity="0.3"/>')
            parts.append(f'<path transform="{tr}" d="{ln.d}" fill="{fill}"/>')
            bx = ln.bounds
            boxes.append((x + bx[0] * scale, b + bx[1] * scale, x + bx[2] * scale, b + bx[3] * scale))
        return "".join(parts), boxes


def word_stack(font_css, words, max_w, max_size, face=("Amiri", 700)):
    """Words stacked one per line (the spine title), each at one common size that fits max_w."""
    path = L.arabic_face(font_css, *face)
    probe = [L.Line(w, path, 10.0) for w in words]
    size = min(max_size, max_w / max(p.width for p in probe) * 10.0)
    return [L.Line(w, path, size) for w in words], size


def stack_svg(lines, cx, top, lead, fill=GOLD, shadow=True):
    out, y = [], top
    for ln in lines:
        base = y - ln.bounds[1]
        x = cx - ln.width / 2
        if shadow:
            out.append(L.svg_path(ln, x + 0.14, base + 0.2, fill="#020A20", fill_opacity="0.55"))
        out.append(L.svg_path(ln, x, base, fill=fill))
        y = base + ln.bounds[3] + lead
    return "".join(out), y


# --------------------------------------------------------------------------- panels (front, spine, back)

TEXT_CSS = """
.cv-a { position: absolute; top: 0; height: 260mm; }
.cv-a .tx { position: absolute; margin: 0; left: 0; right: 0; text-align: center; white-space: nowrap; }
.cv-a .sub { top: 158.5mm; display: flex; align-items: center; justify-content: center; gap: 4.4mm;
  font-family: "Amiri"; font-size: 18.5pt; line-height: 1.3; color: #F4EFE3; }
.cv-a .sub i { position: relative; display: block; width: 16mm; height: .28mm; background: linear-gradient(90deg, #A7884B, #F3E6C0 55%, #B79859); }
.cv-a .sub i::after { content: ""; position: absolute; top: -.62mm; width: 1.5mm; height: 1.5mm; transform: rotate(45deg); background: #D9BE7C; }
.cv-a .sub i:first-child::after { right: -.2mm; } .cv-a .sub i:last-child::after { left: -.2mm; }
.cv-a .by { top: 190.5mm; font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 7.6pt; color: #C9AE6B; }
.cv-a .au { top: 196mm; font-family: "Amiri"; font-weight: 700; font-size: 20pt; line-height: 1.3; color: #F4EFE3;
  text-shadow: 0 .4pt 0 rgba(2, 10, 32, .6); }
.cv-a .dua { top: 236.5mm; font-family: "Amiri"; font-size: 8.8pt; color: #93A2CB; }

.cv-b .hd { top: 53mm; left: 34mm; right: 34mm; white-space: normal; font-family: "Amiri"; font-weight: 700; font-size: 19pt;
  line-height: 1.45; color: #F4EFE3; text-wrap: balance; }
.cv-b .rl { top: 71.5mm; display: flex; justify-content: center; }
.cv-b .rl i { display: block; width: 30mm; height: .28mm; background: linear-gradient(90deg, #A7884B, #F3E6C0 55%, #B79859); }
.cv-b .p { top: 78mm; left: 34mm; right: 34mm; white-space: normal; text-align: justify; text-align-last: center;
  font-family: "Amiri"; font-size: 12.2pt; line-height: 1.9; color: #CBD4EA; }
.cv-b .lad { position: absolute; top: 127mm; left: 28mm; right: 28mm; margin: 0; padding: 0; list-style: none; }
.cv-b .lad li { display: grid; grid-template-columns: 7mm 14mm minmax(0, 1fr); align-items: baseline; gap: 1.6mm; padding: 1.25mm 0;
  border-bottom: .4pt solid #1F3C7C; }
.cv-b .lad li:last-child { border-bottom: 0; }
.cv-b .lad .g { align-self: center; justify-self: center; }
.cv-b .lad .k { font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 7.8pt; color: #C9AE6B; text-align: start; }
.cv-b .lad .v { font-family: "Amiri"; font-size: 10.8pt; line-height: 1.5; color: #F4EFE3; text-align: start; }
.cv-b .lad .v i { display: inline-block; width: 1.2mm; height: 1.2mm; margin: 0 1.6mm; background: #B8995A; transform: rotate(45deg); vertical-align: .25em; }
.cv-b .me { top: 171mm; display: flex; align-items: baseline; justify-content: center; gap: 3mm; font-family: "Amiri"; font-size: 10.4pt; color: #A9B6DA; }
.cv-b .me .tiers { display: inline-flex; gap: 2.4mm; }
.cv-b .me .tiers b { display: inline-flex; gap: .7mm; }
.cv-b .me .tiers b i { width: 1.35mm; height: 1.35mm; transform: rotate(45deg); border: .5pt solid currentColor; }
.cv-b .me .tiers b i.on { background: currentColor; }
.cv-b .au { top: 184mm; font-family: "Amiri"; font-weight: 700; font-size: 13pt; color: #F4EFE3; }
.cv-b .dua { top: 191.5mm; font-family: "Amiri"; font-size: 8.6pt; color: #93A2CB; }
.cv-b .ed { top: 236.5mm; font-family: "IBM Plex Sans Arabic"; font-size: 6.8pt; color: #7F90BC; }

.cv-s .tx { white-space: nowrap; }
.cv-s .ed { font-family: "Noto Kufi Arabic"; font-weight: 600; font-size: 6.4pt; color: #C9AE6B; }
"""

BACK_HEAD = "أن تعرف العربية شيء، وأن تتكلّمها كما ينبغي شيء آخر."
BACK_TEXT = ("هذا الكتاب منهج في صناعة الكلام بالعربية الفصيحة. لا يقف عند صحة الجملة، بل يعلّمك أن تقولها للشخص "
             "المناسب، في الوقت المناسب، بالأسلوب والنبرة والقدر والأدب المناسبة؛ فينقلك من معرفة القاعدة إلى امتلاك "
             "الملكة الشفهية، حتى ترتجل الكلام الناجح في موقف لم تستعد له.")
LADDER = [
    ("rh", "الصوت", ["سلامة النطق", "الطلاقة"]),
    ("alif", "الكلمة", ["اختيار الألفاظ", "فهم المقام"]),
    ("line", "الجملة", ["الحوار", "السؤال والجواب", "الخطاب الأكاديمي والمهني والإعلامي", "التخاطب الاجتماعي"]),
    ("ring", "البيان", ["الإقناع", "حسن البيان", "الارتجال"]),
]
METHOD = "في كل مهارة ثلاثة نماذج للمعنى الواحد: غير الناجح، والمقبول، والناجح؛ ثم تحليل، فتدريب، فمحاكاة، فتقويم."


def ladder_glyph(kind):
    c = GOLD_TEXT
    if kind == "rh":
        return f'<svg class="g" width="2.6mm" height="2.6mm" viewBox="0 0 10 10"><path d="M5 0 L10 5 L5 10 L0 5 Z" fill="{c}"/></svg>'
    if kind == "alif":
        return f'<svg class="g" width="2.6mm" height="4mm" viewBox="0 0 10 16"><rect x="4.1" y="0" width="1.8" height="16" fill="{c}"/></svg>'
    if kind == "line":
        return f'<svg class="g" width="5mm" height="2mm" viewBox="0 0 20 8"><rect x="0" y="3.2" width="20" height="1.6" fill="{c}"/></svg>'
    return f'<svg class="g" width="3.6mm" height="3.6mm" viewBox="0 0 12 12"><circle cx="6" cy="6" r="5.1" fill="none" stroke="{c}" stroke-width="1.3"/></svg>'


def tiers_html():
    rows = []
    for n, col in ((1, "#C9546A"), (2, "#A9B6DA"), (3, "#E9E3D5")):
        dots = "".join('<i class="on"></i>' if k < n else "<i></i>" for k in range(3))
        rows.append(f'<b style="color:{col}">{dots}</b>')
    return f'<span class="tiers">{"".join(rows)}</span>'


class Front:
    def __init__(self, font_css):
        self.title = Lettering(font_css)

    def relief(self, x0, y0):
        px1, py1, px2, py2 = PANEL
        return lattice(x0 + px1 + 3.4, y0 + py1 + 3.4, x0 + px2 - 3.4, y0 + py2 - 3.4)

    def title_geometry(self, x0, y0):
        px1, py1, px2, py2 = PANEL
        t = self.title
        top = y0 + (py1 + py2) / 2 - t.height() / 2 - 2.6      # optical centre, a little above the middle
        return x0 + 100.0, top

    def gold(self, x0, y0, bands=True):
        px1, py1, px2, py2 = PANEL
        cx, top = self.title_geometry(x0, y0)
        title, boxes = self.title.svg(cx, top)
        self.boxes = boxes
        g = [panel_frame(x0 + px1, y0 + py1, x0 + px2, y0 + py2), jewel(x0 + 100, y0 + py1), title]
        if bands:
            g += [measure_band(x0 + 28, x0 + 172, y0 + BAND_TOP), measure_band(x0 + 28, x0 + 172, y0 + BAND_BOT, ticks=False, centre=False)]
        return "".join(g)

    def html(self, x0, y0):
        return (f'<div class="cv-a" style="left:{x0}mm; width:200mm; top:{y0}mm">'
                f'<p class="tx sub"><i></i><span>{SUBTITLE}</span><i></i></p>'
                f'<p class="tx by">تأليف</p><p class="tx au">{AUTHOR}</p><p class="tx dua">{DUA}</p></div>')


class Back:
    def relief(self, x0, y0):
        return []

    def gold(self, x0, y0, bands=True):
        px1, py1, px2, py2 = BACK_PANEL
        g = [panel_frame(x0 + px1, y0 + py1, x0 + px2, y0 + py2)]
        if bands:
            g += [measure_band(x0 + 28, x0 + 172, y0 + BAND_TOP), measure_band(x0 + 28, x0 + 172, y0 + BAND_BOT, ticks=False, centre=False)]
        return "".join(g)

    def html(self, x0, y0):
        rows = "".join(f'<li>{ladder_glyph(g)}<span class="k">{k}</span><span class="v">{"<i></i>".join(v)}</span></li>'
                       for g, k, v in LADDER)
        return (f'<div class="cv-a cv-b" style="left:{x0}mm; width:200mm; top:{y0}mm">'
                f'<p class="tx hd">{BACK_HEAD}</p><p class="tx rl"><i></i></p><p class="tx p">{BACK_TEXT}</p>'
                f'<ul class="lad">{rows}</ul>'
                f'<p class="tx me">{tiers_html()}<span>{METHOD}</span></p>'
                f'<p class="tx au">{AUTHOR}</p><p class="tx dua">{DUA}</p><p class="tx ed">{EDITION}</p></div>')


class Spine:
    """Hardcover spine in panels: head measure, title panel, author, the signature, edition, foot
    measure. The gold rules sit at the same heights on every copy, so a row of copies on a shelf
    reads as one architecture."""

    def __init__(self, font_css, width):
        self.w = width
        self.font_css = font_css
        inner = width - 14.0
        self.title, self.tsize = word_stack(font_css, [TITLE_1, "المتكلّم", "العربي"], inner, 13.5)
        au_words = ["أحمد بن إبراهيم", "السليمي"] if width < 70 else [AUTHOR]
        self.author, self.asize = word_stack(font_css, au_words, width - 12.0, 6.4)

    def relief(self, x0, y0):
        return []

    def gold(self, x0, y0, bands=True):
        w, cx = self.w, x0 + self.w / 2
        x1, x2 = x0 + 5.0, x0 + w - 5.0
        py1, py2 = y0 + 36.0, y0 + 124.0
        out = [panel_frame(x1, py1, x2, py2, inset=1.6, ext=0.0, node=1.1, t=0.4), jewel(cx, py1, 2.3)]
        t_h = sum(l.bounds[3] - l.bounds[1] for l in self.title) + 3.6 * (len(self.title) - 1)
        svg, _ = stack_svg(self.title, cx, (py1 + py2) / 2 - t_h / 2, 3.6)
        out.append(svg)
        a_h = sum(l.bounds[3] - l.bounds[1] for l in self.author) + 1.6 * (len(self.author) - 1)
        asvg, _ = stack_svg(self.author, cx, y0 + 140.0 - a_h / 2, 1.6, fill=PEARL, shadow=False)
        out.append(asvg)
        out.append(hairline(x1 + 4, x2 - 4, y0 + 152.0, 0.25))
        out.append(signature(cx, y0 + 166.0, min(34.0, w * 0.5)))
        out.append(hairline(x1 + 4, x2 - 4, y0 + 214.0, 0.25))
        if bands:
            out += [hairline(x0, x0 + w, y0 + BAND_TOP), hairline(x0, x0 + w, y0 + BAND_BOT)]
            out += [K.foil_rhomb(cx, y0 + BAND_TOP, 1.1), K.foil_rhomb(cx, y0 + BAND_BOT, 1.1)]
        return "".join(out)

    def html(self, x0, y0):
        return (f'<div class="cv-a cv-s" style="left:{x0}mm; width:{self.w}mm; top:{y0}mm">'
                f'<p class="tx ed" style="top:219.5mm">الطبعة الأولى</p></div>')


# --------------------------------------------------------------------------- assembly

PAGE_CSS = """
@page { size: %(w)smm %(h)smm; margin: 0; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; }
.cvr { position: relative; width: %(w)smm; height: %(h)smm; overflow: hidden; background: #0B2461; color: #F4EFE3; }
.cvr > img.fld, .cvr > svg.gold { position: absolute; left: 0; top: 0; width: %(w)smm; height: %(h)smm; }
"""


def texture(name, size_mm, dpi, prims, recesses=(), knock=()):
    size = (round(K.mm(size_mm[0], dpi)), round(K.mm(size_mm[1], dpi)))
    rel = K.knockout(K.draw_relief(size, prims, dpi), knock, dpi, pad=1.6)
    for box in recesses:
        rel = recess(rel, dpi, box)
    CACHE.mkdir(parents=True, exist_ok=True)
    return K.save_jpeg(cloth(size, dpi, relief=rel), CACHE / f"{name}-{dpi}.jpg", dpi)


def section(font_css, tex, svg, html, wmm, hmm, extra=""):
    return (f'<section class="cvr" style="width:{wmm}mm;height:{hmm}mm"><img class="fld" src="{tex.as_uri()}" alt="">'
            f'<svg class="gold" viewBox="0 0 {wmm} {hmm}" xmlns="http://www.w3.org/2000/svg"><defs>{K.gold_defs()}</defs>{svg}</svg>'
            f'{html}{extra}</section>')


def doc(font_css, body, wmm, hmm, title="الغلاف"):
    return (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{TITLE_1} {TITLE_2}: {title}</title>'
            f'<style>{font_css}</style><style>{PAGE_CSS % dict(w=wmm, h=hmm)}{TEXT_CSS}'
            '.fold { position: absolute; top: 0; width: 0; height: 3mm; border-left: .25pt solid #8C9BC4; }'
            '.fold.b { top: auto; bottom: 0; }</style></head><body>' + body + '</body></html>')


def front_section(font_css, dpi=300):
    """The book's first page: the front at trim size."""
    f = Front(font_css)
    svg = f.gold(0, 0)
    px1, py1, px2, py2 = PANEL
    tex = texture("front-a", (W, H), dpi, f.relief(0, 0), recesses=[(px1, py1, px2, py2)], knock=f.boxes)
    return section(font_css, tex, svg, f.html(0, 0), W, H)


def back_section(font_css, dpi=300):
    b = Back()
    px1, py1, px2, py2 = BACK_PANEL
    tex = texture("back-a", (W, H), dpi, b.relief(0, 0), recesses=[(px1, py1, px2, py2)])
    return section(font_css, tex, b.gold(0, 0), b.html(0, 0), W, H)


def spine_width(pages, caliper=0.1, boards=6.0):
    """Casebound spine: leaves x paper caliper, plus boards and case allowance (mm)."""
    return round(pages / 2 * caliper + boards, 1)


def wrap_section(font_css, spine, dpi=300, bleed=BLEED):
    """Front | spine | back, left to right as the flat case lies (an Arabic book opens from the right).
    The two gold measures run unbroken across all three panels."""
    wmm, hmm = 2 * W + spine + 2 * bleed, H + 2 * bleed
    fx, sx, bx = bleed, bleed + W, bleed + W + spine
    f, s, b = Front(font_css), Spine(font_css, spine), Back()
    svg = (f.gold(fx, bleed, bands=False) + s.gold(sx, bleed, bands=False) + b.gold(bx, bleed, bands=False)
           + hairline(fx + 28, bx + 172, bleed + BAND_TOP) + hairline(fx + 28, bx + 172, bleed + BAND_BOT)
           + measure_band(fx + 28, fx + 172, bleed + BAND_TOP) + measure_band(bx + 28, bx + 172, bleed + BAND_TOP)
           + "".join(K.foil_rhomb(x, bleed + y, 1.25) for x in (fx + 28, bx + 172) for y in (BAND_BOT,))
           + K.foil_rhomb(sx + spine / 2, bleed + BAND_TOP, 1.1) + K.foil_rhomb(sx + spine / 2, bleed + BAND_BOT, 1.1))
    pf, pb = PANEL, BACK_PANEL
    prims = f.relief(fx, bleed)
    tex = texture(f"wrap-a-{spine}", (wmm, hmm), dpi, prims,
                  recesses=[(fx + pf[0], bleed + pf[1], fx + pf[2], bleed + pf[3]),
                            (bx + pb[0], bleed + pb[1], bx + pb[2], bleed + pb[3])],
                  knock=f.boxes)
    folds = "".join(f'<div class="fold" style="left:{x}mm"></div><div class="fold b" style="left:{x}mm"></div>' for x in (sx, bx))
    html = f.html(fx, bleed) + s.html(sx, bleed) + b.html(bx, bleed)
    return section(font_css, tex, svg, html, wmm, hmm, folds), wmm, hmm


def main():
    import build as B
    import book_build as BB
    font_css = B.static_instances(B.ensure_fonts(BB.BOOK_FONT_CSS, "bookfonts"))
    dpi = 200 if "--draft" in sys.argv else 300
    pages = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--pages=")), 1400)
    print(B.render(doc(font_css, front_section(font_css, dpi), W, H), "cover-front"))
    print(B.render(doc(font_css, back_section(font_css, dpi), W, H), "cover-back"))
    sp = spine_width(pages)
    sec, wmm, hmm = wrap_section(font_css, sp, dpi)
    print("spine", sp, "mm for", pages, "pages")
    print(B.render(doc(font_css, sec, wmm, hmm, "الغلاف الكامل"), "cover-wrap"))


if __name__ == "__main__":
    main()
