"""HTML builders for the PDF master: cover, title page, openers, diagrams and
the visual examples of Part Six. Every colour and type choice follows the
Visual & Art Direction Bible (bible/06). Markup only; styles live in print.css."""

AR_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


def ar(n):
    """Integer or string -> Arabic-Indic digits."""
    return str(n).translate(AR_DIGITS)


def rh(kind):
    return f'<i class="rh {kind}"></i>'


def dots(level, total=5):
    return '<span class="dots">' + "".join(
        rh("fill-s") if i < level else rh("line-s") for i in range(total)) + "</span>"


def badge(n):
    return f'<span class="badge b{n}"><span>{ar(n)}</span></span>'


def fig(body, num, caption, extra_class=""):
    return (f'<figure class="fig {extra_class}">{body}'
            f'<figcaption><b>{num}</b><span>{caption}</span></figcaption></figure>')


# ------------------------------------------------------------------ architecture (A4, mm)

def _rhombus(x, y, s, fill):
    return f'<path d="M{x} {y - s} L{x + s} {y} L{x} {y + s} L{x - s} {y} Z" fill="{fill}"/>'


def _mix(bg, fg, a):
    b = [int(bg[i:i + 2], 16) for i in (1, 3, 5)]
    f = [int(fg[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * a):02X}" for x, y in zip(b, f))


def arch_svg(hline=182, hline2=None, alif=True, lattice=True, frame=True, bg="#082567"):
    """Architectural frame for full-bleed pages. Colours are pre-mixed with the page
    colour instead of using opacity (Chromium drops group opacity on SVG strokes in PDF)."""
    gold = "#C9A227"
    line = _mix(bg, gold, 0.9)
    faint = _mix(bg, gold, 0.45)
    lat = _mix(bg, "#E1C46A", 0.06)
    parts = ['<svg class="arch" viewBox="0 0 210 297" preserveAspectRatio="none" aria-hidden="true">']
    if lattice:
        for c in range(-297, 211, 15):
            parts.append(f'<line x1="{c}" y1="0" x2="{c + 297}" y2="297" stroke="{lat}" stroke-width="0.2"/>')
        for c in range(0, 508, 15):
            parts.append(f'<line x1="{c}" y1="0" x2="{c - 297}" y2="297" stroke="{lat}" stroke-width="0.2"/>')
    if frame:
        parts.append(f'<rect x="12" y="12" width="186" height="273" fill="none" stroke="{line}" stroke-width="0.3"/>')
    if alif:
        parts.append(f'<line x1="40" y1="12" x2="40" y2="285" stroke="{line}" stroke-width="0.3"/>')
    if hline:
        parts.append(f'<line x1="12" y1="{hline}" x2="198" y2="{hline}" stroke="{line}" stroke-width="0.3"/>')
        if alif:
            parts.append(_rhombus(40, hline, 1.6, gold))
        parts.append(_rhombus(198, hline, 1.6, gold))
    if hline2:
        parts.append(f'<line x1="40" y1="{hline2}" x2="198" y2="{hline2}" stroke="{faint}" stroke-width="0.3"/>')
    if alif:
        parts.append(_rhombus(40, 12, 1.6, gold))
        parts.append(_rhombus(40, 285, 2.2, "#B21F35"))
    parts.append('</svg>')
    return "".join(parts)


# ------------------------------------------------------------------ cover, title page, back

def cover(date_line):
    return f'''
<section class="cover-page" aria-label="الغلاف">
  {arch_svg(hline=182, hline2=226)}
  <div class="cv-kick"><span>الدليل التحريري والعلمي</span><span class="en">Editorial &amp; Scholarly Bible</span></div>
  <div class="cv-mark foil"><span>صناعة</span><span>المتكلّم العربي</span></div>
  <p class="cv-sub">من سلامة اللسان إلى حسن البيان</p>
  <div class="cv-doc">
    <p class="t">الدليل التحريري والعلمي</p>
    <p class="s">الوثيقة التأسيسية الحاكمة لكتب المنظومة وبرامجها وموادها</p>
  </div>
  <div class="cv-ed">
    <span>الإصدار ١٫٠<i class="sep" aria-hidden="true"></i><span class="en">Edition 1.0 · PDF Master</span></span>
    <span class="d">{date_line}</span>
  </div>
</section>'''


def title_page(date_line, n_decisions):
    mark = ('<svg viewBox="0 0 20 40" width="5mm" height="10mm" aria-hidden="true">'
            '<line x1="10" y1="1" x2="10" y2="31" stroke="#C9A227" stroke-width="1.2"/>'
            '<path d="M10 30 L14 34 L10 38 L6 34 Z" fill="#B21F35"/></svg>')
    return f'''
<section class="title-page" aria-label="صفحة العنوان">
  {arch_svg(hline=None, alif=False, lattice=False, bg="#F8F6F0")}
  <div class="tp-in">
    {mark}
    <div class="tp-mark">صناعة المتكلّم العربي</div>
    <div class="tp-sub">من سلامة اللسان إلى حسن البيان</div>
    <div class="tp-title">الدليل التحريري والعلمي</div>
    <div class="tp-en">Editorial &amp; Scholarly Bible</div>
    <div class="tp-desc">الوثيقة التأسيسية الحاكمة لكتب المنظومة وبرامجها وموادها</div>
    <div class="tp-rule"><i></i></div>
    <div class="tp-meta">
      <div><small>الإصدار</small><b>١٫٠ <span class="en">(Edition 1.0)</span></b></div>
      <div><small>النسخة</small><b><span class="en">PDF Master</span> · للطباعة والشاشة</b></div>
      <div><small>تاريخ الإصدار</small><b>{date_line}</b></div>
    </div>
    <div class="tp-status">الحالة: مُعَدّ للاعتماد — {ar(n_decisions)} قرارًا معلّقًا</div>
  </div>
  <div class="tp-aud"><b>تُشارَك هذه الوثيقة مع</b>لجنة العلماء · لجنة المناهج · المؤلفين · المحررين · المصممين · المدربين · فريق إنتاج الكتب · فريق إنتاج المواد الصوتية والرقمية</div>
</section>'''


def back_cover():
    return f'''
<section class="back-page" aria-label="الغلاف الخلفي">
  {arch_svg(hline=None, alif=False, bg="#060E26")}
  <div class="bk-alif"></div>
  <div class="bk-t">
    <p class="m"><span>صناعة</span><span>المتكلّم العربي</span></p>
    <p class="s">من سلامة اللسان إلى حسن البيان</p>
  </div>
  <p class="bk-q">«كلما قرأ الطالب قاعدة وجد مثالًا، وكلما رأى مثالًا وجد تحليلًا، وكلما فهم التحليل وجد تدريبًا، وكلما تدرب وجد موقفًا واقعيًا — حتى يصير الكلام العربي الفصيح عنده ملكةً لا محفوظات.»</p>
  <div class="bk-f">الدليل التحريري والعلمي · الإصدار ١٫٠<span class="en">Editorial &amp; Scholarly Bible — Edition 1.0 — PDF Master</span></div>
</section>'''


def opener(anchor, kicker, kicker_en, numeral, title, lede, items, alt=False, outline=None):
    """items: list of (label, title, href)."""
    lis = "".join(
        f'<li><span>{lab}</span><b><a href="#{href}">{t}</a></b></li>' for lab, t, href in items)
    cls = "opener alt" if alt else "opener"
    bg = "#060E26" if alt else "#082567"
    num_html = f'<div class="op-num foil">{numeral}</div>' if numeral else ""
    data = f' data-outline="{outline}"' if outline else ""
    return f'''
<section class="{cls}" id="{anchor}">
  {arch_svg(hline=178, bg=bg)}
  <div class="op-kick"><span>{kicker}</span><span class="en">{kicker_en}</span></div>
  {num_html}
  <h1 class="op-title"{data}>{title}</h1>
  <p class="op-lede">{lede}</p>
  <div class="op-list"><p class="h">في هذا الجزء</p><ol>{lis}</ol></div>
  <div class="op-foot"><span>صناعة المتكلّم العربي · الدليل التحريري والعلمي</span><span>الإصدار ١٫٠</span></div>
</section>'''


# ------------------------------------------------------------------ Part 1

def mastery_steps(num):
    steps = [
        ("s1", "معرفة العربية", "يعرف القاعدة"),
        ("s2", "استعمال العربية", "يتكلم بها"),
        ("s3", "حسن استعمال العربية", "يتكلم بما يناسب"),
        ("s4", "امتلاك الملكة الشفهية", "يرتجل المناسب بلا تكلف"),
    ]
    body = '<div class="steps">' + "".join(
        f'<div class="step {c}"><span class="n">الدرجة {ar(i + 1)}</span><b>{t}</b><span>{d}</span></div>'
        for i, (c, t, d) in enumerate(steps)) + '</div>'
    return fig(body, num, "الدرجات الأربع التي ينقل المشروعُ المتعلمَ عبرها، من معرفة القاعدة إلى امتلاك الملكة.")


# ------------------------------------------------------------------ Part 2

def context_card_template(num):
    fields = ["المتكلم", "المخاطَب", "العلاقة بينهما", "المكان", "الزمان أو المناسبة",
              "الغرض", "الأثر المطلوب", "الزمن المتاح"]
    rows = "".join(f'<div><dt>{f}</dt><dd class="blank"></dd></div>' for f in fields)
    rows += f'<div><dt>درجة الرسمية</dt><dd>{dots(0)} <span style="color:#6B655D">من ١ (أسري) إلى ٥ (شديد الرسمية)</span></dd></div>'
    body = f'<div class="ctx"><span class="lbl">بطاقة المقام</span><dl>{rows}</dl></div>'
    return fig(body, num, "بطاقة المقام: إطار إلزامي فوق كل نموذج كلامي مهم، تُملأ حقولها قبل كتابة النموذج.")


def six_model(num):
    # positions: (right %, top %) of node centres
    nodes = [
        (14, 16, "مَن؟", "المتكلم"),
        (14, 50, "لِمَن؟", "المخاطَب"),
        (14, 84, "أين ومتى؟", "المقام"),
        (86, 28, "ماذا؟", "الموضوع"),
        (86, 72, "لماذا؟", "الغرض والأثر"),
    ]
    W, H = 170.0, 64.0
    lines = []
    for r, t, *_ in nodes:
        cx = W * (1 - r / 100.0)
        cy = H * t / 100.0
        edge = cx - 18 if r < 50 else cx + 18
        lines.append(f'<line x1="{edge:.1f}" y1="{cy:.1f}" x2="85" y2="39" stroke="#C9A227" stroke-width="0.35"/>')
        lines.append(_rhombus(round(edge, 1), round(cy, 1), 1.1, "#C9A227"))
    svg = f'<svg viewBox="0 0 {W:.0f} {H:.0f}" preserveAspectRatio="none" aria-hidden="true">{"".join(lines)}</svg>'
    node_html = "".join(
        f'<div class="node" style="right:{r}%;top:{t}%"><b>{q}</b><span>{d}</span></div>'
        for r, t, q, d in nodes)
    core = ('<div class="core" style="right:50%;top:50%"><div><b>كيف؟</b>'
            '<span>الصياغة · الأداء</span><span>البنية · التفاعل</span></div></div>')
    body = f'<div class="six">{svg}{node_html}{core}</div>'
    return fig(body, num, "النموذج السداسي: خمسة أسئلة هي المدخلات، و«كيف؟» مُخرَج يُشتق منها.")


# ------------------------------------------------------------------ Part 3

def flow(items, num, caption, levels=None, goal_last=False):
    out = []
    for i, it in enumerate(items):
        cls = "st"
        if levels:
            cls += f" l{levels[i]}"
        if goal_last and i == len(items) - 1:
            cls += " goal"
        out.append(f'<span class="{cls}">{it}</span>')
        if i < len(items) - 1:
            out.append('<span class="ar">←</span>')
    return fig(f'<div class="flow">{"".join(out)}</div>', num, caption)


def example_code(num):
    segs = [("م٤", "المجلد"), ("ب٥", "الباب"), ("ف٢", "الفصل"), ("مث١٧", "المثال")]
    body = '<div class="seg">' + "".join(f'<span><b>{c}</b><small>{l}</small></span>' for c, l in segs) + '</div>'
    return fig(body, num, "رمز المثال الثابت: [م٤-ب٥-ف٢-مث١٧] = المجلد ٤، الباب ٥، الفصل ٢، المثال ١٧؛ ليُحال إليه في دليل المعلم وبنك الاختبارات.")


def ladder_template(num):
    labels = ["المتكلم غير الناجح", "المتكلم المقبول", "المتكلم الناجح", "المتكلم الرفيع (اختياري)"]
    tiers = "".join(
        f'<div class="tier t{i + 1}">{badge(i + 1)}<div><span class="lbl">{lab}</span>'
        f'<div class="ph">«…»</div></div></div>' for i, lab in enumerate(labels))
    body = ('<div class="ctx-strip"><b>بطاقة المقام:</b> المتكلم · المخاطَب · العلاقة · المكان · '
            'الغرض · الأثر · الرسمية · الزمن</div>'
            f'<div class="ladder" style="margin-top:2.2mm">{tiers}</div>')
    return fig(body, num, "قالب العرض: بطاقة المقام، ثم الدرجات المتدرجة؛ والرابعة للمواقف المحورية وحدها.", "fig-flow")


def dialogue_structure(num):
    qs = ["لماذا نجحت البداية أو أخفقت؟", "ما العبارة المناسبة؟ وما التي كان ينبغي تجنبها؟",
          "كيف كانت النبرة؟", "هل كان الجواب طويلًا أو مختصرًا أكثر من اللازم؟",
          "هل أجاب عن السؤال أم ابتعد عنه؟", "هل ظهرت الثقة أم الغرور أم الضعف؟",
          "هل الأسلوب طبيعي؟ هل فيه أثر ترجمة حرفية؟"]
    q_html = '<ul class="qgrid">' + "".join(f"<li>{q}</li>" for q in qs) + "</ul>"
    steps = [
        ("بطاقة المقام", ""),
        ("الحوار الأول", "كما يقع، وفيه أخطاء المتعلم"),
        ("التحليل سطرًا سطرًا", q_html),
        ("النسخة المحسّنة", "كاملة لا مقتطعة"),
        ("جدول «ماذا تغيّر؟»", "السطر، وقبل، وبعد، والسبب"),
        ("تمرين", "أدِّ الحوار في ثنائي، ثم بدّل أحد عناصر المقام وأعد الأداء"),
    ]
    lis = "".join(
        f'<li>{badge(3).replace(">٣<", f">{ar(i + 1)}<")}<div><b>{t}</b>'
        + (f' <span class="d">— {d}</span>' if d and not d.startswith("<") else d) + '</div></li>'
        for i, (t, d) in enumerate(steps))
    body = f'<div class="panel"><ol class="nsteps">{lis}</ol></div>'
    return fig(body, num, "بنية الحوار التعليمي الكامل: ست خطوات إلزامية في كل حوار ممتد.")


def error_card_template(num):
    rows = [("الخطأ", "«…»"), ("التصحيح", "«…»"), ("التعليل", "لماذا هو خطأ؟"),
            ("كيف يحدث؟", "سبب محتمل، بصيغة غير تعميمية"),
            ("كيف يسمعه العربي؟", "الانطباع أو سوء الفهم الذي يسببه"),
            ("البديل الطبيعي", "كيف يقولها العربي الفصيح بسلاسة؟"),
            ("التدريب", "خمس جمل على الأقل لتثبيت النمط")]
    dl = "".join(f'<dt>{k}</dt><dd class="ph">{v}</dd>' for k, v in rows)
    body = (f'<div class="card"><div class="card-h"><b>بطاقة الخطأ</b>'
            f'<span class="meta">الرمز: خ-…</span><span class="meta">الخطورة: …</span>'
            f'<span class="meta">المستوى: م…</span></div>'
            f'<div class="card-b"><dl class="kv">{dl}</dl></div></div>')
    return fig(body, num, "القالب الموحد لبطاقة الخطأ في بنك الأخطاء.")


# ------------------------------------------------------------------ Part 5

def qc_form(num):
    items = ["المراجعات الإحدى عشرة", "أسئلة الاعتماد", "الحدود الدنيا للأمثلة",
             "مصفوفة التنويع", "الأفعال العشرة", "الوسوم التوثيقية معالجة"]
    checks = '<ul class="checks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    status = '<ul class="checks">' + "".join(f"<li>{i}</li>" for i in ["مسودة", "قيد المراجعة", "معتمد"]) + "</ul>"
    body = (f'<div class="card"><div class="card-h"><b>سجل اعتماد الفصل</b><span class="meta">يُرفق بكل فصل</span></div>'
            f'<div class="card-b"><dl class="kv" style="grid-template-columns:30mm 1fr">'
            f'<dt>الفصل · الإصدار · التاريخ</dt><dd class="ph">&nbsp;</dd>'
            f'<dt>قائمة الفحص</dt><dd>{checks}</dd>'
            f'<dt>ملاحظات</dt><dd><div class="rule-line"></div><div class="rule-line"></div></dd>'
            f'<dt>الحالة</dt><dd>{status}</dd></dl></div></div>')
    return fig(body, num, "سجل اعتماد الفصل: نموذج قابل للطباعة يرافق كل فصل حتى اعتماده.")


# ------------------------------------------------------------------ Part 6

def equation(num):
    terms = ["مكانة الإصدارات السعودية الرائدة", "رصانة النشر الأكاديمي الدولي",
             "التراث الفكري العربي الكلاسيكي", "التصميم التحريري الفاخر المعاصر"]
    cells = []
    for i, t in enumerate(terms):
        cells.append(f'<div class="term">{t}</div>')
        if i < 3:
            cells.append('<div class="op">+</div>')
    body = (f'<div class="eq">{"".join(cells)}</div>'
            '<div class="eq-res"><span class="op">=</span><b>هوية أصيلة خاصة بـ<span>«صناعة المتكلّم العربي»</span> وحدها</b></div>')
    return fig(body, num, "المعادلة البصرية: نأخذ المستوى من أربعة مصادر، ونصنع هوية لا تُنسب إلا إلى المشروع.")


def dna(num):
    body = '''<div class="dna">
  <div class="d-sap"><b>الياقوتي</b><div><div class="m">المرجعية · العقل · المكانة</div><div class="x">Sapphire #082567</div></div></div>
  <div class="d-gold"><b>الذهبي</b><div><div class="m">التميّز · التراث · الامتياز</div><div class="x">Gold #C9A227 – #E1C46A</div></div></div>
  <div class="d-pearl"><b>اللؤلؤي</b><div><div class="m">الصفاء · الرقي · المعرفة</div><div class="x">Pearl #F8F6F0</div></div></div>
  <div class="d-crim"><b>القرمزي</b><div><div class="m">الطاقة · التوكيد · الدفء</div><div class="x">Crimson #A51C30</div></div></div>
</div>'''
    return fig(body, num, "الحمض البصري: أربعة ألوان تُعرف بها المنظومة من بعيد.")


def budget(num):
    def bar(parts):
        return '<div class="bar">' + "".join(f'<i class="{c}" style="width:{w}%"></i>' for c, w in parts) + '</div>'
    rows = [
        ("صفحة قراءة وتدريب", [("bp", 65), ("bs", 20), ("bg", 5), ("bc", 2), ("bo", 8)]),
        ("فاتحة جزء أو باب", [("bp", 5), ("bs", 87), ("bg", 7), ("bc", 1)]),
        ("الغلاف (المفهوم أ)", [("bp", 4), ("bs", 88), ("bg", 7), ("bc", 1)]),
    ]
    html = '<div class="budget">' + "".join(
        f'<div class="b-row"><span>{lab}</span>{bar(p)}</div>' for lab, p in rows) + '</div>'
    html += ('<ul class="legend"><li><i style="background:#F8F6F0"></i>لؤلؤي</li>'
             '<li><i style="background:#082567"></i>ياقوتي وليلي</li>'
             '<li><i style="background:linear-gradient(135deg,#B88A20,#E1C46A,#C9A227)"></i>ذهبي</li>'
             '<li><i style="background:#A51C30"></i>قرمزي</li>'
             '<li><i class="bo"></i>غيرها</li></ul>')
    return fig(f'<div class="panel">{html}</div>', num,
               "ميزانية اللون بقيم تمثيلية داخل الحدود المقررة؛ يضبطها المخرج الفني صفحةً صفحة.")


def contrast(num):
    pairs = [
        ("#F8F6F0", "#1F2329", "نصّ المتن", "الفحمي على اللؤلؤي", "14.6 : 1", "ok", "✔ مسموح"),
        ("#F8F6F0", "#082567", "عنوان الفصل", "الياقوتي العميق على اللؤلؤي", "13.2 : 1", "ok", "✔ مسموح"),
        ("#F8F6F0", "#A51C30", "تنبيه", "القرمزي على اللؤلؤي", "6.9 : 1", "ok", "✔ مسموح"),
        ("#F8F6F0", "#7F5F12", "معيار الإتقان", "ذهبي الحبر على اللؤلؤي", "5.5 : 1", "ok", "✔ مسموح"),
        ("#082567", "#D4AF37", "صناعة المتكلّم", "الذهبي الطازج على الياقوتي العميق", "6.8 : 1", "ok", "✔ مسموح"),
        ("#174EA6", "#D4AF37", "عنوان كبير", "الذهبي الطازج على الياقوتي المضيء", "3.7 : 1", "big", "◐ للكبير فقط"),
        ("#F8F6F0", "#C9A227", "نصّ ذهبي", "الذهبي المصقول على اللؤلؤي", "2.2 : 1", "no", "✘ ممنوع"),
        ("#F8F6F0", "#E1C46A", "نصّ ذهبي", "الذهبي الفاتح على اللؤلؤي", "1.6 : 1", "no", "✘ ممنوع"),
    ]
    tiles = "".join(
        f'<div class="pair"><div class="smp" style="background:{bg};color:{fg}"><b>{t}</b><span>{s}</span></div>'
        f'<div class="meta"><span class="ltr">{r}</span><span class="v-{v}">{vt}</span></div></div>'
        for bg, fg, t, s, r, v, vt in pairs)
    return fig(f'<div class="pairs">{tiles}</div>', num,
               "أمثلة بصرية من مصفوفة التباين: الذهب على الفاتح زينة لا نص، و«ذهبي الحبر» بديله للنصوص.")


def foil(num):
    stops = [(0, "#B88A20"), (24, "#E1C46A"), (46, "#C9A227"), (56, "#F2DC8F"), (70, "#C9A227"), (100, "#B88A20")]
    marks = "".join(f'<span style="left:{p}%">{h}</span>' for p, h in stops)
    body = f'<div class="foil-bar"></div><div class="stops">{marks}</div>'
    return fig(f'<div class="panel" style="padding-bottom:2mm">{body}</div>', num,
               "محاكاة الرقائق الذهبية على الشاشة: تدرج بزاوية ١٣٥° ومحطاته؛ والقيمة المسطحة البديلة #C9A227.")


def type_specimen(num):
    rows = [
        ("حرف العرض", "Reem Kufi", '<div class="s-display">صناعة المتكلّم</div>'),
        ("الحرف التحريري", "Amiri Bold", '<div class="s-edit">الباب الخامس: المقام — مَن يتكلم؟ ولمن؟</div>'),
        ("حرف القراءة", "Amiri", '<div class="s-read">حرف القراءة يحمل المتن الطويل: الشرح، والحوار، والشاهد. فإذا طال الدرس لم يتعب القارئ، وإذا شُكِّل النص لم تصطدم حركاته.</div>'),
        ("النص المشكول للإلقاء", "Amiri · 200%+", '<div class="s-voc">إِنَّ الكَلِمَةَ أَمانَةٌ <span class="pm">/</span> فَأَحْسِنْ حَمْلَها <span class="pm">//</span> وَأَحْسِنْ <span class="stress">أَداءَها</span> <span class="pm">↓ //</span></div>'),
        ("الحرف الوظيفي", "IBM Plex Sans Arabic", '<div class="s-func"><span><b>تمرين ٣:</b> التحويل</span><span><b>الزمن:</b> ٥ دقائق</span><span><b>الرسمية:</b> ٤ من ٥</span><span><b>المستوى:</b> م٢</span></div>'),
        ("الحرف القرآني", "Amiri Quran (screen) · KFGQPC (print)", '<div class="s-quran"><span class="br">﴿</span>وَاقْصِدْ فِي مَشْيِكَ وَاغْضُضْ مِن صَوْتِكَ<span class="br">﴾</span></div>'),
        ("المرافق اللاتيني", "Cormorant Garamond · IBM Plex Sans", '<div class="s-pair"><span class="a">السجل اللغوي</span><span class="l">(Register)</span><span class="l2">Pace · Pause · Pitch</span></div>'),
    ]
    html = '<div class="tspec">' + "".join(
        f'<div class="trow"><div class="m"><b>{a}</b><span>{b}</span></div><div>{c}</div></div>'
        for a, b, c in rows) + '</div>'
    return fig(f'<div class="panel">{html}</div>', num,
               "الأدوار الحرفية بالخطوط المفتوحة الترخيص؛ والآية للتمثيل (لقمان: ١٩)، وتُنقل في الكتب من مصدر المصحف الموثق.")


def nuqta(num):
    prim = f'''<div class="prims">
  <div class="prim"><svg viewBox="0 0 84 84"><path d="M42 10 L74 42 L42 74 L10 42 Z" fill="#123C8C"/></svg><b>النقطة</b><span>التعداد والمقاييس وإطار رقم الصفحة</span></div>
  <div class="prim"><svg viewBox="0 0 84 84"><line x1="42" y1="6" x2="42" y2="66" stroke="#C9A227" stroke-width="2"/><path d="M42 64 L48 70 L42 76 L36 70 Z" fill="#B21F35"/></svg><b>الألف</b><span>الخط البنائي في الأغلفة والفواتح</span></div>
  <div class="prim"><svg viewBox="0 0 84 84"><circle cx="42" cy="42" r="30" fill="none" stroke="#123C8C" stroke-width="1.5"/>{"".join(_rhombus(x, y, 3.5, "#123C8C") for x, y in [(42, 12), (42, 72), (68, 27), (68, 57), (16, 27), (16, 57)])}{_rhombus(42, 42, 5, "#C9A227")}</svg><b>الدائرة</b><span>النموذج السداسي حول «كيف؟»</span></div>
</div>'''
    formality = [(5, "شديد الرسمية", "لقاء وزير، وفد رسمي"), (4, "رسمي", "مقابلة، محاضرة، خطبة"),
                 (3, "شبه رسمي", "حديث مع أستاذ بعد الدرس"), (2, "ودي", "الزملاء والأصدقاء"),
                 (1, "أسري", "الوالدان والإخوة والأبناء")]
    f_html = "".join(f'<li>{dots(l)}<span><b>{ar(l)} {n}</b> · {e}</span></li>' for l, n, e in formality)
    sev = [("fill-c", "قاتل", "«إنشاء الله»"), ("half-c", "مغيّر للمعنى", "التباس «ضلّ» بـ«ظلّ»"),
           ("half-g", "لافت", "«سأعطي محاضرة»"), ("line-g", "هنة", "خلاف الأولى")]
    s_html = "".join(f'<li><span class="dots">{rh(k)}</span><span><b>{n}</b> · {e}</span></li>' for k, n, e in sev)
    comp = [(1, "غير ناجح", "كما يقع فيه المتعلم"), (2, "مقبول", "يؤدي الغرض ولا يبلغ الغاية"),
            (3, "ناجح", "فصيح طبيعي مناسب للمقام"), (4, "رفيع", "لمسة بيان بلا تكلف")]
    c_html = "".join(f'<li><span class="dots">{badge(n)}</span><span><b>{t}</b> · {d}</span></li>' for n, t, d in comp)
    scales = (f'<div class="scales"><div><p class="h">سلّم الرسمية</p><ul class="slist">{f_html}</ul></div>'
              f'<div><p class="h">درجات خطورة الخطأ</p><ul class="slist">{s_html}</ul></div>'
              f'<div><p class="h">درجات المقارنة</p><ul class="slist">{c_html}</ul></div></div>')
    return fig(f'<div class="panel">{prim}{scales}</div>', num,
               "نظام النقطة: وحدة واحدة تُبنى منها العلامات كلها، والدرجة تُعرف بالشكل والرقم معًا لا باللون وحده.")


def page_grid(num):
    def page(side):
        # side 'r' = right-hand page (outer edge on the right), 'l' = left-hand page
        if side == "r":
            area = "left:10%;right:8%"
            rail = "right:0;width:25%"
            main = "left:0;width:73%"
        else:
            area = "right:10%;left:8%"
            rail = "left:0;width:25%"
            main = "right:0;width:73%"
        cols = '<div class="cols">' + "<i></i>" * 12 + '</div>'
        return (f'<div class="gpage"><div class="area" style="{area}">{cols}'
                f'<div class="main" style="{main}"></div><div class="rail" style="{rail}"></div>'
                f'<div class="lab" style="{main.split(";")[0]};width:73%;top:46%">المتن<br>٨–٩ أعمدة</div>'
                f'<div class="lab g" style="{rail.split(";")[0]};width:25%;top:46%">العمود<br>الجانبي</div>'
                f'</div></div>')
    body = f'<div class="gridfig">{page("r")}{page("l")}</div>'
    body += ('<div class="gnotes"><div><b>الهامش الداخلي</b> ٢٠ مم جهة التجليد</div>'
             '<div><b>الهامش الخارجي</b> ١٦ مم، ويليه العمود الجانبي</div>'
             '<div><b>العلوي والسفلي</b> ١٨ مم و٢٤ مم</div>'
             '<div><b>الشبكة</b> ١٢ عمودًا في مساحة النص</div>'
             '<div><b>المتن</b> ٨–٩ أعمدة، ٩–١٣ كلمة في السطر</div>'
             '<div><b>العمود الجانبي</b> ٣ أعمدة: أرقام الأسطر، وللمدرب، ورموز الصوت</div></div>')
    return fig(f'<div class="panel">{body}</div>', num,
               "شبكة كتاب الطالب (٢٠×٢٦ سم) في صفحتين متقابلتين: الهوامش مرآوية، والعمود الجانبي على الجهة الخارجية.")


def _cover_a():
    return '''<div class="cover cvA"><svg class="cv-svg" viewBox="0 0 200 260">
<g fill="none" stroke="#C9A227" stroke-width=".8"><rect x="12" y="12" width="176" height="236"/><line x1="40" y1="12" x2="40" y2="248"/><line x1="12" y1="170" x2="188" y2="170"/><line x1="40" y1="206" x2="188" y2="206" stroke="#5F5D4A"/></g>
<g fill="#C9A227"><path d="M40 166 l4 4 -4 4 -4 -4z"/><path d="M188 166 l4 4 -4 4 -4 -4z"/><path d="M40 8 l4 4 -4 4 -4 -4z"/></g><path d="M40 243 l5 5 -5 5 -5 -5z" fill="#B21F35"/></svg>
<div class="t"><div class="ht foil"><span>صناعة</span><span>المتكلّم العربي</span></div><p>من سلامة اللسان إلى حسن البيان</p></div>
<div class="vol"><small>المجلد الأول</small><b>التأسيس</b></div></div>'''


def _cover_b():
    ruling = "".join(f'<line x1="0" y1="{y}" x2="200" y2="{y}" stroke="#E7E6E6" stroke-width=".6"/>' for y in range(14, 260, 13))
    return '''<div class="cover cvB"><svg class="cv-svg" viewBox="0 0 200 260">''' + ruling + '''
<g fill="none" stroke="#C9A227" stroke-width=".9"><path d="M48 142 L128 222 L48 302 L-32 222 Z"/><path d="M48 166 L104 222 L48 278 L-8 222 Z"/><path d="M48 190 L80 222 L48 254 L16 222 Z"/><line x1="48" y1="142" x2="48" y2="302"/><line x1="-32" y1="222" x2="128" y2="222"/></g>
<path d="M48 216 l6 6 -6 6 -6 -6z" fill="#C9A227"/></svg>
<div class="t"><div class="ht"><span>صناعة</span><span>المتكلّم العربي</span></div><p>المكتبة التعبيرية</p></div>
<div class="kind">مرجع مرافق</div></div>'''


def _cover_c():
    return '''<div class="cover cvC"><div class="fr1"></div><div class="fr2"></div>
<div class="t"><div class="ht foil"><span>صناعة</span><span>المتكلّم العربي</span></div><div class="dv"><i></i></div><p>من سلامة اللسان إلى حسن البيان</p></div>
<div class="ed"><small>الطبعة الرائدة</small><span>Premium Flagship Edition</span></div></div>'''


def _cover_d():
    return '''<div class="cover cvD"><div class="alif"></div>
<div class="t"><div class="ht"><span>صناعة</span><span>المتكلّم</span><span>العربي</span></div><p>من سلامة اللسان<br>إلى حسن البيان</p></div></div>'''


def covers(num):
    items = [(_cover_a(), "أ · العمارة الياقوتية", "للمجلدات الأربعة · رقائق وكبس غائر"),
             (_cover_b(), "ب · المخطوط والحداثة", "للمكتبة التعبيرية · الذهب خطوط لا نص"),
             (_cover_c(), "ج · الياقوت الملكي", "للطبعة الرائدة · عنوان مكبوس بارز"),
             (_cover_d(), "د · النقطة والألف", "شارة السلسلة · مقترح اللجنة")]
    html = '<div class="covers">' + "".join(
        f'<div class="cv-fig">{c}<div class="cap"><b>{t}</b><span>{d}</span></div></div>' for c, t, d in items) + '</div>'
    return fig(html, num, "مخططات اتجاه للمفاهيم الأربعة، لا أغلفة نهائية؛ ويُطوَّر لكل مفهوم ثلاثة بدائل قبل الحسم.")


def family(num):
    books = [
        ("background:#082567", "foil", "", "كتاب الطالب", "ياقوتي وذهب (١–٤)"),
        ("background:#F8F6F0", "", "color:#082567", "المكتبة التعبيرية", "لؤلؤي وذهب"),
        ("background:#060E26", "pfoil", "", "دليل المعلم", "ليلي وبلاتين"),
        ("background:#F8F6F0", "", "color:#082567", "كتاب التدريبات", "لؤلؤي وشريط قرمزي"),
        ("background:#060E26", "foil", "", "كتاب الصوتيات", "ليلي وذهب"),
        ("background:#082567", "foil", "", "النماذج الكاملة", "ياقوتي وإطار مزدوج"),
        ("background:#F8F6F0", "", "color:#123C8C", "بنك المواقف والاختبارات", "لؤلؤي وياقوتي"),
        ("background:radial-gradient(120% 90% at 50% 34%,#123C8C,#082567 56%,#051B4F)", "foil", "", "الطبعة الرائدة", "كسوة فاخرة وكبس"),
    ]
    cells = []
    for i, (bg, f, col, name, note) in enumerate(books):
        extra = ""
        if name == "كتاب التدريبات":
            extra = '<div class="band"></div>'
        if name == "النماذج الكاملة":
            extra = '<div style="position:absolute;inset:7%;border:.5pt solid rgba(201,162,39,.8)"></div><div style="position:absolute;inset:10%;border:.5pt solid rgba(201,162,39,.4)"></div>'
        if name == "كتاب الصوتيات":
            extra = '<div style="position:absolute;left:24%;top:14%;bottom:18%;width:1.2cqw;background:linear-gradient(180deg,#B88A20,#F2DC8F,#B88A20)"></div>'
        rule = '' if name in ("كتاب الصوتيات", "النماذج الكاملة") else '<div class="rule"></div>'
        cells.append(f'<div class="fam"><div class="bk" style="{bg}">{extra}<div class="ti {f}" style="{col}">صناعة المتكلّم</div>{rule}</div>'
                     f'<div class="cap"><b>{name}</b>{note}</div></div>')
    grid = '<div class="family">' + "".join(cells) + '</div>'
    spines = []
    for i in range(4):
        spines.append(f'<div class="spine"><span class="n foil">{ar(i + 1)}</span><span class="v">صناعة المتكلّم العربي</span><span class="n" style="font-size:6pt;color:#E1C46A">◆</span></div>')
    sp = ('<div class="spines-wrap"><div class="spines">' + "".join(spines) + '</div>'
          '<svg viewBox="0 0 52 58" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%">'
          '<line x1="49" y1="9" x2="3" y2="49" stroke="#C9A227" stroke-width=".35"/></svg></div>')
    return fig(f'<div class="panel">{grid}{sp}</div>', num,
               "نظام العائلة: لكل كتاب لونه ومعدنه؛ وإذا صُفّت المجلدات الأربعة اتصل عبر كعوبها خط ذهبي واحد.")


def spread(num):
    items = ["أنماط المتحدثين: الشيخ والخطيب والمحاضر", "أنماط المتحدثين: المذيع والمتحدث الرسمي والدبلوماسي",
             "أنماط المتحدثين: المدير والموظف والباحث والطالب", "أنماط المتحدثين: الأب والأم والضيف الجديد",
             "مخاطبة الأعلى منزلة", "مخاطبة الأقران والأدنى", "مخاطبة الجمهور العام",
             "مخاطبة الغاضب والمعترض والمسيء", "مختبر المقام: ثلاثون موقفًا"]
    lis = "".join(f"<li>{i}</li>" for i in items)
    body = f'''<div class="spread">
  <div class="pg pg-open"><div class="num foil">٠٥</div><div class="alif"></div><div class="ti">المقام</div>
    <div class="q">مَن يتكلم؟ ولمن؟ ولماذا؟<br>وأين؟ ومتى؟ وكيف؟</div><div class="tag">المستوى ٤، المرحلة الثانية: التواصل</div></div>
  <div class="pg pg-toc"><div class="h">في هذا الباب</div><ol>{lis}</ol>
    <div class="cap">الصفحة اليسرى: فهرس الباب، أو صورة تحريرية ممتدة إلى حافة الورق.</div></div>
</div>'''
    return fig(body, num, "فاتحة باب «المقام» في كتاب الطالب: تبدأ على الصفحة اليمنى لأنها أول ما يُقرأ في الكتاب العربي.")


def _tile(kind):
    ink, sap, mid, gold = "#9A968F", "#082567", "#060E26", "#C9A227"

    def lines(x1, x2, y0, y1, step, col=ink, w=0.9):
        return "".join(f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{col}" stroke-width="{w}"/>'
                       for y in range(y0, y1, step))
    body = ""
    bgc = "#F8F6F0"
    if kind == "open":
        bgc = sap
        body = (f'<rect x="42" y="16" width="34" height="18" fill="{gold}"/>'
                f'<rect x="26" y="46" width="58" height="4" fill="#F4F1E8"/><rect x="40" y="56" width="44" height="3" fill="#8C97B5"/>')
    elif kind == "quiet":
        body = lines(15, 85, 20, 34, 6)
    elif kind == "rich":
        body = lines(15, 85, 12, 36, 4) + f'<rect x="15" y="42" width="70" height="17" fill="{sap}"/>' + lines(15, 85, 66, 90, 4)
    elif kind == "dia":
        body = lines(74, 86, 14, 90, 10, "#123C8C", 1.4) + lines(12, 66, 14, 90, 5)
    elif kind == "bank":
        body = lines(14, 86, 12, 90, 3)
    elif kind == "breath":
        bgc = "#F1E8D4"
        body = f'<rect x="14" y="14" width="72" height="40" fill="#5D6780"/>' + lines(25, 75, 64, 74, 5)
    elif kind == "ex":
        body = (f'<rect x="14" y="12" width="72" height="34" fill="#FCFBF7" stroke="#123C8C" stroke-width="1"/>'
                + lines(18, 82, 20, 44, 6, "#C9C1B2")
                + f'<rect x="14" y="54" width="72" height="34" fill="#FCFBF7" stroke="#123C8C" stroke-width="1"/>'
                + lines(18, 82, 62, 86, 6, "#C9C1B2"))
    elif kind == "sim":
        body = f'<rect x="0" y="0" width="100" height="24" fill="{mid}"/><rect x="56" y="9" width="30" height="4" fill="{gold}"/>' + lines(15, 85, 36, 90, 5)
    elif kind == "mastery":
        body = f'<rect x="14" y="22" width="72" height="56" fill="none" stroke="{gold}" stroke-width="1.2"/>' + lines(22, 78, 32, 72, 7)
    return (f'<svg class="rt" viewBox="0 0 100 100" preserveAspectRatio="none">'
            f'<rect width="100" height="100" fill="{bgc}"/>{body}</svg>')


def rhythm(num):
    tiles = [("open", "فاتحة"), ("quiet", "السؤال والموقف"), ("rich", "القاعدة والشرح"),
             ("dia", "حوار"), ("dia", "حوار"), ("bank", "بنك أمثلة"), ("breath", "صفحة تنفّس"),
             ("ex", "تدريبات"), ("sim", "محاكاة"), ("mastery", "الخلاصة والإتقان")]
    lis = "".join(f'<li>{_tile(c)}<span class="c"><b>{ar(i + 1)}</b>{t}</span></li>'
                  for i, (c, t) in enumerate(tiles))
    return fig(f'<ol class="rhythm">{lis}</ol>', num,
               "إيقاع الباب النموذجي: لا تتوالى أكثر من صفحتين كثيفتين دون عنصر تنفّس.")


# ---- component gallery (Part 6, ch. 26): a study-circle scenario, not reused elsewhere

def gallery_a(num):
    ctx = ('<div class="ctx"><span class="lbl">بطاقة المقام</span><dl>'
           '<div><dt>المتكلم</dt><dd>طالب علم يحضر المجلس أول مرة</dd></div>'
           '<div><dt>المخاطَب</dt><dd>الشيخ في درس عام بالمسجد</dd></div>'
           '<div><dt>العلاقة</dt><dd>أدنى منزلة، بلا معرفة سابقة</dd></div>'
           '<div><dt>الغرض</dt><dd>الاستئذان في سؤال</dd></div>'
           '<div><dt>الأثر المطلوب</dt><dd>أن يأذن الشيخ ويطمئن إلى أدب السائل</dd></div>'
           f'<div><dt>الرسمية</dt><dd>{dots(4)} ٤ رسمي</dd></div>'
           '<div><dt>الزمن المتاح</dt><dd>جملة أو جملتان</dd></div>'
           '<div><dt>المكان</dt><dd>مجلس الدرس</dd></div></dl></div>')
    tiers = [
        (1, "المتكلم غير الناجح ✘", "يا شيخ، يا شيخ! عندي سؤال مهم جدًّا ولازم تجيبني الآن."),
        (2, "المتكلم المقبول", "يا شيخ، عندي سؤال لو سمحت."),
        (3, "المتكلم الناجح", "أحسن الله إليكم يا شيخنا، هل تأذنون لي بسؤال؟"),
        (4, "المتكلم الرفيع", "أحسن الله إليكم يا شيخنا ونفع بعلمكم، إن أذنتم لي بسؤال يسير في المسألة الأخيرة؛ فإن لم يكن هذا وقته فبعد الدرس."),
    ]
    lad = '<div class="ladder">' + "".join(
        f'<div class="tier t{n}">{badge(n)}<div><span class="lbl">{l}</span><q>{t}</q></div></div>'
        for n, l, t in tiers) + '</div>'
    return fig(f'<div class="paper paper-flow">{ctx}{lad}</div>', num,
               "بطاقة المقام والمقارنة المتدرجة في موقف جديد: الاستئذان في مجلس علم. والأشخاص افتراضيون.", "fig-flow")


def gallery_b(num):
    tbl = '''<table class="dtab"><thead><tr><th>البعد</th><th>١ غير الناجح</th><th>٢ المقبول</th><th>٣ الناجح</th></tr></thead><tbody>
<tr><th scope="row">النداء</th><td>«يا شيخ» مكررة بصوت مرتفع</td><td>نداء مجرد</td><td>دعاء ولقب مناسب</td></tr>
<tr><th scope="row">صيغة الطلب</th><td>أمر: «لازم تجيبني»</td><td>طلب مباشر</td><td>استئذان بصيغة السؤال</td></tr>
<tr><th scope="row">اللغة</th><td>عامية: «لازم»</td><td>فصيحة بسيطة</td><td>فصيحة طبيعية</td></tr>
<tr><th scope="row">مراعاة المقام</th><td>يقطع الدرس</td><td>لا يراعي توقيت الشيخ</td><td>يطلب الإذن ولا يفرض السؤال</td></tr>
</tbody></table>'''
    rule = '<div class="rule-p"><div><span class="lbl">قاعدة</span><p>غيِّر المخاطَب أو المقام يتغيّر الأسلوب، وإن بقي الموضوع واحدًا.</p></div></div>'
    defi = '<div class="def"><span class="lbl">تعريف</span><p>المقام: مجموع ظروف الكلام: المكان والزمان والمناسبة والعلاقة.</p></div>'
    warn = '<div class="warn"><span class="lbl">تنبيه</span><p>لا تقاطع الشيخ ولو كان سؤالك مهمًّا؛ انتظر فراغه من فكرته ثم استأذن.</p></div>'
    evid = ('<div class="evid"><span class="lbl">شاهد</span><p class="ayah"><span class="br">﴿</span>وَاقْصِدْ فِي مَشْيِكَ وَاغْضُضْ مِن صَوْتِكَ<span class="br">﴾</span></p>'
            '<div class="src">سورة لقمان: ١٩؛ ويُنقل النص في الكتاب من مصدر المصحف الموثق</div></div>')
    return fig(f'<div class="paper paper-flow">{tbl}{rule}{defi}{warn}{evid}</div>', num,
               "جدول الفروق والعناصر الأربعة: القاعدة، والتعريف، والتنبيه، والشاهد.", "fig-flow")


def gallery_c(num):
    turns = [
        ("الطالب", '<span class="dir">[ينتظر حتى يُتمّ الشيخ جملته]</span> أحسن الله إليكم يا شيخنا، هل تأذنون لي بسؤال؟'),
        ("الشيخ", "تفضّل يا بُنيّ."),
        ("الطالب", "ذكرتم أن الأصل في الكلام مطابقته لمقتضى الحال؛ فهل يُعدّ رفع الصوت في مجلس العلم خروجًا عن ذلك؟"),
        ("الشيخ", "أحسنت. رفع الصوت فوق الحاجة خروج عن الأدب، إلا لإسماع البعيد."),
        ("الطالب", '<span class="dir">[يخفض صوته]</span> جزاكم الله خيرًا، اتضح الأمر.'),
        ("الشيخ", "وإياك، بارك الله فيك."),
    ]
    rows = "".join(f'<div class="turn"><span class="who">{w}</span><span class="say">{s}</span><span class="ln">س{ar(i + 1)}</span></div>'
                   for i, (w, s) in enumerate(turns))
    dia = f'<div class="dia"><div class="dia-h"><span class="lbl">حوار · النسخة المحسّنة</span><small>مجلس علم · الرسمية ٤</small></div>{rows}</div>'
    ex = ('<div class="ex"><div class="ex-tab"><span>تمرين ٤: التهذيب</span><span>فردي، ٥ دقائق</span></div><div class="ex-b">'
          '<p>اجعل كل عبارة أكثر أدبًا دون ضعف، ثم اقرأها بصوت مسموع.</p><ol>'
          '<li>«يا شيخ، أعد الكلام؛ لم أفهم.»<span class="ans"></span></li>'
          '<li>«أنت أخطأت في هذه المسألة.»<span class="ans"></span></li>'
          '<li>«أريد أن أتكلم الآن.»<span class="ans"></span></li></ol></div></div>')
    rail = ('<div class="railnote"><div><b>للمدرب</b>لاحظ انتظار الطالب حتى يُتمّ الشيخ جملته (س١)، وإعادته صياغة كلام الشيخ قبل سؤاله (س٣).</div>'
            '<div><b>العمود الجانبي</b>أرقام الأسطر، وملاحظات المدرب، ورموز الصوت.</div>'
            '<div class="qr">موضع رمز QR للتسجيل المرجعي</div></div>')
    return fig(f'<div class="paper paper-flow"><div class="twocol">{dia}{rail}</div>{ex}</div>', num,
               "الحوار بتخطيطه المعماري (بلا فقاعات كلام) وبطاقة التدريب، والعمود الجانبي على الجهة الخارجية.", "fig-flow")


def gallery_d(num):
    sim = ('<div class="sim"><div class="sim-h"><span class="lbl">محاكاة</span><b>الاستئذان والسؤال في مجلس علم</b></div><div class="sim-b">'
           '<div><p class="h">الأدوار</p><ul><li>الشيخ: المدرب</li><li>السائل: المتدرب</li><li>المراقب: زميل يملأ سلّم التقييم</li></ul></div>'
           '<div><p class="h">المراحل</p><ol><li>يدخل السائل ويسلّم ويجلس حيث ينتهي المجلس.</li><li>ينتظر فراغ الشيخ من فكرته.</li>'
           '<li>يستأذن بصيغة مناسبة للمقام.</li><li>يسأل سؤالًا واحدًا واضحًا، ثم يشكر.</li></ol></div>'
           f'<div class="meta"><span>الزمن: ٨ دقائق</span><span>الرسمية {dots(4)}</span><span>التقييم: سلّم المئة درجة</span></div></div></div>')
    aud_svg = ('<svg viewBox="0 0 48 48"><g stroke="#123C8C" stroke-width="2.2"><line x1="14" y1="20" x2="14" y2="40"/>'
               '<line x1="24" y1="10" x2="24" y2="40"/><line x1="34" y1="24" x2="34" y2="40"/></g><g fill="#123C8C">'
               '<path d="M14 13 l4 4 -4 4 -4 -4z"/><path d="M24 3 l4 4 -4 4 -4 -4z"/><path d="M34 17 l4 4 -4 4 -4 -4z"/></g></svg>')
    aud = (f'<div class="aud">{aud_svg}<div><span class="lbl">مهمة صوتية</span>'
           '<p>سجّل الاستئذان ثلاث مرات: أمام شيخ، ثم أمام أستاذ جامعي، ثم أمام زميل. تثبت المخارج والإعراب، وتتغير النبرة ودرجة الرسمية.</p>'
           '<p class="voc">أَحْسَنَ اللهُ إِلَيْكُمْ يا شَيْخَنا <span class="pm">//</span> هَلْ تَأْذَنُونَ لِي <span class="pm">/</span> بِسُؤالٍ <span class="stress">يَسِيرٍ</span>؟ <span class="pm">↑</span></p>'
           '<div class="keys"><span><span class="pm">/</span> سكتة قصيرة</span><span><span class="pm">//</span> سكتة طويلة</span>'
           '<span><span class="pm">↑</span> رفع</span><span><span class="pm">↓</span> خفض</span><span><span class="pm">(ت)</span> تنفّس</span>'
           '<span><span class="stress">العريض</span> نبر</span></div></div></div>')
    mas = ('<div class="mas"><i></i><i></i><i></i><i></i><span class="lbl">معيار الإتقان</span>'
           '<p>يُعدّ الدرس متقَنًا إذا استأذن المتدرب وسأل في محاكاة مجلس علم بتقدير كلي لا يقل عن <strong>٨٠ من ١٠٠</strong>، '
           'ولا تقل درجة «الأدب وحسن الخطاب» عن <strong>٨ من ١٠</strong>.</p></div>')
    return fig(f'<div class="paper paper-flow">{sim}{aud}{mas}</div>', num,
               "المحاكاة والمهمة الصوتية ومعيار الإتقان: الإطار الذهبي لمعيار الإتقان وحده.", "fig-flow")
