#!/usr/bin/env python3
"""The general contents of the series (Bible, chs. 112c–112d), read from the manuscript as it now stands.

The volumes and their units come from volumes.py, the authoritative map; the chapter titles come from the files.
The transition table that moved the manuscript into this structure is kept as a record
(book/_production/هندسة-السلسلة/جدول-الانتقال.tsv); this tool no longer writes it.

    python3 series.py      writes book/_production/هندسة-السلسلة/الفهرس-العام.md
"""
from volumes import APPENDIX, AR, BOOK, COMPANIONS, ORD, PROGRAM, VOLUMES, unit_dir, unit_files

OUT = BOOK / "_production" / "هندسة-السلسلة"
STAGE_NAME = {1: "المرحلة الأولى: التأسيس", 2: "المرحلة الثانية: التواصل", 3: "المرحلة الثالثة: المنصّات",
              4: "المرحلة الرابعة: التمكين", None: "المرجع: خارج ترقيم الأبواب والمستويات، يرافق المراحل كلها"}


def first_line(f):
    return f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()


def chapters(d):
    seen = {}
    for f in sorted(d.glob("ف*.md")):
        seen.setdefault(f.name[1:3], first_line(f))
    return list(seen.values())


def opener_title(d):
    return first_line(next(iter(sorted(d.glob("00-*.md"))))).split(":", 1)[-1].strip()


def main():
    md = ["# الفهرس العام للسلسلة", "",
          "صناعة المتكلّم العربي في أحد عشر مجلدًا: عشرة للمنهج تبنيه في ثلاثة عشر بابًا على أربع مراحل، ثم «مرجع المتكلّم "
          "العربي» خارج ترقيم الأبواب والمستويات (الدليل، البابان ١١٢ج و١١٢د). والأبواب ١–١٣ متصلةٌ عبر السلسلة، والمستوى "
          "رقمه رقم بابه.", ""]
    stage, count = "", 0
    for v in VOLUMES:
        if v["stage"] != stage:
            stage = v["stage"]
            md += [f"## {STAGE_NAME[stage]}", ""]
        sub = f" — {v['subtitle']}" if v.get("subtitle") else ""
        md += [f"### المجلد {ORD[v['n'] - 1]}: {v['name']}{sub}", "", f"> {v['sentence']}", ""]
        if v["n"] == 1:
            md.append("- **المقدّمات**: كلمة المؤلف، والرموز والاصطلاحات")
        for u in v["units"]:
            files = unit_files(v["n"], u)
            assert files and all(f.exists() for f in files), f"missing files for {u} in volume {v['n']}"
            count += len(files)
            d = unit_dir(v["n"], u)
            if u[0] == "opening":
                md.append("- **الافتتاحية**: المقدمة العلمية في سبعة عشر فصلًا، وخاتمتها، وملحق التحقيق، وثبت المصادر")
            elif u[0] == "intro":
                md.append("- **المدخل**: العربية ومستوياتها")
            elif u[0] == "bab":
                md.append(f"- **الباب {ORD[u[1] - 1]}: {opener_title(d)}** — المستوى {str(u[1]).translate(AR)}")
                md += [f"  - {t}" for t in chapters(d)]
            elif u[0] == "reference":
                md.append(f"- **المرجع الأول: {opener_title(d)}**")
                md += [f"  - {t}" for t in chapters(d)]
            elif u[0] == "program":
                md.append(f"- **{PROGRAM}**")
            elif u[0] == "app":
                md.append(f"- **ملحق {u[1]}: {APPENDIX[u[1]]}**")
            else:
                md.append(f"- **{first_line(files[0])}**")
        if v["stage"] is None:
            md.append("- **الفهارس العامة للسلسلة** (تُبنى بعد إخراج المجلدات العشرة)")
        md.append("")
    md += ["## الكتب المرافقة", ""]
    for folder, name in COMPANIONS.items():
        md.append(f"- **{name}** (`book/_المرافقة/{folder}/`)")
    md.append("")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "الفهرس-العام.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(count, "files in", len(VOLUMES), "volumes")


if __name__ == "__main__":
    main()
