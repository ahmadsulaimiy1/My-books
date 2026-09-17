#!/usr/bin/env python3
"""
Assemble the stationery. One source, three documents, no drift.

    python3 tools/build-pages.py
      letterhead.html                the blank first sheet
      letterhead-continuation.html   a blank continuation sheet
      letter-tahniah-dr-adewuyi.html a two-sheet letter set on it
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)

NAME_AR  = "الإمام أحمد بن إبراهيم السليمي"
HOUSE_AR = "(آل سلام)"
SCOPE_AR = "للتطوير الأكاديمي والدعوة الإسلامية والعلاقات الدولية والشؤون الأهلية الخاصة"
REF      = "PA/2026/09/0017"

HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="assets/letterhead-typography.css">
<link rel="stylesheet" href="assets/materials.css">
<link rel="stylesheet" href="assets/atelier.css">
</head>
<body>{speckit}
'''
SPECKIT = '\n<button class="speckit" onclick="document.body.classList.toggle(\'spec\')">PRODUCTION SPEC</button>\n'

GUIL = '''      <svg class="fill" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <pattern id="guil" width="44" height="17" patternUnits="userSpaceOnUse">
            <g fill="none" stroke="#E4CC8A" stroke-width=".38">
              <path d="M0 8.5 C 5.5 1, 16.5 1, 22 8.5 S 38.5 16, 44 8.5"/>
              <path d="M0 8.5 C 5.5 16, 16.5 16, 22 8.5 S 38.5 1, 44 8.5"/>
            </g>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#guil)"/>
      </svg>'''

def medallion(cls="medallion", spec=False):
    s = ' data-spec="GOLD FOIL RING · complete insignia, 7mm clear"' if spec else ''
    return f'''  <!-- the medallion resolves the plate's inner corner AND gives the mark its
       clear space; the architecture is built around it, never the reverse -->
  <div class="{cls} gold-block"{s}>
    <div class="med-field field-sapphire">
      <div class="med-hair"></div>
      <img class="med-mark" src="assets/insignia-foil.png"
           alt="Insignia of the Personal Office">
    </div>
  </div>
'''

def plate(spec=False):
    g = ' data-spec="GOLD FOIL keyline"' if spec else ''
    s = ' data-spec="SAPPHIRE FLOOD · offset"' if spec else ''
    r = ' data-spec="RED INLAY"' if spec else ''
    return f'''  <!-- ══ ONE CUT PLATE: head and binding edge, with a stepped lower edge ══ -->
  <div class="plate-gold gold-block"{g}></div>
  <div class="plate field-sapphire"{s}>
    <div class="plate-guil">
{GUIL}
    </div>
  </div>
  <div class="inlay-edge gold-block" style="left:175.9mm"></div>
  <div class="inlay field-red"{r}></div>
  <div class="inlay-edge gold-block" style="left:179.6mm"></div>

  <span class="vert pier-en gold-type gold-type--dark">IMAM AHMAD IBRAHIM SULAIMIY</span>
  <span class="vert pier-sub">PERSONAL OFFICE &nbsp;·&nbsp; ĀL-ES-SALAM</span>

  <div class="verify">
    <div class="frame gold-block"><img src="assets/qr-office.png"
         alt="Scan for the office contact card"></div>
    <div class="serial">{REF}</div>
  </div>
'''

def head(spec=False):
    n = ' data-spec="PEARL, reversed out of sapphire"' if spec else ''
    return f'''
  <div class="office gold-type gold-type--dark">المكتب الخاص</div>
  <h1 class="name"{n}>{NAME_AR}</h1>
  <div class="house gold-type gold-type--dark">{HOUSE_AR}</div>
  <div class="name-rule gold-block gold-block--dark"></div>

  <div class="ident">
    <div class="ident-office">PERSONAL OFFICE</div>
    <div class="ident-name letterpress">IMAM AHMAD<br>IBRAHIM SULAIMIY</div>
    <div class="ident-house">ĀL·ES·SALAM</div>
  </div>

  <p class="scope-ar">{SCOPE_AR}</p>
  <div class="scope-en">Academic Development<i></i>Islamic Da&lsquo;wah<i></i>International Relations<i></i>Private &amp; Civic Affairs</div>

  <div class="classification">
    <span class="en">OFFICIAL CORRESPONDENCE</span>
    <span class="ar">مراسلة رسمية</span>
  </div>
'''

def register(ref="", date_ar="", to_name="", to_role="", subject="", spec=False):
    s = ' data-spec="RED rule · GOLD hairlines · no boxes"' if spec else ''
    def lab(ar, en): return f'<div class="reg-lab"><span class="ar">{ar}</span><span class="en">{en}</span></div>'
    return f'''
  <div class="register"{s}>
    <div class="reg-open field-red"></div>
    <div class="reg-row split">
      {lab("رقم","REF.")}
      <div class="reg-val lat"><span class="ref">{ref}</span></div>
      {lab("التاريخ","DATE")}
      <div class="reg-val">{date_ar}</div>
    </div>
    <div class="reg-rule"></div>
    <div class="reg-row">
      {lab("إلى","TO")}
      <div class="reg-val"><span class="strong">{to_name}</span>{"<br>" if to_role else ""}<span class="sub">{to_role}</span></div>
    </div>
    <div class="reg-rule"></div>
    <div class="reg-row">
      {lab("الموضوع","SUBJECT")}
      <div class="reg-val">{subject}</div>
    </div>
    <div class="reg-close"></div>
  </div>
'''

SECURITY = '''
  <svg class="latent" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <g fill="none" stroke="#6B7080" stroke-width="0.5" opacity="0.18">
      <circle cx="200" cy="200" r="190"/><circle cx="200" cy="200" r="152"/>
      <circle cx="200" cy="200" r="107"/><circle cx="200" cy="200" r="76"/>
      <rect x="65.5" y="65.5" width="269" height="269"/>
      <rect x="65.5" y="65.5" width="269" height="269" transform="rotate(45 200 200)"/>
      <rect x="105" y="105" width="190" height="190" transform="rotate(22.5 200 200)"/>
      <path d="M10 200 H390 M200 10 V390 M66 66 L334 334 M334 66 L66 334"/>
    </g>
  </svg>
  <span class="watermark"><img src="assets/insignia-deboss.png" alt="" aria-hidden="true"></span>
'''

def foot(fa, fe, spec=False):
    m = ' data-spec="MICROTEXT 2.4pt"' if spec else ''
    strip = ("المكتب الخاص · الإمام أحمد بن إبراهيم السليمي (آل سلام) · "
             "PERSONAL OFFICE · ĀL-ES-SALAM · ") * 6
    return f'''
  <div class="microtext"{m}>{strip}</div>
  <div class="foot-rule gold-block"></div>
  <div class="foot">
    <span class="contact">+234&nbsp;810&nbsp;430&nbsp;2087<i></i>+44&nbsp;7961&nbsp;869638<i></i>abisulaimiycollege@gmail.com</span>
    <span class="folio"><span class="ar">{fa}</span><span class="sep">·</span>{fe}</span>
  </div>
'''

SIGNATURES = '''
  <!-- The principal signs. The office that prepared the letter is identified
       beneath, deliberately smaller: a private office, not a ministry.
       The Arabic form leads in an Arabic letter — أ. عبد الله السليمي —
       and is typeset for Arabic correspondence rather than translated from
       the English metadata. -->
  <div class="signatures">
    <div class="sig--principal">
      <div class="sig-space"></div>
      <div class="sig-rule gold-block"></div>
      <div class="sig-ar">الإمام أحمد بن إبراهيم السليمي (آل سلام)</div>
      <div class="sig-lat">Imam Ahmad Ibrahim Sulaimiy</div>
      <div class="sig-role">المكتب الخاص &nbsp;·&nbsp; Personal Office</div>
    </div>
    <div class="sig--issuing">
      <div class="sig-space--sm"><img src="assets/signature-abdullah.png"
           alt="Signature of Abdullah Sulaimiy"></div>
      <div class="sig-rule--fine"></div>
      <div class="sig-ar">أ. عبد الله السليمي <span class="cred">(SMPr · MMJ · Op-Ed)</span></div>
      <div class="sig-fn">للعلاقات والاتصالات الداخلية</div>
      <div class="sig-role">Communications &amp; Internal Relations</div>
    </div>
  </div>
'''

def cont_head(spec=False):
    return f'''
  <div class="cont-plate-gold gold-block"></div>
  <div class="cont-plate field-sapphire"><div class="plate-guil">
{GUIL}
  </div></div>
  <div class="inlay-edge gold-block" style="left:175.9mm"></div>
  <div class="inlay field-red"></div>
  <div class="inlay-edge gold-block" style="left:179.6mm"></div>

  <span class="vert pier-en gold-type gold-type--dark">IMAM AHMAD IBRAHIM SULAIMIY</span>
  <span class="vert pier-sub">PERSONAL OFFICE &nbsp;·&nbsp; ĀL-ES-SALAM</span>
  <div class="verify">
    <div class="frame gold-block"><img src="assets/qr-office.png" alt=""></div>
    <div class="serial">{REF}</div>
  </div>

{medallion("cont-med medallion")}
  <div class="cont-ref">REF. <span class="ref">{REF}</span><br><span class="k">CONTINUATION</span></div>
  <div class="cont-head">
    <div class="cont-name letterpress">{NAME_AR} {HOUSE_AR}</div>
  </div>
  <div class="cont-rule gold-block"></div>
'''

AR_NUM = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def folio(page, total=None):
    ar, en = f"صفحة {str(page).translate(AR_NUM)}", f"PAGE {page}"
    if total is not None:
        ar += f" من {str(total).translate(AR_NUM)}"; en += f" OF {total}"
    return ar, en

def sheet(inner): return '<div class="sheet">\n' + inner + '\n</div>\n'

# ── the correspondence ──────────────────────────────────────────────────────
# Register raised from the earlier draft: every construction that had the writer
# asking leave to address the recipient is gone. أرجو أن تتكرَّموا بالإذن لي
# positions a senior office as a supplicant; ويطيب لي أن أتشرَّف بزيارتكم offers
# the visit as a courtesy between peers. Warmth and humility are kept — they
# belong in Islamic scholarly correspondence — without subordination.
LETTER_1 = [
 '<p class="salutation">السلام عليكم ورحمة الله وبركاته، وبعدُ:</p>',
 '<p>فيطيبُ لي، أصالةً عن نفسي ونيابةً عن كلية السلطان حنفي للقرآن الكريم، أن أرفع إلى '
 'سعادتكم أخلصَ التهاني وأطيبَ التبريكات بمناسبة نَيْلكم درجةَ الدكتوراه؛ تتويجًا لمسيرةٍ '
 'علميةٍ حافلة، وثمرةً لجهدٍ متَّصلٍ في طلب العلم وخدمة أهله.</p>',
 '<p>وإنّ هذا الإنجاز، وإن بدا في ظاهره شهادةً علمية، فهو في حقيقته إضافةٌ إلى رصيد '
 'المؤسسات التي تشرَّفت بانتسابكم إليها، وإلى الحقل الأكاديمي الذي أفدتُموه بعلمكم '
 'وخبرتكم وحُسن رعايتكم.</p>',
 '<p>وأغتنمُ هذه المناسبة لأرفع التهنئة كذلك إلى أسرة كلية منار الهدى العالمية — إدارةً '
 'وهيئةَ تدريسٍ وطلابًا — وإلى أسرتكم الكريمة، على ما بلغتُموه، وعلى ما نرجوه لكم من '
 'مزيد التوفيق.</p>',
]
LETTER_2 = [
 '<p>ويسرُّني أن أؤكّد لسعادتكم حرصَ المكتب الخاص على توثيق أواصر التعاون العلمي بين '
 'مؤسستينا، بما يخدم طلبة العلم، ويرفع من كفاءة العمل الأكاديمي والدعوي.</p>',
 '<p>ونسأل الله تعالى أن يبارك لكم في هذه الدرجة، وأن يجعلها عونًا لكم على مواصلة العطاء '
 'العلمي والتربوي، وأن ينفع بكم الإسلامَ والمسلمين.</p>',
 '<p>ويطيبُ لي أن أرفع إليكم هذه التهنئة مشافهةً، وأن أتشرَّف بزيارتكم في موعدٍ يوافق '
 'ارتباطاتكم الكريمة.</p>',
 '<p>وتفضَّلوا سعادتَكم بقَبول فائق التقدير والاحترام.</p>',
 '<p>والسلام عليكم ورحمة الله وبركاته.</p>',
]

def main():
    fa, fe = folio(1)
    open(os.path.join(ROOT, "letterhead.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Letterhead — The Personal Office", speckit=SPECKIT)
        + sheet(plate(True) + medallion(spec=True) + head(True) + register(spec=True)
                + SECURITY + foot(fa, fe, True))
        + '</body>\n</html>\n')

    fa, fe = folio(2)
    open(os.path.join(ROOT, "letterhead-continuation.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Letterhead — continuation sheet", speckit="")
        + sheet(cont_head() + '  <div class="field field--continued"></div>\n'
                + SECURITY + foot(fa, fe))
        + '</body>\n</html>\n')

    fa1, fe1 = folio(1, 2); fa2, fe2 = folio(2, 2)
    p1 = sheet(plate() + medallion() + head()
        + register(ref=REF,
                   date_ar='٣ ربيع الآخر ١٤٤٨هـ<br><span class="sub">الموافق ١٧ سبتمبر ٢٠٢٦م</span>',
                   to_name="سعادة الدكتور حبيب الله يوسف أديوي المحترم",
                   to_role="مدير كلية منار الهدى العالمية",
                   subject="تهنئة بمناسبة نَيْل درجة الدكتوراه")
        + SECURITY
        + '  <div class="field">\n    <p class="bismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</p>\n'
          '    <div class="letter">\n      ' + "\n      ".join(LETTER_1) + '\n    </div>\n  </div>\n'
        + foot(fa1, fe1))
    p2 = sheet(cont_head() + SECURITY
        + '  <div class="field field--continued">\n    <div class="letter">\n      '
        + "\n      ".join(LETTER_2) + '\n    </div>\n  </div>\n'
        + SIGNATURES + foot(fa2, fe2))
    open(os.path.join(ROOT, "letter-tahniah-dr-adewuyi.html"), "w", encoding="utf-8").write(
        HEAD.format(title="تهنئة بمناسبة نَيْل درجة الدكتوراه", speckit="") + p1 + "\n" + p2
        + '</body>\n</html>\n')
    print("letterhead.html · letterhead-continuation.html · letter-tahniah-dr-adewuyi.html")

if __name__ == "__main__":
    main()
