#!/usr/bin/env python3
"""The terminology audit of the series (Bible, ch. 16 and ch. 65; ch. 31 for the five concepts; ch. 15 §٢ for the
foreign term; ch. 5 §٢ and ch. 10 for the two scales; the governing document, rule 4): every technical word of the
eleven volumes, set against the terminology ledger, the glossary and the Bible.

What it reads
    book/_production/التحقيق/سجل-المصطلحات.tsv   approved form, English equivalent, forbidden alternatives, relations
    the glossary (paths.GLOSSARY)               the printed definitions
    bible/05 ch. 16                              the terminology table and its «لا يُستعمل بدله» column
    bible/07 ch. 31                              the five concepts that are not to be confused
    bible/02 ch. 5 §٢ and ch. 6 §١, bible/03 ch. 10   the formality scale, the context card, the error classes and degrees
What it leaves out (the book is about errors: an error shown on purpose is not a terminological error)
    transmitted text and mentions («…», ﴿…﴾, fully vocalised verse and hadith), model speech (blockquotes that follow a
    speaker's label or open on «/[), the speech columns of dialogue tables, stage directions […], example lines that show
    an error or an acceptable form (✘, ◐, «الخطأ:»), the error cells of tables, titles in the notes, the source lists.
The checks
    C1 forbidden alternatives in use (ledger + Bible ch. 16 + governing document), and the near-synonyms that stand for
       an approved term (FAMILIES)
    C2 the four grades in the graded comparisons (①–④): the label and its place
    C3 the formality scale: the names of the five degrees, wherever they are named
    C4 the error classes (خ-N) and the four severity degrees (● ◐ ◔ ○), wherever they are named
    C5 the five criteria and the five concepts: members of each list
    C6 الفصاحة and البلاغة: definitions crossed or the two joined as synonyms
    C7 spelling variants of a ledger term (hamza, ى/ي, ة/ه, the article)
    C8 two sibling terms claiming the same examples (الحشو الصوتي / الحشو اللفظي …)
    C9 Latin: the foreign term in parentheses, its case, one Arabic term for one Latin term and the reverse, the ledger's
       English, no Arabic transliteration, no bare Latin in the prose
    C10 the ledger, the glossary and the Bible against one another; the terms the text defines and the ledger lacks
Every flagged occurrence a human reader has judged is in READ, with the reading; a judged defect carries its exact
current text and its proposed replacement, and the tool checks that the current text is still there. Nothing in book/
or bible/ is edited.

    python3 termaudit.py [--companions]    writes book/_production/التحقيق/تدقيق-المصطلحات.md
                                           --companions: the two companion books too, in their own section
"""
import csv
import re
import sys
from bisect import bisect_right
from collections import Counter, defaultdict
from pathlib import Path

from paths import GLOSSARY, PRODUCTION
from volumes import BOOK, ORD, VOLUMES, unit_files

HERE = Path(__file__).resolve().parent
BIBLE = HERE.parent / "bible"
LEDGER = PRODUCTION / "التحقيق" / "سجل-المصطلحات.tsv"
OUT = PRODUCTION / "التحقيق" / "تدقيق-المصطلحات.md"

L = "\u0621-\u064A"                                   # Arabic letters
DIAC = "\u064B-\u0652\u0670\u0640"                    # harakat, tanwin, sukun, dagger alif, tatweel
DIA = re.compile(f"[{DIAC}]")
NOT_L = f"(?<![{L}])"
END_L = f"(?![{L}])"
PROCLITIC = "(?:[وفبكل]|لل|وال|بال|فال|كال)?"
SKIP_FILES = ("ثبت-المصادر", "المصادر-والمراجع")    # titles are transmitted text
VOLW = ORD[:10] + ["الحادي عشر"]


def N(s):
    return DIA.sub("", s)


def loose(s):
    """A regex that finds normalised text `s` in the original, whatever harakat it carries."""
    return "".join(re.escape(c) + f"[{DIAC}]*" for c in s)


def strip_art(s):
    return " ".join(w[2:] if w.startswith("ال") else w for w in s.split())


def fold(s):
    """hamza on alif, ى/ي, ة/ه and the article: the letters that write one term two ways."""
    return strip_art(s.translate(str.maketrans("أإآى", "اااي")).replace("ة", "ه"))


def ar(n):
    return str(n).translate(str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩"))


# ----------------------------------------------------------------------------------------------------------------
# the authorities
# ----------------------------------------------------------------------------------------------------------------

def ledger():
    with open(LEDGER, encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def glossary():
    g = GLOSSARY.read_text(encoding="utf-8")
    return {N(dt.strip()): (N(re.sub(r"<[^>]+>", "", dd).strip()), en.strip(), dt.strip())
            for dt, en, dd in re.findall(r'<dt>([^<]+)<span class="en">([^<]*)</span></dt><dd>(.*?)</dd>', g)}


def bible_part(stem):
    return next(BIBLE.glob(stem + "-*.md")).read_text(encoding="utf-8")


def bible_ch16():
    """Bible ch. 16: {term: (definition, [alternatives], [notes])}."""
    t = bible_part("05")
    sec = t[t.index("## الباب السادس عشر"): t.index("## الباب السابع عشر")]
    out = {}
    for m in re.finditer(r"^\| \*\*([^*]+)\*\* \| ([^|]+) \| ([^|]+) \|$", sec, re.M):
        alts, notes = [], []
        for a in m.group(3).split("،"):
            note = re.search(r"\*\(([^)]*)\)\*", a)
            a = N(re.sub(r"\*\([^)]*\)\*", "", a)).strip()
            if a and a != "—":
                alts.append(a)
                notes.append(note.group(1) if note else "")
        out[N(m.group(1))] = (N(m.group(2)).strip(), alts, notes)
    return out


def bible_scale():
    """Bible ch. 5 §٢: {degree digit: name}."""
    t = bible_part("02")
    sec = t[t.index("سلّم الرسمية الخماسي"):]
    sec = sec[: sec.index("###", 5)]
    return {m.group(1): N(m.group(2)).strip() for m in re.finditer(r"^\| \*\*([١-٥])\*\* \| ([^|]+) \|", sec, re.M)}


def bible_card():
    """Bible ch. 6 §١: the fields of the context card, in order."""
    t = bible_part("02")
    box = t[t.index("بطاقة المقام ──"): t.index("### ٢. النموذج السداسي")]
    fields = []
    for m in re.finditer(r"│\s*([^:│]+?):", box):
        fields += [N(x).strip() for x in m.group(1).split("/")]
    return [f for f in fields if f]


def bible_errors():
    """Bible ch. 10: ({code digits: class name}, {symbol: degree name})."""
    t = bible_part("03")
    sec = t[t.index("## الباب العاشر"):]
    classes = {m.group(1): N(re.sub(r"\s*\(.*\)", "", m.group(2))).strip()
               for m in re.finditer(r"^\| خ-([٠-٩]+) \| ([^|]+) \|", sec, re.M)}
    degrees = {m.group(1): N(m.group(2)).strip() for m in re.finditer(r"^\| ([●◐◔○]) \| \*\*([^*]+)\*\* \|", sec, re.M)}
    return classes, degrees


def bible_concepts():
    t = bible_part("07")
    sec = t[t.index("### ١. خمسة مفاهيم لا تُخلط"): t.index("### ٢.")]
    return [N(m.group(1)) for m in re.finditer(r"^\| \*\*([^*]+)\*\* \|", sec, re.M)]


# ----------------------------------------------------------------------------------------------------------------
# the manuscript, and what the audit does not read
# ----------------------------------------------------------------------------------------------------------------

def series_files(companions=False):
    out = [(BOOK / "المجلد-الأول" / "00-كلمة-المؤلف.md", 1)]
    for v in VOLUMES:
        for u in v["units"]:
            out += [(f, v["n"]) for f in unit_files(v["n"], u)]
    if companions:
        out += [(f, None) for f in sorted((BOOK / "_المرافقة").rglob("*.md"))]
    return [(f, v) for f, v in out if f.exists() and not f.stem.endswith(SKIP_FILES) and not any(s in f.stem for s in SKIP_FILES)]


QUOTE = re.compile(r"«[^«»\n]*»|﴿[^﴾\n]*﴾")
DIRECTION = re.compile(r"\[(?!\^)(?![مر][٠-٩])[^\[\]\n]*\]")
TAGS = re.compile(r"<!--.*?-->|<[^>]+>|`[^`\n]*`")
BOX = re.compile(r"^\s*>\s*\*\*")                                # «> **تعريف:**», «> **قاعدة:**»: the author's own box
EXAMPLE_LINE = re.compile(r"^\s*(?:[-*]\s+|\d+\.\s+|[٠-٩]+\.\s+)?(?:✘|◐)")
ERROR_ITEM = re.compile(r"^\s*[-*]\s+\*\*(?:الخطأ|الخاطئ)\*\*|^\s*[-*]\s+\*\*(?:الخطأ|الخاطئ):\*\*")
SPEECH_COLS = ("الكلام", "قبل", "بعد", "الخطأ", "الخاطئ", "✘", "العبارة الخاطئة", "الصيغة الخاطئة", "كما قيل", "كما وقع")
LABEL_ONLY = re.compile(r"^\s*\*\*[^*]+\*\*\s*:?\s*$")


def blank(s, spans):
    s = list(s)
    for a, b in spans:
        for i in range(a, b):
            if s[i] != "\n":
                s[i] = " "
    return "".join(s)


def vocalised(s):
    letters = len(re.findall(f"[{L}]", s))
    return letters > 15 and len(DIA.findall(s)) / letters > 0.3


def cells(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


class Text:
    """A file read for its terminology: two masked copies, normalised, line by line.

    prose   everything the audit leaves out is blanked, «…» mentions too
    mention the same, but «…» kept (the Latin check needs the term the gloss follows)"""

    def __init__(self, path, vol):
        self.path, self.vol = path, vol
        self.rel = str(path.relative_to(BOOK))
        self.raw = path.read_text(encoding="utf-8")
        self.lines = self.raw.split("\n")
        work = re.sub(r"<!--.*?-->", lambda m: re.sub(r"[^\n]", " ", m.group(0)), self.raw, flags=re.S).split("\n")
        prose, mention = [], []
        fence = False
        block_masked = False
        header = None
        prev = ""
        for i, s in enumerate(work):
            if s.strip().startswith("```"):
                fence = not fence
                prose.append(" " * len(s)); mention.append(" " * len(s))
                continue
            if fence:
                prose.append(" " * len(s)); mention.append(" " * len(s))
                continue
            whole = False
            # blockquotes: the author's boxes stay; model speech, verse and quotation go
            if s.lstrip().startswith(">"):
                starts = not (i and work[i - 1].lstrip().startswith(">"))
                if starts:
                    body = s.lstrip()[1:].lstrip()
                    block_masked = not BOX.match(s) and (body[:1] in "«[(\"" or vocalised(s) or LABEL_ONLY.match(prev)
                                                         or prev.rstrip().endswith(":"))
                whole = block_masked
            if EXAMPLE_LINE.match(s) or ERROR_ITEM.match(s) or vocalised(s):
                whole = True
            if whole:
                prose.append(" " * len(s)); mention.append(" " * len(s))
                if s.strip():
                    prev = s
                continue
            spans = [m.span() for m in TAGS.finditer(s)] + [m.span() for m in DIRECTION.finditer(s)]
            if s.startswith("[^"):
                spans += [m.span() for m in re.finditer(r"\*[^*\n]+\*", s)]
            # tables: the speech and error columns go
            if s.lstrip().startswith("|"):
                nxt = work[i + 1] if i + 1 < len(work) else ""
                if re.match(r"^\s*\|[\s:|-]+\|\s*$", nxt):
                    header = cells(s)
                elif header and not re.match(r"^\s*\|[\s:|-]+\|\s*$", s):
                    pos, col = s.find("|") + 1, 0
                    for c in s.strip().strip("|").split("|"):
                        start = s.find(c, pos)
                        if col < len(header) and N(header[col]).startswith(tuple(N(x) for x in SPEECH_COLS)):
                            spans.append((start, start + len(c)))
                        pos, col = start + len(c) + 1, col + 1
            else:
                header = None
            m_spans = spans
            p_spans = spans + [m.span() for m in QUOTE.finditer(s)]
            prose.append(N(blank(s, p_spans)))
            mention.append(N(blank(s, m_spans)))
            if s.strip():
                prev = s
        self.prose = "\n".join(prose)
        self.mention = "\n".join(mention)
        self.starts = {}
        for name, t in (("prose", self.prose), ("mention", self.mention)):
            self.starts[name] = [0] + [k + 1 for k, c in enumerate(t) if c == "\n"]
        self.norm_raw = N(self.raw)
        self.starts["raw"] = [0] + [k + 1 for k, c in enumerate(self.norm_raw) if c == "\n"]

    def line_of(self, pos, which="prose"):
        return bisect_right(self.starts[which], pos)

    def around(self, lineno, norm_text, words=7):
        line = self.lines[lineno - 1]
        m = re.search(loose(norm_text), line)
        if not m:
            return line.strip()[:160]
        a = line[: m.start()].split(" ")
        b = line[m.end():].split(" ")
        left = " ".join(a[-words:]) if len(a) > words else line[: m.start()]
        right = " ".join(b[: words + 1]) if len(b) > words + 1 else line[m.end():]
        return ("…" if len(a) > words else "") + (left + m.group(0) + right).strip() + ("…" if len(b) > words + 1 else "")


# ----------------------------------------------------------------------------------------------------------------
# what the Bible and the ledger forbid, and the near-synonyms that stand for an approved term
# ----------------------------------------------------------------------------------------------------------------

GRADES = {"①": "غير الناجح", "②": "المقبول", "③": "الناجح", "④": "الرفيع"}
NOT_GRADES = r"(?:ال)?(?:وسط|متوسط|ممتاز|جيد|ضعيف|فاشل|متميز|بليغ|ماهر|بارع)(?:ة)?"
NOT_GRADES_RX = re.compile(f"(?<![\u0621-\u064A])" + NOT_GRADES + f"(?![\u0621-\u064A])")
SPEAKER = r"(?:ال)?(?:متكلم|متحدث)(?:ة|ون|ين|ان|تان)?"

# approved form ← near-synonyms that stand for it; the authority for each
FAMILIES = [
    ("الأصوات الحرجة", ["الحروف الحرجة", "حروف حرجة", "الأحرف الحرجة", "الأصوات الصعبة", "أصوات صعبة", "الحروف الصعبة", "حروف صعبة"],
     "السجل والمسرد: «الأصوات الحرجة»؛ والدليل (الباب ١٦) لا يستعمل بدلها «الحروف الصعبة»"),
    ("درجة الرسمية", ["مستوى الرسمية", "مستويات الرسمية", "مستوى رسمية"],
     "السجل: «درجة الرسمية»؛ والدليل (الباب ١٦) يخصّ «المستوى» بمستويات البرنامج، وصفحة «الرموز والاصطلاحات» في كل مجلد تعرّفه بذلك"),
    ("الملكة الشفهية", ["الملكة الشفوية", "ملكة شفوية", "الملكة اللغوية", "الملكة الكلامية", "المهارة الكلامية", "مهارة التحدث",
                        "مهارات التحدث", "القدرة اللغوية", "ملكة الكلام"],
     "السجل: «الملكة الشفهية»، وبديلها الممنوع «مهارة التحدّث»؛ والدليل (الباب ١٦): لا «المهارة الكلامية العامة» ولا «القدرة اللغوية»؛ والباب ٦٥: لا يعني مجلدٌ بالملكة غير ما يعنيه غيره"),
    ("الفصحى المنطوقة", ["الفصحى المعاصرة المنطوقة", "الفصحى المنطوقة المعاصرة"],
     "السجل: «الفصحى المنطوقة» (مقترح؛ يُقرّ)، والدليل (الباب ٣١): «الفصحى المنطوقة المعاصرة»: صيغةٌ واحدة لمستوى واحد"),
    ("مقتضى الحال", ["مقتضى المقام", "مقتضيات المقام"], "السجل والمسرد: «مقتضى الحال»، وتعريفه «ما يستدعيه المقام»"),
    ("الكفاية التواصلية", ["القدرة التواصلية", "الكفاءة التواصلية"],
     "مصطلح هايمز سُمّي في الفصل السابع من الافتتاحية «الكفاية التواصلية»؛ فلا يُسمّى بعده باسمٍ آخر"),
    ("المحاكاة", ["لعب الأدوار", "تمثيل الأدوار"], "الدليل (الباب ١٦): «المحاكاة» لا «لعب الأدوار»"),
    ("السجل اللغوي", ["المستوى اللغوي"], "الدليل (الباب ١٦): لا «المستوى اللغوي»"),
    ("التعبير الطبيعي", ["التعبير السليم"], "الدليل (الباب ١٦): لا «التعبير السليم»"),
    ("المتكلم الناجح", ["المتكلم الجيد", "المتحدث الممتاز", "المتحدث الجيد", "المتحدث الناجح", "المتكلم الماهر", "المتكلم البارع"],
     "الدليل (الباب ١٦): لا «المتكلم الجيد» ولا «المتحدث الممتاز»"),
    ("المتكلم غير الناجح", ["المتكلم الفاشل", "المتكلم الضعيف", "الغير ناجح", "الغير الناجح", "المتحدث الفاشل"],
     "السجل: البديلان الممنوعان «الفاشل» و«الضعيف»؛ والوثيقة الحاكمة (القاعدة ٤): لا يُستعمل لفظ «الفاشل» في المتن"),
    ("المتكلم المقبول", ["المتكلم المتوسط"], "الدليل (الباب ١٦): لا «المتوسط»"),
    ("المتكلم الرفيع", ["المتكلم الممتاز", "المتكلم المتميز"], "الدليل (الباب ١٦): لا «الممتاز» ولا «المتميز»"),
    ("العربية التراثية", ["الفصحى التراثية", "الفصحى الكلاسيكية"], "الدليل (الباب ٣١) والافتتاحية: «العربية التراثية»"),
]
# «الفاشل» as the opposite of «الناجح» (the governing document, rule 4): a performance called a failure
FAILED = re.compile(rf"{NOT_L}(?:[وف]?(?:أما|اما)\s+)?(?:ال)?فاشل(?:ة|ا|ون|ين)?{END_L}")
PERFORMANCE = r"(?:كلام|الكلام|أداء|الأداء|تقديم|التقديم|خطبة|الخطبة|افتتاح|الافتتاح|جواب|الجواب|محاضرة|المحاضرة|نموذج|النموذج)"
SCENARIO = re.compile(rf"{NOT_L}{PROCLITIC}سيناريو(?:هات)?{END_L}")
# the degrees of the formality scale by names that are not theirs
SCALE_ODD = ["الرسمي الشديد", "الرسمية الشديدة", "الودي الحميم", "الرسمي البروتوكولي", "البروتوكولي"]
# Arabic letters for a foreign term (Bible, ch. 15 §٢: «لا يُكتب بحروف عربية (الريجستر)»)
TRANSLIT = ["براغماتي", "براجماتي", "ريجستر", "ديغلوسيا", "دايغلوسيا", "فونولوج", "مورفولوج", "سيمانتي", "سوسيولساني",
            "إنتوناشن", "ديكشن", "كود سويتش", "كودسويتش"]
CONCEPTS_WORDS = ["الصحة", "الطبيعية", "المناسبة", "الفصاحة", "البلاغة"]
CRITERIA_WORDS = ["الوضوح", "الصحة", "المناسبة", "التأثير", "الأدب"]
CHECKS = ["C1 بديلٌ من مصطلحٍ معتمد", "C2 الدرجات الأربع", "C3 سلّم الرسمية", "C4 التصنيف والخطورة", "C5 المعايير والمفاهيم",
          "C6 الفصاحة والبلاغة", "C7 رسم المصطلح", "C8 مصطلحان على أمثلةٍ واحدة", "C9 المقابل الأجنبي"]
# sibling terms whose examples must not be the same examples
SIBLINGS = [("الحشو الصوتي", "الحشو اللفظي")]


# ----------------------------------------------------------------------------------------------------------------
# the readings: every flagged occurrence judged by a reader. file: a path suffix; has: a phrase of the (normalised)
# line; verdict «خلل» carries before/after, exact as in the file.
# ----------------------------------------------------------------------------------------------------------------

READ = [
    # C1 · C8 · forbidden alternatives and near-synonyms ------------------------------------------------------------
    dict(file="ف02-أ-المدخل-والدرس-الأول.md", has="أما الفاشل فيفسد", verdict="خلل",
         why="«الفاشل» في مقابل «الناجح» وصفًا لأداء (التقديم): البديل الممنوع في السجل، والوثيقة الحاكمة (القاعدة ٤) تمنع لفظه في المتن.",
         before="والتقديم الناجح لا يكاد يُلحظ، أما الفاشل فيفسد فعالية أُعدّت شهورًا.",
         after="والتقديم الناجح لا يكاد يُلحظ، أما غير الناجح فيفسد فعالية أُعدّت شهورًا."),
    dict(file="ملحق-د-نصوص-الحلقات.md", has="كلاما فاشلا مقاما", verdict="خلل",
         why="«فاشلًا» وصفًا للكلام في مقامه: البديل الممنوع في السجل، والوثيقة الحاكمة (القاعدة ٤).",
         before="الكلام الصحيح لغةً قد يكون كلامًا فاشلًا مقامًا؛",
         after="الكلام الصحيح لغةً قد يكون كلامًا غير ناجحٍ مقامًا؛"),
    dict(file="ف01-ب-التطبيق-والتقويم.md", has="ثم حدد الحروف الحرجة في كلامك", verdict="خلل",
         why="«الحروف الحرجة» صيغةٌ ثانية لـ«الأصوات الحرجة» (السجل والمسرد)، تجمع «الحروف» التي يمنعها الدليل (الباب ١٦: «الحروف الصعبة») إلى الوصف المعتمد.",
         before="ثم حدّد الحروف الحرجة في كلامك ومناطقها",
         after="ثم حدّد الأصوات الحرجة في كلامك ومناطقها"),
    dict(file="ف01-السلام-والبشاشة-والاستماع.md", has="نطق الحروف الحرجة في السلام", verdict="خلل",
         why="وصف المثال بـ«الحروف الحرجة»، والمصطلح المعتمد «الأصوات الحرجة».",
         before="(نطق الحروف الحرجة في السلام)", after="(نطق الأصوات الحرجة في السلام)"),
    dict(file="ف03-أخطاء-النطق-الأصوات-الحرجة.md", has="تحفظ فيها كل الحروف الحرجة", verdict="خلل",
         why="في فصلٍ عنوانه «الأصوات الحرجة»، وفي البطاقة نفسها «الأصوات الحرجة» في التعليل بعد سطر: صيغتان لمصطلح واحد.",
         before="تحفظ فيها كل الحروف الحرجة وضوحها كاملًا", after="تحفظ فيها كل الأصوات الحرجة وضوحها كاملًا"),
    dict(file="ف06-ب-التطبيق-والتقويم.md", has="بإتقان الأصوات الصعبة وحدها", verdict="خلل",
         why="«الأصوات الصعبة» بديلٌ من «الأصوات الحرجة» على مثال «الحروف الصعبة» الممنوع في الدليل (الباب ١٦)؛ والمقابلة بـ«الأصوات السهلة» قبلها تبقى.",
         before="بإتقان الأصوات الصعبة وحدها", after="بإتقان الأصوات الحرجة وحدها"),
    dict(file="ف03-ب-التطبيق-والتقويم.md", has="هل يتغير مستوى الرسمية", verdict="خلل",
         why="«مستوى الرسمية» بدل «درجة الرسمية»: و«المستوى» مخصوصٌ بمستويات البرنامج (الدليل، الباب ١٦؛ وصفحة الرموز والاصطلاحات).",
         before="(هل يتغير مستوى الرسمية؟ وماذا يبقى كما هو؟)", after="(هل تتغير درجة الرسمية؟ وماذا يبقى كما هو؟)"),
    dict(file="ف04-ب-الدرس-الثاني.md", has="كيف يتغير مستوى الرسمية أكثر", verdict="خلل",
         why="«مستوى الرسمية» بدل «درجة الرسمية».",
         before="(كيف يتغير مستوى الرسمية أكثر؟)", after="(كيف تتغير درجة الرسمية أكثر؟)"),
    dict(file="ف10-ب-التطبيق-والتقويم.md", has="هل يتغير مستوى الرسمية", verdict="خلل",
         why="«مستوى الرسمية» بدل «درجة الرسمية».",
         before="(هل يتغير مستوى الرسمية؟)", after="(هل تتغير درجة الرسمية؟)"),
    dict(file="ف11-أ-المدخل-والدرسان.md", has="بحسب مقتضى المقام", verdict="خلل",
         why="«مقتضى المقام» بدل المصطلح المعتمد «مقتضى الحال» (السجل والمسرد)، في هدفٍ من أهداف الفصل.",
         before="بحسب مقتضى المقام لا بسرعة واحدة ثابتة", after="بحسب مقتضى الحال لا بسرعة واحدة ثابتة"),
    dict(file="16-علوم-العربية-وطريق-التكوين.md", has="الملكة اللغوية", verdict="خلل",
         why="جدولٌ تعريفي يسمّي المرتبة الثانية «الملكة اللغوية»، وسمّاها الفصل السابع «الملكة»، والسجل والمسرد «الملكة الشفهية» (المرتبة الثانية من المراتب الأربع): ثلاثة أسماء لمفهوم واحد في مجلد واحد (الباب ٦٥ §١).",
         before="| **الملكة اللغوية** | جريان اللغة على اللسان من غير استحضار قواعدها |",
         after="| **الملكة الشفهية** | جريان اللغة على اللسان من غير استحضار قواعدها |"),
    dict(file="16-علوم-العربية-وطريق-التكوين.md", has="القدرة التواصلية", verdict="خلل",
         why="سُمّي مفهوم هايمز في الفصل السابع «الكفاية التواصلية» (حسن التصرّف في المقام)، ثم سُمّي في جدول الفصل الخامس عشر «القدرة التواصلية» بتعريفٍ في معناه، فيظنّ القارئ أنهما شيئان. فإن كان المفهوم واحدًا، وتعريفه يدلّ على ذلك، فاسمه واحد.",
         before="| **القدرة التواصلية** | أن يوصل المتكلّم مراده إلى مخاطَبه في موقفٍ بعينه |",
         after="| **الكفاية التواصلية** | أن يوصل المتكلّم مراده إلى مخاطَبه في موقفٍ بعينه |"),
    dict(file="08-من-المعرفة-إلى-الملكة.md", has="الكفاية التواصلية", verdict="ليس خللًا",
         why="الموضع الأول للمصطلح، يحكي اسمه في الدرس الحديث؛ والتوحيد يكون في الموضع الثاني."),
    dict(file="14-أي-عربية-نتكلم.md", has="الفصحى المعاصرة المنطوقة", verdict="خلل",
         why="جدول المستويات الخمسة يسمّي المستوى «الفصحى المعاصرة المنطوقة»، والمدخل «الفصحى المنطوقة»، والفصل الثامن «الفصحى المنطوقة المعاصرة»، والسجل «الفصحى المنطوقة»: ثلاث صيغ لمستوى واحد. (والسجل يجعل صيغته «مقترحًا يُقرّ»، والدليل في الباب ٣١ يكتب «الفصحى المنطوقة المعاصرة»؛ فيُقرّ المؤلف الصيغة أولًا، والمقترح هنا صيغة السجل.)",
         before="| **الفصحى المعاصرة المنطوقة** |", after="| **الفصحى المنطوقة** |"),
    dict(file="15-المفاهيم-الخمسة.md", has="فللفصحى المعاصرة المنطوقة", verdict="خلل",
         why="الصيغة الثانية من صيغ المستوى الثلاث؛ والمقترح صيغة السجل.",
         before="فللفصحى المعاصرة المنطوقة عاداتها", after="فللفصحى المنطوقة عاداتها"),
    dict(file="09-ما-رأيته.md", has="والفصحى المنطوقة المعاصرة ليست", verdict="خلل",
         why="الصيغة الثالثة (وهي صيغة الدليل في الباب ٣١)؛ والمقترح صيغة السجل، فإن أقرّ المؤلف صيغة الدليل عُكس الاقتراح في الموضعين الآخرين والسجل.",
         before="والفصحى المنطوقة المعاصرة ليست لغة الكتب التراثية", after="والفصحى المنطوقة ليست لغة الكتب التراثية"),
    dict(file="00-فاتحة-الباب-الأول.md", has="كيف تكتسب ملكة الكلام", verdict="ليس خللًا",
         why="إضافةٌ وصفية («ملكة الكلام») في عرض محاور الباب، لا اسمٌ اصطلاحي بديل؛ والمصطلح معرَّفٌ في الفصل السادس من الباب نفسه باسمه المعتمد."),
    dict(file="09-ما-رأيته.md", has="ملكة الكلام من أول الطريق", verdict="ليس خللًا",
         why="إضافةٌ وصفية في سرد المؤلف، لا تعريفٌ ولا مصطلحٌ بديل."),
    dict(file="13-لماذا-صناعة.md", has="مهارات التحدث", verdict="ليس خللًا",
         why="ذِكرٌ للاسم المعدول عنه في بيان سبب العدول، وهو بين علامتي تنصيص."),
    dict(file="ف04-ب-الدرس-الثاني.md", has="والمتكلم الماهر لا يكتفي", verdict="ليس خللًا",
         why="وصفٌ عامّ للمتكلم في قراءة الحال، لا درجةٌ من الدرجات الأربع ولا مقابلٌ لها."),
    dict(file="ف02-ج-التطبيق-والتقويم.md", has="تقديم المتحدث الناجح", verdict="ليس خللًا",
         why="«الناجح» صفةٌ لـ«تقديم» (تقديم المتحدث في الفعالية)، لا للمتحدث."),
    dict(file="ف04-ب-الدرس-الثاني.md", has="لا يصعد فجأة إلى الرسمية الشديدة", verdict="خلل",
         why="القاعدة الثانية من قواعد الانتقال في الدليل (الباب ٥ §٣) بلفظها: «لا يُصعد فجأة إلى شديد الرسمية في مقام ودي»؛ وفي المتن اسمٌ آخر للدرجة الخامسة.",
         before="لا يُصعد فجأة إلى الرسمية الشديدة في مقام ودي", after="لا يُصعد فجأة إلى شديد الرسمية في مقام ودي"),
    dict(file="ف09-ج-التوليف-والتدريبات.md", has="وطرفاه الأسري الصرف والرسمي الشديد", verdict="خلل",
         why="يسمّي طرفي السلّم، فيسمّي الأول باسمه («الأسري») والخامس باسمٍ غير اسمه («الرسمي الشديد»، والمعتمد «شديد الرسمية»).",
         before="وطرفاه الأسري الصرف والرسمي الشديد أقل تكرارًا", after="وطرفاه الأسري الصرف وشديد الرسمية أقل تكرارًا"),
    dict(file="ف04-ج-التطبيق-والتقويم.md", has="عودته إلى الرسمية الشديدة", verdict="ليس خللًا",
         why="وصفٌ لأداء المتكلم في تحليل الحوار («الرسمية المفرطة» قبله)، لا تسميةٌ لدرجةٍ من السلّم."),
    dict(file="ف05-الأسلوب-والثقافة-والمقام.md", has="الرسمية الشديدة في المجلس الأسري", verdict="ليس خللًا",
         why="وصفٌ للخطأ في تعليله، لا تسميةٌ لدرجةٍ من السلّم."),
    dict(file="ف09-أ-المدخل-والدرس-الأول.md", has="في سيناريو واحد متصل", verdict="خلل",
         why="«السيناريو» في الدليل (الباب ١٦) لا يُستعمل بدل «الموقف» إلا في بنك المواقف؛ وهذا هدفٌ من أهداف الفصل.",
         before="في سيناريو واحد متصل داخل مجلس العلم", after="في موقفٍ واحد متصل داخل مجلس العلم"),
    dict(file="ف08-الخروج-عن-الموضوع-والتكلف.md", has="متحدث بارع", verdict="ليس خللًا",
         why="وصفٌ لمتكلمٍ يُقتدى به في بطاقة «التقليد»، لا درجةٌ من الدرجات الأربع."),
    dict(file="ف03-أ-المفاهيم-والدرس.md", has="| to ", verdict="ليس خللًا",
         why="جدول الأفعال الإنجليزية التي تُترجم حرفيًّا: الإنجليزية فيه موضوع الدرس، لا مقابلٌ لمصطلح."),
    dict(file="ف03-أ-المدخل-والأصوات-الخمسة.md", has="alcalde", verdict="ليس خللًا",
         why="لفظٌ إسبانيٌّ شاهدٌ في مسألة صوتية (أثر نطق الضاد في الاقتراض)، بحاشيته؛ لا مصطلح."),
    dict(file="ف05-أ-الأفعال-وحروف-الجر.md", has=["give ←", "make ←", "**for**", "**to**", "**from**", "**of**", "**with/at**"],
         verdict="ليس خللًا", why="الأفعال وحروف الجر الإنجليزية التي يُدرَس أثرها في الترجمة الحرفية: موضوع الدرس نفسه."),
    dict(file="ف05-ج-التطبيق-والتقويم.md", has=["on the other hand", "give وtake", "give وtake وmake"], verdict="ليس خللًا",
         why="اللفظ الإنجليزي مذكورٌ موضوعًا للتصحيح أو التمرين (الترجمة الحرفية)، لا مقابلًا لمصطلح."),
    dict(file="ف08-ج-التطبيق-والتقويم.md", has="take a look", verdict="ليس خللًا",
         why="اللفظ الإنجليزي مذكورٌ أصلًا للترجمة الحرفية التي تُصحَّح."),
    dict(file="ف01-ج-التطبيق-والتقويم.md", has="(give my best)", verdict="ليس خللًا",
         why="القالب الإنجليزي الذي تُرجم حرفيًّا مذكورٌ موضوعًا للتصحيح، لا مقابلًا لمصطلح."),
    # C2 · the graded comparisons --------------------------------------------------------------------------------
    dict(file="ف08-ج-التطبيق-والتقويم.md", has="نسخة وسط", verdict="خلل",
         why="النسخة الثانية في المقارنة موضع «المقبول» (والتحليل بعدها: «مقبول لكن باهت»، و«لم تبلغ الغاية»)؛ و«وسط» صيغةٌ من «المتوسط» الذي يمنعه الدليل (الباب ١٦) بديلًا من «المقبول».",
         before="**② نسخة وسط**", after="**② نسخة مقبولة**"),
    # C3 · the formality scale -----------------------------------------------------------------------------------
    dict(file="ف04-ج-التطبيق-والتقويم.md", has="من الودي إلى الرسمي الشديد", verdict="خلل",
         why="«الرسمي الشديد» اسمٌ غير اسم الدرجة الخامسة («شديد الرسمية» في الدليل، الباب ٥ §٢، وصفحة الرموز، وجداول الكتاب كلها)؛ ثم إن «ثلاث درجات متتالية» من «الودي» (٢) لا تبلغ الخامسة: فهي ٢ ← ٣ ← ٤.",
         before="بحيث ينتقل تسجيلك من الودي إلى الرسمي الشديد دون توقف بين الدرجات",
         after="بحيث ينتقل تسجيلك من الودي إلى الرسمي دون توقف بين الدرجات"),
    dict(file="المسرد.md", has="الودي الحميم", verdict="خلل",
         why="المسرد يسمّي طرفي السلّم «الودي الحميم (١)» و«الرسمي البروتوكولي (٥)»، والسلّم المعتمد في المشروع كله (الدليل، الباب ٥ §٢؛ وصفحة «الرموز والاصطلاحات» في كل مجلد؛ وجداول الكتاب الستة والثلاثون): ١ أسري، ٢ ودي، ٣ شبه رسمي، ٤ رسمي، ٥ شديد الرسمية. فالمسرد يعرّف الدرجة الأولى باسم الثانية.",
         before="موضع الكلام على السلّم الخماسي: من الودي الحميم (١) إلى الرسمي البروتوكولي (٥).",
         after="موضع الكلام على السلّم الخماسي: من الأسري (١) إلى شديد الرسمية (٥)."),
    # C4 · the severity degrees ----------------------------------------------------------------------------------
    dict(file="ف12-أ-المدخل-والدرسان.md", verdict="خلل",
         has=["| **●** | شديد (حرج) |", "| **◐** | متوسط |", "| **◔** | خفيف |", "| **○** | متقن |"],
         why="«سلّم الشدة الرباعي» في المجلد الثاني يعطي رموز «درجات الخطورة» الأربعة (الدليل، الباب ١٠ §٢؛ وبنك الأخطاء في المجلد الحادي عشر) أسماءً ومعانيَ أخرى: ● شديد/قاتل، ◐ متوسط/مغيّر للمعنى، ◔ خفيف/لافت، ○ متقن (لا خطأ)/هنة (خطأٌ يسير)؛ و◐ في صفحة «الرموز والاصطلاحات» في كل مجلد «عبارةٌ مقبولة». فالضاد تُنطق دالًا ● في المجلد الثاني [م١-ب٢-ف١٢-مث١] و◐ في البنك [م٤-ب١٣-ف٣-مث١]، و○ «لا خطأ» في الأول و«خطأٌ يسير» في الثاني. والسلّم في المجلد الثاني أداةٌ أخرى (أولوية العلاج بحسب تكرار الخطأ) يقوم عليها الفصل الثاني عشر كله (قياس التقدّم «من ● إلى ◐»)؛ فتوحيده بأسماء الدليل يقتضي إعادة وسم الفصل كله، وهو قرارٌ للمؤلف. والمقترح الأدنى: جملةٌ في التعريف تفصل الأداتين.",
         before="> **تعريف:** سلّم الشدة أداة لترتيب الأخطاء المكتشفة بحسب أولوية علاجها، لا بحسب ترتيب ورودها في التسجيل.",
         after="> **تعريف:** سلّم الشدة أداة لترتيب الأخطاء المكتشفة بحسب أولوية علاجها، لا بحسب ترتيب ورودها في التسجيل. وهو غير «درجات الخطورة» في بنك الأخطاء (المجلد الحادي عشر) وإن اشتركا في الرموز: فهي هناك ● قاتل، و◐ مغيّر للمعنى، و◔ لافت، و○ هنة."),
    # C8 · siblings ----------------------------------------------------------------------------------------------
    dict(file="ف07-ب-التكرار-والغموض.md", verdict="خلل",
         has=["| «في الحقيقة» | في أول كل جملة", "| «بصراحة» | إذا لم يكن", "في المثال الأخير لـ«بصراحة» عمل", "«كما تعلمون جميعًا» | قبل ما"],
         why="«في الحقيقة» و«بصراحة» و«كما تعلمون» هي «عبارات الملء» من أنواع الحشو الصوتي في الدرس الأول (ف٧-أ، والمسرد يعدّ «في الحقيقة» منه)، ثم هي في جدول الدرس الثاني «الحشو اللفظي» بعلاجٍ آخر (الحذف لا السكتة)؛ و«الحشو اللفظي» غير مسجّل في السجل. فيُفرَّق بين المصطلحين بالوظيفة في تعريف الثاني، وتبقى أمثلة الدرسين.",
         before="الحشو اللفظي عبارات كاملة لا كلمة واحدة. وهو أخفى من الحشو الصوتي، لأن ألفاظه فصيحة، فيظنه صاحبه زينة.",
         after="الحشو اللفظي عبارات كاملة لا كلمة واحدة، يُمهَّد بها للكلام ولا تُملأ بها سكتة التفكير؛ فإن جاءت «في الحقيقة» و«بصراحة» ملئًا لتلك السكتة فهي من الحشو الصوتي (الدرس الأول). وهو أخفى من الحشو الصوتي، لأن ألفاظه فصيحة، فيظنه صاحبه زينة."),
    dict(file="ف07-ب-التكرار-والغموض.md", has="| **الحشو اللفظي** | «في الحقيقة»، «كما تعلمون» |", verdict="خلل",
         why="جدول الخلاصة يجعل «في الحقيقة» و«كما تعلمون» علامة «الحشو اللفظي» وحده، وهما في الدرس الأول من «الحشو الصوتي»؛ فيُقيَّد المثالان بوظيفتهما في هذا الموضع.",
         before="| **الحشو اللفظي** | «في الحقيقة»، «كما تعلمون» |",
         after="| **الحشو اللفظي** | «في الحقيقة»، «كما تعلمون» تمهيدًا لكل جملة |"),
    # C9 · Latin -------------------------------------------------------------------------------------------------
    dict(file="ف05-أ-الأفعال-وحروف-الجر.md", has="ويقابلها في الإنجليزية", verdict="خلل",
         why="يجعل «Language Transfer» مقابلًا لـ«التدخل اللغوي»، والفصل السادس بعده يجعله مقابل «النقل اللغوي» ويعرّفه بأنه إيجابيٌّ وسلبي؛ فيقع مصطلحٌ لاتينيٌّ واحد على مصطلحين عربيين يفرّق الكتاب بينهما. ثم إن المقابل الأجنبي في الكتاب بين قوسين (الدليل، الباب ١٥ §٢)، لا في سياق الجملة.",
         before="نسمّي هذه الظاهرة **التدخل اللغوي**، ويقابلها في الإنجليزية Interference أو Language Transfer:",
         after="نسمّي هذه الظاهرة **التدخل اللغوي** (Interference):"),
    dict(file="ف05-أ-الأفعال-وحروف-الجر.md", has="الترجمة الحرفية** (Calque)", verdict="خلل",
         why="المقابل الإنجليزي لـ«الترجمة الحرفية» في السجل والمسرد «Literal translation»، وهنا «Calque». (فإن أراد المؤلف «Calque» عُدّل السجل والمسرد معًا.)",
         before="**الترجمة الحرفية** (Calque)", after="**الترجمة الحرفية** (Literal translation)"),
    dict(file="ف06-أ-أثر-اللغات-المحلية.md", has="«النقل اللغوي» (Language Transfer)", verdict="ليس خللًا",
         why="الموضع الصحيح لـ«Language Transfer»؛ والخلل في الفصل الخامس (انظر ما قبله)."),
    dict(file="ملحق-ج-أخطاء-قد-تظهر-عند-بعض-المتعلمين.md", has="(البراغماتية)", verdict="خلل",
         why="مصطلحٌ أجنبي بحروف عربية بين قوسين بعد مقابله العربي («تداولية»)؛ والدليل (الباب ١٥ §٢): «لا يُكتب بحروف عربية».",
         before="## ٥. أخطاء تداولية ومقامية (البراغماتية)", after="## ٥. أخطاء تداولية ومقامية"),
    dict(file="ف06-مخاطبة-الأقران-والأدنى.md", has="«الوجه» (face)", verdict="خلل",
         why="مصطلح غوفمان نفسه مكتوبٌ «(face)» هنا وفي المجلد السادس، و«(Face)» في المجلد العاشر؛ وعُرف الكتاب (السجل، والمسرد، ومثال الدليل «(Register)»، وأكثر المقابلات في المتن) أن يبدأ المقابل بحرفٍ كبير.",
         before="«الوجه» (face)", after="«الوجه» (Face)"),
    dict(file="ف06-أ-المدخل-والدرس-الأول.md", has="«الوجه» (face)", verdict="خلل",
         why="كالموضع السابق: الحرف الأول صغيرٌ هنا، وكبيرٌ في المجلد العاشر.",
         before="«الوجه» (face)", after="«الوجه» (Face)"),
    dict(file="ف02-ب-التحفظ-والسؤال-الحساس.md", has="«الوجه» (Face)", verdict="ليس خللًا",
         why="على عُرف الكتاب؛ والموضعان الآخران يُحملان عليه."),
    dict(file="ف01-العربية-ومستوياتها.md", has="(diglossia)", verdict="خلل",
         why="المقابل الأجنبي بحرفٍ صغير، وعُرف الكتاب الحرف الكبير (السجل، والمسرد، ومثال الدليل «(Register)»).",
         before="الازدواجية اللغوية (diglossia)", after="الازدواجية اللغوية (Diglossia)"),
    dict(file="ف05-ب-الضمير-والتعبيرات-والأزمنة.md", has="(idioms)", verdict="خلل",
         why="المقابل الأجنبي بحرفٍ صغير، على خلاف عُرف الكتاب.",
         before="تعبيراتها الجاهزة (idioms)", after="تعبيراتها الجاهزة (Idioms)"),
    dict(file="ف02-أ-المطابقة.md", has="(error)", verdict="ليس خللًا",
         why="«error» و«mistake» لفظا كوردر في التفريق بين الخطأ والزلة، يُحكيان كما استعملهما في مقالته؛ ولا مقابل لهما في السجل."),
    dict(file="ف02-ب-التحفظ-والسؤال-الحساس.md", has="(conversational implicature)", verdict="ليس خللًا",
         why="في حاشية مصدرٍ تحكي لفظ غرايس في مقالته المذكورة، لا مقابلٌ يقدّمه المتن."),
    dict(file="ف06-ب-البرنامج-والتطبيق.md", has="المحاكاة الصوتية (Shadowing)", verdict="ليس خللًا",
         why="ورد المقابل أولًا في أهداف الفصل، ثم في موضع التعريف بعد صفحات؛ والتعريف موضعه الأول في المتن الشارح، فلا يُعدّ التكرار بين الأهداف والتعريف إعادةً للمقابل."),
    dict(file="ف01-أ-بناء-الجواب.md", has="DDI", verdict="ليس خللًا",
         why="اسم شركةٍ وحروف اسمها (STAR) كما تنسبه إلى نفسها، مع حاشيته؛ لا مصطلح."),
    dict(file="ف03-أ-المفاهيم-والدرس.md", has="lecture", verdict="ليس خللًا",
         why="جدول الأفعال الإنجليزية التي تُترجم حرفيًّا: الإنجليزية فيه موضوع الدرس، لا مقابلٌ لمصطلح."),
    dict(file="ف05-أ-الأفعال-وحروف-الجر.md", has="take", verdict="ليس خللًا",
         why="الأفعال الإنجليزية التي يُدرَس أثرها في الترجمة الحرفية: موضوع الدرس نفسه."),
    dict(file="ف05-أ-الأفعال-وحروف-الجر.md", has="search", verdict="ليس خللًا",
         why="جدول حروف الجر الإنجليزية التي تُنقل حرفيًّا: موضوع الدرس نفسه."),
    dict(file="ف05-ج-التطبيق-والتقويم.md", has="look", verdict="ليس خللًا",
         why="الفعل الإنجليزي موضوع التمرين (الترجمة الحرفية)."),
    dict(file="ف05-ج-التطبيق-والتقويم.md", has="last but not least", verdict="ليس خللًا",
         why="العبارة الإنجليزية موضوع التمرين (الترجمة الحرفية)."),
    dict(file="00-فاتحة-الباب-الثالث.md", has="The meeting", verdict="ليس خللًا",
         why="الجمل الإنجليزية التي يُعرض أصل ترجمتها الحرفية في فاتحة الباب: موضوع الباب."),
    dict(file="ف01-أ-الاسمية-والفعلية.md", has="there is", verdict="ليس خللًا",
         why="تركيبٌ إنجليزي يُشرح أثره في الجملة العربية: موضوع الدرس."),
    dict(file="ف07-ج-التطبيق-والتقويم.md", has="okay", verdict="ليس خللًا",
         why="من تحليل الحشو الأجنبي في الحوار: اللفظ موضوع التحليل."),
    dict(file="ف01-ج-التطبيق-والتقويم.md", has="problem", verdict="ليس خللًا",
         why="من تحليل الحوار: اللفظ الأجنبي الذي دخل كلام المتكلم هو موضوع الملاحظة."),
    dict(file="ف02-أ-المدخل-وبناء-المحاضرة.md", has="Then the bridge", verdict="ليس خللًا",
         why="من تحليل الحوار: العبارة الإنجليزية التي دخلت كلام المحاضر هي موضوع الملاحظة."),
    dict(file="ف01-ب-الأسئلة-والمحاكاة.md", has="perfectionist", verdict="ليس خللًا",
         why="من كلام المتقدّم في الحوار (السطر س١٩)، يُعرض خطأً في المقابلة."),
    dict(file="ف02-ب-المقابلة-الأكاديمية.md", has="passion", verdict="ليس خللًا",
         why="من كلام المتقدّم في الحوار، يُعرض خطأً."),
    dict(file="ف01-ج-الزيارة-الرسمية-والتقويم.md", has="MoU", verdict="ليس خللًا",
         why="من كلام المدير في الحوار، يُعرض خطأً."),
]

# the ledger, the glossary and the Bible against one another (C10): the readings of what the comparison finds
READ_SOURCES = {
    "ledger-stale:مستوى البرنامج": dict(verdict="خلل",
        why="تعريف السجل «مرحلة من المستويات صفر إلى اثني عشر» من البنية القديمة، والمسرد «من الأول إلى الثالث عشر، ورقم كل مستوى رقم بابه»؛ والسجل يُولَّد من المسرد (pdf/terms.py) ولم يُعد توليده.",
        before="مرحلة من المستويات صفر إلى اثني عشر في منهج الكتاب.",
        after="مرحلةٌ من المستويات الثلاثة عشر في منهج الكتاب، من الأول إلى الثالث عشر، ورقم كل مستوى رقم بابه.",
        where="سجل-المصطلحات.tsv (بإعادة `python3 pdf/terms.py`)"),
    "bible-number:مستوى البرنامج": dict(verdict="خلل",
        why="جدول الدليل (الباب ١٦) يعرّف «مستوى البرنامج» بـ«مرحلة من المستويات ٠–١٢»، والبنية المثبّتة (الباب ١١٢د) ثلاثة عشر مستوى من الأول؛ فالدليل هنا متأخرٌ عن قراره.",
        before="| **مستوى البرنامج** | مرحلة من المستويات ٠–١٢. | — |",
        after="| **مستوى البرنامج** | مرحلة من المستويات ١–١٣، ورقم كل مستوى رقم بابه. | — |",
        where="bible/05، الباب ١٦"),
    "card-fields": dict(verdict="خلل",
        why="تعريف «بطاقة المقام» في المسرد يعدّ ستة بنود، والبطاقة في الدليل (الباب ٦ §١) وصفحة الرموز وبطاقات الكتاب ثمانية: يسقط منه «العلاقة» و«الأثر المطلوب».",
        before="الإطار الإلزامي فوق كل نموذج مهم: المتكلم، والمخاطَب، والمكان والمناسبة، والغرض، ودرجة الرسمية، والزمن المتاح.",
        after="الإطار الإلزامي فوق كل نموذج مهم: المتكلم، والمخاطَب، والعلاقة بينهما، والمكان والمناسبة، والغرض، والأثر المطلوب، ودرجة الرسمية، والزمن المتاح.",
        where="المجلد-الحادي-عشر/الخواتيم/المسرد.md (ثم السجل بـ`python3 pdf/terms.py`)"),
    "ledger-alternatives": dict(verdict="خلل",
        why="عمود «البدائل الممنوعة» في السجل فارغٌ إلا في مصطلحين، وعمود «لا يُستعمل بدله» في جدول الدليل (الباب ١٦) يملأ أكثر مصطلحاته؛ والسجل هو الذي يُرجع إليه في التحرير (الباب ٦٥). يُنقل عمود الدليل إلى `SETTLED` في `pdf/terms.py` ثم يُعاد توليد السجل.",
        before="", after="", where="pdf/terms.py → سجل-المصطلحات.tsv"),
    "unused:التعبير الطبيعي": dict(verdict="خلل",
        why="المسرد والسجل يعتمدان «التعبير الطبيعي» ولا يرد في المتن إلا مرة، والمتن يعرّف في «**تعريف:**» مفهومه نفسه باسم «العربية الطبيعية» (المجلد الأول، الباب الأول، ف٣-أ) ويستعمله سبع عشرة مرة، ولا يعرفه المسرد. فإما أن يُسجَّل «العربية الطبيعية» بتعريف المتن ويُجعل «التعبير الطبيعي» علاقةً له، وإما العكس؛ وهو قرارٌ للمؤلف.",
        before="", after="", where="المسرد والسجل"),
    "unused:مستوى البرنامج": dict(verdict="ليس خللًا",
        why="المصطلح يسمّي المفهوم، والمتن يستعمله بصيغة «المستوى ١»… على ما قرّرته صفحة «الرموز والاصطلاحات» («المستوى: درجة البرنامج التدريبي»)؛ فلا يلزم لفظه.",
        before="", after="", where="المسرد"),
    "undefined-in-ledger": dict(verdict="خلل",
        why="مصطلحاتٌ يعرّفها المتن في «**تعريف:**» ولا يعرفها السجل؛ والباب ٦٥ يجعل لكل مصطلحٍ سطرًا فيه. أولاها بالتسجيل ما له شقيقٌ في السجل يُخلط به: «الحشو اللفظي» (بجوار الحشو الصوتي)، و«العربية الطبيعية» (بجوار التعبير الطبيعي)، و«المحاكاة الصوتية» (بجوار المحاكاة)، و«سلّم الشدة» (بجوار درجات الخطورة)، و«التدخل اللغوي» و«النقل اللغوي».",
        before="", after="", where="سجل-المصطلحات.tsv"),
}
# observations that belong to the author and the Bible, not to a line of the text (they are reported, not replaced)
OBSERVE = [
    ("«المحاكاة» بمعنيين",
     "السجل والمسرد يعرّفان «المحاكاة» بأنها أداء موقفٍ واقعي بأدوارٍ محددة (Simulation)، ثم يعرّف السجل نفسه «الملكة الشفهية» بأنها "
     "«تُكتسب بالسماع والمحاكاة والتكرار»، أي التقليد؛ والمتن يستعمل المعنيين، ويستعمل «المحاكاة» وحدها في الفصل السادس من الباب "
     "الأول بمعنى «المحاكاة الصوتية» (Shadowing). المقترح أن يُسجَّل المعنى الثاني في عمود «العلاقة المفهومية»، وأن تُسجَّل "
     "«المحاكاة الصوتية» مصطلحًا مستقلًّا."),
    ("«المستوى» بمعنيين",
     "صفحة «الرموز والاصطلاحات» في كل مجلد والدليل (الباب ١٦) يخصّان «المستوى» بمستويات البرنامج، والدليل نفسه (الباب ٣١) والافتتاحية "
     "والمدخل يسمّون ضروب العربية «مستويات» («خمسة مستويات»). فيلقى قارئ المجلد الأول «المستوى» بالمعنيين؛ والفصل بينهما قرارٌ في "
     "الدليل قبل المتن."),
    ("◐ بثلاثة معانٍ",
     "◐ في الدليل (الباب ١٥) وصفحة الرموز «عبارةٌ مقبولة»، وفي الباب ١٠ «مغيّر للمعنى»، وفي المجلد الثاني «متوسط». والموضع الثالث "
     "مبيَّنٌ أعلاه؛ والأوّلان قرارٌ في الدليل، ورموز الخطورة الأربعة ليست في صفحة الرموز وإن استعملها المجلدان الثاني والحادي عشر."),
]


# the first words of a definition that are not the term
DEF_OPEN = set("""هو هي أن أي ما من في مجموع اختيار أصوات نقل قدرة تدريب أداء حالة مطابقة سلامة عبارات أداة جدول طريقة
توقف وصف تخل تخلٍّ بيان ختم طلب عرض استعمال حصر الدلالة التعبير توافق تشابه الجمع إبراز صوت نون قطع استئناف مد همزة تمام
ارتفاع قائمة كيفية أسلوب مخالفة كلام حرص خلو كلمة كلمتان عبارة طلاقة هنا شدة جواب ما يقوله ترك لغة""".split())


def defined_term(head):
    head = head.strip()
    m = re.match(r"^\*\*([^*]+)\*\*", head) or re.match(r"^«([^»]+)»", head)
    if m:
        return re.sub(r"\s*\([^)]*\)", "", m.group(1)).strip()
    words = []
    for w in head.split():
        bare = w.strip("*«»،:.؛")
        if not bare or w.startswith("(") or bare in DEF_OPEN:
            break
        words.append(bare)
        if w.endswith((":", "،", ".", "؛")) or len(words) == 4:
            break
    return " ".join(words)


# ----------------------------------------------------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------------------------------------------------

class Audit:
    def __init__(self, companions=False):
        self.companions = companions
        self.led = ledger()
        self.gl = glossary()
        self.b16 = bible_ch16()
        self.scale = bible_scale()
        self.card = bible_card()
        self.classes, self.degrees = bible_errors()
        self.concepts = bible_concepts()
        self.texts = [Text(f, v) for f, v in series_files(companions)]
        self.findings = []
        self.sources = []                     # C10
        self.forms = defaultdict(Counter)     # C7 inventory
        self.glosses = []                     # C9 inventory
        self.defined = {}                     # «**تعريف:**» terms of the text

    def add(self, t, check, lineno, match, note):
        self.findings.append(dict(check=check, file=t.rel, vol=t.vol, line=lineno, match=match,
                                  text=t.lines[lineno - 1], around=t.around(lineno, match), note=note))

    def scan(self, t, pattern, check, note, which="prose", group=0):
        src = t.prose if which == "prose" else t.mention
        for m in re.finditer(pattern, src):
            ln = t.line_of(m.start(), which)
            self.add(t, check, ln, m.group(group).strip(), note)

    # C1 · C8 ------------------------------------------------------------------------------------------------------
    def forbidden(self, t):
        for approved, alts, why in FAMILIES:
            for a in alts:
                self.scan(t, NOT_L + PROCLITIC + re.escape(a) + END_L, "C1 بديلٌ من مصطلحٍ معتمد", f"«{a}» ← «{approved}». {why}")
        for m in FAILED.finditer(t.prose):
            before = t.prose[max(0, m.start() - 70): m.start()]
            if re.search(r"الناجح|ناجح", before) or re.search(PERFORMANCE + r"ا?\s*$", before):
                self.add(t, "C1 بديلٌ من مصطلحٍ معتمد", t.line_of(m.start()), m.group(0).strip(),
                         "«الفاشل» وصفًا لأداءٍ في مقابل «الناجح»: البديل الممنوع في السجل؛ والوثيقة الحاكمة (القاعدة ٤)")
        if "بنك" not in t.rel:
            self.scan(t, SCENARIO, "C1 بديلٌ من مصطلحٍ معتمد", "«السيناريو» لا يُستعمل إلا في بنك المواقف (الدليل، الباب ١٦)")
        self.scan(t, rf"الطلاقة\s*(?:،\s*)?(?:أي|يعني|هي|وهي)\s*(?:ال)?سرعة", "C1 بديلٌ من مصطلحٍ معتمد",
                  "«الطلاقة» ليست «السرعة» (الدليل، الباب ١٦؛ والمسرد)")
        self.scan(t, rf"^\|\s*\*\*(?:المستمع|المستمعون|السامع)\*\*\s*\|", "C1 بديلٌ من مصطلحٍ معتمد",
                  "بند «المخاطَب» في بطاقة المقام؛ و«المستمع» أعمّ (الدليل، الباب ١٦)")
        self.scan(t, rf"{NOT_L}{SPEAKER}\s+{NOT_GRADES}{END_L}", "C1 بديلٌ من مصطلحٍ معتمد",
                  "وصفٌ للمتكلم بغير الدرجات الأربع (الدليل، الباب ١٦)")

    # C2 -------------------------------------------------------------------------------------------------------------
    def grades(self, t):
        for i, line in enumerate(t.lines, 1):
            m = re.match(r"^\s*\*\*\s*([①②③④])\s*([^*«\[]+?)\s*\*\*\s*$", line)
            if not m:
                continue
            label = N(m.group(2))
            found = [g for g in GRADES.values() if re.search(rf"(?:^|\s){g}(?:ة)?(?:\s|$)", label)]
            found = [g for g in found if not (g == "الناجح" and "غير الناجح" in label)]
            bad = NOT_GRADES_RX.search(label)
            if bad:
                self.add(t, "C2 الدرجات الأربع", i, N(m.group(0).strip()),
                         f"«{bad.group(0)}» في موضع الدرجة {m.group(1)} ({GRADES[m.group(1)]})")
            elif found and GRADES[m.group(1)] not in found:
                self.add(t, "C2 الدرجات الأربع", i, N(m.group(0).strip()),
                         f"الرمز {m.group(1)} للدرجة «{GRADES[m.group(1)]}»، والتسمية «{label}»")

    # C3 -------------------------------------------------------------------------------------------------------------
    def formality(self, t):
        names = {v.replace("ال", "", 1) if v.startswith("ال") else v for v in self.scale.values()}
        rows = list(re.finditer(r"^\|\s*\*\*([١-٥])\s+([^*|]+?)\s*\*\*\s*\|", t.prose, re.M))
        tables = defaultdict(list)                          # consecutive rows are one table
        for m in rows:
            tables[t.line_of(m.start()) - len([x for x in rows if t.line_of(x.start()) < t.line_of(m.start())])].append(m)
        for group in tables.values():
            if sum(N(m.group(2)).strip() in self.scale.values() for m in group) < 3:
                continue                                    # another five-step scale (a commitment, a priority)
            for m in group:
                nm = N(m.group(2)).strip()
                if nm != self.scale[m.group(1)]:
                    self.add(t, "C3 سلّم الرسمية", t.line_of(m.start()), m.group(0).strip("| "),
                             f"الدرجة {m.group(1)} اسمها «{self.scale[m.group(1)]}» (الدليل، الباب ٥ §٢)")
        for m in re.finditer(r"درجة الرسمية\**\s*\|\s*\**([١-٥])\s*\(([^)]+)\)", t.prose):
            nm = N(m.group(2)).strip()
            if nm in names and nm != self.scale[m.group(1)]:
                self.add(t, "C3 سلّم الرسمية", t.line_of(m.start()), m.group(0),
                         f"الدرجة {m.group(1)} اسمها «{self.scale[m.group(1)]}»")
        for odd in SCALE_ODD:
            self.scan(t, NOT_L + PROCLITIC + re.escape(odd) + END_L, "C3 سلّم الرسمية",
                      f"«{odd}» ليس اسم درجةٍ في السلّم المعتمد: {'، '.join(f'{k} {v}' for k, v in sorted(self.scale.items()))}")

    # C4 -------------------------------------------------------------------------------------------------------------
    def errors(self, t):
        for m in re.finditer(r"خ-([٠-٩]+)\s*\(([^)]+)\)", t.mention):
            before = t.mention[max(0, m.start() - 4): m.start()]
            if "/" in before:
                continue                                    # «خ-١ / خ-١٧ (…)»: one label for two classes
            label = re.split(r"[؛،]", N(m.group(2)))[0].strip()
            want = self.classes.get(m.group(1))
            if want and label != want and not want.startswith(label):
                self.add(t, "C4 التصنيف والخطورة", t.line_of(m.start(), "mention"), m.group(0),
                         f"خ-{m.group(1)} في الدليل (الباب ١٠) «{want}»")
        rows = [(m, "table") for m in re.finditer(r"^\|\s*\*\*([●◐◔○])\*\*\s*\|\s*\**([^|*(]+?)\**\s*(?:\(|\|)", t.mention, re.M)]
        rows += [(m, "card") for m in re.finditer(r"([●◐◔○])\s*([\u0621-\u064A]+(?:\s+[\u0621-\u064A]+){0,2}?)\s*(?=/|$)", t.mention, re.M)
                 if "الخطورة" in t.mention[t.mention.rfind("\n", 0, m.start()) + 1: m.start()]]
        for m, kind in rows:
            nm, want = N(m.group(2)).strip(), self.degrees.get(m.group(1))
            if want and nm != want and not nm.startswith(want):
                self.add(t, "C4 التصنيف والخطورة", t.line_of(m.start(), "mention"), f"{m.group(1)} {nm}",
                         f"{m.group(1)} في الدليل (الباب ١٠ §٢) «{want}»")

    # C5 · C6 --------------------------------------------------------------------------------------------------------
    def lists(self, t):
        crit, conc = set(CRITERIA_WORDS), set(CONCEPTS_WORDS)
        for m in re.finditer(r"(المعايير الخمسة|معاييره الخمسة|معايير الكلام الخمسة|المفاهيم الخمسة|خمسة مفاهيم|خمسة معايير)", t.prose):
            seg = t.prose[m.end(): m.end() + 170]
            found = [w for w in re.findall(r"(?:[وب]|ل)?(ال[\u0621-\u064A]+)", seg) if w in crit | conc]
            if len(set(found)) >= 3:
                want = crit if "معايير" in m.group(1) or "معاييره" in m.group(1) else conc
                extra = set(found[:5]) - want
                if extra:
                    self.add(t, "C5 المعايير والمفاهيم", t.line_of(m.start()), m.group(0),
                             f"في قائمة «{m.group(1)}» ما ليس منها: {'، '.join(sorted(extra))}")
        for m in re.finditer(r"(?:ال)?[\u0621-\u064A]+(?:[،,]?\s*(?:و|أو\s+)?(?:ال)[\u0621-\u064A]+){3,}", t.prose):
            ws = set(re.findall(r"ال[\u0621-\u064A]+", m.group(0)))
            if len(ws & crit) >= 4 and ws & (conc - crit) or len(ws & conc) >= 4 and ws & (crit - conc):
                self.add(t, "C5 المعايير والمفاهيم", t.line_of(m.start()), m.group(0)[:80],
                         "قائمةٌ تخلط المعايير الخمسة بالمفاهيم الخمسة (الدليل، الباب ٣١)")
        pat = (r"(?:ال)?فصاحة\s*(?:أو|أي|،\s*أي|\(|/)\s*(?:ال)?بلاغة|(?:ال)?بلاغة\s*(?:أو|أي|،\s*أي|\(|/)\s*(?:ال)?فصاحة"
               r"|الفصاحة\s+(?:هي\s+)?مطابقة|البلاغة\s+(?:هي\s+)?(?:سلامة|خلوص)")
        self.scan(t, pat, "C6 الفصاحة والبلاغة", "لا يُخلط بينهما (الدليل، البابان ١٦ و٣١؛ والسجل)")

    # C7 -------------------------------------------------------------------------------------------------------------
    def spelling(self, t, terms):
        for term, p in terms:
            for m in p.finditer(t.prose):
                s = m.group(0)
                cands = [s] + ([s[1:]] if s[0] in "وفبكل" else []) + (["ال" + s[2:]] if s.startswith("لل") else [])
                bare = next((c for c in cands if fold(c) == fold(term)), s)
                if strip_art(bare) == strip_art(term):
                    self.forms[term][bare] += 1
                t_words, s_words = term.split(), bare.split()
                if len(t_words) != len(s_words):
                    continue
                for tw, sw in zip(t_words, s_words):
                    core_t, core_s = tw[2:] if tw.startswith("ال") else tw, sw[2:] if sw.startswith("ال") else sw
                    if core_t == core_s:
                        continue
                    diff = [(a, b) for a, b in zip(core_t, core_s) if a != b]
                    kinds = set()
                    for a, b in diff:
                        if {a, b} <= set("اأإآ"):
                            kinds.add("همزة")
                        elif {a, b} == {"ى", "ي"}:
                            kinds.add("ى/ي")
                        elif {a, b} == {"ة", "ه"} and sw.startswith("ال"):
                            kinds.add("ة/ه")
                    if kinds and len(core_t) >= 4:
                        self.add(t, "C7 رسم المصطلح", t.line_of(m.start()), s,
                                 f"«{sw}» بدل «{tw}» ({'، '.join(sorted(kinds))})")
            # the article: «الغير ناجح», and an article on the head of an idafa term
        for a in ("البطاقة المقام", "الدرجة الرسمية", "المقتضى الحال", "المستوى البرنامج"):
            self.scan(t, NOT_L + PROCLITIC + a + END_L, "C7 رسم المصطلح", f"أداة التعريف على المضاف: «{a}»")

    # C8 -------------------------------------------------------------------------------------------------------------
    def siblings(self, t, ext):
        heading = ""
        for i, line in enumerate(t.lines, 1):
            n = N(line)
            if line.lstrip().startswith("#"):
                heading = n
            if EXAMPLE_LINE.match(line):
                continue
            here = [a for pair in SIBLINGS for a in pair if a in n]
            under = [a for pair in SIBLINGS for a in pair if a in heading]
            owners = here or under
            if len(owners) != 1:
                continue
            for q in re.findall(r"«([^«»]{2,24})»", n):
                q = q.strip(" .،…")
                if len(q.split()) <= 3:
                    ext[owners[0]][q].append((t, i))

    # C9 -------------------------------------------------------------------------------------------------------------
    def latin(self, t):
        if "ملحق-ب" in t.rel:                           # the dictionary of literal translation is made of English
            return
        for m in re.finditer(r"\(\s*([A-Za-z][A-Za-z '\-/]*[A-Za-z])\s*\)", t.mention):
            gloss = m.group(1)
            if "," in gloss or len(gloss.split()) > 4:
                continue
            before = t.mention[max(0, m.start() - 60): m.start()].rstrip()
            term = None
            for rx in (r"\*\*([^*]+)\*\*$", r"«([^«»]+)»$", rf"((?:{NOT_L}[{L}]+\s+)?{NOT_L}(?:[وفبل])?ال[{L}]+)$",
                       rf"({NOT_L}(?:[وفبل])?ال[{L}]+\s+[{L}]+)$"):
                mm = re.search(rx, before)
                if mm:
                    term = mm.group(1).strip()
                    break
            if not term or len(term.split()) > 4 or not re.match(r"^[\u0621-\u064A]", term):
                continue
            if rx == r"«([^«»]+)»$" and not term.startswith("ال") and not gloss[0].isupper():
                continue                                    # a phrase in quotation: a translated expression
            ln = t.line_of(m.start(), "mention")
            self.glosses.append((t, ln, re.sub(r"^[وفبل](?=ال)", "", term), gloss))
        for m in re.finditer(r"\(\s*(?:ال)?([\u0621-\u064A]+)\s*\)", t.prose):
            if any(m.group(1).startswith(x.replace(" ", "")) for x in TRANSLIT):
                self.add(t, "C9 المقابل الأجنبي", t.line_of(m.start()), m.group(0),
                         "مصطلحٌ أجنبي بحروف عربية (الدليل، الباب ١٥ §٢)")
        if "المسرد" in t.rel:
            return
        for i, line in enumerate(t.prose.split("\n"), 1):
            if t.lines[i - 1].startswith("[^"):
                continue                                    # notes: authors and titles in Latin
            if not re.search(f"[{L}]", line):
                continue                                    # an English sentence shown whole: an example, not a gloss
            bare = re.sub(r"\([^()]*\)", "", line)
            for m in re.finditer(r"[A-Za-z][A-Za-z'\-]{2,}(?:\s+[A-Za-z][A-Za-z'\-]*)*", bare):
                self.add(t, "C9 المقابل الأجنبي", i, m.group(0),
                         "لاتينيةٌ في سياق الجملة؛ والمقابل الأجنبي بين قوسين (الدليل، الباب ١٥ §٢)")

    def latin_series(self):
        by_term, by_latin = defaultdict(list), defaultdict(list)
        vol_seen = defaultdict(list)
        led_en = {N(r["الرسم المعتمد"] or r["المصطلح"]): r["المقابل الإنجليزي"].strip() for r in self.led}
        for t, ln, term, gloss in self.glosses:
            key = term[2:] if term.startswith("ال") else term
            by_term[key].append((t, ln, term, gloss))
            by_latin[gloss.lower()].append((t, ln, term, gloss))
            vol_seen[(t.vol, key, gloss.lower())].append((t, ln, term, gloss))
            if gloss[0].islower() and not gloss.isupper():
                self.add(t, "C9 المقابل الأجنبي", ln, f"({gloss})",
                         "المقابل الأجنبي يبدأ بحرفٍ صغير، وعُرف الكتاب الحرف الكبير (السجل، والمسرد، ومثال الدليل «(Register)»)")
            want = led_en.get(term) or led_en.get("ال" + term)
            if want and gloss.lower() != want.lower() and "المسرد" not in t.rel:
                self.add(t, "C9 المقابل الأجنبي", ln, f"({gloss})",
                         f"مقابل «{term}» في السجل والمسرد «{want}»")
        for key, occ in by_term.items():
            variants = {g for _, _, _, g in occ}
            if len(variants) > 1:
                for t, ln, term, g in occ:
                    self.add(t, "C9 المقابل الأجنبي", ln, f"({g})",
                             f"«{term}» بمقابلين أو أكثر في السلسلة: {'، '.join(sorted(variants))}")
        for lat, occ in by_latin.items():
            terms = {k[2:] if k.startswith("ال") else k for _, _, k, _ in occ}
            if len(terms) > 1:
                for t, ln, term, g in occ:
                    self.add(t, "C9 المقابل الأجنبي", ln, f"({g})",
                             f"«{g}» مقابلٌ لأكثر من مصطلح: {'، '.join(sorted(terms))}")
        for (vol, key, lat), occ in vol_seen.items():
            if vol is not None and len(occ) > 1:
                for t, ln, term, g in occ[1:]:
                    self.add(t, "C9 المقابل الأجنبي", ln, f"({g})",
                             f"المقابل مكرّر في المجلد نفسه، والدليل (الباب ١٥ §٢): «عند أول وروده فقط»")
        # inline Latin that stands for a term: the nearest bold term in its line
        for t in self.texts:
            for m in re.finditer(r"\*\*([^*\n]+)\*\*[^\n]{0,40}?في الإنجليزية\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)"
                                 r"(?:\s+أو\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*))?", t.mention):
                for lat in filter(None, (m.group(2), m.group(3))):
                    others = {k for _, _, k, _ in by_latin.get(lat.lower(), [])} - {m.group(1)}
                    if others:
                        self.add(t, "C9 المقابل الأجنبي", t.line_of(m.start(), "mention"), lat,
                                 f"«{lat}» مقابل «{m.group(1)}» هنا، ومقابل «{'، '.join(sorted(others))}» في موضعٍ آخر")

    # C10 ------------------------------------------------------------------------------------------------------------
    def sources_check(self):
        for r in self.led:
            term = N(r["الرسم المعتمد"] or r["المصطلح"])
            g = self.gl.get(term)
            if g and N(r["التعريف"]).strip() != g[0]:
                self.sources.append(("ledger-stale:" + term, f"تعريف «{term}» في السجل غير تعريفه في المسرد",
                                     N(r["التعريف"]).strip(), g[0]))
            if g and r["المقابل الإنجليزي"].strip() != g[1]:
                self.sources.append(("ledger-en:" + term, f"مقابل «{term}» في السجل غير مقابله في المسرد",
                                     r["المقابل الإنجليزي"], g[1]))
        for term, (defn, alts, notes) in self.b16.items():
            g = self.gl.get(term)
            if g:
                nb = set(re.findall(r"[٠-٩]+|صفر|اثني عشر|الثالث عشر", defn))
                ng = set(re.findall(r"[٠-٩]+|صفر|اثني عشر|الثالث عشر", g[0]))
                if nb and nb != ng:
                    self.sources.append(("bible-number:" + term, f"أعداد «{term}» في الدليل غير أعداده في المسرد", defn, g[0]))
        missing = []
        led = {N(r["الرسم المعتمد"] or r["المصطلح"]): r for r in self.led}
        for term, (defn, alts, notes) in self.b16.items():
            have = N(led.get(term, {}).get("البدائل الممنوعة", ""))
            lack = [a for a, note in zip(alts, notes) if a not in have and not note.startswith(("يُستعمل", "يستعمل", "لا يخلط", "لا يُخلط"))]
            if lack:
                missing.append(f"{term}: {'، '.join(lack)}")
        if missing:
            self.sources.append(("ledger-alternatives", "البدائل الممنوعة في الدليل (الباب ١٦) وليست في السجل", "؛ ".join(missing), ""))
        card = self.gl.get("بطاقة المقام")
        if card:
            lack = [f for f in self.card if f not in ("الزمان", "المناسبة") and N(f).replace("العلاقة بينهما", "العلاقة") not in card[0]]
            if lack:
                self.sources.append(("card-fields", "بنود بطاقة المقام في الدليل (الباب ٦ §١) الغائبة عن تعريفها في المسرد",
                                     "، ".join(lack), card[0]))
        # usage of the approved forms, and the terms the text defines that the ledger lacks
        usage = Counter()
        for t in self.texts:
            if "المسرد" in t.rel:
                continue
            for term in led:
                usage[term] += len(re.findall(NOT_L + PROCLITIC + re.escape(term) + END_L, t.prose))
            for m in re.finditer(r"\*\*تعريف:?\*\*:?\s*([^\n]{0,90})", t.norm_raw):
                term = defined_term(m.group(1))
                if term and term not in led and ("ال" + term) not in led and fold(term) not in {fold(k) for k in led}:
                    self.defined.setdefault(term, (t, t.line_of(m.start(), "raw")))
        self.usage = usage
        if self.defined:
            self.sources.append(("undefined-in-ledger", f"مصطلحاتٌ معرَّفة في المتن غائبة عن السجل ({ar(len(self.defined))})",
                                 "، ".join(f"«{k}»" for k in sorted(self.defined)), ""))
        for term in led:
            if term in self.gl and usage[term] <= 1:
                self.sources.append(("unused:" + term, f"«{term}» معتمدٌ في المسرد، ولا يرد في المتن "
                                     + ("إلا مرةً واحدة" if usage[term] == 1 else "بلفظه"), "", ""))

    # -----------------------------------------------------------------------------------------------------------------
    def run(self):
        terms = []
        for r in self.led:
            term = N(r["الرسم المعتمد"] or r["المصطلح"])

            def word(w):
                core = w[2:] if w.startswith("ال") else w
                cls = {"ا": "[اأإآ]", "أ": "[اأإآ]", "إ": "[اأإآ]", "آ": "[اأإآ]", "ى": "[ىي]", "ي": "[ىي]", "ة": "[ةه]"}
                return "(?:ال|لل)?" + "".join(cls.get(c, re.escape(c)) for c in core)
            terms.append((term, re.compile(NOT_L + "(?:[وفبكل])?" + r"\s+".join(word(w) for w in term.split()) + END_L)))
        ext = defaultdict(lambda: defaultdict(list))
        for t in self.texts:
            self.forbidden(t)
            self.grades(t)
            self.formality(t)
            self.errors(t)
            self.lists(t)
            self.spelling(t, terms)
            self.siblings(t, ext)
            self.latin(t)
        # the glossary is read like the text for C8: its definition of a term lists that term's examples
        for a, b in SIBLINGS:
            shared = set(ext[a]) & set(ext[b])
            for q in sorted(shared):
                for t, i in ext[b][q]:
                    loci = "؛ ".join(f"{x.rel.split('/')[-1]}:{ar(j)}" for x, j in ext[a][q][:4])
                    self.add(t, "C8 مصطلحان على أمثلةٍ واحدة", i, f"«{q}»",
                             f"«{q}» مثالٌ لـ«{b}» هنا، ولـ«{a}» في: {loci}")
        self.latin_series()
        self.sources_check()
        self.judge()

    def judge(self):
        """Attach every reading to what it reads; a reading whose text is gone says so."""
        seen = set()
        uniq = []
        for f in self.findings:
            k = (f["file"], f["line"], f["check"], f["match"])
            if k in seen:
                continue
            seen.add(k)
            cand = [r for r in READ if f["file"].endswith(r["file"]) and any(N(h) in N(f["text"]) for h in phrases(r))]
            m = N(f["match"])
            best = [r for r in cand if m and any(m in N(h) or N(h) in m for h in phrases(r))]
            f["read"] = (best or cand or [None])[0]
            uniq.append(f)
        self.findings = uniq
        self.stale = []
        for r in READ:
            if r["verdict"] != "خلل":
                continue
            hits = [t for t in self.texts if t.rel.endswith(r["file"])]
            if not hits and not self.companions and "_المرافقة" not in r["file"] and "نصوص-الحلقات" not in r["file"]:
                self.stale.append((r, "الملف غير موجود"))
            elif hits and not any(r["before"] in t.raw for t in hits):
                self.stale.append((r, "النص الحالي لم يعد في الملف كما هو"))


# ----------------------------------------------------------------------------------------------------------------
# the report
# ----------------------------------------------------------------------------------------------------------------

def phrases(r):
    return r["has"] if isinstance(r["has"], list) else [r["has"]]


def where(f):
    parts = f["file"].split("/")
    vol = "المرافقة" if f["vol"] is None else f"المجلد {VOLW[f['vol'] - 1]}"
    return f"{vol} · `{'/'.join(parts[1:]) if f['vol'] is not None else '/'.join(parts[1:])}`:{ar(f['line'])}"


def cell(s):
    return s.replace("|", "\\|").replace("\n", " ")


def report(a):
    fs = a.findings
    genuine = [f for f in fs if f["read"] and f["read"]["verdict"] == "خلل"]
    cleared = [f for f in fs if f["read"] and f["read"]["verdict"] == "ليس خللًا"]
    unread = [f for f in fs if not f["read"]]
    # one proposal per reading (a reading may answer several flags on its line)
    props, seenr = [], set()
    for f in genuine:
        k = id(f["read"])
        if k in seenr:
            for p in props:
                if p[1] is f["read"]:
                    p[2].append(f["check"])
            continue
        seenr.add(k)
        props.append((f, f["read"], [f["check"]]))
    series = [p for p in props if p[0]["vol"] is not None]
    comp = [p for p in props if p[0]["vol"] is None]
    checks = Counter(f["check"] for f in fs)
    md = ["# تدقيق المصطلحات: السلسلة كلها", "",
          "يُولَّد هذا الملف من `python3 pdf/termaudit.py` (الدليل، البابان ١٦ و٦٥؛ والباب ٣١ للمفاهيم الخمسة، والباب ١٥ §٢ "
          "للمصطلح الأجنبي، والباب ٥ §٢ والباب ١٠ للسلّمين، والوثيقة الحاكمة، القاعدة ٤). تقرأ الأداة سجلّ المصطلحات والمسرد "
          "وجداول الدليل، ثم تمرّ على المجلدات الأحد عشر" + ("، والكتابين المرافقين" if a.companions else "") + " كلمةً كلمة.", "",
          "**ما لا تقرؤه:** النصّ المنقول والمذكور بين «» و﴿﴾، والشعر والحديث المشكولان، وكلام الشخصيات (الاقتباسات المسبوقة "
          "باسم المتكلم أو المفتوحة بـ« أو [)، وأعمدة الكلام في جداول الحوار، وإرشادات الأداء بين معقوفين، وسطور الأمثلة التي تعرض "
          "خطأً أو صيغةً مقبولة (✘، ◐، «الخطأ:»)، وخانات الخطأ في الجداول، وعناوين الكتب في الحواشي، وأثبات المصادر. فالكتاب "
          "كتابُ أخطاء، والخطأ المعروض قصدًا ليس خللًا في المصطلح؛ والنقل المتحقّق يبقى بلفظه.", "",
          "**وكل موضعٍ أشارت إليه الأداة قُرئ في سياقه:** فما كان خللًا حُمل عليه نصّه الحالي بحروفه والبديلُ المقترح، وتتحقّق "
          "الأداة في كل تشغيلٍ أن النص الحالي ما زال في ملفه؛ وما لم يكن خللًا كُتب سببه. ولا تعدّل الأداة شيئًا في `book/` ولا `bible/`.", "",
          "## الخلاصة", "",
          f"- ملفاتٌ قُرئت: {ar(len(a.texts))}؛ ومصطلحات السجل: {ar(len(a.led))}؛ وجدول الدليل (الباب ١٦): {ar(len(a.b16))}.",
          f"- مواضع أشارت إليها الأداة: {ar(len(fs))}؛ منها **{ar(len(genuine))} خللًا** يُصلَح في {ar(len(props))} موضعًا، "
          f"و{ar(len(cleared))} قُرئت فليست خللًا، و{ar(len(unread))} لم تُقرأ بعد.",
          f"- خللٌ في السجل والمسرد والدليل (لا في سطرٍ من المتن): {ar(len([s for s in a.sources if s[0] in READ_SOURCES and READ_SOURCES[s[0]]['verdict'] == 'خلل']))}.",
          ""]
    if a.stale:
        md += ["**تنبيه:** قراءاتٌ لم يعد نصّها في موضعه (عُدّل الملف بعد القراءة؛ تُراجع):", ""]
        md += [f"- `{r['file']}`: {why} — «{r['before']}»" for r, why in a.stale] + [""]
    md += ["| الفحص | مواضع أشار إليها | خلل | ليس خللًا |", "|---|---|---|---|"]
    for c in sorted(set(checks) | set(CHECKS)):
        md.append(f"| {c} | {ar(checks[c])} | {ar(sum(1 for f in genuine if f['check'] == c))} | "
                  f"{ar(sum(1 for f in cleared if f['check'] == c))} |")
    md += [""]

    def section(title, items):
        out = [f"## {title}", ""]
        if not items:
            return out + ["لا شيء.", ""]
        out += ["| # | الموضع | النص الحالي | المشكلة | البديل المقترح |", "|---|---|---|---|---|"]
        for k, (f, r, cks) in enumerate(items, 1):
            raw = (BOOK / f["file"]).read_text(encoding="utf-8")
            ln = raw[: raw.find(r["before"])].count("\n") + 1 if r["before"] in raw else f["line"]
            out.append(f"| {ar(k)} | {where(dict(f, line=ln))} | {cell(r['before'])} | {cell(r['why'])} | {cell(r['after'])} |")
        return out + [""]

    md += section("أولًا: خللٌ في متن المجلدات، ببديله", sorted(series, key=lambda p: (p[0]["vol"], p[0]["file"], p[0]["line"])))
    if a.companions:
        md += section("ثانيًا: خللٌ في الكتابين المرافقين", comp)
    md += ["## " + ("ثالثًا" if a.companions else "ثانيًا") + ": خللٌ في السجل والمسرد والدليل", "",
           "ما يلي لا يُصلَح في سطرٍ من المتن، بل في مصادره: السجلّ (ويُولَّد من المسرد بـ`pdf/terms.py`)، والمسرد، وجدول الدليل.", ""]
    shown = set()
    for key, title, cur, other in a.sources:
        r = READ_SOURCES.get(key)
        if not r or key in shown or r["verdict"] != "خلل":
            continue
        shown.add(key)
        md += [f"### {title}", "", f"- **الموضع:** {r['where']}", f"- **المشكلة:** {r['why']}"]
        if r["before"]:
            md += [f"- **النص الحالي:** {r['before']}", f"- **البديل المقترح:** {r['after']}"]
        elif cur:
            md += [f"- **ما وجدته الأداة:** {cur}"]
        md += [""]
    fine = [(s, READ_SOURCES[s[0]]) for s in a.sources if s[0] in READ_SOURCES and READ_SOURCES[s[0]]["verdict"] != "خلل"]
    if fine:
        md += ["### قُرئ فليس خللًا", ""] + [f"- {x[1]}: {r['why']}" for x, r in fine] + [""]
    others = [s for s in a.sources if s[0] not in READ_SOURCES]
    if others:
        md += ["### فروقٌ أخرى لم تُقرأ بعد", ""]
        md += [f"- {t}" + (f": «{c}»" if c else "") + (f" ← «{o}»" if o else "") + "." for k, t, c, o in others] + [""]
    md += ["## " + ("رابعًا" if a.companions else "ثالثًا") + ": ملاحظاتٌ للمؤلف وللدليل", ""]
    md += [f"- **{t}.** {d}" for t, d in OBSERVE] + [""]
    md += ["## " + ("خامسًا" if a.companions else "رابعًا") + ": مواضع قُرئت فليست خللًا", "",
           "| الموضع | ما أشارت إليه الأداة | الفحص | القراءة |", "|---|---|---|---|"]
    rows = {}
    for f in sorted(cleared, key=lambda f: (f["vol"] or 99, f["file"], f["line"])):
        rows.setdefault((f["file"], f["line"], id(f["read"])), f)
    for f in rows.values():
        md.append(f"| {where(f)} | {cell(f['around'])} | {f['check']} | {cell(f['read']['why'])} |")
    md += [""]
    if unread:
        md += ["## مواضع لم تُقرأ بعد", "", "| الموضع | النص | الفحص | ملاحظة الأداة |", "|---|---|---|---|"]
        for f in sorted(unread, key=lambda f: (f["vol"] or 99, f["file"], f["line"])):
            md.append(f"| {where(f)} | {cell(f['around'])} | {f['check']} | {cell(f['note'])} |")
        md += [""]
    md += ["## " + ("سادسًا" if a.companions else "خامسًا") + ": جرد صيغ المصطلحات المعتمدة في المتن", "",
           "عدد ورود كل مصطلحٍ من السجل في المتن الشارح (بعد حذف ما لا تقرؤه الأداة)، بصيغه كما وردت (بلا حركات، وبعد نزع حروف العطف والجر المتصلة). "
           "والصيغة التي ليست صيغة السجل تُقرأ: أكثرها إعرابٌ أو تنكير، والخللُ منها في الجداول أعلاه.", "",
           "| المصطلح | الورود | الصيغ |", "|---|---|---|"]
    for r in a.led:
        term = N(r["الرسم المعتمد"] or r["المصطلح"])
        forms = a.forms.get(term, Counter())
        total = sum(forms.values())
        fl = "، ".join(f"{k} ({ar(v)})" for k, v in forms.most_common(6))
        md.append(f"| {term} | {ar(total)} | {fl} |")
    md += ["", "## " + ("سابعًا" if a.companions else "سادسًا") + ": المقابلات اللاتينية في المتن", "",
           "| المصطلح | المقابل | الموضع |", "|---|---|---|"]
    for t, ln, term, gloss in sorted(a.glosses, key=lambda x: (x[0].vol or 99, x[0].rel, x[1])):
        md.append(f"| {term} | {gloss} | {where(dict(file=t.rel, vol=t.vol, line=ln))} |")
    md += ["", "## المصطلحات التي يعرّفها المتن ولا يعرفها السجل", "", "| المصطلح | موضع تعريفه |", "|---|---|"]
    for k in sorted(a.defined):
        t, ln = a.defined[k]
        md.append(f"| {k} | {where(dict(file=t.rel, vol=t.vol, line=ln))} |")
    OUT.write_text("\n".join(md) + "\n", encoding="utf-8")
    return genuine, cleared, unread, props


def main():
    comp = "--companions" in sys.argv
    a = Audit(companions=comp)
    a.run()
    genuine, cleared, unread, props = report(a)
    print(f"{len(a.texts)} ملفًّا؛ {len(a.findings)} موضعًا أشارت إليه الأداة: {len(genuine)} خللًا ({len(props)} بديلًا)، "
          f"{len(cleared)} ليس خللًا، {len(unread)} لم يُقرأ.")
    if a.stale:
        print("قراءاتٌ لم يعد نصّها في موضعه:", len(a.stale))
    print("→", OUT.relative_to(HERE.parent))


if __name__ == "__main__":
    main()
