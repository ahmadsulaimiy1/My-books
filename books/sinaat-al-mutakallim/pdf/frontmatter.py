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
RIGHTS_HOLDER = "حقوق التأليف للمؤلف، وحقوق الطبع والنشر لدار الإحسان للتصميم والنشر"
CITY = None
ISBN = None
DEPOSIT = None

VOLUMES = [("الأول", "التأسيس", "العربية التي نتكلّمها، والأسس، واللسان، والعبارة"),
           ("الثاني", "التواصل", "البيان وترتيب الكلام، وآداب المخاطبة، ومراعاة المقام"),
           ("الثالث", "المنصّات", "المجلس والمحاضرة، والخطبة، والمقابلة، والحوار الإعلامي"),
           ("الرابع", "التمكين", "الاختلاف والتفاوض، وبنك الأخطاء، والارتجال، والأداء الختامي")]

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
.ht { position: absolute; top: 62mm; left: 0; right: 0; text-align: center; }
.ht .t { font: 600 23pt/1.5 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--sapphire); }
.ht .s { font: 400 12.5pt/1.6 "Scheherazade New"; color: var(--ink-2); margin-top: 2mm; }
.ht .grule { margin: 9mm 0 8mm; }
.ht .a { font: 300 10.5pt/1.5 "Changa"; color: var(--ink-2); }
.ht .v { position: absolute; top: 118mm; left: 0; right: 0; font: 300 9pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .6pt; }
/* 2. the four volumes: quiet geometry */
.vm { position: absolute; top: 58mm; right: 40mm; left: 40mm; }
.vm .k { font: 300 10pt/1 "Changa"; color: var(--gold-ink); margin-bottom: 10mm; display: flex; gap: 3mm; align-items: center; }
.vm .k i { flex: 1; border-top: .4pt solid var(--gold); }
.vm-row { display: grid; grid-template-columns: 17mm 1fr; gap: 0 5mm; padding: 5.2mm 0; border-bottom: .3pt solid #DCD6CA; align-items: baseline; }
.vm-row .n { font: 300 9pt/1 "Changa"; color: var(--ink-3); }
.vm-row .nm { font: 600 15pt/1.3 "Changa"; color: var(--sapphire); }
.vm-row .d { grid-column: 2; font: 400 10.4pt/1.6 "Scheherazade New"; color: var(--ink-2); margin-top: 1mm; }
.vm-row.here .nm::after { content: ""; display: inline-block; width: 1.8mm; height: 1.8mm; border-radius: 50%%; background: var(--crimson); margin-right: 2.5mm; vertical-align: middle; }
/* 4. imprint: a typographic table */
.im { position: absolute; top: 38mm; right: 36mm; left: 36mm; }
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
.rt { position: absolute; bottom: 34mm; right: 36mm; left: 36mm; }
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
/* dedication: quiet, set high on the page */
.dd { position: absolute; top: 70mm; right: 44mm; left: 44mm; text-align: center; }
.dd p { font: 400 13pt/2.1 "Scheherazade New"; color: var(--ink-2); margin: 0; text-indent: 0; text-align: center; }
.dd p:last-of-type { color: var(--sapphire); margin-top: 3mm; }
.dd-m { margin-top: 10mm; }
/* publisher's word */
.pw h2.tt { font: 700 20pt/1.3 "Changa"; color: var(--sapphire); margin: 0 0 8mm; }
.pw p { font: 400 12.4pt/1.85 "Scheherazade New"; color: var(--ink-2); text-align: justify; margin: 0 0 3mm; text-indent: 0; }
.pw-s { margin-top: 12mm; display: flex; justify-content: flex-start; }
/* colophon */
.co { position: absolute; bottom: 40mm; right: 45mm; left: 45mm; text-align: center; }
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


def half_title():
    return page(f'<div class="ht"><div class="t">{TITLE}</div><div class="s">{SUBTITLE}</div>{grule()}'
                f'<div class="a">{AUTHOR_SHORT}</div><div class="v">المجلد الأول</div></div>')


def volumes_map(current=1):
    rows = "".join(f'<div class="vm-row{" here" if i == current else ""}"><div class="n">المجلد {w}</div><div class="nm">{nm}</div>'
                   f'<div class="d">{d}</div></div>' for i, (w, nm, d) in enumerate(VOLUMES, 1))
    return page(f'<div class="vm"><div class="k"><span>{TITLE} في أربعة مجلدات</span><i></i></div>{rows}</div>')


def imprint(volume="الأول: التأسيس"):
    rows = [("العنوان", f"{TITLE}<br>{SUBTITLE}"),
            ("المؤلف", f"{AUTHOR_KUNYA} {AUTHOR_LONG}"),
            ("المجلد", volume),
            ("الطبعة", f"{EDITION}، {YEAR}"),
            ("الناشر", f"{PUBLISHER_AR}<small>{PUBLISHER_EN}</small>")]
    if CITY:
        rows.append(("مكان النشر", CITY))
    if ISBN:
        rows.append(("ردمك", f'<small>ISBN {ISBN}</small>'))
    if DEPOSIT:
        rows.append(("رقم الإيداع", DEPOSIT))
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


def symbols():
    rows = "".join(f'<div class="sy-row"><div class="m {c}">{m}</div><div class="d">{d}</div></div>' for m, d, c in SYMBOLS)
    return f'<section class="chap sy"><h2 class="tt">الرموز والاصطلاحات</h2>{rows}</section>'


def contents(entries):
    """entries: (level, kicker, title, page, sections) — level "part" rows are dividers."""
    out = ['<section class="chap toc2"><h2 class="tt">المحتويات</h2><div class="tsub">المجلد الأول: التأسيس — الافتتاحية</div>']
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


def colophon():
    return page(f'''<div class="co">{grule()}
<p style="margin-top:8mm">تمّ المجلد الأول من «{TITLE}»، ويليه المجلد الثاني: التواصل.</p>
<p class="f">صُفّ المتن بحرف شهرزاد الجديد، والنصوص التراثية بحرف أميري، والقرآن الكريم بحرف أميري قرآن، والعناوين بحرفَي تشانغا وكوفام، والتنقّل بحرف بلكس العربي، والإحالات اللاتينية بحرف سورس سيريف.</p>
<p class="f">صدر عن {PUBLISHER_AR}، {YEAR}.</p>
{mark()}</div>''')


DEDICATION = ["إلى طالب العلم الذي عرف العربية،", "ولم يُتَح له بعدُ أن يتكلّم بها كما يعرفها؛",
              "وإلى معلّمه الذي يريد أن يرى العلم على لسانه كما رآه في صدره؛", "أُهدي هذا الكتاب."]


def dedication():
    lines = "".join(f"<p>{x}</p>" for x in DEDICATION)
    return page(f'<div class="dd">{lines}<div class="dd-m"><span class="diamond"></span></div></div>')


PUBLISHER_WORD = [
    "تصدر دار الإحسان للتصميم والنشر هذا الكتاب في أربعة مجلدات، أولها هذا.",
    "وقد أُخرج على ما يليق بكتابٍ عربيٍّ علمي: الآيات بالرسم العثماني على رواية حفص عن عاصم، مطابقةً لمصحف المدينة النبوية؛ والأحاديث مخرّجةٌ بأرقامها وكتبها وأبوابها في طبعاتٍ معيّنة؛ والنقول معزوّةٌ إلى مواضعها بالجزء والصفحة، والحاشية في أسفل الصفحة التي تحتاج إليها، لا في آخر الكتاب.",
    "واختيرت حروف الكتاب لوظائفها: حرفٌ للمتن يُقرأ طويلًا بلا تعب، وحرفٌ للنصوص التراثية، وحرف المصحف للقرآن الكريم، وحرفان كوفيّان للعناوين. وصُمّمت صفحاته على تنوّعٍ منضبط: صفحةٌ علمية كثيفة الحواشي، ثم صفحة آيةٍ أو اقتباسٍ أو انتقال، ليجد القارئ في الكتاب إيقاعًا يعينه على طول القراءة.",
    "والدار ترحّب بكل ملاحظةٍ علمية أو لغوية أو فنية على هذه الطبعة، لتُستدرك في الطبعات التالية.",
]


def publisher_word():
    body = "".join(f"<p>{x}</p>" for x in PUBLISHER_WORD)
    return f'<section class="chap pw"><h2 class="tt">كلمة الناشر</h2>{body}<div class="pw-s">{mark()}</div></section>'
