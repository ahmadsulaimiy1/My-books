#!/usr/bin/env python3
"""Seed the terminology ledger (Bible, part ten, ch. 65) from the glossary, and open the errata ledger (ch. 70).

The glossary gives each term its approved form, definition and English equivalent. First occurrence,
prohibited alternatives and relations are filled by the editor; the few already settled are set here.

    python3 terms.py    writes book/_production/التحقيق/سجل-المصطلحات.tsv and سجل-التصحيحات.tsv
"""
import re
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent / "book"
OUT = BOOK / "_production" / "التحقيق"
FIELDS = ["المصطلح", "التعريف", "أول ورود", "الرسم المعتمد", "المقابل الإنجليزي", "البدائل الممنوعة", "العلاقة المفهومية", "الحالة"]
# settled decisions (Bible: ch. 31 and the terminology of the governing document)
SETTLED = {
    "المتكلم غير الناجح": ("«الفاشل»، «الضعيف»", "أدنى الدرجات الأربع؛ وصفٌ لأداءٍ في مقام لا لشخص"),
    "المتكلم المقبول": ("", "الدرجة الثانية"),
    "المتكلم الناجح": ("", "الدرجة الثالثة، وهي الغاية المطلوبة"),
    "المتكلم الرفيع": ("", "الدرجة الرابعة: الناجح مع لمسة بيانٍ لا تكلّف فيها"),
    "الفصاحة": ("", "لا تُخلط بالبلاغة؛ من المفاهيم الخمسة"),
    "البلاغة": ("", "لا تُخلط بالفصاحة؛ من المفاهيم الخمسة"),
    "الملكة الشفهية": ("«مهارة التحدّث» بديلًا منها", "المرتبة الثانية من المراتب الأربع، وغاية الكتاب"),
}
EXTRA = [  # terms named by the author that the glossary does not yet define
    ("الكلام الناجح", "كلامٌ عربيٌّ صحيحٌ طبيعيٌّ مناسبٌ للمقام يبلغ غرضه", "Successful speech"),
    ("الفصحى المنطوقة", "الفصحى المعاصرة في مقاماتها الشفهية: المحاضرة والندوة والمقابلة والخطبة والحوار", "Spoken MSA"),
    ("العربية المعاصرة", "", "Contemporary Arabic"),
    ("الغرض", "", "Purpose"),
    ("الأثر", "", "Effect"),
    ("الأداء", "المرتبة الثالثة: إخراج الكلام في لحظته تحت ضغط الموقف", "Performance"),
    ("الإيقاع", "", "Rhythm"),
    ("الصحة", "سلامة الجملة في نحوها وصرفها ومعجمها ونطقها؛ من المفاهيم الخمسة", "Correctness"),
    ("الطبيعية", "أن يُقال الكلام كما يقوله أهل العربية حين يتكلّمون به؛ من المفاهيم الخمسة", "Naturalness"),
    ("المناسبة", "ملاءمة الكلام للمخاطب والمقام والغرض؛ من المفاهيم الخمسة", "Appropriateness"),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    g = (BOOK / "الخواتيم" / "المسرد.md").read_text(encoding="utf-8")
    rows = []
    for dt, en, dd in re.findall(r'<dt>([^<]+)<span class="en">([^<]*)</span></dt><dd>(.*?)</dd>', g):
        bad, rel = SETTLED.get(dt.strip(), ("", ""))
        rows.append([dt.strip(), re.sub(r"<[^>]+>", "", dd).strip(), "", dt.strip(), en.strip(), bad, rel,
                     "معرَّف في المسرد؛ يُكمَّل"])
    have = {r[0] for r in rows}
    for t, d, en in EXTRA:
        if t not in have:
            rows.append([t, d, "", t, en, "", "", "يُعرَّف" if not d else "مقترح؛ يُقرّ"])
    with open(OUT / "سجل-المصطلحات.tsv", "w", encoding="utf-8") as fh:
        fh.write("\t".join(FIELDS) + "\n")
        for r in rows:
            fh.write("\t".join(c.replace("\t", " ") for c in r) + "\n")
    errata = OUT / "سجل-التصحيحات.tsv"
    if not errata.exists():
        errata.write_text("\t".join(["الرقم", "الطبعة", "المجلد", "الباب", "الفصل", "الصفحة", "الخطأ", "الصواب",
                                     "السبب", "الواجد", "تاريخ التحقق", "صُحّح في طبعة"]) + "\n", encoding="utf-8")
    print(len(rows), "terms")


if __name__ == "__main__":
    main()
