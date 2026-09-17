#!/usr/bin/env python3
"""
Assemble the stationery.

    python3 tools/build-pages.py

The pier, head, classification bar, register, foot and security layer are
written once here and composed into:

    letterhead.html                  the blank first sheet
    letterhead-continuation.html     a blank continuation sheet
    letter-tahniah-dr-adewuyi.html   a three-sheet letter set on it

Generating them rather than hand-keeping three copies is the only way the
masthead on correspondence cannot drift from the masthead on the blank.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OFFICE_AR = "المكتب الخاص"
NAME_AR   = "الإمام أحمد بن إبراهيم السليمي (آل سلام)"
SCOPE_AR  = "للتطوير الأكاديمي والدعوة الإسلامية والعلاقات الدولية والشؤون الأهلية الخاصة"
REF       = "PA/2026/09/0017"

HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="assets/letterhead-typography.css">
<link rel="stylesheet" href="assets/materials.css">
<link rel="stylesheet" href="assets/instrument.css">
</head>
<body>{speckit}
'''

SPECKIT = '\n<button class="speckit" onclick="document.body.classList.toggle(\'spec\')">PRODUCTION SPEC</button>\n'

def pier(spec=False):
    s = ' data-spec="SAPPHIRE FLOOD · offset"' if spec else ''
    m = ' data-spec="GOLD FOIL"' if spec else ''
    q = ' data-spec="QR · ECC Q, scannable at 22mm"' if spec else ''
    return f'''  <!-- ══ THE PIER — the binding edge, which in Arabic is the RIGHT ═════════ -->
  <div class="pier field-sapphire"{s}>
    <div class="pier-guil">
      <svg class="fill" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <defs>
          <pattern id="pierguil" width="40" height="18" patternUnits="userSpaceOnUse">
            <g fill="none" stroke="#C6D2E0" stroke-width=".4">
              <path d="M0 9 C 5 1, 15 1, 20 9 S 35 17, 40 9"/>
              <path d="M0 9 C 5 17, 15 17, 20 9 S 35 1, 40 9"/>
            </g>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#pierguil)"/>
      </svg>
    </div>
  </div>

  <img class="pier-mark" src="assets/insignia-foil.png"{m}
       alt="Insignia of the Personal Office">
  <div class="pier-rule plat-block plat-block--dark" style="top:39mm"></div>

  <span class="vert pier-en plat-type plat-type--dark">IMAM AHMAD IBROHIM SULAIMIY</span>
  <span class="vert pier-sub">PERSONAL OFFICE &nbsp;·&nbsp; ĀL-ES-SALAM</span>

  <div class="verify"{q}>
    <img src="assets/qr-office.png" alt="Scan for the office contact card">
    <div class="serial">{REF}</div>
  </div>
'''

def head(spec=False):
    n = ' data-spec="GOLD FOIL / SAPPHIRE — one line, two materials"' if spec else ''
    r = ' data-spec="PLATINUM FOIL"' if spec else ''
    return f'''
  <!-- ══ THE HEAD — the name is right-aligned INSIDE the pier, and clipped
       against its edge, so it stands in gold there and in sapphire here ═══ -->
  <div class="office letterpress">{OFFICE_AR}</div>

  <h1 class="name name--pearl letterpress"{n}>{NAME_AR}</h1>
  <h1 class="name name--pier" aria-hidden="true">{NAME_AR}</h1>

  <div class="head-rule plat-block"{r}></div>

  <p class="scope-ar">{SCOPE_AR}</p>
  <div class="ident">
    <div class="ident-office">PERSONAL OFFICE</div>
    <div class="ident-name letterpress">IMAM AHMAD<br>IBROHIM SULAIMIY</div>
    <div class="ident-house">ĀL·ES·SALAM</div>
  </div>
'''

def classbar(spec=False):
    c = ' data-spec="RED · offset, PMS 186-ish"' if spec else ''
    return f'''
  <!-- ══ THE CLASSIFICATION — the first of three strikes of red ═══════════ -->
  <div class="classbar field-red"{c}>
    <span class="ar">مراسلة رسمية</span>
    <span class="en">OFFICIAL CORRESPONDENCE</span>
  </div>
  <div class="classbar-edge plat-block"></div>
'''

def register(ref="", date_ar="", to_name="", to_role="", subject="", spec=False):
    s = ' data-spec="PLATINUM HAIRLINES · no boxes"' if spec else ''
    return f'''
  <!-- ══ THE REGISTER — ruled, never boxed ════════════════════════════════ -->
  <div class="register"{s}>
    <div class="rule rule--heavy"></div>
    <div class="reg-row split">
      <div class="reg-lab">الرقم</div>
      <div class="reg-val lat">{ref}</div>
      <div class="reg-lab">التاريخ</div>
      <div class="reg-val">{date_ar}</div>
    </div>
    <div class="rule"></div>
    <div class="reg-row">
      <div class="reg-lab">إلى</div>
      <div class="reg-val"><span class="strong">{to_name}</span>{"<br>" if to_role else ""}<span class="sub">{to_role}</span></div>
    </div>
    <div class="rule"></div>
    <div class="reg-row">
      <div class="reg-lab">الموضوع</div>
      <div class="reg-val">{subject}</div>
    </div>
    <div class="rule rule--heavy"></div>
  </div>
'''

SECURITY = '''
  <!-- ══ THE SECURITY LAYER — latent geometry, watermark, microtext ═══════ -->
  <svg class="latent" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <g fill="none" stroke="#6B7080" stroke-width="0.5" opacity="0.16">
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

def foot(folio_ar, folio_en, spec=False):
    m = ' data-spec="MICROTEXT · 2.4pt, resolves under a loupe"' if spec else ''
    strip = ("المكتب الخاص · الإمام أحمد بن إبراهيم السليمي (آل سلام) · "
             "PERSONAL OFFICE · ĀL-ES-SALAM · ") * 6
    return f'''
  <div class="microtext"{m}>{strip}</div>
  <div class="foot-rule plat-block"></div>
  <div class="foot">
    <span class="contact">+234&nbsp;810&nbsp;430&nbsp;2087<i></i>+44&nbsp;7961&nbsp;869638<i></i>abisulaimiycollege@gmail.com</span>
    <span class="folio"><span class="ar">{folio_ar}</span><span class="sep">·</span>{folio_en}</span>
  </div>
'''

def signatures(sig_img=True):
    img = ('<img src="assets/signature-abdullah.png" alt="Signature of Abdullah Sulaimiy">'
           if sig_img else '')
    return f'''
  <!-- ══ TWO HANDS — the principal signs, the issuing office dispatches ═══ -->
  <div class="signatures">
    <div class="sig sig--principal">
      <div class="sig-space"></div>
      <div class="sig-rule"></div>
      <div class="sig-ar">{NAME_AR}</div>
      <div class="sig-lat">Imam Ahmad Ibrohim Sulaimiy</div>
      <div class="sig-role">المكتب الخاص &nbsp;·&nbsp; Personal Office</div>
    </div>
    <div class="sig sig--issuing">
      <div class="sig-space">{img}</div>
      <div class="sig-rule"></div>
      <div class="sig-lat" style="font-size:8.6pt;color:var(--sapphire-800)">Abdullah Sulaimiy <span style="font-size:6.6pt;letter-spacing:.1em">(SMPr, MMJ, Op-Ed)</span></div>
      <div class="sig-role">For&nbsp;&nbsp;·&nbsp;&nbsp;Communications &amp; Internal Relations<br>
        Ref.&nbsp; <span class="ref">{REF}</span></div>
    </div>
  </div>
'''

def cont_head(page, total):
    ar = f"صفحة {page} من {total}"
    return f'''
  <div class="cont-ref">REF. <span class="ref">{REF}</span><br>CONTINUATION</div>
  <div class="cont-head">
    <div class="cont-name letterpress">{NAME_AR}</div>
  </div>
  <div class="cont-rule plat-block"></div>
'''

AR_NUM = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
def folio(page, total=None):
    """A BLANK sheet cannot know how many pages a letter will run to, so it
    carries only its own number. The 'of N' appears when a letter is set."""
    ar = f"صفحة {str(page).translate(AR_NUM)}"
    en = f"PAGE {page}"
    if total is not None:
        ar += f" من {str(total).translate(AR_NUM)}"
        en += f" OF {total}"
    return ar, en


def sheet(inner):
    return '<div class="sheet">\n' + inner + '\n</div>\n'


# ── the correspondence ──────────────────────────────────────────────────────
# Elevated Modern Standard Arabic: the formulas a private office actually uses
# — وبعد: to open the body, سعادة … المحترم for a senior academic,
# وتفضلوا … بقبول فائق التقدير to close — with the register and the rhetoric
# pitched to correspondence between a scholar's office and an institution's
# head. Dignified, not ornate.
LETTER_1 = [
    ('<p class="salutation">السلام عليكم ورحمة الله وبركاته، وبعدُ:</p>'),
    ('<p>فإنه ليَسُرُّني ويُشرِّفني، أصالةً عن نفسي ونيابةً عن كلية السلطان حنفي '
     'للقرآن الكريم، أن أرفع إلى سعادتكم أخلصَ التهاني وأطيبَ التبريكات بمناسبة '
     'نَيْلِكم درجةَ الدكتوراه؛ تتويجًا لمسيرةٍ علميةٍ حافلة، وثمرةً لجهدٍ متَّصلٍ '
     'في طلب العلم وخدمة أهله.</p>'),
    ('<p>وإنّ هذا الإنجاز، وإن بدا في ظاهره شهادةً علمية، فهو في حقيقته إضافةٌ إلى '
     'رصيد المؤسسات التي تشرَّفت بانتسابكم إليها، وإلى الحقل الأكاديمي الذي '
     'أفدتُموه بعلمكم وخبرتكم وحُسن رعايتكم.</p>'),
    ('<p>ولذلك فإننا إذ نهنّئ سعادتكم بهذا الاستحقاق، نهنّئ معكم أسرةَ كلية منار '
     'الهدى العالمية — إدارةً وهيئةَ تدريسٍ وطلابًا — وأسرتَكم الكريمة، على ما '
     'بلغتُموه، وعلى ما نرجوه لكم من مزيد التوفيق.</p>'),
]
LETTER_2 = [
    ('<p>ولا يفوتُني في هذا المقام أن أؤكّد لسعادتكم حرصَ المكتب الخاص على توثيق '
     'أواصر التعاون العلمي بين مؤسستينا، بما يخدم طلبة العلم، ويرفع من كفاءة '
     'العمل الأكاديمي والدعوي.</p>'),
    ('<p>ونسأل الله تعالى أن يبارك لكم في هذه الدرجة، وأن يجعلها عونًا لكم على '
     'مواصلة العطاء العلمي والتربوي، وأن ينفع بكم الإسلامَ والمسلمين.</p>'),
    ('<p>وإذ كنتُ أُوثِرُ أن أرفع إليكم هذه التهنئة مشافهةً، فإني أرجو أن تتكرَّموا '
     'بالإذن لي بزيارتكم في الوقت الذي ترونه مناسبًا، إن كان في ذلك سَعَةٌ من '
     'أوقاتكم.</p>'),
    ('<p class="closing">وتفضَّلوا سعادتَكم بقَبول فائق التقدير والاحترام.</p>'),
    ('<p>والسلام عليكم ورحمة الله وبركاته.</p>'),
]


def build_letter():
    fa1, fe1 = folio(1, 2)
    fa2, fe2 = folio(2, 2)

    page1 = sheet(
        pier() + head() + classbar()
        + register(ref=REF,
                   date_ar='٣ ربيع الآخر ١٤٤٨هـ<br><span class="sub">الموافق ١٧ سبتمبر ٢٠٢٦م</span>',
                   to_name="سعادة الدكتور حبيب الله يوسف أديوي المحترم",
                   to_role="مدير كلية منار الهدى العالمية",
                   subject="تهنئة بمناسبة نَيْل درجة الدكتوراه")
        + SECURITY
        + '  <div class="field">\n'
          '    <p class="bismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</p>\n'
          '    <div class="letter">\n      ' + "\n      ".join(LETTER_1) + '\n    </div>\n'
          '  </div>\n'
        + foot(fa1, fe1))

    page2 = sheet(
        pier() + cont_head(2, 2)
        + SECURITY
        + '  <div class="field field--continued">\n'
          '    <div class="letter">\n      ' + "\n      ".join(LETTER_2) + '\n    </div>\n'
          '  </div>\n'
        + signatures()
        + foot(fa2, fe2))

    doc = (HEAD.format(title="تهنئة بمناسبة نَيْل درجة الدكتوراه — سعادة الدكتور حبيب الله يوسف أديوي",
                       speckit="")
           + page1 + "\n" + page2 + '</body>\n</html>\n')
    open(os.path.join(ROOT, "letter-tahniah-dr-adewuyi.html"), "w", encoding="utf-8").write(doc)
    print("letter-tahniah-dr-adewuyi.html  (2 sheets)")


def main():
    # ── the blank first sheet ───────────────────────────────────────────────
    fa, fe = folio(1)
    p = (HEAD.format(title="Letterhead — The Personal Office", speckit=SPECKIT)
         + sheet(pier(True) + head(True) + classbar(True)
                 + register(spec=True) + SECURITY + foot(fa, fe, True))
         + '</body>\n</html>\n')
    open(os.path.join(ROOT, "letterhead.html"), "w", encoding="utf-8").write(p)

    # ── a blank continuation sheet ──────────────────────────────────────────
    fa, fe = folio(2)
    p = (HEAD.format(title="Letterhead — continuation sheet", speckit="")
         + sheet(pier() + cont_head(2, 2)
                 + '  <div class="field field--continued"></div>\n'
                 + SECURITY + foot(fa, fe))
         + '</body>\n</html>\n')
    open(os.path.join(ROOT, "letterhead-continuation.html"), "w", encoding="utf-8").write(p)
    build_letter()
    print("letterhead.html, letterhead-continuation.html")


if __name__ == "__main__":
    main()
