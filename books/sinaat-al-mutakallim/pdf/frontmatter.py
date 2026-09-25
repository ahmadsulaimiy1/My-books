"""The front matter and colophon of each volume, in the Al-Ihsān Editorial House style (Bible, part fourteen).

Each page has its own function and rhythm: the half-title and the map of the volumes are quiet; the title page is
strong; the imprint is a typographic table; the rights page is sober; the colophon closes the volume. The publisher
appears on the title page (its mark only), the imprint, the rights page and the colophon, and nowhere else.

What the author or the publisher has not decided (dedication, publisher's word, rights holder, city, ISBN, legal
deposit) is not printed: its line is left out, never filled with a placeholder (Bible, ch. 99).
"""
from __future__ import annotations

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

TITLE = "صناعة المتكلّم العربي"
SUBTITLE = "من سلامة اللسان إلى حسن البيان"
AUTHOR_SHORT = "أحمد بن إبراهيم السليمي"                                   # the cover form (Bible, ch. 71)
AUTHOR_KUNYA = "أبو عبد الله جلال الدين"
AUTHOR_LONG = "أحمد بن إبراهيم بن عبد السلام السليمي"                       # the title-page form, without the tribe
EDITION = "الطبعة الأولى"
YEAR = "١٤٤٨هـ / ٢٠٢٦م"
PUBLISHER_AR = "دار الإحسان للتصميم والنشر"
PUBLISHER_EN = "Al-Ihsān Design & Publishing House"
PHONES = ["+234 903 395 5872", "+234 903 344 6273"]
EMAIL = "al-ihsan.design@gmail.com"
# decided by the author or the publisher; None means "not yet decided": the line is not printed
# the warning on the names in the examples, printed on the rights page of every volume (Bible, ch. 112d §٤)
FICTIONAL_NAMES = ("الأسماء الواردة في أمثلة هذا الكتاب وحواراته أسماءٌ افتراضية، وُضعت لتمثيل المواقف التعليمية، "
                   "ولا يُقصد بها أشخاصٌ بأعيانهم؛ وما ذُكر فيها من مدنٍ فهو إطارٌ للموقف لا غير.")
RIGHTS_HOLDER = "حقوق التأليف للمؤلف، وحقوق الطبع والنشر لدار الإحسان للتصميم والنشر"
CITY = None
# the ISBNs are the publisher's to issue: one for each volume, and one for the set if the publisher prints it on every
# volume; the legal deposit likewise. None: not yet issued, and the line is not printed (the release check reports it)
ISBN = {n: None for n in range(1, 12)}
ISBN_SET = None
DEPOSIT = {n: None for n in range(1, 12)}

# the series in eleven volumes: ten in four stages and thirteen babs, then the reference (Bible, chs. 112c–112و).
# (ordinal, name, what it holds, stage, its babs); the babs' numbers are set in Amiri (<b>)
VOLUMES = [("الأول", "الأصول", "المقدمة والمدخل، ثم أسس الكلام: معاييره، والمتكلّم، والبيان، وأصل المقام، وأصل السماع", "التأسيس", "الباب <b>١</b>"),
           ("الثاني", "اللسان", "المخارج والصفات، والأصوات الحرجة، والوقف والصوت؛ وبرنامج النطق اليومي", "التأسيس", "الباب <b>٢</b>"),
           ("الثالث", "العبارة", "الجملة العربية الطبيعية: الإعراب، والترجمة الحرفية، والحشو، واختيار الكلمة", "التأسيس", "الباب <b>٣</b>"),
           ("الرابع", "البيان", "ترتيب الكلام: الافتتاح والتعريف بالنفس، والانتقال والخاتمة، والبلاغة التطبيقية", "التأسيس", "الباب <b>٤</b>"),
           ("الخامس", "المقام", "من يتكلّم، ولمن، ولماذا، وأين، ومتى، وكيف؛ ومختبر المقام", "التواصل", "الباب <b>٥</b>"),
           ("السادس", "الأدب", "السلام والشكر، والطلب والرفض، والاعتذار والتهنئة، وأدب الخلاف", "التواصل", "الباب <b>٦</b>"),
           ("السابع", "الحوار", "السؤال والجواب، والاستيضاح والمداخلة، والإقناع والمناظرة، والنقد والنصيحة", "التواصل", "الباب <b>٧</b>"),
           ("الثامن", "المجالس والمنبر", "مجلس العلم ومجالس الجامعة، ثم الخطبة والمحاضرة والكلمة وعرض البحث", "المنصّات", "البابان <b>٨</b> و<b>٩</b>"),
           ("التاسع", "المؤسسة", "المقابلة، وإدارة الاجتماع، وخطاب المدير والموظف", "المنصّات", "الباب <b>١٠</b>"),
           ("العاشر", "التمكين", "الإعلام والتقديم، والخطاب الرسمي والتفاوض، ثم الملكة: الارتجال والأداء الختامي", "التمكين", "الأبواب <b>١١–١٣</b>"),
           ("الحادي عشر", "مرجع المتكلّم العربي", "بنك الأخطاء، والمعجم التطبيقي للتعبيرات، ومعجم أخطاء الترجمة الحرفية، والنماذج الكاملة، "
            "ثم المسرد والمصادر والفهارس العامة للسلسلة", "", "")]
REFERENCE_SUB = "بنك الأخطاء والتعبيرات والنماذج"
STAGES = {"التأسيس": "المرحلة الأولى", "التواصل": "المرحلة الثانية", "المنصّات": "المرحلة الثالثة", "التمكين": "المرحلة الرابعة"}
# the stage's mark on the spine and on the map: as many dots as its number (Bible, ch. 111 §٦)
STAGE_DOTS = {"التأسيس": 1, "التواصل": 2, "المنصّات": 3, "التمكين": 4}
# what each stage adds, in the words of chapter seventeen (§١)
STAGE_LINE = {"التأسيس": "أداة المتكلّم قبل أن يقف أمام أحد: المعيار، والصوت، والجملة، والترتيب",
              "التواصل": "يدخل المخاطَب: المقام، ثم العلاقة، ثم الكلام المتبادل",
              "المنصّات": "تتّسع الدائرة: الجماعة، ثم المؤسسة التي تحاسب على الكلام",
              "التمكين": "من صوابٍ يُستحضر بالانتباه إلى صوابٍ يجري بالعادة"}
COMPANIONS = ("بنك الاختبارات ودليل المعلّم", "سكريبتات الحلقات")


def volume_line(n):
    """«المجلد الأول: الأصول»."""
    w, nm = VOLUMES[n - 1][:2]
    return f"المجلد {w}: {nm}"


CSS = r"""
/* ---------------------------------------------------------------- front matter (Bible, part fourteen) */
.fm { position: absolute; inset: 0; background: var(--paper); color: var(--ink); }
.diamond { display: inline-block; width: 1.5mm; height: 1.5mm; background: var(--gold); transform: rotate(45deg); }
.grule { display: flex; align-items: center; justify-content: center; gap: 2.2mm; }
.grule i { display: block; width: 14mm; border-top: .45pt solid var(--gold); }
/* the publisher's mark: a typographic signature, not a commercial logo */
.imark { display: flex; flex-direction: column; align-items: center; gap: 1.4mm; }
.imark .w { font: 600 15pt/1 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--sapphire); letter-spacing: .4pt; }
.imark .e { font: 400 6.4pt/1 "Source Serif 4"; letter-spacing: 1.6pt; text-transform: uppercase; color: var(--ink-3); direction: ltr; }
.imark.on-dark .w { color: var(--gold-l); } .imark.on-dark .e { color: #C9C2B2; }
/* 1. half-title: quiet */
.ht { position: absolute; top: 56mm; left: 0; right: 0; text-align: center; }
.ht .t { font: 600 23pt/1.5 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--sapphire); }
.ht .s { font: 400 12.5pt/1.6 "Scheherazade New"; color: var(--ink-2); margin-top: 2mm; }
.ht .grule { margin: 9mm 0 8mm; }
.ht .a { font: 300 10.5pt/1.5 "Changa"; color: var(--ink-2); }
.ht .v { position: absolute; top: 108mm; left: 0; right: 0; font: 300 9pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .6pt; }
/* 2. the series map, a spread (Bible, ch. 111 §٥): the right-hand page opens it with the title and the first two
   stages, the left-hand page carries the last two and, off the path, the reference. Each volume carries its spine's
   marks: its number in Amiri within a gold rhombus, its stage in dots; the volume in hand has the rhombus filled */
.sm { position: absolute; top: 0; bottom: 0; z-index: 0; }
.sm.r { right: 22mm; left: 16mm; }
.sm.l { right: 16mm; left: 22mm; }
.sm-rule { position: absolute; top: 25.2mm; border-top: .45pt solid var(--gold); }
.sm.r .sm-rule { right: 0; left: -16mm; }
.sm.l .sm-rule { right: -16mm; left: 0; }
.sm.l .sm-rule::after { content: ""; position: absolute; left: -1.1mm; top: -1.35mm; width: 2.2mm; height: 2.2mm; transform: rotate(45deg); background: var(--gold); }
.sm-k { position: absolute; top: 23.4mm; right: 0; background: var(--paper); padding: 0 0 0 3mm; font: 300 10pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .5pt; }
.sm-h { position: absolute; top: 32mm; right: 0; left: 0; }
.sm-h .t { font: 600 24pt/1.3 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--sapphire); }
.sm-h .n { font: 400 13.4pt/1.4 "Changa"; color: var(--gold-ink); margin-top: 1.2mm; }
.sm-h .p { font: 400 11.2pt/1.7 "Scheherazade New"; color: var(--ink-2); margin-top: 2.6mm; max-width: 118mm; }
.sm-col { position: absolute; right: 0; left: 0; }
.sm.r .sm-col { top: 74mm; }
.sm.l .sm-col { top: 36mm; }
.smv, .sms { display: grid; grid-template-columns: 14mm 1fr; column-gap: 4mm; position: relative; }
.smv::before, .sms::before { content: ""; position: absolute; right: 7mm; top: 0; bottom: 0; border-right: .5pt solid var(--gold); }
.sm-col > .sms:first-child::before { top: 3.9mm; }
.sm-col > .last::before { bottom: auto; height: 6.9mm; }
.smv { padding: 1.7mm 0 2.1mm; }
.smv .b { position: relative; }
.smv .b i, .smv .b span { position: absolute; top: 1.6mm; right: 3.4mm; width: 7.2mm; height: 7.2mm; box-sizing: border-box; }
.smv .b i { transform: rotate(45deg); border: .6pt solid var(--gold); background: var(--paper); }
.smv .b span { display: flex; align-items: center; justify-content: center; font: 700 11.2pt/1 "Amiri"; color: var(--sapphire); padding-top: .5mm; }
.smv.here::after { content: ""; position: absolute; top: .4mm; bottom: .6mm; right: -3mm; left: -3mm; background: var(--paper-2); border-right: 1.2pt solid var(--gold); z-index: -1; }
.smv.here .b i { background: var(--gold); border-color: var(--gold); }
.smv .l1 { display: flex; align-items: baseline; gap: 2.4mm; }
.smv .w { font: 300 9pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .3pt; }
.smv .nm { font: 600 14.4pt/1.35 "Changa"; color: var(--sapphire); }
.smv .sd { display: inline-flex; gap: 1mm; align-self: center; margin-top: .6mm; }
.smv .sd i { width: 1.2mm; height: 1.2mm; border-radius: 50%%; background: var(--gold); }
.smv .tg { margin-right: auto; font: 400 8pt/1 "IBM Plex Sans Arabic"; color: var(--ink-3); }
.smv .tg b { font: 700 9.4pt/1 "Amiri"; color: var(--ink-2); }
.smv .d { font: 400 10.1pt/1.5 "Scheherazade New"; color: var(--ink-2); margin-top: .1mm; text-wrap: pretty; }
.sms { padding: 5.2mm 0 .8mm; }
.sm-col > .sms:first-child { padding-top: 0; }
.sms .b { position: relative; }
.sms .b i { position: absolute; top: 2.7mm; right: 5.8mm; width: 2.4mm; height: 2.4mm; border-radius: 50%%; background: var(--sapphire); }
.sms .l1 { display: flex; align-items: baseline; gap: 2.4mm; }
.sms .o { font: 300 9pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .4pt; }
.sms b { font: 700 13pt/1.35 "Changa"; color: var(--sapphire); }
.sms .f { font: 400 10pt/1.45 "Scheherazade New"; color: var(--ink-3); }
.smr { margin-top: 11mm; border-top: .6pt solid var(--gold); padding-top: .9mm; }
.smr::before { content: ""; display: block; border-top: .3pt solid var(--gold); margin-bottom: 5mm; }
.smr .k { font: 300 9pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .4pt; margin-bottom: 1mm; }
.smr .smv::before { content: none; }
.smr .smv .b i { outline: .3pt solid var(--gold); outline-offset: .8mm; }
.smr .sub { font: 300 11.6pt/1.4 "Changa"; color: var(--ink-2); }
.smr .x { font: 400 8.6pt/1.6 "IBM Plex Sans Arabic"; color: var(--gold-ink); margin-top: 1.6mm; display: flex; gap: 2.2mm; align-items: center; }
.smr .x i { width: 1.9mm; height: 1.9mm; border: .5pt solid var(--gold-ink); transform: rotate(45deg); box-sizing: border-box; flex: none; }
.smc { margin-top: 8mm; font: 400 10.4pt/1.7 "Scheherazade New"; color: var(--ink-2); }
.sml { position: absolute; bottom: 22mm; right: 0; left: 0; display: flex; flex-wrap: wrap; gap: 1.6mm 6mm; font: 400 8pt/1.4 "IBM Plex Sans Arabic"; color: var(--ink-3); border-top: .3pt solid #DCD6CA; padding-top: 2.6mm; }
.sml span { display: inline-flex; align-items: center; gap: 1.8mm; }
.sml .f, .sml .e { width: 2.1mm; height: 2.1mm; transform: rotate(45deg); box-sizing: border-box; }
.sml .f { background: var(--gold); } .sml .e { border: .5pt solid var(--gold-ink); }
.sml .dt { display: inline-flex; gap: .8mm; } .sml .dt i { width: 1.1mm; height: 1.1mm; border-radius: 50%%; background: var(--gold); }
/* 3. the title page's volume: number, name, and the line of its stage and babs (Bible, ch. 111 §٥) */
.tpv { position: absolute; top: 96mm; right: 24mm; left: 24mm; }
.tpv .w { font: 400 11pt/1.3 "Changa"; color: var(--gold-l); letter-spacing: .4pt; }
.tpv .nm { font: 700 25pt/1.3 "Changa"; color: #F4ECD9; margin-top: .6mm; }
.tpv .ln { font: 400 8.6pt/1.5 "IBM Plex Sans Arabic"; color: #C9C2B2; margin-top: 1.6mm; }
/* 4. imprint: a typographic table */
.im { position: absolute; top: 30mm; right: 24mm; left: 24mm; }
.im h4 { font: 300 10pt/1 "Changa"; color: var(--gold-ink); margin: 0 0 7mm; display: flex; gap: 3mm; align-items: center; }
.im h4 i { flex: 1; border-top: .4pt solid var(--gold); }
.im-row { display: grid; grid-template-columns: 30mm 1fr; gap: 4mm; padding: 2.6mm 0; border-bottom: .3pt solid #E0DBD0; }
.im-row .l { font: 400 8.4pt/1.7 "IBM Plex Sans Arabic"; color: var(--ink-3); }
.im-row .v { font: 400 11.2pt/1.65 "Scheherazade New"; color: var(--ink); }
.im-row .v small { display: block; font: 400 8.2pt/1.5 "Source Serif 4"; color: var(--ink-3); direction: ltr; text-align: right; }
.im-pub { margin-top: 13mm; display: grid; grid-template-columns: auto 1fr; gap: 8mm; align-items: center; }
.im-pub .c { font: 400 8.4pt/1.9 "IBM Plex Sans Arabic"; color: var(--ink-2); border-right: .4pt solid var(--gold); padding-right: 6mm; }
.im-pub .c .ltr { direction: ltr; unicode-bidi: isolate; font-family: "Source Serif 4"; font-size: 8.6pt; letter-spacing: .2pt; }
/* 5. rights and editions: sober */
.rt { position: absolute; bottom: 28mm; right: 24mm; left: 24mm; }
.rt .c { font: 600 9.8pt/1.8 "Changa"; color: var(--sapphire); margin-bottom: 4mm; }
.rt p { font: 400 9.4pt/1.85 "Scheherazade New"; color: var(--ink-2); text-align: justify; margin: 0 0 2.6mm; text-indent: 0; }
.rt .h2 { font: 400 9.6pt/1.8 "Scheherazade New"; color: var(--ink); margin: -2mm 0 4mm; }
.rt .ed { margin-top: 8mm; border-top: .4pt solid var(--gold); padding-top: 3.4mm; }
.rt .ed .h { font: 300 8.6pt/1 "Changa"; color: var(--gold-ink); margin-bottom: 2.4mm; }
.rt .ed-row { display: grid; grid-template-columns: 30mm 1fr; gap: 4mm; font: 400 9pt/1.7 "IBM Plex Sans Arabic"; color: var(--ink-2); }
.rt .top { position: absolute; top: -150mm; right: 0; left: 0; text-align: center; }
/* 6. deliberate white */
.blank { position: absolute; inset: 0; background: var(--paper); }
/* contents: several levels */
.toc2 h2.tt { font: 700 22pt/1.3 "Changa"; color: var(--sapphire); margin: 0 0 1.6mm; }
.toc2 .tsub { font: 300 10pt/1.4 "Changa"; color: var(--gold-ink); margin-bottom: 9mm; }
.toc2 .part { font: 600 10.4pt/1 "Changa"; color: var(--gold-ink); margin: 7mm 0 2.4mm; display: flex; gap: 3mm; align-items: center; letter-spacing: .3pt; break-after: avoid; }
.toc2 .part i { flex: 1; border-top: .4pt solid var(--gold); }
.toc2 .e { display: grid; grid-template-columns: 21mm 1fr 12mm; gap: 0 3mm; align-items: baseline; padding: 1.7mm 0 1.9mm; break-inside: avoid; }
.toc2 .e .k { font: 300 8.6pt/1.4 "Changa"; color: var(--ink-3); }
.toc2 .e .t { font: 600 12.6pt/1.45 "Changa"; color: var(--sapphire); }
.toc2 .e .p { font: 700 11pt/1 "Amiri"; color: var(--sapphire); text-align: left; }
.toc2 .e .s { grid-column: 2 / 4; font: 400 9.4pt/1.7 "Scheherazade New"; color: var(--ink-2); margin-top: .6mm; }
.toc2 .e .s b { font: 700 8.6pt "Amiri"; color: var(--gold-ink); margin: 0 .6mm 0 1.4mm; }
.toc2 .e.lite .t { font: 500 11.6pt/1.45 "Changa"; color: var(--ink); }
/* symbols and terms */
.sy h2.tt { font: 700 20pt/1.3 "Changa"; color: var(--sapphire); margin: 0 0 8mm; }
.sy-row { display: grid; grid-template-columns: 26mm 1fr; gap: 5mm; padding: 2.5mm 0; border-bottom: .3pt solid #E0DBD0; align-items: baseline; }
.sy-row .m { font: 400 13pt/1.5 "Amiri"; color: var(--sapphire); text-align: center; }
.sy-row .m.s { font: 600 10pt/1.5 "Changa"; }
.sy-row .d { font: 400 11pt/1.7 "Scheherazade New"; color: var(--ink-2); }
.sy h3 { font: 600 11.6pt/1.3 "Changa"; color: var(--gold-ink); margin: 9mm 0 2mm; display: flex; gap: 3mm; align-items: center; }
.sy h3 i { flex: 1; border-top: .4pt solid var(--gold); }
.sy .sy-note { margin-top: 7mm; padding-top: 3mm; border-top: .3pt solid #DCD6CA; font: 400 10.6pt/1.75 "Scheherazade New"; color: var(--ink-2); text-indent: 0; text-align: right; }
.sy-scale { display: grid; grid-template-columns: 10mm 26mm 1fr; gap: 0 4mm; padding: 1.8mm 0; border-bottom: .3pt solid #E0DBD0; align-items: baseline; }
.sy-scale .n { font: 700 12pt/1.4 "Amiri"; color: var(--sapphire); text-align: center; }
.sy-scale .t { font: 600 10pt/1.5 "Changa"; color: var(--ink); }
.sy-scale .d { font: 400 10.6pt/1.6 "Scheherazade New"; color: var(--ink-2); }
/* dedication: quiet, set high on the page */
.dd { position: absolute; top: 62mm; right: 30mm; left: 30mm; text-align: center; }
.dd p { font: 400 13pt/2.1 "Scheherazade New"; color: var(--ink-2); margin: 0; text-indent: 0; text-align: center; }
.dd p:last-of-type { color: var(--sapphire); margin-top: 3mm; }
.dd-m { margin-top: 10mm; }
/* publisher's word */
.pw h2.tt { font: 700 20pt/1.3 "Changa"; color: var(--sapphire); margin: 0 0 8mm; }
.pw p { font: 400 12.4pt/1.85 "Scheherazade New"; color: var(--ink-2); text-align: justify; margin: 0 0 3mm; text-indent: 0; }
.pw-s { margin-top: 12mm; display: flex; justify-content: flex-start; }
/* colophon */
.co { position: absolute; bottom: 34mm; right: 30mm; left: 30mm; text-align: center; }
.co p { font: 400 9.6pt/1.9 "Scheherazade New"; color: var(--ink-2); margin: 0 0 3mm; text-indent: 0; text-align: center; }
.co .f { font: 400 8.2pt/1.8 "IBM Plex Sans Arabic"; color: var(--ink-3); }
.co .imark { margin-top: 9mm; }
"""


def page(inner, cls=""):
    return f'<section class="full {cls}"><div class="fm">{inner}</div></section>'


def mark(dark=False):
    return (f'<div class="imark{" on-dark" if dark else ""}"><span class="diamond"></span><span class="w">الإحسان</span>'
            f'<span class="e">{PUBLISHER_EN}</span></div>')


def grule():
    return '<div class="grule"><i></i><span class="diamond"></span><i></i></div>'


def half_title(n=1):
    return page(f'<div class="ht"><div class="t">{TITLE}</div><div class="s">{SUBTITLE}</div>{grule()}'
                f'<div class="a">{AUTHOR_SHORT}</div><div class="v">{volume_line(n)}</div></div>')


def _map_volume(i, current, sub="", after=""):
    w, nm, d, st, tag = VOLUMES[i - 1]
    dots = '<span class="sd">' + "<i></i>" * STAGE_DOTS[st] + "</span>" if st else ""
    tg = f'<span class="tg">{tag}</span>' if tag else ""
    return (f'<div class="smv{" here" if i == current else ""}"><div class="b"><i></i><span>{str(i).translate(AR)}</span></div>'
            f'<div class="tx"><div class="l1"><span class="w">المجلد {w}</span><span class="nm">{nm}</span>{dots}{tg}</div>'
            f'{sub}<div class="d">{d}</div>{after}</div></div>')


def _map_stage(st):
    return (f'<div class="sms"><div class="b"><i></i></div><div class="tx"><div class="l1"><span class="o">{STAGES[st]}</span>'
            f'<b>{st}</b></div><div class="f">{STAGE_LINE[st]}</div></div></div>')


def _map_column(stages, current):
    out = []
    for st in stages:
        out.append(_map_stage(st))
        out += [_map_volume(i, current) for i, v in enumerate(VOLUMES, 1) if v[3] == st]
    out[-1] = out[-1].replace('class="smv', 'class="smv last', 1)
    return f'<div class="sm-col">{"".join(out)}</div>'


def volumes_map(current=1):
    """The series map, a spread of two pages: the right-hand page (even) and the left-hand page (odd) after it."""
    right = (f'<div class="sm r"><div class="sm-rule"></div><div class="sm-k">خريطة السلسلة</div>'
             f'<div class="sm-h"><div class="t">{TITLE}</div><div class="n">في أحد عشر مجلدًا</div>'
             f'<div class="p">عشرةٌ للمنهج في أربع مراحل وثلاثة عشر بابًا، يأخذ كلٌّ منها ما أحكمه الذي قبله ويزيد عليه؛ '
             f'ثم مرجعٌ يُفتح مع كل مجلد.</div></div>{_map_column(["التأسيس", "التواصل"], current)}</div>')
    ref = _map_volume(11, current, sub=f'<div class="sub">{REFERENCE_SUB}</div>',
                      after='<div class="x"><i></i>خارج ترقيم الأبواب والمستويات؛ يُفتح مع أيّ مجلد، ولا يُقرأ بعدها وحدها</div>')
    legend = ('<div class="sml"><span><i class="f"></i>المجلد الذي بين يديك</span>'
              '<span><span class="dt"><i></i><i></i></span>النقاط: رقم المرحلة، كما على الكعب</span>'
              '<span><i class="e"></i>المرجع: لا مرحلة له ولا باب</span></div>')
    left = (f'<div class="sm l"><div class="sm-rule"></div>{_map_column(["المنصّات", "التمكين"], current)[:-6]}'
            f'<div class="smr"><div class="k">ثم المرجع</div>{ref}</div>'
            f'<div class="smc">ويرافق السلسلة كتابان خارج مجلداتها: «{COMPANIONS[0]}»، و«{COMPANIONS[1]}».</div></div>{legend}</div>')
    return page(right) + page(left)


def title_volume(n=1, babs=None):
    """The volume on the title page: «المجلد الأول»، its name, then its stage and its babs by their numbers
    («البابان الثامن والتاسع»: a bab's number is not its place in the volume; Bible, ch. 112d)."""
    w, nm, _, st, _ = VOLUMES[n - 1]
    babs = babs if babs is not None else {1: "المقدمة، والمدخل، والباب الأول: الأسس"}.get(n, "")
    line = " · ".join(x for x in (f"{STAGES[st]}: {st}" if st else "المرجع", babs) if x)
    return f'<div class="tpv"><div class="w">المجلد {w}</div><div class="nm">{nm}</div><div class="ln">{line}</div></div>'


def imprint(n=1):
    volume = f"{VOLUMES[n - 1][0]} (من أحد عشر): {VOLUMES[n - 1][1]}"
    rows = [("العنوان", f"{TITLE}<br>{SUBTITLE}"),
            ("المؤلف", f"{AUTHOR_KUNYA} {AUTHOR_LONG}"),
            ("المجلد", volume),
            ("الطبعة", f"{EDITION}، {YEAR}"),
            ("الناشر", f"{PUBLISHER_AR}<small>{PUBLISHER_EN}</small>")]
    if CITY:
        rows.append(("مكان النشر", CITY))
    if ISBN.get(n):
        rows.append(("ردمك المجلد", f'<small>ISBN {ISBN[n]}</small>'))
    if ISBN_SET:
        rows.append(("ردمك المجموعة", f'<small>ISBN {ISBN_SET}</small>'))
    if DEPOSIT.get(n):
        rows.append(("رقم الإيداع", DEPOSIT[n]))
    body = "".join(f'<div class="im-row"><div class="l">{a}</div><div class="v">{b}</div></div>' for a, b in rows)
    contact = "".join(f'<div class="ltr">{x}</div>' for x in PHONES + [EMAIL])
    return page(f'<div class="im"><h4><span>بيانات النشر</span><i></i></h4>{body}'
                f'<div class="im-pub">{mark()}<div class="c">{PUBLISHER_AR}{contact}</div></div></div>')


def rights():
    holder = f'<div class="h2">{RIGHTS_HOLDER}</div>' if RIGHTS_HOLDER else ""
    return page(f'''<div class="rt">
<div class="c">جميع الحقوق محفوظة<br>{YEAR}</div>{holder}
<p>لا يجوز نشر هذا الكتاب أو أيّ جزءٍ منه، ولا نسخه أو اختزانه في نظامٍ لاسترجاع المعلومات، ولا نقله بأيّ وسيلةٍ إلكترونيةٍ أو آليةٍ أو تصويريةٍ أو تسجيلية أو غير ذلك، إلا بإذنٍ كتابيٍّ مسبق من الناشر.</p>
<p>ويُستثنى من ذلك الاقتباس اليسير لأغراض البحث العلمي والتعليم والنقد والمراجعة، على أن يُنسب إلى الكتاب ومؤلّفه نسبةً تامّة، وأن يُنقل بلفظه.</p>
<p>{FICTIONAL_NAMES}</p>
<p>والآيات القرآنية مثبتةٌ بالرسم العثماني على رواية حفص عن عاصم، مطابقةً لمصحف المدينة النبوية. والنقول موثّقةٌ في حواشيها بطبعاتها، وبيانات الطبعات كاملةً في ثبت المصادر.</p>
<div class="ed"><div class="h">الطبعات</div><div class="ed-row"><span>{EDITION}</span><span>{YEAR}</span></div></div>
</div>''')


def blank():
    return '<section class="full"><div class="blank"></div></section>'


SYMBOLS = [("﴿ ﴾", "نصّ القرآن الكريم، بالرسم العثماني، وتليه السورة ورقم الآية.", ""),
           ("« »", "نصٌّ منقولٌ بلفظه من مصدره. وما نُقل بمعناه لم يوضع بينهما.", ""),
           ("١/٧٥٣", "الجزء والصفحة من الطبعة المذكورة في الحاشية.", "s"),
           ("§٤", "الفقرة الرابعة من الفصل، في الإحالات الداخلية.", "s"),
           ("تحقيق:", "حاشيةٌ في اختلاف الروايات أو الألفاظ أو النسبة.", "s"),
           ("لغة:", "حاشيةٌ في ضبط مصطلحٍ أو بحثٍ في كلمة.", "s"),
           ("انظر:", "إحالةٌ إلى موضعٍ آخر من الكتاب.", "s"),
           ("تعقيب:", "رأيٌ للمؤلف في قولٍ نقله.", "s"),
           ("تنبيه:", "ملاحظةٌ على النصّ نفسه، كخطأٍ في طبعة.", "s"),
           ("ﷺ", "صلّى الله عليه وسلّم.", "")]


# the symbols of the lessons, which every volume uses and every volume explains (Bible, ch. 112d §٤)
TEACHING = [("▣", "بطاقة المقام: المتكلّم، والمخاطَب، والعلاقة، والمكان، والغرض، والأثر المطلوب، ودرجة الرسمية، والزمن.", ""),
            ("① ② ③ ④", "درجات المقارنة: المتكلّم غير الناجح، والمقبول، والناجح، والرفيع.", ""),
            ("✔", "عبارةٌ صحيحةٌ مناسبة.", ""),
            ("✘", "عبارةٌ خاطئة أو غير مناسبة.", ""),
            ("◐", "عبارةٌ مقبولة تحتمل التحسين.", ""),
            ("(س٧)", "السطر السابع من الحوار.", "s"),
            ("[ب٦-ف٤-مث١]", "رمز المثال: الباب السادس، الفصل الرابع، المثال الأول. وفي المرجع: [ر١-ف٤-مث١]، أي بنك الأخطاء، الفصل الرابع، البطاقة الأولى.", "s"),
            ("/ و //", "سكتةٌ قصيرة، وسكتةٌ طويلة، في نصوص التدريب الصوتي.", ""),
            ("↑ و ↓", "ارفع الصوت، واخفضه.", ""),
            ("(ت)", "موضع التنفّس.", "s")]
# the book's own tools, said once for every volume (Bible, ch. 34 §٢: «أداة تدريبية من إنشاء الكتاب»)
TOOLS_NOTE = ("والأدوات والنماذج والتدريبات والجداول التعليمية في هذا الكتاب من بنائه، وهي جزءٌ من هندسته التربوية، "
              "ما لم يُنسب شيءٌ منها إلى قائله.")
FORMALITY = [("٥", "شديد الرسمية", "لقاء وزير، حفلٌ رسمي، وفدٌ دبلوماسي"),
             ("٤", "رسمي", "مقابلةٌ وظيفية، محاضرة، خطبة، اجتماع مجلس"),
             ("٣", "شبه رسمي", "حديثٌ مع أستاذ بعد الدرس، اجتماع قسم"),
             ("٢", "وُدّي", "الزملاء والأصدقاء"),
             ("١", "أُسَري", "الوالدان والإخوة والأبناء")]
NUMBERS = [("المجلد", "الكتاب المادّي، من الأول إلى الحادي عشر؛ ويُذكر في الإحالة إلى موضعٍ في مجلدٍ آخر.", "s"),
           ("الباب", "الوحدة العلمية، متصلةٌ عبر السلسلة كلها من الأول إلى الثالث عشر.", "s"),
           ("المستوى", "درجة البرنامج التدريبي، ورقمه رقم بابه دائمًا.", "s"),
           ("الفصل", "الفصل داخل الباب، والدرس داخل الفصل.", "s"),
           ("المرجع", "المجلد الحادي عشر، «مرجع المتكلّم العربي»: خارج ترقيم الأبواب والمستويات.", "s")]


def _rows(items):
    return "".join(f'<div class="sy-row"><div class="m {c}">{m}</div><div class="d">{d}</div></div>' for m, d, c in items)


def symbols():
    scale = "".join(f'<div class="sy-scale"><div class="n">{n}</div><div class="t">{k}</div><div class="d">{d}</div></div>'
                    for n, k, d in FORMALITY)
    return (f'<section class="chap sy"><h2 class="tt">الرموز والاصطلاحات</h2>'
            f'<h3><span>في الدروس</span><i></i></h3>{_rows(TEACHING)}'
            f'<h3><span>سلّم الرسمية</span><i></i></h3>{scale}'
            f'<h3><span>الأرقام الأربعة</span><i></i></h3>{_rows(NUMBERS)}'
            f'<h3><span>في الجهاز العلمي</span><i></i></h3>{_rows(SYMBOLS)}<p class="sy-note">{TOOLS_NOTE}</p></section>')


def contents(entries, n=1):
    """entries: (level, kicker, title, page, sections) — level "part" rows are dividers."""
    out = [f'<section class="chap toc2"><h2 class="tt">المحتويات</h2><div class="tsub">{volume_line(n)}</div>']
    for e in entries:
        if e[0] == "part":
            out.append(f'<div class="part"><span>{e[2]}</span><i></i></div>')
            continue
        _, k, t, p, secs = e
        s = ""
        if secs:
            s = '<div class="s">' + "".join(f'<b>{i}</b>{x}' for i, x in secs) + '</div>'
        lite = " lite" if not k else ""
        out.append(f'<div class="e{lite}"><div class="k">{k}</div><div class="t">{t}</div><div class="p">{p}</div>{s}</div>')
    return "".join(out) + "</section>"


def colophon(n=1, proof=None):
    """The volume's close: it names what is done and hands the reader to the next volume (Bible, ch. 39)."""
    if n < 10:
        nxt = f"، ويليه {volume_line(n + 1)}"
    elif n == 10:
        nxt = f"، وبه تمّ منهج الكتاب، ويرافقه {volume_line(11)}"
    else:
        nxt = ""
    w, nm = VOLUMES[n - 1][:2]
    done = f"تمّ المجلد {w} من «{TITLE}»: {nm}{nxt}."
    note = f'<p class="f" style="margin-top:4mm;color:var(--crimson)">{proof}</p>' if proof else ""
    return page(f'''<div class="co">{grule()}
<p style="margin-top:8mm">{done}</p>
<p class="f">صُفّ المتن بحرف شهرزاد الجديد، والنصوص التراثية بحرف أميري، والقرآن الكريم بحرف أميري قرآن، والعناوين بحرفَي تشانغا وكوفام، والتنقّل بحرف بلكس العربي، والإحالات اللاتينية بحرف سورس سيريف.</p>
<p class="f">صدر عن {PUBLISHER_AR}، {YEAR}.</p>{note}
{mark()}</div>''')


DEDICATION = ["إلى طالب العلم الذي عرف العربية،", "ولم يُتَح له بعدُ أن يتكلّم بها كما يعرفها؛",
              "وإلى معلّمه الذي يريد أن يرى العلم على لسانه كما رآه في صدره؛", "أُهدي هذا الكتاب."]


def dedication():
    lines = "".join(f"<p>{x}</p>" for x in DEDICATION)
    return page(f'<div class="dd">{lines}<div class="dd-m"><span class="diamond"></span></div></div>')


PUBLISHER_WORD = [
    "تصدر دار الإحسان للتصميم والنشر هذا الكتاب سلسلةً من المجلدات، أولها هذا.",
    "وقد أُخرج على ما يليق بكتابٍ عربيٍّ علمي: الآيات بالرسم العثماني على رواية حفص عن عاصم، مطابقةً لمصحف المدينة النبوية؛ والأحاديث مخرّجةٌ بأرقامها وكتبها وأبوابها في طبعاتٍ معيّنة؛ والنقول معزوّةٌ إلى مواضعها بالجزء والصفحة، والحاشية في أسفل الصفحة التي تحتاج إليها، لا في آخر الكتاب.",
    "واختيرت حروف الكتاب لوظائفها: حرفٌ للمتن يُقرأ طويلًا بلا تعب، وحرفٌ للنصوص التراثية، وحرف المصحف للقرآن الكريم، وحرفان كوفيّان للعناوين. وصُمّمت صفحاته على تنوّعٍ منضبط: صفحةٌ علمية كثيفة الحواشي، ثم صفحة آيةٍ أو اقتباسٍ أو انتقال، ليجد القارئ في الكتاب إيقاعًا يعينه على طول القراءة.",
    "والدار ترحّب بكل ملاحظةٍ علمية أو لغوية أو فنية على هذه الطبعة، لتُستدرك في الطبعات التالية.",
]


def publisher_word():
    body = "".join(f"<p>{x}</p>" for x in PUBLISHER_WORD)
    return f'<section class="chap pw"><h2 class="tt">كلمة الناشر</h2>{body}<div class="pw-s">{mark()}</div></section>'
