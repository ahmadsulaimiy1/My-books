#!/usr/bin/env python3
"""ثبت المصادر of a volume: every source its notes cite, with the edition the book uses (Bible, chs. 45, 74, 112و).

The sources are the titles the Master Bibliography marks as cited in the volume (its field «المجلدات», set when the
volume's notes are set), completed by the few the base does not hold (OUTSIDE). The edition is the base's catalogue
record, or, where that record is open or is not the edition cited, the edition read on the book's card or on the scan
of the print (EDITION). No thabat holds a book its notes do not cite, and no cited book is left out: a title the
volume cites whose edition is still open stops the build. Arabic sources are ordered by the name the author is known
by, the article set aside; foreign sources follow, by surname.

    python3 thabat.py [N]     writes the thabat of volume N (the first by default) where that volume keeps it
"""
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "book" / "_production" / "المصادر" / "قاعدة-المصادر.tsv"
sys.path.insert(0, str(HERE))
from paths import OPENING  # noqa: E402
from volumes import ORD, vol_folder  # noqa: E402


def volume_name(n):
    return "المجلد " + ORD[n - 1]


def out_of(n):
    """Where a volume keeps its thabat: the first beside the opening's appendix, the others among their closings."""
    return OPENING / "91-ثبت-المصادر.md" if n == 1 else vol_folder(n) / "الخواتيم" / "ثبت-المصادر.md"


# where the base's catalogue record is open, or is not the edition the notes cite: the edition as read on its card
# or on its scan
EDITION = [
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
]
# sources the notes cite that the base does not hold (an article, a collection of records): (volumes, author, title,
# edition); to be entered in the base when it is next revised
OUTSIDE = [
    (("الأول",), "العقاد، عباس محمود", "«الحروف اللاتينية»", "مجلة الرسالة، القاهرة، السنة الثانية عشرة، العدد ٥٨٥، ١٨ سبتمبر ١٩٤٤م، ص٧٦١ وما بعدها"),
]
# the foreign sources as the thabat sets them: those the base holds, by the base's title; then those it does not
FOREIGN = {
    "Diglossia": ("Ferguson, Charles A.", '"Diglossia."', "*Word* 15, no. 2 (1959): 325–340."),
    "On Communicative Competence": ("Hymes, Dell", '"On Communicative Competence."', "In J. B. Pride and J. Holmes (eds.), *Sociolinguistics: Selected Readings*. Harmondsworth: Penguin, 1972."),
    "What Is Educated Spoken Arabic?": ("Mitchell, T. F.", '"What Is Educated Spoken Arabic?"', "*International Journal of the Sociology of Language* 61 (1986): 7–32."),
}
FOREIGN_OUTSIDE = [
    (("الأول",), "Sharp, H. (ed.)", "*Selections from Educational Records, Part I: 1781–1839.*", "Calcutta: Superintendent Government Printing, 1920. (Macaulay's Minute, 2 February 1835; Lord Bentinck's Resolution, 7 March 1835.)"),
    (("الأول",), "Spitta-Bey, Wilhelm", "*Grammatik des arabischen Vulgärdialectes von Aegypten.*", "Leipzig: J. C. Hinrichs, 1880."),
    (("الأول",), "Wensinck, A. J., et al.", "*Concordance et indices de la tradition musulmane.*", "Leiden: E. J. Brill."),
]


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


def short(title):
    return re.sub(r"^كتاب ", "", title.split(":")[0].split("(")[0].strip())


def edition_for(author, title):
    """The EDITION entry for a base title: the same book (short title) by the same author."""
    for a, t, e in EDITION:
        same_book = short(t) == short(title) or short(title).startswith(short(t)) or short(t).startswith(short(title))
        if same_book and (a.split("،")[0] in author or author in a):
            return a, t, e
    return None


def cited(n):
    """The base's titles the notes of volume n cite."""
    name = volume_name(n)
    with open(BASE, encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh, delimiter="\t") if name in [v.strip() for v in r["المجلدات"].split("،")]]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    ord_ = ORD[n - 1]
    rows, foreign, open_ = {}, [], []
    for r in cited(n):
        author, title = r["المؤلف"], r["العنوان"]
        if author.isascii():
            if title not in FOREIGN:
                open_.append(f"{author}, {title}: no form in FOREIGN")
                continue
            foreign.append(FOREIGN[title])
            continue
        e = edition_for(author, title)
        if e:
            rows[(e[0], e[1])] = e
            continue
        ed = re.sub(r"\s*\[ت [^\]]*\]", "", r["الطبعة (من سجلّ فهرسة)"]).replace("&lt;i&gt;", "").replace("&lt;/i&gt;", "")
        if "تُحدَّد" in ed:
            open_.append(f"{r['الرقم']} {author}، {title}: the edition is still open")
            continue
        title = re.sub(r"\s*\((طوق النجاة|دار التأصيل|ترقيم عبد الباقي|الطبعة التركية|ت\. [^)]*|تاريخ ابن خلدون، ج١|الجواب الكافي|رواية حفص)[^)]*\)", "", title)
        rows[(author, r["العنوان"])] = (author, title.strip(), tidy(ed))
    if open_:
        raise SystemExit("the thabat of " + volume_name(n) + " cannot be set:\n  " + "\n  ".join(open_))
    for vols, a, t, e in OUTSIDE:
        if ord_ in vols:
            rows[(a, t)] = (a, t, e)
    foreign += [(a, t, e) for vols, a, t, e in FOREIGN_OUTSIDE if ord_ in vols]
    if not rows and not foreign:
        raise SystemExit(volume_name(n) + ": the base marks no title as cited in its notes")
    ar = sorted(rows.values(), key=lambda x: (key(x[0]), x[1]))
    EDITIONS.update({(a, t): e for a, t, e in ar})
    names = [a.split("،")[0].strip() for a, _, _ in ar]
    MULTI.update(x for x in names if names.count(x) > 1 and x not in ("البخاري", "مسلم", "أبو داود"))
    ar = [(a, t, e + f'. <span class="deg">{DEGREE[degree(a, t, e)]}</span>') for a, t, e in ar]
    md = ["## ثبت المصادر", "", "<!-- sub: ما أُحيل إليه في حواشي هذا المجلد، بالطبعة التي أُحيل إليها -->", "",
          "رُتّبت المصادر العربية على شهرة مؤلّفيها، من غير اعتدادٍ بـ«ال» و«ابن» و«أبي» في أولها، ثم المصادر الأجنبية على أسماء عائلات مؤلّفيها. "
          "وحيث ذُكر للكتاب طبعتان فالأولى للإحالة والثانية للمقابلة.",
          "وليست المصادر كلّها على درجةٍ واحدة من الاستعمال، فبُيّنت درجة كلٍّ منها في آخره: «طوبق على المطبوع» لما رُئي النقل منه "
          "في صفحته من مصوّرة الطبعة المذكورة؛ و«على نسخةٍ رقمية» لما طوبق على نسخةٍ رقميةٍ لتلك الطبعة ولم تُرَ صفحته المطبوعة؛ "
          "و«إحالةٌ عامّة» لما أُحيل إليه بلا نقلٍ منصوص، أو حُكي معناه.", "", "### المصادر العربية", ""]
    md += [f"- **{a}**، {t}، {e}" for a, t, e in ar]
    md += ["", "### المصادر الأجنبية", ""]
    md += [f"- {a.rstrip('.')}. {t} {e} <span class=\"deg\">{DEGREE[FOREIGN_DEGREE.get(a, 'general')]}</span>" for a, t, e in sorted(foreign)]
    out = out_of(n)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(volume_name(n) + ":", out.relative_to(HERE.parent), len(ar), "Arabic,", len(foreign), "foreign")


if __name__ == "__main__":
    main()
