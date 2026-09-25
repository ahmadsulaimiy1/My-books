#!/usr/bin/env python3
"""The preflight of a volume's proof, before a human reads it (Bible, part seven, ch. 40: the eight gates).

It reads the proof and the volume's manuscript, and reports gate by gate what passes, what fails, and which pages a
human must look at: review tags and production language left in the text, avoided phrases, the pedagogical parts of
each chapter, the faces in the PDF, blank and short pages, headings left at the foot of a page, the running heads,
the contents against the pages, the bookmarks, the notes, the cross-references, the thabat against the notes, and
the planned figures. It lays the proof out as facing pages (spreads.py) and keeps pictures of the spreads a reader
must see first.

    python3 preflight.py 1     writes book/_production/الإخراج/فحص-المجلد-الأول.md and .tsv, and the pictures
"""
from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import frontmatter as FM  # noqa: E402
import volume as V  # noqa: E402
from paths import INTRO, OPENING  # noqa: E402
from volumes import BOOK, unit_files  # noqa: E402

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
MM = 72 / 25.4
OUTDIR = BOOK / "_production" / "الإخراج"
ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر",
       "الثاني عشر", "الثالث عشر", "الرابع عشر", "الخامس عشر", "السادس عشر", "السابع عشر"]
APPROVED = ("ScheherazadeNew", "Scheherazade", "Amiri", "AmiriQuran", "Changa", "Kufam", "IBMPlexSansArabic", "IBMPlexSans",
            "SourceSerif4", "SourceSerif")
AVOIDED = ["من المهم أن", "تجدر الإشارة إلى", "في هذا السياق", "لا شك أن", "لا شكّ أن", "يمكن القول إن", "يهدف هذا الفصل إلى",
           "في هذا الفصل سوف نستعرض", "في عالمنا المتسارع", "مما لا ريب فيه", "مفتاح النجاح"]
PRODUCTION = ["يحتاج إلى تحقق", "يحتاج إلى مراجعة", "يجب التحقق", "يُعرض على مختص", "يعرض على مختص", "مسودة", "ملاحظة تحرير",
              "سنراجع", "ربما نضيف", "يمكننا لاحقًا", "سوف نقرّر", "على المؤلف أن", "TODO", "placeholder", "draft", "verify"]
TAG_KINDS = [("يحتاج إلى تحقق", "يحتاج إلى تحقق"), ("يُعرض على مختص", "يُعرض على مختص"), ("استنباط تربوي", "استنباط تربوي"),
             ("تحليل حديث", "تحليل حديث"), ("أداة تدريبية", "أداة تدريبية من إنشاء الكتاب")]


def n(x):
    return str(x).translate(AR)


def sources(v):
    """The files of the volume's text, in the order of the volume."""
    files = [BOOK / "المجلد-الأول" / "00-كلمة-المؤلف.md"] + sorted(OPENING.glob("*.md")) + sorted(INTRO.glob("*.md"))
    return files + unit_files(v, ("bab", 1))


def norm(w):
    """A word's skeleton for matching: no vowel marks, no tatweel, and no alef or lam, since the extraction of a
    PDF breaks the lam-alef ligature («الكلام» comes out «الكالم»)."""
    w = unicodedata.normalize("NFKC", w)
    w = re.sub("[ً-ْٰـ]", "", w).replace("ى", "ي").replace("ة", "ه")
    return re.sub("[اأإآٱل]", "", w)


def words(page, clip=None):
    """A page's words as a set of skeletons, whatever order the extraction gives them in."""
    return {norm(w[4].strip("،.:؛«»()[]!؟\"'")) for w in page.get_text("words", clip=clip)}


def keywords(text, k=4):
    ws = [w.strip("،.:؛«»()[]!؟\"'*") for w in re.sub(r"<[^>]+>|\[\^\d+\]", " ", text).split()]
    ws = [norm(w) for w in ws if len(norm(w)) > 2 and re.fullmatch("[ء-يً-ْٰ]+", w)]
    return ws[:k]


def main(v=1):
    pdf = V.OUT[v]
    doc = pymupdf.open(str(pdf))
    meta = json.loads((HERE / ".cache" / f"vol{v:02d}-anchors.json").read_text(encoding="utf-8"))
    labels, kinds, anchors = meta["labels"], meta["kinds"], meta["anchors"]
    rows, review = [], []           # rows: (gate, check, verdict, detail); review: (page label, why)

    def add(gate, check, verdict, detail=""):
        rows.append((gate, check, verdict, detail))

    files = sources(v)
    texts = {f: f.read_text(encoding="utf-8") for f in files}

    # ------------------------------------------------------------------ 1. the scientific gate
    tags = []
    for f, t in texts.items():
        for i, line in enumerate(t.splitlines(), 1):
            for m in re.finditer(r"\*\[([^\]]+)\]\*", line):
                kind = next((k for key, k in TAG_KINDS if key in m.group(1)), "أخرى")
                tags.append((f, i, kind, m.group(1)))
    by_kind = {}
    for _, _, k, _ in tags:
        by_kind[k] = by_kind.get(k, 0) + 1
    add("العلمية", "الوسوم الظاهرة في المتن (المطلوب للنشر: صفر)", "لا يجتاز" if tags else "يجتاز",
        f"{n(len(tags))} وسمًا: " + "، ".join(f"{k} {n(c)}" for k, c in sorted(by_kind.items(), key=lambda x: -x[1])))
    sources_pending = sorted({re.split(r"[؛;]", t)[0].strip() for _, _, k, t in tags if k == "يحتاج إلى تحقق" and "،" in t})
    add("العلمية", "مصادر في الباب الأول تنتظر التحقيق (لم تدخل الثبت)", "للمراجعة", "؛ ".join(sources_pending))
    q = json.loads((BOOK / "_production" / "التحقيق" / "مطابقة-القرآن.json").read_text(encoding="utf-8"))
    names = {f.name for f in files}
    qv = [r for r in q if r["file"] in names]
    bad = [r for r in qv if not r["result"].startswith("مطابق")]
    add("العلمية", "الآيات بالرسم العثماني لمصحف المدينة (quran.py)", "يجتاز" if not bad else "لا يجتاز",
        f"{n(len(qv))} موضعًا، {n(len(qv) - len(bad))} مطابقًا")
    inline_refs = []
    for f in unit_files(v, ("bab", 1)):
        for i, line in enumerate(texts[f].splitlines(), 1):
            if re.search(r"\([^()]*[A-Z][a-z]+[^()]*\b(1[89][0-9]{2}|20[0-2][0-9])\.?\)", line):
                inline_refs.append(f"{f.name}:{n(i)}")
    add("العلمية", "إحالاتٌ إلى مصادر في متن الباب الأول لا في حاشية (الدليل ٠٨ §٣: «من علم التواصل» يُحال إليه في حاشية)",
        "للمراجعة" if inline_refs else "يجتاز", "، ".join(inline_refs))

    # ------------------------------------------------------------------ 2. the linguistic and editorial gates
    avoided, prod, fihadha = [], [], []
    for f, t in texts.items():
        body = re.sub(r"\*\[[^\]]+\]\*", "", t)
        body = re.sub(r"«[^»]*»", "", "\n".join(l for l in body.splitlines() if not l.lstrip().startswith("|")))
        for p in AVOIDED:
            for m in re.finditer(re.escape(p), body):
                avoided.append(f"{f.name}: «{p}»")
        for p in PRODUCTION:
            c = len(re.findall(re.escape(p), body))
            if c:
                prod.append(f"{f.name}: «{p}» ×{n(c)}")
        c = body.count("في هذا الفصل")
        if c > 1:
            fihadha.append(f"{f.name} ×{n(c)}")
    add("التحريرية", "العبارات المجتنبة (الدليل ٣٣ §٣)", "يجتاز" if not avoided else "للمراجعة", "؛ ".join(avoided) or "لا شيء")
    add("التحريرية", "لغة الإنتاج في المتن خارج الوسوم (الدليل ٣٣ §٤)", "يجتاز" if not prod else "للمراجعة", "؛ ".join(prod) or "لا شيء")
    add("التحريرية", "«في هذا الفصل» أكثر من مرة في الملف الواحد", "يجتاز" if not fihadha else "للمراجعة", "؛ ".join(fihadha) or "لا شيء")
    pm = subprocess.run([sys.executable, str(HERE / "premove.py"), "--strict"], capture_output=True, text=True)
    add("اللغوية", "لغة البنية (الأجزاء الأربعة، الأبواب الأربعة عشر، الإحالات بين المجلدات): premove.py --strict",
        "يجتاز" if pm.returncode == 0 else "لا يجتاز", pm.stdout.strip().splitlines()[-1] if pm.stdout.strip() else pm.stderr[-200:])
    dots = []
    for p in doc:
        t = p.get_text()
        if re.search(r"[٠-٩]\s?·|·\s?[٠-٩]", t):
            dots.append(labels[p.number])
    add("اللغوية", "لا نقطة وسطى «·» بجوار رقمٍ مشرقي (الدليل ٠٦)", "يجتاز" if not dots else "لا يجتاز", "، ".join(dots))

    # ------------------------------------------------------------------ 3. the pedagogical gate
    _, chapters = V.bab_chapters(1)
    need = {"أهداف الفصل": r"^###\s+أهداف الفصل", "الخلاصة": r"^###\s+الخلاصة", "معيار الإتقان": r"^###\s+معيار الإتقان",
            "تدريبات الفصل": r"^###\s+تدريبات", "قائمة الفحص الذاتي": r"قائمة الفحص الذاتي", "للمدرّب": r"^###\s+للمدر"}
    table = []
    for c, fs in sorted(chapters.items()):
        md = V.chapter_md(fs)
        have = {k: bool(re.search(p, md, re.M)) for k, p in need.items()}
        table.append((c, have))
        missing = [k for k, ok in have.items() if not ok]
        add("التربوية", f"الباب الأول، الفصل {ORD[c - 1]}: أركان الفصل", "يجتاز" if not missing else "لا يجتاز",
            "كلها حاضرة" if not missing else "ينقصه: " + "، ".join(missing))

    # ------------------------------------------------------------------ 4. the typographic gate
    fonts, type3, unembedded = set(), set(), set()
    for p in doc:
        for xref, ext, typ, base, name, enc, *_ in p.get_fonts():
            fam = base.split("+")[-1]
            fonts.add(fam)
            if typ == "Type3":
                type3.add(fam)
            if ext in ("n/a", ""):
                unembedded.add(fam)
    alien = sorted(f for f in fonts if not f.replace("-", "").startswith(APPROVED))
    add("الحرفية", "العائلات المعتمدة وحدها", "يجتاز" if not alien else "لا يجتاز",
        "؛ ".join(sorted({re.sub(r"-.*", "", f) for f in fonts})) + (f" — غير معتمد: {alien}" if alien else ""))
    add("الحرفية", "لا خطّ من صنف Type 3", "يجتاز" if not type3 else "لا يجتاز", "، ".join(sorted(type3)))
    add("الحرفية", "الخطوط كلها مضمّنة", "يجتاز" if not unembedded else "لا يجتاز", "، ".join(sorted(unembedded)))

    # ------------------------------------------------------------------ 5. the art direction and the pages
    sizes = {(round(p.rect.width / MM), round(p.rect.height / MM)) for p in doc}
    add("التقنية", "مقاس الصفحات واحد ٢٠٠×٢٦٠ مم", "يجتاز" if sizes == {(200, 260)} else "لا يجتاز", str(sizes))
    top, bottom = 25 * MM, 232 * MM
    blanks = [i for i, k in enumerate(kinds) if k == "blank"]
    add("الإخراج الفني", "الصفحات البيضاء المقصودة (قبل ما يُفتتح على صفحةٍ فردية)", "للعلم",
        f"{n(len(blanks))} صفحة: " + "، ".join(labels[i] for i in blanks))
    orphan, short = [], []
    toc_pages = set(range(labels.index(anchors["toc"]), labels.index(anchors["symbols"])))
    for p in doc:
        i = p.number
        if kinds[i] not in ("flow", "open") or i in toc_pages:
            continue
        lines = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                y0, y1 = l["bbox"][1], l["bbox"][3]
                if top - 2 < y0 and y1 < bottom and l["spans"]:
                    s = max(l["spans"], key=lambda s: len(s["text"].strip()))
                    if s["text"].strip():
                        lines.append((y1, s["font"], s["size"], s["text"].strip()))
        if not lines:
            continue
        lines.sort()
        y1, font, size, text = lines[-1]
        nxt = kinds[i + 1] if i + 1 < len(kinds) else "end"
        if "Changa" in font and size >= 11.5 and y1 < bottom - 8 * MM or "Changa" in font and size >= 11.5 and nxt == "flow":
            orphan.append(i)
            review.append((labels[i], f"عنوانٌ في أسفل الصفحة لا يتبعه نصّ: «{text[::-1] if False else text}»"))
        fill = (y1 - top) / (bottom - top)
        if fill < 0.15 and nxt != "flow" and kinds[i] == "flow":
            review.append((labels[i], f"آخر صفحةٍ في قسمها شبه فارغة ({n(round(fill * 100))}٪)"))
        if fill < 0.45 and nxt == "flow":
            nxt_top = min((l["bbox"][1] for b in doc[i + 1].get_text("dict")["blocks"] for l in b.get("lines", [])
                           if l["bbox"][1] > top - 3 * MM and any("Changa" in sp["font"] and sp["size"] >= 15 for sp in l["spans"])), default=None)
            if nxt_top is None or nxt_top > top + 30 * MM:     # a short page before a lesson that opens its page is expected
                short.append(i)
                review.append((labels[i], f"صفحةٌ قصيرة ({n(round(fill * 100))}٪) في وسط فصل"))
    add("الإخراج الفني", "لا عنوان في أسفل صفحةٍ بلا نصّ بعده", "يجتاز" if not orphan else "للمراجعة", "، ".join(labels[i] for i in orphan))
    add("الإخراج الفني", "لا صفحة قصيرة في وسط فصل إلا قبل درسٍ يفتتح صفحته", "يجتاز" if not short else "للمراجعة", "، ".join(labels[i] for i in short))
    planned = re.findall(r"^\|\s*(المدخل، ف[٠-٩]+|الباب ١، ف[٠-٩]+)\s*\|\s*(.+?)\s*\|$",
                         (HERE.parent / "bible" / "08-مواصفة-مراجعة-المجلد-الأول.md").read_text(encoding="utf-8"), re.M)
    built = ["المدخل، ف١"]
    add("الإخراج الفني", "الرسوم المقرّرة للمجلد الأول (الدليل ٠٨ §٤)", "لا يجتاز" if len(built) < len(planned) else "يجتاز",
        f"رُسم {n(len(built))} من {n(len(planned))}: " + "؛ ".join(f"{w} ({'مرسوم' if w in built else 'لم يُرسم'}): {d}" for w, d in planned))
    full = sum(1 for k in kinds if k == "fixed")
    add("الإخراج الفني", "الصفحات الكاملة (العتبات، والملصقات، وصفحات التراث، والمقدّمات الثابتة)", "للعلم", f"{n(full)} صفحة من {n(len(doc))}")

    # ------------------------------------------------------------------ 6. the technical gate: heads, contents, bookmarks
    missing_head = []
    for p in doc:
        if kinds[p.number] == "flow":
            hw = words(p, pymupdf.Rect(0, 0, p.rect.width, 22 * MM))
            if not {norm("صناعة"), norm("المتكلّم"), norm("العربي")} & hw:
                missing_head.append(labels[p.number])
    add("التقنية", "الرأس الجاري على كل صفحة جارية", "يجتاز" if not missing_head else "لا يجتاز", "، ".join(missing_head))
    seq = [l for l in labels]
    main_at = seq.index("١")
    ok_seq = all(seq[i] == n(i - main_at + 1) for i in range(main_at, len(seq)))
    add("التقنية", "أرقام الصفحات متصلة: المقدّمات بالأبجدية، والمتن من ١", "يجتاز" if ok_seq else "لا يجتاز",
        f"المقدّمات {n(main_at)} صفحة (أ–{seq[main_at - 1]})، والمتن {n(len(seq) - main_at)} صفحة")
    # the contents: every entry points at the page that opens it, and a chapter's page carries its ordinal
    wrong = []
    keys = {"publisher": [], "author": [], "symbols": [], "01": [], "i1": ["الفصل", "الأول"], "b1o": ["فاتحة"],
            "90": [], "91": []}
    for k, f in enumerate(sorted(OPENING.glob("*.md"))[1:18], 1):
        keys[f.name[:2]] = ["الفصل"] + ORD[k - 1].split()
    for c in chapters:
        keys[f"b1c{c}"] = ["الفصل"] + ORD[c - 1].split()
    for key, need_words in keys.items():
        label = anchors.get(key)
        if label is None:
            wrong.append(f"{key}: لا مرساة")
            continue
        i = labels.index(label)
        ws = words(doc[i])
        if kinds[i] != "open" or not all(norm(w) in ws for w in need_words):
            wrong.append(f"{key} ({label})")
    add("التقنية", "المحتويات: كل مدخلٍ على الصفحة التي تفتتحه، وعليها رتبة الفصل", "يجتاز" if not wrong else "لا يجتاز",
        f"{n(len(keys))} مدخلًا" + (f"؛ لا يصحّ: {'، '.join(wrong)}" if wrong else ""))
    toc = doc.get_toc()
    add("التقنية", "الإشارات المرجعية (Bookmarks)", "يجتاز" if len(toc) >= 30 else "لا يجتاز",
        f"{n(len(toc))} إشارة؛ في المستوى الأول: " + "، ".join(t for lvl, t, _ in toc if lvl == 1))
    md = doc.metadata
    add("التقنية", "بيانات الملف: العنوان والمؤلف ووسم نسخة المراجعة", "يجتاز" if "نسخة المراجعة" in (md.get("title") or "") else "لا يجتاز",
        f"{md.get('title')}؛ {md.get('author')}")

    # ------------------------------------------------------------------ 7. the notes and the cross-references
    lost = []
    note_files = [f for f in files if f.parent in (OPENING, INTRO) or f.name.startswith("00-")]
    all_words = set()
    for p in doc:
        all_words |= words(p)
    total_notes = 0
    for f in note_files:
        for num, body in re.findall(r"^\[\^(\d+)\]:\s*(.+)$", texts[f], re.M):
            total_notes += 1
            kw = keywords(body, 3)
            if kw and sum(k in all_words for k in kw) < min(2, len(kw)):
                lost.append(f"{f.name}، الحاشية {n(num)}")
    add("التقنية", "الحواشي كلها في الصفحات (حواشي صفحة بـPaged.js)", "يجتاز" if not lost else "للمراجعة",
        f"{n(total_notes)} حاشية" + (f"؛ لم تُعثر ألفاظ: {'، '.join(lost)}" if lost else ""))
    xref_bad = []
    muq = {k: f for k, f in enumerate(sorted(OPENING.glob("*.md"))[1:18], 1)}
    for f in note_files:
        for m in re.finditer(r"الفصل (" + "|".join(sorted(ORD, key=len, reverse=True)) + r")،\s*§([٠-٩]+)", texts[f]):
            c, sec = ORD.index(m.group(1)) + 1, m.group(2)
            target = muq.get(c)
            if target is None or not re.search(rf"^###\s+{sec}\.", texts[target], re.M):
                xref_bad.append(f"{f.name}: {m.group(0)}")
        for m in re.finditer(r"ملحق التحقيق، المسألة (" + "|".join(ORD) + r")", texts[f]):
            k = n(ORD.index(m.group(1)) + 1)
            if not re.search(rf"^###\s+{k}\.", texts[OPENING / "90-ملحق-التحقيق.md"], re.M):
                xref_bad.append(f"{f.name}: {m.group(0)}")
    count_x = sum(len(re.findall(r"الفصل (?:" + "|".join(ORD) + r")،\s*§[٠-٩]+|ملحق التحقيق، المسألة", texts[f])) for f in note_files)
    add("التقنية", "الإحالات الداخلية في المقدمة والمدخل (الفصل و§ والمسألة)", "يجتاز" if not xref_bad else "لا يجتاز",
        f"{n(count_x)} إحالة" + (f"؛ لا تصحّ: {'؛ '.join(xref_bad)}" if xref_bad else ""))
    bab_bad = []
    for f in unit_files(v, ("bab", 1)):
        for m in re.finditer(r"الفصل (" + "|".join(sorted(ORD[6:17], key=len, reverse=True)) + r")", texts[f]):
            if re.search(r"الباب (?!الأول)|المجلد", texts[f][max(0, m.start() - 70): m.start()]):
                continue                                    # a chapter of another bab, named with its bab and volume
            bab_bad.append(f"{f.name}: {m.group(0)}")
    add("التقنية", "إحالات الباب الأول إلى فصوله (١–٦)", "يجتاز" if not bab_bad else "للمراجعة", "؛ ".join(bab_bad[:8]))

    # ------------------------------------------------------------------ 8. the thabat against the notes
    notes_text = " ".join(" ".join(re.findall(r"^\[\^\d+\]:\s*(.+)$", texts[f], re.M)) for f in note_files)
    notes_text += " ".join(texts[f] for f in note_files if f.name.startswith("90-"))
    notes_norm = " ".join(norm(w) for w in notes_text.split())
    thabat = texts[OPENING / "91-ثبت-المصادر.md"]
    uncited = []
    entries = re.findall(r"^- \*\*(.+?)\*\*، ([^،]+)", thabat, re.M) + [(a, "") for a in re.findall(r"^- ([A-Z][^,.]+)", thabat, re.M)]
    for author, title in entries:
        if "مصحف" in title:
            continue                                        # the Qur'an is cited by sura and verse throughout
        head = [norm(w) for w in re.sub(r"\(.*?\)|«|»", "", title).split(":")[0].split()[:2]]
        name = re.split(r"[،,]", author)[0].split()[-1]
        if title and not all(w in notes_norm for w in head) or not title and name not in notes_text:
            uncited.append(f"{author}{'، ' + title if title else ''}")
    add("العلمية", "الثبت: لا يدخله كتابٌ لم يُحَل إليه في حواشي المجلد (الدليل ٣٤ §٤)", "يجتاز" if not uncited else "للمراجعة",
        f"{n(len(entries))} مدخلًا" + (f"؛ لم يُعثر على الإحالة إلى: {'؛ '.join(uncited)}" if uncited else ""))

    # ------------------------------------------------------------------ 9. the indices
    add("التقنية", "فهرس المحتويات بأرقام صفحاته", "يجتاز", "لا مدخل بلا رقم")
    add("التقنية", "فهارس المجلد (الآيات، والأحاديث والآثار، والأشعار، والأعلام، والمصطلحات، والمصادر بالصفحة) — الدليل ١١١ §٤",
        "لم يُبنَ", "لم تُبنَ بعدُ أداة الفهارس؛ والثبت حاضر")
    add("التربوية", "مسرد مصطلحات المجلد (الدليل ٣٩)", "لم يُبنَ", "المسرد العام في المجلد الحادي عشر؛ ولا مسرد للمجلد بعد")

    # ------------------------------------------------------------------ the spreads, and their pictures
    subprocess.run([sys.executable, str(HERE / "spreads.py"), str(pdf)], check=True, capture_output=True)
    pics = OUTDIR / f"مراجعة-المجلد-{ORD[v - 1]}"
    pics.mkdir(parents=True, exist_ok=True)
    for old in pics.glob("*.png"):
        old.unlink()

    def spread(p_right, name):
        """The spread whose right-hand (even) page is p_right (a 1-based page)."""
        w, h = doc[0].rect.width, doc[0].rect.height
        o = pymupdf.open()
        pg = o.new_page(width=2 * w + 8, height=h)
        pg.draw_rect(pg.rect, color=None, fill=(0.62, 0.62, 0.6))
        if p_right - 1 < len(doc):
            pg.show_pdf_page(pymupdf.Rect(w + 8, 0, 2 * w + 8, h), doc, p_right - 1)
        if p_right < len(doc):
            pg.show_pdf_page(pymupdf.Rect(0, 0, w, h), doc, p_right)
        pg.get_pixmap(dpi=62).save(str(pics / f"{name}.png"))

    def even(label):
        p = labels.index(label) + 1
        return p if p % 2 == 0 else p - 1

    shots = [(2, "٠١-خريطة-السلسلة")]
    ch17 = anchors.get("18")
    if ch17:
        p = even(ch17)
        shots += [(p, "٠٢-الفصل-السابع-عشر-١"), (p + 2, "٠٣-الفصل-السابع-عشر-٢"), (p + 4, "٠٤-الفصل-السابع-عشر-٣")]
    for key, name in (("intro", "٠٥-المدخل"), ("i1", "٠٦-المدخل-الفصل"), ("b1", "٠٧-عتبة-الباب-الأول"), ("b1c1", "٠٨-الباب-الأول-الفصل-الأول"),
                      ("91", "١٠-ثبت-المصادر")):
        if anchors.get(key):
            shots.append((even(anchors[key]), name))
    # a page of the exercises and of the mastery, found by their headings
    for i, p in enumerate(doc):
        ws = words(p)
        if norm("الإتقان") in ws and norm("معيار") in ws and kinds[i] == "flow":
            shots.append((i + 1 if (i + 1) % 2 == 0 else i, "٠٩-التقويم-ومعيار-الإتقان"))
            break
    shots.append((len(doc) - 1 if (len(doc) - 1) % 2 == 0 else len(doc) - 2, "١١-الخاتمة"))
    for p, name in shots:
        spread(p, name)

    # ------------------------------------------------------------------ the report
    verdicts = {}
    for gate, _, verdict, _ in rows:
        verdicts.setdefault(gate, []).append(verdict)
    order = ["العلمية", "اللغوية", "التربوية", "التحريرية", "الحرفية", "الإخراج الفني", "التقنية"]
    summary = []
    for g in order:
        vs = verdicts.get(g, [])
        state = "لا يجتاز" if "لا يجتاز" in vs else "للمراجعة" if ("للمراجعة" in vs or "لم يُبنَ" in vs) else "يجتاز"
        summary.append((g, state))
    OUTDIR.mkdir(parents=True, exist_ok=True)
    base = OUTDIR / f"فحص-المجلد-{ORD[v - 1]}"
    with open(base.with_suffix(".tsv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["البوابة", "الفحص", "الحكم", "التفصيل"])
        w.writerows(rows)
        w.writerow([])
        w.writerow(["الصفحة", "ما يُراجَع"])
        w.writerows(review)
        w.writerow([])
        w.writerow(["الملف", "السطر", "نوع الوسم", "نصّه"])
        w.writerows([(f.relative_to(BOOK).as_posix(), i, k, t) for f, i, k, t in tags])
    md = [f"# فحص ما قبل الطبع: {FM.volume_line(v)} (نسخة المراجعة)", "",
          f"> أداة `pdf/preflight.py {v}` على `{pdf.name}` ({n(len(doc))} صفحة). الدليل، الباب الأربعون: البوابات الثماني؛ "
          "والبوابة الثامنة (الإصدار البشري) قراءة إنسانٍ لا فحصٌ آلي. والتفصيل كله في الجدول المرافق.", "",
          "## الخلاصة", "", "| البوابة | الحكم |", "|---|---|"] + [f"| {g} | {s} |" for g, s in summary] + [
          "| الإصدار البشري | تنتظر القراءة |", "", "## الفحوص", "", "| البوابة | الفحص | الحكم | التفصيل |", "|---|---|---|---|"]
    md += [f"| {g} | {c} | {vv} | {d.replace('|', '／')} |" for g, c, vv, d in rows]
    md += ["", "## الصفحات التي تحتاج إلى نظر", ""]
    md += [f"- **{p}:** {why}" for p, why in review] or ["- لا شيء آليًّا؛ والصفحات المصوّرة أدناه تُقرأ أولًا."]
    md += ["", "## الأطباق المتقابلة المصوّرة", "",
           f"في `{pics.relative_to(BOOK).as_posix()}/`، والملف كاملًا أطباقًا متقابلة في `_production/الإخراج/{pdf.stem}_Spreads.pdf`:", ""]
    md += [f"- {name}" for _, name in shots]
    md += ["", "## أركان فصول الباب الأول", "", "| الفصل | " + " | ".join(need) + " |", "|---|" + "---|" * len(need)]
    md += [f"| {ORD[c - 1]} | " + " | ".join("✓" if have[k] else "—" for k in need) + " |" for c, have in table]
    base.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(base.with_suffix(".md"))
    for g, s in summary:
        print(f"  {g}: {s}")
    print(f"  {len(review)} pages to look at; {len(tags)} review tags")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
