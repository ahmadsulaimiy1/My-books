#!/usr/bin/env python3
"""The opening of Volume I, typeset in the edition-1.2 system (Bible, part seven).

Flowing pages (Chromium pagination), with the page types of ch. 36 placed where the argument turns:
title page, the verse of Surat al-Rahman, the author's word, a sapphire threshold for the مقدمة,
a sapphire band opening every chapter, heritage pages for the scholars, poster interludes,
Qur'an in Amiri Quran, poetry in hemistichs, tables in IBM Plex Sans Arabic, notes at chapter end.

Type: Scheherazade New for reading; Changa Bold / Light as the principal display Kufi; Kufam
(the book's cut) for the logotype and poster words; Amiri for heritage; Plex for navigation.

    python3 opening.py          writes ../Volume-I_Opening.pdf
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import cover2 as C2  # noqa: E402
import proto2 as P2  # noqa: E402

BOOK = HERE.parent / "book"
OUT = HERE.parent / "Volume-I_Opening.pdf"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
ORD = ["", "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي عشر", "الثاني عشر", "الثالث عشر"]

CSS = r"""
@page { size: 200mm 260mm; margin: 25mm 39mm 30mm 39mm;
  @top-right { content: "صناعة المتكلّم العربي"; font: 400 7.4pt "IBM Plex Sans Arabic"; color: #7C7467; vertical-align: bottom; padding-bottom: 6mm; }
  @top-left { content: "%(head)s"; font: 400 7.4pt "IBM Plex Sans Arabic"; color: #7C7467; vertical-align: bottom; padding-bottom: 6mm; }
}
@page :first { margin-top: 104mm; @top-right { content: none; } @top-left { content: none; } }
:root { --ink: #1C1915; --ink-2: #4A443C; --ink-3: #7C7467; --paper: #FBF8F1; --paper-2: #F2ECDF;
  --sapphire: #0C2766; --sapphire-2: #2B4A8F; --gold: #C9A95C; --gold-l: #E4CB8C; --gold-ink: #8A6A1F; --crimson: #A8172E; }
html, body { margin: 0; background: var(--paper); }
body { direction: rtl; color: var(--ink); font: 400 13.2pt/1.85 "Scheherazade New", serif; }
.full { position: relative; width: 200mm; height: 260mm; overflow: hidden; break-before: page; break-after: page; }
.wrap-pg { page: wrap; break-after: page; }
.dark { background: var(--sapphire); color: #EFE7D6; }
.chap { break-before: page; }
.chap-band { position: absolute; top: 0; left: 0; right: 0; height: 92mm; background: var(--sapphire); color: #EFE7D6; }
.chap-band .k { position: absolute; top: 36mm; right: 39mm; font: 300 11pt/1 "Changa"; color: var(--gold-l); display: flex; gap: 3mm; align-items: center; }
.chap-band .k i { width: 10mm; border-top: .5pt solid var(--gold); display: inline-block; }
.chap-band h2 { position: absolute; top: 46mm; right: 39mm; left: 39mm; margin: 0; font: 700 29pt/1.25 "Changa"; color: #F4ECD9; string-set: chap content(); }
.chap-band .dot { position: absolute; bottom: -1.3mm; right: 39mm; width: 2.6mm; height: 2.6mm; border-radius: 50%%; background: var(--crimson); }
.chap-open { position: relative; }
p { margin: 0; text-align: justify; }
p + p { text-indent: 6mm; }
.chap-open > p:first-of-type { font-size: 14.4pt; line-height: 1.8; text-indent: 0; }
h3 { font: 700 15pt/1.45 "Changa"; color: var(--sapphire); margin: 7mm 0 2.4mm; break-after: avoid; }
h3::after { content: ""; display: block; width: 12mm; border-top: .8pt solid var(--gold); margin-top: 1.6mm; }
h3 + p { text-indent: 0; }
strong { font-weight: 700; }
.q { font: 400 14.6pt/1.9 "Amiri Quran", "Amiri"; color: var(--sapphire); }
.qref { font: 400 8.2pt/1 "IBM Plex Sans Arabic"; color: var(--ink-3); margin-right: 1.4mm; white-space: nowrap; }
p.ayah { text-align: center; text-indent: 0; margin: 4mm 0; break-inside: avoid; }
p.ayah .q { font-size: 17pt; line-height: 2.05; }
p.ayah .qref { display: block; margin-top: 1mm; }
blockquote { margin: 4mm 0; padding: 0; break-inside: avoid; }
blockquote.quote { border-right: 1.4pt solid var(--gold); padding: 1mm 5mm 1mm 0; }
blockquote.quote p { font: 400 14pt/1.9 "Amiri"; color: var(--sapphire); text-indent: 0; }
blockquote.def p { font: 400 13.6pt/1.8 "Scheherazade New"; color: var(--sapphire); text-align: center; text-indent: 0; }
.bayt { display: grid; grid-template-columns: 1fr 8mm 1fr; font: 400 14.2pt/2.05 "Amiri"; white-space: nowrap; }
.bayt span:first-child { text-align: left; } .bayt span:last-child { text-align: right; }
blockquote.poem { background: var(--paper-2); padding: 3mm 6mm; border-top: .5pt solid var(--gold); border-bottom: .5pt solid var(--gold); }
ol, ul { margin: 1mm 0 2mm; padding: 0 6.5mm 0 0; }
li { text-align: justify; margin: .4mm 0; }
ul { list-style: none; } ul > li { position: relative; }
ul > li::before { content: ""; position: absolute; right: -4.8mm; top: 3.9mm; width: 1.4mm; height: 1.4mm; transform: rotate(45deg); background: var(--gold); }
.sig { margin: 9mm 0 0 0; text-align: left; break-inside: avoid; }
.sig-name { display: block; font: 700 14pt "Changa"; color: var(--sapphire); }
.sig-du { display: block; font: 400 11pt/1.6 "Amiri"; color: var(--gold-ink); margin-top: 1mm; }
ol { list-style: arabic-indic; } ol > li { padding-right: 1.6mm; } ol > li::marker { font: 600 11pt "Changa"; color: var(--gold-ink); }
table { width: 100%%; border-collapse: collapse; font: 400 8.8pt/1.55 "IBM Plex Sans Arabic"; margin: 4mm 0; break-inside: avoid; }
th { font: 600 9.2pt/1.4 "Changa"; text-align: right; color: #F3ECDC; background: var(--sapphire); padding: 1.6mm 2mm; }
td { border-bottom: .4pt solid #D8D0C0; padding: 1.4mm 2mm; vertical-align: top; color: var(--ink-2); }
tr:nth-child(even) td { background: #F6F1E6; }
td:first-child { font-weight: 600; color: var(--ink); }
sup.fn { font: 600 7pt/0 "IBM Plex Sans Arabic"; color: var(--gold-ink); vertical-align: super; margin: 0 .3mm; }
sup.fn a { color: inherit; text-decoration: none; }
.notes { margin-top: 9mm; break-inside: auto; }
.notes h4 { font: 300 11pt/1 "Changa"; color: var(--gold-ink); margin: 0 0 2mm; display: flex; gap: 3mm; align-items: center; }
.notes h4::after { content: ""; flex: 1; border-top: .5pt solid var(--gold); }
.notes ol { padding-right: 6mm; }
.notes li { font: 400 9.8pt/1.55 "Scheherazade New"; color: var(--ink-2); }
.notes li::marker { font: 500 8pt "IBM Plex Sans Arabic"; color: var(--gold-ink); }
.lat { direction: ltr; unicode-bidi: isolate; font-family: "Source Serif 4"; font-size: .86em; }
/* heritage and poster interludes */
.her { position: absolute; top: 40mm; bottom: 40mm; right: 24mm; left: 24mm; border: .6pt solid var(--gold); padding: 3mm; }
.her-in { border: .3pt solid var(--gold); height: 100%%; box-sizing: border-box; padding: 16mm 12mm; display: flex; flex-direction: column; justify-content: center; background: var(--paper-2); text-align: center; }
.her .who { font: 300 12pt/1.4 "Changa"; color: var(--gold-ink); margin-bottom: 7mm; }
.her .qt { font: 400 18pt/2 "Amiri"; color: var(--sapphire); }
.her .src { font: 400 8.4pt/1.5 "IBM Plex Sans Arabic"; color: var(--ink-3); margin-top: 6mm; }
.poster { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; padding: 0 30mm; }
.poster .kick { font: 300 12pt/1 "Changa"; color: var(--gold-l); margin-bottom: 9mm; display: flex; gap: 3mm; align-items: center; }
.poster .kick i { width: 12mm; border-top: .5pt solid var(--gold); }
.poster .big { font: 700 60pt/1.2 "Changa"; color: var(--gold-l); }
.poster .big.kufam { font-family: "Kufam SMA"; font-feature-settings: "liga" 0; font-weight: 600; }
.poster .line { font: 400 16pt/1.8 "Scheherazade New"; color: #E7DFCE; max-width: 120mm; margin-top: 9mm; }
.toc-p { font: 400 12pt/1.9 "Scheherazade New"; }
.toc-row { display: flex; gap: 3mm; align-items: baseline; border-bottom: .4pt dotted #CFC5B1; padding: 1.2mm 0; }
.toc-row b { font: 600 10pt "Changa"; color: var(--gold-ink); min-width: 22mm; }
.toc-row span { font: 400 13pt "Scheherazade New"; }
"""


def ayat(html):
    """﴿…﴾ (ref) → Amiri Quran span + reference; a paragraph that is only an ayah becomes a display ayah."""
    html = re.sub(r"﴿([^﴾]+)﴾\s*\(([^)]+)\)", r'<span class="q">﴿\1﴾</span><span class="qref">(\2)</span>', html)
    html = re.sub(r"﴿([^﴾]+)﴾", r'<span class="q">﴿\1﴾</span>', html)
    return html


def md_to_html(md):
    notes = dict(re.findall(r"^\[\^(\d+)\]:\s*(.+)$", md, re.M))
    md = re.sub(r"^\[\^\d+\]:.*$", "", md, flags=re.M)
    md = re.sub(r"\[\^(\d+)\]", lambda m: f'<sup class="fn">{m.group(1).translate(AR)}</sup>', md)
    md = re.sub(r"^\*\*(أحمد بن إبراهيم السليمي)\*\*\n(.+)$",
                r'<div class="sig"><span class="sig-name">\1</span><span class="sig-du">\2</span></div>', md, flags=re.M)
    html = markdown.markdown(md, extensions=["tables"])
    html = ayat(html)
    soup = BeautifulSoup(html, "html.parser")
    for p in soup.find_all("p"):
        t = p.get_text().strip()
        if t.startswith("﴿") and p.find(class_="q") and len(p.find_all(class_="q")) == 1 and t.endswith(")"):
            p["class"] = ["ayah"]
    for bq in soup.find_all("blockquote"):
        txt = bq.get_text("\n").strip()
        if " ... " in txt:
            lines = [l.strip() for l in txt.split("\n") if " ... " in l]
            bq.clear()
            bq["class"] = ["poem"]
            for l in lines:
                a, b = l.split(" ... ")
                bq.append(BeautifulSoup(f'<div class="bayt"><span>{a}</span><span></span><span>{b}</span></div>', "html.parser"))
        elif txt.startswith("«"):
            bq["class"] = ["quote"]
        else:
            bq["class"] = ["def"]
    for t in soup.find_all(string=re.compile(r"[A-Za-z]{3,}")):
        if t.parent.name not in ("style",) and not t.find_parent(class_="lat"):
            t.replace_with(BeautifulSoup(re.sub(r"([A-Za-z][^؀-ۿ]*[A-Za-z.)])", r'<span class="lat">\1</span>', str(t)), "html.parser"))
    note_html = ""
    if notes:
        items = "".join(f'<li>{ayat(v)}</li>' for k, v in sorted(notes.items(), key=lambda kv: int(kv[0])))
        items = re.sub(r"(\*)([^*]+)\*", r"<i>\2</i>", items)
        note_html = f'<section class="notes"><h4>حواشي الفصل</h4><ol>{items}</ol></section>'
    return str(soup), note_html


def chapter(md, kicker):
    m = re.search(r"^##\s+(.+)$", md, re.M)
    title = m.group(1)
    title = re.sub(r"^الفصل [^:]+:\s*", "", title)
    body = md[m.end():]
    html, notes = md_to_html(body)
    return f'<section class="chap"><div class="chap-open">{html}{notes}</div></section>', band(kicker, title)


def band(kicker, title):
    return (f'<section class="full"><div class="chap-band"><div class="k"><span>{kicker}</span><i></i></div>'
            f'<h2>{title}</h2><div class="dot"></div></div></section>')


def full(inner, cls=""):
    return f'<section class="full {cls}">{inner}</section>'


def heritage(who, quote, src):
    return full(f'<div class="her"><div class="her-in"><div class="who">{who}</div><div class="qt">{quote}</div><div class="src">{src}</div></div></div>')


def poster(kick, big, line, kufam=False):
    return full(f'<div class="poster"><div class="kick"><span>{kick}</span><i></i></div><div class="big{" kufam" if kufam else ""}">{big}</div>'
                f'<div class="line">{line}</div></div>', "dark")


def author_word():
    md = (BOOK / "00-كلمة-المؤلف.md").read_text(encoding="utf-8").replace("# كلمة المؤلف", "## كلمة المؤلف")
    return chapter(md, "الافتتاحية")


def contents(files):
    rows = []
    for f in files:
        m = re.search(r"^##\s+(.+)$", f.read_text(encoding="utf-8"), re.M)
        t = m.group(1)
        k, _, name = t.partition(":")
        rows.append(f'<div class="toc-row"><b>{k if name else ""}</b><span>{name.strip() or t}</span></div>')
    return (f'<section class="chap"><div class="chap-open"><p class="toc-p" style="text-indent:0">فصول المقدمة:</p>{"".join(rows)}</div></section>',
            band("المقدمة", "في صناعة الكلام"))


FIXED_CSS = "@page { size: %(w)smm %(h)smm; margin: 0; } html, body { margin: 0; }"


def doc(css, body, page_css, head=""):
    return (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>صناعة المتكلّم العربي</title>'
            f'<style>{css}</style><style>{CSS % dict(wrapw=0, wraph=0, head=head)}{C2.TEXT_CSS}{extra_css()}</style>'
            f'<style>{page_css}</style></head><body>{body}</body></html>')


def flow(css, piece, head):
    body, bandhtml = piece
    # the text flows on a transparent page laid over a full-bleed paper (or band) underlay,
    # so the paper colour reaches the trim instead of stopping at the text block
    return (doc(css, body, "html, body { background: transparent !important; }", head),
            doc(css, bandhtml, FIXED_CSS % dict(w=200, h=260)))


def folios(css, numbers):
    pages = "".join(f'<section style="position:relative;width:200mm;height:260mm;break-after:page">'
                    + (f'<div style="position:absolute;bottom:16mm;left:0;right:0;text-align:center;font:600 9.4pt Changa;color:#0C2766">'
                       f'{str(n).translate(AR)}</div>' if n else "") + '</section>' for n in numbers)
    return doc(css, pages, FIXED_CSS % dict(w=200, h=260) + " html, body { background: transparent !important; }")


def main():
    from pypdf import PdfReader, PdfWriter
    css = C2.fonts()
    wrap, wmm, hmm = C2.wrap(css, 1, 48.2, dpi=300)
    files = sorted((BOOK / "الافتتاحية").glob("*.md"))
    fixed = FIXED_CSS % dict(w=200, h=260)
    pieces = [("wrap", doc(css, wrap, FIXED_CSS % dict(w=wmm, h=hmm))),
              ("fixed", doc(css, P2.title_page(css).replace('class="pg', 'class="full'), fixed)),
              ("fixed", doc(css, P2.verse_page().replace('class="pg', 'class="full'), fixed)),
              ("flow", flow(css, author_word(), "كلمة المؤلف")),
              ("fixed", doc(css, poster("الافتتاحية", "المقدمة", "في صناعة الكلام: البيان في خلق الإنسان وفي الكتاب والسنة وعند علماء العربية، والفرق بين أن تعرف اللغة وأن تملكها، وأيّ عربيةٍ نتكلّم.", kufam=True), fixed)),
              ("flow", flow(css, contents(files[1:]), "المقدمة"))]
    tamhid = files[0].read_text(encoding="utf-8").replace("# المقدمة: في صناعة الكلام\n", "")
    pieces.append(("flow", flow(css, chapter(tamhid, "المقدمة"), "تمهيد")))
    for n, f in enumerate(files[1:], 1):
        md = f.read_text(encoding="utf-8")
        if f.name.startswith("05-"):
            pieces.append(("fixed", doc(css, heritage("سيبويه", "«فمنه مستقيمٌ حسن، ومُحال، ومستقيمٌ كذب، ومستقيمٌ قبيح، وما هو مُحالٌ كذب»",
                                                     "الكتاب، باب الاستقامة من الكلام والإحالة"), fixed)))
        if f.name.startswith("07-"):
            pieces.append(("fixed", doc(css, poster("المقدمة", "فأين الخلل؟", "ليس في علم المتعلّم، ولا في عقله، ولا في دينه؛ بل في صناعةٍ لم تُعلَّم تعليمًا مقصودًا: أن يصير ما يعرفه كلامًا يُقال، لمن يُقال له، حين يُقال."), fixed)))
        if f.name.startswith("11-"):
            pieces.append(("fixed", doc(css, heritage("من الصحيفة المنسوبة إلى بشر بن المعتمر",
                                                     "«فيجعل لكلّ طبقةٍ من ذلك كلامًا، ولكلّ حالةٍ من ذلك مقامًا»", "رواها الجاحظ في البيان والتبيين"), fixed)))
        title = re.sub(r"^الفصل [^:]+:\s*", "", re.search(r"^##\s+(.+)$", md, re.M).group(1))
        pieces.append(("flow", flow(css, chapter(md, f"الفصل {ORD[n]}"), title)))
    paper = B.render(doc(css, '<div style="width:200mm;height:260mm;background:var(--paper)"></div>', fixed), "opening-paper")
    w = PdfWriter()
    kinds = []
    for i, (kind, html) in enumerate(pieces):
        if kind == "flow":
            body, bandhtml = html
            r = PdfReader(str(B.render(body, f"opening-{i:02d}")))
            band = B.render(bandhtml, f"opening-{i:02d}-band")
            for j, pg in enumerate(r.pages):
                under = PdfReader(str(band if j == 0 else paper)).pages[0]
                under.merge_page(pg)
                w.add_page(under)
                kinds.append(kind)
            continue
        r = PdfReader(str(B.render(html, f"opening-{i:02d}")))
        for pg in r.pages:
            w.add_page(pg)
            kinds.append(kind)
    # folios: count from the title page; the case wrap and full-bleed pages carry none
    nums, n = [], 0
    for k in kinds:
        if k == "wrap":
            nums.append(0)
            continue
        n += 1
        nums.append(n if k == "flow" else 0)
    fr = PdfReader(str(B.render(folios(css, nums[1:]), "opening-folios")))
    for i, pg in enumerate(w.pages[1:]):
        if nums[i + 1]:
            pg.merge_page(fr.pages[i])
    w.add_metadata({"/Title": "صناعة المتكلّم العربي — المجلد الأول: الافتتاحية", "/Author": "أحمد بن إبراهيم السليمي"})
    w.write(str(OUT))
    print(OUT, len(w.pages), "pages")


def extra_css():
    """Styles the borrowed title and verse pages need (from proto2), scoped to .full pages."""
    keep = []
    for sel in (".tp-band", ".tp-sub", ".tp-desc", ".tp-vol", ".tp-auth", ".verse", ".kufi", ".gold-foil", ".qref"):
        for m in re.finditer(r"(?m)^" + re.escape(sel) + r"[^{]*\{[^}]*\}", P2.CSS.replace("%%", "%")):
            keep.append(m.group(0))
    return "\n".join(keep).replace("var(--read)", '"Scheherazade New"').replace("var(--sans)", '"IBM Plex Sans Arabic"').replace("var(--quran)", '"Amiri Quran"')


if __name__ == "__main__":
    main()
