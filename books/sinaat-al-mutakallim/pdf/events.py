#!/usr/bin/env python3
"""The colour events of the eleven volumes: white is the norm, colour is the event (Bible, ch. 22 §7).

Each volume's few events are declared here, not improvised by the build, and every one is anchored in the manuscript:

  framework  the volume's operative model («القاعدة»…) on a very pale sapphire field, in the text's flow — at most one
             a volume;
  heritage   one verbatim classical sentence whose row in the quotation ledger reads «متحقّق», on a restrained warm
             pearl field in the flow — never the Quran or a hadith, never an unestablished attribution;
  hinge      a chapter opening that the bab itself declares a turn: a movement of its «هذا الباب يعطيك ثلاثة أشياء»
             (the bullet is set on the plate, verbatim) or the chapter the manuscript names as the bab's close; very
             pale sapphire, or graphite where reading turns into a workbook — at most two a volume;
  statement  a unit's governing sentence, re-staged verbatim on a midnight field, on its own page (V1, V10 only).

Doors (a sapphire field for every bab, graphite for the reference) are structural and built by volume.py; they are
not events. The Quran is never on a field.

    python3 pdf/events.py      checks every anchor against the sources and the ledger (the build runs it too)
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
LEDGER = BOOK / "_production" / "التحقيق" / "سجل-النقول.tsv"
MAX_FIELD = 1600          # characters of source: longer than this a field would not fit one page; it is refused

# (kind, volume folder, file relative to it, heading line (a section) or a phrase (its paragraph), extra)
FIELDS = {
    1: [("framework", "الباب-الأول/ف01-ب-الدرس-الثاني.md", "### القاعدة: النموذج السداسي", None),
        ("heritage", "الافتتاحية/05-البيان-عند-علماء-العربية.md", "«فمنه مستقيمٌ حسن، ومُحال", "م١-٠٤٥")],
    2: [("framework", "الباب-الثاني/00-فاتحة-الباب-الثاني.md", "### معيار النطق في هذا الباب", None)],
    3: [("heritage", "الباب-الثالث/ف01-أ-الاسمية-والفعلية.md", "قال سيبويه في حديثه عن تقديم المفعول على الفاعل", "م٣-٠٢٣"),
        ("framework", "الباب-الثالث/ف02-ب-الإعراب-والنواسخ.md", "### الطبقات الثلاث", "with-table")],
    4: [("framework", "الباب-الرابع/ف01-أ-المدخل-والدرس-الأول.md", "### القاعدة", None)],
    6: [("heritage", "الباب-السادس/ف01-السلام-والبشاشة-والاستماع.md", "قال ابن المقفع في «الأدب الكبير»", "م٦-٠٠١")],
    7: [("framework", "الباب-السابع/ف02-أ-الجواب-المدخل-والدرس-الأول.md", "### القاعدة", None)],
    9: [("framework", "الباب-العاشر/ف01-أ-بناء-الجواب.md", "### القاعدة: الجواب الرباعي", None)],
    10: [("heritage", "الباب-الحادي-عشر/ف01-أ-المدخل-والدرس-الأول.md", "جعل الجاحظ الصوت أصلًا يقوم عليه الكلام كله", "م١٠-٠٠١")],
}

# hinges: (volume, bab or "program", chapter) -> (plate, the فاتحة's bullet label or "close")
HINGES = {
    (2, 2, 10): ("ice", "صوتًا يحمل المعنى"),
    (2, "program", 0): ("graphite", None),
    (3, 3, 5): ("ice", "طبيعية"),
    (3, 3, 8): ("ice", "اختيارًا"),
    (4, 4, 3): ("ice", "مواضع"),
    (4, 4, 7): ("ice", "أدوات"),
    (5, 5, 5): ("ice", "اتجاهات للخطاب"),
    (5, 5, 9): ("graphite", "مختبرًا"),
    (6, 6, 9): ("ice", "close"),
    (7, 7, 7): ("ice", "close"),
}

# statements: volume -> [(where, kicker (a heading, verbatim), the lead-in, the sentence, file)]
STATEMENTS = {
    1: [("10-", "١٧. ومن هنا وُلد الكتاب", "ومن هنا لم يعد السؤال عندي: كيف نعلّم الطالب مزيدًا من العربية؟",
         "بل صار: كيف نجعل العربية التي تعلّمها تظهر على لسانه حين يحتاج إليها، ثم يُحسن وضعها في موضعها؟",
         "المجلد-الأول/الافتتاحية/09-ما-رأيته.md")],
    10: [("closing", "كلمة أخيرة إلى القارئ", "", "فتكلم الآن. المقام ينتظرك.",
          "المجلد-العاشر/الباب-الثالث-عشر/ف03-ج-التطبيق-والتقويم-والخاتمة.md")],
}

ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي-عشر"]
START, END = "⟪fld:{}⟫", "⟪/fld⟫"


def vol_dir(n):
    return BOOK / f"المجلد-{ORD[n - 1]}"


def _block(lines, i, heading, table=False):
    """The line range of the event: a section to the next heading of any level, figure or table (its core — the rules
    themselves — before its sub-steps and reference tables), or one paragraph."""
    if heading:
        j = i + 1
        stop = r"^#{1,6}\s|^<!--\s*figure:" + ("" if table else r"|^\|")    # a figure or a table keeps its own frame,
        while j < len(lines) and not re.match(stop, lines[j]):                 # unless the table is the model itself
            j += 1
        return i, j
    j = i
    while j < len(lines) and lines[j].strip():
        j += 1
    return i, j


def _find(lines, anchor):
    heading = anchor.startswith("#")
    hits = [k for k, l in enumerate(lines) if (l.strip() == anchor if heading else anchor in l)]
    return hits, heading


def stage(path: Path, text: str, n: int) -> str:
    """Put the sentinels round a declared event of this file (the layout wraps what lies between them)."""
    for kind, rel, anchor, _ in FIELDS.get(n, []):
        if Path(path).resolve() != (vol_dir(n) / rel).resolve():
            continue
        lines = text.split("\n")
        hits, heading = _find(lines, anchor)
        if len(hits) != 1:
            raise SystemExit(f"events: «{anchor}» found {len(hits)} times in {rel}")
        i, j = _block(lines, hits[0], heading, _ == "with-table")
        tag = "ice" if kind == "framework" else "warm"
        lines = lines[:i] + [START.format(tag), ""] + lines[i:j] + ["", END, ""] + lines[j:]
        text = "\n".join(lines)
    return text


def wrap(soup):
    """The layout's half: every pair of sentinel paragraphs becomes a field round what lies between them."""
    for p in list(soup.find_all("p")):
        t = p.get_text(strip=True)
        m = re.fullmatch(r"⟪fld:(\w+)⟫", t)
        if not m or p.parent is None:
            continue
        field = soup.new_tag("div", attrs={"class": f"fld {m.group(1)}"})
        node = p.next_sibling
        p.replace_with(field)
        while node is not None:
            nxt = node.next_sibling
            if getattr(node, "name", None) == "p" and node.get_text(strip=True) == END:
                node.extract()
                break
            field.append(node.extract())
            node = nxt
    for p in list(soup.find_all("p")):           # a stray sentinel (its pair in another block) never prints
        if re.fullmatch(r"⟪/?fld(:\w+)?⟫", p.get_text(strip=True)):
            p.decompose()
    return soup


def hinge(n, bab, chapter):
    """The plate of a chapter opening, and the verbatim line it carries: (plate, line) or (None, None)."""
    h = HINGES.get((n, bab, chapter))
    if not h:
        return None, None
    plate, label = h
    if label in (None, "close"):
        return plate, label
    return plate, bullet(n, bab, label)


def bullet(n, bab, label):
    """The opener's own bullet for a movement («- **طبيعية:** …»), verbatim."""
    for f in sorted(vol_dir(n).glob("الباب-*/00-فاتحة-*.md")):
        for line in f.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^- \*\*(.+?):\*\*\s*(.+)$", line)
            if m and m.group(1) == label:
                return f"<b>{m.group(1)}:</b> {m.group(2)}"
    raise SystemExit(f"events: no bullet «{label}» in the opener of volume {n}")


def statements(n, where):
    return [s for s in STATEMENTS.get(n, []) if s[0] == where]


def check(verbose=False):
    ledger = {r["الرقم"]: r for r in csv.DictReader(open(LEDGER, encoding="utf-8"), delimiter="\t")}
    problems, count = [], 0
    for n, evs in FIELDS.items():
        kinds = [e[0] for e in evs]
        if kinds.count("framework") > 1 or kinds.count("heritage") > 1:
            problems.append(f"volume {n}: more than one framework or heritage field")
        for kind, rel, anchor, lid in evs:
            f = vol_dir(n) / rel
            if not f.exists():
                problems.append(f"volume {n}: no file {rel}")
                continue
            lines = f.read_text(encoding="utf-8").split("\n")
            hits, heading = _find(lines, anchor)
            if len(hits) != 1:
                problems.append(f"volume {n}: «{anchor}» found {len(hits)} times in {rel}")
                continue
            i, j = _block(lines, hits[0], heading, lid == "with-table")
            block = "\n".join(lines[i:j])
            if heading and len([l for l in block.strip().splitlines() if l.strip()]) < 2:
                problems.append(f"volume {n}: the {kind} field at «{anchor}» would hold nothing but its heading")
            if "﴿" in block:
                problems.append(f"volume {n}: the {kind} field at «{anchor}» holds the Quran; the Quran is never on a field")
            if kind == "heritage" and re.search(r"ﷺ|صلى الله عليه وسلم|رسول الله", block):
                problems.append(f"volume {n}: the heritage field at «{anchor}» holds a hadith; a heritage field is one scholar's sentence")
            if len(block) > MAX_FIELD:
                problems.append(f"volume {n}: the {kind} field at «{anchor}» is {len(block)} characters, longer than a page")
            if kind == "heritage":
                row = ledger.get(lid)
                if not row or not row["الحالة"].startswith("متحقّق"):
                    problems.append(f"volume {n}: heritage «{anchor}»: ledger {lid} is not «متحقّق»")
                elif row["الصيغة"].strip() != "نص":
                    problems.append(f"volume {n}: heritage «{anchor}»: ledger {lid} is not a verbatim text")
            count += 1
    for (n, bab, c), (plate, label) in HINGES.items():
        if label and label != "close":
            bullet(n, bab, label)
        if label == "close":
            files = [f for f in vol_dir(n).glob(f"الباب-*/ف{c:02d}-*.md")]
            if not any("خاتمة الباب" in f.read_text(encoding="utf-8") for f in files):
                problems.append(f"volume {n}: chapter {c} is not declared the bab's close")
        count += 1
    for n, sts in STATEMENTS.items():
        for where, kick, pre, main, rel in sts:
            src = (BOOK / rel).read_text(encoding="utf-8")
            for piece in (kick, pre, main):
                if piece and piece not in src:
                    problems.append(f"volume {n}: statement text not verbatim in {rel}: «{piece}»")
            count += 1
    if verbose:
        print(f"{count} events checked; {len(problems)} problems")
    return problems


if __name__ == "__main__":
    ps = check(verbose=True)
    for p in ps:
        print("PROBLEM:", p)
    sys.exit(1 if ps else 0)
