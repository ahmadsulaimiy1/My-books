#!/usr/bin/env python3
"""
The English counterpart of the atelier stationery. One source, three documents.

    python3 tools/build-en.py
      letterhead-en.html               the blank first sheet
      letterhead-en-continuation.html  a blank continuation sheet
      letter-en-tahniah-dr-adewuyi.html  the Arabic specimen letter, in English
    python3 tools/build-en.py --pdf    and print all three

NOTHING IS REBUILT HERE. Every construction below is the atelier's own, and
every stylesheet is loaded from ../letterhead-atelier/assets, which is sealed
and untouched. assets/letterhead-en.css is laid over the top and moves the
plate, the pier, the seal and the furniture to the binding edge at the left,
re-lighting the nine-member section as it goes so the lamp stays where it is.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
AT   = "../letterhead-atelier/assets"

def _find(*c): return next((p for p in c if os.path.exists(p)), None)
CHROME = _find("/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
               "/usr/bin/chromium", "/usr/bin/google-chrome")

NAME_AR  = "الإمام أحمد بن إبراهيم السليمي"
HOUSE_AR = "(آل سلام)"
SCOPE_AR = "للتطوير الأكاديمي والدعوة الإسلامية والعلاقات الدولية والشؤون الأهلية الخاصة"
REF      = "PO/2026/09/0017"

# THE ROOT STAYS RTL. The masthead, the seal's ground and the Bismillah are
# Arabic and must shape as Arabic; the English parts declare themselves ltr
# where they sit. Switching the root to ltr to carry an English body would put
# the whole identity into a direction it was not set in.
HEAD = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="{at}/letterhead-typography.css">
<link rel="stylesheet" href="{at}/materials.css">
<link rel="stylesheet" href="{at}/atelier.css">
<link rel="stylesheet" href="assets/letterhead-en.css">
</head>
<body>
'''

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

def medallion(cls="medallion"):
    # moved, never flipped: the insignia is an Arabic calligraphic mark and a
    # mirrored mark is a different mark
    return f'''  <div class="{cls} gold-block">
    <div class="med-steel steel-block"></div>
    <div class="med-field field-sapphire">
      <div class="med-hair"></div>
      <img class="med-mark" src="{AT}/insignia-foil.png"
           alt="Insignia of the Personal Office">
    </div>
  </div>
'''

def edge(full=False):
    """Nine members, one order, no gaps — emitted from ONE function so the
    first sheet and the continuation cannot drift apart. The members are the
    atelier's; the overlay re-places and re-lights them."""
    a = " edge-arris--full" if full else ""
    return f'''  <div class="edge-arris{a}"></div>
  <div class="edge">
    <i class="edge-rule"></i>
    <i class="edge-wall"></i>
    <i class="edge-plat plat-block"></i>
    <i class="edge-ret"></i>
    <i class="edge-rail gold-block gold-block--rich"></i>
    <i class="edge-cut"></i>
    <i class="edge-sill"></i>
  </div>
'''

def pier(ref=None):
    ref = ref or REF
    return f'''  <span class="vert pier-en gold-type gold-type--dark">IMAM AHMAD IBROHIM SULAIMIY</span>
  <span class="vert pier-sub">PERSONAL OFFICE &nbsp;·&nbsp; ĀL-ES-SALAM</span>

  <div class="verify">
    <div class="frame gold-block"><img src="{AT}/qr-office.png"
         alt="Scan for the office contact card"></div>
    <div class="serial">{ref}</div>
  </div>
'''

def plate(ref=None):
    return f'''  <!-- ══ ONE MILLED PLATE: head across the sheet, pier down the binding edge ══ -->
  <div class="plate-gold gold-block"></div>
  <div class="plate field-sapphire">
    <div class="plate-guil">
{GUIL}
    </div>
  </div>
{edge()}{pier(ref)}'''

def head():
    return f'''
  <div class="office gold-type gold-type--dark">المكتب الخاص</div>
  <h1 class="name">{NAME_AR}</h1>
  <div class="house gold-type gold-type--dark">{HOUSE_AR}</div>
  <div class="name-rule gold-block gold-block--dark"></div>
  <p class="scope-ar">{SCOPE_AR}</p>

  <div class="ident">
    <div class="ident-rule"></div>
    <div class="ident-office">PERSONAL OFFICE</div>
    <div class="ident-name letterpress">IMAM AHMAD IBROHIM SULAIMIY</div>
    <div class="ident-house">ĀL · ES · SALAM</div>
    <div class="scope-en">Academic Development<i></i>Islamic Da&lsquo;wah<i></i>International Relations<i></i>Private &amp; Civic Affairs</div>
  </div>

  <!-- ══ THE RED CHANNEL — the binding section turned through 90° ══ -->
  <div class="redch-steel steel-block steel-block--dark"></div>
  <div class="redch field-red"></div>
  <div class="redch-in">
    <span class="en">OFFICIAL CORRESPONDENCE</span>
    <span class="ar">مراسلة رسمية</span>
  </div>
  <div class="redch-gold gold-block gold-block--rich"></div>
'''

def register(ref="", date="", date_sub="", to_name="", to_role="", subject=""):
    blank = '&nbsp;'
    tpl = " register--blank" if not (ref or to_name) else ""
    return f'''
  <div class="register{tpl}">
    <div class="reg-pair">
      <div class="reg-to">
        <span class="k">To</span>
        <div class="to-name">{to_name or blank}</div>
        <div class="to-role">{to_role or blank}</div>
      </div>
      <div class="reg-file">
        <div class="rf"><span class="k">Ref.</span><span class="v lat"><span class="ref">{ref or blank}</span></span></div>
        <div class="rf"><span class="k">Date</span><span class="v">{date or blank}</span></div>
        <div class="rf"><span class="k"></span><span class="v sub">{date_sub or blank}</span></div>
      </div>
    </div>
    <div class="reg-hair gold-block"></div>
    <div class="reg-subject"><span class="k">Subject</span><span class="s">{subject or blank}</span></div>
  </div>
'''

SECURITY = f'''
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
  <span class="watermark"><img src="{AT}/insignia-deboss.png" alt="" aria-hidden="true"></span>
'''

def foot(fa, fe):
    strip = ("المكتب الخاص · الإمام أحمد بن إبراهيم السليمي (آل سلام) · "
             "PERSONAL OFFICE · ĀL-ES-SALAM · ") * 6
    return f'''
  <div class="microtext">{strip}</div>
  <div class="foot-rule gold-block"></div>
  <div class="foot">
    <span class="contact">+234&nbsp;810&nbsp;430&nbsp;2087<i></i>+44&nbsp;7961&nbsp;869638<i></i>abisulaimiycollege@gmail.com</span>
    <span class="folio"><span class="ar">{fa}</span><span class="sep">·</span>{fe}</span>
  </div>
'''

SIGNATURES = f'''
  <!-- The principal signs. The office that prepared the letter is identified
       beneath, deliberately smaller: a private office, not a ministry. On an
       English letter the Latin form leads and the Arabic stands under it —
       the same two lines in the same two founts, in the other order. -->
  <div class="signatures">
    <div class="sig--principal sig--en">
      <div class="sig-space"><img src="{AT}/signature-imam.png"
           alt="Signature of Imam Ahmad Ibrohim Sulaimiy"></div>
      <div class="sig-rule gold-block"></div>
      <div class="sig-lat">Imam Ahmad Ibrohim Sulaimiy</div>
      <div class="sig-ar">الإمام أحمد بن إبراهيم السليمي (آل سلام)</div>
      <div class="sig-role">Personal Office &nbsp;·&nbsp; المكتب الخاص</div>
    </div>
    <div class="sig--issuing sig--en">
      <div class="sig-space--sm"><img src="{AT}/signature-abdullah.png"
           alt="Signature of Abdullah Sulaimiy"></div>
      <div class="sig-rule--fine"></div>
      <div class="sig-lat">Abdullah Sulaimiy <span class="cred">(SMPr · MMJ · Op-Ed)</span></div>
      <div class="sig-ar">أ. عبد الله السليمي</div>
      <div class="sig-role">Communications &amp; Internal Relations</div>
    </div>
  </div>
'''

def signature_solo(lat, role="Personal Office &nbsp;·&nbsp; المكتب الخاص"):
    """Personal correspondence carries ONE hand. The office's own second
       signatory (Communications & Internal Relations) countersigns official
       correspondence and has no business under a private letter, so the block
       is the principal's alone. The furniture is the atelier's, untouched; on
       an English letter the overlay has already ranged it to the left."""
    return f'''
  <div class="signatures">
    <div class="sig--principal sig--en">
      <div class="sig-space"><img src="{AT}/signature-imam.png"
           alt="Signature of Imam Ahmad Ibrohim Sulaimiy"></div>
      <div class="sig-rule gold-block"></div>
      <div class="sig-lat">{lat}</div>
      <div class="sig-ar">{NAME_AR} {HOUSE_AR}</div>
      <div class="sig-role">{role}</div>
    </div>
  </div>
'''

def cont_head(ref=None):
    ref = ref or REF
    return f'''
  <div class="cont-plate field-sapphire"><div class="plate-guil">
{GUIL}
  </div></div>
{edge(full=True)}{pier(ref)}
{medallion("cont-med medallion")}
  <div class="cont-ref">REF. <span class="ref">{ref}</span><br><span class="k">CONTINUATION</span></div>
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
# The English counterpart of the Arabic specimen, not a translation of it: the
# same letter as this office would have written it in English. The register is
# raised in the same way — nothing here asks leave to address the recipient,
# and the visit is offered as a courtesy between peers rather than requested as
# a favour. Warmth and humility are kept; subordination is not.
#
# The diacritics are held to what the embedded Latin cut actually carries:
# ā ī ū ō and the accented Latin-1 range. The ayn and the dotted emphatics are
# not in the subset, so the transliteration is set without them rather than
# being silently dropped to a fallback face in the PDF.
LETTER_1 = [
 '<p class="salutation">As-salāmu alaykum wa rahmatu Llāhi wa barakātuh.</p>',
 '<p>It gives me great pleasure, on my own behalf and on behalf of Sultan Hanafi College '
 'for the Holy Qur&rsquo;ān, to offer Your Excellency my sincerest congratulations on the '
 'conferment upon you of the degree of Doctor of Philosophy &mdash; the crown of a '
 'distinguished scholarly course, and the fruit of sustained effort in the pursuit of '
 'knowledge and in the service of those who seek it.</p>',
 '<p>This achievement, though it appears outwardly as an academic award, is in truth an '
 'addition to the standing of the institutions honoured by your association with them, and '
 'to the academic field which you have served with your learning, your experience and your '
 'careful stewardship.</p>',
 '<p>I take this occasion to extend my congratulations also to the family of Manarul Huda '
 'International College &mdash; its administration, its faculty and its students &mdash; and '
 'to your own honoured family, upon what you have attained, and upon what we hope for you of '
 'still greater success.</p>',
]
LETTER_2 = [
 '<p>It is my pleasure to affirm to Your Excellency the concern of this Office to strengthen '
 'the bonds of scholarly cooperation between our two institutions, in a manner that serves '
 'students of knowledge and raises the standard of academic and da&rsquo;wah work alike.</p>',
 '<p>We ask God, exalted be He, to bless you in this degree, to make it a support to you in '
 'continuing your scholarly and educational giving, and to benefit Islam and the Muslims '
 'through you.</p>',
 '<p>It would give me pleasure to convey these congratulations in person, and to have the '
 'honour of visiting you at a time that suits your kind engagements.</p>',
 '<p class="close">Please accept, Your Excellency, the assurance of my highest regard and '
 'esteem.</p>',
 '<p>Wa-s-salāmu alaykum wa rahmatu Llāhi wa barakātuh.</p>',
]

# ── the completion of Sina'at al-Mutakallim al-'Arabi ───────────────────────
# A private letter, not an official minute: it shares news with a man the
# writer counts among those closest to him, and asks for du'a and for counsel.
# The register and the furniture stay exactly as the stationery sets them.
#
# ORTHOGRAPHY. The embedded Latin cut carries the macrons (a i u o) and the
# Latin-1 range and NOTHING else: the ayn, the hamza and the dotted emphatics
# are absent, and U+1E00-1EFF is DECLARED by the supplementary face while
# holding no glyph in it, so an h-dot or an s-dot would be served by whatever
# face the renderer finds and would print in the wrong fount. The
# transliteration is therefore set with the macrons and with the quote-mark
# substitutes that scholarship uses when the letters are unavailable:
# the ayn as a left single quote and the hamza as a right single quote.
# The work's own title is additionally given in Arabic script, which the
# document fount carries in full -- that is transcription of the title the
# author supplied, not an addition to it. His Arabic SUBTITLE was not
# supplied, so the subtitle stands in English alone.
REF_SINAAH = "PO/2026/10/0023"

SINAAH_1 = [
 '<p class="salutation">As-sal&#257;mu alaykum wa rahmatu Ll&#257;hi wa barak&#257;tuh.</p>',
 '<p>Dear Sir,</p>',
 '<p>All praise is due to Allah, by whose grace good works are completed.</p>',
 '<p>With a heart full of gratitude, I share with you, among those dearest to me, the '
 'completion of my Arabic work <span class="ar">&#1589;&#1606;&#1575;&#1593;&#1577; '
 '&#1575;&#1604;&#1605;&#1578;&#1603;&#1604;&#1605; &#1575;&#1604;&#1593;&#1585;&#1576;'
 '&#1610;</span> (Sin&#257;&lsquo;at al-Mutakallim al-&lsquo;Arab&#299; &mdash; The Art of '
 'the Arabic Speaker: From Purity of the Tongue to Perfection of Expression). It comes in '
 'eleven volumes, spanning 5,479 pages.</p>',
]

SINAAH_2 = [
 '<p>It would honour me if you would share in this joy, and remember the work and its '
 'author in your du&lsquo;&#257;&rsquo;. I ask Allah to accept it, to make it sincerely '
 'for His Face, and to make it of benefit to all who read it.</p>',
 '<p>The attachments accompany this letter. Your counsel and observations would be most '
 'welcome.</p>',
 '<p class="close">With love and respect,</p>',
]

SINAAH_SIG = ("Abu Abdillah, Jal&#257;lud-Deen,<br>"
              "Ahmad bin Ibrohim Abdus-Sal&#257;m, Sulaimiy")

def main():
    fa, fe = folio(1)
    open(os.path.join(ROOT, "letterhead-en.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Letterhead (English) — The Personal Office", at=AT)
        + sheet(plate() + medallion() + head() + register() + SECURITY + foot(fa, fe))
        + '</body>\n</html>\n')

    fa, fe = folio(2)
    open(os.path.join(ROOT, "letterhead-en-continuation.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Letterhead (English) — continuation sheet", at=AT)
        + sheet(cont_head() + '  <div class="field field--continued"></div>\n'
                + SECURITY + foot(fa, fe))
        + '</body>\n</html>\n')

    fa1, fe1 = folio(1, 2); fa2, fe2 = folio(2, 2)
    p1 = sheet(plate() + medallion() + head()
        + register(ref=REF,
                   date="17 September 2026",
                   date_sub="3 Rabī&rsquo; al-Ākhir 1448 AH",
                   to_name="His Excellency Dr Habibullah Yusuf Adewuyi",
                   to_role="Director, Manarul Huda International College",
                   subject="Congratulations on the conferment of the doctoral degree")
        + SECURITY
        + '  <div class="field">\n    <p class="bismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</p>\n'
          '    <div class="open-rule gold-block"></div>\n'
          '    <div class="letter letter--en">\n      ' + "\n      ".join(LETTER_1)
        + '\n    </div>\n  </div>\n' + foot(fa1, fe1))
    p2 = sheet(cont_head() + SECURITY
        + '  <div class="field field--continued">\n    <div class="letter letter--en">\n      '
        + "\n      ".join(LETTER_2) + '\n    </div>\n  </div>\n'
        + SIGNATURES + foot(fa2, fe2))
    open(os.path.join(ROOT, "letter-en-tahniah-dr-adewuyi.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Congratulations on the conferment of the doctoral degree", at=AT)
        + p1 + "\n" + p2 + '</body>\n</html>\n')

    # ── the completion letter: two sheets, the principal's hand alone ─────
    fa1, fe1 = folio(1, 2); fa2, fe2 = folio(2, 2)
    s1 = sheet(plate(REF_SINAAH) + medallion() + head()
            + register(ref=REF_SINAAH,
                       date="9 October 2026",
                       date_sub="25 Rab&#299;&lsquo; al-&#256;khir 1448 AH",
                       to_name="Alh. (Dr) Zakariya O. Anofi",
                       to_role="Chairman, Board of Governors,<br>Sultan Hanafi Royal Schools",
                       subject="Completion of Sin&#257;&lsquo;at al-Mutakallim al-&lsquo;Arab&#299; &mdash; eleven volumes, 5,479 pages")
            + SECURITY
            + '  <div class="field">\n    <p class="bismillah">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</p>\n'
              '    <div class="open-rule gold-block"></div>\n'
              '    <div class="letter letter--en">\n      ' + "\n      ".join(SINAAH_1)
            + '\n    </div>\n  </div>\n' + foot(fa1, fe1))
    s2 = sheet(cont_head(REF_SINAAH) + SECURITY
        + '  <div class="field field--continued">\n    <div class="letter letter--en">\n      '
        + "\n      ".join(SINAAH_2) + '\n    </div>\n  </div>\n'
        + signature_solo(SINAAH_SIG) + foot(fa2, fe2))
    open(os.path.join(ROOT, "letter-en-sinaah-completion.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Completion of Sina\u2018at al-Mutakallim al-\u2018Arabi", at=AT)
        + s1 + "\n" + s2 + '</body>\n</html>\n')

    names = ["letterhead-en.html", "letterhead-en-continuation.html",
             "letter-en-tahniah-dr-adewuyi.html",
             "letter-en-sinaah-completion.html"]
    print(" · ".join(names))
    if "--pdf" in sys.argv:
        for n in names:
            pdf = os.path.join(ROOT, "print", n.replace(".html", ".pdf"))
            subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                "--virtual-time-budget=20000", "--run-all-compositor-stages-before-draw",
                "--no-pdf-header-footer", f"--print-to-pdf={pdf}",
                "file://" + os.path.join(ROOT, n)], check=True, capture_output=True, timeout=300)
            print(pdf)

if __name__ == "__main__":
    main()
