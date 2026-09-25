#!/usr/bin/env python3
"""ثبت المصادر of the opening: every source its notes cite, with the edition the book uses (Bible, chs. 45 and 74).

Drawn from the Master Bibliography (the titles it marks as used in the opening), completed by the sources added
since, whose editions were read on their Shamela cards or on the scans of the printed books. Arabic sources are
ordered by the name the author is known by, the article set aside; foreign sources follow, by surname.

    python3 thabat.py      writes book/الافتتاحية/91-ثبت-المصادر.md
"""
import csv
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "book" / "_production" / "المصادر" / "قاعدة-المصادر.tsv"
import sys  # noqa: E402
sys.path.insert(0, str(HERE))
from paths import OPENING  # noqa: E402
OUT = OPENING / "91-ثبت-المصادر.md"

# sources cited in the opening that the Master Bibliography does not (yet) mark as used there, or whose edition
# it leaves open; each edition as read on its card or its scan
EXTRA = [
    ("مجمع الملك فهد لطباعة المصحف الشريف", "مصحف المدينة النبوية", "برواية حفص عن عاصم، المدينة المنورة"),
    ("الجاحظ", "البيان والتبيين", "تحقيق عبد السلام محمد هارون، مكتبة الخانجي، القاهرة"),
    ("الشافعي", "الرسالة", "تحقيق وشرح أحمد محمد شاكر، مصطفى البابي الحلبي وأولاده، مصر، الأولى، ١٣٥٨هـ / ١٩٤٠م"),
    ("الغزالي", "المستصفى", "تحقيق محمد عبد السلام عبد الشافي، دار الكتب العلمية، الأولى، ١٤١٣هـ / ١٩٩٣م"),
    ("الشاطبي", "الموافقات", "تحقيق أبي عبيدة مشهور بن حسن آل سلمان، دار ابن عفان، الأولى، ١٤١٧هـ / ١٩٩٧م"),
    ("ابن فارس", "الصاحبي في فقه اللغة العربية ومسائلها وسنن العرب في كلامها", "محمد علي بيضون، الأولى، ١٤١٨هـ / ١٩٩٧م"),
    ("الزركلي", "الأعلام", "دار العلم للملايين، بيروت، الخامسة عشرة، ٢٠٠٢م"),
    ("ضياء الدين ابن الأثير", "المثل السائر في أدب الكاتب والشاعر", "تحقيق أحمد الحوفي وبدوي طبانة، دار نهضة مصر، القاهرة، ٤ أجزاء"),
    ("السعيد محمد بدوي", "مستويات العربية المعاصرة في مصر: بحثٌ في علاقة اللغة بالحضارة", "دار المعارف، القاهرة، ١٩٧٣م"),
    ("الذهبي", "سير أعلام النبلاء", "أشرف على تحقيقه شعيب الأرنؤوط، مؤسسة الرسالة، بيروت، الثانية، ١٤٠٢هـ / ١٩٨٢م، ٢٥ جزءًا"),
    ("ابن جني", "الخصائص", "تحقيق محمد علي النجار، دار الكتب المصرية، القسم الأدبي؛ المكتبة العلمية، ٣ أجزاء"),
    ("عبد القاهر الجرجاني", "دلائل الإعجاز", "تحقيق محمود محمد شاكر أبو فهر، مكتبة الخانجي، القاهرة، رقم الإيداع ١١٨٨٩/٢٠٠٠"),
    ("الخطيب القزويني", "الإيضاح في علوم البلاغة", "تحقيق محمد عبد المنعم خفاجي، المكتبة الأزهرية للتراث، القاهرة، الثالثة، ١٤١٣هـ / ١٩٩٣م"),
    ("أبو هلال العسكري", "كتاب الصناعتين: الكتابة والشعر", "تحقيق علي محمد البجاوي ومحمد أبو الفضل إبراهيم، دار إحياء الكتب العربية (عيسى البابي الحلبي وشركاه)، القاهرة، الأولى، ١٣٧١هـ / ١٩٥٢م"),
    ("ابن تيمية", "اقتضاء الصراط المستقيم", "تحقيق ناصر عبد الكريم العقل، مكتبة الرشد، الرياض، مجلّدان"),
    ("ابن خلكان", "وفيات الأعيان", "تحقيق إحسان عباس، دار صادر، بيروت، ٧ أجزاء"),
    ("العقاد، عباس محمود", "«الحروف اللاتينية»", "مجلة الرسالة، القاهرة، السنة الثانية عشرة، العدد ٥٨٥، ١٨ سبتمبر ١٩٤٤م، ص٧٦١ وما بعدها"),
]
FOREIGN = [
    ("Ferguson, Charles A.", '"Diglossia."', "*Word* 15, no. 2 (1959): 325–340."),
    ("Hymes, Dell", '"On Communicative Competence."', "In J. B. Pride and J. Holmes (eds.), *Sociolinguistics: Selected Readings*. Harmondsworth: Penguin, 1972."),
    ("Sharp, H. (ed.)", "*Selections from Educational Records, Part I: 1781–1839.*", "Calcutta: Superintendent Government Printing, 1920. (Macaulay's Minute, 2 February 1835; Lord Bentinck's Resolution, 7 March 1835.)"),
    ("Spitta-Bey, Wilhelm", "*Grammatik des arabischen Vulgärdialectes von Aegypten.*", "Leipzig: J. C. Hinrichs, 1880."),
    ("Wensinck, A. J., et al.", "*Concordance et indices de la tradition musulmane.*", "Leiden: E. J. Brill."),
]
SKIP_TITLES = ("Diglossia", "On Communicative Competence")     # set among the foreign sources


def tidy(ed):
    """A catalogue card is not a bibliography entry: drop its bookkeeping and keep publisher, place, edition, year, parts."""
    ed = re.sub(r"\s*\((?:متسلسلة الترقيم|الأخير فهارس|آخر ٢ فهارس|الثامن فهارس|[٠-٩]+ والفهارس|وأعادوا طباعتها بالتصوير مِرار|الأولى لدار ابن حزم)\)", "", ed)
    ed = re.sub(r"الجزء: [٠-٩]+ - الطبعة: [٠-٩]+، [٠-٩]+،\s*", "", ed)
    ed = re.sub(r"مجموعة محققين\s*وهم:\s*،", "مجموعة من المحققين،", ed).replace("وهم:،", "،").replace("مجموعة محققين،", "مجموعة من المحققين،").replace("٢. أجزاء", "٢ أجزاء").replace(" م.،", " م،")
    ed = re.sub(r"،\s*٢ أجزاء", "، جزآن", ed)
    ed = re.sub(r"،\s*([٠-٩]+) أجزاء", lambda m: f"، {m.group(1)} أجزاء", ed)
    return re.sub(r"\s+", " ", ed).strip(" ،.")


DEGREE = {"print": "طوبق على المطبوع", "digital": "على نسخةٍ رقمية", "general": "إحالةٌ عامّة"}
FOREIGN_DEGREE = {"Sharp, H. (ed.)": "print", "Spitta-Bey, Wilhelm": "print"}
# the Qur'an was set from the Uthmani text of two digital services; the second editions of the Sahihs and of Abu
# Dawud were used for comparison and grading only
OVERRIDE = {"مصحف المدينة النبوية": "digital"}
BY_EDITION = {("صحيح البخاري", "السلطانية"): "print", ("صحيح البخاري", "التأصيل"): "digital",
              ("صحيح مسلم", "عبد الباقي"): "print", ("صحيح مسلم", "ذهني"): "digital",
              ("سنن أبي داود", "محيي الدين"): "print", ("سنن أبي داود", "الأرنؤوط"): "digital"}
EDITIONS = {}
MULTI = set()   # authors with more than one book in the list: matched by title only


def degree(author, title, edition=""):
    """How far the book was used: matched on the scan of the print, matched on a digital copy, or cited in general."""
    import ledger as L
    if title in OVERRIDE:
        return OVERRIDE[title]
    for (t, mark), deg in BY_EDITION.items():
        if t == title and mark in edition:
            return deg
    found = "general"
    head = " ".join(title.split(":")[0].split("(")[0].split()[:2])
    name = author.split("،")[0].strip()
    for row in L.ROWS:
        who, src, ed = row[5], row[6], row[7]
        by_name = name not in MULTI and (name in src or (name in who and len(name) > 3))
        if not (head in src or by_name):
            continue
        if row[0] and row[0] in L.ON_PRINT:
            return "print"
        if row[10] and row[14] != "incomplete":
            found = "digital"
    return found


def key(name):
    n = re.sub(r"^(ال|ابن |أبو |أبي |ضياء الدين |الخطيب |عبد القاهر )", "", name.strip())
    return re.sub(r"^ال", "", n)


def main():
    rows = {}
    with open(BASE, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if "مستعمَل في الافتتاحية" not in r["حالة الاستعمال"] or r["العنوان"].startswith(SKIP_TITLES):
                continue
            ed = re.sub(r"\s*\[ت [^\]]*\]", "", r["الطبعة (من سجلّ فهرسة)"]).replace("&lt;i&gt;", "").replace("&lt;/i&gt;", "")
            if "تُحدَّد" in ed:
                continue
            title = re.sub(r"\s*\((طوق النجاة|دار التأصيل|ترقيم عبد الباقي|الطبعة التركية|ت\. [^)]*|تاريخ ابن خلدون، ج١|الجواب الكافي|رواية حفص)[^)]*\)", "", r["العنوان"])
            rows[(r["المؤلف"], r["العنوان"])] = (r["المؤلف"], title.strip(), tidy(ed))
    extra_titles = {t.split(":")[0] for _, t, _ in EXTRA}
    rows = {k: v for k, v in rows.items() if v[1].split(":")[0] not in extra_titles or v[0] in ("البخاري", "مسلم", "أبو داود")}
    for a, t, e in EXTRA:
        rows[(a, t)] = (a, t, e)
    ar = sorted(rows.values(), key=lambda x: (key(x[0]), x[1]))
    EDITIONS.update({(a, t): e for a, t, e in ar})
    names = [a.split("،")[0].strip() for a, _, _ in ar]
    MULTI.update(n for n in names if names.count(n) > 1 and n not in ("البخاري", "مسلم", "أبو داود"))
    ar = [(a, t, e + f'. <span class="deg">{DEGREE[degree(a, t, e)]}</span>') for a, t, e in ar]
    md = ["## ثبت المصادر", "", "<!-- sub: ما أُحيل إليه في حواشي الافتتاحية، بالطبعة التي أُحيل إليها -->", "",
          "رُتّبت المصادر العربية على شهرة مؤلّفيها، من غير اعتدادٍ بـ«ال» و«ابن» و«أبي» في أولها، ثم المصادر الأجنبية على أسماء عائلات مؤلّفيها. "
          "وحيث ذُكر للكتاب طبعتان فالأولى للإحالة والثانية للمقابلة.",
          "وليست المصادر كلّها على درجةٍ واحدة من الاستعمال، فبُيّنت درجة كلٍّ منها في آخره: «طوبق على المطبوع» لما رُئي النقل منه "
          "في صفحته من مصوّرة الطبعة المذكورة؛ و«على نسخةٍ رقمية» لما طوبق على نسخةٍ رقميةٍ لتلك الطبعة ولم تُرَ صفحته المطبوعة؛ "
          "و«إحالةٌ عامّة» لما أُحيل إليه بلا نقلٍ منصوص، أو حُكي معناه.", "", "### المصادر العربية", ""]
    md += [f"- **{a}**، {t}، {e}" for a, t, e in ar]
    md += ["", "### المصادر الأجنبية", ""]
    md += [f"- {a.rstrip('.')}. {t} {e} <span class=\"deg\">{DEGREE[FOREIGN_DEGREE.get(a, 'general')]}</span>" for a, t, e in sorted(FOREIGN)]
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(OUT.name, len(ar), "Arabic,", len(FOREIGN), "foreign")


if __name__ == "__main__":
    main()
