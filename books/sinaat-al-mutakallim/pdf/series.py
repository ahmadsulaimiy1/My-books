#!/usr/bin/env python3
"""The series in eleven volumes (Bible, ch. 112c–112d): ten volumes of the programme in four stages, then the
reference. The volumes and their boundaries are model C of the gate (gate.py), approved by the author; they are read
from there, not restated here. Thirteen abwab, numbered 1–13 across the series; a level always equals its bab; the
reference stands outside both numberings.

Writes the general contents and the table that sends every file of the manuscript to its place — a volume, a
companion book, the production files, or the archive — with the path it will have after the move. Nothing is moved
here; the table is the plan of the move. It covers every .md file under book/ (outside _production) exactly once,
and no two files share a new path.

    python3 series.py      writes book/_production/هندسة-السلسلة/{الفهرس-العام.md, جدول-الانتقال.tsv}
"""
from gate import APPENDIX, AR, BOOK, DIRS, MODELS, ORD, OUT, OUTSIDE_C

MODEL = "C"
VOLUMES = MODELS[MODEL]["volumes"]
# the approved title of a volume where it differs from its short name in the gate (Bible, ch. 112d §٧)
TITLES = {11: ("مرجع المتكلّم العربي", "بنك الأخطاء والتعبيرات والنماذج")}
STAGE = {"التأسيس": "المرحلة الأولى: التأسيس", "التواصل": "المرحلة الثانية: التواصل",
         "المنصّات": "المرحلة الثالثة: المنصّات", "التمكين": "المرحلة الرابعة: التمكين",
         "المرجع": "المرجع: خارج ترقيم الأبواب والمستويات، يرافق المراحل كلها"}
ORD_M = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي عشر"]
VOL_DIR = ["المجلد-" + o.replace(" ", "-") for o in ORD_M]

ARCHIVE = "_production/الأرشيف/البنية-القديمة"
# what leaves the printed series (OUTSIDE_C in gate.py), by unit: (destination, new folder)
OUTSIDE = {("app", "د"): (OUTSIDE_C[0][1], "_المرافقة/سكريبتات-الحلقات"),
           ("app", "ز"): (OUTSIDE_C[1][1], "_المرافقة/بنك-الاختبارات-ودليل-المعلم"),
           ("end", "تقرير-ضبط-الجودة"): (OUTSIDE_C[2][1], "_production/qa")}

# the eight files model C does not place, as the author decided them (Bible, ch. 112d §٢):
# path -> (volume, destination, new path, note). A file whose material moves into another is archived only after
# that material has been written into its place (the work orders of ch. 112d §٦).
DECIDED = {
    "00-كلمة-المؤلف.md": ("1", "مقدّمات المجلد الأول", f"{VOL_DIR[0]}/00-كلمة-المؤلف.md",
                          "مطبوع؛ يُصحَّح فيه ذكر «الثمانية» بالأحد عشر"),
    "00-الإهداء.md": ("—", "أرشيف", f"{ARCHIVE}/00-الإهداء.md",
                      "المعتمد الإهداء الذي يخرجه frontmatter.py"),
    "00-الواجهة.md": ("—", "أرشيف", f"{ARCHIVE}/00-الواجهة.md",
                      "بعد نقل تنبيه الأسماء الافتراضية إلى صفحة الحقوق في كل مجلد"),
    "01-المقدمة.md": ("—", "أرشيف", f"{ARCHIVE}/01-المقدمة.md",
                      "مدمجٌ في الافتتاحية؛ لا يُطبع ملفًّا مستقلًّا"),
    "02-مدخل.md": ("—", "أرشيف", f"{ARCHIVE}/02-مدخل.md",
                   "بعد دمج الأبعاد العشرة وطريق المهارة ومثالها في الافتتاحية ١٧ §٢؛ و«الدرجات الأربع» لا تُعتمد"),
    "03-كيف-تستعمل-الكتاب.md": ("—", "أرشيف", f"{ARCHIVE}/03-كيف-تستعمل-الكتاب.md",
                                "بعد توزيعه: طريقة الاستعمال في الافتتاحية ١٧، والرموز التعليمية وسلّم الرسمية في صفحة الرموز من كل مجلد"),
    "00-التكليف-الرسمي.md": ("—", "ملفات الإنتاج", "_production/00-التكليف-الرسمي.md",
                             "وثيقة تأليفٍ ملزمة؛ لا تدخل المجلدات المطبوعة"),
    "الجزء-الأول/00-فاتحة-الجزء-الأول.md": ("—", "أرشيف", f"{ARCHIVE}/00-فاتحة-الجزء-الأول.md",
                                           "بعد دمج «لماذا هذا الترتيب؟» في الافتتاحية ١٧ وقدرات نهاية المرحلة حيث تُعرَّف مخرجات التأسيس"),
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


def unit_dir(u):
    """The folder a unit takes inside its volume."""
    if u[0] in ("opening", "intro"):
        return {"opening": "الافتتاحية", "intro": "المدخل"}[u[0]]
    if u[0] == "bab":
        return "المرجع-الأول-بنك-الأخطاء" if u[2] is None else "الباب-" + DIRS[u[2] - 1]
    if u[0] == "app":
        return "الملاحق"
    return "الخاتمة" if u[1] == "00-خاتمة-الكتاب" else "الخواتيم"


def new_name(u, f):
    """A file keeps its name, except a bab opener whose name carries the old number."""
    if u[0] == "bab" and f.name.startswith("00-فاتحة-"):
        return "00-فاتحة-بنك-الأخطاء.md" if u[2] is None else f"00-فاتحة-الباب-{DIRS[u[2] - 1]}.md"
    return f.name


def label(u):
    """(unit in the series, level, note) for one unit of a volume."""
    if u[0] == "opening":
        return "الافتتاحية", "", ""
    if u[0] == "intro":
        return "المدخل", "", ""
    if u[0] == "bab":
        old, new = u[1], u[2]
        if new is None:
            return "المرجع الأول: بنك الأخطاء", "—", f"كان الباب {ORD[old - 1]}؛ يخرج من تسلسل الأبواب ولا مستوى له"
        note = [f"كان الباب {ORD[old - 1]}؛ يُعاد ترقيمه"] if new != old else []
        note.append(f"المستوى كان {old - 1 if old < 13 else 12}")
        return f"الباب {ORD[new - 1]}", str(new), "؛ ".join(note)
    if u[0] == "app":
        name = f"ملحق {u[1]}: {APPENDIX[u[1]]}"
        return name, "", ("ينتقل من الملاحق إلى آخر الباب الثاني" if u[1] == "و" else "")
    t = first_line(BOOK / "الخواتيم" / f"{u[1]}.md")
    return t, "", ("تنتقل إلى ختام آخر مجلدٍ تدريبي" if u[1] == "00-خاتمة-الكتاب" else "")


def vol_title(i):
    return TITLES[i][0] if i in TITLES else VOLUMES[i - 1]["name"]


def plan():
    """(rows, contents lines). A row: present path, volume, volume or destination, unit, level, new path, note."""
    rows, placed, targets = [], set(), set()

    def add(f, vol, dest, unit, level, new, note):
        rel = str(f.relative_to(BOOK))
        assert rel not in placed, f"mapped twice: {rel}"
        assert new not in targets, f"two files for one new path: {new}"
        placed.add(rel)
        targets.add(new)
        rows.append([rel, vol, dest, unit, level, new, note])

    md = ["# الفهرس العام للسلسلة", "",
          "صناعة المتكلّم العربي في أحد عشر مجلدًا: عشرة للمنهج تبنيه في ثلاثة عشر بابًا على أربع مراحل، "
          "ثم «مرجع المتكلّم العربي» خارج ترقيم الأبواب والمستويات (الدليل، البابان ١١٢ج و١١٢د). "
          "والأبواب ١–١٣ متصلةٌ عبر السلسلة، والمستوى رقمه رقم بابه.", ""]
    stage = None
    for i, v in enumerate(VOLUMES, 1):
        if v["stage"] != stage:
            stage = v["stage"]
            md += [f"## {STAGE[stage]}", ""]
        sub = f"\n\n**{TITLES[i][1]}**" if i in TITLES else ""
        md += [f"### المجلد {ORD_M[i - 1]}: {vol_title(i)}{sub}", "", f"> {v['sentence']}", ""]
        if i == 1:
            rel = "00-كلمة-المؤلف.md"
            vol, dest, new, note = DECIDED[rel]
            add(BOOK / rel, vol, dest, "المقدّمات: كلمة المؤلف", "", new, note)
            md.append("- **المقدّمات**: كلمة المؤلف، والرموز والاصطلاحات")
        for u in v["units"]:
            unit, level, note = label(u)
            for f in unit_files(u):
                add(f, str(i), vol_title(i), unit, level, f"{VOL_DIR[i - 1]}/{unit_dir(u)}/{new_name(u, f)}", note)
            if u[0] == "opening":
                md.append("- **الافتتاحية**: المقدمة العلمية في سبعة عشر فصلًا، وخاتمتها، وملحق التحقيق، وثبت المصادر")
            elif u[0] == "intro":
                md.append("- **المدخل**: العربية ومستوياتها")
            elif u[0] == "bab":
                title = first_line(next(iter(sorted(bab_dir(u[1]).glob("00-*.md"))))).split(":", 1)[-1].strip()
                lvl = f" — المستوى {level.translate(AR)}" if level not in ("", "—") else ""
                was = f" (كان الباب {ORD[u[1] - 1]})" if u[2] != u[1] else ""
                head = unit if u[2] is None else f"{unit}: {title}"
                md.append(f"- **{head}**{lvl}{was}")
                md += [f"  - {t}" for t in chapters(bab_dir(u[1]))]
            else:
                md.append(f"- **{unit}**")
        if v["stage"] == "المرجع":
            md.append("- **الفهارس العامة للسلسلة** (تُبنى بعد إخراج المجلدات العشرة)")
        md.append("")

    for u, (dest, folder) in OUTSIDE.items():
        for f in unit_files(u):
            add(f, "—", dest, label(u)[0], "", f"{folder}/{f.name}", "يخرج من السلسلة المطبوعة")
    md += ["## خارج السلسلة المطبوعة", "", "| المادة | موضعها | السبب |", "|---|---|---|"]
    md += [f"| {a} | {b} | {c} |" for a, b, c in OUTSIDE_C]
    md.append("")

    md += ["## ملفات البنية القديمة", "",
           "قرّرها المؤلف (الباب ١١٢د §٢). وما تُنقل مادّته إلى موضعٍ آخر لا يُؤرشف إلا بعد كتابتها في موضعها.", "",
           "| الملف | الوجهة | ملاحظة |", "|---|---|---|"]
    for rel, (vol, dest, new, note) in DECIDED.items():
        if vol != "—":
            continue
        add(BOOK / rel, vol, dest, "", "", new, note)
        md.append(f"| `{rel}` | {dest} | {note} |")
    md.append("")

    every = {str(p.relative_to(BOOK)) for p in BOOK.rglob("*.md") if "_production" not in p.parts and p.name != "README.md"}
    missing, extra = every - placed, placed - every
    assert not missing and not extra, f"unmapped: {sorted(missing)}; not found: {sorted(extra)}"
    return rows, md


HEADER = ["الملف الحالي", "المجلد", "اسم المجلد أو الوجهة", "الوحدة في السلسلة", "المستوى", "الموضع الجديد", "ملاحظة"]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, md = plan()
    (OUT / "الفهرس-العام.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(OUT / "جدول-الانتقال.tsv", "w", encoding="utf-8") as fh:
        for r in [HEADER] + rows:
            fh.write("\t".join(r) + "\n")
    by = {}
    for r in rows:
        by[r[1]] = by.get(r[1], 0) + 1
    print(len(rows), "files mapped:", ", ".join(f"{k}: {n}" for k, n in by.items()))


if __name__ == "__main__":
    main()
