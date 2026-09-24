#!/usr/bin/env python3
"""Reference pages for edition 1.2 (Bible, part seven; Volume I revision specification, §5).

Each page is composed by hand as the art director would set it, in the new type system:
Qahiri for single display words, Markazi Text for headings, Amiri for reading, IBM Plex Sans
Arabic for navigation, tables and figures. The pages are prototypes of page types, not final pages.

    python3 proto.py      writes ../Volume-I_Revision-Prototypes.pdf and a contact sheet
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import cover2 as C2  # noqa: E402
import lettering as L  # noqa: E402

OUT = HERE.parent / "Volume-I_Revision-Prototypes.pdf"
BOOK = HERE.parent / "book"

CSS = r"""
@page { size: 200mm 260mm; margin: 0; }
@page wrap { size: %(wrapw)smm %(wraph)smm; margin: 0; }
:root {
  --ink: #1D1A16; --ink-2: #4A443C; --ink-3: #7A7266; --paper: #FBF8F1; --paper-2: #F3EDE0;
  --sapphire: #0E2A6B; --sapphire-2: #2B4A8F; --sand: #C9B27A; --gold-ink: #8A6A1F; --crimson: #A8172E;
  --read: "Amiri", serif; --title: "Markazi Text", "Amiri", serif; --kufi: "Qahiri", serif;
  --sans: "IBM Plex Sans Arabic", sans-serif; --latin: "Source Serif 4", serif; --latin-sans: "IBM Plex Sans", sans-serif;
  --quran: "Amiri Quran", "Amiri", serif;
}
html, body { margin: 0; }
body { background: #888; }
.pg { position: relative; width: 200mm; height: 260mm; background: var(--paper); overflow: hidden; break-after: page; color: var(--ink); direction: rtl; }
.wrap-pg { page: wrap; break-after: page; }
.blk { position: absolute; top: 26mm; bottom: 32mm; right: 41mm; left: 41mm; }
.rh { position: absolute; top: 13mm; font: 400 7.4pt/1 var(--sans); color: var(--ink-3); }
.rh.r { right: 41mm; } .rh.l { left: 41mm; }
.fo { position: absolute; bottom: 15mm; font: 400 8pt/1 var(--sans); color: var(--ink-2); display: flex; align-items: center; gap: 2mm; }
.fo::before { content: ""; width: 1.3mm; height: 1.3mm; border-radius: 50%%; background: var(--sand); }
.fo.r { right: 41mm; } .fo.l { left: 41mm; flex-direction: row-reverse; }
p { font: 400 12.4pt/2.0 var(--read); text-align: justify; margin: 0 0 0; text-indent: 0; hyphens: none; }
p + p { text-indent: 6mm; }
p.flush, .noind p { text-indent: 0; }
.lead { font-size: 13.4pt; line-height: 1.95; }
h2.t { font: 600 17pt/1.4 var(--title); color: var(--sapphire); margin: 7mm 0 2.4mm; display: flex; align-items: center; gap: 2.4mm; }
h2.t::before { content: ""; width: 1.5mm; height: 1.5mm; border-radius: 50%%; background: var(--sand); flex: none; }
h3.s { font: 500 13.5pt/1.5 var(--title); color: var(--ink); margin: 5mm 0 1.4mm; }
.en { font-family: var(--latin); font-size: .86em; direction: ltr; unicode-bidi: isolate; }
sup.fn { font: 500 7pt/0 var(--sans); color: var(--sapphire-2); vertical-align: super; margin: 0 .4mm; }
.notes { position: absolute; bottom: 32mm; right: 41mm; left: 41mm; }
.notes::before { content: ""; display: block; width: 25mm; border-top: .5pt solid var(--ink-3); margin-bottom: 2mm; }
.notes div { font: 400 9.4pt/1.6 var(--read); color: var(--ink-2); display: flex; gap: 1.6mm; }
.notes div b { font: 500 7.6pt/1.9 var(--sans); color: var(--sapphire-2); }
.notes .lat { direction: ltr; unicode-bidi: isolate; font-family: var(--latin); font-size: 8.4pt; text-align: left; }
ol.nums, ul.bl { margin: .6mm 0 1.2mm; padding: 0 6mm 0 0; }
ul.bl li, ol.nums li { font: 400 12.4pt/2.0 var(--read); text-align: justify; }
ul.bl { list-style: none; } ul.bl li { position: relative; } ul.bl li::before { content: ""; position: absolute; right: -4.4mm; top: 4.1mm; width: 1.2mm; height: 1.2mm; border-radius: 50%%; background: var(--sand); }
ol.nums li { font: 400 12.4pt/2.0 var(--read); }
.ayah { font: 400 15pt/2 var(--quran); color: var(--sapphire); text-align: center; margin: 3mm 0; }
.ayah .ref { font: 400 8.4pt/1 var(--sans); color: var(--ink-3); margin-right: 2mm; }
/* ---- title page, threshold, openers */
.center { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.kick { font: 500 8.4pt/1.4 var(--sans); color: var(--gold-ink); letter-spacing: .02em; }
.part-word { font: 400 118pt/1.05 var(--kufi); color: var(--sapphire); }
.part-line { font: 400 15pt/1.6 var(--title); color: var(--ink-2); max-width: 104mm; margin-top: 8mm; }
.dot { width: 1.8mm; height: 1.8mm; border-radius: 50%%; background: var(--crimson); margin: 9mm auto 0; }
.op { position: absolute; top: 50mm; right: 41mm; left: 41mm; }
.op .num { font: 500 8.6pt/1 var(--sans); color: var(--gold-ink); display: flex; gap: 3mm; }
.op .num span + span::before { content: ""; display: inline-block; width: 6mm; border-top: .5pt solid var(--sand); vertical-align: middle; margin-left: 3mm; }
.op h1 { font: 600 30pt/1.3 var(--title); color: var(--sapphire); margin: 4mm 0 0; max-width: 90mm; }
.op .rule { width: 18mm; border-top: .8pt solid var(--sand); margin: 7mm 0 7mm; }
/* ---- figures */
figure { margin: 5mm 0 4mm; }
figcaption { font: 400 8.2pt/1.55 var(--sans); color: var(--ink-2); margin-top: 2.6mm; display: flex; gap: 2mm; }
figcaption b { font-weight: 600; color: var(--sapphire); white-space: nowrap; }
.fig-title { font: 500 13pt/1.4 var(--title); color: var(--sapphire); margin-bottom: 3mm; }
/* ---- comparison */
.ctx { font: 400 8.2pt/1.7 var(--sans); color: var(--ink-2); border-top: .5pt solid var(--sand); border-bottom: .5pt solid var(--sand); padding: 1.4mm 0; margin: 2mm 0 5mm; display: flex; flex-wrap: wrap; gap: 0 5mm; }
.ctx b { font-weight: 600; color: var(--ink); }
.tier { display: grid; grid-template-columns: 24mm 1fr; gap: 0 4mm; margin: 0 0 4.2mm; }
.tier .lab { font: 600 8.2pt/1.5 var(--sans); padding-top: 1.8mm; }
.tier .lab small { display: block; font-weight: 400; font-size: 7.4pt; color: var(--ink-3); }
.tier .say { font: 400 12pt/1.95 var(--read); padding-right: 4mm; border-right: 1pt solid var(--tc); text-align: justify; }
.tier.t1 { --tc: var(--crimson); } .tier.t1 .lab { color: var(--crimson); }
.tier.t2 { --tc: #8A8378; } .tier.t2 .lab { color: #5E584F; }
.tier.t3 { --tc: var(--sapphire); } .tier.t3 .lab { color: var(--sapphire); }
.tier.t3 .say { background: var(--paper-2); padding: 1.2mm 4mm 1.2mm 3mm; }
table.cmp { width: 100%%; border-collapse: collapse; font: 400 8.6pt/1.55 var(--sans); margin-top: 2mm; }
table.cmp th { font-weight: 600; text-align: right; color: var(--ink); border-bottom: .8pt solid var(--ink); padding: 1.2mm 1.4mm; }
table.cmp td { border-bottom: .4pt solid #D8D0C0; padding: 1.3mm 1.4mm; vertical-align: top; color: var(--ink-2); }
table.cmp td:first-child { font-weight: 600; color: var(--ink); white-space: nowrap; }
table.cmp th.c1 { color: var(--crimson); } table.cmp th.c3 { color: var(--sapphire); }
/* ---- dialogue as a script */
.script { display: grid; grid-template-columns: 7mm 20mm 1fr; gap: 1.2mm 3mm; align-items: baseline; margin: 3mm 0; }
.script .n { font: 400 7.4pt/1 var(--sans); color: var(--ink-3); text-align: left; direction: ltr; }
.script .who { font: 600 8.4pt/1.5 var(--sans); color: var(--sapphire); }
.script .who.b { color: var(--ink-2); }
.script .say { font: 400 12pt/1.9 var(--read); }
.script .dir { color: var(--ink-3); font-size: 10.6pt; }
/* ---- practice */
.prac-h { display: flex; align-items: baseline; justify-content: space-between; border-bottom: .8pt solid var(--ink); padding-bottom: 1.6mm; margin-bottom: 4mm; }
.prac-h h2 { font: 600 17pt/1.3 var(--title); color: var(--sapphire); margin: 0; }
.prac-h span { font: 500 8pt/1 var(--sans); color: var(--ink-3); }
.card { border: .6pt solid #CFC5B1; background: #FFFDF8; padding: 3mm 4mm 3.2mm; margin-bottom: 3.4mm; display: grid; grid-template-columns: 9mm 1fr; gap: 0 3mm; }
.card .k { font: 600 17pt/1 var(--title); color: var(--sand); padding-top: 1mm; }
.card .tag { font: 600 7.6pt/1.4 var(--sans); color: var(--gold-ink); }
.card .tag i { font-style: normal; color: var(--ink-3); font-weight: 400; margin-right: 2mm; }
.card p { font-size: 11.4pt; line-height: 1.85; text-indent: 0; }
.mastery { margin-top: 5mm; }
.mastery h3 { font: 600 9.4pt/1.4 var(--sans); color: var(--ink); margin: 0 0 1.6mm; }
/* ---- foreword */
.fw-h { font: 600 24pt/1.3 var(--title); color: var(--sapphire); margin: 34mm 0 9mm; }
"""


def rh(right, left):
    return f'<div class="rh r">{right}</div><div class="rh l">{left}</div>'


def fo(n, side):
    return f'<div class="fo {side}">{n}</div>'


def page(inner, cls=""):
    return f'<section class="pg {cls}">{inner}</section>'


# --------------------------------------------------------------------------- page makers

def title_page(css):
    logo = C2.Logotype(css, width=118.0)
    svg, bottom = logo.svg(159.0, 58.0, shadow=False)
    svg = svg.replace('fill="url(#foil)"', 'fill="#0E2A6B"').replace('fill="#FFF4D8" fill-opacity="0.18"', 'fill="none"')
    return page(f'''<svg viewBox="0 0 200 260" style="position:absolute;inset:0;width:200mm;height:260mm">{svg}</svg>
<div style="position:absolute;top:{bottom + 9:.1f}mm;right:41mm;left:41mm;text-align:right">
 <div style="font:400 17pt/1.4 var(--title);color:var(--ink)">من سلامة اللسان إلى حسن البيان</div>
 <div style="font:400 10pt/1.7 var(--sans);color:var(--ink-2);margin-top:3mm;max-width:100mm">منهجٌ شامل في النطق والتعبير والخطاب وآداب التواصل والملكة الشفهية</div>
</div>
<div style="position:absolute;top:150mm;right:41mm;left:41mm;border-top:.5pt solid var(--sand)"></div>
<div style="position:absolute;top:156mm;right:41mm;font:500 8.6pt/1.6 var(--sans);color:var(--gold-ink)">المجلد الأول</div>
<div style="position:absolute;top:161mm;right:41mm;font:400 34pt/1.2 var(--kufi);color:var(--sapphire)">التأسيس</div>
<div style="position:absolute;bottom:40mm;right:41mm;text-align:right">
 <div style="font:400 7.8pt/1.6 var(--sans);color:var(--ink-3)">تأليف</div>
 <div style="font:500 15pt/1.5 var(--title);color:var(--ink)">أحمد بن إبراهيم السليمي</div>
 <div style="font:400 9.6pt/1.6 var(--read);color:var(--ink-2)">غفر الله له ولوالديه ولجميع المسلمين</div>
</div>''')


def foreword_page():
    md = (BOOK / "00-كلمة-المؤلف.md").read_text(encoding="utf-8")
    paras = [p.strip() for p in md.split("\n\n") if p.strip() and not p.startswith("#")]
    body = "".join(f"<p>{x}</p>" for x in paras[:4])
    return page(f'''{rh("", "")}<div class="blk"><h1 class="fw-h">كلمة المؤلف</h1>{body}</div>{fo("٩", "l")}''')


def threshold():
    return page('''<div class="center">
<div class="kick">الجزء الأول</div>
<div class="part-word">التأسيس</div>
<div class="part-line">أن يستقيم اللسان قبل أن يُطلب منه البيان: من أيّ عربيةٍ نتكلّم، إلى صحة الصوت، إلى استقامة الجملة.</div>
<div class="dot"></div></div>''')


def md_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\*(.+?)\*", r"<i>\1</i>", s)
    s = re.sub(r"\(diglossia\)", '(<span class="en">diglossia</span>)', s)
    s = re.sub(r"\[\^(\d)\]", lambda m: f'<sup class="fn">{"٠١٢٣٤٥٦٧٨٩"[int(m.group(1))]}</sup>', s)
    return s


def md_block(b, first=False):
    lines = [l for l in b.split("\n") if l.strip()]
    if all(re.match(r"^- ", l) for l in lines):
        return '<ul class="bl">' + "".join(f"<li>{md_inline(l[2:])}</li>" for l in lines) + "</ul>"
    if all(re.match(r"^\d+\. ", l) for l in lines):
        items = [md_inline(re.sub(r"^\d+\. ", "", l)) for l in lines]
        return '<ol class="nums">' + "".join(f"<li>{x}</li>" for x in items) + "</ol>"
    if b.startswith("## "):
        return f'<h2 class="t">{md_inline(b[3:])}</h2>'
    return f'<p class="{"flush" if first else ""}">{md_inline(b)}</p>'


def flow(blocks):
    out, prev_h = [], True
    for b in blocks:
        out.append(md_block(b, first=prev_h))
        prev_h = b.startswith("## ") or b.startswith("- ") or re.match(r"^\d+\. ", b) is not None
    return "".join(out)


def chapter_text():
    md = (BOOK / "المدخل" / "ف01-العربية-ومستوياتها.md").read_text(encoding="utf-8")
    body = md.split("\n", 1)[1]
    notes = dict(re.findall(r"^\[\^(\d)\]:\s*(.+)$", body, re.M))
    body = re.sub(r"^\[\^\d\]:.*$", "", body, flags=re.M)
    blocks = [b.strip() for b in body.split("\n\n") if b.strip()]
    return blocks, notes


def opener(blocks):
    first, second = blocks[0], blocks[1]
    return page(f'''{rh("", "")}<div class="op"><div class="num"><span>المدخل</span><span>الفصل الأول</span></div>
<h1>العربية ومستوياتها</h1><div class="rule"></div>
<p class="lead flush">{md_inline(first)}</p><p>{md_inline(second)}</p>{flow(blocks[2:4])}</div>{fo("٣١", "l")}''')


def prose_page(blocks, notes):
    # «لغة واحدة…» second paragraph onward, then «ما يقوله الدارسون» with notes 1–2
    sec2 = [b for b in blocks if b.startswith("## ما يقوله")][0]
    i = blocks.index(sec2)
    html = flow(blocks[4:i + 3])
    nts = "".join(f'<div><b>{"٠١٢٣٤٥٦٧٨٩"[int(k)]}</b><span class="{"lat" if re.search("[A-Za-z]", v) else ""}">{md_inline(v)}</span></div>'
                  for k, v in sorted(notes.items()) if k == "1")
    return page(f'''{rh("صناعة المتكلّم العربي", "")}<div class="blk">{html}</div><div class="notes">{nts}</div>{fo("٣٢", "r")}''')


def spectrum_svg():
    W, Hh = 118, 70
    xs = [110, 86, 62, 38, 12]
    labels = [("العربية التراثية", "القرآن والحديث وكتب العلم والشعر القديم"),
              ("الفصحى المعاصرة المكتوبة", "الكتاب والصحيفة والمراسلة الرسمية"),
              ("الفصحى المنطوقة", "المحاضرة والندوة والمقابلة والخطبة"),
              ("عامية المثقفين", "حديث المتعلمين في الشأن الجادّ"),
              ("العاميات", "البيت والسوق والحياة اليومية")]
    out = [f'<defs><linearGradient id="sp" x1="1" x2="0"><stop offset="0" stop-color="#0E2A6B"/><stop offset="1" stop-color="#C9B27A"/></linearGradient></defs>',
           f'<rect x="8" y="30" width="106" height="1.6" fill="url(#sp)"/>',
           # the book's field: written and spoken fusha
           f'<path d="M92 50.5 L92 53 L56 53 L56 50.5" fill="none" stroke="#0E2A6B" stroke-width=".35"/>',
           f'<text x="74" y="57.4" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-weight="600" font-size="3.1" fill="#0E2A6B">ميدان هذا الكتاب</text>']
    for n, (x, (a, b)) in enumerate(zip(xs, labels)):
        up = n % 2 == 1
        out.append(f'<circle cx="{x}" cy="30.8" r="1.6" fill="#FBF8F1" stroke="#0E2A6B" stroke-width=".4"/>')
        y = 8.5 if up else 39.5
        if up:
            out.append(f'<path d="M{x} 29 L{x} {y + 9.5}" stroke="#C9B27A" stroke-width=".25"/>')
        out.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-weight="600" font-size="2.9" fill="#1D1A16">{a}</text>')
        words = b.split(" ")
        mid = (len(words) + 1) // 2
        for j, ln in enumerate((" ".join(words[:mid]), " ".join(words[mid:]))):
            out.append(f'<text x="{x}" y="{y + 4.4 + j * 3.6:.1f}" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-size="2.45" fill="#4A443C">{ln}</text>')
    out.append('<text x="113" y="64" text-anchor="end" font-family="IBM Plex Sans Arabic" font-size="2.4" fill="#7A7266">أعلى الرسمية</text>')
    out.append('<text x="7" y="64" text-anchor="start" font-family="IBM Plex Sans Arabic" font-size="2.4" fill="#7A7266">أدنى الرسمية</text>')
    out.append('<path d="M100 66.5 L20 66.5" stroke="#7A7266" stroke-width=".25" marker-end="url(#ah)"/>')
    out.append('<defs><marker id="ah" markerWidth="4" markerHeight="4" refX="2" refY="2" orient="auto"><path d="M0 0 L4 2 L0 4 Z" fill="#7A7266"/></marker></defs>')
    return f'<svg viewBox="0 0 {W} {Hh}" style="width:118mm;height:{Hh}mm" direction="ltr">{"".join(out)}</svg>'


def figure_page(blocks):
    sec = [b for b in blocks if b.startswith("## المستويات التي")][0]
    i = blocks.index(sec)
    return page(f'''{rh("", "المدخل: ما العربية التي نتكلّم بها؟")}<div class="blk">
<h2 class="t">المستويات التي يعمل بها هذا الكتاب</h2><p class="flush">يعمل الكتاب بخمسة مستويات، يرسمها الشكل الآتي على طيفٍ واحد.</p>
<figure><div class="fig-title">طيف العربية</div>{spectrum_svg()}
<figcaption><b>الشكل ١</b><span>مستويات العربية مواضعُ على طيفٍ متصل لا غرفٌ منفصلة. يتنقّل المتكلّم الواحد بينها بحسب المقام والمخاطَب والموضوع، ويعمل هذا الكتاب في الفصحى المعاصرة بشقّيها المكتوب والمنطوق.</span></figcaption></figure>
{flow(blocks[i + 3:i + 4])}</div>{fo("٣٥", "l")}''')


def model_svg():
    out = ['<defs><marker id="a2" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto"><path d="M0 0 L4 2 L0 4 Z" fill="#0E2A6B"/></marker></defs>',
           # the maqam: the frame every exchange happens inside
           '<rect x="2" y="6" width="114" height="62" rx="2" fill="#F3EDE0" stroke="#C9B27A" stroke-width=".35"/>',
           '<text x="113" y="11.6" text-anchor="end" font-family="Markazi Text" font-weight="600" font-size="4.2" fill="#8A6A1F">المقام</text>',
           '<text x="113" y="15.6" text-anchor="end" font-family="IBM Plex Sans Arabic" font-size="2.3" fill="#7A7266">المكان والزمان والعلاقة والعُرف</text>']
    # speaker (right) and addressee (left)
    for x, a, b in ((100, "المتكلّم", "يختار"), (18, "المخاطَب", "يسمع ويفهم ويستجيب")):
        out.append(f'<circle cx="{x}" cy="37" r="9" fill="#FBF8F1" stroke="#0E2A6B" stroke-width=".5"/>')
        out.append(f'<text x="{x}" y="38.2" text-anchor="middle" font-family="Markazi Text" font-weight="600" font-size="3.8" fill="#0E2A6B">{a}</text>')
        out.append(f'<text x="{x}" y="51" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-size="2.3" fill="#4A443C">{b}</text>')
    # the four choices along the utterance
    steps = ["الغرض", "الموضوع", "الأسلوب", "الصوت"]
    for j, s in enumerate(steps):
        x = 82 - j * 15.3
        out.append(f'<rect x="{x - 6.4:.1f}" y="33.2" width="12.8" height="7.6" rx="1" fill="#FFFFFF" stroke="#2B4A8F" stroke-width=".3"/>')
        out.append(f'<text x="{x:.1f}" y="38" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-weight="600" font-size="2.6" fill="#1D1A16">{s}</text>')
    out.append('<path d="M90.6 37 L89 37" stroke="#0E2A6B" stroke-width=".4"/>')
    out.append('<path d="M29.8 37 L27.6 37" stroke="#0E2A6B" stroke-width=".4" marker-end="url(#a2)"/>')
    out.append('<text x="59" y="29.6" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-size="2.3" fill="#7A7266">الكلام</text>')
    # effect: returns to the speaker
    out.append('<path d="M18 46.5 C 30 64, 88 64, 100 46.5" fill="none" stroke="#A8172E" stroke-width=".4" stroke-dasharray="1.2 .9" marker-end="url(#a3)"/>')
    out.append('<defs><marker id="a3" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto"><path d="M0 0 L4 2 L0 4 Z" fill="#A8172E"/></marker></defs>')
    out.append('<text x="59" y="62.4" text-anchor="middle" font-family="IBM Plex Sans Arabic" font-weight="600" font-size="2.7" fill="#A8172E">الأثر</text>')
    return f'<svg viewBox="0 0 118 70" style="width:118mm;height:70mm" direction="ltr">{"".join(out)}</svg>'


def model_page():
    return page(f'''{rh("صناعة المتكلّم العربي", "")}<div class="blk">
<h2 class="t">أركان الموقف الكلامي</h2>
<p class="flush">لا يقع الكلام في فراغ. فللمتكلّم غرضٌ يريد بلوغه، وموضوعٌ يتكلّم فيه، وأسلوبٌ يختاره، وصوتٌ يؤدّي به، وله مخاطَبٌ يسمع فيفهم أو لا يفهم، ويستجيب أو يُعرض. والموقف كله يقع في مقامٍ له زمانه ومكانه وعلاقاته وأعرافه، وهو الذي يحكم على الاختيارات جميعًا.</p>
<figure>{model_svg()}<figcaption><b>الشكل ٢</b><span>المتكلّم يختار أربعة أمور، والمقام يحيط بالموقف كله، والأثر يعود إليه فيعرف به هل بلغ كلامه أم لم يبلغ.</span></figcaption></figure>
<p class="flush">وأهمّ ما في هذا الرسم خطّه المنقوط. فالمتكلّم الذي لا ينظر في أثر كلامه يتكلّم إلى نفسه، ولو كان أمامه ألف سامع. ومن هنا يبدأ الفرق بين الدرجات الأربع التي يقوم عليها الكتاب: فغير الناجح لا يرى إلا ما يريد أن يقول، والناجح يرى ما سيصل.</p>
</div>{fo("٥٢", "r")}''')


def comparison_page():
    t1 = "السلام عليكم يا دكتور. دكتور، أنا عندي مشكلة كبيرة جدًّا، يعني… أمي مريضة، وأنا سافرت، والبحث ما كمل، يعني أنا ما قدرت. وأنت تعرف أن البحث صعب جدًّا، وكل الطلاب يقولون إن الموعد قريب. فأنا أريد منك أن تعطيني وقتًا إضافيًّا، أسبوعًا أو أسبوعين، لأن هذا ليس خطئي."
    t2 = "السلام عليكم يا دكتور. أعتذر عن الإزعاج. والدتي مريضة، وقد سافرت إليها الأسبوع الماضي، فلم أستطع إكمال البحث. هل يمكن أن تؤجلوا لي موعد التسليم؟"
    t3 = "السلام عليكم ورحمة الله يا دكتور. هل يسمح وقتكم بدقيقة؟ [تنتظر الإذن] جزاكم الله خيرًا. أنا زينب، من طالبات السنة الرابعة. سافرتُ الأسبوع الماضي إلى والدتي لمرضها، فتأخرتُ في البحث: أتممتُ الفصلين الأولين، وبقي الفصل الأخير. فهل تأذنون لي بتأجيل التسليم ثلاثة أيام، إلى يوم الأحد؟ وإن لم يكن ذلك ممكنًا، فأنا مستعدة لتسليم ما أنجزته في موعده."
    t3 = t3.replace("[تنتظر الإذن]", '<span style="color:var(--ink-3);font-size:10.6pt">(تنتظر الإذن)</span>')
    rows = [("الاستئذان", "لا استئذان", "اعتذار عام", "سؤالٌ عن الوقت ثم انتظار الإذن"),
            ("التحديد", "«أسبوعًا أو أسبوعين»", "لا مدة", "«ثلاثة أيام، إلى يوم الأحد»"),
            ("ترتيب الأفكار", "شكوى فسبب فطلب فدفاع", "سبب فطلب", "سبب فما أُنجز فطلب فبديل"),
            ("المسؤولية", "«ليس خطئي»", "محايد", "عرضُ بديلٍ عند الرفض")]
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>" for a, b, c, d in rows)
    return page(f'''{rh("", "الفصل الأول: الكلام وأركانه")}<div class="blk">
<h2 class="t">طلبُ تأجيل موعد البحث</h2>
<div class="ctx"><span><b>المتكلّمة:</b> زينب، طالبة في السنة الرابعة</span><span><b>المخاطَب:</b> أستاذ المادة في ساعاته المكتبية</span><span><b>الرسمية:</b> ٣ إلى ٤ من ٥</span><span><b>الزمن:</b> أقلّ من دقيقة، والطلاب عند الباب</span></div>
<div class="tier t1"><div class="lab">غير الناجحة<small>ينفد الوقت قبل الطلب</small></div><div class="say">{t1}</div></div>
<div class="tier t2"><div class="lab">المقبولة<small>سليمة ولا تكفي</small></div><div class="say">{t2}</div></div>
<div class="tier t3"><div class="lab">الناجحة<small>كل جملة تؤدي وظيفة</small></div><div class="say">{t3}</div></div>
<table class="cmp"><tr><th>البعد</th><th class="c1">غير الناجحة</th><th>المقبولة</th><th class="c3">الناجحة</th></tr>{tr}</table>
</div>{fo("٥٥", "l")}''')


def dialogue_page():
    lines = [("المعلّمة خديجة", "(تقف، بصوتٍ مهذّبٍ واضح)", "السلام عليكم يا أستاذة سعاد."),
             ("المديرة سعاد", "", "وعليكم السلام. أين تقرير الحضور الشهري؟ كان موعده اليوم."),
             ("المعلّمة خديجة", "", "صحيح يا أستاذة، وأعتذر عن التأخر في إبلاغك. أنجزتُ منه ثلاثة أرباعه، وبقي قسم الغيابات الاستثنائية وحده."),
             ("المديرة سعاد", "", "التقرير يُرفع إلى الإدارة العليا عصر اليوم. هل تكفيكِ نصف الساعة فعلًا؟"),
             ("المعلّمة خديجة", "", "نعم يا أستاذة، سأنهيه خلال نصف ساعة، وأرسله إليكِ قبل الساعة الواحدة لتراجعيه قبل الرفع."),
             ("المديرة سعاد", "(تبتسم قليلًا)", "حسنًا، أعتمد على ذلك."),
             ("المعلّمة خديجة", "", "لن أُخلف الموعد إن شاء الله.")]
    rows = ""
    for i, (w, d, s) in enumerate(lines, 1):
        cls = "who" if "خديجة" in w else "who b"
        dd = f'<span class="dir">{d}</span> ' if d else ""
        rows += f'<div class="n">{i}</div><div class="{cls}">{w.split(" ")[1]}</div><div class="say">{dd}{s}</div>'
    return page(f'''{rh("صناعة المتكلّم العربي", "")}<div class="blk">
<h2 class="t">من المزاح إلى المكتب</h2>
<p class="flush">كانت المعلّمة خديجة تحادث صديقةً لها في الهاتف بصوتٍ مرتفع، حين دخلت المديرة تسأل عن تقريرٍ تأخّر. وقد رأينا في الصفحة السابقة كيف يقع الموقف عادةً. وهذا هو نفسه كما ينبغي أن يقع:</p>
<div class="ctx"><span><b>المقام:</b> غرفة المعلّمات، في أثناء الدوام</span><span><b>العلاقة:</b> معلّمة ومديرتها</span><span><b>الرسمية:</b> ٤ من ٥</span></div>
<div class="script">{rows}</div>
<p class="flush">لم تقل خديجة شيئًا بليغًا. لكنها أنهت المكالمة قبل أن تُحرَج، وانتقلت إلى الفصحى حين تغيّر المخاطَب، واعترفت بالتأخّر في جملة واحدة، ثم أعطت رقمًا وموعدًا. وبهذا انتقل الحديث من المحاسبة إلى الثقة في أربعة أسطر.</p>
</div>{fo("١٠٨", "r")}''')


def practice_page():
    cards = [("تدريب", "فردي، عشر دقائق", "اكتب طلبك أنت لتأجيل موعدٍ ما: عملٍ أو اجتماعٍ أو امتحان، بالترتيب الذي رأيته في النموذج الناجح: السبب، فما أُنجز، فالطلب المحدد، فالبديل. ثم احذف منه كل كلمة لا تؤدي وظيفة."),
             ("سجّل صوتك", "ثلاثون ثانية", "أدِّ الطلب نفسه بصوتك في ثلاثين ثانية أو أقل. ثم استمع إليه واسأل: هل استأذنتُ؟ هل حدّدتُ المدة؟ هل تركتُ للمخاطَب ما يقرّر به؟"),
             ("محاكاة", "في أزواج", "يؤدي أحدكما دور الأستاذ ويرفض الطلب بأدب. ويؤدي الآخر دور الطالب، فيقبل الرفض ويعرض بديله دون أن يعود إلى الشكوى."),
             ("مسار الناطق بالعربية", "", "أعد الطلب نفسه موجّهًا إلى رئيسك في العمل ثم إلى زميلك، ولاحظ ما يتغيّر من الألفاظ والنبرة، وما يبقى ثابتًا.")]
    html = "".join(f'<div class="card"><div class="k">{"١٢٣٤"[i]}</div><div><div class="tag">{t}<i>{s}</i></div><p>{b}</p></div></div>'
                   for i, (t, s, b) in enumerate(cards))
    rows = [("يحدّد المدة أو المطلوب بالرقم", "دائمًا"), ("يرتّب: سبب، فإنجاز، فطلب، فبديل", "في ثلاث محاولات من ثلاث"),
            ("لا يتجاوز الطلب ثلاثين ثانية", "في التسجيل"), ("يخلو من الشكوى ودفع المسؤولية", "دائمًا")]
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    return page(f'''{rh("", "الفصل الأول: الكلام وأركانه")}<div class="blk">
<div class="prac-h"><h2>تدريبات الفصل</h2><span>أربع مهام</span></div>{html}
<div class="mastery"><h3>معيار الإتقان</h3><table class="cmp"><tr><th>يُعدّ المتدرّب متقنًا لهذا الفصل إذا كان</th><th>الحدّ</th></tr>{tr}</table></div>
</div>{fo("٦٧", "l")}''')


def main():
    css = C2.fonts()
    body_wrap, wmm, hmm = C2.wrap(css, 1, 48.2, dpi=300)
    blocks, notes = chapter_text()
    pages = [f'<section class="wrap-pg">{body_wrap}</section>', title_page(css), foreword_page(), threshold(),
             opener(blocks), prose_page(blocks, notes), figure_page(blocks), model_page(), comparison_page(),
             dialogue_page(), practice_page()]
    html = (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>صناعة المتكلّم العربي: عيّنات الإصدار ١٫٢</title>'
            f'<style>{css}</style><style>{CSS % dict(wrapw=wmm, wraph=hmm)}{C2.TEXT_CSS}</style></head><body>{"".join(pages)}</body></html>')
    pdf = B.render(html, "proto12")
    OUT.write_bytes(Path(pdf).read_bytes())
    print(OUT)


if __name__ == "__main__":
    main()
