#!/usr/bin/env python3
"""The audit before the move (Bible, ch. 112d §٥): the four checks on the transition table, and a scan of every file
for the names of the old structure (four parts, fourteen abwab, eight volumes, levels 0–12, example codes that carry
the part), each occurrence classed — correct / keep as history / delete / needs a human reader.

Nothing is changed. The same scan is the gate after the move: with --strict it fails while any printed file still
has an occurrence to correct or to read.

    python3 premove.py [--strict]
        writes book/_production/هندسة-السلسلة/{فحص-ما-قبل-النقل.md, فحص-ما-قبل-النقل.tsv}
"""
import re
import sys
from collections import Counter, defaultdict

from gate import BOOK, HERE, OUT
from series import DIRS, HEADER, ORD, VOLUMES, plan

ROOT = HERE.parent
ORD_NUM = {o: i for i, o in enumerate(ORD, 1)}               # «الأول» … «الرابع عشر» → 1 … 14
ORD_RE = "|".join(sorted(ORD, key=len, reverse=True))
AR_DIG = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
PART_OF = {b: (1 if b <= 3 else 2 if b <= 6 else 3 if b <= 10 else 4) for b in range(1, 15)}

CORRECT, KEEP, DELETE, HUMAN = "يُصحّح", "يُحفظ", "يُحذف", "مراجعة بشرية"
GENERIC = "استعمالٌ لغويٌّ عام، لا بنية الكتاب"
STAGES = r"(التأسيس|التواصل|المنصات|المنصّات|التمكين)"


def num(s):
    return int(s.translate(AR_DIG))


def is_note(line):
    return line.lstrip().startswith("[^")


def new_bab(old):
    """The series number of a present bab: 14 becomes 13, 13 leaves for the reference (None)."""
    return {13: None, 14: 13}.get(old, old)


def rules(rel, line, vol, bab_of_file, vol_of_bab):
    """Yield (rule, match text, class, action) for one line of one file."""
    ctx = line
    for m in re.finditer(r"\[م([٠-٩]+)-ب([٠-٩]+)-ف([٠-٩]+)-مث([٠-٩]+)\]", line):
        p, b, c, n = (num(x) for x in m.groups())
        nb = new_bab(b)
        printed = f"[ر١-ف{m.group(3)}-مث{m.group(4)}]" if nb is None else f"[ب{str(nb).translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))}-ف{m.group(3)}-مث{m.group(4)}]"
        if PART_OF.get(b) != p:
            yield "رمز المثال", m.group(0), HUMAN, f"رقم الجزء {p} لا يوافق الباب {b}"
        elif bab_of_file and b != bab_of_file:
            yield "رمز المثال", m.group(0), HUMAN, f"رمزٌ من الباب {b} في ملفٍّ من الباب {bab_of_file}: إحالة أم خطأ نسخ؟"
        else:
            yield "رمز المثال", m.group(0), KEEP, f"معرّفٌ إنتاجيٌّ في المصدر؛ ويُطبع {printed} (يُحوَّل عند الإخراج)"
    for m in re.finditer(r"الباب الرابع عشر", line):
        yield "الباب ١٤", m.group(0), CORRECT, "الباب الثالث عشر"
    for m in re.finditer(r"الباب الثالث عشر", line):
        # in the present manuscript the thirteenth bab is the error bank; only inside the Malaka (present 14) may a
        # writer have used the new number already
        if bab_of_file == 14 and "الأخطاء" not in line[max(0, m.start() - 120): m.end() + 120]:
            yield "الباب ١٣", m.group(0), HUMAN, "في باب الملكة: أهو بنك الأخطاء أم الملكة بترقيمها الجديد؟"
        else:
            yield "الباب ١٣ (بنك الأخطاء)", m.group(0), CORRECT, "المرجع الأول: بنك الأخطاء (في المجلد الحادي عشر)"
    for m in re.finditer(r"الأبواب الأربعة عشر|أربعة عشر بابًا|الأبواب الأربعة عشرة", line):
        yield "أربعة عشر بابًا", m.group(0), CORRECT, "ثلاثة عشر بابًا، والمرجع خارجها"
    for m in re.finditer(r"ثمانية مجلدات|المجلدات الثمانية|المجلد الثامن|\(من ثمانية\)|من ثمانية\)|الثمانية", line):
        yield "الثمانية", m.group(0), CORRECT, "الأحد عشر"
    # «الجزء» is both the old part of the book and an ordinary word (the first part of a sentence, of a meeting, of a
    # formula); a pattern cannot tell them apart, so every case that is not certain goes to a human reader, with a
    # proposed reading
    def part_case(rule, m):
        before, after = line[max(0, m.start() - 25): m.start()], line[m.end(): m.end() + 40]
        if is_note(line) or re.match(r"\s*من\s*[«(]", after):
            return KEEP, "في حاشية أو إحالة: جزءٌ من مصدرٍ مطبوع"
        if "الدليل" in before or re.match(r"\s*[٠-٩\d–-]*\s*من الدليل", after):
            return KEEP, "جزءٌ من الدليل، لا الكتاب"
        if re.match(rf"\s*[:،]?\s*{STAGES}", after) or re.match(r"\s*(من أربعة|من الكتاب|من هذا الكتاب)", after) \
                or m.group(0) == "أجزاء الكتاب":
            return CORRECT, "المرحلة أو المجلد بحسب السياق"
        structural = re.search(r"(تعلّمت|تعلمت|درست|عرفت|سبق|مرّ بك|مر بك|في هذا الكتاب)\s*(في)?\s*$", before)
        return HUMAN, "قراءة مقترحة: " + ("إحالةٌ إلى جزءٍ من الكتاب القديم؛ يُصحّح" if structural else GENERIC + "؛ يُحفظ")
    for m in re.finditer(r"أربعة أجزاء|الأجزاء الأربعة|أجزاء الكتاب|الأجزاء التالية|الأجزاء", line):
        yield ("الأجزاء", m.group(0), *part_case("الأجزاء", m))
    for m in re.finditer(rf"الجزء ({ORD_RE})", line):
        yield ("الجزء ن", m.group(0), *part_case("الجزء ن", m))
    for m in re.finditer(r"هذا الجزء", line):
        yield ("هذا الجزء", m.group(0), *part_case("هذا الجزء", m))
    for m in re.finditer(r"المستويات ([٠-٩]+)\s*[–-]\s*([٠-٩]+)", line):
        yield "المستويات ن–م", m.group(0), CORRECT, f"المستويات {num(m.group(1)) + 1}–{num(m.group(2)) + 1}"
    for m in re.finditer(r"المستوى ([٠-٩]+)|المستوى صفر", line):
        if rel.startswith("المدخل/"):
            yield "المستوى ن", m.group(0), HUMAN, "في المدخل: مستويات العربية أم مستوى البرنامج؟"
        else:
            old = 0 if m.group(0).endswith("صفر") else num(m.group(1))
            yield "المستوى ن", m.group(0), CORRECT, f"المستوى {old + 1}"
    for m in re.finditer(r"م([٠-٩]+)\s*[–-]\s*م([٠-٩]+)|\bم٠\b", line):
        yield "مN–مN", m.group(0), CORRECT, "المستويات ١–١٣"
    for m in re.finditer(rf"(مخرجات?|نهاية|أهداف) المستوى ({ORD_RE})", line):
        yield "المستوى بالعدد اللفظي", m.group(0), CORRECT, f"المستوى {ORD[ORD_NUM[m.group(2)]]} (+١)"
    for m in re.finditer(rf"(?<!مخرج )(?<!مخرجات )(?<!نهاية )(?<!أهداف )المستوى ({ORD_RE})(?! من)", line):
        if re.search(r"طلاب\s*$", line[max(0, m.start() - 8): m.start()]):
            yield "المستوى بالعدد اللفظي", m.group(0), KEEP, "صفٌّ دراسيٌّ في مثال، لا مستوى البرنامج"
        else:
            yield "المستوى بالعدد اللفظي", m.group(0), CORRECT, f"المستوى {ORD[ORD_NUM[m.group(1)]]} (+١)"
    for m in re.finditer(r"\b(Part|Volume|Vol\.)\s*[\dIVX]+|\b\d+\s+volumes\b|\bparts?\b", line, re.I):
        if is_note(line) or "ثبت" in rel or "الترجمة-الحرفية" in rel:
            yield "إنجليزية", m.group(0), KEEP, "عنوان مصدرٍ أو عبارةٌ إنجليزية مدروسة، لا بنية الكتاب"
        else:
            yield "إنجليزية", m.group(0), HUMAN, ""
    # references to a bab: renumbered (13, 14), or in another volume (the volume is added: Bible, ch. 111 §٢)
    for m in re.finditer(rf"(انظر|راجع|في|إلى|من)\s+الباب ({ORD_RE})(?:،\s*الفصل ({ORD_RE}))?", line):
        b = ORD_NUM[m.group(2)]
        if b >= 13:
            continue                                     # renumbering is counted above
        ch = ORD_NUM.get(m.group(3) or "", 0)
        if ch and ch > n_chapters(b):
            yield "إحالة", m.group(0), HUMAN, f"مكسورة: الباب {b} فيه {n_chapters(b)} فصول"
        elif vol and vol_of_bab.get(b) and vol_of_bab[b] != vol:
            yield "إحالة", m.group(0), CORRECT, f"يُزاد المجلد: «في المجلد {vol_of_bab[b]}، …»"
    for m in re.finditer(r"\]\(([^)]+\.md)(#[^)]*)?\)", line):
        if LINK_BASE is None:
            continue
        target = (LINK_BASE / m.group(1)).resolve()
        if not target.exists():
            yield "رابط ملف", m.group(1), HUMAN, "مكسور الآن"
        elif BOOK in target.parents and "_production" not in target.parts and target.name != "README.md":
            yield "رابط ملف", m.group(1), CORRECT, "يشير إلى ملفٍّ سيتغيّر موضعه؛ يُحدَّث من جدول الانتقال"


_CH = {}
LINK_BASE = None   # the folder of the file being scanned, for relative links


def n_chapters(b):
    if b not in _CH:
        d = next(BOOK.glob("الجزء-*/الباب-" + DIRS[b - 1]))
        _CH[b] = len({f.name[1:3] for f in d.glob("ف*.md")})
    return _CH[b]


def main(strict=False):
    global LINK_BASE
    rows, _ = plan()
    vol_of = {r[0]: r[1] for r in rows}
    dest_of = {r[0]: r[2] for r in rows}
    vol_of_bab = {}
    for i, v in enumerate(VOLUMES, 1):
        for u in v["units"]:
            if u[0] == "bab":
                vol_of_bab[u[1]] = str(i)

    # --- the four checks on the table -------------------------------------------------------------------------------
    printed = [r for r in rows if r[1] not in ("—", "؟")]
    checks = {
        "A. كل ملفٍّ مطبوعٍ في مجلدٍ واحد": len(printed) == len({r[0] for r in printed}),
        "B. لا ملفّ في موضعين، ولا موضع لملفّين": len(rows) == len({r[0] for r in rows}) == len({r[5] for r in rows}),
        "C. لكل ملفٍّ قديمٍ وجهة (لا «؟»)": all(r[1] != "؟" and r[2] for r in rows),
    }

    # --- the scan ------------------------------------------------------------------------------------------------------
    hits = []
    for r in rows:
        rel = r[0]
        f = BOOK / rel
        m = re.search(r"الباب-(" + "|".join(sorted(DIRS, key=len, reverse=True)) + r")/", rel)
        bab = DIRS.index(m.group(1)) + 1 if m else None
        vol = r[1] if r[1] not in ("—", "؟") else None
        LINK_BASE = f.parent
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for rule, text, cls, act in rules(rel, line, vol, bab, vol_of_bab):
                if vol is None and cls != KEEP:
                    kind = r[2]
                    cls, act = (KEEP, f"الملف {kind}؛ لا يُطبع") if kind in ("أرشيف", "ملفات الإنتاج") or "الإنتاج" in kind else (cls, act + f" ({kind})")
                hits.append(["book/" + rel, str(n), r[1], rule, text, cls, act])
    # the printed front matter, written in the build tools
    LINK_BASE = None
    for tool in ("frontmatter.py", "opening.py"):
        for n, line in enumerate((HERE / tool).read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("#"):
                continue
            for rule, text, cls, act in rules("", line, "1", None, {}):
                if rule in ("الثمانية", "أربعة عشر بابًا", "الأجزاء", "الجزء ن", "الباب ١٤", "المستوى ن"):
                    hits.append([f"pdf/{tool}", str(n), "مقدّمات", rule, text, cls, act])
    # the project's working documents: not printed, but they describe the structure
    for doc in ["00-الوثيقة-الحاكمة.md", "01-الرؤية-والفلسفة.md", "02-خريطة-الكتاب.md", "03-المستويات-والمخرجات.md",
                "04-نظام-التقييم.md", "README.md", "book/README.md"]:
        p = ROOT / doc
        if not p.exists():
            continue
        LINK_BASE = p.parent
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            for rule, text, cls, act in rules("", line, None, None, {}):
                if rule in ("رمز المثال", "إحالة"):
                    continue
                hits.append([doc, str(n), "وثيقة المشروع", rule, text, cls, act + " (وثيقة عمل، تُحدَّث مع النقل)"])

    # the tools that read the present paths, and what points at a file that moves
    tools = []
    for p in sorted(HERE.glob("*.py")):
        if p.name in ("premove.py", "build.py"):          # build.py builds the Bible, not the book
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r'"الجزء-|الجزء-\*|"الافتتاحية"|"الملاحق"|"الخواتيم"|"المدخل"|"الباب-|الباب-"|BOOK / "0[0-3]-|'
                         r'م[١-٤] (التأسيس|التواصل|المنصات|التمكين)|title="(التأسيس|التواصل|المنصات|التمكين)"', line):
                tools.append((p.name, n, line.strip()[:110]))
    moved = {r[0] for r in rows}
    pointers = []
    for p in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.py")):
        # the records of the decision and the plan itself name these files on purpose
        if ".cache" in p.parts or p.name in ("series.py", "premove.py", "الفهرس-العام.md", "حسم-الملفات-الثمانية.md") \
                or p.name.startswith("فحص-ما-قبل") or p.name.startswith("15-هندسة-السلسلة"):
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        for rel in ("00-التكليف-الرسمي.md", "01-المقدمة.md", "02-مدخل.md", "03-كيف-تستعمل-الكتاب.md", "00-الواجهة.md", "00-الإهداء.md"):
            if rel in t and p.name != rel and rel in moved:
                pointers.append((str(p.relative_to(ROOT)), rel))

    # --- the report ----------------------------------------------------------------------------------------------------
    by = Counter((h[3], h[5]) for h in hits)
    printed_hits = [h for h in hits if h[2] not in ("—", "؟", "وثيقة المشروع")]
    open_printed = [h for h in printed_hits if h[5] in (CORRECT, HUMAN)]
    checks["D. لا نصّ مطبوعًا يفترض البنية القديمة إلا سجلًّا تاريخيًّا"] = not open_printed

    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "فحص-ما-قبل-النقل.tsv", "w", encoding="utf-8") as fh:
        fh.write("\t".join(["الملف", "السطر", "المجلد", "القاعدة", "النص", "التصنيف", "الإجراء"]) + "\n")
        for h in hits:
            fh.write("\t".join(x.replace("\t", " ") for x in h) + "\n")

    L = ["# فحص ما قبل النقل", "",
         "من `python3 pdf/premove.py` (الدليل، الباب ١١٢د §٥). لم يُغيَّر به شيء. والفحص نفسه بوابة ما بعد النقل: "
         "`--strict` يفشل ما بقي في نصٍّ مطبوعٍ موضعٌ «يُصحّح» أو «مراجعة بشرية».", "",
         "## الفحوص الأربعة", "", "| الفحص | قبل النقل |", "|---|---|"]
    L += [f"| {k} | {'نعم' if v else 'لا'} |" for k, v in checks.items()]
    L += ["", f"وفحص D لا يصحّ قبل النقل بطبيعته: هو ما يصحّحه النقل. وفي النصوص المطبوعة الآن **{len(open_printed)}** موضعًا مفتوحًا "
          "(«يُصحّح» أو «مراجعة بشرية»)، تفصيلها أدناه وفي `فحص-ما-قبل-النقل.tsv`.", "",
          "## أسماء البنية القديمة: العدّ", "",
          "| القاعدة | " + " | ".join([CORRECT, KEEP, DELETE, HUMAN]) + " |", "|---|---|---|---|---|"]
    for rule in dict.fromkeys(h[3] for h in hits):
        L.append(f"| {rule} | " + " | ".join(str(by.get((rule, c), 0)) for c in (CORRECT, KEEP, DELETE, HUMAN)) + " |")
    L += ["", "## ما يحتاج قارئًا بشريًّا (في الملفات المطبوعة والمرافقة)", ""]
    human = [h for h in hits if h[5] == HUMAN and h[2] != "وثيقة المشروع"]
    grouped = defaultdict(list)
    for h in human:
        grouped[h[3]].append(h)
    for rule, hs in grouped.items():
        L += [f"### {rule} ({len(hs)})", "", "| الملف:السطر | النص | السؤال |", "|---|---|---|"]
        L += [f"| `{h[0].replace('book/', '')}:{h[1]}` | {h[4]} | {h[6]} |" for h in hs]
        L.append("")
    generic = [h for h in hits if h[5] == KEEP and h[2] not in ("—", "وثيقة المشروع")]
    L += ["## ما صُنّف «يُحفظ» في الملفات المطبوعة", "",
          "قُرئ كل موضعٍ منها في سياقه قبل أن تُكتب قاعدته؛ وهي هنا ليتحقّق المؤلف منها.", "",
          "| الملف:السطر | النص | السبب |", "|---|---|---|"]
    L += [f"| `{h[0].replace('book/', '')}:{h[1]}` | {h[4]} | {h[6]} |" for h in generic]
    L.append("")
    L += ["## أدوات البناء التي تقرأ المسارات الحالية", "",
          "تُحدَّث في النقل نفسه، وإلا انكسر البناء:", "", "| الأداة:السطر | السطر |", "|---|---|"]
    L += [f"| `{a}:{b}` | `{c.replace('|', '¦')}` |" for a, b, c in tools]
    L += ["", "## ما يشير إلى ملفٍّ سيتغيّر موضعه", "", "| الملف | يشير إلى |", "|---|---|"]
    L += [f"| `{a}` | `{b}` |" for a, b in sorted(set(pointers))]
    (OUT / "فحص-ما-قبل-النقل.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    print({k: v for k, v in checks.items()})
    print("hits:", len(hits), "open in printed files:", len(open_printed))
    for (rule, cls), n in sorted(by.items()):
        print(f"  {rule} · {cls}: {n}")
    if strict and open_printed:
        raise SystemExit(f"{len(open_printed)} occurrences of the old structure remain in printed files")


if __name__ == "__main__":
    main("--strict" in sys.argv)
