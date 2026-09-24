#!/usr/bin/env python3
"""Cover, edition 1.2 (Bible, part seven, ch. 38): designed from zero.

One object across front, spine and back:
- deep sapphire soft-touch cloth;
- the word «البيان» from the subtitle, in Qahiri at a huge size, blind-debossed tone on tone, running
  from the back over the spine onto the front (the only ornament, and it is the book's own word);
- one hairline of gold foil crossing the whole case at a single level, with one crimson nuqta;
- the title as a composed logotype: «صناعة» in Qahiri as a crown over «المتكلّم العربي» in Markazi
  Text SemiBold, drawn as outlines and spaced by hand, set flush to the spine side (asymmetric);
- nothing else: no frame, no rhombi, no measure bands.

    python3 cover2.py            writes .cache/cover2/wrap-v1.pdf and front-v1.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import cover as CV  # noqa: E402
import cover_kit as K  # noqa: E402
import lettering as L  # noqa: E402

FONT_CSS_12 = [
    "https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Amiri+Quran&display=swap",
    "https://fonts.googleapis.com/css2?family=Markazi+Text:wght@400;500;600;700&display=swap",
    "https://fonts.googleapis.com/css2?family=Qahiri&display=swap",
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&display=swap",
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap",
    "https://fonts.googleapis.com/css2?family=Source+Serif+4:wght@400;600&display=swap",
]
CACHE = HERE / ".cache" / "cover2"
W, H, BLEED = 200.0, 260.0, 3.0
MARGIN = 26.0                     # front margin on the spine side, where the title stands
LINE_Y = 104.0                    # the one gold line (trim coordinates)
PEARL = "#F1EBDD"
GOLD = "url(#foil)"
CRIMSON = "#A8172E"
VOLUMES = {1: ("الأول", "التأسيس", "١"), 2: ("الثاني", "التواصل", "٢"), 3: ("الثالث", "المنصّات", "٣"), 4: ("الرابع", "التمكين", "٤")}
AUTHOR = "أحمد بن إبراهيم السليمي"
SUBTITLE = "من سلامة اللسان إلى حسن البيان"
BLURB = ("كتابٌ في صناعة الكلام بالعربية الفصحى المعاصرة، لمن يعرف العربية ثم لا يجدها على لسانه حين يحتاج إليها. "
         "يبدأ من سؤالٍ لا بدّ منه: أيّ عربية نتكلّم؟ ثم يمضي من صحة الصوت واستقامة الجملة إلى مراعاة المقام وحسن البيان، "
         "جامعًا بين أصول البيان العربي وما انتهى إليه الدرس الحديث في التواصل، ومقيمًا ذلك كله على النماذج المتدرّجة والحوار والتدريب والتقويم.")
VOL_BLURB = {1: "يضع المجلد الأول الأساس: ما العربية التي نتكلّم بها، وأركان الكلام ودرجاته، وصحة النطق ومخارج الحروف، واستقامة العبارة.",
             2: "يبني المجلد الثاني على الأساس: البيان وترتيب الكلام، وآداب المخاطبة، وقراءة المقام.",
             3: "ينقل المجلد الثالث المتكلّم إلى المنصّات: المجلس والمحاضرة والمقابلة والإعلام.",
             4: "يختم المجلد الرابع بالملكة نفسها: الارتجال، وبنك الأخطاء، والأداء الختامي."}


def fonts():
    return B.static_instances(B.ensure_fonts(FONT_CSS_12, "fonts12"))


def face(css, fam, w):
    return L.arabic_face(css, fam, w)


# --------------------------------------------------------------------------- the logotype

class Logotype:
    """«صناعة» (Qahiri) over «المتكلّم العربي» (Markazi 600), flush right."""

    def __init__(self, css, width=142.0, crown_ratio=0.40, gap=4.2):
        mk, qh = face(css, "Markazi Text", 600), face(css, "Qahiri", 400)
        p1, p2 = L.Line("المتكلّم", mk, 10.0), L.Line("العربي", mk, 10.0)
        word_space = 10.0 * 0.22
        s = width / (p1.width + word_space + p2.width) * 10.0
        self.w1, self.w2 = L.Line("المتكلّم", mk, s), L.Line("العربي", mk, s)
        self.space = s * 0.22
        self.width = self.w1.width + self.space + self.w2.width
        c = L.Line("صناعة", qh, 10.0)
        self.crown = L.Line("صناعة", qh, width * crown_ratio / c.width * 10.0)
        self.gap = gap
        self.size = s

    def svg(self, x_right, top, shadow=True):
        cb = self.crown.bounds
        base_c = top - cb[1]
        tb = (min(self.w1.bounds[1], self.w2.bounds[1]), max(self.w1.bounds[3], self.w2.bounds[3]))
        base_t = base_c + cb[3] + self.gap - tb[0]
        items = [(self.crown, x_right - self.crown.width, base_c),
                 (self.w1, x_right - self.w1.width, base_t),
                 (self.w2, x_right - self.w1.width - self.space - self.w2.width, base_t)]
        out = []
        for ln, x, b in items:
            if shadow:   # the foil is stamped into the cloth: a crisp dark lip below and right
                out.append(L.svg_path(ln, x + 0.18, b + 0.24, fill="#020A1E", fill_opacity="0.6"))
            out.append(L.svg_path(ln, x, b, fill=GOLD))
            out.append(L.svg_path(ln, x - 0.05, b - 0.08, fill="#FFF4D8", fill_opacity="0.18"))
        bottom = base_t + tb[1]
        return "".join(out), bottom


# --------------------------------------------------------------------------- blind deboss: «البيان»

def deboss_map(css, size_px, dpi, centre_x_mm, baseline_mm, height_mm):
    """Height map of «البيان» in Qahiri, centred on the spine so the word runs from the back over the
    spine onto the front, whole and legible, below the gold line."""
    w, h = size_px
    k = dpi / 25.4
    font_path = face(css, "Qahiri", 400)
    from fontTools.ttLib import TTFont
    import io
    ttf = CACHE / "qahiri.ttf"
    if not ttf.exists():
        CACHE.mkdir(parents=True, exist_ok=True)
        f = TTFont(font_path)
        f.flavor = None
        f.save(str(ttf))
    fnt = ImageFont.truetype(str(ttf), size=int(height_mm * k), layout_engine=ImageFont.Layout.RAQM)
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0, 0), "البيان", font=fnt, direction="rtl", language="ar")
    tw = bbox[2] - bbox[0]
    x = centre_x_mm * k - tw / 2 - bbox[0]
    print('deboss word width mm', round(tw / k, 1), 'ink height mm', round((bbox[3] - bbox[1]) / k, 1))
    asc = fnt.getmetrics()[0]
    y = baseline_mm * k - asc
    d.text((x, y), "البيان", font=fnt, fill=255, direction="rtl", language="ar")
    img = img.filter(ImageFilter.GaussianBlur(dpi / 300 * 1.2))
    return np.asarray(img, np.float32) / 255 * 0.42


def cloth_tex(css, name, wmm, hmm, dpi, deboss):
    size = (round(wmm / 25.4 * dpi), round(hmm / 25.4 * dpi))
    rel = deboss_map(css, size, dpi, *deboss) if deboss else None
    CACHE.mkdir(parents=True, exist_ok=True)
    arr = CV.cloth(size, dpi, relief=rel)
    return K.save_jpeg(arr, CACHE / f"{name}-{dpi}.jpg", dpi)


# --------------------------------------------------------------------------- panels

TEXT_CSS = """
.cv { position: absolute; color: %(pearl)s; direction: rtl; }
.cv-sub { font-family: "Markazi Text"; font-weight: 400; font-size: 17pt; line-height: 1.3; }
.cv-by { font-family: "IBM Plex Sans Arabic"; font-weight: 400; font-size: 7.6pt; color: #C9B27A; }
.cv-author { font-family: "Markazi Text"; font-weight: 500; font-size: 15pt; line-height: 1.3; }
.cv-vol { font-family: "IBM Plex Sans Arabic"; font-weight: 400; font-size: 7.8pt; color: #C9B27A; }
.cv-blurb { font-family: "Amiri"; font-size: 11.6pt; line-height: 1.95; text-align: justify; color: %(pearl)s; }
.cv-blurb p { margin: 0 0 3.2mm; }
.cv-steps { font-family: "IBM Plex Sans Arabic"; font-size: 8pt; color: #B7AE9C; display: flex; gap: 5mm; align-items: baseline; }
.cv-steps b { font-weight: 500; color: #E9D7A6; }
.cv-spine-part { font-family: "Markazi Text"; font-weight: 500; font-size: 12pt; color: %(pearl)s; text-align: center; }
.cv-spine-author { font-family: "Markazi Text"; font-weight: 500; font-size: 11pt; color: %(pearl)s; white-space: nowrap;
  position: absolute; transform: translate(-50%%, -50%%) rotate(-90deg); }
""" % dict(pearl=PEARL)


def front(css, x0, y0, vol):
    """Front panel at (x0, y0) of the wrap; returns (svg, html)."""
    logo = Logotype(css)
    xr = x0 + W - MARGIN
    svg, bottom = logo.svg(xr, y0 + 36.0)
    ord_, part, num = VOLUMES[vol]
    html = (f'<div class="cv cv-sub" style="right:{MARGIN + (BLEED if x0 else 0) + (0)}mm;top:{y0 + LINE_Y - 12.6:.2f}mm;'
            f'right:auto;left:{x0 + MARGIN:.2f}mm;width:{W - 2 * MARGIN:.2f}mm;text-align:right">{SUBTITLE}</div>'
            f'<div class="cv cv-by" style="left:{x0 + MARGIN:.2f}mm;width:{W - 2 * MARGIN:.2f}mm;top:{y0 + 219:.2f}mm;text-align:right">تأليف</div>'
            f'<div class="cv cv-author" style="left:{x0 + MARGIN:.2f}mm;width:{W - 2 * MARGIN:.2f}mm;top:{y0 + 224:.2f}mm;text-align:right">{AUTHOR}</div>'
            f'<div class="cv cv-vol" style="left:{x0 + MARGIN:.2f}mm;top:{y0 + 219:.2f}mm">المجلد {ord_}</div>')
    # volume word in Qahiri, gold, at the free (outer) corner, on the author's baseline
    qh = face(css, "Qahiri", 400)
    pv = L.Line(part, qh, 13.0)
    svg += L.svg_path(pv, x0 + MARGIN + 0.18, y0 + 236.2 + 0.24, fill="#020A1E", fill_opacity="0.6")
    svg += L.svg_path(pv, x0 + MARGIN, y0 + 236.2, fill=GOLD)
    return svg, html


def spine(css, x0, y0, sw, vol):
    ord_, part, num = VOLUMES[vol]
    cx = x0 + sw / 2
    qh, mk = face(css, "Qahiri", 400), face(css, "Markazi Text", 600)
    n = L.Line(num, mk, 17.0)
    out = [L.svg_path(n, cx - n.width / 2 + 0.16, y0 + 36 + 0.22, fill="#020A1E", fill_opacity="0.6"),
           L.svg_path(n, cx - n.width / 2, y0 + 36, fill=GOLD)]
    # the title reads top to bottom: rotate the line so its tops face the front (left)
    t = L.Line("صناعة المتكلّم العربي", mk, 10.0)
    size = min(sw * 0.40, 104.0 / t.width * 10.0)
    t = L.Line("صناعة المتكلّم العربي", mk, size)
    ymid = y0 + LINE_Y + 10 + t.width / 2
    b = t.bounds
    base_off = -(b[1] + b[3]) / 2            # centre the ink on the spine axis
    tr = f"translate({cx:.3f} {ymid:.3f}) rotate(-90) translate({-t.width / 2:.3f} {base_off:.3f})"
    out.append(f'<path transform="translate(0.2 0.18) {tr}" d="{t.d}" fill="#020A1E" fill-opacity="0.6"/>')
    out.append(f'<path transform="{tr}" d="{t.d}" fill="{GOLD}"/>')
    html = (f'<div class="cv cv-spine-part" style="left:{x0:.2f}mm;width:{sw:.2f}mm;top:{y0 + 42:.2f}mm">{part}</div>'
            f'<div class="cv cv-spine-author" style="left:{cx:.2f}mm;top:{y0 + 236:.2f}mm">{AUTHOR}</div>')
    return "".join(out), html


def back(css, x0, y0, vol):
    ord_, part, num = VOLUMES[vol]
    steps = "".join(f'<span>{"<b>" if v == vol else ""}{VOLUMES[v][1]}{"</b>" if v == vol else ""}</span>' for v in (1, 2, 3, 4))
    html = (f'<div class="cv cv-blurb" style="left:{x0 + 54:.2f}mm;width:{W - 54 - MARGIN:.2f}mm;top:{y0 + LINE_Y + 12:.2f}mm">'
            f'<p>{BLURB}</p><p>{VOL_BLURB[vol]}</p></div>'
            f'<div class="cv cv-steps" style="left:{x0 + 54:.2f}mm;width:{W - 54 - MARGIN:.2f}mm;top:{y0 + 226:.2f}mm;justify-content:flex-start;direction:rtl">{steps}</div>')
    return "", html


def wrap(css, vol=1, spine_mm=48.2, dpi=300, bleed=BLEED):
    wmm, hmm = 2 * W + spine_mm + 2 * bleed, H + 2 * bleed
    fx, sx, bx = bleed, bleed + W, bleed + W + spine_mm
    y0 = bleed
    # «البيان» starts on the back near its outer third and ends on the front
    tex = cloth_tex(css, f"wrap-v{vol}-{spine_mm}", wmm, hmm, dpi,
                    deboss=(sx - 34.0, y0 + 238.0, 100.0))
    fs, fh = front(css, fx, y0, vol)
    ss, sh = spine(css, sx, y0, spine_mm, vol)
    bs, bh = back(css, bx, y0, vol)
    line = (f'<rect x="0" y="{y0 + LINE_Y + 0.22:.3f}" width="{wmm:.2f}" height="0.34" fill="#020A1E" fill-opacity="0.5"/>'
            f'<rect x="0" y="{y0 + LINE_Y - 0.17:.3f}" width="{wmm:.2f}" height="0.34" fill="{GOLD}"/>')
    nuqta = (f'<circle cx="{fx + W - MARGIN + 0.2:.2f}" cy="{y0 + LINE_Y + 0.25:.2f}" r="1.25" fill="#020A1E" fill-opacity="0.55"/>'
             f'<circle cx="{fx + W - MARGIN:.2f}" cy="{y0 + LINE_Y:.2f}" r="1.25" fill="{CRIMSON}"/>'
             f'<path d="M{fx + W - MARGIN - 0.9:.2f} {y0 + LINE_Y - 0.4:.2f} a1 1 0 0 1 1.5 -0.75" fill="none" stroke="#E6808E" stroke-width="0.18" stroke-opacity="0.8"/>')
    svg = line + nuqta + fs + ss + bs
    body = (f'<section class="cvr" style="position:relative;width:{wmm}mm;height:{hmm}mm;overflow:hidden;background:#0B2461">'
            f'<img src="{tex.as_uri()}" style="position:absolute;left:0;top:0;width:{wmm}mm;height:{hmm}mm" alt="">'
            f'<svg viewBox="0 0 {wmm} {hmm}" style="position:absolute;left:0;top:0;width:{wmm}mm;height:{hmm}mm" xmlns="http://www.w3.org/2000/svg">'
            f'<defs>{K.gold_defs()}</defs>{svg}</svg>{fh}{sh}{bh}</section>')
    return body, wmm, hmm


def doc(css, body, wmm, hmm):
    return (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>صناعة المتكلّم العربي: الغلاف</title>'
            f'<style>{css}</style><style>@page {{ size: {wmm}mm {hmm}mm; margin: 0; }} html,body{{margin:0}} {TEXT_CSS}</style>'
            f'</head><body>{body}</body></html>')


def main():
    css = fonts()
    body, wmm, hmm = wrap(css, 1, 48.2, dpi=int(sys.argv[1]) if len(sys.argv) > 1 else 200)
    CACHE.mkdir(parents=True, exist_ok=True)
    pdf = B.render(doc(css, body, wmm, hmm), "cover2-wrap")
    out = CACHE / "wrap-v1.pdf"
    out.write_bytes(Path(pdf).read_bytes())
    import pypdfium2 as pdfium
    pdfium.PdfDocument(str(out))[0].render(scale=1.2).to_pil().save(CACHE / "wrap-v1.png")
    print(out)


if __name__ == "__main__":
    main()
