#!/usr/bin/env python3
"""Build «الدليل التحريري والعلمي» — Editorial & Scholarly Bible — Edition 1.0 — PDF Master.

    python3 build.py            build the PDF from the Markdown sources in ../bible
    python3 build.py --review   also render page thumbnails and a layout report for review

Pipeline: Markdown -> HTML (python-markdown + BeautifulSoup transforms) -> Chromium (Playwright)
-> PDF. A first "measuring" pass carries invisible page markers used to fill the table of
contents and to check the layout (orphaned headings, split tables and figures); the final pass
drops them. pypdf then fixes the bookmark titles (Chromium stores RTL titles in visual order),
and sets the metadata, the document language and right-to-left reading order.
Before rendering, a typographic check rejects a middle dot «·» written next to an Arabic-Indic
digit: it reads as the zero «٠» (e.g. «للاعتماد · ٢٠» looks like «٢٠٠»).

Requirements: Python 3.9+ with markdown, beautifulsoup4, pypdf, fonttools and brotli (pypdfium2 +
Pillow for --review); Node.js with the playwright package and a Chromium build. Fonts (SIL OFL) are
fetched once from Google Fonts into .cache/; variable fonts are cut into static weights there,
because Chromium writes variable fonts into a PDF as Type 3 glyphs, which print preflight rejects.
The build stops if any font outside the approved set (e.g. a system fallback for a missing
glyph) or a Type 3 font reaches the PDF.
"""
from __future__ import annotations

import argparse
import html
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

import markdown
from bs4 import BeautifulSoup, NavigableString, Tag
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, Fit, NameObject, TextStringObject

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import components as C  # noqa: E402
from components import ar  # noqa: E402

ROOT = HERE.parent
BIBLE = ROOT / "bible"
CACHE = HERE / ".cache"
OUT = ROOT / "Editorial-Scholarly-Bible_Edition-1.0_PDF-Master.pdf"
DATE_LINE = "سبتمبر ٢٠٢٦م / ١٤٤٨هـ"
N_DECISIONS = 20

FONT_CSS = [
    "https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cormorant+Garamond:wght@500;600"
    "&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600&family=IBM+Plex+Sans:wght@400;500&display=swap",
    "https://fonts.googleapis.com/css2?family=Reem+Kufi:wght@400..700&display=swap",
    "https://fonts.googleapis.com/css2?family=Amiri+Quran&display=swap",
]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

PARTS = [
    dict(n=1, file="01-الفلسفة-والمبادئ-والهوية.md", word="الأول", en="Part One",
         title="الفلسفة والمبادئ والهوية",
         lede="ماذا نريد من المتعلم؟ وما المبادئ التي لا نتنازل عنها؟ وبماذا يختلف هذا المشروع عمّا سبقه؟"),
    dict(n=2, file="02-النظام-اللغوي-والسجلات-والمقام.md", word="الثاني", en="Part Two",
         title="النظام اللغوي والسجلات والمقام",
         lede="الفصحى طيف من السجلات لا مستوى واحد؛ ولكل متكلم ومخاطَب ومقام ما يناسبه."),
    dict(n=3, file="03-الأمثلة-والمقارنة-والحوار-والأخطاء.md", word="الثالث", en="Part Three",
         title="الأمثلة والمقارنة والحوار والأخطاء",
         lede="كيف نكتب المثال والحوار، وكيف نقارن بين الأداء غير الناجح والمقبول والناجح، وكيف نصنّف الخطأ ونصححه."),
    dict(n=4, file="04-التوثيق-والتربية-والصوت-والثقافة.md", word="الرابع", en="Part Four",
         title="التوثيق والتربية والصوت والثقافة",
         lede="لا قول بلا مصدر، ولا درس بلا تدريب، ولا صوت بلا معيار، ولا تعميم على الشعوب."),
    dict(n=5, file="05-الأسلوب-والمصطلحات-والبنية-والجودة.md", word="الخامس", en="Part Five",
         title="الأسلوب والمصطلحات والبنية والجودة",
         lede="لغة الكتاب ومصطلحاته الثابتة، وبنية مجلداته، والمراجعات التي لا يُعتمد فصل قبلها."),
    dict(n=6, file="06-الهوية-البصرية-والإخراج-الفني.md", word="السادس", en="Part Six",
         title="الهوية البصرية والإخراج الفني",
         lede="الياقوتي والذهبي واللؤلؤي والقرمزي: هوية إصدار رائد، الفخامة فيها بالدقة لا بالزخرفة."),
]
PART_WORDS = {p["word"]: p["n"] for p in PARTS}

PART_SUMMARIES = {
    1: ["الدليل دستور المشروع: يحكم كل ما يُنتَج بعده، ولا يُخالَف بعد اعتماده إلا بتوجيه صريح.",
        "الغاية نقل المتعلم من معرفة العربية إلى امتلاك الملكة العربية الشفهية.",
        "الكلام الناجح: واضح، صحيح، مناسب، مؤثر، مهذب، في الوقت والقدر المناسبين.",
        "واحد وثلاثون مبدأً حاكمًا، أعلاها مبدأ الشمول: موسوعة تدريبية لا كتيب نظري.",
        "هوية مستقلة تميّز المشروع عن كتب التعبير والمحادثة والبلاغة والخطابة."],
    2: ["الفصحى طيف من السجلات، والمستوى الأساس فيها الفصحى المعاصرة الطبيعية.",
        "سلّم رسمية خماسي موحد، وقواعد مضبوطة للانتقال بين درجاته.",
        "دليل سجلات لواحد وعشرين متحدثًا: المخاطَب والغرض والرسمية والنبرة والسرعة والعبارات.",
        "لا نموذج كلامي مهم بلا بطاقة مقام تسبقه.",
        "النموذج السداسي: خمسة أسئلة مدخلات، و«كيف؟» مُخرَج يُشتق منها."],
    3: ["الأمثلة موسوعية بحدود دنيا ومصفوفة تنويع إلزامية، بلا تكرار ولا حشو.",
        "المقارنة المتدرجة هوية المشروع: غير ناجح، ومقبول، وناجح، ورفيع عند الحاجة، مع جدول الفروق.",
        "الحوار حيّ مرقّم الأسطر، يتبعه تحليل ونسخة محسّنة كاملة.",
        "بنك الأخطاء: عشرون صنفًا، وأربع درجات خطورة، وبطاقة موحدة."],
    4: ["لا اقتباس بلا مصدر، ولا صفحة مخترعة، ووسوم التحقق ظاهرة حتى يُتحقق منها.",
        "قالب موحد للدرس، وسلّم تدرج عشري، وإحدى عشرة صيغة للتمارين.",
        "معيار نطق فصيح معاصر، ورموز أداء موحدة لنصوص التدريب الصوتي.",
        "لا تعميم على الشعوب واللغات، ولا سخرية من لهجة، والبيئة الإفريقية مختبر أصيل للأمثلة."],
    5: ["لغة فصيحة معاصرة بمقاييس للفقرة والجملة، وقائمة بالعبارات النمطية المجتنبة.",
        "مصطلحات ثابتة لا تتبدل من فصل إلى فصل، وكل تغيير يُسجَّل بسببه.",
        "أربعة مجلدات للطالب وثمانية كتب مرافقة، وتسلسل هرمي من الجزء إلى التقييم.",
        "إحدى عشرة مراجعة وخمسة عشر سؤالًا قبل اعتماد أي فصل.",
        "الشمول بلا حشو: كل مثال يؤدي وظيفة تعليمية واضحة."],
    6: ["الياقوتي والذهبي واللؤلؤي والقرمزي، بميزانية لون ومصفوفة تباين محسوبة.",
        "أربعة أدوار حرفية وحرف قرآني، ولا ميل ولا تسطير ولا تباعد في الحرف العربي.",
        "«نظام النقطة» وحدة الهوية، والهندسة عمارة لا زخرفة.",
        "أربعة مفاهيم للأغلفة، ونظام عائلة للكتب، وعناصر تعليمية ثابتة الهيئة.",
        "اختبار الريادة شرط للاعتماد، والإصدار النهائي بصيغة PDF Master."],
}

APPENDICES = [
    ("a", "أ", "01-الرؤية-والفلسفة.md", "الرؤية والعناوين المقترحة والفلسفة"),
    ("b", "ب", "02-خريطة-الكتاب.md", "خريطة الكتاب"),
    ("c", "ج", "03-المستويات-والمخرجات.md", "مستويات البرنامج ومخرجات التعلم"),
    ("d", "د", "04-نظام-التقييم.md", "نظام التقييم"),
    ("e", "هـ", "00-الوثيقة-الحاكمة.md", "الوثيقة الحاكمة المختصرة (برومبت التشغيل)"),
]

COLOR_NAMES = {
    "الفحمي": "#1F2329", "اللؤلؤي": "#F8F6F0", "الرملي": "#F1E8D4", "الغرافيتي": "#4A4540",
    "الحجري": "#ECE8E1", "الياقوتي العميق": "#082567", "الياقوتي": "#123C8C",
    "الياقوتي المضيء": "#174EA6", "الأزرق الملكي": "#2F5FC4", "القرمزي": "#A51C30",
    "العنّابي": "#8E1B2A", "ذهبي الحبر": "#7F5F12", "الليلي": "#060E26",
    "الذهبي الفاتح": "#E1C46A", "الذهبي الطازج": "#D4AF37", "الذهبي المصقول": "#C9A227",
    "الذهبي العتيق": "#B88A20", "أي ذهبي (٣٠٠–٧٠٠)": "#C9A227", "اللؤلؤي أو الرملي": "#F8F6F0",
}

APPROVAL_ROWS = [
    ("العنوان الرسمي", "«صناعة المتكلّم العربي: من سلامة اللسان إلى حسن البيان»"),
    ("مستوى المتعلم", "يبدأ من المتوسط"),
    ("الحدود الدنيا للأمثلة", "اعتمادها حدودًا دنيا تُرفع عند الحاجة"),
    ("درجات المقارنة", "ثلاث إلزامية، و«الرفيع» في المواقف المحورية"),
    ("عدد المجلدات", "٤ مجلدات للطالب وكتب مرافقة"),
    ("سياسة التشكيل", "كما في دليل الأسلوب"),
    ("الأرقام", "المشرقية في المتن"),
    ("نطق الضاد والقاف", "النطق الفصيح المعاصر، بعد عرضه على مختص"),
    ("الرواية والترقيم", "حفص عن عاصم، وترقيم مصحف المدينة"),
    ("الطبعات المرجعية", "اعتماد المبدأ، وتحديدها في ملف المراجع"),
    ("ترتيب البدء", "الباب الأول، مع فصل نموذجي يُعتمد قالبًا"),
    ("المراجع النيجيري", "تعيين مراجع مختص إن أمكن"),
    ("اتجاه الأغلفة", "أ للمجلدات، ب للمكتبة، ج للرائدة، د شارة"),
    ("الخطوط", "المفتوحة للنماذج، وتقييم تجارية للورقية"),
    ("أرقام الفواتح", "المشرقية «٠١»"),
    ("مقاس الكتاب", "٢٠×٢٦، ١٥×٢١، ٢١×٢٨ سم"),
    ("الطبعات والتشطيب", "دراسية + رائدة مجلدة"),
    ("الشعار الكتابي", "تكليف خطاط أو مصمم حروف"),
    ("التصوير", "جلسات أصلية + صور مرخصة منتقاة"),
    ("الجهة الناشرة", "تُحدَّد قبل تصميم الأغلفة"),
]


# --------------------------------------------------------------------------- fonts

def fetch(url: str) -> bytes:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.read()
    except Exception:
        return subprocess.run(["curl", "-sSf", "-A", UA, url], check=True, capture_output=True).stdout


def ensure_fonts() -> str:
    fdir = CACHE / "fonts"
    css_path = fdir / "fonts.css"
    if css_path.exists():
        return css_path.read_text(encoding="utf-8")
    fdir.mkdir(parents=True, exist_ok=True)
    css = "".join(fetch(u).decode("utf-8") for u in FONT_CSS)
    urls = sorted(set(re.findall(r"url\((https://fonts\.gstatic\.com/[^)]+)\)", css)))
    for i, u in enumerate(urls):
        dest = fdir / f"f{i:02d}{Path(u).suffix}"
        dest.write_bytes(fetch(u))
        css = css.replace(u, dest.as_uri())
    css_path.write_text(css, encoding="utf-8")
    return css


def static_instances(css: str) -> str:
    """Replace every variable face by static instances, one per weight (cached next to the source)."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    def face(block: str) -> str:
        url = re.search(r"url\((file://[^)]+)\)", block).group(1)
        path = Path(urllib.request.url2pathname(url[len("file://"):]))
        font = TTFont(path)
        if "fvar" not in font:
            return "@font-face {" + block + "}"
        axes = {a.axisTag: a for a in font["fvar"].axes}
        w = re.search(r"font-weight:\s*(\d+)(?:\s+(\d+))?;", block)
        lo, hi = int(w.group(1)), int(w.group(2) or w.group(1))
        faces = []
        for wt in range(lo, hi + 1, 100):
            dest = path.with_name(f"{path.stem}-w{wt}.woff2")
            if not dest.exists():
                limits = {tag: a.defaultValue for tag, a in axes.items()}
                limits["wght"] = min(max(wt, axes["wght"].minValue), axes["wght"].maxValue)
                try:   # name the instance after its weight (e.g. ReemKufi-SemiBold) where the font allows
                    inst = instancer.instantiateVariableFont(TTFont(path), limits, updateFontNames=True)
                except Exception:
                    inst = instancer.instantiateVariableFont(TTFont(path), limits)
                inst.flavor = "woff2"
                inst.save(dest)
            b = re.sub(r"font-weight:\s*[^;]+;", f"font-weight: {wt};", block.replace(url, dest.as_uri()))
            faces.append("@font-face {" + b + "}")
        return "\n".join(faces)

    return re.sub(r"@font-face\s*{(.*?)}", lambda m: face(m.group(1)), css, flags=re.S)


# --------------------------------------------------------------------------- markdown

LIST_RE = re.compile(r"^(\s*)([-*+]|\d+\.)\s+")


def prep_md(text: str):
    """Pull out fenced blocks and add the blank lines python-markdown needs
    (GitHub renders lists and tables that directly follow a paragraph)."""
    codes: list[str] = []

    def grab(m):
        codes.append(m.group(1))
        return f"\n\n@@CODE{len(codes) - 1}@@\n\n"

    text = re.sub(r"```[^\n]*\n(.*?)```", grab, text, flags=re.S)
    out: list[str] = []
    prev = ""
    for line in text.split("\n"):
        m = LIST_RE.match(line)
        if m and m.group(1):
            line = " " * (len(m.group(1)) * 2) + line.lstrip()
        is_table = line.lstrip().startswith("|")
        is_list = bool(m)
        is_quote = line.lstrip().startswith(">")
        if prev.strip():
            prev_table = prev.lstrip().startswith("|")
            prev_list = bool(LIST_RE.match(prev)) or prev.startswith("  ")
            prev_quote = prev.lstrip().startswith(">")
            if is_table and not prev_table:
                out.append("")
            elif is_list and not prev_list:
                out.append("")
            elif is_quote and not prev_quote:
                out.append("")
            elif line.startswith("#"):
                out.append("")
            elif line.strip() and not is_table and prev_table:
                out.append("")
            elif line.strip() and not is_list and not line.startswith(" ") and prev_list and not is_quote:
                out.append("")
        out.append(line)
        prev = line
    return "\n".join(out), codes


def md_to_soup(text: str, code_handler) -> BeautifulSoup:
    text, codes = prep_md(text)
    body = markdown.markdown(text, extensions=["tables", "sane_lists"])
    soup = BeautifulSoup(f'<div class="root">{body}</div>', "html.parser")
    for p in soup.find_all("p"):
        m = re.fullmatch(r"@@CODE(\d+)@@", p.get_text(strip=True))
        if m:
            p.replace_with(BeautifulSoup(code_handler(codes[int(m.group(1))]), "html.parser"))
    return soup


class FigNum:
    def __init__(self, prefix: str):
        self.prefix, self.n = prefix, 0

    def __call__(self) -> str:
        self.n += 1
        return f"شكل {self.prefix}–{ar(self.n)}"


def code_component(code: str, fignum: FigNum) -> str:
    c = code
    if "معرفة العربية" in c:
        return C.mastery_steps(fignum())
    if "┌" in c and "المتكلم:" in c:
        return C.context_card_template(fignum())
    if "بسيط" in c and "ارتجالي" in c:
        return C.flow(["بسيط", "متوسط", "متقدم", "احترافي", "ارتجالي"], fignum(),
                      "سُلّم تدرج الأمثلة: يشتد لونه كلما ارتفعت الدرجة.", levels=[1, 2, 3, 4, 5])
    if "مث١٧" in c:
        return C.example_code(fignum())
    if "▣" in c:
        return C.ladder_template(fignum())
    if "الحوار الأول" in c:
        return C.dialogue_structure(fignum())
    if "الرمز: خ-" in c:
        return C.error_card_template(fignum())
    if "هدف ← تمهيد" in c:
        return C.flow(["هدف", "تمهيد", "موقف", "نموذج", "تحليل", "قاعدة", "أمثلة", "تدريب موجّه",
                       "تدريب حر", "محاكاة", "تسجيل", "تقييم", "إعادة"], fignum(),
                      "المسار التعليمي الثابت لكل درس.", goal_last=True)
    if "الجزء (المجلد)" in c:
        return C.flow(["الجزء (المجلد)", "الباب", "الفصل", "الوحدة", "الدرس", "التدريب", "المحاكاة", "التقييم"],
                      fignum(), "التسلسل الهرمي للكتاب والمجلدات، من الأكبر إلى الأصغر.",
                      levels=[5, 4, 3, 2, 1, 1, 1, 1])
    if "الفصل: …" in c:
        return C.qc_form(fignum())
    if "مكانة الإصدارات" in c:
        return C.equation(fignum())
    if "┌" in c and "صورة تحريرية" in c:
        return C.spread(fignum())
    if "فاتحة (درامية)" in c:
        return C.rhythm(fignum())
    raise ValueError("Unmapped code block:\n" + code)


# --------------------------------------------------------------------------- transforms

LATIN_RE = re.compile(r"\(?[A-Za-z][A-Za-z0-9&.,;:'’\- ]*[A-Za-z0-9.]\)?")


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def wrap_latin(text: str) -> str:
    """Escape text and wrap Latin runs so headings use the Latin companion face."""
    out, last = [], 0
    for m in LATIN_RE.finditer(text):
        out.append(esc(text[last:m.start()]))
        out.append(f'<span class="en">{esc(m.group(0))}</span>')
        last = m.end()
    out.append(esc(text[last:]))
    return "".join(out)


def frag(s: str):
    return BeautifulSoup(s, "html.parser")


def split_heading(text: str):
    if ":" in text:
        a, b = text.split(":", 1)
        return a.strip(), b.strip()
    return "", text.strip()


def number_h3(h: Tag):
    first = next((c for c in h.contents if isinstance(c, NavigableString) and c.strip()), None)
    if first is None or h.contents.index(first) != 0:
        h["data-outline"] = h.get_text(" ", strip=True)
        return
    m = re.match(r"^\s*([٠-٩0-9]+|[أ-ي])\.\s*(.*)$", str(first), flags=re.S)
    h["data-outline"] = h.get_text(" ", strip=True)
    if m:
        span = frag(f'<span class="num">{m.group(1)}</span>')
        first.replace_with(m.group(2))
        h.insert(0, span)


def latinize_heading(h: Tag):
    for s in list(h.find_all(string=True)):
        if re.search(r"[A-Za-z]", s) and s.parent.name not in ("code",):
            s.replace_with(frag(wrap_latin(str(s))))


def sectionize(soup: BeautifulSoup, bab_counter: list, babs: list, first_class=True):
    root = soup.find("div", class_="root")
    children = list(root.children)
    intro = soup.new_tag("div", attrs={"class": "part-intro"})
    sections: list[Tag] = []
    current = None
    for child in children:
        if isinstance(child, Tag) and child.name == "h2":
            bab_counter[0] += 1
            n = bab_counter[0]
            eyebrow, title = split_heading(child.get_text(" ", strip=True))
            sec = soup.new_tag("section", attrs={"class": "bab", "id": f"bab-{n}"})
            sec.append(frag(
                f'<header class="bab-h"><p class="eyebrow">{esc(eyebrow)}</p>'
                f'<h2 data-outline="{esc(eyebrow)}: {esc(title)}">{wrap_latin(title)}</h2>'
                f'<div class="nrule"></div></header>'))
            babs.append((n, eyebrow, title, f"bab-{n}"))
            sections.append(sec)
            current = sec
            child.extract()
            continue
        node = child.extract()
        (current if current is not None else intro).append(node)
    root.clear()
    if intro.get_text(strip=True):
        root.append(intro)
    for i, s in enumerate(sections):
        if i == 0 and first_class and not intro.get_text(strip=True):
            s["class"] = s.get("class", []) + ["first"]
        root.append(s)


def style_tables(soup: BeautifulSoup):
    for t in soup.find_all("table"):
        if t.find_parent(class_="tbl") or "dtab" in (t.get("class") or []) or t.find_parent("figure"):
            continue
        body_rows = t.find("tbody").find_all("tr") if t.find("tbody") else []
        first = t.find("tr")
        ncols = len(first.find_all(["th", "td"])) if first else 0
        wrap = soup.new_tag("div", attrs={"class": "tbl"})
        t.wrap(wrap)
        if len(body_rows) <= 3 or (len(body_rows) <= 6 and len(t.get_text()) < 500):
            wrap["class"] = ["tbl", "short"]
        if ncols >= 6:
            t["class"] = (t.get("class") or []) + ["dense"]


def style_code(soup: BeautifulSoup):
    for c in soup.find_all("code"):
        txt = c.get_text()
        if re.fullmatch(r"#[0-9A-Fa-f]{6}", txt):
            c.insert_before(frag(f'<span class="sw" style="background:{txt}"></span>'))
        elif re.search(r"[؀-ۿ]", txt):
            c["class"] = (c.get("class") or []) + ["ar"]


SYMBOLS = "✔✘●◐◔○①②③④◆◇←"
# drawn marks for glyphs the text faces lack (a system fallback font would otherwise be embedded)
SVG_OK = ('<svg class="mk" viewBox="0 0 12 12" aria-hidden="true"><path d="M2.2 6.6 L4.9 9.2 L9.8 2.9" '
          'fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>')
SVG_NO = ('<svg class="mk" viewBox="0 0 12 12" aria-hidden="true"><path d="M3 3 L9 9 M9 3 L3 9" fill="none" '
          'stroke="currentColor" stroke-width="1.9" stroke-linecap="round"/></svg>')
SVG_ARROW = ('<svg class="arw" viewBox="0 0 16 10" aria-hidden="true"><path d="M15 5 H2.2 M6 1.4 L2 5 L6 8.6" '
             'fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def replace_symbols(soup: BeautifulSoup):
    for s in list(soup.find_all(string=True)):
        if not any(ch in s for ch in SYMBOLS):
            continue
        if s.parent.name in ("style", "script") or s.find_parent(class_="badge"):
            continue
        if s.parent.name == "code" and any(ch in s for ch in SYMBOLS.replace("←", "")):
            continue
        row = s.find_parent("tr")
        severity_ctx = "مغيّر" in s or (row is not None and "مغيّر" in row.get_text())
        out = []
        for ch in str(s):
            if ch == "✔":
                out.append(f'<span class="ok" role="img" aria-label="نعم">{SVG_OK}</span>')
            elif ch == "✘":
                out.append(f'<span class="no" role="img" aria-label="لا">{SVG_NO}</span>')
            elif ch == "←":
                out.append(SVG_ARROW)
            elif ch == "●":
                out.append(C.rh("fill-c"))
            elif ch == "◔":
                out.append(C.rh("half-g"))
            elif ch == "○":
                out.append(C.rh("line-g"))
            elif ch == "◐":
                out.append(C.rh("half-c" if severity_ctx else "half-g"))
            elif ch in "①②③④":
                out.append(C.badge("①②③④".index(ch) + 1))
            elif ch == "◆":
                out.append(C.rh("fill-s"))
            elif ch == "◇":
                out.append(C.rh("line-s"))
            else:
                out.append(esc(ch))
        s.replace_with(frag("".join(out)))


def style_quotes(soup: BeautifulSoup):
    for bq in soup.find_all("blockquote"):
        text = bq.get_text(" ", strip=True)
        paras = bq.find_all("p")
        if "المعيار النهائي" in text:
            cls, label = "rule-p principle", "نص المبدأ"
        elif text.startswith("قاعدة") or "غيِّر المخاطَب" in text:
            cls, label = "rule-p", "قاعدة"
        elif text.startswith("تنبيه"):
            cls, label = "warn", ""
        elif text.startswith("«") or text.startswith("الكلام الناجح"):
            cls, label = "def", "تعريف"
        else:
            cls, label = "note", ""
        if label and paras:   # «قاعدة» label + «**قاعدة الذهب…:**» would say the word twice
            first = paras[0].find("strong")
            if first and first.string and first.string.startswith(label + " "):
                first.string = first.string[len(label) + 1:]
        inner = "".join(str(p) for p in paras) if paras else f"<p>{bq.decode_contents()}</p>"
        lab = f'<span class="lbl">{label}</span>' if label else ""
        if cls.startswith("rule-p"):
            new = f'<div class="{cls}"><div>{lab}{inner}</div></div>'
        else:
            new = f'<div class="{cls}">{lab}{inner}</div>'
        bq.replace_with(frag(new))


def style_em(soup: BeautifulSoup):
    for e in soup.find_all("em"):
        t = e.get_text(strip=True)
        if t.startswith("["):
            e["class"] = ["tag-verify"]
        elif re.search(r"قرار معلّق رقم", t):
            e["class"] = ["tag-dec"]


def contrast_samples(soup: BeautifulSoup):
    for wrap in soup.find_all("div", class_="tbl"):
        t = wrap.find("table")
        head = [th.get_text(strip=True) for th in t.find("thead").find_all("th")] if t.find("thead") else []
        if head[:2] != ["النص", "الخلفية"]:
            continue
        t.find("thead").find("tr").insert(0, frag("<th>عيّنة</th>"))
        for tr in t.find("tbody").find_all("tr"):
            tds = tr.find_all("td")
            fg = COLOR_NAMES.get(tds[0].get_text(strip=True), "#1F2329")
            bg = COLOR_NAMES.get(tds[1].get_text(strip=True), "#F8F6F0")
            tr.insert(0, frag(f'<td class="samp"><div class="samp-b" style="background:{bg};color:{fg}">نص</div></td>'))


def formality_dots(soup: BeautifulSoup):
    for wrap in soup.find_all("div", class_="tbl"):
        t = wrap.find("table")
        head = [th.get_text(strip=True) for th in t.find("thead").find_all("th")] if t.find("thead") else []
        if head[:2] != ["الدرجة", "الاسم"]:
            continue
        for tr in t.find("tbody").find_all("tr"):
            td = tr.find("td")
            digits = td.get_text(strip=True).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
            if digits.isdigit():
                td.insert(0, frag(C.dots(int(digits)) + " "))


def ladders(soup: BeautifulSoup):
    """Part 3 worked example: the ▣ context line and ①②③ paragraphs become components."""
    for p in list(soup.find_all("p")):
        if p.get_text().strip().startswith("▣"):
            inner = p.decode_contents().replace("▣", "", 1).strip()
            p.replace_with(frag(f'<div class="ctx-strip">{inner}</div>'))
    tier_ps = [p for p in soup.find_all("p") if re.match(r"^\s*[①②③④]", p.get_text())]
    if not tier_ps:
        return
    names = {"غير الناجح": "المتكلم غير الناجح", "المقبول": "المتكلم المقبول",
             "الناجح": "المتكلم الناجح", "الرفيع": "المتكلم الرفيع"}
    tiers = []
    for p in tier_ps:
        n = "①②③④".index(p.get_text().strip()[0]) + 1
        strong = p.find("strong")
        label = names.get(strong.get_text(strip=True).rstrip(":"), strong.get_text(strip=True).rstrip(":"))
        quote = p.get_text().split(":", 1)[1].strip().strip("«»").strip()
        tiers.append(f'<div class="tier t{n}">{C.badge(n)}<div><span class="lbl">{label}</span><q>{esc(quote)}</q></div></div>')
    ctx = tier_ps[0].find_previous_sibling("div", class_="ctx-strip")
    fig = f'<figure class="fig fig-flow">{str(ctx) if ctx else ""}<div class="ladder" style="margin-top:2.2mm">{"".join(tiers)}</div>' \
          f'<figcaption><b>مثال تطبيقي</b><span>المقارنة المتدرجة في التعريف بالنفس أمام لجنة مقابلة.</span></figcaption></figure>'
    if ctx:
        ctx.extract()
    tier_ps[0].replace_with(frag(fig))
    for p in tier_ps[1:]:
        p.decompose()


def error_cards(soup: BeautifulSoup):
    for p in list(soup.find_all("p")):
        st = p.find("strong")
        if not st or not st.get_text(strip=True).startswith("البطاقة ("):
            continue
        title = st.get_text(strip=True)
        st.extract()
        meta = [m.strip() for m in p.decode_contents().split("|") if m.strip()]
        meta_p = None
        ul = p.find_next_sibling("ul")
        items = []
        for li in ul.find_all("li", recursive=False):
            s = li.find("strong")
            k = s.get_text(strip=True).rstrip(":") if s else ""
            if s:
                s.extract()
            items.append(f'<li><span class="k">{esc(k)}</span><span class="v">{li.decode_contents().strip()}</span></li>')
        card = (f'<div class="card errcard"><div class="card-h"><b>{esc(title)}</b>'
                + "".join(f'<span class="meta">{m}</span>' for m in meta)
                + f'</div><div class="card-b"><ul class="kvlist">{"".join(items)}</ul></div></div>')
        p.replace_with(frag(card))
        if meta_p:
            meta_p.decompose()
        ul.decompose()


def voiced_example(soup: BeautifulSoup):
    for p in soup.find_all("p"):
        if p.get_text().startswith("مثال: «السلام"):
            h = p.decode_contents()
            h = h.replace("//", "@@D@@").replace(" / ", ' <span class="pm">/</span> ')
            h = h.replace("@@D@@", '<span class="pm">//</span>').replace("(ت)", '<span class="pm">(ت)</span>')
            h = h.replace("<strong>", '<strong class="stress">')
            p.clear()
            p.append(frag(h))
            p["class"] = ["voc-ex"]


def drop_hr(soup: BeautifulSoup):
    for hr in soup.find_all("hr"):
        hr.decompose()


def h3_sections(sec: Tag):
    """Map h3 title -> list of following sibling nodes up to the next h3."""
    out, cur = {}, None
    for ch in sec.children:
        if isinstance(ch, Tag) and ch.name == "h3":
            cur = ch.get("data-outline", ch.get_text(" ", strip=True))
            out[cur] = [ch]
        elif cur is not None:
            out[cur].append(ch)
    return out


def insert_after_section(soup, h3_contains: str, html_str: str, after="end"):
    for h in soup.find_all("h3"):
        if h3_contains in h.get("data-outline", h.get_text(" ", strip=True)):
            nodes = [h]
            for sib in h.next_siblings:
                if isinstance(sib, Tag) and sib.name in ("h3", "h2"):
                    break
                nodes.append(sib)
            tags = [n for n in nodes if isinstance(n, Tag)]
            if after == "lead":   # after the opening paragraph, ahead of the section's tables and lists
                anchor = tags[1] if len(tags) > 1 and tags[1].name == "p" else h
            elif after == "first-table":
                anchor = next((t for t in tags if "tbl" in (t.get("class") or [])), tags[-1])
            elif after == "last-table":
                anchor = [t for t in tags if "tbl" in (t.get("class") or [])][-1]
            else:
                anchor = tags[-1]
            anchor.insert_after(frag(html_str))
            return
    raise ValueError(f"heading not found: {h3_contains}")


# --------------------------------------------------------------------------- parts

def build_part(p: dict, bab_counter: list):
    md = (BIBLE / p["file"]).read_text(encoding="utf-8")
    md = re.sub(r"^# .*\n", "", md, count=1)
    md = re.sub(r"^## .*\n", "", md.lstrip("\n"), count=1)
    md = re.sub(r"^\*\*الإصدار ١[.٫]٠.*\n", "", md, flags=re.M)
    md = md.replace("انظر «الفهرس والقرارات المعلّقة»", "انظر [«القرارات المعلّقة»](#sec-decisions) في قسم الاعتماد")
    md = md.replace("في «سجل التغييرات» (انظر الفهرس)", "في [«سجل الإصدارات والتعديلات»](#sec-log) في آخر الوثيقة")
    if p["n"] == 6:
        md = re.sub(r"^### .*\n", "", md.lstrip("\n"), count=1)
        md = re.sub(r"^> \*\*المرافق التطبيقي:\*\*.*\n", "", md, flags=re.M)
    fignum = FigNum(ar(p["n"]))
    soup = md_to_soup(md, lambda c: code_component(c, fignum))
    drop_hr(soup)
    babs: list = []
    sectionize(soup, bab_counter, babs)
    for h in soup.find_all("h3"):
        number_h3(h)
        latinize_heading(h)
    style_tables(soup)
    style_code(soup)
    style_em(soup)
    style_quotes(soup)
    if p["n"] == 2:
        formality_dots(soup)
        insert_after_section(soup, "النموذج السداسي", C.six_model(fignum()), after="first-table")
    if p["n"] == 3:
        ladders(soup)
        error_cards(soup)
    if p["n"] == 4:
        voiced_example(soup)
    if p["n"] == 6:
        contrast_samples(soup)
        insert_after_section(soup, "الألوان الأربعة الأساسية", C.dna(fignum()), after="first-table")
        insert_after_section(soup, "ميزانية اللون", C.budget(fignum()), after="first-table")
        insert_after_section(soup, "مصفوفة التباين", C.contrast(fignum()), after="last-table")
        insert_after_section(soup, "الذهب بين الطباعة والشاشة", C.foil(fignum()))
        insert_after_section(soup, "سلّم الأحجام", C.type_specimen(fignum()), after="first-table")
        insert_after_section(soup, "«نظام النقطة»", C.nuqta(fignum()), after="lead")
        insert_after_section(soup, "الشبكة وقياس الصفحة", C.page_grid(fignum()), after="lead")
        insert_after_section(soup, "المفاهيم الأربعة", C.covers(fignum()), after="lead")
        insert_after_section(soup, "نظام العائلة", C.family(fignum()), after="first-table")
        gal = C.gallery_a(fignum()) + C.gallery_b(fignum()) + C.gallery_c(fignum()) + C.gallery_d(fignum())
        target = next(s for s in soup.find_all("section", class_="bab")
                      if "نظام العناصر التعليمية" in s.find("h2").get_text())
        target.find("div", class_="tbl").insert_after(frag(gal))
    replace_symbols(soup)
    root = soup.find("div", class_="root")
    return root.decode_contents(), babs


def build_appendix(key, letter, fname, title):
    md = (ROOT / fname).read_text(encoding="utf-8")
    md = re.sub(r"^# .*\n", "", md, count=1)
    # demote headings: ## -> ###, ### -> ####
    md = re.sub(r"^### ", "#### ", md, flags=re.M)
    md = re.sub(r"^## ", "### ", md, flags=re.M)
    fignum = FigNum(f"ملحق {letter}")
    soup = md_to_soup(md, lambda c: code_component(c, fignum))
    drop_hr(soup)
    for h in soup.find_all(["h3", "h4"]):
        h["data-outline"] = h.get_text(" ", strip=True)
        latinize_heading(h)
    style_tables(soup)
    style_code(soup)
    style_em(soup)
    style_quotes(soup)
    replace_symbols(soup)
    body = soup.find("div", class_="root").decode_contents()
    return (f'<section class="bab appx" id="appx-{key}"><header class="bab-h"><p class="eyebrow">ملحق {letter}</p>'
            f'<h2 data-outline="ملحق {letter}: {esc(title)}">{wrap_latin(title)}</h2><div class="nrule"></div></header>{body}</section>')


def index_sections():
    """Split bible/00 into its level-2 sections."""
    md = (BIBLE / "00-الفهرس-والقرارات-المعلقة.md").read_text(encoding="utf-8")
    parts = re.split(r"^## ", md, flags=re.M)
    out = {}
    for chunk in parts[1:]:
        head, _, body = chunk.partition("\n")
        out[head.strip()] = body
    status = re.search(r"^> \*\*المرجع الأعلى.*?(?=\n\n)", md, flags=re.S | re.M)
    return out, (status.group(0) if status else "")


def simple_md(md: str, fig_prefix="٠") -> str:
    fignum = FigNum(fig_prefix)
    soup = md_to_soup(md, lambda c: code_component(c, fignum))
    drop_hr(soup)
    for h in soup.find_all(["h3", "h4"]):
        h["data-outline"] = h.get_text(" ", strip=True)
    style_tables(soup)
    style_code(soup)
    style_em(soup)
    style_quotes(soup)
    replace_symbols(soup)
    return soup.find("div", class_="root").decode_contents()


# --------------------------------------------------------------------------- front and back matter

def sec_header(eyebrow, title, level="h1", anchor=None, outline=None):
    data = f' data-outline="{esc(outline or title)}"'
    return (f'<header class="sec-h"><p class="eyebrow">{eyebrow}</p><{level}{data}>{wrap_latin(title)}</{level}>'
            f'<div class="nrule"></div></header>')


def pgref(anchor):
    return f'<span class="pgref" data-for="{anchor}">٠٠٠</span>'


def mgmt_page():
    rows = [
        ("عنوان الوثيقة", "الدليل التحريري والعلمي لمنهج «صناعة المتكلّم العربي» — <span class=\"en\">Editorial &amp; Scholarly Bible</span>"),
        ("رمز الوثيقة", '<span class="ltr" style="font-family:var(--f-mono)">SMA-BIBLE-1.0</span>'),
        ("الإصدار", "١٫٠ (<span class=\"en\">Edition 1.0</span>) — <span class=\"en\">PDF Master</span>: نسخة رئيسية للطباعة والقراءة الرقمية"),
        ("تاريخ الإصدار", DATE_LINE),
        ("الحالة", f"مُعَدّ للاعتماد — {ar(N_DECISIONS)} قرارًا معلّقًا (ص {pgref('sec-decisions')})"),
        ("المرجعية", "المرجع الأعلى للمشروع بعد اعتماده؛ لا يُخالَف إلا بتوجيه صريح من صاحب المشروع، ويُسجَّل كل تعديل في سجل الإصدارات."),
        ("نطاق الحكم", "الكتب والمجلدات والوحدات والدروس والأمثلة والحوارات والتدريبات والسيناريوهات والاختبارات، وأدلة المعلمين، والمواد الصوتية والرقمية، ونصوص المحاضرات، وأوراق العمل."),
        ("الجمهور", "لجنة العلماء، ولجنة المناهج، والمؤلفون، والمحررون، والمصممون، والمدربون، وفريق إنتاج الكتب، وفريق إنتاج المواد الصوتية والرقمية."),
        ("جهة الإعداد", "فريق المشروع. أُعدّت الصياغة الأولى بمساعدة الذكاء الاصطناعي، وتخضع لمراجعة اللجنة العلمية قبل الاعتماد."),
        ("الجهة الناشرة", "تُحدَّد (القرار المعلّق ٢٠)."),
        ("الملفات المصدرية", 'ملفات <span class="en">Markdown</span> في <span class="ltr" style="font-family:var(--f-mono);font-size:.9em">books/sinaat-al-mutakallim/bible/</span>، ويُولَّد هذا الملف منها بأداة <span class="ltr" style="font-family:var(--f-mono);font-size:.9em">pdf/build.py</span>.'),
        ("الخطوط المضمّنة", 'Amiri، وReem Kufi، وIBM Plex Sans Arabic، وIBM Plex Sans، وCormorant Garamond، وAmiri Quran — بترخيص <span class="en">SIL Open Font License</span>.'),
        ("الحقوق", "© ٢٠٢٦ صاحب مشروع «صناعة المتكلّم العربي». جميع الحقوق محفوظة. تُشارَك الوثيقة مع لجان المشروع وفرقه للمراجعة والاعتماد والإنتاج، ولا تُنشر خارجها إلا بإذن صاحب المشروع."),
    ]
    trs = "".join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
    policy = ("<ul><li><strong>١٫٠</strong> الإصدار الأول، مُعَدّ للاعتماد.</li>"
              "<li><strong>١٫١، ١٫٢…</strong> تعديلات جزئية لا تغيّر البنية، ومنها تسجيل القرارات بعد اعتمادها.</li>"
              "<li><strong>٢٫٠</strong> تغيير بنيوي في الأجزاء أو الأبواب أو المصطلحات الحاكمة.</li>"
              "<li>كل إصدار يُسجَّل في سجل الإصدارات والتعديلات مع سببه، ويُعاد توليد الملف من مصادره.</li></ul>")
    notes = ("<ul><li>الأسماء في الأمثلة والحوارات افتراضية، ولا تشير إلى أشخاص حقيقيين.</li>"
             "<li>النصوص القرآنية في هذا الإصدار للتمثيل؛ وتُنقل في الكتب من مصدر المصحف الموثق ولا تُكتب يدويًا.</li>"
             "<li>وسوم التوثيق مثل <em class=\"tag-verify\">[يحتاج إلى تحقق من الصفحة]</em> ظاهرة عمدًا في هذا الإصدار حتى يُتحقق من مواضعها.</li>"
             "<li>الألوان في الملف بنظام الشاشة (<span class=\"en\">RGB</span>)؛ وللطباعة التجارية تُحوَّل بملف ألوان المطبعة ببروفة معتمدة.</li></ul>")
    return (f'<section class="fm-sec mgmt-sec" id="sec-mgmt">{sec_header("الوثيقة", "الحقوق وإدارة الوثيقة")}'
            f'<div class="sec-body"><div class="tbl"><table class="mgmt"><tbody>{trs}</tbody></table></div>'
            f'<h3 data-outline="سياسة الإصدارات">سياسة الإصدارات</h3>{policy}'
            f'<h3 data-outline="ملاحظات">ملاحظات</h3>{notes}'
            f'</div></section>')


def toc_page(entries):
    rows = []
    for kind, key, title, anchor in entries:
        if kind == "part":
            rows.append(f'<div class="toc-part"><span class="pn">{key}</span><a href="#{anchor}">{title}</a>'
                        f'<span class="pg" data-for="{anchor}">٠٠٠</span></div>')
        else:
            rows.append(f'<div class="toc-row"><span class="k">{key}</span><a href="#{anchor}">{title}</a>'
                        f'<span class="lead"></span><span class="pg" data-for="{anchor}">٠٠٠</span></div>')
    return f'<section class="fm-sec fm" id="sec-toc">{sec_header("الوثيقة", "فهرس المحتويات")}<div class="toc">{"".join(rows)}</div></section>'


def howto_page(idx_sections, part_babs):
    intro = ('<p>الدليل التحريري والعلمي هو <strong>دستور منظومة «صناعة المتكلّم العربي»</strong>: يحكم كل ما يُكتب ويُصمَّم ويُنتَج بعده، '
             'من الكتب والدروس والأمثلة والتدريبات والاختبارات، إلى المواد الصوتية والرقمية. وهو في هذا الإصدار <strong>مُعَدّ للاعتماد</strong>؛ '
             'فإذا اعتُمد صار المرجع الأعلى للمشروع، لا يُخالَف إلا بتوجيه صريح من صاحب المشروع.</p>')
    part_rows = "".join(
        f'<tr><td><a class="xref" href="#part-{p["n"]}">الجزء {p["word"]}</a></td><td>{p["title"]}</td>'
        f'<td>{ar(part_babs[p["n"]][0][0])}–{ar(part_babs[p["n"]][-1][0])}</td><td>{pgref("part-" + str(p["n"]))}</td></tr>'
        for p in PARTS)
    structure = (f'<div class="tbl short"><table><thead><tr><th>الجزء</th><th>موضوعه</th><th>الأبواب</th><th>الصفحة</th></tr></thead>'
                 f'<tbody>{part_rows}<tr><td><a class="xref" href="#part-appr">الاعتماد</a></td><td>القرارات المعلّقة، ونقاط للقرار العلمي، وورقة الاعتماد</td><td>—</td><td>{pgref("part-appr")}</td></tr>'
                 f'<tr><td><a class="xref" href="#part-appx">الملاحق</a></td><td>المسودات المُدخلة التي بُني عليها الدليل</td><td>أ–هـ</td><td>{pgref("part-appx")}</td></tr></tbody></table></div>')
    steps = ("<ol>"
             "<li>اقرأ الأجزاء الستة، أو ما يخص دورك منها (الجدول التالي).</li>"
             f"<li>راجع <a class=\"xref\" href=\"#sec-decisions\">القرارات المعلّقة</a> وتوصية اللجنة في كل منها (ص {pgref('sec-decisions')}).</li>"
             f"<li>سجّل قرارك في <a class=\"xref\" href=\"#sec-sheet\">ورقة الاعتماد</a> (ص {pgref('sec-sheet')}): موافقة على التوصية، أو خيار آخر مع ملاحظتك.</li>"
             "<li>بعد الاعتماد يُحدَّث الدليل إلى الإصدار ١٫١، وتبدأ كتابة الفصول بالقالب المعتمد.</li></ol>")
    roles = [
        ("لجنة العلماء", "الأول (المبادئ)، والرابع (التوثيق)، والقرارات ٨–١٠"),
        ("لجنة المناهج", "الثاني والثالث والرابع والخامس"),
        ("المؤلفون والمحررون", "الثاني (السجلات)، والثالث (الأمثلة والحوار)، والخامس (الأسلوب والمصطلحات)"),
        ("المصممون وفريق إنتاج الكتب", "السادس كاملًا، والخامس (البنية والمجلدات)"),
        ("المدربون", "الثالث (المقارنة والحوار)، والرابع (التربوي والصوت)"),
        ("فريق المواد الصوتية والرقمية", "الرابع (دليل الصوت ورموز الأداء)، والسادس (الإخراج الرقمي)"),
    ]
    roles_t = ('<div class="tbl short"><table><thead><tr><th>الدور</th><th>الأجزاء الأهم له</th></tr></thead><tbody>'
               + "".join(f"<tr><td><strong>{a}</strong></td><td>{b}</td></tr>" for a, b in roles) + "</tbody></table></div>")
    summary_md = idx_sections.get("خلاصة المقترحات المطلوبة (البند العشرون)", "")
    summary_md = (summary_md.replace("+ خريطة الكتاب", "+ خريطة الكتاب (ملحق ب)")
                  .replace("ملف المستويات والمخرجات", "الملحق ج").replace("ملف نظام التقييم", "الملحق د"))
    summary = simple_md(summary_md)
    legend = [
        ('<i class="rh fill-gold"></i>', "نقطة التعداد في القوائم، من «نظام النقطة»."),
        ('<em class="tag-verify">[يحتاج إلى تحقق من الصفحة]</em>', "وسم توثيق: موضع لم يُطابَق بعد على المصدر."),
        ('<em class="tag-dec"><a href="#dec-7">(قرار معلّق رقم ٧)</a></em>', "إحالة إلى قرار معلّق، تنقلك إليه عند النقر."),
        ('<a class="xref" href="#bab-22">الباب ٢٢</a>', "إحالة داخلية قابلة للنقر."),
        (C.dots(3), "سلّم الرسمية: عدد النقاط الممتلئة هو الدرجة (٣ من ٥ هنا)."),
        (C.rh("fill-c") + C.rh("half-c") + C.rh("half-g") + C.rh("line-g"), "درجات خطورة الخطأ: قاتل، مغيّر للمعنى، لافت، هنة."),
        (C.badge(1) + C.badge(2) + C.badge(3) + C.badge(4), "درجات المقارنة: غير ناجح، مقبول، ناجح، رفيع."),
    ]
    legend_t = ('<div class="tbl short"><table><thead><tr><th>الرمز</th><th>معناه</th></tr></thead><tbody>'
                + "".join(f"<tr><td style=\"width:52mm\">{a}</td><td>{b}</td></tr>" for a, b in legend) + "</tbody></table></div>")
    return (f'<section class="fm-sec fm" id="sec-howto">{sec_header("الوثيقة", "كيف تُقرأ هذه الوثيقة")}<div class="sec-body">'
            f'{intro}<h3 data-outline="بنية الوثيقة">بنية الوثيقة</h3>{structure}'
            f'<h3 data-outline="طريقة الاعتماد">طريقة الاعتماد</h3>{steps}'
            f'<h3 data-outline="لمن هذا الجزء؟">لمن هذا الجزء؟</h3>{roles_t}'
            f'<h3 data-outline="خلاصة المقترحات المطلوبة">خلاصة المقترحات المطلوبة</h3>{summary}'
            f'<h3 data-outline="مفتاح الرموز">مفتاح الرموز</h3>{legend_t}</div></section>')


def approval_body(idx_sections):
    dec_md = idx_sections["القرارات المعلّقة (تحتاج إلى اعتمادك)"]
    dec_md = dec_md.replace("### القرارات البصرية (الجزء السادس)", "### القرارات البصرية")
    dec_html = simple_md(dec_md)
    soup = frag(dec_html)
    for tr in soup.find_all("tr"):
        first = tr.find("td")
        if first:
            d = first.get_text(strip=True).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
            if d.isdigit():
                tr["id"] = f"dec-{int(d)}"
    for h in soup.find_all("h3"):
        h["data-outline"] = h.get_text(" ", strip=True)
    for t in soup.find_all("table"):
        t["class"] = (t.get("class") or []) + ["dense"]
    sci = simple_md(idx_sections["نقاط تحتاج إلى قرار علمي (مقترحات للنقاش)"])
    rows = "".join(
        f'<tr><td style="width:8mm"><strong>{ar(i + 1)}</strong></td><td style="width:34mm"><strong>{a}</strong></td><td>{b}</td>'
        f'<td class="box"><i></i></td><td class="line"></td></tr>'
        for i, (a, b) in enumerate(APPROVAL_ROWS))
    sheet = (f'<p>ضع علامة في خانة «موافق» إذا اعتمدتَ توصية اللجنة، أو اكتب الخيار البديل أو ملاحظتك في الخانة الأخيرة.</p>'
             f'<div class="tbl"><table class="approve"><thead><tr><th>#</th><th>القرار</th><th>توصية اللجنة</th><th>موافق</th><th>خيار آخر / ملاحظة</th></tr></thead>'
             f'<tbody>{rows}</tbody></table></div>'
             f'<div class="sign"><div>الاسم</div><div>الصفة</div><div>التاريخ</div><div>التوقيع</div></div>')
    return (f'<section class="bab first" id="sec-decisions">{bab_like_header("الاعتماد", "القرارات المعلّقة")}{soup.decode()}</section>'
            f'<section class="bab" id="sec-sci">{bab_like_header("الاعتماد", "نقاط تحتاج إلى قرار علمي")}{sci}</section>'
            f'<section class="bab fm" id="sec-sheet">{bab_like_header("الاعتماد", "ورقة الاعتماد")}{sheet}</section>')


def bab_like_header(eyebrow, title):
    return (f'<header class="bab-h"><p class="eyebrow">{eyebrow}</p><h2 data-outline="{esc(title)}">{wrap_latin(title)}</h2>'
            f'<div class="nrule"></div></header>')


def changelog(idx_sections):
    log = simple_md(idx_sections["سجل التغييرات"])
    policy = ('<p>يُسجَّل هنا كل تعديل على الدليل: رقم الإصدار، وتاريخه، والتغيير، وسببه. وتتبع الأرقام سياسة الإصدارات في '
              f'<a class="xref" href="#sec-mgmt">صفحة الحقوق وإدارة الوثيقة</a> (ص {pgref("sec-mgmt")}).</p>')
    return (f'<section class="fm-sec fm" id="sec-log">{sec_header("الوثيقة", "سجل الإصدارات والتعديلات")}'
            f'<div class="sec-body">{policy}{log}</div></section>')


# --------------------------------------------------------------------------- links

LINK_SKIP = ("h1", "h2", "h3", "h4", "a", "code", "figcaption", "style", "script", "title", "head")
LINK_SKIP_CLASS = ("opener", "cover-page", "title-page", "back-page", "toc", "sec-h", "bab-h", "fig")
DEC_RE = re.compile(r"(القرارات\s+|القرار(?:\s+المعلّق)?\s+(?:رقم\s+)?|قرار\s+معلّق\s+رقم\s+)([٠-٩]+)")
BAB_RE = re.compile(r"الباب\s+([٠-٩]+)")
PART_RE = re.compile(r"الجزء\s+(الأول|الثاني|الثالث|الرابع|الخامس|السادس)")
APPX_RE = re.compile(r"(?:الملحق|ملحق)\s+(أ|ب|ج|د|هـ)(?![\u0600-\u06FF])")
APPX_KEYS = {"أ": "a", "ب": "b", "ج": "c", "د": "d", "هـ": "e"}


def to_int(s):
    return int(s.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")))


def linkify(soup: BeautifulSoup, n_babs: int):
    for s in list(soup.find_all(string=True)):
        if not re.search(r"القرار|قرار|الباب|الجزء|ملحق", s):
            continue
        if any(p.name in LINK_SKIP for p in s.parents if isinstance(p, Tag)):
            continue
        if any(set(p.get("class") or []) & set(LINK_SKIP_CLASS) for p in s.parents if isinstance(p, Tag)):
            continue
        text = str(s)
        spans = []
        for m in DEC_RE.finditer(text):
            n = to_int(m.group(2))
            if 1 <= n <= N_DECISIONS:
                spans.append((m.start(), m.end(), f"dec-{n}"))
        for m in BAB_RE.finditer(text):
            n = to_int(m.group(1))
            if 1 <= n <= n_babs:
                spans.append((m.start(), m.end(), f"bab-{n}"))
        for m in PART_RE.finditer(text):
            spans.append((m.start(), m.end(), f"part-{PART_WORDS[m.group(1)]}"))
        for m in APPX_RE.finditer(text):
            spans.append((m.start(), m.end(), f"appx-{APPX_KEYS[m.group(1)]}"))
        if not spans:
            continue
        spans.sort()
        out, last = [], 0
        for a, b, href in spans:
            if a < last:
                continue
            out.append(esc(text[last:a]))
            out.append(f'<a class="xref" href="#{href}">{esc(text[a:b])}</a>')
            last = b
        out.append(esc(text[last:]))
        s.replace_with(frag("".join(out)))
    for em in soup.find_all("em", class_="tag-dec"):
        m = re.search(r"رقم\s+([٠-٩]+)", em.get_text())
        if m and not em.find("a"):
            inner = em.decode_contents()
            em.clear()
            em.append(frag(f'<a href="#dec-{to_int(m.group(1))}">{inner}</a>'))


# --------------------------------------------------------------------------- assembly

def page_rules() -> str:
    def rule(name, text):
        return (f'@page {name} {{ @top-right {{ content: "{text}"; font-family: "IBM Plex Sans Arabic"; '
                f'font-size: 7.4pt; color: #7F5F12; vertical-align: bottom; padding-bottom: 6mm; }} }}\n')
    css = rule("fm", "الوثيقة")
    for p in PARTS:
        css += rule(f"p{p['n']}", f"الجزء {p['word']} · {p['title']}")
    css += rule("appr", "الاعتماد")
    css += rule("appx", "الملاحق")
    return css


def assemble(font_css: str):
    idx_sections, _status = index_sections()
    bab_counter = [0]
    part_html, part_babs = {}, {}
    for p in PARTS:
        h, babs = build_part(p, bab_counter)
        part_html[p["n"]], part_babs[p["n"]] = h, babs
    n_babs = bab_counter[0]

    entries = [("row", "", "الحقوق وإدارة الوثيقة", "sec-mgmt"), ("row", "", "كيف تُقرأ هذه الوثيقة", "sec-howto")]
    for p in PARTS:
        entries.append(("part", ar(p["n"]), f"الجزء {p['word']} · {p['title']}", f"part-{p['n']}"))
        entries += [("row", e, t, a) for _n, e, t, a in part_babs[p["n"]]]
    entries.append(("part", "", "الاعتماد", "part-appr"))
    entries += [("row", "", "القرارات المعلّقة", "sec-decisions"), ("row", "", "نقاط تحتاج إلى قرار علمي", "sec-sci"),
                ("row", "", "ورقة الاعتماد", "sec-sheet")]
    entries.append(("part", "", "الملاحق", "part-appx"))
    entries += [("row", f"ملحق {l}", t, f"appx-{k}") for k, l, _f, t in APPENDICES]
    entries.append(("part", "", "سجل الإصدارات والتعديلات", "sec-log"))

    body = [C.cover(DATE_LINE), C.title_page(DATE_LINE, N_DECISIONS),
            '<div class="fm-wrap" style="page: fm">', mgmt_page(), toc_page(entries),
            howto_page(idx_sections, part_babs), "</div>"]
    for p in PARTS:
        items = [(e, t, a) for _n, e, t, a in part_babs[p["n"]]]
        body.append(C.opener(f"part-{p['n']}", f"الجزء {p['word']}", p["en"], ar(p["n"]), p["title"], p["lede"],
                             items, outline=f"الجزء {p['word']}: {p['title']}"))
        summary = "".join(f"<li>{esc(x)}</li>" for x in PART_SUMMARIES[p["n"]])
        summary = (f'<aside class="part-sum"><p class="lbl">خلاصة الجزء {p["word"]}</p><ul>{summary}</ul></aside>')
        body.append(f'<div class="part-body" style="page: p{p["n"]}">{part_html[p["n"]]}{summary}</div>')
    body.append(C.opener("part-appr", "الاعتماد", "Approval", "", "القرارات المطلوبة للاعتماد",
                         "عشرون قرارًا تنتظر كلمة صاحب المشروع، لكل منها توصية اللجنة، وفي آخرها ورقة اعتماد قابلة للطباعة.",
                         [("", "القرارات المعلّقة", "sec-decisions"), ("", "نقاط تحتاج إلى قرار علمي", "sec-sci"),
                          ("", "ورقة الاعتماد", "sec-sheet")], alt=True, outline="الاعتماد: القرارات المطلوبة للاعتماد"))
    body.append(f'<div class="part-body" style="page: appr">{approval_body(idx_sections)}</div>')
    body.append(C.opener("part-appx", "الملاحق", "Appendices", "", "المسودات المُدخلة",
                         "المسودات التي بُني عليها الدليل. تُعدَّل لتوافقه بعد الاعتماد؛ وعند التعارض يُقدَّم الدليل.",
                         [(f"ملحق {l}", t, f"appx-{k}") for k, l, _f, t in APPENDICES], alt=True,
                         outline="الملاحق: المسودات المُدخلة"))
    appx_note = ('<div class="note appx-note"><span class="lbl">عن هذه الملاحق</span><p>هذه مسودات سابقة للدليل، أُثبتت كما هي ليُرجع إليها. '
                 'وفيها فروق معروفة تُعالَج بعد الاعتماد: منها تسمية «القسم» في خريطة الكتاب (وهو «الباب» في الدليل)، '
                 'ووصف «متقن» في تفسير سلّم التقييم. وعند أي تعارض يُقدَّم الدليل.</p></div>')
    appx = "".join(build_appendix(*a) for a in APPENDICES)
    appx = appx.replace('<div class="nrule"></div></header>', '<div class="nrule"></div></header>' + appx_note, 1)
    body.append(f'<div class="part-body" style="page: appx">{appx}</div>')
    body.append(f'<div class="part-body" style="page: fm">{changelog(idx_sections)}</div>')
    body.append(C.back_cover())

    css = (HERE / "print.css").read_text(encoding="utf-8")
    doc = (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">'
           f'<title>الدليل التحريري والعلمي — صناعة المتكلّم العربي — الإصدار ١٫٠</title>'
           f'<style>{font_css}</style><style>{css}\n{page_rules()}</style></head><body>{"".join(body)}</body></html>')
    soup = BeautifulSoup(doc, "html.parser")
    linkify(soup, n_babs)
    return soup, entries


# --------------------------------------------------------------------------- measuring pass

TOKEN_RE = re.compile(r"Q\s*([A-Z]{1,2})\s*(\d{4})\s*Q")


def add_markers(soup: BeautifulSoup):
    """Insert invisible page markers. Returns (toc token map, QA pairs)."""
    counter = [0]

    def tok(kind):
        counter[0] += 1
        return f"Q{kind}{counter[0]:04d}Q"

    def abs_mark(el, kind, end=False):
        t = tok(kind)
        el.insert(0 if not end else len(el.contents), frag(f'<span class="pmk{" end" if end else ""}">{t}</span>'))
        return t

    MARKABLE = ["p", "li", "td", "th", "dd", "ul", "ol"]
    POS_CLASSES = {"note", "def", "warn", "rule-p", "card", "ctx-strip", "ladder", "panel", "paper",
                   "flow", "steps", "sec-body", "part-intro", "tbl"}

    def start_mark(el, kind):
        if not isinstance(el, Tag):
            return None
        classes = set(el.get("class") or [])
        if el.name in ("figure", "h3", "h4") or el.name in MARKABLE or classes & POS_CLASSES:
            return abs_mark(el, kind)
        target = el.find(MARKABLE)
        return abs_mark(target, kind) if target is not None else None

    toc_tokens = {}
    for anchor in [e for e in soup.select("[id]")]:
        if anchor.name in ("section",) or "opener" in (anchor.get("class") or []):
            toc_tokens[anchor["id"]] = abs_mark(anchor, "A")

    qa = []
    for h in soup.select(".bab-h, .sec-h, h3, h4"):
        if h.find_parent(class_=["opener", "cover-page", "title-page", "back-page", "fig"]):
            continue
        ht = abs_mark(h, "H")
        nxt = h.find_next_sibling()
        nt = start_mark(nxt, "N") if nxt is not None else None
        label = h.get_text(" ", strip=True)[:60]
        if nt:
            qa.append(("heading", label, ht, nt))
    for el in soup.select("figure.fig, div.tbl"):
        if el.find_parent("figure"):
            continue
        st, en = abs_mark(el, "S"), abs_mark(el, "E", end=True)
        kind = "figure" if el.name == "figure" else ("short-table" if "short" in el.get("class", []) else "table")
        flow = " fig-flow" if "fig-flow" in (el.get("class") or []) else ""
        qa.append((kind, el.get_text(" ", strip=True)[:60] + flow, st, en))
    return toc_tokens, qa


def token_pages(pdf: Path):
    pages = {}
    reader = PdfReader(str(pdf))
    for i, page in enumerate(reader.pages, start=1):
        for m in TOKEN_RE.finditer(page.extract_text() or ""):
            pages.setdefault(f"Q{m.group(1)}{m.group(2)}Q", i)
    return pages, len(reader.pages)


def fill_pages(soup: BeautifulSoup, pages_by_id: dict):
    for el in soup.select("[data-for]"):
        n = pages_by_id.get(el["data-for"])
        if n:
            el.string = ar(n)


def render(html_str: str, name: str) -> Path:
    CACHE.mkdir(exist_ok=True)
    src = CACHE / f"{name}.html"
    out = CACHE / f"{name}.pdf"
    src.write_text(html_str, encoding="utf-8")
    env = dict(os.environ)
    try:
        gnm = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
        env["NODE_PATH"] = os.pathsep.join(filter(None, [env.get("NODE_PATH", ""), gnm]))
    except FileNotFoundError:
        pass
    subprocess.run(["node", str(HERE / "render.js"), str(src), str(out)], check=True, env=env)
    return out


# --------------------------------------------------------------------------- post-processing

def outline_titles(soup: BeautifulSoup):
    titles = []
    for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        titles.append(h.get("data-outline") or h.get_text(" ", strip=True))
    return titles


def finalize(pdf_in: Path, titles: list, pdf_out: Path):
    reader = PdfReader(str(pdf_in))
    writer = PdfWriter(clone_from=reader)

    flat = []

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it)
            else:
                flat.append(it)
    walk(reader.outline)
    if len(flat) != len(titles):
        raise SystemExit(f"Outline mismatch: PDF has {len(flat)} bookmarks, HTML has {len(titles)} headings")

    if "/Outlines" in writer._root_object:
        del writer._root_object["/Outlines"]
    it_titles = iter(titles)

    def rebuild(items, parent=None):
        i = 0
        while i < len(items):
            item = items[i]
            if isinstance(item, list):
                i += 1
                continue
            page_no = reader.get_destination_page_number(item)
            top = item.get("/Top") if hasattr(item, "get") else None
            fit = Fit.xyz(left=None, top=float(top) if top is not None else None, zoom=None)
            ref = writer.add_outline_item(next(it_titles), page_no, parent=parent, fit=fit)
            if i + 1 < len(items) and isinstance(items[i + 1], list):
                rebuild(items[i + 1], ref)
                i += 2
            else:
                i += 1
    rebuild(reader.outline)

    writer.add_metadata({
        "/Title": "الدليل التحريري والعلمي — صناعة المتكلّم العربي — الإصدار ١٫٠",
        "/Subject": "Editorial & Scholarly Bible — Edition 1.0 — PDF Master",
        "/Author": "فريق مشروع «صناعة المتكلّم العربي»",
        "/Keywords": "صناعة المتكلّم العربي; الدليل التحريري والعلمي; Editorial & Scholarly Bible; Edition 1.0; PDF Master",
        "/Creator": "books/sinaat-al-mutakallim/pdf/build.py (Chromium)",
    })
    writer._root_object[NameObject("/Lang")] = TextStringObject("ar")
    vp = writer.create_viewer_preferences()
    vp[NameObject("/Direction")] = NameObject("/R2L")
    vp[NameObject("/DisplayDocTitle")] = BooleanObject(True)
    writer.page_mode = "/UseOutlines"
    with open(pdf_out, "wb") as f:
        writer.write(f)


# --------------------------------------------------------------------------- review

def review(pdf: Path, qa_report: list):
    import pypdfium2 as pdfium
    from PIL import Image

    rdir = CACHE / "review"
    rdir.mkdir(parents=True, exist_ok=True)
    for old in rdir.glob("*.png"):
        old.unlink()
    doc = pdfium.PdfDocument(str(pdf))
    thumbs, sparse = [], []
    for i in range(len(doc)):
        img = doc[i].render(scale=0.32).to_pil().convert("RGB")
        thumbs.append(img)
        px = img.load()
        w, h = img.size
        bg = px[w // 2, 4]
        ink = sum(1 for x in range(0, w, 2) for y in range(0, h, 2)
                  if sum(abs(a - b) for a, b in zip(px[x, y], bg)) > 60)
        ratio = ink / ((w // 2) * (h // 2))
        if ratio < 0.045:
            sparse.append((i + 1, round(ratio, 3)))
    cols, rows = 6, 3
    tw, th = thumbs[0].size
    for s in range(0, len(thumbs), cols * rows):
        sheet = Image.new("RGB", (cols * (tw + 12) + 12, rows * (th + 30) + 12), (200, 196, 188))
        for k, img in enumerate(thumbs[s:s + cols * rows]):
            x = 12 + (cols - 1 - k % cols) * (tw + 12)   # right-to-left like the book
            y = 12 + (k // cols) * (th + 30)
            sheet.paste(img, (x, y))
        sheet.save(rdir / f"sheet-{s // (cols * rows) + 1:02d}.png")
    print(f"review sheets: {rdir}")
    print("sparse pages (ink ratio):", sparse)
    for line in qa_report:
        print("QA:", line)


# --------------------------------------------------------------------------- typographic checks

DOT_BY_DIGIT = re.compile(r"[٠-٩٫][\s\u00a0\u200e\u200f]*·|·[\s\u00a0\u200e\u200f]*[٠-٩٫]")


def check_separators(soup: BeautifulSoup):
    """Fail on a middle dot beside an Arabic-Indic digit, in the text or in CSS generated content."""
    hits = []
    for node in soup.find_all(string=DOT_BY_DIGIT):
        if node.find_parent(["script", "title"]):
            continue
        text = str(node)
        if node.find_parent("style"):
            text = " ".join(re.findall(r'content:\s*"([^"]*)"', text))
        for m in DOT_BY_DIGIT.finditer(text):
            hits.append(text[max(0, m.start() - 30):m.end() + 30].replace("\n", " "))
    if hits:
        raise SystemExit("middle dot beside an Arabic-Indic digit (reads as «٠»); use «،» «؛» «:» «/» or "
                         "<i class=\"sep\"></i>:\n  " + "\n  ".join(hits))


FONT_FAMILIES = ("Amiri", "IBMPlexSans", "CormorantGaramond", "ReemKufi")


def check_fonts(pdf: Path):
    """Every font in the PDF must be an approved embedded face: no Type 3, no system fallback."""
    bad: dict = {}

    def scan(res, page_no):
        res = res.get_object() if res else {}
        for f in (res.get("/Font") or {}).values():
            f = f.get_object()
            name = "Type3" if f.get("/Subtype") == "/Type3" else str(f.get("/BaseFont", "?")).split("+")[-1]
            if name == "Type3" or not name.replace("-", "").startswith(FONT_FAMILIES):
                bad.setdefault(name, set()).add(page_no)
        for x in (res.get("/XObject") or {}).values():
            x = x.get_object()
            if x.get("/Subtype") == "/Form" and x.get("/Resources"):
                scan(x["/Resources"], page_no)

    for i, page in enumerate(PdfReader(str(pdf)).pages, 1):
        scan(page.get("/Resources"), i)
    if bad:
        raise SystemExit("fonts outside the approved set (a glyph missing from the text faces falls back to a "
                         "system font; a variable font becomes Type 3): "
                         + "; ".join(f"{k} on p{sorted(v)[:8]}" for k, v in bad.items()))


# --------------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    args = ap.parse_args()

    font_css = static_instances(ensure_fonts())
    soup, _entries = assemble(font_css)
    check_separators(soup)
    base_html = str(soup)

    # pass 1: measure
    s1 = BeautifulSoup(base_html, "html.parser")
    toc_tokens, qa = add_markers(s1)
    p1 = render(str(s1), "pass1")
    tpages, n1 = token_pages(p1)
    pages_by_id = {k: tpages.get(t) for k, t in toc_tokens.items()}
    missing = [k for k, v in pages_by_id.items() if v is None]
    if missing:
        print("warning: no page found for", missing[:10])

    report = []
    for kind, label, a, b in qa:
        pa, pb = tpages.get(a), tpages.get(b)
        if pa is None or pb is None:
            continue
        if kind == "heading" and pb > pa:
            report.append(f"orphan heading p{pa}: {label}")
        if kind in ("figure", "short-table") and pb > pa and "fig-flow" not in label:
            report.append(f"split {kind} p{pa}-{pb}: {label}")
        if kind == "table" and pb > pa:
            report.append(f"long table spans p{pa}-{pb} (header repeats): {label}")

    # pass 2: final
    s2 = BeautifulSoup(base_html, "html.parser")
    fill_pages(s2, pages_by_id)
    p2 = render(str(s2), "pass2")
    n2 = len(PdfReader(str(p2)).pages)
    if n2 != n1:
        raise SystemExit(f"layout changed between passes: {n1} vs {n2} pages")
    check_fonts(p2)

    # verification: final layout + markers must give the same pages
    s3 = BeautifulSoup(base_html, "html.parser")
    fill_pages(s3, pages_by_id)
    toc3, _ = add_markers(s3)
    p3 = render(str(s3), "pass3")
    t3, _ = token_pages(p3)
    drift = {k: (pages_by_id.get(k), t3.get(t)) for k, t in toc3.items() if t3.get(t) != pages_by_id.get(k)}
    if drift:
        raise SystemExit(f"page numbers drifted after filling the contents: {drift}")

    finalize(p2, outline_titles(s2), OUT)
    print(f"wrote {OUT} ({n2} pages)")
    for line in report:
        print(line)
    if args.review:
        review(OUT, report)


if __name__ == "__main__":
    main()
