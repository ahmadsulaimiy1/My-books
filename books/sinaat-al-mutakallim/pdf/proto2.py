#!/usr/bin/env python3
"""Reference pages, edition 1.2 revised (Bible, part seven, ch. 35–38 as corrected).

Scheherazade New for reading, Amiri / Amiri Quran for revelation, hadith, poetry and heritage,
Kufam (the book's cut, "Kufam SMA") for architecture, IBM Plex Sans Arabic for navigation.
The pages alternate richness and restraint: sapphire thresholds and transitions, a verse page,
a heritage page, the author's pages, prose, figure, comparison, dialogue, practice.

    python3 proto2.py     writes ../Volume-I_Revision-Prototypes.pdf
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import cover2 as C2  # noqa: E402
import proto as P1  # noqa: E402

OUT = HERE.parent / "Volume-I_Revision-Prototypes.pdf"
BOOK = HERE.parent / "book"
from paths import AUTHOR_WORD  # noqa: E402
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

CSS = r"""
@page { size: 170mm 240mm; margin: 0; }
@page wrap { size: %(wrapw)smm %(wraph)smm; margin: 0; }
:root {
  --ink: #1C1915; --ink-2: #4A443C; --ink-3: #7C7467; --paper: #FBF8F1; --paper-2: #F2ECDF; --paper-3: #EAE1CE;
  --sapphire: #0C2766; --sapphire-d: #081B4A; --sapphire-2: #2B4A8F; --gold: #C9A95C; --gold-l: #E4CB8C; --gold-ink: #8A6A1F; --crimson: #A8172E;
  --read: "Scheherazade New", "Amiri", serif; --heritage: "Amiri", serif; --quran: "Amiri Quran", "Amiri", serif;
  --kufi: "Kufam SMA", "Kufam", sans-serif; --sans: "IBM Plex Sans Arabic", sans-serif; --latin: "Source Serif 4", serif;
}
html, body { margin: 0; } body { background: #888; }
.pg { position: relative; width: 170mm; height: 240mm; background: var(--paper); overflow: hidden; break-after: page; color: var(--ink); direction: rtl; }
.wrap-pg { page: wrap; break-after: page; }
.dark { background: var(--sapphire); color: #EFE7D6; }
.gold-foil { background: linear-gradient(118deg, #A7884B 0%%, #D8BF88 14%%, #F3E6C0 28%%, #D2B67D 40%%, #9E7F44 52%%, #CDB078 70%%, #EEDDB0 84%%, #B39359 100%%); -webkit-background-clip: text; color: transparent; }
.kufi { font-family: var(--kufi); font-feature-settings: "liga" 0; }
.blk { position: absolute; top: 25mm; bottom: 30mm; right: 39mm; left: 39mm; }
.rh { position: absolute; top: 12.5mm; font: 400 7.4pt/1 var(--sans); color: var(--ink-3); display: flex; gap: 2.4mm; align-items: center; }
.rh b { font-weight: 500; color: var(--gold-ink); }
.rh.r { right: 39mm; } .rh.l { left: 39mm; }
.fo { position: absolute; bottom: 14mm; font: 500 9pt/1 var(--kufi); font-feature-settings: "liga" 0; color: var(--sapphire); }
.fo.r { right: 39mm; } .fo.l { left: 39mm; }
.fo::after { content: ""; position: absolute; top: 50%%; width: 7mm; border-top: .5pt solid var(--gold); }
.fo.r::after { right: calc(100%% + 2.4mm); } .fo.l::after { left: calc(100%% + 2.4mm); }
p { font: 400 13.2pt/1.85 var(--read); text-align: justify; margin: 0; }
p + p { text-indent: 6mm; }
p.flush { text-indent: 0; }
h2.t { font: 500 16pt/1.4 var(--kufi); font-feature-settings: "liga" 0; color: var(--sapphire); margin: 6.5mm 0 2.4mm; }
h2.t::after { content: ""; display: block; width: 12mm; border-top: .8pt solid var(--gold); margin-top: 2mm; }
h3.s { font: 700 13pt/1.5 var(--read); margin: 4mm 0 1mm; }
.en { font-family: var(--latin); font-size: .84em; direction: ltr; unicode-bidi: isolate; }
sup.fn { font: 600 7pt/0 var(--sans); color: var(--gold-ink); vertical-align: super; margin: 0 .4mm; }
.notes { position: absolute; bottom: 30mm; right: 39mm; left: 39mm; }
.notes::before { content: ""; display: block; width: 25mm; border-top: .5pt solid var(--gold); margin-bottom: 2mm; }
.notes div { font: 400 9.6pt/1.5 var(--read); color: var(--ink-2); display: flex; gap: 1.8mm; }
.notes div b { font: 600 7.4pt/1.9 var(--sans); color: var(--gold-ink); }
.notes .lat { direction: ltr; unicode-bidi: isolate; font-family: var(--latin); font-size: 8.4pt; text-align: left; }
ul.bl, ol.nums { margin: .6mm 0 1.2mm; padding: 0 6mm 0 0; }
ul.bl li, ol.nums li { font: 400 13.2pt/1.85 var(--read); text-align: justify; }
ul.bl { list-style: none; } ul.bl li { position: relative; }
ul.bl li::before { content: ""; position: absolute; right: -4.6mm; top: 4mm; width: 1.4mm; height: 1.4mm; transform: rotate(45deg); background: var(--gold); }
.q { font: 400 15pt/2 var(--quran); color: var(--sapphire); }
.qref { font: 400 8.2pt/1 var(--sans); color: var(--ink-3); margin-right: 1.4mm; white-space: nowrap; }
/* --- the sapphire band that opens a chapter or essay */
.band { position: absolute; top: 0; left: 0; right: 0; height: 92mm; background: var(--sapphire); color: #EFE7D6; }
.band .k { position: absolute; top: 34mm; right: 39mm; font: 500 8.6pt/1 var(--sans); color: var(--gold-l); display: flex; gap: 3mm; align-items: center; }
.band .k i { width: 9mm; border-top: .5pt solid var(--gold); display: inline-block; }
.band h1 { position: absolute; top: 44mm; right: 39mm; left: 39mm; margin: 0; font: 600 31pt/1.25 var(--kufi); font-feature-settings: "liga" 0; }
.band .dot { position: absolute; bottom: -1.3mm; right: 39mm; width: 2.6mm; height: 2.6mm; border-radius: 50%%; background: var(--crimson); }
.band + .blk { top: 104mm; }
.lead { font-size: 14.2pt; line-height: 1.8; color: var(--ink); }
/* --- author page */
.author p { font-size: 14pt; line-height: 1.9; }
.sig { margin-top: 7mm; text-align: left; }
.sig b { display: block; font: 600 14pt/1.4 var(--read); color: var(--sapphire); }
.sig span { font: 400 10pt/1.5 var(--read); color: var(--ink-2); }
/* --- verse page */
.verse { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
.verse .q { font-size: 27pt; line-height: 2.1; }
.verse .rule { width: 26mm; border-top: .7pt solid var(--gold); margin: 9mm auto; }
/* --- heritage page */
.her { position: absolute; top: 34mm; bottom: 34mm; right: 22mm; left: 22mm; border: .6pt solid var(--gold); padding: 3mm; }
.her-in { border: .3pt solid var(--gold); height: 100%%; box-sizing: border-box; padding: 12mm 9mm; display: flex; flex-direction: column; justify-content: center; background: var(--paper-2); }
.her .who { font: 500 9pt/1.4 var(--kufi); font-feature-settings: "liga" 0; color: var(--gold-ink); text-align: center; margin-bottom: 5mm; }
.her .quote { font: 400 17pt/2 var(--heritage); color: var(--sapphire); text-align: center; }
.her .src { font: 400 8.2pt/1.5 var(--sans); color: var(--ink-3); text-align: center; margin-top: 3mm; }
.her .sep { width: 3mm; height: 3mm; transform: rotate(45deg); background: var(--gold); margin: 9mm auto; }
.bayt { display: grid; grid-template-columns: 1fr 7mm 1fr; font: 400 13.4pt/2.1 var(--heritage); white-space: nowrap; color: var(--ink); }
.bayt span:first-child { text-align: left; } .bayt span:last-child { text-align: right; }
/* --- poster pages */
.poster { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; padding: 0 30mm; }
.poster .big { font: 700 64pt/1.2 var(--kufi); font-feature-settings: "liga" 0; }
.poster .line { font: 400 16pt/1.8 var(--read); color: #E7DFCE; max-width: 118mm; margin-top: 8mm; }
.poster .num { font: 500 9pt/1 var(--sans); color: var(--gold-l); margin-bottom: 8mm; display: flex; gap: 3mm; align-items: center; }
.poster .num i { width: 12mm; border-top: .5pt solid var(--gold); }
/* --- misconceptions */
.mis { display: grid; grid-template-columns: 14mm 1fr; gap: 0 4mm; padding: 3.2mm 0; border-bottom: .4pt solid #DCD2BE; }
.mis .n { font: 600 22pt/1 var(--kufi); font-feature-settings: "liga" 0; color: var(--gold); }
.mis b { display: block; font: 700 14pt/1.5 var(--read); color: var(--sapphire); }
.mis span { font: 400 12.4pt/1.7 var(--read); color: var(--ink-2); }
/* --- figures, comparison, script, practice (from the first prototype, retuned) */
figure { margin: 4mm 0 3mm; }
figcaption { font: 400 8.2pt/1.55 var(--sans); color: var(--ink-2); margin-top: 2.4mm; display: flex; gap: 2mm; }
figcaption b { font-weight: 600; color: var(--sapphire); white-space: nowrap; }
.fig-title { font: 500 12pt/1.4 var(--kufi); font-feature-settings: "liga" 0; color: var(--sapphire); margin-bottom: 3mm; }
.ctx { font: 400 8.2pt/1.7 var(--sans); color: var(--ink-2); background: var(--paper-2); padding: 1.6mm 3mm; margin: 2mm 0 4.4mm; display: flex; flex-wrap: wrap; gap: 0 5mm; border-right: 1.2pt solid var(--gold); }
.ctx b { font-weight: 600; color: var(--ink); }
.tier { display: grid; grid-template-columns: 26mm 1fr; gap: 0 4mm; margin: 0 0 4mm; align-items: start; }
.tier .lab { padding-top: 1.4mm; }
.tier .lab .g { font: 600 9pt/1.3 var(--kufi); font-feature-settings: "liga" 0; display: block; }
.tier .lab small { display: block; font: 400 7.4pt/1.4 var(--sans); color: var(--ink-3); margin-top: 1mm; }
.tier .lab .dots { display: flex; gap: 1mm; margin-top: 1.6mm; }
.tier .lab .dots i { width: 1.8mm; height: 1.8mm; transform: rotate(45deg); border: .5pt solid var(--tc); }
.tier .lab .dots i.on { background: var(--tc); }
.tier .say { font: 400 12.8pt/1.85 var(--read); text-align: justify; padding: 1.6mm 4mm; border-right: 1.4pt solid var(--tc); }
.tier.t1 { --tc: var(--crimson); } .tier.t1 .g { color: var(--crimson); }
.tier.t2 { --tc: #8A8378; } .tier.t2 .g { color: #5E584F; }
.tier.t3 { --tc: var(--sapphire); } .tier.t3 .g { color: var(--sapphire); }
.tier.t3 .say { background: var(--paper-2); }
table.cmp { width: 100%%; border-collapse: collapse; font: 400 8.6pt/1.55 var(--sans); margin-top: 1mm; }
table.cmp th { font-weight: 600; text-align: right; color: #F3ECDC; background: var(--sapphire); padding: 1.4mm 1.6mm; }
table.cmp td { border-bottom: .4pt solid #D8D0C0; padding: 1.3mm 1.6mm; vertical-align: top; color: var(--ink-2); }
table.cmp tr:nth-child(odd) td { background: #F6F1E6; }
table.cmp td:first-child { font-weight: 600; color: var(--ink); white-space: nowrap; }
.script { display: grid; grid-template-columns: 6mm 20mm 1fr; gap: 1.4mm 3mm; align-items: baseline; margin: 3mm 0 4mm; }
.script .n { font: 400 7.4pt/1 var(--sans); color: var(--gold-ink); text-align: left; direction: ltr; }
.script .who { font: 600 9pt/1.5 var(--kufi); font-feature-settings: "liga" 0; color: var(--sapphire); }
.script .who.b { color: var(--ink-2); }
.script .say { font: 400 13pt/1.8 var(--read); }
.script .dir { color: var(--ink-3); font-size: 11pt; }
.prac-h { background: var(--sapphire); color: #F1EADA; margin: -25mm -39mm 6mm; padding: 16mm 39mm 6mm; display: flex; align-items: baseline; justify-content: space-between; }
.prac-h h2 { font: 600 20pt/1.3 var(--kufi); font-feature-settings: "liga" 0; margin: 0; }
.prac-h span { font: 500 8.4pt/1 var(--sans); color: var(--gold-l); }
.card { border: .6pt solid #D6CBB4; background: #FFFDF8; padding: 3mm 4mm; margin-bottom: 3.2mm; display: grid; grid-template-columns: 11mm 1fr; gap: 0 3mm; position: relative; }
.card::before { content: ""; position: absolute; right: -.6pt; top: -.6pt; bottom: -.6pt; width: 1.4pt; background: var(--gold); }
.card .k { font: 600 20pt/1 var(--kufi); font-feature-settings: "liga" 0; color: var(--gold); padding-top: 1mm; }
.card .tag { font: 600 7.8pt/1.4 var(--sans); color: var(--gold-ink); }
.card .tag i { font-style: normal; color: var(--ink-3); font-weight: 400; margin-right: 2mm; }
.card p { font-size: 12pt; line-height: 1.8; text-indent: 0; }
.mastery h3 { font: 600 9.4pt/1.4 var(--sans); color: var(--sapphire); margin: 4mm 0 1.6mm; }
/* --- title page */
.tp-band { position: absolute; top: 0; left: 0; right: 0; height: 138mm; background: var(--sapphire); }
.tp-sub { position: absolute; top: 150mm; right: 24mm; left: 24mm; font: 400 19pt/1.4 var(--read); color: var(--ink); }
.tp-desc { position: absolute; top: 164mm; right: 24mm; left: 44mm; font: 400 10pt/1.7 var(--sans); color: var(--ink-2); }
.tp-vol { position: absolute; top: 106mm; right: 24mm; color: var(--gold-l); font: 500 8.6pt/1.6 var(--sans); }
.tp-auth { position: absolute; bottom: 26mm; right: 24mm; }
.tp-auth small { font: 400 8pt/1.5 var(--sans); color: var(--ink-3); display: block; }
.tp-auth b { font: 600 17pt/1.5 var(--read); color: var(--sapphire); display: block; }
.tp-auth .kn { font: 400 11.5pt/1.5 var(--read); font-style: normal; color: var(--gold-ink, #8A6A1F); display: block; margin-top: 1mm; }
.tp-auth span { font: 400 10.4pt/1.5 var(--read); color: var(--ink-2); }
"""


def page(inner, cls=""):
    return f'<section class="pg {cls}">{inner}</section>'


def rh(side, text, bold=""):
    return f'<div class="rh {side}">{f"<b>{bold}</b>" if bold else ""}{text}</div>'


def fo(n, side):
    return f'<div class="fo {side}">{str(n).translate(AR)}</div>'


def md_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"\[\^(\d+)\]", lambda m: f'<sup class="fn">{m.group(1).translate(AR)}</sup>', s)
    s = re.sub(r"﴿([^﴾]+)﴾\s*\(([^)]+)\)", r'<span class="q">﴿\1﴾</span><span class="qref">(\2)</span>', s)
    return s


def essay():
    # the short essay these prototypes were set from was replaced by the treatise in الافتتاحية/;
    # read it from the commit that last carried it so the prototype set stays reproducible
    import subprocess
    md = subprocess.run(["git", "show", "e52c19a:books/sinaat-al-mutakallim/book/00-بين-يدي-الكتاب.md"],
                        cwd=BOOK, capture_output=True, text=True, check=True).stdout
    secs = re.split(r"^## ", md, flags=re.M)[1:]
    out = {}
    for s in secs:
        title, body = s.split("\n", 1)
        body = re.sub(r"^\[\^\d+\]:.*$", "", body, flags=re.M)
        out[title.strip()] = [b.strip() for b in body.split("\n\n") if b.strip()]
    return out


# --------------------------------------------------------------------------- pages

def title_page(css, volume=None):
    """volume: the volume's block (frontmatter.title_volume); the prototype's line stands in when none is given."""
    logo = C2.Logotype(css, width=122.0)
    svg, bottom = logo.svg(146.0, 50.0, shadow=True)
    return page(f'''<div class="tp-band"></div>
<svg viewBox="0 0 170 240" style="position:absolute;inset:0;width:170mm;height:240mm"><defs>{C2.K.gold_defs()}</defs>{svg}
<rect x="0" y="137.6" width="170" height="0.5" fill="url(#foil)"/><circle cx="146" cy="137.85" r="1.3" fill="#A8172E"/></svg>
{volume or '<div class="tp-vol">المجلد الأول<span class="kufi" style="display:block;font-size:22pt;line-height:1.3;color:#E4CB8C;font-weight:500">التأسيس</span></div>'}
<div class="tp-sub">من سلامة اللسان إلى حسن البيان</div>
<div class="tp-desc">منهجٌ شامل في النطق والتعبير والخطاب وآداب التواصل والملكة الشفهية</div>
<div class="tp-auth"><small>تأليف</small><i class="kn">أبو عبد الله جلال الدين</i><b>أحمد بن إبراهيم بن عبد السلام السليمي</b><span>غفر الله له ولوالديه ولجميع المسلمين</span></div>''')


def verse_page():
    return page('''<div class="verse">
<div class="q">﴿ٱلرَّحْمَٰنُ ۝١ عَلَّمَ ٱلْقُرْءَانَ ۝٢<br>خَلَقَ ٱلْإِنسَٰنَ ۝٣ عَلَّمَهُ ٱلْبَيَانَ ۝٤﴾</div>
<div class="rule"></div><div class="qref" style="font-size:9pt">سورة الرحمن: ١–٤</div></div>''')


def author_page():
    md = AUTHOR_WORD.read_text(encoding="utf-8")
    paras = [p.strip() for p in md.split("\n\n") if p.strip() and not p.startswith("#")]
    body = "".join(f'<p class="{"flush" if i == 0 else ""}">{md_inline(x)}</p>' for i, x in enumerate(paras[:3]))
    return page(f'''<div class="band" style="height:70mm"><div class="k"><span>الافتتاحية</span><i></i></div>
<h1 style="top:40mm">كلمة المؤلف</h1><div class="dot"></div></div>
<div class="blk author" style="top:84mm">{body}</div>{fo(9, "l")}''')


def essay_opener(E):
    s = E["يعرف العربية ولا يتكلّم بها"]
    body = f'<p class="lead flush">{md_inline(s[0])}</p>' + "".join(f"<p>{md_inline(x)}</p>" for x in s[1:3])
    return page(f'''<div class="band"><div class="k"><span>الافتتاحية</span><i></i><span>في صناعة الكلام</span></div>
<h1>بين يدي الكتاب</h1><div class="dot"></div></div><div class="blk" style="top:104mm">
<h2 class="t" style="margin-top:0">يعرف العربية ولا يتكلّم بها</h2>{body}</div>{fo(13, "l")}''')


def quran_page(E):
    s = E["القول في القرآن"]
    lis = re.findall(r"^- \*\*(.+?)\*\*\s*(.+)$", s[1], re.M)
    rows = "".join(f'<div class="mis"><div class="n">{str(i + 1).translate(AR)}</div><div><b>{a}</b><span>{md_inline(b)}</span></div></div>'
                   for i, (a, b) in enumerate(lis[:5]))
    return page(f'''{rh("r", "بين يدي الكتاب")}<div class="blk"><h2 class="t" style="margin-top:0">القول في القرآن</h2>
<p class="flush">{md_inline(s[0])}</p>{rows}</div>{fo(18, "r")}''')


def heritage_page():
    return page(f'''<div class="her"><div class="her-in">
<div class="who">الجاحظ</div>
<div class="quote">«والبيانُ اسمٌ جامعٌ لكلِّ شيءٍ كشفَ لك قِناعَ المعنى، وهتكَ الحجابَ دون الضمير، حتى يُفضيَ السامعُ إلى حقيقته»</div>
<div class="src">البيان والتبيين، الجزء الأول</div>
<div class="sep"></div>
<div class="who">زهير بن أبي سلمى</div>
<div class="bayt"><span>وكائنْ ترى من صامتٍ لكَ مُعجِبٍ</span><span></span><span>زيادتُه أو نقصُه في التكلّمِ</span></div>
<div class="bayt"><span>لسانُ الفتى نصفٌ ونصفٌ فؤادُهُ</span><span></span><span>فلم يبقَ إلا صورةُ اللحمِ والدمِ</span></div>
<div class="src">من المعلّقة</div></div></div>''')


def poster_page():
    return page('''<div class="poster"><div class="num"><span>بين يدي الكتاب</span><i></i></div>
<div class="big gold-foil">فأين الخلل؟</div>
<div class="line">ليس في علم المتعلّم، ولا في عقله، ولا في دينه؛ بل في صناعةٍ لم تُعلَّم تعليمًا مقصودًا: أن يصير ما يعرفه كلامًا يُقال، لمن يُقال له، حين يُقال.</div></div>''', "dark")


def misconceptions_page(E):
    s = E["تصوّراتٌ تحتاج إلى تصحيح"]
    lis = re.findall(r"^- \*\*(.+?)\*\*\s*(.+)$", s[1], re.M)
    rows = "".join(f'<div class="mis"><div class="n">{str(i + 1).translate(AR)}</div><div><b>{a}</b><span>{md_inline(b)}</span></div></div>'
                   for i, (a, b) in enumerate(lis))
    return page(f'''{rh("l", "بين يدي الكتاب")}<div class="blk"><h2 class="t" style="margin-top:0">تصوّراتٌ تحتاج إلى تصحيح</h2>
<p class="flush">{md_inline(s[0])}</p>{rows}</div>{fo(23, "l")}''')


def threshold():
    return page('''<div class="poster" style="align-items:center;text-align:center;padding:0 24mm">
<div class="num" style="justify-content:center"><i></i><span>الجزء الأول</span><i></i></div>
<div class="big gold-foil" style="font-size:92pt;font-weight:600">التأسيس</div>
<div class="line" style="margin-inline:auto">أن يستقيم اللسان قبل أن يُطلب منه البيان: من أيّ عربيةٍ نتكلّم، إلى صحة الصوت، إلى استقامة الجملة.</div>
<div style="width:2.6mm;height:2.6mm;border-radius:50%;background:#A8172E;margin:12mm auto 0"></div></div>''', "dark")


def chapter_opener(blocks):
    return page(f'''<div class="band"><div class="k"><span>المدخل</span><i></i><span>الفصل الأول</span></div>
<h1>العربية ومستوياتها</h1><div class="dot"></div></div><div class="blk" style="top:104mm">
<p class="lead flush">{P1.md_inline(blocks[0])}</p><p>{P1.md_inline(blocks[1])}</p></div>{fo(31, "l")}''')


def figure_page(blocks):
    sec = [b for b in blocks if b.startswith("## المستويات التي")][0]
    i = blocks.index(sec)
    svg = P1.spectrum_svg().replace("#0E2A6B", "#0C2766")
    return page(f'''{rh("l", "المدخل: ما العربية التي نتكلّم بها؟")}<div class="blk">
<h2 class="t" style="margin-top:0">المستويات التي يعمل بها هذا الكتاب</h2><p class="flush">يعمل الكتاب بخمسة مستويات، يرسمها الشكل الآتي على طيفٍ واحد.</p>
<figure><div class="fig-title">طيف العربية</div>{svg}
<figcaption><b>الشكل ١</b><span>مستويات العربية مواضعُ على طيفٍ متصل لا غرفٌ منفصلة. يتنقّل المتكلّم الواحد بينها بحسب المقام والمخاطَب والموضوع، ويعمل هذا الكتاب في الفصحى المعاصرة بشقّيها المكتوب والمنطوق.</span></figcaption></figure>
{P1.flow(blocks[i + 3:i + 4])}</div>{fo(35, "l")}''')


def comparison_page():
    html = P1.comparison_page()
    inner = html[html.index('<div class="blk">'):html.rindex('<div class="fo')]
    for t, dots, tag in (("t1", 1, "غير الناجحة"), ("t2", 2, "المقبولة"), ("t3", 3, "الناجحة")):
        inner = re.sub(rf'<div class="tier {t}"><div class="lab">{tag}<small>(.*?)</small></div>',
                       lambda m: (f'<div class="tier {t}"><div class="lab"><span class="g">{tag}</span><small>{m.group(1)}</small>'
                                  f'<span class="dots">{"".join("<i class=on></i>" if k < dots else "<i></i>" for k in range(4))}</span></div>'),
                       inner)
    inner = inner.replace('<h2 class="t">', '<h2 class="t" style="margin-top:0">')
    return page(f'{rh("l", "الفصل الأول: الكلام وأركانه", "الباب الأول")}{inner}{fo(55, "l")}')


def dialogue_page():
    html = P1.dialogue_page()
    inner = html[html.index('<div class="blk">'):html.rindex('<div class="fo')]
    inner = inner.replace('<h2 class="t">', '<h2 class="t" style="margin-top:0">')
    return page(f'{rh("r", "صناعة المتكلّم العربي")}{inner}{fo(108, "r")}')


def practice_page():
    html = P1.practice_page()
    inner = html[html.index('<div class="blk">'):html.rindex('<div class="fo')]
    inner = inner.replace('<div class="prac-h"><h2>تدريبات الفصل</h2><span>أربع مهام</span></div>',
                          '<div class="prac-h"><h2>تدريبات الفصل</h2><span>أربع مهام، ومعيار إتقان</span></div>')
    return page(f'{inner}{fo(67, "l")}')


def main():
    css = C2.fonts()
    body_wrap, wmm, hmm = C2.wrap(css, 1, 48.2, dpi=300)
    E = essay()
    blocks, notes = P1.chapter_text()
    pages = [f'<section class="wrap-pg">{body_wrap}</section>', title_page(css), verse_page(), author_page(),
             essay_opener(E), quran_page(E), heritage_page(), poster_page(), misconceptions_page(E), threshold(),
             chapter_opener(blocks), figure_page(blocks), comparison_page(), dialogue_page(), practice_page()]
    html = (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>صناعة المتكلّم العربي: عيّنات الإصدار ١٫٢</title>'
            f'<style>{css}</style><style>{CSS % dict(wrapw=wmm, wraph=hmm)}{C2.TEXT_CSS}</style></head><body>{"".join(pages)}</body></html>')
    pdf = B.render(html, "proto12b")
    OUT.write_bytes(Path(pdf).read_bytes())
    print(OUT)


if __name__ == "__main__":
    main()
