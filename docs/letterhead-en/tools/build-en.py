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
import os, re, subprocess, sys

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

def head(channel_en="OFFICIAL CORRESPONDENCE", channel_ar="مراسلة رسمية"):
    """The red channel names the CLASS of correspondence, not its subject --
       the register's subject line does that. A letter written by the man
       rather than issued by the office is PERSONAL, not 'informal' (nothing
       bearing a seal, a serial and a signature is informal) and not
       'non-official' (a class should be named for what it is). The Arabic
       is مراسلة شخصية, not خاصة: the masthead already reads المكتب الخاص a
       few millimetres above, and خاصة would echo it."""
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
    <span class="en">{channel_en}</span>
    <span class="ar">{channel_ar}</span>
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

# ── the completion of Ṣināʿat al-Mutakallim al-ʿArabī ───────────────────────
# A private letter that also sets out a work: it shares news with a man the
# writer counts among those closest to him, describes the book, and asks for
# duʿāʾ and for counsel. The register and the furniture stay as the
# stationery sets them; the sections announce themselves in the first phrase
# of their own paragraph so the measure is never broken by a heading line.
#
# ORTHOGRAPHY. assets/letterhead-en.css now carries four supplementary faces
# holding the twelve codepoints the sealed v1 cut lacks, so the ayn, the
# hamza and the dotted emphatics are set as the letters they are -- al-Jāḥiẓ
# and ʿAbd al-Qāhir al-Jurjānī, not al-Jahiz and Abd al-Qahir. Those faces
# cover EB Garamond and Inter ONLY. Nothing set in Playfair Display (the
# masthead name, the signature line) or in Reem Kufi / Scheherazade New (the
# recipient's name and role) may use them. Audit every build.
#
# The author's own italics are not reproduced: the embedded cut has no italic
# face, so an <em> would be a synthesised oblique of the roman. Titles and
# technical terms stand in roman, which is what the specimen letter does.
REF_SINAAH = "PO/2026/10/0023"

# Groups that must not be broken across a sheet. Each group is a list of
# top-level blocks; the packer keeps a group whole.
SINAAH_GROUPS = [
 ['<p class="salutation">Assalāmu ʿalaykum wa raḥmatullāhi wa barakātuh,</p>'],
 # "Dear Sir," and the courtesies stay together: a salutation orphaned from
 # the prayer and the greeting that follow it would read as abruptness.
 #
 # Three facts shape this paragraph, and each rules out a stock courtesy:
 #   - they met the day the letter was written, so "I trust this finds you
 #     in good health" would be a politeness that is also a falsehood;
 #   - he travelled AND THE FAMILY TRAVELLED WITH HIM, so the greeting runs
 #     to them through him, and the prayer covers those with him;
 #   - the relationship is PROSPECTIVE, not yet contracted, so the letter
 #     carries respect and warmth but claims no familial footing. Nothing
 #     here may read as though the writer were already of the household.
 # What is left to ask after, and the only thing worth asking, is the journey.
 ['<p>Dear Sir,</p>',
  '<p>May Allah preserve you in health and faith, and grant you and those with you '
  'safety and ease in your travels. We ask after the journey, and pray that it went '
  'well. Kindly convey my greetings to the family.</p>'],
 ['<p>All praise is due to Allah, by whose grace good works are completed.</p>'],
 ['<p>With a heart full of gratitude, I share with you, among those dearest to me, the '
  'completion of my Arabic work <span class="ar">صناعة المتكلم العربي</span> '
  '(Ṣināʿat al-Mutakallim al-ʿArabī &mdash; The Art of the Arabic Speaker: From Purity '
  'of the Tongue to Perfection of Expression). It comes in eleven volumes, spanning '
  '5,479 pages.</p>'],
 ['<p><span class="run">Why this book.</span> Many who have studied Arabic for years, '
  'and know its grammar and its rhetoric, still do not find it on their tongue when '
  'they need it: in a lesson, a sermon, a meeting or a conversation. Our books teach '
  'the rules of the language and the analysis of fine speech. Few of them take the '
  'learner by the hand from knowing Arabic to speaking it well. This work was written '
  'for that gap.</p>'],
 # the run-in heading, its list and the paragraph that closes it stay together
 ['<p><span class="run">What it brings together.</span> The work gathers into one '
  'graded path what lies scattered across many books:</p>',
  '<ul>'
  '<li>Sībawayh and Ibn Jinnī on the sound and structure of the language.</li>'
  '<li>Ibn al-Jazarī on the points and qualities of the letters.</li>'
  '<li>al-Jāḥiẓ and ʿAbd al-Qāhir al-Jurjānī on bayān and the ordering of speech.</li>'
  '<li>Ibn Khaldūn on the acquired faculty (malaka).</li>'
  '</ul>',
  '<p>Alongside these, it draws on what modern studies of communication have reached. '
  'Classical texts are quoted in their own words and cited to their editions by volume '
  'and page.</p>'],
 ['<p><span class="run">Its path.</span> It opens with a question that cannot be '
  'avoided: which Arabic are we to speak? It then goes in four stages:</p>',
  '<ol>'
  '<li><span class="run">Grounding:</span> the fundamentals of speech, pronunciation, '
  'the natural Arabic sentence, and the ordering of speech.</li>'
  '<li><span class="run">Communication:</span> context, courtesy and dialogue.</li>'
  '<li><span class="run">Platforms:</span> the circle of learning, the sermon, the '
  'lecture, the interview and the meeting.</li>'
  '<li><span class="run">Mastery:</span> media, official discourse and negotiation, '
  'ending in improvisation and the acquired faculty.</li>'
  '</ol>'],
 ['<p><span class="run">The Reference volume.</span> An eleventh volume serves as a '
  'reference. It holds a Bank of Errors, which gives each error with its correction, '
  'its explanation and its severity. It also holds an applied dictionary of '
  'expressions, a dictionary of literal-translation errors, and complete model '
  'texts.</p>'],
 ['<p>It would honour me if you would share in this joy, and remember the work and its '
  'author in your duʿāʾ. I ask Allah to accept it, to make it sincerely for His Face, '
  'and to make it of benefit to all who read it. Your counsel and observations would '
  'be most welcome.</p>',
  '<p class="close">With love and respect,</p>'],
]

SINAAH_SIG = "Ahmad Sulaimiy"

# Field capacities, in mm, read off the stationery itself:
#   sheet 1      .field            top 147  bottom 245            ->  98mm
#   continuation .field--continued top  44  bottom 240            -> 196mm
#   ...but .signatures is pinned at bottom:28mm and stands ~40mm tall, so a
#   sheet that carries the hand can only run to 229mm.
CAP_FIRST, CAP_CONT, CAP_CONT_SIG = 98.0, 196.0, 185.0

GALLEY_JS = """
<script>
document.fonts.ready.then(() => {
  const MM = 96/25.4;
  const h = [...document.querySelectorAll('#galley > div')].map(g => {
    let t = 0;
    for (const c of g.children) {
      const r = c.getBoundingClientRect();
      const m = parseFloat(getComputedStyle(c).marginBottom) || 0;
      t += r.height + m;
    }
    return +(t/MM).toFixed(3);
  });
  const pre = document.createElement('pre');
  pre.id = 'H'; pre.textContent = JSON.stringify(h);
  document.body.appendChild(pre);
});
</script>
"""

def measure_groups(groups, body_cls='letter letter--en', tight=False):
    """Render every group once, at the real measure and in the real founts,
       and read its true height back out of the browser. Guessing line counts
       is how a sheet silently overruns."""
    import json, tempfile
    # group zero is the OPENER -- the Bismillah and its rule, which stand
    # inside sheet one's field above the first word and eat into its
    # capacity. Measuring it is the difference between a sheet that fits and
    # a sheet that silently overruns by the height of the invocation.
    t = ' bismillah--tight' if tight else ''
    r = ' open-rule--tight' if tight else ''
    opener = (f'<p class="bismillah{t}">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</p>'
              f'<div class="open-rule{r} gold-block"></div>')
    body = '<div id="galley">' + "".join(
        f'<div class="{body_cls}" style="width:138mm">' + "".join(g) + '</div>'
        for g in [[opener]] + groups) + '</div>'
    # the galley MUST live at ROOT or its relative stylesheet links resolve nowhere
    gp = os.path.join(ROOT, ".galley.html")
    open(gp, "w", encoding="utf-8").write(
        HEAD.format(title="galley", at=AT) + body + GALLEY_JS + "</body></html>")
    shell = _find("/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell")
    out = subprocess.run([shell, "--disable-gpu", "--no-sandbox",
        "--virtual-time-budget=25000", "--dump-dom", "file://" + gp],
        capture_output=True, timeout=300).stdout.decode("utf-8", "replace")
    os.remove(gp)
    m = re.search(r'<pre id="H">(.*?)</pre>', out, re.S)
    if not m:
        raise SystemExit("galley did not measure -- webfonts never settled")
    h = json.loads(m.group(1))
    return h[1:], h[0]          # (group heights, opener height)

def pack(groups, heights, opener=0.0):
    """Greedy, keep-with-next. Continuations are packed against the SHORTER
       capacity -- the one that leaves room for the hand -- so whichever
       sheet ends up last always has room for the signature. The few
       millimetres given up on a middle sheet are cheaper than a letter whose
       last page collides with its own signature."""
    sheets, cur, used, cap = [], [], 0.0, CAP_FIRST - opener
    for g, h in zip(groups, heights):
        if h > cap and not cur:
            raise SystemExit(f"a single keep-together group is {h:.1f}mm "
                             f"and will not fit a {cap:.0f}mm field")
        if cur and used + h > cap:
            sheets.append(cur); cur, used, cap = [], 0.0, CAP_CONT_SIG
        cur.append(g); used += h
    sheets.append(cur)
    return sheets

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

    # ── the completion letter: paginated from measured heights ───────────
    BODY = "letter letter--en letter--tight"
    heights, opener = measure_groups(SINAAH_GROUPS, BODY, tight=True)
    packed  = pack(SINAAH_GROUPS, heights, opener)
    n = len(packed)
    print(f"  sinaah: {len(SINAAH_GROUPS)} groups, "
          f"{sum(heights):.1f}mm of text (opener {opener:.1f}mm) -> {n} sheet(s) "
          f"[{', '.join(f'{sum(heights[sum(len(x) for x in packed[:i]):sum(len(x) for x in packed[:i+1])]):.1f}mm' for i in range(n))}]")

    def blocks(groups):
        return "\n      ".join(b for g in groups for b in g)

    fa, fe = folio(1, n)
    out = [sheet(plate(REF_SINAAH) + medallion()
        + head(channel_en="PERSONAL CORRESPONDENCE", channel_ar="مراسلة شخصية")
        + register(ref=REF_SINAAH,
                   date="9 October 2026",
                   date_sub="25 Rabīʿ al-Ākhir 1448 AH",
                   to_name="Alh. (Dr) Zakariya O. Anofi",
                   to_role="Chairman, Board of Governors,<br>Sultan Hanafi Royal Schools",
                   subject="Completion of Ṣināʿat al-Mutakallim al-ʿArabī &mdash; eleven volumes, 5,479 pages")
        + SECURITY
        + '  <div class="field">\n    <p class="bismillah bismillah--tight">بِسْمِ اللهِ الرَّحْمٰنِ الرَّحِيمِ</p>\n'
          '    <div class="open-rule open-rule--tight gold-block"></div>\n'
          f'    <div class="{BODY}">\n      ' + blocks(packed[0])
        + '\n    </div>\n  </div>\n'
        + (signature_solo(SINAAH_SIG) if n == 1 else "")
        + foot(fa, fe))]
    for i in range(1, n):
        fa, fe = folio(i + 1, n)
        out.append(sheet(cont_head(REF_SINAAH) + SECURITY
            + f'  <div class="field field--continued">\n    <div class="{BODY}">\n      '
            + blocks(packed[i]) + '\n    </div>\n  </div>\n'
            + (signature_solo(SINAAH_SIG) if i == n - 1 else "")
            + foot(fa, fe)))
    open(os.path.join(ROOT, "letter-en-sinaah-completion.html"), "w", encoding="utf-8").write(
        HEAD.format(title="Completion of Ṣināʿat al-Mutakallim al-ʿArabī", at=AT)
        + "\n".join(out) + '</body>\n</html>\n')

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
