#!/usr/bin/env python3
"""The gate before the files move (Bible, ch. 112b): the map of the volumes, measured, and the two questions put to
each volume — can it be defined in one scientific sentence, and what function is lost if it is removed?

Pages are estimated from words at a density measured, not assumed: sample chapters of six different kinds were set
in the book's own layout (opening.py) and counted — 185 words a page at the opening's body size (13.2pt/1.85),
208 at the student book's (12pt/1.8, Bible part six). Each chapter adds half a page (it opens a page), each chapter
of the program two (its title page), each volume its front matter and its indices.

    python3 gate.py      writes book/_production/هندسة-السلسلة/{خريطة-المجلدات.md, خريطة-المجلدات.json}
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
OUT = BOOK / "_production" / "هندسة-السلسلة"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي عشر", "الثاني عشر", "الثالث عشر", "الرابع عشر"]
DIRS = [o.replace(" ", "-") for o in ORD]

# measured words a page (six sample chapters: sounds and tables, grammar, the situations lab, manners and dialogue,
# the interview, the error cards); see the docstring
DENSITY = {"student": 208, "opening": 185}
SAMPLES = [("ب٢/ف١", "أصوات وجداول", 8755, 44, 47), ("ب٣/ف٢", "نحو وأمثلة", 12236, 61, 68),
           ("ب٥/ف٩", "مختبر مواقف", 8013, 37, 45), ("ب٦/ف٦", "آداب وحوار", 12994, 61, 66),
           ("ب١٠/ف١", "مقابلة وحوار ممتد", 17550, 85, 94), ("ب١٣/ف٤", "بطاقات أخطاء", 6985, 33, 39)]
OPENING_PAGES = 194          # the opening as set (front matter, seventeen chapters, appendix, bibliography)
FRONT, INDEX_MIN, SERIES_INDEX = 12, 16, 70

QUESTION = {1: "ما الكلام الناجح؟", 2: "هل صوتي عربيٌّ واضح؟", 3: "هل جملتي عربيةٌ طبيعية؟",
            4: "هل كلامي مرتّبٌ مبين، له افتتاحٌ وخاتمة؟", 5: "هل أعرف لمن أتكلّم وكيف؟", 6: "هل يحبّني السامع ويحترمني؟",
            7: "هل أُحسن السؤال والجواب والاعتراض؟", 8: "هل أُحسن الدخول إلى مجلس العلم والكلام فيه؟",
            9: "هل أُحسن الخطبة والمحاضرة والكلمة أمام الجمع؟", 10: "هل أجتاز المقابلة وأدير الاجتماع؟",
            11: "هل أتكلّم أمام الكاميرا والمذياع؟", 12: "هل أُحسن الخطاب الرسمي والتحفّظ والتفاوض؟",
            14: "هل أرتجل في موقفٍ لم أستعدّ له؟", 13: "أين أخطئ بالضبط، وكم تبلغ خطورة خطئي؟"}
APPENDIX = {"أ": "المعجم التطبيقي (البنوك التعبيرية)", "ب": "معجم أخطاء الترجمة الحرفية", "ج": "أخطاء قد تظهر عند بعض المتعلّمين",
            "د": "نصوص الحلقات", "هـ": "النماذج الكاملة", "و": "برنامج النطق اليومي في ثلاثين يومًا", "ز": "أدوات التقويم"}


def words(p):
    return len(p.read_text(encoding="utf-8").split())


def bab(n):
    d = next(BOOK.glob("الجزء-*/الباب-" + DIRS[n - 1]))
    chs = {}
    for f in sorted(d.glob("*.md")):
        m = re.match(r"ف(\d+)", f.name)
        k = int(m.group(1)) if m else 0
        c = chs.setdefault(k, {"title": f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip(), "words": 0})
        c["words"] += words(f)
    title = chs.pop(0)["title"] if 0 in chs else d.name
    opener = sum(words(f) for f in d.glob("00-*.md"))
    return {"title": title, "opener": opener, "chapters": [{"n": k, **v} for k, v in sorted(chs.items())]}


def appendix(letter):
    fs = [f for f in (BOOK / "الملاحق").glob("*.md") if f.stem.split("-")[1] == letter]
    return {"title": "ملحق " + letter + ": " + APPENDIX[letter], "words": sum(words(f) for f in fs), "files": [f.name for f in fs]}


def end(stem):
    f = BOOK / "الخواتيم" / f"{stem}.md"
    return {"title": f.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip(), "words": words(f)}


def pages(w, d, chapters=0, openers=0):
    return w / d + .5 * chapters + 2 * openers


# ------------------------------------------------------------------ the two models, and what each volume is for
# units: ("opening",) · ("intro",) · ("bab", present number, number in the series) · ("app", letter) · ("end", stem)
MODELS = {
    "A": {"name": "ثمانية مجلدات (القرار كما اتُّخذ)", "volumes": [
        dict(name="الأصول", stage="التأسيس", units=[("opening",), ("intro",), ("bab", 1, 1)],
             sentence="ما الكلام الناجح، ولماذا يُتعلَّم صناعةً: المقدمة العلمية، ثم معايير الكلام الخمسة، وأسئلته الستة، وطريق الملكة.",
             adds="الأصل النظري والأدوات التي تطبّقها المجلدات كلّها: المعايير، والنموذج السداسي، وطريق السماع.",
             lost="يفقد القارئ الميزان الذي يُقاس به كل كلامٍ بعده، والحجّة العلمية للصناعة كلّها."),
        dict(name="اللسان", stage="التأسيس", units=[("bab", 2, 2)],
             sentence="صحّة الصوت الذي يحمل الكلام: المخارج والصفات، والأصوات الحرجة، والوقف والنفَس، والصوت الإنساني.",
             adds="وحده يدرّب النطق والصوت؛ ولا يعيده مجلدٌ بعده إلا مرجعًا.",
             lost="يضيع تدريب النطق كلّه، وهو أول ما يسمعه السامع."),
        dict(name="العبارة والبيان", stage="التأسيس", units=[("bab", 3, 3), ("bab", 4, 4)],
             sentence="من الجملة إلى الكلام: سلامة الجملة وطبيعيتها، ثم ترتيب الكلام وافتتاحه وانتقاله وختامه وبلاغته التطبيقية.",
             adds="صناعة الجملة ثم صناعة الكلام؛ وهما وجها العنوان: من سلامة اللسان إلى حسن البيان.",
             lost="يضيع ما بين الصوت والمقام: الجملة الطبيعية، والكلام المرتّب."),
        dict(name="المقام", stage="التواصل", units=[("bab", 5, 5)],
             sentence="لمن أتكلّم وكيف: خريطة المتحدّثين والمخاطَبين، واتجاهات الخطاب، ومختبر ثلاثين موقفًا.",
             adds="يحوّل «مَن» و«لمن» من سؤالين إلى خريطةٍ للناس.",
             lost="يضيع اختيار اللسان المناسب للشخص والمنزلة."),
        dict(name="الأدب والحوار", stage="التواصل", units=[("bab", 6, 6), ("bab", 7, 7)],
             sentence="الكلام بين اثنين: أفعال الأدب التي تحفظ العلاقة، ثم أبنية الحوار التي يتبادل بها المعنى.",
             adds="أفعال المخاطبة (السلام والطلب والرفض والاعتذار والخلاف)، ثم السؤال والجواب والمداخلة والإقناع والمناظرة.",
             lost="يضيع أدب المخاطبة والكلام المتبادل معًا."),
        dict(name="المنصّات", stage="المنصّات", units=[("bab", 8, 8), ("bab", 9, 9), ("bab", 10, 10)],
             sentence="الكلام في المقامات المنظّمة: المجلس، والمنبر، والمؤسسة.",
             adds="ينقل ما سبق إلى أماكنه: مجلس العلم، والخطبة والمحاضرة، والمقابلة والاجتماع.",
             lost="يضيع الأداء في المقامات العامة والمؤسسية."),
        dict(name="التمكين", stage="التمكين", units=[("bab", 11, 11), ("bab", 12, 12), ("bab", 14, 13)],
             sentence="الكلام حيث لا يُحتمل الخطأ ولا الإعادة: أمام الكاميرا، وباسم الجهة، وبلا إعداد.",
             adds="الإعلام، والخطاب الرسمي والتفاوض، ثم الملكة: الارتجال والمحاكاة ومشروع التخرّج.",
             lost="يضيع أعلى المقامات ضغطًا، ويضيع الختام الذي يمتحن ما قبله كلّه."),
        dict(name="المرجع", stage="المرجع", units=[("bab", 13, None), ("app", "أ"), ("app", "ب"), ("app", "ج"), ("app", "د"),
                                                   ("app", "هـ"), ("app", "و"), ("app", "ز"), ("end", "00-خاتمة-الكتاب"),
                                                   ("end", "المسرد"), ("end", "المصادر-والمراجع"), ("end", "تقرير-ضبط-الجودة")],
             sentence="ما يُرجع إليه ولا يُقرأ متتابعًا: ما يُقال، وما لا يُقال، وأين يوجد كلّ شيء في السلسلة.",
             adds="بنك الأخطاء، والبنوك التعبيرية، والمعاجم، والنماذج، والفهارس العامة.",
             lost="يضيع التشخيص الذاتي وأدوات الرجوع؛ ويتفرّق بنك الأخطاء في المجلدات."),
    ]},
    "C": {"name": "عشرة مجلدات للمنهج ومجلدٌ للمرجع (ما تنتهي إليه البوابة)", "volumes": [
        dict(name="الأصول", stage="التأسيس", units=[("opening",), ("intro",), ("bab", 1, 1)],
             sentence="ما الكلام الناجح، ولماذا يُتعلَّم صناعةً: المقدمة العلمية، ثم معايير الكلام الخمسة، وأسئلته الستة، وطريق الملكة.",
             adds="الأصل النظري والأدوات التي تطبّقها المجلدات كلّها.",
             lost="يفقد القارئ الميزان الذي يُقاس به كل كلامٍ بعده، والحجّة العلمية للصناعة."),
        dict(name="اللسان", stage="التأسيس", units=[("bab", 2, 2), ("app", "و")],
             sentence="صحّة الصوت الذي يحمل الكلام، ثم برنامجٌ يوميٌّ يحفظها ثلاثين يومًا.",
             adds="وحده يدرّب النطق والصوت؛ ويُختم ببرنامجه اليومي الذي يقول عن نفسه إنه «يلخّص ما درسته في الباب الثاني».",
             lost="يضيع تدريب النطق كلّه."),
        dict(name="العبارة", stage="التأسيس", units=[("bab", 3, 3)],
             sentence="هل جملتي عربيةٌ طبيعية؟ سلامة الجملة المنطوقة: ما يظهر من الإعراب، والصرف، والمطابقة، ومقاومة الترجمة الحرفية وأثر اللغة الأم، والحشو، واختيار الكلمة، وطول الجملة.",
             adds="الجملة وحدها: ما يلتقطه سمع العربي فورًا، لا النحو كلّه.",
             lost="تضيع الجملة الطبيعية، ويبقى البيان بلا أساسٍ يقوم عليه."),
        dict(name="البيان", stage="التأسيس", units=[("bab", 4, 4)],
             sentence="هل كلامي مرتّبٌ مبين؟ بناء الكلام قبل النطق، وأول عشر ثوانٍ، والافتتاح والتعريف بالنفس والانتقال والخاتمة، ثم المعاني والبيان والبديع والاقتباس تطبيقًا.",
             adds="الكلام بعد الجملة: ترتيبه ومواضعه وحسنه.",
             lost="يضيع بناء الكلام؛ فيبقى المتكلّم صحيح الجمل مضطرب الكلام."),
        dict(name="المقام", stage="التواصل", units=[("bab", 5, 5)],
             sentence="هل أعرف لمن أتكلّم وكيف؟ خريطة المتحدّثين والمخاطَبين، واتجاهات الخطاب، ومختبر ثلاثين موقفًا.",
             adds="اختيار اللسان للشخص والمنزلة والمقام.",
             lost="يضيع اختيار اللسان المناسب."),
        dict(name="الأدب", stage="التواصل", units=[("bab", 6, 6)],
             sentence="هل يحبّني السامع ويحترمني؟ أفعال الأدب: السلام والإنصات، والشكر والدعاء، والطلب والرفض، والاعتذار والتهنئة والتعزية، وأدب الخلاف، ولغة الجسد.",
             adds="ما يحفظ العلاقة وهو يقول الحقّ؛ وبه تنتهي الدورة المكثّفة (المستويات ٠–٥).",
             lost="يضيع أدب المخاطبة، فيصحّ الكلام ويُردّ صاحبه."),
        dict(name="الحوار", stage="التواصل", units=[("bab", 7, 7)],
             sentence="هل أُحسن السؤال والجواب والاعتراض؟ الكلام المتبادل: السؤال، والجواب، والاستيضاح، والمداخلة، والإقناع، والمناظرة، والنقد والنصيحة.",
             adds="أول ما لا يقوله المتكلّم وحده؛ والباب يقول ذلك في فاتحته.",
             lost="يضيع الحوار، وهو أكثر الكلام في الحياة."),
        dict(name="المجالس والمنبر", stage="المنصّات", units=[("bab", 8, 8), ("bab", 9, 9)],
             sentence="الكلام أمام الجماعة، من الحلقة إلى الجمهور: أدب مجلس العلم ومجالس الجامعة والمناسبات، ثم الخطبة والمحاضرة والكلمة وعرض البحث.",
             adds="وهو «مسار الأئمة والخطباء» في المنهج (المستويان ٧–٨) بتمامه.",
             lost="يضيع الكلام أمام الجماعة، في المجلس وعلى المنبر."),
        dict(name="المؤسسة", stage="المنصّات", units=[("bab", 10, 10)],
             sentence="الكلام الذي يُكتب ويُحاسَب عليه: المقابلة، وإدارة الاجتماع، وخطاب المدير والموظف.",
             adds="وهو «مسار المقابلات والوظائف» (المستوى ٩) بتمامه.",
             lost="يضيع كلام المؤسسة، حيث تقرّر الجملة وظيفةً أو مشروعًا."),
        dict(name="التمكين", stage="التمكين", units=[("bab", 11, 11), ("bab", 12, 12), ("bab", 14, 13), ("end", "00-خاتمة-الكتاب")],
             sentence="الكلام حيث لا يُحتمل الخطأ ولا الإعادة: أمام الكاميرا، وباسم الجهة، وبلا إعداد؛ ثم خاتمة الكتاب.",
             adds="مسار الإعلام (١٠)، وتتمّة مسار القيادات (١١)، والملكة التي تمتحن ما قبلها كلّه.",
             lost="يضيع أعلى المقامات ضغطًا، والختام."),
        dict(name="المرجع", stage="المرجع", units=[("bab", 13, None), ("app", "أ"), ("app", "ب"), ("app", "ج"), ("app", "هـ"),
                                                   ("end", "المسرد"), ("end", "المصادر-والمراجع")],
             sentence="ما يُرجع إليه ولا يُقرأ متتابعًا: ما يُقال (البنوك التعبيرية والنماذج)، وما لا يُقال (بنك الأخطاء ومعجم الترجمة الحرفية)، وأين يوجد كلّ شيء (المسرد والفهارس العامة).",
             adds="هو «المكتبة التعبيرية» التي نصّ عليها الدليل في كتبه المرافقة، ومعها بنك الأخطاء والفهارس العامة.",
             lost="يضيع التشخيص الذاتي وأدوات الرجوع؛ ويتفرّق بنك الأخطاء في المجلدات."),
    ]},
}
# what leaves the printed series under model C, and where it goes (Bible, part five: the companion books)
OUTSIDE_C = [("ملحق د: نصوص الحلقات", "سكريبتات الحلقات (كتابٌ مرافق)", "نصوصٌ لإنتاج البرنامج المرئي، لا يقرؤها المتعلّم في مجلده"),
             ("ملحق ز: أدوات التقويم", "بنك الاختبارات ودليل المعلم (كتابان مرافقان)", "اختبار تحديد المستوى وموازين التقويم أداةٌ للمعلّم والمؤسسة"),
             ("تقرير المراجعة وضبط الجودة", "ملفات الإنتاج", "«جزءٌ من طبعة المراجعة» بنصّه، ولا لغة إنتاجٍ في الكتاب المطبوع")]


def build(model):
    babs = {n: bab(n) for n in range(1, 15)}
    intro_w = sum(words(f) for f in (BOOK / "المدخل").glob("*.md"))
    vols = []
    for i, v in enumerate(MODELS[model]["volumes"], 1):
        units, w_total, p_s, p_o, series_babs = [], 0, 0.0, 0.0, []
        has_opening = False
        for u in v["units"]:
            if u[0] == "opening":
                has_opening = True
                units.append({"kind": "opening", "title": "الافتتاحية: المقدمة العلمية", "pages": OPENING_PAGES})
            elif u[0] == "intro":
                units.append({"kind": "intro", "title": "المدخل: العربية ومستوياتها", "words": intro_w})
                w_total += intro_w; p_s += pages(intro_w, DENSITY["student"], 1); p_o += pages(intro_w, DENSITY["opening"], 1)
            elif u[0] == "bab":
                b = babs[u[1]]; w = b["opener"] + sum(c["words"] for c in b["chapters"])
                label = f"الباب {ORD[u[2] - 1]}" if u[2] else "المرجع الأول"
                units.append({"kind": "bab", "present": u[1], "series": u[2], "label": label, "title": b["title"].split(":", 1)[-1].strip(),
                              "question": QUESTION[u[1]], "level": (u[1] - 1 if u[1] < 13 else 12) if u[2] else None,
                              "words": w, "chapters": b["chapters"]})
                w_total += w; series_babs.append(u[2])
                p_s += pages(w, DENSITY["student"], len(b["chapters"]), 1); p_o += pages(w, DENSITY["opening"], len(b["chapters"]), 1)
            elif u[0] == "app":
                a = appendix(u[1]); units.append({"kind": "app", **a})
                w_total += a["words"]; p_s += pages(a["words"], DENSITY["student"], 2); p_o += pages(a["words"], DENSITY["opening"], 2)
            elif u[0] == "end":
                e = end(u[1]); units.append({"kind": "end", **e})
                w_total += e["words"]; p_s += pages(e["words"], DENSITY["student"], 2); p_o += pages(e["words"], DENSITY["opening"], 2)
        extra = (0 if has_opening else FRONT)
        idx_s, idx_o = max(INDEX_MIN, .04 * p_s), max(INDEX_MIN, .04 * p_o)
        if v["stage"] == "المرجع":
            idx_s = idx_o = SERIES_INDEX
        pages_s = round(p_s + extra + idx_s + (OPENING_PAGES if has_opening else 0))
        pages_o = round(p_o + extra + idx_o + (OPENING_PAGES if has_opening else 0))
        vols.append({"n": i, **{k: v[k] for k in ("name", "stage", "sentence", "adds", "lost")}, "units": units,
                     "words": w_total, "pages": pages_s, "pages_max": pages_o})
    return vols


def md_of(model, vols):
    m = MODELS[model]
    L = [f"## النموذج {model}: {m['name']}", "",
         "| المجلد | المرحلة | الأبواب | الكلمات | الصفحات (١٢ نقطة) | الصفحات (١٣٫٢ نقطة) |", "|---|---|---|---|---|---|"]
    for v in vols:
        babs = "، ".join(u["label"] for u in v["units"] if u["kind"] == "bab")
        L.append(f"| {str(v['n']).translate(AR)}. {v['name']} | {v['stage']} | {babs or '—'} | {v['words']:,} | {v['pages']} | {v['pages_max']} |".translate(AR).replace(",", "٬"))
    L.append("")
    for v in vols:
        L += [f"### {str(v['n']).translate(AR)}. {v['name']} ({v['stage']})", "",
              f"- **تعريفه في جملة:** {v['sentence']}", f"- **ما يضيفه ولا يكرّره:** {v['adds']}", f"- **ما يضيع لو حُذف:** {v['lost']}",
              f"- **حجمه:** {v['words']:,} كلمة؛ نحو {v['pages']} صفحة بمتن ١٢ نقطة، و{v['pages_max']} بمتن ١٣٫٢.".translate(AR).replace(",", "٬"), ""]
        for u in v["units"]:
            if u["kind"] == "bab":
                L.append(f"- **{u['label']}: {u['title']}** — {u['question']} ({u['words']:,} كلمة)".translate(AR).replace(",", "٬"))
                L += [f"  - {c['title']} ({c['words']:,})".translate(AR).replace(",", "٬") for c in u["chapters"]]
            elif u["kind"] == "opening":
                L.append(f"- **{u['title']}** ({str(OPENING_PAGES).translate(AR)} صفحة مخرَجة)")
            else:
                L.append(f"- **{u['title']}** ({u['words']:,} كلمة)".translate(AR).replace(",", "٬"))
        L.append("")
    return L


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"density": DENSITY, "samples": SAMPLES, "models": {k: {"name": MODELS[k]["name"], "volumes": build(k)} for k in MODELS},
            "outside_c": OUTSIDE_C}
    (OUT / "خريطة-المجلدات.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# خريطة المجلدات: قياس البوابة", "",
         "الكثافة مقيسةٌ لا مفروضة: رُكّبت ستة فصولٍ مختلفة الطبيعة بإخراج الكتاب نفسه ثم عُدّت صفحاتها "
         f"({DENSITY['opening']} كلمة للصفحة بمتن الافتتاحية ١٣٫٢ نقطة، و{DENSITY['student']} بمتن كتاب الطالب ١٢ نقطة كما في الجزء السادس من الدليل)."
         .translate(AR), "", "| العيّنة | طبيعتها | الكلمات | صفحات ١٢ ن | صفحات ١٣٫٢ ن |", "|---|---|---|---|---|"]
    L += [f"| {a} | {b} | {c:,} | {d} | {e} |".translate(AR).replace(",", "٬") for a, b, c, d, e in SAMPLES]
    L.append("")
    for k in MODELS:
        L += md_of(k, data["models"][k]["volumes"])
    L += ["## ما يخرج من السلسلة المطبوعة في النموذج C", "", "| المادة | موضعها | السبب |", "|---|---|---|"]
    L += [f"| {a} | {b} | {c} |" for a, b, c in OUTSIDE_C]
    (OUT / "خريطة-المجلدات.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    for k in MODELS:
        print(k, [(v["name"], v["pages"], v["pages_max"]) for v in data["models"][k]["volumes"]])


if __name__ == "__main__":
    main()
