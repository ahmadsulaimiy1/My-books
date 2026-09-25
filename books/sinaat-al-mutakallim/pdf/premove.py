#!/usr/bin/env python3
"""The gate of the fixed structure (Bible, ch. 112d §٦–§٧): run after the move, and after any later change to it.

It checks the manuscript as it now stands against the authoritative map (volumes.py) and the frozen transition
table, and scans every printed and companion file for what the old structure left behind. Each finding is a failure,
or — where a pattern alone cannot judge — an occurrence listed for a human reader with the reading applied.

    python3 premove.py [--strict]
        writes book/_production/هندسة-السلسلة/{فحص-ما-بعد-النقل.md, فحص-ما-بعد-النقل.tsv}
        --strict: exit with an error while any check fails

(The audit that ran before the move is archived with the old tools; its report is فحص-ما-قبل-النقل.)
"""
import csv
import re
import sys
from pathlib import Path

import frontmatter as FM
import ids
from paths import OPENING
from volumes import BOOK, ORD, VOL_OF_BAB, VOLUMES, bab_dir, unit_files

HERE = Path(__file__).resolve().parent
OUT = BOOK / "_production" / "هندسة-السلسلة"
ARCHIVE = BOOK / "_production" / "الأرشيف" / "البنية-القديمة"
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
ORD_RE = "|".join(sorted(ORD, key=len, reverse=True))
VOLW = ORD[:10] + ["الحادي عشر"]
LETTER = r"(?![ء-ي])"
# the classical usage in the opening (Bible, ch. 112d): «الباب» there is a class of argument, not a bab of the series
NOT_A_REFERENCE = ["فهي من الباب الثاني لا من الباب الأول"]
# occurrences a human reader has judged, with the reading (the post-move semantic review)
REVIEWED = {"الباب الثالث عشر (الملكة، المجلد العاشر)، وبنك الأخطاء": "الملكة، ثم بنك الأخطاء: إحالتان صحيحتان"}


def num(s):
    return int(s.translate(EN))


def files_of_series():
    """(path, volume) for every file the map places, and the companions (volume None)."""
    out = []
    for v in VOLUMES:
        for u in v["units"]:
            out += [(f, v["n"]) for f in unit_files(v["n"], u)]
    out.append((BOOK / "المجلد-الأول" / "00-كلمة-المؤلف.md", 1))
    out += [(f, None) for f in sorted((BOOK / "_المرافقة").rglob("*.md"))]
    return out


def chapters_in(b):
    return len({f.name[1:3] for f in bab_dir(b).glob("ف*.md")})


def scan(path, vol, text, bab_of_file):
    """Yield (check, text, verdict, note). verdict: fail · read (a human reads it; the reading is given)."""
    in_bank = "المرجع-الأول-بنك-الأخطاء" in str(path)
    for m in re.finditer(r"باب الرابع عشر", text):
        yield "الباب ١٤", m.group(0), "fail", "لا باب رابع عشر في البنية"
    for m in re.finditer(r"الباب الثالث عشر", text):
        near = text[max(0, m.start() - 60): m.end() + 60]
        if in_bank:
            yield "الباب ١٣", m.group(0), "fail", "بنك الأخطاء مرجعٌ لا باب"
        elif "بنك الأخطاء" in near and not any(k in text[max(0, m.start() - 5): m.end() + 60] for k in REVIEWED):
            yield "الباب ١٣", m.group(0), "read", "بجواره «بنك»: الملكة لا بنك الأخطاء؟"
    for m in re.finditer(r"ثمانية مجلدات|المجلدات الثمانية|\(من ثمانية\)|الأبواب الأربعة عشر|أربعة عشر بابًا|أجزاء الكتاب|كل جزءٍ? من (هذا )?الكتاب", text):
        yield "البنية القديمة", m.group(0), "fail", "أثرٌ للأجزاء الأربعة أو الأبواب الأربعة عشر أو الثمانية"
    # «أربعة أجزاء» is also an ordinary count (a formula in four parts): only the book's parts are the old structure
    for m in re.finditer(r"أربعة أجزاء|الأجزاء الأربعة", text):
        if re.search(r"الكتاب|السلسلة|التأسيس|التواصل|المنصات|المنصّات|التمكين|الجزء الأول", text[max(0, m.start() - 60): m.end() + 60]):
            yield "البنية القديمة", m.group(0), "fail", "الأجزاء الأربعة للكتاب"
    for m in re.finditer(r"المجلد الثامن", text):
        if re.search(r"المرجع|بنك الأخطاء|الفهارس العامة", text[max(0, m.start() - 50): m.end() + 50]):
            yield "المجلد الثامن", m.group(0), "fail", "المرجع هو المجلد الحادي عشر"
    for m in re.finditer(rf"الجزء ({ORD_RE}){LETTER}", text):
        before, after = text[max(0, m.start() - 25): m.start()], text[m.end(): m.end() + 30]
        if re.match(r"\s*[:،]?\s*(التأسيس|التواصل|المنصات|المنصّات|التمكين)", after) or re.search(r"(تعلّمت|تعلمت|درست|عرفت)\s+في\s*$", before):
            yield "الجزء ن", m.group(0), "fail", "إحالةٌ إلى جزءٍ من البنية القديمة"
    for m in re.finditer(r"المستوى (٠|صفر)(?![٠-٩])|المستويات (٠|صفر)|(?<![\[ء-ي])م٠(?![٠-٩])", text):
        yield "المستوى ٠", m.group(0), "fail", "المستويات من ١ إلى ١٣"
    for m in re.finditer(r"المستوى ([٠-٩]+)", text):
        if num(m.group(1)) > 13:
            yield "المستوى > ١٣", m.group(0), "fail", ""
    for m in re.finditer(r"(ال)?ملحق (هـ|و|ز)" + LETTER, text):
        yield "حرف ملحق", m.group(0), "fail", "الملاحق أ–د في المرجع؛ وبرنامج النطق ملحق الباب الثاني؛ ود وز القديمان كتابان مرافقان"
    for m in re.finditer(r"[0٠][0-4٠-٤][-‐](المستويات|نظام|خريطة|الرؤية|الوثيقة)|\S+\.md\b|`[^`]*\.(md|py|tsv)`", text):
        yield "اسم ملف", m.group(0), "fail", "لا أسماء ملفات في النص المطبوع"
    for m in ids.PROD.finditer(text):
        try:
            ids.teaching_id(m)
        except ValueError as e:
            yield "معرّف مثال", m.group(0), "fail", str(e)
    # references to a bab in another volume carry the volume (Bible, ch. 111 §٢); the named volume must be right
    for m in re.finditer(rf"(?:(المجلد ({'|'.join(sorted(VOLW, key=len, reverse=True))}))،\s*)?الباب ({ORD_RE}){LETTER}"
                         rf"(?:،\s*الفصل ({ORD_RE}|[ء-ي]+))?(?:\s*\(([^)]*)\))?", text):
        ctx = text[max(0, m.start() - 40): m.end() + 40]
        if any(s in ctx for s in NOT_A_REFERENCE):
            continue
        b = ORD.index(m.group(3)) + 1
        tv = VOL_OF_BAB[b]
        named = m.group(2) or (re.search(r"المجلد (" + "|".join(sorted(VOLW, key=len, reverse=True)) + r")", m.group(5) or "") or [None, None])[1]
        if named and VOLW.index(named) + 1 != tv:
            yield "إحالة", m.group(0), "fail", f"الباب {b} في المجلد {VOLW[tv - 1]}، لا {named}"
        ch = m.group(4)
        if ch in ORD and ORD.index(ch) + 1 > chapters_in(b):
            yield "إحالة", m.group(0), "fail", f"الباب {b} فيه {chapters_in(b)} فصول"
        if vol != tv and not named and not re.search(r"المجلد", text[max(0, m.start() - 30): m.end() + 60]):
            if re.search(r"انظر\s+(المجلد [^،]+،\s*)?" + re.escape("الباب " + m.group(3)) + LETTER, text[m.end(): m.end() + 160]):
                continue                                    # the volume is named in the reference that follows
            yield "إحالة", m.group(0), "fail", f"إحالةٌ إلى مجلدٍ آخر (المجلد {VOLW[tv - 1]}) بلا ذكر المجلد"


def main(strict=False):
    results, findings = [], []

    def check(name, ok, detail=""):
        results.append((name, ok, detail))

    # --- the files: none unplaced, none twice, none ambiguous -------------------------------------------------------
    placed = files_of_series()
    paths = [str(f.relative_to(BOOK)) for f, _ in placed]
    every = sorted(str(p.relative_to(BOOK)) for p in BOOK.rglob("*.md")
                   if "_production" not in p.parts and p.name != "README.md")
    orphans = sorted(set(every) - set(paths))
    check("لا ملفّ بلا مكان (orphans)", not orphans, "، ".join(orphans[:5]))
    dups = sorted({p for p in paths if paths.count(p) > 1})
    check("لا ملفّ في موضعين (duplicates)", not dups, "، ".join(dups[:5]))
    missing = [p for p in paths if not (BOOK / p).exists()]
    check("كل ملفٍّ في الخريطة موجود", not missing, "، ".join(missing[:5]))
    loose = [p.name for p in BOOK.glob("*.md") if p.name != "README.md"] + [p.name for p in BOOK.glob("الجزء-*")] \
        + [p.name for p in BOOK.glob("الملاحق")] + [p.name for p in BOOK.glob("الخواتيم")] + [p.name for p in BOOK.glob("الافتتاحية")]
    check("لا وجهة ملتبسة (لا ملفات ولا مجلّدات من البنية القديمة في book/)", not loose, "، ".join(loose))

    # --- nothing lost: every file of the transition table is where the plan (or a recorded rename) put it ---------
    table = list(csv.reader(open(OUT / "جدول-الانتقال.tsv", encoding="utf-8"), delimiter="\t"))[1:]
    renames = {}
    log = OUT / "سجل-التصحيحات-البنيوية.tsv"
    for r in csv.reader(open(log, encoding="utf-8"), delimiter="\t"):
        if len(r) > 3 and r[2] == "(اسم الملف)":
            renames[r[0]] = r[3]
    lost = []
    for r in table:
        new = r[5]
        new = renames.get(new, new)
        if new.startswith("_production/الأرشيف/البنية-القديمة/"):
            new = "_production/الأرشيف/البنية-القديمة/" + Path(new).name
        if not (BOOK / new).exists():
            lost.append(f"{r[0]} → {new}")
    check(f"لا ملفّ ضائع من الملفات الـ{len(table)} (ولا حذفٌ صامت)", not lost, "، ".join(lost[:5]))
    archived = [p.name for p in ARCHIVE.glob("*.md") if p.name != "README.md"]
    check("الملفات القديمة الستة في الأرشيف بإشعاره", len(archived) == 6 and (ARCHIVE / "README.md").exists(), "، ".join(archived))

    # --- the scan ------------------------------------------------------------------------------------------------------
    for f, vol in placed:
        m = re.search(r"الباب-(" + "|".join(sorted((o.replace(" ", "-") for o in ORD), key=len, reverse=True)) + r")", str(f))
        bab = [o.replace(" ", "-") for o in ORD].index(m.group(1)) + 1 if m else None
        text = f.read_text(encoding="utf-8")
        for name, t, verdict, note in scan(f, vol, text, bab):
            line = text[: text.find(t)].count("\n") + 1 if t in text else 0
            findings.append([str(f.relative_to(BOOK)), str(line), name, t, verdict, note])
        if bab:                                            # the level in every chapter header is its bab
            head = "\n".join(text.splitlines()[:6])
            for hm in re.finditer(r"المستوى ([٠-٩]+)", head):
                if num(hm.group(1)) != bab:
                    findings.append([str(f.relative_to(BOOK)), "رأس", "المستوى والباب", hm.group(0), "fail", f"الباب {bab}"])
    for tool in ("frontmatter.py", "opening.py"):
        text = (HERE / tool).read_text(encoding="utf-8")
        for m in re.finditer(r"ثمانية|من ثمانية|الأجزاء الأربعة|الباب الرابع عشر", text):
            findings.append([f"pdf/{tool}", str(text[: m.start()].count("\n") + 1), "المقدّمات", m.group(0), "fail", ""])
    fails = [x for x in findings if x[4] == "fail"]
    reads = [x for x in findings if x[4] == "read"]
    by = {}
    for x in fails:
        by[x[2]] = by.get(x[2], 0) + 1
    check("لا أثر للبنية القديمة في النص المطبوع والكتب المرافقة والمقدّمات", not fails,
          "، ".join(f"{k}: {v}" for k, v in by.items()))

    # --- example IDs ---------------------------------------------------------------------------------------------------
    prod = sum(len(ids.PROD.findall(f.read_text(encoding="utf-8"))) for f, _ in placed)
    sample = "".join(ids.printed(f.read_text(encoding="utf-8")) for f, _ in placed)
    left = re.findall(r"\[م[٠-٩]+-ب[٠-٩]+", sample)
    check(f"المعرّفات الإنتاجية باقية ({prod})، والمطبوعة كلها بالنظام الجديد", prod > 0 and not left, f"بقي {len(left)}")

    # --- the reference stands outside the numbering -------------------------------------------------------------------
    ref = VOLUMES[-1]
    bank = (BOOK / "المجلد-الحادي-عشر" / "المرجع-الأول-بنك-الأخطاء" / "00-فاتحة-بنك-الأخطاء.md").read_text(encoding="utf-8")
    ok = ref["stage"] is None and not any(u[0] == "bab" for u in ref["units"]) and bank.startswith("# المرجع الأول: بنك الأخطاء") \
        and ref["name"] == "مرجع المتكلّم العربي" and "خارج ترقيم الأبواب والمستويات" in FM.volumes_map() \
        and "وليس بابًا رابع عشر ولا مستوًى" in (OPENING / "18-كيف-تقرأ-المجلدات-وعهد-المؤلف.md").read_text(encoding="utf-8")
    check("المجلد الحادي عشر مرجعٌ خارج ترقيم الأبواب والمستويات، بعنوانه المعتمد", ok)

    # --- the unique material of the eight files is in its place --------------------------------------------------------
    ch17 = (OPENING / "18-كيف-تقرأ-المجلدات-وعهد-المؤلف.md").read_text(encoding="utf-8")
    need = {"الأبعاد العشرة (٠٢)": "| **الطبيعية** |" in ch17 and "| **مراعاة المخاطَب** |" in ch17,
            "طريق المهارة (٠٢)": "المفهوم ← الشرح ← المثال غير الناجح" in ch17,
            "مثال السؤال بعد المحاضرة (٠٢)": "المعنى يسبق اللفظ في الاختيار" in ch17,
            "الحلقة: النموذج ← الأبعاد ← التشخيص ← الطريق ← الإعادة": "النموذج ← الأبعاد العشرة ← تشخيص الأداء ← طريق المهارة ← إعادة الأداء" in ch17,
            "مسار الدرس والمدرّب (٠٣)": "حصةٌ تدريبيةٌ نحو تسعين دقيقة" in ch17 and "**وللمدرّب**" in ch17,
            "شرط التأسيس (٠١)": "كتابٍ تأسيسيٍّ قبله" in ch17,
            "«لماذا هذا الترتيب؟» (الفاتحة)": "وليس هذا الترتيب اتفاقًا" in ch17,
            "قدرات نهاية التأسيس (الفاتحة، معادةً على الأبواب الأربعة)": "ويعرف المتعلّم أنه أتمّ مرحلة التأسيس" in ch17,
            "تنبيه الأسماء الافتراضية (الواجهة)": FM.FICTIONAL_NAMES in FM.rights(),
            "الرموز التعليمية وسلّم الرسمية (٠٣)": "◐" in FM.symbols() and "شديد الرسمية" in FM.symbols(),
            "كلمة المؤلف على الأحد عشر": "أحد عشر مجلدًا" in (BOOK / "المجلد-الأول" / "00-كلمة-المؤلف.md").read_text(encoding="utf-8")}
    for k, v in need.items():
        check(f"مادةٌ فريدة في موضعها: {k}", v)

    # --- the tools read the new paths ----------------------------------------------------------------------------------
    stale = []
    for p in sorted(HERE.glob("*.py")):
        if p.name == "premove.py":
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r'"الجزء-|الجزء-\*|BOOK / "(الافتتاحية|الملاحق|الخواتيم|المدخل|00-كلمة-المؤلف\.md)"', line):
                stale.append(f"{p.name}:{n}")
    check("لا أداة حيّة تقرأ مسارات البنية القديمة", not stale, "، ".join(stale))

    # --- the report ----------------------------------------------------------------------------------------------------
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "فحص-ما-بعد-النقل.tsv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["الملف", "السطر", "الفحص", "النص", "الحكم", "ملاحظة"])
        w.writerows(findings)
    passed = sum(1 for _, ok, _ in results if ok)
    L = ["# فحص ما بعد النقل", "",
         f"من `python3 pdf/premove.py --strict` (الدليل، الباب ١١٢د). **{passed} من {len(results)} فحصًا ناجح.**", "",
         "| الفحص | النتيجة | تفصيل |", "|---|---|---|"]
    L += [f"| {n} | {'✔' if ok else '✘'} | {d} |" for n, ok, d in results]
    L += ["", "## مواضع تحتاج قارئًا", ""]
    L += [f"- `{x[0]}:{x[1]}` «{x[3]}»: {x[5]}" for x in reads] or ["لا شيء."]
    L += ["", "## الإخفاقات", ""]
    L += [f"- `{x[0]}:{x[1]}` [{x[2]}] «{x[3]}»: {x[5]}" for x in fails] or ["لا شيء."]
    (OUT / "فحص-ما-بعد-النقل.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for n, ok, d in results:
        print(("PASS " if ok else "FAIL ") + n + (f" — {d}" if d and not ok else ""))
    print(f"{passed}/{len(results)} checks; {len(fails)} failures; {len(reads)} for a reader")
    if strict and passed != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main("--strict" in sys.argv)
