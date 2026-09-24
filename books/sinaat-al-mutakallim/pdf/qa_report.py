#!/usr/bin/env python3
"""Write the book's quality-control report (book/الخواتيم/تقرير-ضبط-الجودة.md) from the manuscript.

Every figure in the report is counted from the Markdown sources at build time; nothing is asserted
by hand. Run before book_build.py:

    python3 qa_report.py
"""
from __future__ import annotations

import collections
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
OUT = BOOK / "الخواتيم" / "تقرير-ضبط-الجودة.md"

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
# chapter counts per bab (Bible book map)
EXPECTED = {1: 6, 2: 12, 3: 9, 4: 10, 5: 9, 6: 9, 7: 7, 8: 5, 9: 5, 10: 5, 11: 4, 12: 3, 13: 8, 14: 3}
ORD = ["", "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي عشر", "الثاني عشر", "الثالث عشر", "الرابع عشر"]
BANNED = ["في عالمنا المتسارع", "لا شك أن", "مما لا ريب فيه", "مفتاح النجاح", "في هذا الفصل سوف نستعرض"]
# the ten dialogues required by the production directive: (label, designated chapter, words that
# must appear in that chapter besides a dialogue table)
REQUIRED = [
    ("خريج في مقابلة جامعية", (10, 2), ["مقابلة", "خريج"]),
    ("طالب يزور عالمًا كبيرًا", (8, 1), ["زيارة", "طالب"]),
    ("موظف جديد يلتقي مدير الجامعة", (5, 3), ["موظف", "مدير الجامعة"]),
    ("معلم يصحح خطأ طالب", (7, 7), ["معلم", "طالب"]),
    ("باحث يعرض بحثه", (9, 4), ["عرض", "بحث"]),
    ("مقدّم يفتتح مؤتمرًا", (9, 3), ["مؤتمر", "افتتاح"]),
    ("صحفي يحاور عالمًا", (11, 3), ["صحفي", "عالم"]),
    ("مدير يخاطب موظفًا مخطئًا", (10, 4), ["مدير", "موظف"]),
    ("مخالفة عالم كبير بأدب", (6, 6), ["شيخ", "خلاف"]),
    ("زائر يحضر مجلس علم أول مرة", (8, 1), ["مجلس", "أول مرة"]),
]


def ar(n):
    return f"{n:,}".replace(",", "٬").translate(AR)


def files():
    return sorted(p for p in BOOK.rglob("*.md") if "_production" not in p.parts and p.name != "README.md"
                  and "التكليف" not in p.name and "الواجهة" not in p.name and p.parent.name != "الخواتيم")


def bab_of(p: Path):
    for n in range(14, 0, -1):
        if f"الباب-{ORD[n].replace(' ', '-')}" in p.parts:
            return n
    return None


def main():
    fs = files()
    texts = {f: f.read_text(encoding="utf-8") for f in fs}
    words = sum(len(t.split()) for t in texts.values())
    chapters = collections.defaultdict(str)
    for f, t in texts.items():
        b = bab_of(f)
        m = re.match(r"ف(\d+)", f.name)
        if b and m:
            chapters[(b, int(m.group(1)))] += t
    complete = {k for k, t in chapters.items()
                if re.search(r"^#+\s*الخلاصة", t, re.M) and re.search(r"^#+\s*معيار الإتقان", t, re.M)}
    per_bab = collections.Counter(b for (b, _) in complete)
    all_text = "\n".join(texts.values())
    examples = len(re.findall(r"\[م[٠-٩]+-ب[٠-٩]+-ف[٠-٩]+-مث[٠-٩]+\]", all_text))
    tiers = {k: len(re.findall(rf"^\*\*{k}", all_text, re.M)) for k in "①②③④"}
    dialogues = len(re.findall(r"^\|\s*السطر\s*\|\s*المتكلم", all_text, re.M))
    improved = len(re.findall(r"^#+\s*النسخة المحسّنة", all_text, re.M))
    changed = len(re.findall(r"^#+\s*ماذا تغيّر", all_text, re.M))
    ctx = len(re.findall(r"▣", all_text))
    exercises = len(re.findall(r"^#+\s*تدريبات الفصل", all_text, re.M))
    ayat = len(re.findall(r"﴿", all_text))
    cards = len(re.findall(r"^\*\*الرمز والخطورة:?\*\*|^-\s*\*\*الرمز والخطورة", all_text, re.M))
    tags = collections.Counter()
    for m in re.finditer(r"\*\[([^\]]{2,160})\]\*", all_text):
        s = m.group(1)
        if "يحتاج إلى تحقق" in s:
            tags["يحتاج إلى تحقق (مصدر أو صفحة أو رقم)"] += 1
        elif "يُعرض على" in s:
            tags["يُعرض على مراجع مختص"] += 1
        elif "استنباط تربوي" in s:
            tags["استنباط تربوي"] += 1
        elif "تحليل حديث" in s:
            tags["تحليل حديث"] += 1
        elif "أداة تدريبية" in s:
            tags["أداة تدريبية من إنشاء الكتاب"] += 1
        else:
            tags["وسوم أخرى"] += 1
    banned = sum(len(re.findall(b, all_text)) for b in BANNED)
    middot = len(re.findall(r"[٠-٩]\s?·|·\s?[٠-٩]", all_text))
    wrong_tier = len(re.findall(r"المتكلم المتقن", all_text))
    h5 = sum(1 for t in texts.values() if re.search(r"^#####", t, re.M))

    def where(chapter, words):
        b, c = chapter
        txt = chapters.get(chapter, "")
        ok = bool(txt) and re.search(r"^\|\s*السطر\s*\|", txt, re.M) and all(w in txt for w in words)
        return f"الباب {ORD[b]}، الفصل {ORD[c]}", ("موجود" if ok else "لم يكتمل بعد")

    total_expected = sum(EXPECTED.values())
    lines = [
        "# تقرير المراجعة وضبط الجودة",
        "",
        "هذا التقرير جزء من طبعة المراجعة. كُتبت أرقامه كلها آليًّا من ملفات الكتاب نفسها عند إخراجه، ولم يُدخل منها شيء باليد. "
        "والغرض منه أن ترى لجنة المراجعة العلمية ما فُحص، وما بقي عليها أن تفحصه.",
        "",
        "## أولًا: الاكتمال",
        "",
        f"- عدد كلمات الكتاب (المتن والفواتح والملاحق، دون ملفات الإنتاج): **{ar(words)}** كلمة تقريبًا.",
        f"- الفصول المكتملة بتشريحها التام (الخلاصة ومعيار الإتقان): **{ar(len(complete))}** من **{ar(total_expected)}** فصلًا في خريطة الكتاب.",
        "",
        "| الباب | الفصول المكتملة | فصول الخريطة |",
        "|---|---|---|",
    ]
    for b in range(1, 15):
        lines.append(f"| الباب {ORD[b]} | {ar(per_bab.get(b, 0))} | {ar(EXPECTED[b])} |")
    lines += [
        "",
        "## ثانيًا: المادة التطبيقية",
        "",
        "| العنصر | العدد |",
        "|---|---|",
        f"| أمثلة مرقّمة (بالرمز [م-ب-ف-مث]) | {ar(examples)} |",
        f"| نماذج «المتكلم غير الناجح» ① | {ar(tiers['①'])} |",
        f"| نماذج «المتكلم المقبول» ② | {ar(tiers['②'])} |",
        f"| نماذج «المتكلم الناجح» ③ | {ar(tiers['③'])} |",
        f"| نماذج «المتكلم الرفيع» ④ | {ar(tiers['④'])} |",
        f"| بطاقات المقام | {ar(ctx)} |",
        f"| حوارات مجدولة (بأرقام الأسطر) | {ar(dialogues)} |",
        f"| نسخ محسّنة للحوارات | {ar(improved)} |",
        f"| جداول «ماذا تغيّر؟» | {ar(changed)} |",
        f"| مجموعات «تدريبات الفصل» | {ar(exercises)} |",
        f"| بطاقات بنك الأخطاء | {ar(cards)} |",
        f"| مواضع الآيات | {ar(ayat)} |",
        "",
        "## ثالثًا: الحوارات العشرة المطلوبة في التكليف",
        "",
        "| الحوار | موضعه | الحال |",
        "|---|---|---|",
    ]
    for label, chapter, words in REQUIRED:
        loc, state = where(chapter, words)
        lines.append(f"| {label} | {loc} | {state} |")
    lines += [
        "",
        "## رابعًا: الأمانة العلمية",
        "",
        "لم يُنسب قول إلى قائله إلا بعد التحقق. وما لم تُطابَق صفحته أو رقمه على الطبعة المعتمدة بقي عليه وسمٌ ظاهر. "
        "وهذه الوسوم كلها في المتن، ويجب أن تمر عليها لجنة المراجعة واحدًا واحدًا قبل طبعة النشر:",
        "",
        "| الوسم | عدد المواضع |",
        "|---|---|",
    ]
    for k, v in tags.most_common():
        lines.append(f"| {k} | {ar(v)} |")
    lines += [
        "",
        "## خامسًا: الفحوص الآلية للأسلوب",
        "",
        "| الفحص | النتيجة |",
        "|---|---|",
        f"| العبارات الممنوعة في دليل الأسلوب | {ar(banned)} موضعًا |",
        f"| نقطة وسطى «·» بجوار رقم مشرقي | {ar(middot)} |",
        f"| تسمية الدرجة الثالثة «المتقن» بدل «الناجح» | {ar(wrong_tier)} |",
        f"| عناوين من المستوى الخامس (#####) | {ar(h5)} ملفًا |",
        "",
        "## سادسًا: الإخراج",
        "",
        "- **الحروف:** كل حرف في الملف مضمَّن من العائلات المعتمدة في قانون الحرف، ويتوقف التوليد آليًّا إن دخله حرف من خطوط النظام أو حرف بصيغة Type 3.",
        "- **الأرقام:** يُرفض التوليد إن وقعت نقطة وسطى بجوار رقم مشرقي.",
        "- **الإشارات المرجعية:** لكل جزء وباب وفصل وموضوع رئيس علامة في فهرس الملف الجانبي، وتُصحَّح عناوينها لتُقرأ من اليمين.",
        "- **أرقام الصفحات في الفهرس:** تُحسب في مرور أول وتُثبَّت في مرور ثانٍ، ويتوقف التوليد إن اختلف عدد الصفحات بين المرورين.",
        "- **بيانات الملف:** العنوان والمؤلف والموضوع، واللغة العربية، واتجاه القراءة من اليمين.",
        "",
        "## سابعًا: ما بقي على لجنة المراجعة",
        "",
        "1. مطابقة كل نقل موسوم بـ«يحتاج إلى تحقق» على طبعته المعتمدة، ثم حذف الوسم.",
        "2. عرض المواضع الموسومة بـ«يُعرض على…» على المختص المسمّى في الوسم (الأصوات، الشريعة، اللغة).",
        "3. المراجعات الإحدى عشرة في الباب الثامن عشر من الدليل، بلجنة بشرية، فصلًا فصلًا.",
        "4. تسجيل النماذج الناجحة تسجيلًا مرجعيًّا بصوت متقن، للمهام الصوتية.",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT, words, len(complete), "/", total_expected)


if __name__ == "__main__":
    main()
