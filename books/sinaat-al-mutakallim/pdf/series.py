#!/usr/bin/env python3
"""The series in eleven volumes (Bible, ch. 112c): ten volumes of the programme in four stages, then the reference.
The volumes and their boundaries are model C of the gate (gate.py), approved by the author; they are read from there,
not restated here. Levels are numbered 1–13 and equal the series number of their bab; the reference has no level.

Writes the general contents and the table that sends every file of the manuscript to its place: a volume, a
companion book, the production files, or «?» where the author has still to decide. Nothing is moved here; the
table is the plan of the move, and it covers every .md file under book/ (outside _production) exactly once.

    python3 series.py      writes book/_production/هندسة-السلسلة/{الفهرس-العام.md, جدول-الانتقال.tsv}
"""
from pathlib import Path

from gate import APPENDIX, AR, BOOK, DIRS, MODELS, ORD, OUT, OUTSIDE_C

MODEL = "C"
VOLUMES = MODELS[MODEL]["volumes"]
STAGE = {"التأسيس": "المرحلة الأولى: التأسيس", "التواصل": "المرحلة الثانية: التواصل",
         "المنصّات": "المرحلة الثالثة: المنصّات", "التمكين": "المرحلة الرابعة: التمكين", "المرجع": "المرجع: يرافق المراحل كلها"}
ORD_M = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر"]
ORD_F = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة"]

# what leaves the printed series (OUTSIDE_C in gate.py), by unit
OUTSIDE = {("app", "د"): OUTSIDE_C[0][1], ("app", "ز"): OUTSIDE_C[1][1], ("end", "تقرير-ضبط-الجودة"): OUTSIDE_C[2][1]}

# files that model C does not place; each waits for the author, with what the files show about it
UNDECIDED = {
    "00-كلمة-المؤلف.md": "مقدّمات المجلد الأول (تبنيها opening.py)؛ وفيها «ثمانية مجلدات» تُصحَّح بالأحد عشر",
    "00-الإهداء.md": "مخطوط الطبعة ذات الأجزاء الأربعة (book_build.py)؛ والإهداء المعتمد في frontmatter.py",
    "00-الواجهة.md": "صفحة عنوان «الجزء الأول» من الطبعة ذات الأجزاء الأربعة؛ وصفحة العنوان الآن في frontmatter.py",
    "01-المقدمة.md": "مقدّمة الطبعة ذات الأجزاء الأربعة؛ هل تغني عنها الافتتاحية؟",
    "02-مدخل.md": "«مدخل: حين لا يظهر العلم على اللسان» من الطبعة ذات الأجزاء الأربعة؛ هل تغني عنه الافتتاحية؟",
    "03-كيف-تستعمل-الكتاب.md": "يصف أربعة أجزاء ومستويات ٠–١٢؛ ويقابله في الافتتاحية الفصل ١٨ «كيف تقرأ المجلدات»",
    "00-التكليف-الرسمي.md": "وثيقة تأليفٍ ملزمة لا نصٌّ للقارئ؛ مكانها المقترح ملفات الإنتاج",
    "الجزء-الأول/00-فاتحة-الجزء-الأول.md": "فاتحة «الجزء الأول: التأسيس» ولا أجزاء في السلسلة؛ فاتحةٌ للمرحلة أم تُطوى؟",
}


def bab_dir(n):
    return next(BOOK.glob("الجزء-*/الباب-" + DIRS[n - 1]))


def first_line(f):
    return f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()


def chapters(d):
    seen = {}
    for f in sorted(d.glob("ف*.md")):
        seen.setdefault(f.name[1:3], first_line(f))
    return list(seen.values())


def app_files(letter):
    return sorted(f for f in (BOOK / "الملاحق").glob("*.md") if f.stem.split("-")[1] == letter)


def unit_files(u):
    if u[0] == "opening":
        return sorted((BOOK / "الافتتاحية").glob("*.md"))
    if u[0] == "intro":
        return sorted((BOOK / "المدخل").glob("*.md"))
    if u[0] == "bab":
        return sorted(bab_dir(u[1]).glob("*.md"))
    if u[0] == "app":
        return app_files(u[1])
    return [BOOK / "الخواتيم" / f"{u[1]}.md"]


def label(u):
    """(unit in the series, level, note) for one unit of a volume."""
    if u[0] == "opening":
        return "الافتتاحية", "", ""
    if u[0] == "intro":
        return "المدخل", "", ""
    if u[0] == "bab":
        old, new = u[1], u[2]
        if new is None:
            return "المرجع الأول", "—", f"كان الباب {ORD[old - 1]}؛ يخرج من تسلسل الأبواب ولا مستوى له"
        note = [f"كان الباب {ORD[old - 1]}؛ يُعاد ترقيمه"] if new != old else []
        note.append(f"المستوى كان {old - 1 if old < 13 else 12}")
        return f"الباب {ORD[new - 1]}", str(new), "؛ ".join(note)
    if u[0] == "app":
        name = f"ملحق {u[1]}: {APPENDIX[u[1]]}"
        return name, "", ("ينتقل من الملاحق إلى آخر الباب الثاني" if u[1] == "و" else "")
    t = first_line(BOOK / "الخواتيم" / f"{u[1]}.md")
    return t, "", ("تنتقل إلى ختام آخر مجلدٍ تدريبي" if u[1] == "00-خاتمة-الكتاب" else "")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, placed = [], set()

    def add(f, *rest):
        rel = str(f.relative_to(BOOK))
        assert rel not in placed, f"mapped twice: {rel}"
        placed.add(rel)
        rows.append([rel, *rest])

    md = ["# الفهرس العام للسلسلة", "",
          "صناعة المتكلّم العربي في أحد عشر مجلدًا: عشرة للمنهج في أربع مراحل، ثم المرجع (الدليل، الباب ١١٢ج). "
          "والأبواب ١–١٣ متصلةٌ عبر السلسلة، والمستوى رقمه رقم بابه، ولا مستوى للمرجع.", ""]
    stage = None
    for i, v in enumerate(VOLUMES, 1):
        if v["stage"] != stage:
            stage = v["stage"]
            md += [f"## {STAGE[stage]}", ""]
        md += [f"### المجلد {ORD_M[i - 1]}: {v['name']}", "", f"> {v['sentence']}", ""]
        for u in v["units"]:
            unit, level, note = label(u)
            for f in unit_files(u):
                add(f, str(i), v["name"], unit, level, note)
            if u[0] == "opening":
                md.append("- **الافتتاحية**: المقدمة العلمية في سبعة عشر فصلًا، وخاتمتها، وملحق التحقيق، وثبت المصادر")
            elif u[0] == "intro":
                md.append("- **المدخل**: العربية ومستوياتها")
            elif u[0] == "bab":
                title = first_line(next(iter(sorted(bab_dir(u[1]).glob("00-*.md"))))).split(":", 1)[-1].strip()
                lvl = f" — المستوى {level.translate(AR)}" if level not in ("", "—") else ""
                was = f" (كان الباب {ORD[u[1] - 1]})" if u[2] != u[1] else ""
                md.append(f"- **{unit}: {title}**{lvl}{was}")
                md += [f"  - {t}" for t in chapters(bab_dir(u[1]))]
            else:
                md.append(f"- **{unit}**")
        if v["stage"] == "المرجع":
            md.append("- **الفهارس العامة للسلسلة** (تُبنى بعد إخراج المجلدات العشرة)")
        md.append("")

    for u, dest in OUTSIDE.items():
        for f in unit_files(u):
            add(f, "—", dest, label(u)[0], "", "يخرج من السلسلة المطبوعة")
    md += ["## خارج السلسلة المطبوعة", "", "| المادة | موضعها | السبب |", "|---|---|---|"]
    md += [f"| {a} | {b} | {c} |" for a, b, c in OUTSIDE_C]
    md.append("")

    md += ["## ملفاتٌ تنتظر قرار المؤلف", "",
           "لم يضعها النموذج C في مجلد، ولا تُنقل حتى يُقرَّر مكانها.", "", "| الملف | ما تُظهره الملفات |", "|---|---|"]
    for rel, why in UNDECIDED.items():
        add(BOOK / rel, "؟", "", "", "", "يحتاج قرار المؤلف: " + why)
        md.append(f"| `{rel}` | {why} |")
    md.append("")

    every = {str(p.relative_to(BOOK)) for p in BOOK.rglob("*.md") if "_production" not in p.parts and p.name != "README.md"}
    missing, extra = every - placed, placed - every
    assert not missing and not extra, f"unmapped: {sorted(missing)}; not found: {sorted(extra)}"

    (OUT / "الفهرس-العام.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(OUT / "جدول-الانتقال.tsv", "w", encoding="utf-8") as fh:
        fh.write("\t".join(["الملف الحالي", "المجلد", "اسم المجلد أو الوجهة", "الوحدة في السلسلة", "المستوى", "ملاحظة"]) + "\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")
    by = {}
    for r in rows:
        by[r[1]] = by.get(r[1], 0) + 1
    print(len(rows), "files mapped:", ", ".join(f"{k}: {n}" for k, n in by.items()))


if __name__ == "__main__":
    main()
