#!/usr/bin/env python3
"""The series in eight volumes (Bible, part fifteen): the general contents, and the table that moves each file of
the manuscript from its present part to its volume. Nothing is moved here; the table is the plan of the move.

    python3 series.py      writes book/_production/هندسة-السلسلة/{الفهرس-العام.md, جدول-الانتقال.tsv}
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
OUT = BOOK / "_production" / "هندسة-السلسلة"

ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي-عشر", "الثاني-عشر", "الثالث-عشر", "الرابع-عشر"]
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

# (volume, name, stage, [(present bab number, bab number in the series)], extra units)
VOLUMES = [
    (1, "الأصول", "المرحلة الأولى: التأسيس", [(1, 1)], ["الافتتاحية"]),
    (2, "اللسان", "المرحلة الأولى: التأسيس", [(2, 2)], []),
    (3, "العبارة والبيان", "المرحلة الأولى: التأسيس", [(3, 3), (4, 4)], []),
    (4, "المقام", "المرحلة الثانية: التواصل", [(5, 5)], []),
    (5, "الأدب والحوار", "المرحلة الثانية: التواصل", [(6, 6), (7, 7)], []),
    (6, "المنصّات", "المرحلة الثالثة: المنصّات", [(8, 8), (9, 9), (10, 10)], []),
    (7, "التمكين", "المرحلة الرابعة: التمكين", [(11, 11), (12, 12), (14, 13)], []),
    (8, "المرجع", "يرافق المراحل كلها", [(13, None)], ["الملاحق", "الخواتيم"]),
]
LEVEL = {n: n - 1 for n in range(1, 14)}
ORDINAL_F = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن"]


def bab_dir(n):
    name = "الباب-" + ORD[n - 1]
    for d in BOOK.glob("الجزء-*/" + name):
        return d
    raise FileNotFoundError(name)


def chapters(d):
    seen = {}
    for f in sorted(d.glob("ف*.md")):
        k = re.match(r"ف(\d+)", f.name).group(1)
        seen.setdefault(k, f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip())
    return seen


def title(d):
    f = next(iter(sorted(d.glob("00-*.md"))), None)
    return f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").split(":", 1)[-1].strip() if f else d.name


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = ["# الفهرس العام للسلسلة", "",
          "صناعة المتكلّم العربي في ثمانية مجلدات: أربع مراحل، ثم المرجع (الدليل، الجزء الخامس عشر).", ""]
    rows = [["الملف الحالي", "المجلد", "الباب في السلسلة", "ملاحظة"]]
    stage = None
    for vol, name, st, babs, extra in VOLUMES:
        if st != stage:
            md += [f"## {st}", ""]
            stage = st
        md += [f"### المجلد {ORDINAL_F[vol - 1]}: {name}", ""]
        if "الافتتاحية" in extra:
            md.append("- **الافتتاحية**: المقدمة العلمية في سبعة عشر فصلًا، وملحق التحقيق، وثبت المصادر")
            md.append("- **المدخل**: العربية ومستوياتها")
            for unit in ("الافتتاحية", "المدخل"):
                for f in sorted((BOOK / unit).glob("*.md")):
                    rows.append([str(f.relative_to(BOOK)), str(vol), unit, ""])
        for old, new in babs:
            d = bab_dir(old)
            if new is None:
                md.append(f"- **المرجع الأول: {title(d)}** (كان الباب الثالث عشر)")
            else:
                note = f" (كان الباب {ORD[old - 1].replace('-', ' ')})" if new != old else ""
                md.append(f"- **الباب {ORD[new - 1].replace('-', ' ')}: {title(d)}** — المستوى {str(LEVEL[new]).translate(AR)}{note}")
            for k, t in chapters(d).items():
                md.append(f"  - {t}")
            for f in sorted(d.glob("*.md")):
                rows.append([str(f.relative_to(BOOK)), str(vol),
                             "المرجع الأول" if new is None else f"الباب {ORD[new - 1].replace('-', ' ')}",
                             "يُعاد ترقيمه" if new not in (None, old) else ("يخرج من تسلسل الأبواب" if new is None else "")])
        for unit in extra:
            if unit == "الافتتاحية":
                continue
            md.append(f"- **{ 'الملاحق' if unit == 'الملاحق' else 'الخاتمة، والمسرد، والمصادر، وتقرير الجودة'}**")
            for f in sorted((BOOK / unit).glob("*.md")):
                if unit == "الملاحق":
                    md.append(f"  - {f.read_text(encoding='utf-8').splitlines()[0].lstrip('# ').strip()}")
                rows.append([str(f.relative_to(BOOK)), str(vol), unit, ""])
        if vol == 8:
            md.append("- **الفهارس العامة للسلسلة** (تُبنى بعد إخراج المجلدات السبعة)")
        md.append("")
    (OUT / "الفهرس-العام.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    with open(OUT / "جدول-الانتقال.tsv", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write("\t".join(r) + "\n")
    print(len(rows) - 1, "files mapped to 8 volumes")


if __name__ == "__main__":
    main()
