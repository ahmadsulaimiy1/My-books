#!/usr/bin/env python3
"""Build the complete book «صناعة المتكلّم العربي» as one premium PDF.

    python3 book_build.py            build the PDF from the Markdown manuscript in ../book
    python3 book_build.py --review   also render page thumbnails and a layout report

Reuses the machinery of build.py (fonts, Markdown, Chromium rendering, page markers, font and
separator checks). The manuscript conventions it relies on are fixed in
book/_production/writer-brief.md §5: context cards, graded models ①–④, coded examples,
dialogue tables, labelled boxes, voice drills, checklists.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, TextStringObject, Fit

import build as B
import components as C
from components import ar, badge

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BOOK = ROOT / "book"
IMG = HERE / "images"
OUT = ROOT / "Sinaat-al-Mutakallim-al-Arabi_Complete-Book.pdf"
TITLE = "صناعة المتكلّم العربي"
SUBTITLE = "من سلامة اللسان إلى حسن البيان"
DESC = "منهج شامل في النطق والتعبير والخطاب وآداب التواصل والملكة الشفهية"
AUTHOR = "أحمد بن إبراهيم السليمي"
DUA = "غفر الله له ولوالديه ولجميع المسلمين"
EDITION = "الطبعة الأولى، ١٤٤٨هـ / ٢٠٢٦م"

ORD = ["", "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي عشر", "الثاني عشر", "الثالث عشر", "الرابع عشر"]
ORD_F = ["", "الأولى", "الثانية", "الثالثة", "الرابعة"]

PARTS = [
    dict(n=1, title="التأسيس", sub="الأسس، واللسان، والعبارة", folder="الجزء-الأول", babs=[1, 2, 3], en="Part One",
         lede="قبل أن تخاطب الشيخ والوزير والجمهور تحتاج إلى معيار تحكم به على الكلام، وصوت عربي واضح يحمله، "
              "وجملة عربية طبيعية تصوغه. على هذه الثلاثة يقوم كل ما بعدها."),
    dict(n=2, title="التواصل", sub="البيان، والمقام، والأدب", folder="الجزء-الثاني", babs=[4, 5, 6], en="Part Two",
         lede="الكلام السليم لا يكفي حتى يكون مرتبًا مبينًا، مناسبًا لمن يُقال له، مهذبًا يحفظ القلوب. "
              "في هذا الجزء تتعلم كيف تبني كلامك، وكيف تغيّره بتغير المخاطَب والمقام، وكيف تكسب به احترام السامع."),
    dict(n=3, title="المنصات", sub="الحوار، والمجالس، والمنبر والمنصة، والمؤسسة", folder="الجزء-الثالث",
         babs=[7, 8, 9, 10], en="Part Three",
         lede="هنا يخرج المتدرب إلى المقامات الحية: حوار يسأل فيه ويجيب ويعترض، ومجلس علم يدخله ويخرج منه بأدب، "
              "ومنبر ومنصة يخطب عليهما ويحاضر، ومؤسسة يُقابَل فيها ويدير فيها الاجتماع."),
    dict(n=4, title="التمكين", sub="الإعلام، والدبلوماسية، وبنك الأخطاء، والملكة", folder="الجزء-الرابع",
         babs=[11, 12, 13, 14], en="Part Four",
         lede="الجزء الأخير يضع المتكلم أمام المذياع والكاميرا، وفي اللقاء الرسمي والتفاوض، ويجمع له الأخطاء التي تُسقط "
              "الكلام، ثم ينتهي به إلى الغاية: أن يرتجل الكلام المناسب في موقف لم يستعد له."),
]

BABS = {
    1: ("الأسس", "فلسفة الكلام والملكة العربية", "٠", "ما الكلام الناجح؟"),
    2: ("اللسان", "هندسة النطق والصوت", "١", "هل صوتي عربي واضح؟"),
    3: ("العبارة", "الجملة العربية الطبيعية", "٢", "هل جملتي عربية طبيعية؟"),
    4: ("البيان", "ترتيب المعنى والبلاغة التطبيقية", "٣", "هل كلامي مرتب مبين، له افتتاح وانتقال وخاتمة؟"),
    5: ("المقام", "مَن يتكلم؟ ولمن؟ ولماذا؟ وأين؟ ومتى؟ وكيف؟", "٤", "هل أعرف لمن أتكلم، وكيف أغيّر كلامي بتغيّر المقام؟"),
    6: ("الأدب", "آداب الكلام وكسب القلوب", "٥", "هل يحترمني السامع ويألف كلامي؟"),
    7: ("الحوار", "السؤال والجواب والمناقشة والإقناع", "٦", "هل أُحسن السؤال والجواب والاعتراض؟"),
    8: ("المجالس", "مجالس العلم والجامعة والمجتمع", "٧", "هل أُحسن الدخول إلى مجلس العلم والكلام فيه والخروج منه؟"),
    9: ("المنبر والمنصة", "الخطبة والمحاضرة والكلمة وعرض البحث", "٨", "هل أُحسن الخطبة والمحاضرة والكلمة؟"),
    10: ("المؤسسة", "الإدارة والقيادة والمقابلة الوظيفية", "٩", "هل أجتاز المقابلة، وأدير الاجتماع، وأخاطب الرئيس والمرؤوس؟"),
    11: ("الإعلام والتقديم", "المذياع والشاشة والمنصة", "١٠", "هل أتكلم أمام المذياع والكاميرا بثقة ووضوح؟"),
    12: ("الدبلوماسية والتواصل الرسمي", "البروتوكول والمجاملة والتفاوض", "١١", "هل أُحسن الخطاب الرسمي والتحفظ والتفاوض؟"),
    13: ("بنك الأخطاء", "الأخطاء القاتلة وما دونها", "مرجع", "ما الأخطاء التي تُسقط المتكلم، وكيف أتخلص منها؟"),
    14: ("الملكة", "الارتجال", "١٢", "هل أرتجل الكلام المناسب في موقف لم أستعد له؟"),
}
BAB_FOLDER = {n: f"الباب-{ORD[n].replace(' ', '-')}" for n in BABS}
BAB_PART = {b: p["n"] for p in PARTS for b in p["babs"]}

APPX_ORDER = ["أ", "ب", "ج", "د", "هـ", "و", "ز"]


# --------------------------------------------------------------------------- utilities

def esc(s):
    return B.esc(s)


def frag(s):
    return B.frag(s)


def read_md(path: Path) -> str:
    md = path.read_text(encoding="utf-8")
    # internal review records are not part of the published text
    md = re.split(r"^#{2,4}\s*سجل اعتماد الفصل.*$", md, maxsplit=1, flags=re.M)[0]
    return md


def code_handler(code: str) -> str:
    return f'<pre class="mono">{esc(code.strip())}</pre>'


def md_soup(md: str) -> BeautifulSoup:
    soup = B.md_to_soup(md, code_handler)
    B.drop_hr(soup)
    return soup


def text_of(el) -> str:
    return el.get_text(" ", strip=True) if isinstance(el, Tag) else str(el).strip()


# --------------------------------------------------------------------------- manuscript transforms

KINDS = [
    (("التدريب الصوتي", "تدريب النطق", "تمارين النطق", "التدريب على النطق", "الأداء المتعدد"), "تدريب صوتي", "k-drill"),
    (("المحاكاة",), "محاكاة", "k-sim"),
    (("الاستماع", "السماع"), "استماع", "k-listen"),
    (("تدريب", "التدريبات", "تمرين", "التمارين"), "تدريب", "k-practice"),
    (("الموقف", "بطاقة المقام", "المواقف الواقعية"), "الموقف", "k-ctx"),
    (("من التراث", "الشاهد", "التأصيل"), "من التراث", "k-heritage"),
    (("المقارنة", "النماذج", "جدول تحليل الفروق"), "المقارنة المتدرجة", "k-model"),
    (("القاعدة", "القواعد"), "القاعدة", "k-rule"),
    (("الحوار", "حوار"), "حوار", "k-dialogue"),
    (("دراسة حالة", "بنك المواقف", "حالات"), "حالات ومواقف", "k-case"),
    (("التقويم", "اختبار", "معيار الإتقان", "قائمة الفحص", "مهمة التسجيل", "المهمة الواقعية"), "تقويم", "k-assess"),
    (("الخلاصة",), "خلاصة", "k-summary"),
    (("للمدرب",), "للمدرب", "k-trainer"),
    (("من علم التواصل", "من علم اللغة"), "تحليل حديث", "k-listen"),
]


def kind_of(title: str):
    for keys, label, cls in KINDS:
        if any(title.startswith(k) or f" {k}" in f" {title}"[:len(k) + 12] for k in keys):
            return label, cls
    return None


LABELS = {
    "تعريف": "def", "قاعدة": "rule", "قاعدة جامعة": "rule", "قاعدة الترتيب": "rule", "تنبيه": "warn",
    "فائدة": "tip", "للمدرب": "trainer", "دراسة حالة": "case", "ملاحظة": "note", "من علم التواصل": "comm",
    "من علم اللغة الحديث": "comm", "تحليل حديث": "comm", "مثال": "note", "تذكير": "tip", "خلاصة": "tip",
}

DIR_RE = re.compile(r"\[([^\]\[]{1,80})\]")
TAG_TEXTS = ("يحتاج إلى تحقق", "استنباط", "تحليل حديث", "يُعرض على", "أداة تدريبية", "موثّق")


def wrap_dirs(tag: Tag, soup):
    """Stage directions [..] inside dialogue cells and models -> muted span (not verification tags)."""
    for s in list(tag.find_all(string=DIR_RE)):
        if s.find_parent(["em", "code"]):
            continue
        txt = str(s)
        out, last = [], 0
        for m in DIR_RE.finditer(txt):
            inner = m.group(1)
            if any(t in inner for t in TAG_TEXTS) or inner.startswith("م") and "-" in inner:
                continue
            out.append(esc(txt[last:m.start()]))
            out.append(f'<span class="dir">[{esc(inner)}]</span>')
            last = m.end()
        if out:
            out.append(esc(txt[last:]))
            s.replace_with(frag("".join(out)))


def split_lines(p: Tag):
    html = p.decode_contents()
    return [ln.strip() for ln in html.split("\n") if ln.strip()]


EX_START = re.compile(r"^\s*\[م[٠-٩]+-ب[٠-٩]+-ف[٠-٩]+-مث[٠-٩]+\]")


def ex_line(ln: str) -> str:
    t = BeautifulSoup(ln, "html.parser").get_text().strip()
    if t.startswith("✘"):
        cls, ic, body = "bad", B.SVG_NO, ln.split("✘", 1)[1]
        ic = f'<span class="ic no">{ic}</span>'
    elif t.startswith("✔"):
        cls, body = "good", ln.split("✔", 1)[1]
        ic = f'<span class="ic ok">{B.SVG_OK}</span>'
    elif t.startswith("◐"):
        cls, body = "mid", ln.split("◐", 1)[1]
        ic = '<span class="ic"><i class="ic-mid"></i></span>'
    else:
        return f'<div class="ln plain"><span class="tx">{ln}</span></div>'
    return f'<div class="ln {cls}">{ic}<span class="tx">{body.strip()}</span></div>'


def transform_examples(soup):
    for p in list(soup.find_all("p")):
        if p.find_parent(["td", "li", "blockquote"]):
            continue
        lines = split_lines(p)
        if not lines:
            continue
        first_txt = BeautifulSoup(lines[0], "html.parser").get_text().strip()
        coded = EX_START.match(first_txt)
        marked = sum(1 for ln in lines if BeautifulSoup(ln, "html.parser").get_text().strip()[:1] in "✘✔◐")
        if not coded and not (marked >= 2 and len(lines) >= 2):
            continue
        top = ""
        body_lines = lines
        if coded:
            m = re.match(r"^\s*(\[[^\]]+\])(.*)$", lines[0], flags=re.S)
            code, ctx = m.group(1), m.group(2).strip()
            top = f'<div class="ex-top"><span class="ex-code">{code}</span><span>{ctx}</span></div>'
            body_lines = lines[1:]
        card = f'<div class="ex-card">{top}{"".join(ex_line(ln) for ln in body_lines)}</div>'
        p.replace_with(frag(card))


TIER = {"①": 1, "②": 2, "③": 3, "④": 4}


def transform_models(soup):
    for p in list(soup.find_all("p")):
        t = p.get_text(" ", strip=True)
        if not t or t[0] not in TIER or len(t) > 70:
            continue
        nxt = p.find_next_sibling()
        if nxt is None or nxt.name != "blockquote":
            continue
        n = TIER[t[0]]
        label = esc(t[1:].strip().rstrip(":："))
        wrap_dirs(nxt, soup)
        inner = nxt.decode_contents()
        html = (f'<div class="model t{n}">{badge(n)}<div><p class="ml">{label}</p>'
                f'<div class="mq">{inner}</div></div></div>')
        nxt.decompose()
        p.replace_with(frag(html))


def transform_context_cards(soup):
    for p in list(soup.find_all("p")):
        t = p.get_text(" ", strip=True)
        if not t.startswith("▣"):
            continue
        tbl = p.find_next_sibling()
        if tbl is not None and tbl.name == "table":
            rows = []
            for tr in tbl.find_all("tr"):
                cells = tr.find_all(["td", "th"])
                if len(cells) < 2 or tr.find_parent("thead"):
                    continue
                k = cells[0].get_text(" ", strip=True)
                v = cells[1].decode_contents()
                wide = " wide" if len(cells[1].get_text()) > 70 else ""
                rows.append(f'<div class="{wide.strip()}"><dt>{esc(k)}</dt><dd>{v}</dd></div>')
            title = esc(t.lstrip("▣").strip().strip("*") or "بطاقة المقام")
            card = f'<div class="ctx-card"><div class="cc-h"><i></i><span>{title}</span></div><dl>{"".join(rows)}</dl></div>'
            tbl.decompose()
            p.replace_with(frag(card))
        else:
            # inline card: ▣ **المتكلم:** …؛ **المخاطَب:** …
            p["class"] = ["ctx-inline"]
            inner = p.decode_contents().replace("▣", "", 1)
            p.replace_with(frag(f'<div class="ctx-card"><div class="cc-h"><i></i><span>بطاقة المقام</span></div>'
                                f'<dl><div class="wide"><dd>{inner}</dd></div></dl></div>'))


def transform_dialogues(soup):
    for t in list(soup.find_all("table")):
        head = [c.get_text(strip=True) for c in (t.find("tr").find_all(["th", "td"]) if t.find("tr") else [])]
        if len(head) != 3 or head[0] != "السطر" or "المتكلم" not in head[1]:
            continue
        t["class"] = ["dlg"]
        for tr in t.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) == 3:
                cells[0]["class"] = ["ln"]
                cells[1]["class"] = ["who"]
                cells[2]["class"] = ["say"]
                wrap_dirs(cells[2], soup)
        prev = t.find_previous(["h5", "p", "h4"])
        improved = prev is not None and ("المحسّنة" in prev.get_text() or "المحسنة" in prev.get_text())
        label = "النسخة المحسّنة" if improved else "الحوار"
        wrap = soup.new_tag("div", attrs={"class": "dlg-wrap improved" if improved else "dlg-wrap"})
        t.wrap(wrap)
        wrap.insert(0, frag(f'<div class="dlg-h"><span>{label}</span></div>'))


DRILL_HINT = re.compile(r"(//|\(ت\)|↓|↑)")


def transform_blockquotes(soup):
    for bq in list(soup.find_all("blockquote")):
        if bq.find_parent("blockquote"):
            continue
        text = bq.get_text("\n", strip=True)
        paras = bq.find_all("p", recursive=False) or [bq]
        first = paras[0]
        strong = first.find("strong")
        label = None
        if strong is not None and first.contents and (first.contents[0] is strong or (
                isinstance(first.contents[0], NavigableString) and not first.contents[0].strip()
                and first.contents[1] is strong)):
            lab = strong.get_text(strip=True).rstrip(":：").strip()
            if lab in LABELS or any(lab.startswith(k) for k in ("دراسة حالة", "قاعدة", "تنبيه", "من علم")):
                label = lab
                strong.decompose()
                # drop the leading colon/space left after the label
                if first.contents and isinstance(first.contents[0], NavigableString):
                    first.contents[0].replace_with(first.contents[0].lstrip(" :："))
        if label:
            kind = LABELS.get(label) or next((v for k, v in LABELS.items() if label.startswith(k)), "note")
            inner = bq.decode_contents()
            if kind == "rule":
                html = f'<div class="box rule"><div><span class="lbl">{esc(label)}</span>{inner}</div></div>'
            else:
                html = f'<div class="box {kind}"><span class="lbl">{esc(label)}</span>{inner}</div>'
            bq.replace_with(frag(html))
            continue
        if DRILL_HINT.search(text) and re.search(r"[ً-ْ]", text):
            lines = []
            for p in paras:
                lines += split_lines(p)
            body = "".join(f'<span class="dl">{ln}</span>' for ln in lines)
            bq.replace_with(frag(f'<div class="drill"><span class="lbl">نص التدريب الصوتي</span>{body}</div>'))
            continue
        wrap_dirs(bq, soup)
        bq.replace_with(frag(f'<div class="speech">{bq.decode_contents()}</div>'))


def transform_ayat(soup):
    for p in soup.find_all("p"):
        t = p.get_text().strip()
        if not t.startswith("﴿") or p.find_parent(["td", "li"]):
            continue
        html = p.decode_contents()
        k = html.rfind("﴾")
        if k != -1 and html[k + 1:].strip():
            html = html[:k + 1] + f'<span class="ref">{html[k + 1:].strip()}</span>'
        html = html.replace("﴿", '<span class="qb">﴿</span>').replace("﴾", '<span class="qb">﴾</span>')
        p.clear()
        p.append(frag(html))
        p["class"] = ["ayah"]


def transform_checklists(soup):
    for ul in soup.find_all("ul"):
        lis = ul.find_all("li", recursive=False)
        if lis and all(li.get_text().lstrip().startswith(("[ ]", "[✔]", "[x]", "[X]")) for li in lis):
            ul["class"] = ["checklist"]
            for li in lis:
                for s in li.find_all(string=True):
                    if re.match(r"^\s*\[( |✔|x|X)\]\s*", s):
                        s.replace_with(re.sub(r"^\s*\[( |✔|x|X)\]\s*", "", s))
                        break


def transform_em(soup):
    for e in soup.find_all("em"):
        t = e.get_text(strip=True)
        if t.startswith("[") and t.endswith("]"):
            e["class"] = ["tag-verify"]


def transform_why(soup):
    for p in soup.find_all("p"):
        s = p.find("strong")
        if s is not None and p.contents and p.contents[0] is s and s.get_text().strip().startswith(("لماذا", "ما الذي جعل")):
            p["class"] = (p.get("class") or []) + ["why"]


def headings(soup, lesson_eyebrow=True):
    """md H2 -> h4.lesson, md H3 -> h5 (+kind chip), md H4 -> p.hx (not bookmarked)."""
    for h in soup.find_all("h2"):
        t = h.get_text(" ", strip=True)
        k, title = "", t
        m = re.match(r"^(الدرس\s+\S+|المستوى\s+\S+|القسم\s+\S+)\s*[:：]\s*(.+)$", t)
        if m:
            k, title = m.group(1), m.group(2)
        new = frag(f'<h4 class="lesson" data-outline="{esc(t)}">{f"<span class=k>{esc(k)}</span>" if k else ""}'
                   f'{B.wrap_latin(title)}</h4>')
        h.replace_with(new)
    for h in soup.find_all("h3"):
        t = h.get_text(" ", strip=True)
        inner = h.decode_contents()
        kd = kind_of(t)
        if kd and t.replace("ال", "", 1).startswith(kd[0].replace("ال", "", 1)[:4]):
            kd = None   # the heading already says what the chip would say
        chip = f'<span class="kind {kd[1]}">{kd[0]}</span>' if kd else ""
        h.replace_with(frag(f'<h5 data-outline="{esc(t)}">{chip}{inner}</h5>'))
    for h in soup.find_all(["h4"]):
        if "lesson" in (h.get("class") or []):
            continue
        h.replace_with(frag(f'<p class="hx">{h.decode_contents()}</p>'))
    for h in soup.find_all(["h5", "h6"]):
        if h.get("data-outline") is None and h.find_parent(class_="idx") is None:
            h.name = "p"
            h["class"] = ["hx"]


def mark_practice(root: Tag):
    """Exercise sub-headings inside practice sections get the practice accent."""
    current = None
    for el in root.find_all(["h4", "h5", "p"], recursive=True):
        if el.name == "h4" or el.name == "h5":
            chip = el.find(class_="kind")
            current = chip.get("class")[1] if chip else None
        elif "hx" in (el.get("class") or []) and current in ("k-practice", "k-sim"):
            el.find_parent() and el.parent
            el["class"] = el.get("class") + ["px"]


KEEP_CLASSES = ("box", "model", "ex-card", "ctx-card", "drill", "ch-h")


def keep_wrappers(soup):
    """Chromium paints a sliver of a background box at the foot of the page it was pushed away
    from; hold the no-break rule on a transparent wrapper instead of on the painted box."""
    for el in soup.find_all(["div", "header"], class_=lambda c: c and any(k in c.split() for k in KEEP_CLASSES)):
        if el.parent is not None and "keep" in (el.parent.get("class") or []):
            continue
        w = soup.new_tag("div", attrs={"class": "keep"})
        el.wrap(w)


def keep_headings(soup):
    """A heading followed by an unbreakable block travels with it (break-after: avoid alone is not
    reliable in Chromium when the next block does not fit)."""
    for h in soup.find_all(["h4", "h5", "p"]):
        if h.name == "p" and "hx" not in (h.get("class") or []):
            continue
        nxt = h.find_next_sibling()
        if nxt is None or not isinstance(nxt, Tag):
            continue
        cls = nxt.get("class") or []
        small_tbl = "tbl" in cls and "short" in cls
        if "keep" in cls or small_tbl or (nxt.name == "div" and "dlg-wrap" not in cls and len(nxt.get_text()) < 900):
            w = soup.new_tag("div", attrs={"class": "keep-with"})
            h.wrap(w)
            w.append(nxt.extract())


def transform(soup):
    transform_context_cards(soup)
    transform_models(soup)
    transform_examples(soup)
    transform_dialogues(soup)
    transform_blockquotes(soup)
    transform_ayat(soup)
    transform_checklists(soup)
    transform_em(soup)
    transform_why(soup)
    headings(soup)
    B.style_tables(soup)
    B.style_code(soup)
    B.replace_symbols(soup)
    for t in soup.find_all("table"):
        if "dlg" in (t.get("class") or []):
            wrap = t.find_parent("div", class_="tbl")
            if wrap is not None:
                wrap.unwrap()


# --------------------------------------------------------------------------- manuscript discovery

def chapter_files(folder: Path):
    groups = {}
    for f in sorted(folder.glob("ف*.md")):
        m = re.match(r"ف(\d+)", f.stem)
        if not m:
            continue
        groups.setdefault(int(m.group(1)), []).append(f)
    return [groups[k] for k in sorted(groups)]


def split_title(h1: str):
    h1 = re.sub(r"\s*\(تابع\)\s*$", "", h1.strip())
    if ":" in h1:
        a, b = h1.split(":", 1)
        return a.strip(), b.strip()
    return "", h1


def load_chapter(files):
    md_all = [read_md(f) for f in files]
    first = md_all[0]
    m = re.search(r"^#\s+(.+)$", first, flags=re.M)
    eyebrow, title = split_title(m.group(1)) if m else ("", files[0].stem)
    sub, note = "", ""
    body_parts = []
    for i, md in enumerate(md_all):
        md = re.sub(r"^#\s+.+\n", "", md, count=1, flags=re.M)
        if i == 0:
            lead = md.lstrip("\n")
            ms = re.match(r"##\s+(.+)\n", lead)
            if ms:
                nxt_line = lead[ms.end():].lstrip("\n")
                # subtitle only if it is not a structural block heading
                if not re.match(r"(مدخل|الدرس|التطبيق|أهداف)", ms.group(1)):
                    sub = ms.group(1).strip()
                    lead = nxt_line
            mn = re.match(r"\*\((.+?)\)\*\s*\n", lead)
            if mn:
                note = mn.group(1)
                lead = lead[mn.end():]
            md = lead
        body_parts.append(md)
    return eyebrow, title, sub, note, "\n\n".join(body_parts)


def ch_grid_svg():
    lines = []
    for c in range(-60, 200, 9):
        lines.append(f'<line x1="{c}" y1="0" x2="{c + 60}" y2="60" stroke="#0E2D72" stroke-width="0.25"/>')
        lines.append(f'<line x1="{c + 60}" y1="0" x2="{c}" y2="60" stroke="#0E2D72" stroke-width="0.25"/>')
    return f'<svg class="grid" viewBox="0 0 166 60" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{"".join(lines)}</svg>'


def chapter_html(bab, n, files, anchor):
    eyebrow, title, sub, note, body = load_chapter(files)
    soup = md_soup(body)
    transform(soup)
    code = f"م{ar(BAB_PART[bab])}-ب{ar(bab)}-ف{ar(n)}"
    eb = f"الباب {ORD[bab]}{'<i class=sep></i>' if eyebrow else ''}{esc(eyebrow)}"
    header = (f'<header class="ch-h">{ch_grid_svg()}<div class="bar"></div>'
              f'<div class="nbox"><span>{ar(n)}</span></div>'
              f'<p class="eb"><span>{eb}</span><span class="code">{code}</span></p>'
              f'<h3 data-outline="{esc((eyebrow + ": ") if eyebrow else "")}{esc(title)}">{B.wrap_latin(title)}</h3>'
              f'{f"<p class=sub>{esc(sub)}</p>" if sub else ""}</header>')
    note_html = f'<p class="chnote">{esc(note)}</p>' if note else ""
    root = soup.find("div", class_="root")
    return (f'<section class="ch" id="{anchor}" style="page: b{bab}">{header}{note_html}{root.decode_contents()}</section>',
            eyebrow, title)


def bab_intro_html(bab, path: Path):
    md = read_md(path)
    md = re.sub(r"^#\s+.+\n", "", md, count=1, flags=re.M)
    lead = md.lstrip("\n")
    ms = re.match(r"##\s+(.+)\n", lead)
    if ms:
        lead = lead[ms.end():]
    # the guiding question is shown on the opener page
    lead = re.sub(r"^\s*>\s*.*السؤال الذي يجيب عنه.*\n", "", lead, count=1)
    soup = md_soup(lead)
    transform(soup)
    return soup.find("div", class_="root").decode_contents()


# --------------------------------------------------------------------------- designed pages

def frame_svg(W=200, H=259.6, bg="#082567", lattice=True, alif_x=30, hline=None, frame=True):
    gold = "#C9A227"
    line = C._mix(bg, gold, 0.85)
    lat = C._mix(bg, "#E1C46A", 0.07)
    parts = [f'<svg class="arch" viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true">']
    if lattice:
        for c in range(-int(H), int(W) + 1, 14):
            parts.append(f'<line x1="{c}" y1="0" x2="{c + H}" y2="{H}" stroke="{lat}" stroke-width="0.2"/>')
        for c in range(0, int(W + H) + 1, 14):
            parts.append(f'<line x1="{c}" y1="0" x2="{c - H}" y2="{H}" stroke="{lat}" stroke-width="0.2"/>')
    if frame:
        parts.append(f'<rect x="11" y="11" width="{W - 22}" height="{H - 22}" fill="none" stroke="{line}" stroke-width="0.3"/>')
    if alif_x:
        parts.append(f'<line x1="{alif_x}" y1="11" x2="{alif_x}" y2="{H - 11}" stroke="{line}" stroke-width="0.3"/>')
        parts.append(C._rhombus(alif_x, 11, 1.5, gold))
        parts.append(C._rhombus(alif_x, H - 11, 2.1, "#B21F35"))
    if hline:
        parts.append(f'<line x1="11" y1="{hline}" x2="{W - 11}" y2="{hline}" stroke="{line}" stroke-width="0.3"/>')
        parts.append(C._rhombus(W - 11, hline, 1.5, gold))
        if alif_x:
            parts.append(C._rhombus(alif_x, hline, 1.5, gold))
    parts.append("</svg>")
    return "".join(parts)


def cover():
    return f'''<section class="full cover" aria-label="الغلاف">{frame_svg(hline=160)}
<div class="cv-kick"><span>الكتاب كاملًا</span><span class="en">The Complete Book</span></div>
<p class="cv-mark foil"><span>صناعة</span><span>المتكلّم العربي</span></p>
<p class="cv-sub">{SUBTITLE}</p>
<p class="cv-desc">{DESC}</p>
<p class="cv-ed"><span>الأجزاء الأربعة</span><i class="sep"></i><span>أربعة عشر بابًا</span><i class="sep"></i><span>والملاحق</span></p>
<p class="cv-auth"><span class="l">تأليف</span><span class="n">{AUTHOR}</span><span class="d">{DUA}</span></p>
</section>'''


def front_pages():
    half = (f'<section class="fp-center halftitle"><p class="t">{TITLE}</p><p class="s">{SUBTITLE}</p></section>')
    authorp = (f'<section class="fp-center authorpage"><p class="l">المؤلف</p><p class="n">{AUTHOR}</p>'
               f'<p class="du">{DUA}</p></section>')
    tp = (f'<section class="fp-center tp" style="position:relative"><p class="t">{TITLE}</p><p class="s">{SUBTITLE}</p>'
          f'<p class="d">{DESC}</p><div class="rule"><i></i></div><p class="by">تأليف</p><p class="n">{AUTHOR}</p>'
          f'<p class="du">{DUA}</p><p class="ed">{EDITION}</p></section>')
    rows = [
        ("العنوان", f"{TITLE}: {SUBTITLE}"), ("العنوان الشارح", DESC), ("المؤلف", f"{AUTHOR}، {DUA}"),
        ("الطبعة", f"{EDITION}، نسخة كاملة معدّة للجنة المراجعة العلمية والنشر"),
        ("البنية", "أربعة أجزاء، وأربعة عشر بابًا تقابل مستويات البرنامج من ٠ إلى ١٢ وبنك الأخطاء، وسبعة ملاحق"),
        ("المقاس", "٢٠ × ٢٦ سم (مقاس كتاب الطالب المعتمد)"),
        ("الناشر", "يُحدَّد عند النشر"), ("رقم الإيداع والترقيم الدولي", "يُضافان عند النشر"),
        ("المرجع الحاكم", "الدليل التحريري والعلمي للمشروع، الإصدار ١٫٠ (معتمد)"),
    ]
    trs = "".join(f'<tr><th scope="row">{k}</th><td>{v}</td></tr>' for k, v in rows)
    copy = f'''<section class="copy-page" aria-label="صفحة الحقوق">
<p class="big">{TITLE}: {SUBTITLE}</p>
<div class="tbl"><table><tbody>{trs}</tbody></table></div>
<p><b>حقوق التأليف والنشر محفوظة للمؤلف.</b> لا يجوز نسخ هذا الكتاب أو جزء منه، ولا اختزانه في نظام استرجاع، ولا نقله بأي وسيلة ورقية أو إلكترونية أو صوتية أو مرئية، إلا بإذن مكتوب من المؤلف؛ ويُستثنى الاقتباس اليسير لأغراض البحث والتعليم مع العزو إلى الكتاب ومؤلفه.</p>
<p><b>الأسماء في الأمثلة والحوارات</b> أسماء افتراضية للتمثيل التدريبي، لا يُقصد بها أشخاص حقيقيون، وما ذُكر من مدن فهو خلفية للموقف.</p>
<p><b>وسوم التوثيق:</b> تظهر في هذه الطبعة علامات مثل «يحتاج إلى تحقق من الصفحة» بجوار بعض النقول، وهي من منهج الكتاب في الأمانة العلمية، وتُزال في طبعة النشر بعد مطابقة كل نقل على طبعته المعتمدة.</p>
<p><b>الصور:</b> الصور الفوتوغرافية في فواتح الأجزاء والأبواب من الملك العام أو مرخصة بترخيص CC0، ومصادرها مثبتة في صفحة «مصادر الصور» آخر الكتاب.</p>
</section>'''
    return half + authorp + tp + copy


def sec_header(anchor, eyebrow, title, page="fm"):
    return (f'<header class="sec-h" id="{anchor}"><p class="eb">{esc(eyebrow)}</p>'
            f'<h2 data-outline="{esc(title)}">{esc(title)}</h2><div class="rule"></div></header>')


def md_section(anchor, eyebrow, title, md, page="fm", extra_cls=""):
    soup = md_soup(md)
    transform(soup)
    return (f'<section class="fm-sec {extra_cls}" style="page: {page}">{sec_header(anchor, eyebrow, title)}'
            f'<div class="sec-body">{soup.find("div", class_="root").decode_contents()}</div></section>')


def pgref(anchor):
    return f'<span class="pg" data-for="{anchor}">٠٠٠٠</span>'


def part_opener(p, bab_rows, photo):
    lis = "".join(f'<li><span>الباب {ORD[b]}</span><b><a href="#bab-{b}">{esc(BABS[b][0])}</a></b></li>' for b in p["babs"])
    img = ""
    if photo:
        img = (f'<img class="photo" src="{photo["src"]}" alt=""><div class="photo-edge"></div>'
               f'<span class="po-credit">{esc(photo["credit"])}</span>')
    return f'''<section class="full part-op" id="part-{p["n"]}">{frame_svg(alif_x=None, frame=False, lattice=not photo)}{img}
<div class="nbox po-nbox"><span>{ar(p["n"])}</span></div>
<p class="po-kick">الجزء {ORD[p["n"]]}<span class="en">{p["en"]}</span></p>
<h1 data-outline="الجزء {ORD[p["n"]]}: {esc(p["title"])}">{esc(p["title"])}</h1>
<p class="po-sub">{esc(p["sub"])}</p>
<p class="po-lede">{esc(p["lede"])}</p>
<ul class="po-list">{lis}</ul>
</section>'''


def bab_opener(b, chapters, photo):
    name, sub, level, q = BABS[b]
    lis = "".join(f'<li><span>{esc(eb or "")}</span><b><a href="#{a}">{esc(t)}</a></b><i>{pgref(a)}</i></li>'
                  for eb, t, a in chapters)
    lvl = "مرجع لكل المستويات" if level == "مرجع" else f"المستوى {level}"
    img = ""
    if photo:
        img = f'<img src="{photo["src"]}" alt="">'
    credit = f'<span class="bo-credit">{esc(photo["credit"])}</span>' if photo else ""
    return f'''<section class="full bab-op" id="bab-{b}"><div class="band">{img if img else frame_svg(W=200, H=74, lattice=True, frame=False, alif_x=None)}</div><div class="band-edge"></div>{credit}
<div class="nbox bo-nbox"><span>{ar(b)}</span></div>
<p class="bo-kick"><span>الباب {ORD[b]}</span><span class="lvl">{lvl}</span></p>
<h2 data-outline="الباب {ORD[b]}: {esc(name)}">{esc(name)}</h2>
<p class="bo-sub">{esc(sub)}</p>
<p class="bo-q">{esc(q)}</p>
<ul class="bo-list"><li class="h" style="display:block;border:0">فصول الباب</li>{lis}</ul>
<div class="bo-foot"><span>{TITLE}</span><span>الجزء {ORD[BAB_PART[b]]}: {esc(PARTS[BAB_PART[b] - 1]["title"])}</span></div>
</section>'''


def appx_opener(items):
    lis = "".join(f'<li><span>ملحق {l}</span><b><a href="#{a}">{esc(t)}</a></b></li>' for l, t, a in items)
    return f'''<section class="full part-op" id="part-appx">{frame_svg(alif_x=None, frame=False)}

<p class="po-kick">الملاحق<span class="en">Appendices</span></p>
<h1 data-outline="الملاحق">الملاحق والمراجع</h1>
<p class="po-sub">أدوات يعود إليها المتدرب والمدرب</p>
<p class="po-lede">معجم تطبيقي للعبارات، ومعجم لأخطاء الترجمة الحرفية، وملاحظات على ما قد يظهر لدى المتعلمين، وسكريبتات الحلقات، ونماذج كاملة للإلقاء، وبرنامج نطق يومي، وأدوات التقييم، ثم المسرد والمصادر والكشاف.</p>
<ul class="po-list">{lis}</ul>
</section>'''


def toc(entries):
    out = ['<div class="toc">']
    for kind, k, t, a in entries:
        if kind == "part":
            out.append(f'<div class="toc-part"><span class="pn">{esc(k)}</span><a href="#{a}">{esc(t)}</a>{pgref(a)}</div>')
        elif kind == "bab":
            out.append(f'<div class="toc-bab"><span class="k">{esc(k)}</span><a href="#{a}">{esc(t)}</a><span class="lead"></span>{pgref(a)}</div>')
        else:
            out.append(f'<div class="toc-row"><span class="k">{esc(k)}</span><a href="#{a}">{esc(t)}</a><span class="lead"></span>{pgref(a)}</div>')
    out.append("</div>")
    return (f'<section class="fm-sec" style="page: fm">{sec_header("toc", "المحتويات", "فهرس المحتويات")}'
            + "".join(out) + "</section>")


def back_cover():
    return f'''<section class="full back" aria-label="الغلاف الخلفي"><div class="bk-alif"></div>
<div class="bk-t"><p class="m">{TITLE}</p><p class="s">{SUBTITLE}</p></div>
<div class="bk-q"><p>قد يملك الإنسان سنوات من الدراسة، وشهادات، وقراءة واسعة، ثم لا يظهر علمه حين يتكلم.</p>
<p>هذا الكتاب منهج تدريبي متدرج في ثلاثة عشر مستوى: من سلامة الصوت، إلى الجملة العربية الطبيعية، إلى مراعاة المقام وأدب الخطاب، إلى المجلس والمنبر والمقابلة والإعلام واللقاء الرسمي، حتى الارتجال في الموقف الذي لم يُستعد له.</p>
<p>في كل مهارة: نموذج غير ناجح، ونموذج مقبول، ونموذج ناجح، ثم تحليل، ثم تدريب، ثم محاكاة، ثم تقويم.</p></div>
<div class="bk-f">تأليف: {AUTHOR}<br>{DUA}</div>
</section>'''


# --------------------------------------------------------------------------- cross references

BAB_WORD = {ORD[n]: n for n in range(1, 15)}
CH_WORD = {ORD[n]: n for n in range(1, 13)}
XREF_RE = re.compile(r"الباب\s+(الحادي عشر|الثاني عشر|الثالث عشر|الرابع عشر|الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر)"
                     r"(?:،\s*الفصل\s+(الحادي عشر|الثاني عشر|الأول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر))?")


def linkify(soup, ch_ids):
    for s in list(soup.find_all(string=XREF_RE)):
        if s.find_parent(["a", "h1", "h2", "h3", "h4", "h5", "style", "script", "title", "head", "header"]):
            continue
        if s.find_parent(class_=["full", "toc", "ch-h"]):
            continue
        txt = str(s)
        out, last = [], 0
        for m in XREF_RE.finditer(txt):
            b = BAB_WORD[m.group(1)]
            c = CH_WORD.get(m.group(2)) if m.group(2) else None
            target = f"ch-{b}-{c}" if c and f"ch-{b}-{c}" in ch_ids else f"bab-{b}"
            out.append(esc(txt[last:m.start()]))
            out.append(f'<a class="xref" href="#{target}">{esc(m.group(0))}</a>')
            last = m.end()
        out.append(esc(txt[last:]))
        s.replace_with(frag("".join(out)))


# --------------------------------------------------------------------------- photos

def load_photos():
    import json
    meta = IMG / "photos.json"
    if not meta.exists():
        return {}
    data = json.loads(meta.read_text(encoding="utf-8"))
    out = {}
    for key, d in data.items():
        f = IMG / d["file"]
        if f.exists():
            out[key] = {"src": f.as_uri(), "credit": d.get("credit", ""), **d}
    return out


# --------------------------------------------------------------------------- assembly

def page_rules():
    css = "@page fm { @top-left { content: none; } }\n@page appx { @top-left { content: \"الملاحق والمراجع\"; font-family: \"IBM Plex Sans Arabic\"; font-size: 7.2pt; color: #6B655D; vertical-align: bottom; padding-bottom: 5.4mm; } }\n"
    for b, (name, *_rest) in BABS.items():
        css += (f'@page b{b} {{ @top-left {{ content: "الباب {ORD[b]}: {name}"; font-family: "IBM Plex Sans Arabic"; '
                f'font-size: 7.2pt; color: #6B655D; vertical-align: bottom; padding-bottom: 5.4mm; }} }}\n')
    return css


def assemble(font_css):
    photos = load_photos()
    missing = []
    entries = []
    body_parts = []
    ch_ids = set()

    # front matter texts
    fm_files = [("fm-dedication", "إهداء", "الإهداء", BOOK / "00-الإهداء.md"),
                ("fm-note", "كلمة", "كلمة المؤلف", BOOK / "00-كلمة-المؤلف.md"),
                ("fm-preface", "المقدمة", "المقدمة", BOOK / "01-المقدمة.md"),
                ("fm-intro", "مدخل", "مدخل: حين لا يظهر العلم على اللسان", BOOK / "02-مدخل.md"),
                ("fm-howto", "دليل الاستعمال", "كيف تستعمل هذا الكتاب", BOOK / "03-كيف-تستعمل-الكتاب.md")]

    parts_html = []
    for p in PARTS:
        pfold = BOOK / p["folder"]
        entries.append(("part", f"الجزء {ORD[p['n']]}", f"{p['title']}: {p['sub']}", f"part-{p['n']}"))
        part_body = [part_opener(p, None, photos.get(f"part{p['n']}"))]
        for b in p["babs"]:
            bfold = pfold / BAB_FOLDER[b]
            groups = chapter_files(bfold) if bfold.exists() else []
            chapters, ch_html = [], []
            for n, files in enumerate(groups, start=1):
                num = int(re.match(r"ف(\d+)", files[0].stem).group(1))
                anchor = f"ch-{b}-{num}"
                html, eb, t = chapter_html(b, num, files, anchor)
                ch_ids.add(anchor)
                chapters.append((eb, t, anchor))
                ch_html.append(html)
            if not groups:
                missing.append(f"bab {b}: no chapters in {bfold}")
            entries.append(("bab", f"الباب {ORD[b]}", f"{BABS[b][0]}: {BABS[b][1]}", f"bab-{b}"))
            entries += [("row", eb, t, a) for eb, t, a in chapters]
            part_body.append(bab_opener(b, chapters, photos.get(f"bab{b}")))
            intro = next(iter(sorted(bfold.glob("00-فاتحة*.md"))), None) if bfold.exists() else None
            if intro:
                part_body.append(f'<section class="bab-intro" style="page: b{b}">{bab_intro_html(b, intro)}</section>')
            else:
                missing.append(f"bab {b}: no opener file")
            part_body += ch_html
        parts_html.append("".join(part_body))

    # appendices
    appx_dir = BOOK / "الملاحق"
    appx_items, appx_html = [], []
    for letter in APPX_ORDER:
        files = sorted(appx_dir.glob(f"ملحق-{letter}-*.md")) if appx_dir.exists() else []
        if not files:
            missing.append(f"appendix {letter} missing")
            continue
        md = "\n\n".join(read_md(f) for f in files)
        m = re.search(r"^#\s+(.+)$", md, flags=re.M)
        h1 = m.group(1) if m else f"ملحق {letter}"
        md = re.sub(r"^#\s+.+\n", "", md, flags=re.M)
        eb, t = split_title(h1)
        a = f"appx-{APPX_ORDER.index(letter) + 1}"
        appx_items.append((letter, t, a))
        entries.append(("row", f"ملحق {letter}", t, a))
        appx_html.append(md_section(a, eb or f"ملحق {letter}", t, md, page="appx", extra_cls="appx"))
    back_files = [("gloss", "المسرد", "مسرد المصطلحات", BOOK / "الخواتيم" / "المسرد.md"),
                  ("biblio", "المراجع", "المصادر والمراجع", BOOK / "الخواتيم" / "المصادر-والمراجع.md"),
                  ("photos", "الصور", "مصادر الصور", None),
                  ("audit", "ضبط الجودة", "تقرير المراجعة وضبط الجودة", BOOK / "الخواتيم" / "تقرير-ضبط-الجودة.md")]
    back_html = []
    for a, eb, t, f in back_files:
        if f is None:
            rows = "".join(f"<tr><td>{esc(v.get('where', k))}</td><td>{esc(v.get('title', ''))}</td>"
                           f"<td>{esc(v.get('credit', ''))}</td><td>{esc(v.get('license', ''))}</td></tr>"
                           for k, v in photos.items())
            if not rows:
                continue
            html = (f'<section class="fm-sec appx" style="page: appx">{sec_header(a, eb, t)}<div class="sec-body">'
                    f'<p>الصور في فواتح الأجزاء والأبواب صور فوتوغرافية حقيقية لأماكن العلم والكلام، من الملك العام أو بترخيص CC0، '
                    f'عولجت لونيًّا بدرجات الياقوتي لتوافق هوية الكتاب.</p><div class="tbl"><table><thead><tr><th>الموضع</th><th>الصورة</th>'
                    f'<th>المصدر</th><th>الترخيص</th></tr></thead><tbody>{rows}</tbody></table></div></div></section>')
            back_html.append(html)
            entries.append(("row", "", t, a))
            continue
        if not f.exists():
            missing.append(f"back matter missing: {f.name}")
            continue
        md = read_md(f)
        md = re.sub(r"^#\s+.+\n", "", md, count=1, flags=re.M)
        back_html.append(md_section(a, eb, t, md, page="appx", extra_cls="appx"))
        entries.append(("row", "", t, a))

    fm_html = []
    toc_entries = []
    for a, eb, t, f in fm_files:
        if not f.exists():
            missing.append(f"front matter missing: {f.name}")
            continue
        md = read_md(f)
        md = re.sub(r"^#\s+.+\n", "", md, count=1, flags=re.M)
        if a == "fm-dedication":
            soup_d = md_soup(md)
            fm_html.append(f'<section class="fp-center dedic" id="{a}"><h2 class="dedic-h" data-outline="{t}">{t}</h2>'
                           f'{soup_d.find("div", class_="root").decode_contents()}</section>')
        else:
            fm_html.append(md_section(a, eb, t, md, page="fm"))
        toc_entries.append(("row", "", t, a))

    all_entries = toc_entries + entries[:]
    # appendices group heading inside the toc
    first_appx = next((i for i, e in enumerate(all_entries) if e[3].startswith("appx-")), None)
    if first_appx is not None:
        all_entries.insert(first_appx, ("part", "الملاحق", "الملاحق والمراجع", "part-appx"))

    body = [cover(), front_pages(), "".join(fm_html), toc(all_entries), "".join(parts_html)]
    if appx_items:
        body.append(appx_opener(appx_items))
    body += appx_html + back_html
    body.append(back_cover())

    css = (HERE / "book.css").read_text(encoding="utf-8")
    doc = (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>{TITLE}: {SUBTITLE}</title>'
           f'<style>{font_css}</style><style>{css}\n{page_rules()}</style></head><body>{"".join(body)}</body></html>')
    soup = BeautifulSoup(doc, "html.parser")
    linkify(soup, ch_ids)
    keep_wrappers(soup)
    keep_headings(soup)
    return soup, all_entries, missing


# --------------------------------------------------------------------------- markers / finalize

def add_markers(soup):
    counter = [0]

    def tok(kind):
        counter[0] += 1
        return f"Q{kind}{counter[0]:05d}Q"

    toc_tokens = {}
    for el in soup.select("[id]"):
        t = tok("A")
        el.insert(0, frag(f'<span class="pmk">{t}</span>'))
        toc_tokens[el["id"]] = t
    qa = []
    for h in soup.select("h4.lesson, h5, p.hx"):
        nxt = h.find_next_sibling()
        if nxt is None or not isinstance(nxt, Tag):
            continue
        ht = tok("H")
        h.insert(0, frag(f'<span class="pmk">{ht}</span>'))
        target = nxt if nxt.name in ("p", "ul", "ol", "div", "h5", "table") else None
        if target is None:
            continue
        nt = tok("N")
        target.insert(0, frag(f'<span class="pmk">{nt}</span>'))
        qa.append((h.get_text(" ", strip=True)[:50], ht, nt))
    return toc_tokens, qa


TOKEN_RE = re.compile(r"Q\s*([A-Z])\s*(\d{5})\s*Q")


def token_pages(pdf: Path):
    pages = {}
    reader = PdfReader(str(pdf))
    for i, page in enumerate(reader.pages, start=1):
        for m in TOKEN_RE.finditer(page.extract_text() or ""):
            pages.setdefault(f"Q{m.group(1)}{m.group(2)}Q", i)
    return pages, len(reader.pages)


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
        print(f"warning: outline has {len(flat)} items, HTML {len(titles)} headings; titles left as rendered")
        titles = None
    if titles is not None:
        if "/Outlines" in writer._root_object:
            del writer._root_object["/Outlines"]
        it = iter(titles)

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
                ref = writer.add_outline_item(next(it), page_no, parent=parent, fit=fit)
                if i + 1 < len(items) and isinstance(items[i + 1], list):
                    rebuild(items[i + 1], ref)
                    i += 2
                else:
                    i += 1
        rebuild(reader.outline)
    writer.add_metadata({
        "/Title": f"{TITLE}: {SUBTITLE}",
        "/Subject": DESC,
        "/Author": AUTHOR,
        "/Keywords": "صناعة المتكلّم العربي; الكلام بالعربية الفصيحة; الخطابة; المقابلة; آداب الكلام; الارتجال",
        "/Creator": "books/sinaat-al-mutakallim/pdf/book_build.py (Chromium)",
    })
    writer._root_object[NameObject("/Lang")] = TextStringObject("ar")
    vp = writer.create_viewer_preferences()
    vp[NameObject("/Direction")] = NameObject("/R2L")
    vp[NameObject("/DisplayDocTitle")] = BooleanObject(True)
    writer.page_mode = "/UseOutlines"
    with open(pdf_out, "wb") as f:
        writer.write(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--fast", action="store_true", help="single pass, no page numbers (layout preview)")
    args = ap.parse_args()

    font_css = B.static_instances(B.ensure_fonts())
    soup, entries, missing = assemble(font_css)
    for m in missing:
        print("MISSING:", m)
    B.check_separators(soup)
    base = str(soup)

    if args.fast:
        p = B.render(base, "book-fast")
        print("fast preview:", p, len(PdfReader(str(p)).pages), "pages")
        return

    s1 = BeautifulSoup(base, "html.parser")
    toc_tokens, qa = add_markers(s1)
    p1 = B.render(str(s1), "book-pass1")
    tpages, n1 = token_pages(p1)
    pages_by_id = {k: tpages.get(t) for k, t in toc_tokens.items()}
    lost = [k for k, v in pages_by_id.items() if v is None]
    if lost:
        print("warning: no page for", lost[:12])
    report = [f"orphan heading p{tpages[a]}: {lab}" for lab, a, b in qa
              if tpages.get(a) and tpages.get(b) and tpages[b] > tpages[a]]

    s2 = BeautifulSoup(base, "html.parser")
    B.fill_pages(s2, pages_by_id)
    p2 = B.render(str(s2), "book-pass2")
    n2 = len(PdfReader(str(p2)).pages)
    if n2 != n1:
        raise SystemExit(f"layout changed between passes: {n1} vs {n2}")
    B.check_fonts(p2)
    finalize(p2, B.outline_titles(s2), OUT)
    print(f"wrote {OUT} ({n2} pages)")
    for line in report[:200]:
        print(line)
    print(f"{len(report)} orphan headings")
    if args.review:
        B.review(OUT, [])


if __name__ == "__main__":
    main()
