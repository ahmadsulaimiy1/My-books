#!/usr/bin/env python3
"""The series as fixed after the manuscript was complete (Bible, chs. 112c–112d): the authoritative map.

Eleven volumes. Ten carry the programme in four stages and thirteen abwab, numbered 1–13 across the series; a level
is always the number of its bab. The eleventh, «مرجع المتكلّم العربي», is a reference outside both numberings.
Every tool that needs the structure reads it from here; the files live under book/<volume folder>/<unit folder>/.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"

ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي عشر", "الثاني عشر", "الثالث عشر"]
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
STAGES = {1: "التأسيس", 2: "التواصل", 3: "المنصّات", 4: "التمكين"}


def dash(ordinal):
    return ordinal.replace(" ", "-")


def bab_folder(n):
    return "الباب-" + dash(ORD[n - 1])


REFERENCE_FIRST = "المرجع-الأول-بنك-الأخطاء"

# units: ("opening",) · ("intro",) · ("bab", n) · ("program",) the pronunciation programme · ("reference",) the error
# bank · ("app", letter) · ("closing",)
# · ("back", stem) glossary and sources; a volume whose notes cite sources closes on its thabat (thabat.py)
VOLUMES = [
    dict(n=1, name="الأصول", stage=1, units=[("opening",), ("intro",), ("bab", 1)],
         sentence="ما الكلام الناجح، ولماذا يُتعلَّم صناعةً: المقدمة العلمية، ثم معايير الكلام الخمسة، وأسئلته الستة، وطريق الملكة."),
    dict(n=2, name="اللسان", stage=1, units=[("bab", 2), ("program",), ("back", "ثبت-المصادر")],
         sentence="صحّة الصوت الذي يحمل الكلام، ثم برنامجٌ يوميٌّ يحفظها ثلاثين يومًا."),
    dict(n=3, name="العبارة", stage=1, units=[("bab", 3), ("back", "ثبت-المصادر")],
         sentence="هل جملتي عربيةٌ طبيعية؟ سلامة الجملة المنطوقة: ما يظهر من الإعراب، والصرف، والمطابقة، ومقاومة الترجمة "
                  "الحرفية وأثر اللغة الأم، والحشو، واختيار الكلمة، وطول الجملة."),
    dict(n=4, name="البيان", stage=1, units=[("bab", 4), ("back", "ثبت-المصادر")],
         sentence="هل كلامي مرتّبٌ مبين؟ بناء الكلام قبل النطق، وأول عشر ثوانٍ، والافتتاح والتعريف بالنفس والانتقال والخاتمة، "
                  "ثم المعاني والبيان والبديع والاقتباس تطبيقًا."),
    dict(n=5, name="المقام", stage=2, units=[("bab", 5), ("back", "ثبت-المصادر")],
         sentence="هل أعرف لمن أتكلّم وكيف؟ خريطة المتحدّثين والمخاطَبين، واتجاهات الخطاب، ومختبر ثلاثين موقفًا."),
    dict(n=6, name="الأدب", stage=2, units=[("bab", 6), ("back", "ثبت-المصادر")],
         sentence="هل يحبّني السامع ويحترمني؟ أفعال الأدب: السلام والإنصات، والشكر والدعاء، والطلب والرفض، والاعتذار والتهنئة "
                  "والتعزية، وأدب الخلاف، ولغة الجسد."),
    dict(n=7, name="الحوار", stage=2, units=[("bab", 7), ("back", "ثبت-المصادر")],
         sentence="هل أُحسن السؤال والجواب والاعتراض؟ الكلام المتبادل: السؤال، والجواب، والاستيضاح، والمداخلة، والإقناع، "
                  "والمناظرة، والنقد والنصيحة."),
    dict(n=8, name="المجالس والمنبر", stage=3, units=[("bab", 8), ("bab", 9), ("back", "ثبت-المصادر")],
         sentence="الكلام أمام الجماعة، من الحلقة إلى الجمهور: أدب مجلس العلم ومجالس الجامعة والمناسبات، ثم الخطبة والمحاضرة "
                  "والكلمة وعرض البحث."),
    dict(n=9, name="المؤسسة", stage=3, units=[("bab", 10), ("back", "ثبت-المصادر")],
         sentence="الكلام الذي يُكتب ويُحاسَب عليه: المقابلة، وإدارة الاجتماع، وخطاب المدير والموظف."),
    dict(n=10, name="التمكين", stage=4, units=[("bab", 11), ("bab", 12), ("bab", 13), ("closing",), ("back", "ثبت-المصادر")],
         sentence="الكلام حيث لا يُحتمل الخطأ ولا الإعادة: أمام الكاميرا، وباسم الجهة، وبلا إعداد؛ ثم خاتمة الكتاب."),
    dict(n=11, name="مرجع المتكلّم العربي", subtitle="بنك الأخطاء والتعبيرات والنماذج", stage=None,
         units=[("reference",), ("app", "أ"), ("app", "ب"), ("app", "ج"), ("app", "د"), ("back", "المسرد"),
                ("back", "المصادر-والمراجع")],
         sentence="ما يُرجع إليه ولا يُقرأ متتابعًا: ما يُقال (التعبيرات والنماذج)، وما لا يُقال (بنك الأخطاء ومعجم الترجمة "
                  "الحرفية)، وأين يوجد كلّ شيء (المسرد والفهارس العامة). خارج ترقيم الأبواب والمستويات."),
]
APPENDIX = {"أ": "المعجم التطبيقي (البنوك التعبيرية)", "ب": "معجم أخطاء الترجمة الحرفية",
            "ج": "أخطاء قد تظهر عند بعض المتعلّمين", "د": "النماذج الكاملة"}
# the pronunciation programme closes volume two as the appendix of its bab (Bible, ch. 112d)
PROGRAM = "ملحق الباب الثاني: برنامج النطق اليومي في ثلاثين يومًا"
COMPANIONS = {"سكريبتات-الحلقات": "سكريبتات الحلقات", "بنك-الاختبارات-ودليل-المعلم": "بنك الاختبارات ودليل المعلم"}


def vol_folder(n):
    return BOOK / ("المجلد-" + dash(ORD[n - 1] if n <= 10 else "الحادي عشر"))


VOL_OF_BAB = {u[1]: v["n"] for v in VOLUMES for u in v["units"] if u[0] == "bab"}


def bab_dir(n):
    return vol_folder(VOL_OF_BAB[n]) / bab_folder(n)


def unit_dir(vol, u):
    base = vol_folder(vol)
    return {"opening": base / "الافتتاحية", "intro": base / "المدخل", "reference": base / REFERENCE_FIRST,
            "app": base / "الملاحق", "program": base / "الملاحق", "closing": base / "الخاتمة", "back": base / "الخواتيم"}.get(u[0]) \
        if u[0] != "bab" else base / bab_folder(u[1])


def reading_order(f):
    """A file split in parts reads in its order: «…-برنامج-النطق.md» before «…-برنامج-النطق-٢.md» and «-٣»."""
    m = re.match(r"^(.*?)-([٠-٩]+)$", f.stem)
    return (m.group(1), int(m.group(2).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")))) if m else (f.stem, 1)


def unit_files(vol, u):
    d = unit_dir(vol, u)
    if u[0] == "app":
        return sorted((f for f in d.glob("*.md") if f.stem.split("-")[1] == u[1]), key=reading_order)
    if u[0] == "program":
        return sorted(d.glob("ملحق-الباب-الثاني-*.md"), key=reading_order)
    if u[0] == "back":
        return [d / f"{u[1]}.md"]
    return sorted(d.glob("*.md"), key=reading_order)
