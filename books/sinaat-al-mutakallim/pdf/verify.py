#!/usr/bin/env python3
"""First matching of the opening's citations (Bible, part nine): hadith, athar, scholars' texts and poetry.

For each citation the quotation is read from the manuscript, searched as an exact phrase in the adopted
edition on Shamela (then in the collation edition), the source page is fetched, and the closest span of
the source is aligned with our wording, word by word. The result is a matching report: where the text
was found (book, edition, volume, printed page), how close our wording is, and every word that differs.
Shamela is the means of finding and comparing; the final check is on the adopted edition itself.

    python3 verify.py          writes book/_production/التحقيق/مطابقة-النقول.json and .md
"""
from __future__ import annotations

import difflib
import json
import re
from pathlib import Path

import shamela as S

BOOK = Path(__file__).resolve().parent.parent / "book"
OPEN = BOOK / "الافتتاحية"
OUT = BOOK / "_production" / "التحقيق"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# adopted edition first, then the collation edition (Bible, ch. 43 as revised)
BUKHARI = ["1681", "1284"]          # السلطانية (= طوق النجاة في الجزء والصفحة) ثم التأصيل
MUSLIM = ["1727", "711"]            # عبد الباقي ثم التركية
ABUDAWUD = ["1726", "117359"]       # محيي الدين ثم الأرنؤوط

# (id, file prefix, a phrase that finds the quotation in the manuscript, the search phrase, books, kind)
ITEMS = [
    ("ح١", "04", "بُعثتُ بجوامع الكلم", "بعثت بجوامع الكلم", BUKHARI + MUSLIM, "حديث"),
    ("ح٢", "04", "كان كلامُ رسول الله", "كلاما فصلا يفهمه كل من سمعه", ABUDAWUD, "حديث"),
    ("ح٣", "04", "لو عدّه العادُّ", "لو عده العاد لأحصاه", BUKHARI + MUSLIM, "حديث"),
    ("ح٤", "04", "أعادها ثلاثًا", "أعادها ثلاثا حتى تفهم عنه", BUKHARI, "حديث"),
    ("ح٥", "04", "يتخوّلنا بالموعظة", "يتخولنا بالموعظة في الأيام كراهة السآمة علينا", BUKHARI + MUSLIM, "أثر في صفة الفعل النبوي"),
    ("ح٦", "04", "مَئِنّةٌ من فقهه", "مئنة من فقهه", MUSLIM, "حديث"),
    ("ح٧", "04", "فليقل خيرًا أو ليصمت", "فليقل خيرا أو ليصمت", BUKHARI + MUSLIM, "حديث"),
    ("ح٨", "04", "والكلمة الطيبة صدقة", "والكلمة الطيبة صدقة", BUKHARI + MUSLIM, "حديث"),
    ("ح٩", "04", "إنّ العبد ليتكلّم بالكلمة", "إن العبد ليتكلم بالكلمة من رضوان الله", BUKHARI, "حديث"),
    ("ح١٠", "04", "إنّ الله رفيقٌ", "إن الله رفيق يحب الرفق في الأمر كله", BUKHARI + MUSLIM, "حديث"),
    ("ح١١", "04", "حدّثوا الناس بما يعرفون", "حدثوا الناس بما يعرفون", BUKHARI, "أثر موقوف"),
    ("ح١٢", "04", "ما أنت بمحدّثٍ قومًا", "ما أنت بمحدث قوما حديثا لا تبلغه عقولهم", MUSLIM, "أثر موقوف"),
    ("ح١٣", "07", "يرفع بهذا الكتاب أقوامًا", "إن الله يرفع بهذا الكتاب أقواما", MUSLIM, "حديث"),
    ("ح١٤", "07", "الماهرُ بالقرآن", "الماهر بالقرآن مع السفرة الكرام البررة", MUSLIM + BUKHARI, "حديث"),
    ("ع١", "05", "فمنه مستقيمٌ حسن", "فمنه مستقيم حسن ومحال", ["23018"], "نقل عالم"),
    ("ع٢", "05", "أمّا حدُّها فإنها أصواتٌ", "أصوات يعبر بها كل قوم عن أغراضهم", ["9986"], "نقل عالم"),
    ("ع٣", "05", "والبيانُ اسمٌ جامعٌ", "كشف لك قناع المعنى", ["10614"], "نقل عالم"),
    ("ع٤", "05", "لأنّ مدارَ الأمر", "إنما هو الفهم والإفهام", ["10614"], "نقل عالم"),
    ("ع٥", "05", "ينبغي للمتكلّم أن يعرف أقدارَ", "أن يعرف أقدار المعاني", ["10614"], "نقل عالم"),
    ("ع٦", "05", "واعلم أن ليس النظمُ", "ليس النظم إلا أن تضع كلامك", ["12055"], "نقل عالم"),
    ("ع٧", "05", "وأمّا بلاغة الكلام فهي", "بلاغة الكلام فهي مطابقته لمقتضى الحال", ["7380"], "نقل عالم"),
    ("ع٨", "05", "واعلم أنّ اعتياد اللغة", "اعتياد اللغة يؤثر في العقل", ["11620"], "نقل عالم"),
    ("ع٩", "05", "فإنّ نفس اللغة العربية", "نفس اللغة العربية من الدين", ["11620"], "نقل عالم"),
    ("ع١٠", "05", "ومن العجب أنّ الإنسان يهون", "يهون عليه التحفظ والاحتراز من أكل الحرام", ["98093", "158"], "نقل عالم"),
    ("ع١١", "05", "اعلم أنّ اللغات كلَّها", "اللغات كلها ملكات شبيهة بالصناعة", ["12320"], "نقل عالم"),
    ("ع١٢", "05", "فهو علمٌ بكيفيّةٍ", "علم بكيفية لا نفس كيفية", ["12320"], "نقل عالم"),
    ("ع١٣", "05", "السمعُ أبو الملكات", "أبو الملكات اللسانية", ["12320"], "نقل عالم"),
    ("ش١", "02", "لسانُ الفتى نصفٌ", "لسان الفتى نصف ونصف فؤاده", ["1487", "11253"], "شعر"),
    ("ش٢", "02", "وكائنْ ترى من صامتٍ", "وكائن ترى من صامت لك معجب", ["1487", "11253"], "شعر"),
    ("ش٣", "02", "إنّ الكلامَ لفي الفؤادِ", "إن الكلام لفي الفؤاد وإنما", [], "شعر منسوب"),
]


def quote_from_manuscript(prefix: str, key: str) -> str:
    f = next(OPEN.glob(prefix + "-*.md"))
    for line in f.read_text(encoding="utf-8").splitlines():
        if key in line:
            line = re.sub(r"\[\^\d+\]", "", line.lstrip("> ").strip())
            m = re.search(r"«([^»]+)»", line)
            return (m.group(1) if m else line).replace(" ... ", " ").strip()
    raise KeyError(key)


def best_window(src: str, quote: str) -> tuple[float, str, list]:
    """The span of the source page closest to the quotation, its ratio, and the word differences."""
    sw_raw = src.split()
    sw = [S.plain(w) for w in sw_raw]
    qw = [w for w in S.plain(quote).split() if w]
    n = len(qw)
    best = (0.0, 0, 0)
    for i in range(len(sw)):
        for L in (n - 2, n - 1, n, n + 1, n + 2):
            if L <= 0 or i + L > len(sw):
                continue
            r = difflib.SequenceMatcher(None, qw, [w for w in sw[i:i + L] if w]).ratio()
            if r > best[0]:
                best = (r, i, i + L)
    r, a, b = best
    span_plain = [w for w in sw[a:b] if w]
    diffs = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, qw, span_plain).get_opcodes():
        if op != "equal":
            diffs.append({"نحن": " ".join(qw[i1:i2]), "المصدر": " ".join(span_plain[j1:j2]), "نوع": op})
    return r, " ".join(sw_raw[a:b]), diffs


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = {}
    results = []
    for iid, prefix, key, phrase, books, kind in ITEMS:
        quote = quote_from_manuscript(prefix, key)
        rec = {"id": iid, "kind": kind, "quote": quote, "hits": []}
        for b in books:
            hits = S.search(f'"{phrase}"', [b])
            if not hits:
                continue
            h = hits[0]
            pg = S.page(h["book"], h["page"])
            # a quotation may run over the next page
            nxt = S.page(h["book"], str(int(h["page"]) + 1))
            ratio, span, diffs = best_window(pg["text"] + " " + nxt["text"], quote)
            if b not in cards:
                cards[b] = S.book_card(b)
            num = re.search(r"([٠-٩0-9]{1,5})\s*[-–]\s*\S*\s*(?:حدثنا|حدثني|أخبرنا|وحدثنا|وحدثني|عن)", pg["text"])
            rec["hits"].append({"book": b, "title": cards[b].get("title", ""), "edition": {k: cards[b].get(k, "") for k in
                                ("المحقق", "الناشر", "الطبعة", "عدد الأجزاء")}, "pid": h["page"], "part": pg["part"],
                                "printed_page": pg["printed_page"], "ratio": round(ratio, 3), "span": span, "diffs": diffs,
                                "hadith_no_near": num.group(1) if num else "", "url": f"https://shamela.ws/book/{b}/{h['page']}"})
        results.append(rec)
        best = max((x["ratio"] for x in rec["hits"]), default=0)
        print(iid, kind, "hits:", len(rec["hits"]), "best:", best)
    (OUT / "مطابقة-النقول.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# مطابقة النقول: افتتاحية المجلد الأول (المطابقة الأولى)", "",
          "مطابقةٌ أولى على نسخ المكتبة الشاملة الموافقة للمطبوع، وتبقى المطابقة النهائية على الطبعة المعتمدة نفسها "
          "(الدليل، الجزء التاسع، الباب ٤٨). يُولَّد من `pdf/verify.py`.", ""]
    for rec in results:
        md.append(f"## {rec['id']} — {rec['kind']}")
        md.append(f"**نصّنا:** «{rec['quote']}»")
        if not rec["hits"]:
            md.append("- لم يوجد في الطبعات المحدّدة؛ يُنظر في خريطة نسب القول.")
        for h in rec["hits"]:
            md.append(f"- **{h['title'].replace(' - المكتبة الشاملة', '')}**؛ الجزء: {h['part']}؛ الصفحة: {h['printed_page']}؛ "
                      f"التطابق: {round(h['ratio'] * 100)}٪؛ [الصفحة]({h['url']})")
            md.append(f"  - **في المصدر:** {h['span']}")
            for d in h["diffs"]:
                md.append(f"  - اختلاف: نحن «{d['نحن']}» / المصدر «{d['المصدر']}»")
        md.append("")
    (OUT / "مطابقة-النقول.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
