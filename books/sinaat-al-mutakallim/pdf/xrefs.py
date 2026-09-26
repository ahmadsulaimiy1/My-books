#!/usr/bin/env python3
"""The internal references of the series (Bible, ch. 111 §٢; ch. 112د–112و): every pointer, resolved and judged.

The first volume promises it («وإذا أحال الكتاب إلى موضعٍ في مجلدٍ آخر ذكر المجلد مع الباب والفصل»), and CLAUDE.md
states the rules: a bab in another volume names its volume; the four numbers (volume, bab, level, chapter) are never
mixed; no page number of the book (pagination changes); the old architecture (four parts, fourteen babs, eight
volumes) is never referred to; no language of production in the printed text. This pass checks them all, series-wide.

What is extracted from the sources (book/المجلد-*/**/*.md; the generated المصادر-والمراجع is an index and is left out):

    عنوان          an address: «المجلد…»، «الباب…» (by number or by name: «باب البيان»)، «الفصل…» (also «الفصلين…»،
                   «الفصول ٣-٦»، «الفصل السابق/الآتي»، «… منه»)، «الدرس…»، «§…»، «القسم…»، «المستوى…»، «بنك الأخطاء»،
                   «المرجع الأول»، «الملحق أ–د»، «ملحق الباب الثاني»، «المسرد»، «المقدمة»، «المدخل»، «خاتمة الكتاب»،
                   «ملحق التحقيق، المسألة…»؛ adjacent parts make one address («المجلد الرابع، الباب الرابع، الفصل الثالث»)
    إحالة نسبية    «انظر»، «راجع»، «سبق»، «تقدّم»، «كما مرّ»، «سيأتي» without an address: what they name («…»، or the
                   words that follow) must be where they point (above, below, the chapter's entry, the bab's opener;
                   «سبق» the reader's unit before it, «سيأتي» the chapter after it); «ما سبق» names nothing
    مثال            example IDs [م٢-ب٦-ف٤-مث١] (printed [ب٦-ف٤-مث١], the bank [ر١-…]): one definition each, in its bab and
                   chapter; one named in a sentence points to an example that exists
    صنف الخطأ       «خ-٢٠» named outside a card: a class the bank's cards carry
    سطر الحوار      «س٧»، «س١–س٥»: a line of the scene it follows (or of the first version, in «ماذا تغيّر؟»)
    جدول الفصول     the chapter table of a bab's opener (and the bank's): each row a chapter that exists, by its title
    رأس الفصل       the line under a chapter's title: its bab and the bab's name, its lessons, its parts
    يوم البرنامج    «اليوم ١٤» in the pronunciation programme: a day of the thirty, ahead for «الآتي»
    إشارة           «هذا الباب»، «هذا المرجع»، «هذا الملحق»، «هذا الفصل»، «هذا الدرس»: the unit it stands in
    الكتاب المرافق  «حلقة الباب العاشر»: an episode of «سكريبتات الحلقات», which must be named
    لغة الملفات     «ف٦-أ»، «الملف الثاني»، «الفصل في ملفين»: the files are not a structure of the printed book
    البنية القديمة، رقم صفحة

And the judgement, resolved on the map (volumes.py: VOLUMES, units, VOL_OF_BAB), the places (paths.py), the files and
their «#»/«##»/«###» headings, and the example IDs the sources hold:

    سليمة     the target exists, and the form is the series' form
    مقروءة    a reader has read it: READINGS (a verbatim piece of the line → the reading)
    للقارئ    a pattern cannot decide; the passage must be read, and its reading or finding recorded here
    مخفقة     the target does not exist, or the form breaks a rule above; FINDINGS holds what reading established
              where a pattern saw nothing wrong

A failure's exact correction (current text → proposed text) is in PROPOSALS; the report prints it under the failure.
The tool reads the book and writes only its report: nothing in the sources is changed.

    python3 xrefs.py [--strict] [--quiet]
        prints the counts and every failure, and writes book/_production/هندسة-السلسلة/تدقيق-الإحالات.md
        --strict: exit with an error while a reference fails or waits for a reader
        --quiet:  the counts only
"""
import re
import sys
from collections import Counter, defaultdict

import ids
from paths import AUTHOR_WORD, CLOSING, GLOSSARY, INTRO, OPENING
from volumes import APPENDIX, BOOK, COMPANIONS, ORD, PROGRAM, VOL_OF_BAB, VOLUMES, unit_files

OUT = BOOK / "_production" / "هندسة-السلسلة" / "تدقيق-الإحالات.md"
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

# ordinals as they are written for a chapter, a lesson or a volume (the opening has seventeen chapters)
ORDS = ORD + ["الرابع عشر", "الخامس عشر", "السادس عشر", "السابع عشر", "الثامن عشر", "التاسع عشر", "العشرون"]
FEM = ["الأولى", "الثانية", "الثالثة", "الرابعة", "الخامسة", "السادسة", "السابعة", "الثامنة", "التاسعة", "العاشرة"]
VOLW = ORD[:10] + ["الحادي عشر"]
L = r"(?![ء-ي])"                                      # the end of an Arabic word
B = r"(?<![ء-ي])"                                     # the start of an Arabic word


def alt(words):
    return "|".join(sorted((re.escape(w) for w in words), key=len, reverse=True))


O_RE, V_RE, F_RE = alt(ORDS), alt(VOLW), alt(FEM)


def ordn(w):
    """The number of an ordinal: «الحادي عشر» → 11, «الثالثة» → 3."""
    return ORDS.index(w) + 1 if w in ORDS else FEM.index(w) + 1 if w in FEM else None


def num(s):
    return int(s.translate(EN))


def ar(n):
    return str(n).translate(AR)


def plain(s):
    """For comparing titles and topics: no diacritics, no tatweel, no punctuation, one form of alif and ya."""
    s = re.sub("[\u064B-\u0652\u0670\u0640]", "", s)
    s = re.sub("[\u0625\u0623\u0622]", "\u0627", s).replace("\u0649", "\u064A").replace("\u0629", "\u0647")
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# --------------------------------------------------------------------------------------------------- the structure

class Place:
    """A unit that can be pointed to: a chapter of a bab, of the opening, of the bank; an appendix; the programme…"""

    def __init__(self, kind, vol, key, title, files, order):
        self.kind, self.vol, self.key, self.title, self.files, self.order = kind, vol, key, title, files, order
        self.text = "\n".join(f.read_text(encoding="utf-8") for f in files)
        self.lessons = self._lessons()
        self.sections = {num(m.group(1)) for m in re.finditer(r"^###\s+([٠-٩]+)\.", self.text, re.M)}
        self.parts = {ordn(m.group(1)) for m in re.finditer(rf"^##\s+القسم ({O_RE}){L}", self.text, re.M)}
        self.numbered = {num(m.group(1)) for m in re.finditer(r"^##\s+([٠-٩]+)\.", self.text, re.M)}

    def _lessons(self):
        out = {ordn(m.group(1)) for m in re.finditer(rf"^##\s+الدرس ({O_RE}){L}", self.text, re.M)}
        if re.search(r"^##\s+الدرس:", self.text, re.M):
            out.add(1)                                  # «## الدرس: …» — a chapter of one lesson
        return out

    def section(self, n):
        """The text of «### n.» up to the next «###» heading."""
        m = re.search(rf"^###\s+{ar(n)}\..*?(?=^###\s|\Z)", self.text, re.M | re.S)
        return m.group(0) if m else ""

    def __repr__(self):
        return self.key


class Series:
    """The series as it stands: its files in their units, its chapters, and the IDs of its examples."""

    def __init__(self):
        self.files = []                                 # (path, vol, unit)
        for v in VOLUMES:
            for u in v["units"]:
                self.files += [(f, v["n"], u) for f in unit_files(v["n"], u)]
        self.files.insert(0, (AUTHOR_WORD, 1, ("author",)))
        self.order = {f: i for i, (f, _, _) in enumerate(self.files)}
        self.unit_of = {f: (v, u) for f, v, u in self.files}
        self.bab_name, self.bab_chapters = {}, {}       # n → name; n → {c: Place}
        for b, v in VOL_OF_BAB.items():
            files = unit_files(v, ("bab", b))
            opener = next(f for f in files if f.name.startswith("00-"))
            self.bab_name[b] = re.search(r"^#\s+الباب [^:]+:\s*(.+)$", opener.read_text(encoding="utf-8"), re.M).group(1).strip()
            self.bab_chapters[b] = self._chapters(files, "bab", v, f"ب{b}")
        bank = unit_files(11, ("reference",))
        self.bank = self._chapters(bank, "bank", 11, "ر")
        self.opening = {}                               # the opening's chapters are its «## الفصل …» headings
        for f in sorted(OPENING.glob("*.md")):
            m = re.search(rf"^##\s+الفصل ({O_RE}):\s*(.+)$", f.read_text(encoding="utf-8"), re.M)
            if m:
                c = ordn(m.group(1))
                self.opening[c] = Place("opening", 1, f"مقدمة/ف{c}", m.group(2).strip(), [f], self.order[f])
        self.verification = OPENING / "90-ملحق-التحقيق.md"
        self.intro = {1: Place("intro", 1, "المدخل/ف1", "العربية ومستوياتها", sorted(INTRO.glob("*.md")),
                               self.order[sorted(INTRO.glob("*.md"))[0]])}
        self.apps = {}
        for letter in APPENDIX:
            fs = unit_files(11, ("app", letter))
            self.apps[letter] = Place("app", 11, f"ملحق {letter}", APPENDIX[letter], fs, self.order[fs[0]])
        pf = unit_files(2, ("program",))
        self.program = Place("program", 2, "برنامج النطق", PROGRAM, pf, self.order[pf[0]])
        self.days = {num(m.group(1)) for m in re.finditer(r"^##\s+اليوم ([٠-٩]+):", self.program.text, re.M)}
        self.closing = Place("closing", 10, "خاتمة الكتاب", "خاتمة الكتاب", [CLOSING], self.order[CLOSING])
        self.glossary = Place("glossary", 11, "المسرد", "مسرد المصطلحات", [GLOSSARY], self.order[GLOSSARY])
        # the IDs of the examples as they stand, and the error classes the bank's cards carry
        self.ids = defaultdict(list)
        for f, _, _ in self.files:
            for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                for m in ids.PROD.finditer(line):
                    self.ids[m.group(0)].append((f, n))
        self.classes = set()
        for p in self.bank.values():
            for m in re.finditer(r"الرمز والخطورة[^\n]*", p.text):
                self.classes |= {num(x) for x in re.findall(r"خ-([٠-٩]+)", m.group(0))}

    def _chapters(self, files, kind, vol, tag):
        out = defaultdict(list)
        for f in files:
            m = re.match(r"ف([0-9]+)", f.name)
            if m:
                out[int(m.group(1))].append(f)
        places = {}
        for c, fs in out.items():
            head = re.search(r"^#\s+الفصل [^:]+:\s*(.+)$", fs[0].read_text(encoding="utf-8"), re.M).group(1)
            places[c] = Place(kind, vol, f"{tag}/ف{c}", re.sub(r"\s*\(تابع\)\s*$", "", head).strip(), fs, self.order[fs[0]])
        return places

    def chapter_of(self, f):
        """The Place a file belongs to (a chapter), or None."""
        v, u = self.unit_of[f]
        m = re.match(r"ف([0-9]+)", f.name)
        if u[0] == "bab" and m:
            return self.bab_chapters[u[1]][int(m.group(1))]
        if u[0] == "reference" and m:
            return self.bank[int(m.group(1))]
        if u[0] == "opening":
            return next((p for p in self.opening.values() if f in p.files), None)
        if u[0] == "intro":
            return self.intro[1]
        if u[0] == "app":
            return self.apps[u[1]]
        if u[0] == "program":
            return self.program
        return None


# ------------------------------------------------------------------------------------------------ the references

class Ref:
    """One reference: where it stands, what it says, what it points to, and the judgement."""

    def __init__(self, f, line, kind, text, target="", verdict="سليمة", note="", start=0):
        self.f, self.line, self.kind, self.text = f, line, kind, text
        self.target, self.verdict, self.note, self.start = target, verdict, note, start

    @property
    def where(self):
        return f"{self.f.relative_to(BOOK)}:{self.line}"


NAMES = {}                                             # a bab's name → its number (filled from the openers)
ELEVEN = r"المجلد الحادي عشر|مرجع المتكلّم العربي"  # the reference named in the paragraph
DIRECTION_BACK = B + r"[وف]?(?:سبق|سبقت|تقدّم|مرّ|مرّت|مر|مرت|عرفت|رأيت|درست|تعلّمت|تعلمت|أسلفنا|ذكرنا|فُصّل|فصّلنا)" + L
DIRECTION_FWD = B + r"[وف]?(?:سيأتي|ستأتي|سنعود|ستعرف|سترى|ستتعلّم|ستتعلم|سنفصّل|يأتي تفصيله|فيما بعد|لاحقًا)" + L
# words that make «الدرس الأول» or «المستوى الأول» a class or a school year in a scene, not a unit of the book
NOT_UNIT_BEFORE = r"(?:طلاب|طالب|طالبات|طلبة|أستاذ|معلّم|معلم|قاعة|حصة|حصّة|موعد|بعد|قبل|آخر حصة|يوم)\s*$"


# an ordinal of a source's own chapters («الفصل التاسع والعشرون» in Ibn Khaldun) is not the series'
DECADE = r"(?! و(?:العشر|الثلاث|الأربع|الخمس|الست|السبع|الثمان|التسع)(?:ون|ين))"
# «باب الحوار» is also the door of dialogue («أغلق باب الحوار»), «باب المؤسسة» the door of a building, «من باب
# الأدب» a matter of courtesy: a bab named by its name is a reference only where it is pointed to
BABNAME_BEFORE = r"(?:في|انظر|إلى|عالجه|يعالجه|تعالجه|فصّله|يفصّله|تفصيله|مرّ|سبق|تقدّم|علّمك|تعلّمته|درسته|عرفته|و)\s+(?:ال[ء-ي]+\s+)?$"


def tokens(line):
    """The unit words of a line, in order: (kind, start, end, values, raw). A leading «و» marks a new address."""
    names = alt(NAMES)
    pre = r"(?:[وف]?(?:لل|[بلك])?)"                     # «و»، «ف»، «ب»، «ل»، «لل»، «وللباب»، «كالفصل»
    pats = [
        ("vol", rf"{B}{pre}(?:ال)?مجلد(?:ين|ان)? ({V_RE}){L}(?: و({V_RE}){L})?"),
        ("bab", rf"{B}{pre}(?:ال)?باب(?:ين|ان)? ({O_RE}){L}{DECADE}(?: و({O_RE}){L})?"),
        ("babname", rf"{B}{pre}باب(?:ي)? ({names}){L}"),
        ("ch", rf"{B}{pre}(?:ال)?فصل(?:ين|ان)? ({O_RE}){L}{DECADE}(?: و({O_RE}){L}{DECADE})?"),
        ("chn", r"(?:ال)?فصول ([٠-٩]+)\s*[-–]\s*([٠-٩]+)"),
        ("lesson", rf"{B}{pre}(?:ال)?درس(?:ين|ان)? ({O_RE}){L}(?: و({O_RE}){L})?"),
        ("sec", r"§\s?([٠-٩]+)((?:\s*(?:و|،)\s*§\s?[٠-٩]+)*)"),
        ("part", rf"{B}{pre}القسم ({O_RE}){L}"),
        ("bank", rf"{B}{pre}(?:بنك الأخطاء|المرجع الأول{L})"),
        ("app", rf"{B}{pre}(?:ال)?ملحق ([أ-د]|هـ|ز){L}"),
        ("program", r"ملحق الباب الثاني|برنامج النطق"),
        ("gloss", rf"{B}{pre}(?:ال)?مسرد{L}"),
        ("opening", r"مقدّ?مة الكتاب|خاتمة المقدّ?مة|ملحق التحقيق|هذه المقدّ?مة|(?<=انظر )المقدّ?مة"
                    r"|(?:(?<=مرّ في )|(?<=سبق في )|(?<=تقدّم في )|(?<=ذكرنا في ))المقدّ?مة"),
        ("chrel", rf"{B}{pre}(?:ال)?فصل (السابق|الآتي|التالي){L}"),
        ("bablast", rf"{B}{pre}(?:ال)?باب الأخير{L}"),                  # «الباب الأخير»: the thirteenth
        ("intro", r"«المدخل»|«مدخلًا»"),
        ("closing", r"خاتمة الكتاب"),
        ("level", rf"{B}{pre}(?:ال)?مستوى ({O_RE}|[٠-٩]+){L}"),
    ]
    out = []
    for kind, p in pats:
        for m in re.finditer(p, line):
            if kind == "babname" and not re.search(BABNAME_BEFORE, line[max(0, m.start() - 30):m.start()]) \
                    and not re.match(r"\s*\((?:انظر\s+)?المجلد", line[m.end():]) \
                    and not (m.group(0).startswith("و") and re.search(rf"باب (?:{names})\s*$", line[:m.start()])):
                continue
            if kind == "opening" and re.search(r"ابن خلدون[^.؛]{0,12}$|كتاب العين|معجمه", line[max(0, m.start() - 60):m.start()]):
                continue                                 # Ibn Khaldun's Muqaddima, the preface of al-Khalil's «العين»
            out.append((kind, m.start(), m.end(), m.groups(), m.group(0)))
    out.sort(key=lambda t: (t[1], -t[2]))
    kept, end = [], -1
    for t in out:                                        # the longer match wins where two overlap
        if t[1] >= end:
            kept.append(t)
            end = t[2]
    return kept


def mask_quotes(line, keep):
    """Speech in «…» is not a reference; a quoted title («المدخل»، «بنك الأخطاء») is."""
    def sub(m):
        inner = m.group(1).strip()
        return m.group(0) if inner in keep else "«" + " " * len(m.group(1)) + "»"
    return re.sub(r"«([^«»]*)»", sub, line)


GAP_OK = [r"[\s،,:()\*]*(?:(?:من|في|ضمن)[\s،,:()\*]+)?",           # «المجلد الرابع، الباب الرابع»، «من الباب»
          r"\s*\(\s*«?[^()«»،]{1,30}»?\s*،\s*",                    # «الباب الثالث (العبارة، المجلد الثالث)»
          r"\s*،?\s*\(\s*(?:في\s+)?"]                               # «الباب الثاني (المجلد الثاني)»


def chains(toks, line):
    """Adjacent unit words make one address: «المجلد الرابع، الباب الرابع، الفصل الثالث»، «الفصل الرابع، §١٢».
    A unit word that opens with «و» («والباب الخامس») starts another address, and so does a repeated kind."""
    groups = []
    for t in toks:
        if groups:
            prev = groups[-1][-1]
            gap = line[prev[2]:t[1]]
            conj = re.match(r"و(?:ال|لل|باب|بنك|مجلد|فصل)", t[4]) is not None
            same = t[0] == prev[0] and t[0] != "sec" or "chrel" in (t[0], prev[0])
            if not conj and not same and any(re.fullmatch(g, gap) for g in GAP_OK):
                groups[-1].append(t)
                continue
        groups.append([t])
    return groups


class Context:
    """Where a reference stands: its volume, its unit, its bab, its chapter."""

    def __init__(self, S, f):
        self.f = f
        self.vol, self.unit = S.unit_of[f]
        self.bab = self.unit[1] if self.unit[0] == "bab" else None
        self.chapter = S.chapter_of(f)
        self.order = S.order[f]


def named_volumes(chain, after):
    """The volumes an address names: in itself, or right after it («… في المجلد الحادي عشر»، «(المجلد الثاني)»)."""
    out = [VOLW.index(v) + 1 for t in chain if t[0] == "vol" for v in t[3] if v]
    m = re.match(rf"^[^.؛\n]{{0,30}}?(?:في|من|،|\()\s*المجلد(?:ين)? ({V_RE}){L}(?: و({V_RE}){L})?", after)
    if m:
        out += [VOLW.index(v) + 1 for v in m.groups() if v]
    return out


def paren_name(after):
    """«الباب الثالث (العبارة، المجلد الثالث)» → «العبارة»."""
    m = re.match(r"^\s*\(\s*«?([^()،»]{2,30})»?\s*[،)]", after)
    return m.group(1).strip() if m else None


def topic_of(after):
    """What an address says it is about: «…، الفصل العاشر: الوقف والابتداء»، «… الباب الثاني في سرعة الكلام»."""
    m = re.match(r"^\s*[:]\s*([^()\[\].؛،\n*]{3,60})", after) or re.match(r"^\s+في ([^()\[\].؛،\n*]{3,40})", after)
    return m.group(1).strip() if m else None


STOP = {"في", "من", "إلى", "على", "عن", "مع", "ثم", "أو", "و", "ما", "لا", "هذا", "هذه", "ذلك", "التي", "الذي", "كل",
        "بين", "عند", "بعد", "قبل", "أن", "إن", "كما", "خاصة", "تفصيل", "بتفصيل", "أوسع", "الفصل", "الباب", "المجلد"}


def topic_found(topic, place):
    words = [w for w in plain(topic).split() if w not in STOP and len(w) > 2]
    text = plain(place.text)
    hits = [w for w in words if w in text or (w.startswith("ال") and w[2:] in text) or ("ال" + w) in text
            or (w[:1] in "وفبل" and w[1:] in text)]
    return not words or len(hits) * 2 >= len(words), words, hits


def resolve(S, ctx, chain, line, start, end, stop=None):
    """Judge one address. Returns a list of (verdict, target, note). stop: where the next address begins."""
    kinds = [t[0] for t in chain]
    after, before = line[end:min(end + 90, stop or len(line))], line[max(0, start - 160):start]
    vols = named_volumes(chain, after)
    res = []

    def add(v, target, note=""):
        res.append((v, target, note))

    babs, chs, lessons, secs, parts, levels = [], [], [], [], [], []
    for kind, s, e, g, raw in chain:
        if kind == "bab":
            babs += [ordn(x) for x in g if x]
        elif kind == "bablast":
            babs.append(13)
        elif kind == "babname":
            babs.append(NAMES[g[0]])
        elif kind == "ch":
            chs += [ordn(x) for x in g if x]
        elif kind == "chn":
            chs += list(range(num(g[0]), num(g[1]) + 1))
        elif kind == "lesson":
            lessons += [ordn(x) for x in g if x]
        elif kind == "sec":
            secs += [num(x) for x in re.findall(r"[٠-٩]+", raw)]
        elif kind == "part":
            parts.append(ordn(g[0]))
        elif kind == "level":
            levels.append(ordn(g[0]) if g[0] in ORDS else num(g[0]))
    this = re.match(r"^\s*(?:من|في)\s+(هذا الباب|هذا المرجع|هذه المقدّ?مة|هذا الملحق|هذا الفصل)", after)
    this = this.group(1) if this else None

    # --- the form: «المجلد الرابع، الباب الرابع، الفصل الثالث» — the parts of an address are set apart by «،» ------
    for a, b in zip(chain, chain[1:]):
        if a[0] in ("vol", "bab", "babname", "ch") and b[0] in ("vol", "bab", "ch", "lesson") and re.fullmatch(r"\s+", line[a[2]:b[1]]):
            add("مخفقة", "", f"صيغة الإحالة: «{a[4]}، {b[4]}» بفاصلة بين أجزائها (الدليل، الباب ١١١ §٢)")

    # --- the levels: one to thirteen, and a level is its bab's number ---------------------------------------------
    for n in levels:
        if n < 1 or n > 13:
            add("مخفقة", f"المستوى {ar(n)}", "المستويات من ١ إلى ١٣ (البنية القديمة: المستوى ٠)")
        elif babs and n not in babs:
            add("مخفقة", f"المستوى {ar(n)}", f"المستوى رقمه رقم بابه، وهنا الباب {ar(babs[0])}")
        elif vols and not any(VOL_OF_BAB[n] == v for v in vols):
            add("مخفقة", f"المستوى {ar(n)}", f"المستوى {ar(n)} في المجلد {VOLW[VOL_OF_BAB[n] - 1]}")
    if kinds == ["level"]:
        if not res and ctx.bab and levels[0] != ctx.bab:    # a level alone, in a bab: its own (the old 0–12 left «ن-١»)
            return [("مخفقة", f"المستوى {ar(levels[0])}",
                     f"في الباب {ORDS[ctx.bab - 1]} مستواه {ar(ctx.bab)}: «المستوى {ORDS[ctx.bab - 1]}» (رقم المستوى رقم بابه؛ "
                     f"والمستويات القديمة ٠–١٢ تنقص واحدًا)")]
        return res or [("سليمة", f"المستوى {ar(levels[0])}", "")]

    # --- babs ----------------------------------------------------------------------------------------------------
    if babs:
        if "bank" in kinds:
            add("مخفقة", "بنك الأخطاء", "بنك الأخطاء مرجعٌ في المجلد الحادي عشر، لا باب")
        for b in babs:
            if b > 13:
                add("مخفقة", f"الباب {ORDS[b - 1]}", "لا باب بعد الثالث عشر (البنية القديمة)")
                continue
            tv = VOL_OF_BAB[b]
            target = f"المجلد {VOLW[tv - 1]}، الباب {ORDS[b - 1]} ({S.bab_name[b]})"
            wrong = [v for v in vols if v != tv]
            if wrong and not any(v == tv for v in vols):
                add("مخفقة", target, f"الباب {ORDS[b - 1]} في المجلد {VOLW[tv - 1]}، لا في المجلد {VOLW[wrong[0] - 1]}")
                continue
            if tv != ctx.vol and not vols:
                nearby = re.search(rf"المجلد {VOLW[tv - 1]}{L}", line[max(0, start - 60): end + 160])
                if not nearby:
                    add("مخفقة", target, f"إحالةٌ إلى بابٍ في مجلدٍ آخر (المجلد {VOLW[tv - 1]}) بلا ذكر المجلد")
                    continue
            bt = next((t for t in chain if t[0] in ("bab", "babname", "bablast")), None)
            nm = paren_name(line[bt[2]:bt[2] + 60]) if bt else None
            if nm and not nm.startswith(("المجلد", "انظر", "الفصل", "في ")) and len(babs) == 1 \
                    and plain(nm) not in (plain(S.bab_name[b]), plain(VOLUMES[tv - 1]["name"])) \
                    and not plain(S.bab_name[b]).startswith(plain(nm)) and not plain(nm).startswith(plain(S.bab_name[b])):
                ch_named = [c for c, q in S.bab_chapters[b].items() if plain(q.title).startswith(plain(nm))]
                if ch_named:
                    add("مخفقة", target + f"، الفصل {ORDS[ch_named[0] - 1]}",
                        f"بين القوسين عنوان الفصل {ORDS[ch_named[0] - 1]} في موضع اسم الباب («{S.bab_name[b]}»): يُذكر الفصل برقمه")
                else:
                    add("للقارئ", target, f"الاسم بين القوسين «{nm}» والباب «{S.bab_name[b]}»")
            if len(babs) == 1 and chs:
                for c in chs:
                    p = S.bab_chapters[b].get(c)
                    if not p:
                        add("مخفقة", target + f"، الفصل {ORDS[c - 1]}", f"الباب {ORDS[b - 1]} فيه {ar(len(S.bab_chapters[b]))} فصول")
                        continue
                    res += judge_place(S, ctx, p, lessons, secs, parts, after, before)
            elif not res or all(r[0] == "سليمة" for r in res):
                add("سليمة", target, "")
        return res

    # --- the bank, the appendices, the programme, the glossary, the opening, the closing ----------------------------
    if "bank" in kinds:
        if ctx.vol != 11 and 11 not in vols and not re.search(ELEVEN, line):
            add("مخفقة", "المجلد الحادي عشر، بنك الأخطاء", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
        if chs:
            for c in chs:
                p = S.bank.get(c)
                if not p:
                    add("مخفقة", f"بنك الأخطاء، الفصل {ORDS[c - 1]}", f"في بنك الأخطاء {ar(len(S.bank))} فصول")
                else:
                    res += judge_place(S, ctx, p, lessons, secs, parts, after, before)
        elif not res:
            add("سليمة", "المجلد الحادي عشر، المرجع الأول: بنك الأخطاء", "")
        return res
    if "app" in kinds:
        for kind, s, e, g, raw in chain:
            if kind != "app":
                continue
            letter = g[0]
            if letter not in S.apps:
                add("مخفقة", f"ملحق {letter}", "الملاحق أ–د في المجلد الحادي عشر (ملحق هـ–ز من البنية القديمة)")
                continue
            p = S.apps[letter]
            if ctx.vol != 11 and 11 not in vols and not re.search(ELEVEN, line):
                add("مخفقة", f"المجلد الحادي عشر، {p.key}", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
                continue
            res += judge_place(S, ctx, p, lessons, secs, parts, after, before)
        return res
    if "program" in kinds:
        if ctx.vol != 2 and 2 not in vols and not re.search(r"المجلد الثاني", line):
            add("مخفقة", "المجلد الثاني، " + PROGRAM, "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
        else:
            add("سليمة", "المجلد الثاني، " + PROGRAM, "")
        return res
    if "gloss" in kinds:
        if ctx.vol != 11 and 11 not in vols and not re.search(ELEVEN, line):
            add("مخفقة", "المجلد الحادي عشر، المسرد", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
        else:
            add("سليمة", "المجلد الحادي عشر، مسرد المصطلحات", "")
        return res
    if "closing" in kinds:
        if ctx.vol != 10 and 10 not in vols and not re.search(r"المجلد العاشر", line):
            add("مخفقة", "المجلد العاشر، خاتمة الكتاب", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
        else:
            add("سليمة", "المجلد العاشر، خاتمة الكتاب", "")
        return res
    opening = "opening" in kinds or this and "مقد" in this
    if "intro" in kinds and not chs:
        if ctx.vol != 1 and 1 not in vols:
            add("مخفقة", "المجلد الأول، المدخل", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
        else:
            add("سليمة", "المجلد الأول، المدخل: " + S.intro[1].title, "")
        return res

    # --- a chapter, a lesson or a section without its bab: in the reader's own unit --------------------------------
    if chs:
        if opening or ctx.unit[0] in ("opening", "author") and not vols:
            space, label = S.opening, "المقدمة"
            if ctx.vol != 1 and 1 not in vols:
                add("مخفقة", "المجلد الأول، المقدمة", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")
        elif this == "هذا المرجع" or ctx.unit[0] == "reference" and not vols:
            space, label = S.bank, "بنك الأخطاء"
        elif vols:
            babs_v = [u[1] for u in VOLUMES[vols[0] - 1]["units"] if u[0] == "bab"]
            if len(babs_v) != 1:
                add("مخفقة", f"المجلد {VOLW[vols[0] - 1]}، الفصل {ORDS[chs[0] - 1]}",
                    f"في المجلد {VOLW[vols[0] - 1]} {'بابان' if len(babs_v) == 2 else 'أبواب' if babs_v else 'لا أبواب'}: يُذكر الباب")
                return res
            space, label = S.bab_chapters[babs_v[0]], f"المجلد {VOLW[vols[0] - 1]}، الباب {ORDS[babs_v[0] - 1]}"
        elif ctx.bab:
            space, label = S.bab_chapters[ctx.bab], f"الباب {ORDS[ctx.bab - 1]}"
        elif ctx.unit[0] == "program":
            space, label = S.bab_chapters[2], "الباب الثاني"
        elif ctx.unit[0] == "intro":
            space, label = S.opening, "المقدمة"
        else:
            add("للقارئ", f"الفصل {ORDS[chs[0] - 1]}", f"فصلٌ بلا باب في {ctx.unit[0]}: من أيّ وحدة؟")
            return res
        for c in chs:
            p = space.get(c)
            if not p:
                add("مخفقة", f"{label}، الفصل {ORDS[c - 1]}", f"{label} فيه {ar(len(space))} فصول")
            else:
                res += judge_place(S, ctx, p, lessons, secs, parts, after, before)
        return res
    if lessons or secs or parts:
        p = ctx.chapter
        if not p:
            return [("للقارئ", "", "درسٌ أو مبحثٌ أو قسمٌ خارج فصل")]
        return judge_place(S, ctx, p, lessons, secs, parts, after, before, local=True)
    if opening:
        if ctx.vol != 1 and 1 not in vols:
            return [("مخفقة", "المجلد الأول، المقدمة", "إحالةٌ إلى موضعٍ في مجلدٍ آخر بلا ذكر المجلد")]
        q = re.match(rf"^\s*[،,]\s*المسألة ({F_RE}){L}", after)
        if any(t[4] == "ملحق التحقيق" for t in chain) and q:
            k = FEM.index(q.group(1)) + 1
            have = {num(x) for x in re.findall(r"^###\s+([٠-٩]+)\.", S.verification.read_text(encoding="utf-8"), re.M)}
            if k not in have:
                return [("مخفقة", f"المجلد الأول، ملحق التحقيق، المسألة {q.group(1)}", f"في ملحق التحقيق {ar(len(have))} مسائل")]
            return [("سليمة", f"المجلد الأول، ملحق التحقيق، المسألة {q.group(1)}", "")]
        return [("سليمة", "المجلد الأول، المقدمة: في صناعة الكلام", "")]

    # --- «الفصل السابق»، «الفصل الآتي»: the chapter next to the reader's -------------------------------------------
    if kinds == ["chrel"]:
        rel = chain[0][3][0]
        p = ctx.chapter
        space = (S.bab_chapters[ctx.bab] if ctx.bab else S.opening if ctx.unit[0] == "opening" else
                 S.bank if ctx.unit[0] == "reference" else None)
        if not p or space is None:
            return [("سليمة", "", "")]
        c = int(p.key.split("ف")[-1])
        c2 = c - 1 if rel == "السابق" else c + 1
        q = space.get(c2)
        if not q:
            return [("للقارئ", "", f"«الفصل {rel}» من الفصل {ORDS[c - 1]}: لا فصل هناك في وحدته")]
        return judge_place(S, ctx, q, [], [], [], after, before)

    # --- a volume alone: its name, if one is given, is its own --------------------------------------------------------
    if "vol" in kinds:
        for v in vols or []:
            nm = paren_name(after) or (re.match(r"^\s*[:،]\s*«([^»]+)»", after) or [None, None])[1]
            own = {VOLUMES[v - 1]["name"], {1: "التأسيس", 2: "التواصل", 3: "المنصّات", 4: "التمكين"}.get(VOLUMES[v - 1]["stage"], "المرجع")}
            if nm and not any(plain(nm).startswith(plain(x)) or plain(x).startswith(plain(nm)) for x in own) \
                    and not nm.startswith(("الباب", "انظر", "المجلد")):
                add("مخفقة", f"المجلد {VOLW[v - 1]}", f"المجلد {VOLW[v - 1]} هو «{VOLUMES[v - 1]['name']}»، لا «{nm}»")
            else:
                add("سليمة", f"المجلد {VOLW[v - 1]}: {VOLUMES[v - 1]['name']}", "")
        return res
    return res


def object_before(clause):
    """What the sentence says is found at the address: «الأدب الذي مرّ بك في الفصل الأول»، «في النموذج السداسي
    (الفصل الأول)»، «… «وقفة الثواني العشر» (انظر …)». Returns (terms, quoted) or None."""
    c = re.split(r"[.؛!؟?:]\s", clause)[-1]
    m = re.search(r"(ال[ء-ي]+(?:\s+ال[ء-ي]+)?)\s+(?:الذي|التي)\s+(?:مرّ|مرت|مرّت|درسته|درستها|درستَه|تعلمته|تعلّمته|تعلّمتَه|"
                  r"تعلمتها|عرفته|عرفتها|رأيته|رأيتها)(?:\s+بك)?\s+في\s*$", c)
    if m:
        return [m.group(1)], False
    m = re.search(r"(?:في|من)\s+(ال[ء-ي]+(?:\s+ال[ء-ي]+)?)\s*\(\s*(?:انظر\s+)?$", c)
    if m:
        return [m.group(1)], False
    m = re.search(r"(?:^|[،؛]\s*)و?((?:ال)?[ء-ي]{3,}\s+ال[ء-ي]+|ال[ء-ي]+)\s+(?:مفصّلة?\s+)?في\s*$", c)
    if m:
        return [m.group(1)], False
    q = re.findall(r"«([^«»]{3,40})»", c)
    if q and re.search(r"«[^«»]{3,40}»[^«»()]{0,25}\(\s*(?:انظر\s+)?$", c):
        return [q[-1]], True
    return None


def judge_place(S, ctx, p, lessons, secs, parts, after, before, local=False):
    """A chapter (or an appendix) found: its lessons, sections and parts exist, its topic is its own, and a «سبق»
    points back and a «سيأتي» forward."""
    out = []
    label = p.key
    if p.kind == "bab":
        b = int(re.match(r"ب(\d+)", p.key).group(1))
        label = f"المجلد {VOLW[p.vol - 1]}، الباب {ORDS[b - 1]}، الفصل {ORDS[int(p.key.split('ف')[-1]) - 1]}: {p.title}"
    elif p.kind == "opening":
        label = f"المجلد الأول، المقدمة، الفصل {ORDS[int(p.key.split('ف')[-1]) - 1]}: {p.title}"
    elif p.kind == "bank":
        label = f"المجلد الحادي عشر، بنك الأخطاء، الفصل {ORDS[int(p.key.split('ف')[-1]) - 1]}: {p.title}"
    elif p.kind == "app":
        label = f"المجلد الحادي عشر، {p.key}: {p.title}"
    elif p.kind == "program":
        label = "المجلد الثاني، " + PROGRAM
    for n in lessons:
        if p.lessons and n not in p.lessons:
            out.append(("مخفقة", label + f"، الدرس {ORDS[n - 1]}", f"في الفصل {ar(len(p.lessons))} {'دروس' if len(p.lessons) > 2 else 'درسان' if len(p.lessons) == 2 else 'درس'}"))
        elif not p.lessons and not local:
            out.append(("للقارئ", label + f"، الدرس {ORDS[n - 1]}", "فصلٌ لا دروس معنونة فيه"))
    for n in secs:
        if n not in p.sections:
            out.append(("مخفقة", label + f"، §{ar(n)}", f"مباحث الفصل {ar(max(p.sections or [0]))}"))
        elif re.match(r"^[^.؛]{0,12}(?:و§[٠-٩]+)?،?\s*و(?:توثيقه|توثيقهما|تخريجه|تخريجهما|تخريج الحديثين) هناك", after) \
                and not re.search(r"\[\^\d+\]", p.section(n)):
            out.append(("مخفقة", label + f"، §{ar(n)}", "«وتوثيقه هناك» والمبحث بلا حاشية"))
    for n in parts:
        if p.kind == "program":
            out.append(("مخفقة", label + f"، القسم {ORDS[n - 1]}", "برنامج النطق أيامٌ لا أقسام: القسم هنا ملفٌّ من ملفاته"))
            continue
        pool = p.parts or p.numbered or (set(range(1, len(p.files) + 1)) if p.kind in ("bab", "bank") else set())
        if pool and n not in pool:
            out.append(("مخفقة", label + f"، القسم {ORDS[n - 1]}", f"أقسامه {ar(len(pool))}"))
    ob = object_before(before) if not local and p.kind in ("bab", "opening", "app", "bank") else None
    if ob:
        terms, quoted = ob
        text = plain(p.text)
        if not quoted:                                   # «وتفصيل الإضافة»: the thing, not the word for its treatment
            terms = [w for t in terms for w in t.split()
                     if plain(w) not in {plain(x) for x in ("تفصيل", "وتفصيل", "بيان", "ضبط", "موضوع", "أحكام", "آداب")}] or terms
        if not all(plain(t) in text or plain(re.sub(r"(?<!\S)ال", "", t)) in text for t in terms):
            others = [q for q in list(S.bab_chapters[1].values()) + list(S.opening.values())
                      if q is not p and all(plain(t) in plain(q.text) for t in terms)]
            where = f"؛ وهو في {others[0].key}" if others else ""
            out.append(("للقارئ", label, f"«{'، '.join(terms)}» لا يظهر في الموضع{where}"))
    t = topic_of(after)
    if t and not local and p.kind in ("bab", "opening", "bank", "app"):
        ok, words, hits = topic_found(t, p)
        if not ok:
            out.append(("للقارئ", label, f"الموضوع «{t}» لا تظهر ألفاظه في الموضع ({'، '.join(words)})"))
    back = re.search(DIRECTION_BACK + r"[^.؛]{0,30}$", before)
    fwd = re.search(DIRECTION_FWD + r"[^.؛]{0,30}$", before)
    if p is not ctx.chapter and p.kind in ("bab", "opening", "intro"):
        if back and p.order > ctx.order:
            out.append(("مخفقة", label, f"«{back.group(0).split()[0]}» يشير إلى ما بعده"))
        if fwd and p.order < ctx.order:
            out.append(("مخفقة", label, f"«{fwd.group(0).split()[0]}» يشير إلى ما قبله"))
    if not any(v == "مخفقة" for v, _, _ in out):
        out.append(("سليمة", label, ""))
    return out


# ------------------------------------------------------------------------------------------------------ the scan

def line_kind(line):
    if line.startswith("#"):
        return "heading"
    if re.match(r"^\[\^\d+\]:", line):
        return "note"
    if re.match(r"^\|\s*س[٠-٩]+\s*\|", line):
        return "dialogue"                                # a line of a scene: speech, never a reference
    if line.startswith("|"):
        return "table"
    return "text"


def scan_addresses(S, f, text):
    """The addresses of a file: volume, bab, chapter, lesson, section, bank, appendix, programme, glossary…"""
    ctx = Context(S, f)
    keep = set(NAMES) | {v["name"] for v in VOLUMES} | {"المدخل", "بنك الأخطاء", "مرجع المتكلّم العربي", "المقدمة",
                                                         "مدخلًا", "المسرد"}
    out = []
    for n, raw in enumerate(text.splitlines(), 1):
        kind = line_kind(raw)
        if kind in ("heading", "dialogue"):
            continue
        line = mask_quotes(raw, keep)
        toks = [t for t in tokens(line) if not (t[0] in ("lesson", "level") and re.search(NOT_UNIT_BEFORE, line[:t[1]]))
                and not (t[0] == "ch" and re.search(r"(?:تسليم|كتابة|أكتب|رسالته|بحثه)\s*$", line[:t[1]]))
                and not (t[0] == "part" and re.match(r"\s+من (?!هذا)", line[t[2]:]))]
        groups = chains(toks, line)
        prev_bab = None
        for i, chain in enumerate(groups):
            s, e = chain[0][1], chain[-1][2]
            stop = groups[i + 1][0][1] if i + 1 < len(groups) else None
            if prev_bab and re.match(r"\s*منه(?![ء-ي])", line[e:]) and not any(t[0] in ("bab", "babname") for t in chain):
                chain = [("bab", s, s, (ORDS[prev_bab - 1], None), "")] + chain   # «الفصل الثالث منه»
            results = resolve(S, ctx, chain, line, s, e, stop)
            babs_here = [ordn(t[3][0]) for t in chain if t[0] == "bab" and t[3][0]] + [NAMES[t[3][0]] for t in chain if t[0] == "babname"]
            prev_bab = babs_here[-1] if babs_here else prev_bab
            bad = list(dict.fromkeys(r for r in results if r[0] != "سليمة"))
            if bad:                                      # one entry per distinct judgement
                out += [Ref(f, n, "عنوان", raw[s:e], target, verdict, note, s) for verdict, target, note in bad]
            elif results:                                # «الفصول ٣-٦»: one address, its targets together
                targets = "؛ ".join(dict.fromkeys(t for _, t, _ in results if t))
                out.append(Ref(f, n, "عنوان", raw[s:e], targets, "سليمة", "", s))
    return out


def scan_ids(S, f, text):
    """Example IDs: each is defined once where its example stands; one named in a sentence («أعدهم إلى المثال
    [م١-ب١-ف٢-مث٣٢]») points to an example that exists. A definition sits in its bab and chapter."""
    ctx, out = Context(S, f), []
    for n, line in enumerate(text.splitlines(), 1):
        for m in ids.PROD.finditer(line):
            pid = m.group(0)
            try:
                shown = ids.teaching_id(m)
            except ValueError as e:
                out.append(Ref(f, n, "مثال", pid, "", "مخفقة", str(e), m.start()))
                continue
            pointer = re.search(r"(?:المثال|مثال|مثل|انظر|إلى)\s*$", line[max(0, m.start() - 16):m.start()])
            defs = [(g, k) for g, k in S.ids[pid] if (g, k) != (f, n)]
            if pointer:
                if not defs:
                    out.append(Ref(f, n, "مثال", pid, f"{shown}: لا مثال بهذا الرمز", "مخفقة",
                                   "يُحال إلى مثالٍ لا يحمل رمزه أحدٌ في المصدر", m.start()))
                else:
                    g, k = defs[0]
                    out.append(Ref(f, n, "مثال", pid, f"{shown}: {g.relative_to(BOOK)}:{k}", "سليمة", "", m.start()))
                continue
            if defs and (f, n) == S.ids[pid][-1]:
                g, k = defs[0]
                if not re.search(r"(?:المثال|مثال|مثل|انظر|إلى)\s*$", g.read_text(encoding="utf-8").splitlines()[k - 1][:200]):
                    out.append(Ref(f, n, "مثال", pid, f"{shown}", "مخفقة", f"الرمز معرّفٌ مرتين (والأخرى {g.relative_to(BOOK)}:{k})", m.start()))
            b, c = num(m.group(2)), num(m.group(3))
            home = "bank" if b == 13 else (13 if b == 14 else b)
            where = "bank" if ctx.unit[0] == "reference" else ctx.bab
            fc = re.match(r"ف([0-9]+)", f.name)
            if home != where or (fc and int(fc.group(1)) != c):
                out.append(Ref(f, n, "مثال", pid, shown, "مخفقة", "رمز المثال لا يطابق بابه أو فصله", m.start()))
    return out


def scan_classes(S, f, text):
    """The error classes of the bank («خ-٢٠»): named outside a card, the class must be one the bank's cards carry."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        if "الرمز والخطورة" in line:
            continue
        for m in re.finditer(r"(?<![ء-ي])خ-([٠-٩]+)", line):
            k = num(m.group(1))
            ok = k in S.classes
            out.append(Ref(f, n, "صنف الخطأ", m.group(0), "المجلد الحادي عشر، بنك الأخطاء، " + m.group(0),
                           "سليمة" if ok else "مخفقة",
                           "" if ok else f"لا تحمل بطاقةٌ في بنك الأخطاء الصنف {m.group(0)}: فلا يجده القارئ", m.start()))
    return out


def dialogues(S):
    """Every scene of every chapter — a table headed «| السطر | المتكلم | الكلام |» — in reading order:
    {chapter key: [(file, first line, last line, {line number: text})]}, and the set of (file, line) of their rows."""
    out, rows = defaultdict(list), set()
    for f, v, u in S.files:
        place = S.chapter_of(f)
        key = place.key if place else str(f)
        cur = None
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\|\s*السطر\s*\|\s*المتكلمة?\s*\|", line):
                cur = [f, n, n, {}]
                out[key].append(cur)
                continue
            if cur is None:
                continue
            m = re.match(r"^\|\s*س([٠-٩]+)\s*\|(.*)$", line)
            if m:
                cur[2] = n
                cur[3][num(m.group(1))] = m.group(2)
                rows.add((f, n))
            elif not line.startswith("|"):
                cur = None
    return out, rows


def scan_lines(S, f, text, scenes):
    """«(س٧)»: a line of the scene it follows — the scene itself, or, in «ماذا تغيّر؟», the first version before the
    improved one; before any scene of the chapter, the scene that comes next."""
    out = []
    scenes, rows = scenes
    place = S.chapter_of(f)
    key = place.key if place else str(f)
    mine = scenes.get(key, [])
    for n, line in enumerate(text.splitlines(), 1):
        if (f, n) in rows:
            continue
        for m in re.finditer(r"(?<![ء-ي\w])س([٠-٩]+)(?:\s*[–-]\s*س?([٠-٩]+))?(?![٠-٩])", line):
            a = num(m.group(1))
            z = num(m.group(2)) if m.group(2) else a
            here = S.order[f] * 100000 + n
            before = [d for d in mine if S.order[d[0]] * 100000 + d[1] < here]
            near = before[-2:][::-1] if before else mine[:1]
            if not near:
                out.append(Ref(f, n, "سطر الحوار", m.group(0), "", "للقارئ", "لا حوار مسطّر في الفصل", m.start()))
                continue
            scene = next((d for d in near if all(k in d[3] for k in range(a, z + 1))), None)
            if scene is None:
                d = near[0]
                out.append(Ref(f, n, "سطر الحوار", m.group(0), f"{d[0].relative_to(BOOK)}:{d[1]} (س١–س{ar(max(d[3] or [0]))})",
                               "مخفقة", f"الحوار الذي يسبقه ينتهي عند س{ar(max(d[3] or [0]))}", m.start()))
            else:
                out.append(Ref(f, n, "سطر الحوار", m.group(0), f"{scene[0].relative_to(BOOK)}:{scene[1]}", "سليمة", "", m.start()))
    return out


def scan_forms(S, f, text):
    """What must never stand in the printed text: the language of the files, a page number of the book itself, the
    old architecture; and the deictics («هذا الباب») must name the unit they stand in."""
    ctx, out = Context(S, f), []
    opener = f.name.startswith("00-")
    for n, line in enumerate(text.splitlines(), 1):
        kind = line_kind(line)
        for m in re.finditer(r"(?<![\[ء-ي-])ف[٠-٩]+-(?:[أ-د]|مث[٠-٩]+)(?![ء-ي])", line):
            out.append(Ref(f, n, "لغة الملفات", m.group(0), "", "مخفقة", "رمزُ ملفٍّ أو مثالٍ بغير نظام المعرّفات في النص المطبوع", m.start()))
        header = line.startswith("*(")
        files_re = (r"(?<![ء-ي])[وف]?(?:ال)?(?:ملف|ملفين|ملفات) ?(?:الأول|الثاني|الثالث|التالي|السابق)?(?![ء-ي])" if header else
                    r"(?<![ء-ي])[وف]?الملف (?:الأول|الثاني|الثالث|التالي|السابق) من هذا (?:الملحق|الفصل|الباب|المرجع)")
        for m in re.finditer(files_re, line):
            if header and re.search(r"الصوتي", line[m.end():m.end() + 8]):
                continue                                 # «الملف الصوتي»: the learner's recordings, a thing of the book
            out.append(Ref(f, n, "لغة الملفات", m.group(0), "", "مخفقة", "تقسيم الملفات ليس بنيةً في الكتاب المطبوع", m.start()))
        if kind != "dialogue" and not re.match(r"^\s*[✘✔◐]", line):
            masked = re.sub(r"\[[^\]]*\]", lambda m: " " * len(m.group(0)), mask_quotes(line, set()))
            for m in re.finditer(r"(?:انظر|راجع|في)\s+(?:ص\.?\s?|صفحة\s|الصفحة\s)[٠-٩]+|الصفحة (?:السابقة|التالية|المقابلة|الآتية)", masked):
                if kind == "note" and "،" in masked[:m.start()]:
                    continue                             # the page of the source just cited
                out.append(Ref(f, n, "رقم صفحة", m.group(0), "", "مخفقة", "لا إحالة إلى صفحةٍ من الكتاب: الترقيم يتغيّر", m.start()))
            for m in re.finditer(r"باب(?:ًا)? (?:ال)?رابع عشر|الأبواب الأربعة عشر|أربعة عشر بابًا|ثمانية مجلدات|المجلدات الثمانية|"
                                 r"\(من ثمانية\)|الأجزاء الأربعة|أربعة أجزاء|أجزاء الكتاب|(?<![ء-ي])ملحق (?:هـ|و|ز)(?![ء-ي])|المستوى (?:٠|صفر)(?![٠-٩])|"
                                 r"(?<![\[ء-ي])م٠(?![٠-٩])|المستويات ٠", masked):
                if "أربعة" in m.group(0) and "أجزاء" in m.group(0) + "الأجزاء" and not re.search(
                        r"الكتاب|السلسلة|التأسيس|التواصل|المنصّ?ات|التمكين|الجزء الأول", masked[max(0, m.start() - 60): m.end() + 60]):
                    continue                             # «الأجزاء الأربعة للإقرار بالحد»: an ordinary count
                out.append(Ref(f, n, "البنية القديمة", m.group(0), "", "مخفقة", "أثرٌ للأجزاء الأربعة أو الأبواب الأربعة عشر أو الثمانية", m.start()))
            for m in re.finditer(rf"(?<![ء-ي])الجزء ({O_RE}){L}", masked):
                near = masked[max(0, m.start() - 40): m.end() + 40]
                if re.search(r"التأسيس|التواصل|المنصّ?ات|التمكين|من الكتاب|من هذا الكتاب|من السلسلة|(?:تعلّمت|تعلمت|درست|عرفت) في\s*$", near):
                    out.append(Ref(f, n, "البنية القديمة", m.group(0), "", "مخفقة", "«الجزء» لا يصف بنية السلسلة", m.start()))
        for m in re.finditer(rf"(?<=انظر )باب (ال[ء-ي]+(?: ال[ء-ي]+)?)", line):
            if not any(plain(m.group(1)).startswith(plain(k)) for k in NAMES):
                out.append(Ref(f, n, "عنوان", m.group(0), "", "مخفقة", f"لا باب في السلسلة اسمه «{m.group(1)}»", m.start()))
        for m in re.finditer(rf"حلقة الباب ({O_RE}){L}(?!\s*من «سكريبتات)", line):
            out.append(Ref(f, n, "الكتاب المرافق", m.group(0), "«سكريبتات الحلقات»", "مخفقة",
                           "الحلقة في الكتاب المرافق «سكريبتات الحلقات»، والإحالة لا تسمّيه", m.start()))
        if ctx.unit[0] == "reference":
            for m in re.finditer(r"فصول الباب|أهداف الباب|فاتحة الباب(?! الأول)|خاتمة الباب|أبواب أخرى من الكتاب", line):
                out.append(Ref(f, n, "البنية القديمة", m.group(0), "المرجع الأول: بنك الأخطاء", "مخفقة",
                               "بنك الأخطاء مرجعٌ خارج ترقيم الأبواب، لا باب", m.start()))
        for m in re.finditer(r"(?<![ء-ي])[وف]?(?:في |من |إلى )?(هذا|هذه) (الباب|المرجع|الملحق|الفصل|الدرس)(?![ء-ي])", line):
            unit = m.group(2)
            u = ctx.unit[0]
            ok = {"الباب": u == "bab", "المرجع": u == "reference",
                  "الملحق": u in ("app", "program") or f == S.verification,
                  "الفصل": u in ("bab", "reference", "opening", "intro") and not opener,
                  "الدرس": u in ("bab",) and not opener}[unit]
            if not ok:
                out.append(Ref(f, n, "إشارة", m.group(0), f"{ctx.unit[0]}", "للقارئ",
                               f"«{m.group(1)} {unit}» في غير {unit}", m.start()))
    return out


def scan_openers(S, f, text):
    """The chapter table of a bab's opener (and of the bank's): each row names a chapter that exists, by its title."""
    ctx, out = Context(S, f), []
    if not f.name.startswith("00-") or ctx.unit[0] not in ("bab", "reference"):
        return out
    space = S.bab_chapters[ctx.bab] if ctx.bab else S.bank
    rows, n0 = [], None
    lines = text.splitlines()
    for n, line in enumerate(lines, 1):
        if re.match(r"^\|\s*الفصل\s*\|", line):
            n0 = n
            continue
        if n0 and line.startswith("|"):
            m = re.match(r"^\|\s*([٠-٩]+)\s*\|\s*([^|]+)\|", line)
            if m:
                rows.append((n, num(m.group(1)), m.group(2).strip()))
        elif n0 and rows:
            break
    for n, c, title in rows:
        p = space.get(c)
        if not p:
            out.append(Ref(f, n, "جدول الفصول", f"{ar(c)} | {title}", "", "مخفقة", f"لا فصل {ORDS[c - 1]}", 0))
        elif plain(title) != plain(p.title) and not plain(title).startswith(plain(p.title)) and not plain(p.title).startswith(plain(title)):
            out.append(Ref(f, n, "جدول الفصول", title, f"الفصل {ORDS[c - 1]}: {p.title}", "مخفقة",
                           "العنوان في جدول الفاتحة غير عنوان الفصل", 0))
        else:
            out.append(Ref(f, n, "جدول الفصول", title, f"الفصل {ORDS[c - 1]}: {p.title}", "سليمة", "", 0))
    if rows and len(rows) != len(space):
        out.append(Ref(f, rows[0][0], "جدول الفصول", f"{ar(len(rows))} صفًّا", f"{ar(len(space))} فصول", "مخفقة",
                       "عدد صفوف الجدول غير عدد الفصول", 0))
    return out


COUNT = {"درس واحد": 1, "درسين": 2, "ثلاثة دروس": 3, "أربعة دروس": 4}
PARTS = {"جزأين": 2, "ثلاثة أجزاء": 3, "قسمين": 2, "ثلاثة أقسام": 3, "أربعة أقسام": 4, "ملفين": 2}


def scan_headers(S, f, text):
    """The line under a chapter's title — «*(الباب الأول: الأسس، المستوى ١. الفصل في درسين …)*» — describes the
    chapter: its bab, the bab's name, its level, and the number of its lessons."""
    ctx, out = Context(S, f), []
    if ctx.unit[0] not in ("bab", "reference") or f.name.startswith("00-"):
        return out
    for n, line in enumerate(text.splitlines()[:8], 1):
        m = re.search(r"في (جزأين|ثلاثة أجزاء|قسمين|ثلاثة أقسام|أربعة أقسام|ملفين)", line) if line.startswith("*(") else None
        p = ctx.chapter
        if m and p and f == p.files[0] and (len(p.files) > 1 or "هذا القسم" in line) and PARTS[m.group(1)] != len(p.files):
            out.append(Ref(f, n, "رأس الفصل", m.group(0), f"{p.key}: {ar(len(p.files))} أقسام", "مخفقة",
                           "عدد أقسام الفصل في رأسه غير عددها", m.start()))
        if not ctx.bab:
            continue
        if not line.startswith("*(") or line.startswith("*(تابع"):
            continue
        m = re.search(rf"^\*\(الباب ({O_RE}): ([^،.]+)،", line)
        if m:
            b = ordn(m.group(1))
            if b != ctx.bab or plain(m.group(2)) != plain(S.bab_name[ctx.bab]):
                out.append(Ref(f, n, "رأس الفصل", m.group(0), f"الباب {ORDS[ctx.bab - 1]}: {S.bab_name[ctx.bab]}", "مخفقة",
                               "رأس الفصل يسمّي غير بابه", m.start()))
        m = re.search(r"في (درس واحد|درسين|ثلاثة دروس|أربعة دروس)", line)
        p = ctx.chapter
        if m and p and p.lessons and COUNT[m.group(1)] != len(p.lessons) and f == p.files[0]:
            out.append(Ref(f, n, "رأس الفصل", m.group(0), f"{p.key}: {ar(len(p.lessons))} من الدروس المعنونة", "للقارئ",
                           "عدد الدروس في رأس الفصل غير عدد عناوينها", m.start()))
        break
    return out


def scan_days(S, f, text):
    """The days of the pronunciation programme: one to thirty, and «الآتي» ahead, «مرّ» behind."""
    out = []
    ctx = Context(S, f)
    if ctx.unit[0] != "program":
        return out
    day = 0
    for n, line in enumerate(text.splitlines(), 1):
        h = re.match(r"^##\s+اليوم ([٠-٩]+):", line)
        if h:
            day = num(h.group(1))
            continue
        for m in re.finditer(r"(?<![ء-ي])[لو]?(?:اليوم|الأيام|اليومين|للأيام) ([٠-٩]+)(?:\s*[–-]\s*([٠-٩]+))?", line):
            a = num(m.group(1))
            z = num(m.group(2)) if m.group(2) else a
            bad = [k for k in range(a, z + 1) if k not in S.days]
            before = line[max(0, m.start() - 30):m.start()]
            if bad:
                out.append(Ref(f, n, "يوم البرنامج", m.group(0), "", "مخفقة", "البرنامج ثلاثون يومًا", m.start()))
            elif re.search(r"الآتي|سيأتي|القادم", before) and a <= day:
                out.append(Ref(f, n, "يوم البرنامج", m.group(0), f"اليوم {ar(a)}", "مخفقة",
                               f"«الآتي» في اليوم {ar(day)} إلى يومٍ مضى", m.start()))
            elif re.search(DIRECTION_BACK, before) and a > day:
                out.append(Ref(f, n, "يوم البرنامج", m.group(0), f"اليوم {ar(a)}", "مخفقة",
                               f"«مرّ» في اليوم {ar(day)} إلى يومٍ آتٍ", m.start()))
            else:
                out.append(Ref(f, n, "يوم البرنامج", m.group(0), f"اليوم {ar(a)}", "سليمة", "", m.start()))
    return out


UNITISH = r"(?:الفصل|الباب|الدرس|«|مدخل|أول|مطلع|المقدمة|فاتحة|بطاقة|القسم|المثال|الموقف|الحديث|قول|كلام|ذكر|الجدول|جدول|القاعدة|التنبيه|الحوار|المقارنة|النموذج|تعريف)"
POINTER = (rf"{B}[وف]?(?:انظر|انظري|انظروا)(?:\s+أيضًا)?{L}(?!:?\s+(?:كيف|إلى|هل|ماذا|لماذا|ما|من|فيما|حولك|في المرآة|أمامك|هنا))"
           rf"|{B}[وف]?راجع(?=\s+(?:القسم|الفصل|الباب|جدول|الملحق|بطاقة|المثال|الموقف|قائمة|التمهيد|المقدمة|أهداف))"
           rf"|{B}(?:ما|مما|فيما)\s+(?:سبق|تقدّم|مرّ){L}"
           rf"|{B}(?:كما|وكما|وقد|قد)\s+(?:سبق|تقدّم|تقدم|مرّ|مر|مرّت|مرت|أسلفنا)(?:\s+(?:معنا|بك|بنا|ذكره|ذكرها|بيانه))?{L}"
           rf"|{B}(?:الذي|التي)\s+(?:سبق|تقدّم|مرّ|مرّت){L}(?!\s+إلي)"
           rf"|{B}(?:سبق|تقدّم|مرّ|مرّت)(?:\s+(?:معنا|بك|بنا))?\s+(?:في|أن ذكرنا|ذكره|ذكرها|بيانه){L}(?=\s*{UNITISH})"
           rf"|{B}(?:كما\s+|و)?(?:سيأتي|ستأتي)(?:\s+(?:تفصيله|تفصيلها|بيانه|بيانها))?{L}(?=\s*(?:في|أن|من|:|،|\.))"
           rf"|{B}(?:سنعود|وسنعود|فسنعود)\s+إلي{L}")


def unit_before(S, ctx, f, n):
    """The text of the reader's unit (the bab, the opening, the bank…) up to the pointer."""
    v, u = ctx.vol, ctx.unit
    files = [x for x, vv, uu in S.files if vv == v and uu == u]
    text = ""
    for x in files:
        if x == f:
            return text + "\n".join(x.read_text(encoding="utf-8").splitlines()[:n - 1])
        text += x.read_text(encoding="utf-8") + "\n"
    return text


def series_before(S, f):
    """{volume: its text} for every file before this one in reading order."""
    out = defaultdict(str)
    for x, v, u in S.files:
        if x == f:
            break
        out[v] += x.read_text(encoding="utf-8") + "\n"
    return out


def pointer_scope(S, ctx, f, n, phrase, back, fwd):
    """Where a pointer without an address looks: above or below in the file, the chapter's entry, the bab's opener,
    the bank's opener; «سبق» the reader's unit before it, «سيأتي» the chapter after it; otherwise the chapter."""
    lines = f.read_text(encoding="utf-8").splitlines()
    if re.search(r"أعلاه|آنفًا|فيما سبق|قبل قليل", phrase):
        return "\n".join(lines[:n - 1]), "ما قبله في الملف"
    if re.search(r"أدناه|فيما يلي", phrase):
        return "\n".join(lines[n:]), "ما بعده في الملف"
    if re.search(r"مدخل (?:هذا )?الفصل|أول الفصل|مطلع الفصل", phrase) and ctx.chapter:
        return ctx.chapter.files[0].read_text(encoding="utf-8").split("\n## الدرس")[0], "مدخل الفصل"
    if re.search(r"فاتحة الباب|فاتحته|فاتحة هذا الباب", phrase) and ctx.bab:
        opener = next(x for x in unit_files(VOL_OF_BAB[ctx.bab], ("bab", ctx.bab)) if x.name.startswith("00-"))
        return opener.read_text(encoding="utf-8"), "فاتحة الباب"
    if re.search(r"أول هذا المرجع|فاتحة المرجع", phrase):
        return unit_files(11, ("reference",))[0].read_text(encoding="utf-8"), "فاتحة المرجع"
    if back:
        return unit_before(S, ctx, f, n), "ما قبله في وحدته"
    place = ctx.chapter
    if place is None:
        return "\n".join(lines[n:] if fwd else lines), "الملف"
    text, here = "", None
    for x in place.files:
        if x == f:
            here = len(text) + sum(len(l) + 1 for l in lines[:n])
        text += x.read_text(encoding="utf-8") + "\n"
    if fwd and here is not None:
        return text[here:], "ما بعده في الفصل"
    return text, "الفصل"


def found_in(what, quoted, words, text):
    t = plain(text)
    if quoted:
        return all(plain(q) in t or plain(re.sub(r"(?<!\S)ال", "", q)) in t for q in quoted)
    hits = [w for w in words if w in t or (w.startswith("ال") and w[2:] in t)]
    return len(hits) * 2 >= len(words)


def scan_pointers(S, f, text):
    """«انظر»، «راجع»، «سبق»، «تقدّم»، «كما مرّ»، «سيأتي» without an address: the thing they name must be where
    they point (a quoted title in «…», or the words that follow). «ما سبق» names nothing and is only counted."""
    ctx, out = Context(S, f), []
    keep = set(NAMES) | {"المدخل", "بنك الأخطاء", "المقدمة"}
    companions = {plain(t) for t in COMPANIONS.values()}
    for n, raw in enumerate(text.splitlines(), 1):
        kind = line_kind(raw)
        if kind in ("heading", "dialogue") or re.match(r"^\s*[✘✔◐]", raw):
            continue
        line = re.sub(r"«([^«»]*)»", lambda m: "«" + "ـ" * len(m.group(1)) + "»", raw)   # speech is not a pointer
        for m in re.finditer(POINTER, line):
            addressed = [t for t in tokens(mask_quotes(raw, keep)) if m.end() - 3 <= t[1] <= m.end() + 70]
            if addressed:
                continue                                 # an address follows: judged with the addresses
            if re.match(r"(?:ما|مما|فيما)\s", m.group(0)):
                out.append(Ref(f, n, "إحالة نسبية", m.group(0), "ما قبله", "سليمة", "لا تسمّي شيئًا يُبحث عنه", m.start()))
                continue
            tail = raw[m.end():m.end() + 110]
            phrase = re.split(r"[.؛)\n]|،\s*(?:ثم|و\S+)\s", tail)[0]
            if re.search(r"[A-Za-z]|[٠-٩]+/[٠-٩]+|\([٠-٩]+|(?<![ء-ي])ص[٠-٩]|^[:\s]*[^،:]{2,40}،\s*[^،]{2,60}،", tail[:90]) \
                    or re.search(r"الأطلس|الإيضاح في|السلسلة الصحيحة|والخمسين|والأربعين|والثلاثين|والعشرين", phrase):
                continue                                 # a source outside the series, cited in a note
            back = re.search(r"سبق|تقدّ?م|مرّ?|أسلفنا", m.group(0)) is not None
            fwd = re.search(r"سيأتي|ستأتي|سنعود", m.group(0)) is not None
            quoted = [q.strip() for q in re.findall(r"«([^«»]{3,60})»", phrase)]
            if quoted and all(plain(q) in companions for q in quoted):
                out.append(Ref(f, n, "إحالة نسبية", m.group(0) + tail[:len(phrase)], "الكتاب المرافق: " + "، ".join(quoted),
                               "سليمة", "", m.start()))
                continue
            words = [w for w in plain(re.sub(r"«[^«»]*»", " ", phrase)).split()
                     if w not in STOP and len(w) > 2 and w not in ("اعلاه", "ادناه", "انفا", "ايضا", "هنا", "هناك", "تفصيل",
                                                                  "ذكره", "بيانه", "معنا", "الفصل", "الدرس", "فاتحته", "مدخل")][:3]
            if not quoted and not words:
                out.append(Ref(f, n, "إحالة نسبية", m.group(0), "في موضعها", "سليمة", "لا تسمّي شيئًا يُبحث عنه", m.start()))
                continue
            scope, where = pointer_scope(S, ctx, f, n, phrase, back, fwd)
            what = "، ".join(f"«{q}»" for q in quoted) if quoted else " ".join(words)
            text_ = m.group(0) + tail[:len(phrase)]
            if found_in(what, quoted, words, scope):
                out.append(Ref(f, n, "إحالة نسبية", text_, f"{where}: {what}", "سليمة", "", m.start()))
                continue
            if back:
                earlier = [v for v, t in series_before(S, f).items() if v != ctx.vol and found_in(what, quoted, words, t)]
                if earlier:
                    out.append(Ref(f, n, "إحالة نسبية", text_, f"المجلد {VOLW[earlier[-1] - 1]}: {what}", "للقارئ",
                                   "مرّ في مجلدٍ سابق، والإحالة لا تسمّيه", m.start()))
                    continue
            out.append(Ref(f, n, "إحالة نسبية", text_, f"{where}: {what}", "للقارئ", f"لا يظهر {what} في {where}", m.start()))
    return out


def scan(S):
    refs = []
    scenes = dialogues(S)
    for f, v, u in S.files:
        text = f.read_text(encoding="utf-8")
        if u == ("back", "المصادر-والمراجع"):
            continue                                     # generated by bibliography.py: its «(المجلد ١، ٦)» are an index
        refs += scan_addresses(S, f, text)
        refs += scan_ids(S, f, text)
        refs += scan_classes(S, f, text)
        refs += scan_lines(S, f, text, scenes)
        refs += scan_forms(S, f, text)
        refs += scan_openers(S, f, text)
        refs += scan_headers(S, f, text)
        refs += scan_days(S, f, text)
        refs += scan_pointers(S, f, text)
    return refs


# ------------------------------------------------------------------------------------------------ the reading
#
# What a pattern cannot decide, a reader decided, passage by passage (the flagged passages were read in full). Each
# entry is (file under book/, a verbatim piece of the line, the reading). A reading turns «للقارئ» or a pattern's
# «مخفقة» into «مقروءة»; a finding turns a pattern's «سليمة» into «مخفقة». Both are matched on the verbatim text, so
# an edited line falls out of them and is judged afresh.

READINGS = [
    ("المجلد-الأول/الافتتاحية/06-منزلة-العربية.md", "فهي من الباب الثاني لا من الباب الأول",
     "«الباب» هنا صنف الدعوى (الأول ما يُحسم بالنص، والثاني ما يُحسم بالمقارنة)، لا باب السلسلة (premove.py: NOT_A_REFERENCE)"),
    ("المجلد-الأول/الافتتاحية/18-كيف-تقرأ-المجلدات-وعهد-المؤلف.md", "وليس بابًا رابع عشر ولا مستوًى",
     "نفيٌ للبنية القديمة تطلبه بوابة البنية (premove.py)، لا إحالة إليها"),
    ("المجلد-الأول/الافتتاحية/18-كيف-تقرأ-المجلدات-وعهد-المؤلف.md", "عاد إلى بنك الأخطاء",
     "في الفصل الذي يعرّف المجلدات؛ وقد سمّى المرجع ومجلده في أوله: «وهو المجلد الحادي عشر»"),
    ("المجلد-الثاني/الباب-الثاني/ف01-أ-المدخل-والمخارج.md", "ويُروى في مقدمة الكتاب",
     "مقدمة كتاب «العين» للخليل، لا مقدمة هذا الكتاب"),
    ("المجلد-الأول/الافتتاحية/05-البيان-عند-علماء-العربية.md", "وهذا الباب، على قصره",
     "باب سيبويه في «الكتاب»، لا باب السلسلة"),
    ("المجلد-الأول/الافتتاحية/09-ما-رأيته.md", "ما فتح الله به عليّ في هذا الباب",
     "«الباب» بمعنى الموضوع (الاستعمال اللغوي)"),
    ("المجلد-الأول/الافتتاحية/09-ما-رأيته.md", "قد ظلمت هذا الباب",
     "«الباب» بمعنى الموضوع (الاستعمال اللغوي)"),
    ("المجلد-العاشر/الخاتمة/00-خاتمة-الكتاب.md", "وما أنا في هذا الباب إلا طالب علمٍ",
     "«الباب» بمعنى الموضوع (الاستعمال اللغوي)"),
    ("المجلد-الحادي-عشر/الملاحق/ملحق-د-النماذج-الكاملة.md", "من أشهر ما يُستشهد به في هذا الباب",
     "«الباب» بمعنى الموضوع (الاستعمال اللغوي)"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/ف06-الصوت-والسرعة-وترتيب-الأفكار.md", "من أخطاء هذا الباب الثلاثي",
     "«الباب» بمعنى الصنف (الصوت والسرعة والترتيب)، على ما أُبقي في البنك مما معناه الموضوع لا باب السلسلة (الدليل، الباب ١١٢هـ §١)"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/ف07-المقابلات-والخطابة-والإعلام-والعلماء.md", "من هذا الدرس أو هذا اللقاء",
     "درس الشيخ في البطاقة، لا درسٌ من الكتاب"),
    ("المجلد-الحادي-عشر/الملاحق/ملحق-أ-المعجم-التطبيقي", "تُستعمل عبارات هذا الباب",
     "أبواب المعجم التطبيقي نفسه، كما يسمّيها في مقدمته («وآخر كل باب سطر «تنبيه»»): الاستعمال المعجمي لا باب السلسلة"),
    ("المجلد-الأول/الافتتاحية/03-القول-في-القرآن.md", "سيأتي في الكتاب من فنّ الاعتذار والرفض بأدب",
     "تمهيدٌ عامّ في المقدمة لما في الكتاب، لا عنوانٌ يُرجع إليه"),
    ("المجلد-الأول/الافتتاحية/03-القول-في-القرآن.md", "سيأتي من مراتب المخاطبة ودرجات الرسمية",
     "تمهيدٌ عامّ في المقدمة لما في الكتاب، لا عنوانٌ يُرجع إليه"),
    ("المجلد-الرابع/الباب-الرابع/ف09-ب-التطبيق-والتقويم.md", "خطأ بلاغي (خ-٨)",
     "رمز صنفٍ مفسَّرٌ في موضعه («خطأ بلاغي»)، لا إحالة إلى بطاقة"),
]

FINDINGS = [
    ("المجلد-الثاني/الملاحق/ملحق-الباب-الثاني-برنامج-النطق.md", "(كما مرّ في مقدمة الكتاب)",
     "المجلد الأول، المقدمة: لا رموز أداءٍ فيها",
     "«مقدمة الكتاب» هي المقدمة في المجلد الأول، ولا رموز أداءٍ فيها؛ ورموز الأداء في «الرموز والاصطلاحات» من مقدّمات كل مجلد"),
    ("المجلد-الثالث/الباب-الثالث/ف01-أ-الاسمية-والفعلية.md", "«كأنّهم يقدّمون الذي بيانُه أهمُّ لهم»",
     "المجلد الثالث، الباب الثالث، الفصل الأول، «من التراث» (س٦٢)",
     "قول سيبويه «الذي مرّ» ليس بلفظه هناك: سقطت «[إنّما]» من النقل المتحقّق (سجل النقول م٣-٠٢٣)"),
    ("المجلد-الثالث/الباب-الثالث/ف09-ب-متى-تطيل.md", "في النموذج السداسي (الفصل الأول)",
     "المجلد الأول، الباب الأول، الفصل الأول، الدرس الثاني: النموذج السداسي",
     "«الفصل الأول» في المجلد الثالث هو «الجملة الاسمية والفعلية»؛ والنموذج السداسي في الباب الأول"),
    ("المجلد-الرابع/الباب-الرابع/ف10-أ-الاقتباس-والتضمين.md", "فصل محوري في ثلاثة دروس",
     "المجلد الرابع، الباب الرابع، الفصل العاشر: أربعة دروس معنونة",
     "رأس الفصل يقول ثلاثة دروس، والفصل فيه «الدرس الأول» إلى «الدرس الرابع»"),
    ("المجلد-العاشر/الباب-الثالث-عشر/ف03-أ-الملف-الصوتي-ومشروع-التخرج.md", "وهو خاتمة الكتاب. الفصل في",
     "المجلد العاشر، خاتمة الكتاب: وحدةٌ مستقلة بعد الباب الثالث عشر",
     "رأس الفصل يجعل الباب «خاتمة الكتاب»، و«خاتمة الكتاب» وحدةٌ مستقلة تليه (volumes.py: closing)؛ وفاتحة الباب تقول «الباب الأخير في الكتاب»"),
    ("المجلد-الثامن/الباب-التاسع/ف04-ب-الدرس-الثاني.md", "في الفصل الخامس: الجسر، والانعطاف، والإرجاء",
     "المجلد الثامن، الباب التاسع، الفصل الخامس، الدرس الثاني",
     "لا تُسمّى في الفصل الخامس أدواتٌ بهذه الأسماء: فيه «اعترف… ← رد على مضمونه… ← أعِد النقاش»، و«لا أعلم» بلا حرج؛ و«الإرجاء» صيغةٌ في جدول هذا الدرس نفسه"),
    ("المجلد-الثالث/الباب-الثالث/ف08-ب-الدقة-والإيحاء-والسجل.md", "وهذا هو الأدب الذي مرّ بك في الفصل الأول",
     "المجلد الأول، الباب الأول، الفصل الأول (المعيار الخامس: الأدب)",
     "«الفصل الأول» في المجلد الثالث هو «الجملة الاسمية والفعلية»؛ والأدب معيارٌ من معايير الكلام الخمسة في الباب الأول"),
    ("المجلد-الثالث/الباب-الثالث/ف08-ج-التطبيق-والتقويم.md", "بالأدب الذي درسته في الفصل الأول",
     "المجلد الأول، الباب الأول، الفصل الأول (المعيار الخامس: الأدب)",
     "«الفصل الأول» في المجلد الثالث هو «الجملة الاسمية والفعلية»؛ والأدب معيارٌ من معايير الكلام الخمسة في الباب الأول"),
    ("المجلد-الثاني/الباب-الثاني/ف06-ب-التطبيق-والتقويم.md", "ولباب اللسان كله (الفصول ١-٦)",
     "المجلد الثاني، الباب الثاني: اثنا عشر فصلًا",
     "باب اللسان اثنا عشر فصلًا، ومخرج إتقانه كاملًا في الفصل الثاني عشر («يتحقق مخرج إتقان الباب الثاني كاملًا… حين ينفّذ المتدرب بروتوكول التشخيص»)"),
    ("المجلد-الثاني/الباب-الثاني/ف06-ب-التطبيق-والتقويم.md", "مستوفيًا مخرج إتقان الباب الثاني كاملًا",
     "المجلد الثاني، الباب الثاني، الفصل الثاني عشر: معيار الإتقان",
     "الفصل السادس لا يستوفي مخرج الباب كله؛ والفصلان الثالث والخامس يقولان «اقترابًا من مخرج إتقان الباب»"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/00-فاتحة-بنك-الأخطاء.md", "تصنيف الخطأ في دليل الأخطاء الموحد",
     "«دليل الأخطاء الموحد»: لا يُطبع في السلسلة ولا في الكتابين المرافقين",
     "إحالة إلى وثيقةٍ من وثائق الإنتاج (الدليل، الجزء الثالث، الباب العاشر) لا يجدها القارئ"),
]

# The exact corrections of the failures (current text → proposed text), for the author; nothing is applied here.
PROPOSALS = [
    ("المجلد-الأول/الافتتاحية/05-البيان-عند-علماء-العربية.md", 90,
     "وهذا مما يعالجه الكتاب في باب العبارة، وفي فصول الترجمة الحرفية.",
     "وهذا مما يعالجه الكتاب في باب العبارة (المجلد الثالث)، وفي فصول الترجمة الحرفية."),
    ("المجلد-الأول/الافتتاحية/18-كيف-تقرأ-المجلدات-وعهد-المؤلف.md", 74,
     "وطريقهما في باب البيان وباب المقام؛",
     "وطريقهما في باب البيان (المجلد الرابع) وباب المقام (المجلد الخامس)؛"),
    ("المجلد-الأول/الباب-الأول/ف02-ب-الدرس-الثاني.md", 124,
     "| الباب الثاني، والباب التاسع (المنبر، المجلد الثامن) |",
     "| الباب الثاني (اللسان، المجلد الثاني)، والباب التاسع (المنبر، المجلد الثامن) |"),
    ("المجلد-الأول/الباب-الأول/ف01-ب-الدرس-الثاني.md", 314,
     "ثم يُبنى عليها الارتجال في الباب الأخير.", "ثم يُبنى عليها الارتجال في الباب الأخير (الباب الثالث عشر، المجلد العاشر)."),
    ("المجلد-الأول/الباب-الأول/ف02-ب-الدرس-الثاني.md", 268,
     "الباب الثالث (الجملة القصيرة والطويلة، المجلد الثالث)", "الباب الثالث، الفصل التاسع (المجلد الثالث)"),
    ("المجلد-الثاني/الباب-الثاني/ف03-ج-التطبيق-والتقويم.md", 364,
     "(يُضاف إلى زمن الدرس الأول في ف٣-أ)", "(يُضاف إلى زمن الدرس الأول)"),
    ("المجلد-الثاني/الباب-الثاني/ف04-ب-التطبيق-والتقويم.md", 358,
     "(يُضاف إلى زمن ف٤-أ)", "(يُضاف إلى زمن المدخل والدرس)"),
    ("المجلد-الثاني/الباب-الثاني/ف05-ج-التطبيق-والتقويم.md", 358,
     "(تضاف إلى زمن ف٥-أ وف٥-ب)", "(تضاف إلى زمن المدخل والدرسين)"),
    ("المجلد-الثاني/الباب-الثاني/ف06-ب-التطبيق-والتقويم.md", 356,
     "(يُضاف إلى زمن ف٦-أ)", "(يُضاف إلى زمن المدخل والدرس)"),
    ("المجلد-الثاني/الباب-الثاني/ف06-ب-التطبيق-والتقويم.md", 346,
     "يُعدّ المتدرب متقنًا لهذا الفصل، ولباب اللسان كله (الفصول ١-٦)، إذا حقق ما يأتي:",
     "يُعدّ المتدرب متقنًا لهذا الفصل، ولما مضى من باب اللسان (الفصول ١-٦)، إذا حقق ما يأتي:"),
    ("المجلد-الثاني/الباب-الثاني/ف06-ب-التطبيق-والتقويم.md", 350,
     "مستوفيًا مخرج إتقان الباب الثاني كاملًا:", "اقترابًا من مخرج إتقان الباب الثاني كاملًا:"),
    ("المجلد-الثاني/الملاحق/ملحق-الباب-الثاني-برنامج-النطق.md", 15,
     "**رموز الأداء المستعملة (كما مرّ في مقدمة الكتاب):**", "**رموز الأداء المستعملة:**"),
    ("المجلد-الثاني/الملاحق/ملحق-الباب-الثاني-برنامج-النطق.md", 480,
     "في الأيام ١٦–٣٠ (الملف الثاني من هذا الملحق) تنتقل", "في الأيام ١٦–٣٠ تنتقل"),
    ("المجلد-الثاني/الملاحق/ملحق-الباب-الثاني-برنامج-النطق-٢.md", 1,
     "*(تتمة ملحق الباب الثاني: برنامج النطق اليومي في ثلاثين يومًا. الأيام ١٦–٣٠. راجع القسم الأول لمقدمة الاستعمال ورموز الأداء، وللأيام ١–١٥.)*",
     "*(الأيام ١٦–٣٠ من برنامج النطق اليومي. ومقدمة الاستعمال ورموز الأداء والأيام ١–١٥ في أول هذا الملحق.)*"),
    ("المجلد-الثالث/الباب-الثالث/ف01-أ-الاسمية-والفعلية.md", 286,
     "«كأنّهم يقدّمون الذي بيانُه أهمُّ لهم»", "«كأنّهم [إنّما] يقدّمون الذي بيانُه أهمُّ لهم»"),
    ("المجلد-الثالث/الباب-الثالث/ف08-ب-الدقة-والإيحاء-والسجل.md", 162,
     "وهذا هو الأدب الذي مرّ بك في الفصل الأول.",
     "وهذا هو الأدب الذي مرّ بك في المجلد الأول، الباب الأول، الفصل الأول."),
    ("المجلد-الثالث/الباب-الثالث/ف08-ج-التطبيق-والتقويم.md", 53,
     "وما علاقة هذا بالأدب الذي درسته في الفصل الأول؟",
     "وما علاقة هذا بالأدب الذي درسته في المجلد الأول، الباب الأول، الفصل الأول؟"),
    ("المجلد-الثالث/الباب-الثالث/ف09-ب-متى-تطيل.md", 362,
     "في النموذج السداسي (الفصل الأول)", "في النموذج السداسي (المجلد الأول، الباب الأول، الفصل الأول)"),
    ("المجلد-الرابع/الباب-الرابع/ف03-أ-فن-الافتتاح.md", 121,
     "انظر الباب الرابع الفصل الثاني", "انظر الباب الرابع، الفصل الثاني"),
    ("المجلد-الرابع/الباب-الرابع/ف01-ج-التطبيق-والتقويم.md", 323,
     "أساس المخرج المقرر للمستوى الثالث:", "أساس المخرج المقرر للمستوى الرابع:"),
    ("المجلد-الرابع/الباب-الرابع/ف02-ج-التطبيق-والتقويم.md", 335,
     "يخدم المخرج المقرر للمستوى الثالث:", "يخدم المخرج المقرر للمستوى الرابع:"),
    ("المجلد-الثامن/الباب-التاسع/00-فاتحة-الباب-التاسع.md", 52,
     "هذا التسجيل خط الأساس للمستوى الثامن.", "هذا التسجيل خط الأساس للمستوى التاسع."),
    ("المجلد-التاسع/الباب-العاشر/00-فاتحة-الباب-العاشر.md", 47,
     "هذان التسجيلان خط الأساس للمستوى التاسع.", "هذان التسجيلان خط الأساس للمستوى العاشر."),
    ("المجلد-العاشر/الباب-الثالث-عشر/ف03-ج-التطبيق-والتقويم-والخاتمة.md", 243,
     "وللباب الثالث عشر كله، وللمستوى الثاني عشر تبعًا له،", "وللباب الثالث عشر كله، وللمستوى الثالث عشر تبعًا له،"),
    ("المجلد-الرابع/الباب-الرابع/ف10-أ-الاقتباس-والتضمين.md", 5,
     "فصل محوري في ثلاثة دروس: القرآن والحديث، ثم الشعر والأمثال والحكم، ثم تطبيق ختامي",
     "فصل محوري في أربعة دروس: القرآن، ثم الحديث، ثم الشعر، ثم الأمثال والحكم، ثم تطبيق ختامي"),
    ("المجلد-الخامس/الباب-الخامس/ف02-أ-المدخل-والدرس-الأول.md", 23,
     "ويُترك تفصيله للبابين الحادي عشر والثاني عشر.",
     "ويُترك تفصيله للبابين الحادي عشر والثاني عشر (المجلد العاشر)."),
    ("المجلد-السابع/الباب-السابع/ف05-ج-الإقناع-التطبيق-والتقويم.md", 194,
     "(مثال ف٥-مث٥٢)", "(المثال [م٣-ب٧-ف٥-مث٥٢])"),
    ("المجلد-الثامن/الباب-التاسع/ف01-ب-العبارة-والصوت-والنموذج.md", 278,
     "ويقابلها في بنك الأخطاء (المجلد الحادي عشر) الصنفان «خ-٢٠» (أخطاء الخطابة) و«خ-٢» (الأخطاء الأدائية):",
     "ويقابلها في بنك الأخطاء (المجلد الحادي عشر) «أخطاء الخطابة» في الفصل السابع، والأخطاء النطقية الأدائية «خ-٢» في الفصلين الأول والثاني:"),
    ("المجلد-الثامن/الباب-التاسع/ف04-ب-الدرس-الثاني.md", 207,
     "لها أدوات تفصيلية في الفصل الخامس: الجسر، والانعطاف، والإرجاء.",
     "لها أدوات تفصيلية في الفصل الخامس (الدرس الثاني)."),
    ("المجلد-العاشر/الباب-الثالث-عشر/ف01-أ-المدخل-وسلم-الارتجال.md", 5,
     "والملف الثاني لثلاث درجات أخرى وللحوار الممتد، والملف الثالث لبنك المواقف",
     "والثاني لثلاث درجات أخرى وللحوار الممتد، والثالث لبنك المواقف"),
    ("المجلد-العاشر/الباب-الثالث-عشر/ف03-أ-الملف-الصوتي-ومشروع-التخرج.md", 6,
     "وهو خاتمة الكتاب. الفصل في ملفين: هذا للملف الصوتي المرئي ولمشروع التخرج بمحطاته ومعاييره، والثاني ليوم الأداء الختامي وحواره الممتد والتطبيقات والتقويم وكلمة ختامية إلى القارئ.",
     "وهو آخر أبواب الكتاب. الفصل في ثلاثة أقسام: هذا للملف الصوتي المرئي ولمشروع التخرج بمحطاته ومعاييره، والثاني ليوم الأداء الختامي وحواره الممتد، والثالث للتطبيقات والتقويم وكلمة ختامية إلى القارئ."),
    ("المجلد-العاشر/الخاتمة/00-خاتمة-الكتاب.md", 35,
     "فأذكّرك بما مرّ في المقدمة:", "فأذكّرك بما مرّ في المقدمة (المجلد الأول، الفصل الثامن):"),
    ("المجلد-العاشر/الخاتمة/00-خاتمة-الكتاب.md", 43,
     "وقد مرّ في المقدمة أن العبد", "وقد مرّ في المقدمة (المجلد الأول، الفصل الثالث) أن العبد"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/00-فاتحة-بنك-الأخطاء.md", 28,
     "كل بطاقة في هذا المرجع تحمل رمزًا مثل [م٤-ب١٣-ف١-مث٥] للإحالة إليها",
     "كل بطاقة من الفصل الثالث فما بعده تحمل رمزًا مثل [م٤-ب١٣-ف٣-مث١] للإحالة إليها"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/00-فاتحة-بنك-الأخطاء.md", 30,
     "تصنيف الخطأ في دليل الأخطاء الموحد (خ-١ صوتي، خ-٣ نحوي…)", "صنف الخطأ برمزه (خ-١ صوتي، خ-٣ نحوي…)"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/00-فاتحة-بنك-الأخطاء.md", 52,
     "### فصول الباب", "### فصول المرجع"),
    ("المجلد-الحادي-عشر/المرجع-الأول-بنك-الأخطاء/ف07-المقابلات-والخطابة-والإعلام-والعلماء.md", 26,
     "في أبواب أخرى من الكتاب (المؤسسة، والمنبر والمنصة، والإعلام، والمجالس)؛",
     "في أبواب الكتاب: المؤسسة (الباب العاشر، المجلد التاسع)، والمنبر والمنصة (الباب التاسع، المجلد الثامن)، والإعلام والتقديم (الباب الحادي عشر، المجلد العاشر)، والمجالس (الباب الثامن، المجلد الثامن)؛"),
    ("المجلد-الحادي-عشر/الملاحق/ملحق-ج-أخطاء-قد-تظهر-عند-بعض-المتعلمين.md", 92,
     "(انظر باب التدريب الصوتي)", "(انظر المجلد الثاني، الباب الثاني، الفصل الحادي عشر)"),
    ("المجلد-الحادي-عشر/الملاحق/ملحق-د-النماذج-الكاملة.md", 149,
     "الذي تراه أيضًا في حلقة الباب العاشر (المجلد التاسع).",
     "الذي تراه أيضًا في حلقة الباب العاشر من «سكريبتات الحلقات» (الكتاب المرافق)."),
]
NOTES = {   # what the author decides beyond the exact text (the proposal is the smallest correction)
    ("00-فاتحة-بنك-الأخطاء.md", 28): "بطاقات الفصلين الأول والثاني (٤١ بطاقة) بلا معرّفات؛ فإما هذا التقييد، وإما أن تُعطى معرّفاتها فيصدق الإطلاق.",
    ("00-فاتحة-بنك-الأخطاء.md", 30): "أو يُطبع جدول الأصناف التي تحملها البطاقات (خ-١…خ-١٧) من الدليل (الجزء الثالث، الباب العاشر §١) في فاتحة المرجع.",
    ("ملحق-الباب-الثاني-برنامج-النطق.md", 15): "«مقدمة الكتاب» هي المقدمة في المجلد الأول، ولا رموز فيها؛ والرموز في صفحة «الرموز والاصطلاحات» من مقدّمات كل مجلد، إلا «الخط العريض».",
}


def review(refs):
    """Apply the readings and the findings; attach the proposals."""
    lines = {}

    def line_of(r):
        if r.f not in lines:
            lines[r.f] = r.f.read_text(encoding="utf-8").splitlines()
        return lines[r.f][r.line - 1]

    for r in refs:
        if r.verdict in ("مخفقة", "للقارئ"):
            for f, piece, reading in READINGS:           # every flagged reference of a line the reader has read
                if str(r.f.relative_to(BOOK)).startswith(f) and piece in line_of(r):
                    r.verdict, r.note = "مقروءة", reading
                    break
    for f, piece, target, note in FINDINGS:
        path = BOOK / f
        hit = False
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if piece in line:
                hit = True
                mine = [r for r in refs if r.f == path and r.line == n and (r.verdict == "للقارئ" or r.text and r.text in piece)]
                for r in mine:
                    r.verdict, r.target, r.note = "مخفقة", target, note
                if not mine:
                    refs.append(Ref(path, n, "قراءة", piece, target, "مخفقة", note, line.find(piece)))
        if not hit:
            print(f"  (قراءة لم تعد تطابق: {f}: «{piece}»)")
    for f, piece, reading in READINGS:
        if not any(r.verdict == "مقروءة" and r.note == reading and str(r.f.relative_to(BOOK)).startswith(f) for r in refs):
            print(f"  (قراءة لا يحتاج إليها شيء: {f}: «{piece}»)")
    stale = []
    for f, n, cur, new in PROPOSALS:
        path = BOOK / f
        text = path.read_text(encoding="utf-8").splitlines()
        if n > len(text) or cur not in text[n - 1]:
            stale.append(f"{f}:{n}")
    return stale


# ------------------------------------------------------------------------------------------------ the report

def md_escape(s):
    return s.replace("|", "\\|").replace("\n", " ")


def write_report(refs, stale):
    fails = [r for r in refs if r.verdict == "مخفقة"]
    reads = [r for r in refs if r.verdict == "للقارئ"]
    read_ok = [r for r in refs if r.verdict == "مقروءة"]
    kinds = sorted({r.kind for r in refs})
    verdicts = ["سليمة", "مقروءة", "للقارئ", "مخفقة"]
    by = Counter((r.kind, r.verdict) for r in refs)
    L = ["# تدقيق الإحالات الداخلية", "",
         "من `python3 pdf/xrefs.py` (الدليل، الباب ١١١ §٢ والأبواب ١١٢د–١١٢و؛ ومقدمة المجلد الأول، الفصل السابع عشر: "
         "«وإذا أحال الكتاب إلى موضعٍ في مجلدٍ آخر ذكر المجلد مع الباب والفصل»). "
         "تُستخرج كل إحالةٍ في مصادر المجلدات الأحد عشر، وتُحلّ على البنية الحيّة (`volumes.py` و`paths.py` والملفات "
         "وعناوينها ومعرّفات الأمثلة)، ويُحكم عليها. ولا تعدّل الأداة شيئًا في الكتاب؛ والتصحيحات المقترحة نصًّا بنصّ أدناه.", "",
         f"**{len(refs)} إحالة: {sum(1 for r in refs if r.verdict == 'سليمة')} سليمة، {len(read_ok)} مقروءة، "
         f"{len(reads)} للقارئ، {len(fails)} مخفقة.**", "",
         "| النوع | " + " | ".join(verdicts) + " |", "|---|" + "---|" * len(verdicts)]
    L += [f"| {k} | " + " | ".join(str(by.get((k, v), 0) or "") for v in verdicts) + " |" for k in kinds]
    L += ["", "**الأحكام:** سليمة: الموضع موجود والصيغة صيغة السلسلة. مقروءة: حكم عليها قارئ (القراءة مذكورة). "
          "للقارئ: لا يقطع فيها النمط. مخفقة: الموضع غير موجود، أو الصيغة تخالف قاعدة: موضعٌ في مجلدٍ آخر بلا مجلده، "
          "أو خلطٌ بين الأرقام الأربعة، أو رقم صفحة، أو أثرٌ للبنية القديمة، أو لغة الملفات في النص المطبوع، أو «سبق» إلى ما بعده.", ""]
    prop = {(f, n): (cur, new) for f, n, cur, new in PROPOSALS}
    L += ["## الإخفاقات والتصحيح المقترح", ""]
    shown = set()
    if not fails:
        L.append("لا شيء.")
    for r in sorted(fails, key=lambda r: (S_ORDER.get(r.f, 0), r.line)):
        rel = str(r.f.relative_to(BOOK))
        L.append(f"- `{rel}:{r.line}` [{r.kind}] «{md_escape(r.text)}»" + (f" ← {md_escape(r.target)}" if r.target else "") + f": {r.note}")
        if (rel, r.line) in prop and (rel, r.line) not in shown:
            shown.add((rel, r.line))
            cur, new = prop[(rel, r.line)]
            L.append(f"  - **الآن:** «{md_escape(cur)}»")
            L.append(f"  - **يُقترح:** «{md_escape(new)}»")
            note = NOTES.get((r.f.name, r.line))
            if note:
                L.append(f"  - {note}")
    bare = sorted({(str(r.f.relative_to(BOOK)), r.line) for r in fails} - set(prop))
    if bare:
        L += ["", "**إخفاقاتٌ لم يُكتب لها تصحيح بعد:** " + "، ".join(f"`{f}:{n}`" for f, n in bare)]
    if stale:
        L += ["", "**اقتراحاتٌ لم يعد نصّها في موضعه (تُراجَع):** " + "، ".join(f"`{s}`" for s in stale)]
    L += ["", "## مواضع للقارئ", ""]
    L += [f"- `{r.f.relative_to(BOOK)}:{r.line}` [{r.kind}] «{md_escape(r.text)}» ← {md_escape(r.target)}: {r.note}" for r in reads] or ["لا شيء."]
    L += ["", "## القراءات", ""]
    grouped = defaultdict(list)
    for r in read_ok:
        grouped[r.note].append(f"`{r.f.relative_to(BOOK)}:{r.line}`")
    L += [f"- {note}: " + "، ".join(where) for note, where in grouped.items()] or ["لا شيء."]
    L += ["", "## السجل", "",
          "كل إحالةٍ في موضعها، مجلدًا مجلدًا: النوع، والنص، والوجهة، والحكم. وأسطر الحوار («س٧») مجموعةٌ في كل ملفٍّ "
          "بوجهة كلٍّ منها (الحوار المسطّر الذي تشير إليه)."]
    by_vol = defaultdict(list)
    for r in refs:
        by_vol[S_UNIT[r.f][0]].append(r)
    for v in sorted(by_vol):
        L += ["", f"### المجلد {VOLW[v - 1]}: {VOLUMES[v - 1]['name']}", "", "| الموضع | النوع | الإحالة | الوجهة | الحكم |", "|---|---|---|---|---|"]
        rows = sorted(by_vol[v], key=lambda r: (S_ORDER.get(r.f, 0), r.line, r.start))
        lines_by_file = defaultdict(list)
        for r in rows:
            if r.kind == "سطر الحوار" and r.verdict == "سليمة":
                lines_by_file[r.f].append(r)
                continue
            L.append(f"| `{r.f.relative_to(BOOK)}:{r.line}` | {r.kind} | {md_escape(r.text)[:90]} | {md_escape(r.target)[:110]} | {r.verdict} |")
        for f, rs in lines_by_file.items():
            scenes = defaultdict(list)
            for r in rs:
                scenes[r.target].append(f"{ar(r.line)}:{r.text}")
            for target, items in scenes.items():
                L.append(f"| `{f.relative_to(BOOK)}` | سطر الحوار | {len(items)}: " + "، ".join(items)[:400] + f" | {md_escape(target)} | سليمة |")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")


S_ORDER, S_UNIT = {}, {}


def main(argv):
    S = Series()
    S_ORDER.update(S.order)
    S_UNIT.update(S.unit_of)
    NAMES.update({v: k for k, v in S.bab_name.items()})
    NAMES.update({"المنبر": 9, "الإعلام": 11, "الدبلوماسية": 12})
    refs = scan(S)
    stale = review(refs)
    write_report(refs, stale)
    c = Counter(r.verdict for r in refs)
    kinds = Counter((r.kind, r.verdict) for r in refs)
    print(f"{len(refs)} references: " + ", ".join(f"{v} {c.get(v, 0)}" for v in ("سليمة", "مقروءة", "للقارئ", "مخفقة")))
    if "--quiet" not in argv:
        for (k, v), n in sorted(kinds.items()):
            print(f"  {k} · {v}: {n}")
        for r in refs:
            if r.verdict in ("مخفقة", "للقارئ"):
                print(f"{r.verdict} {r.where} «{r.text}» → {r.target} — {r.note}")
    if stale:
        print("stale proposals:", ", ".join(stale))
    print(f"report: {OUT.relative_to(BOOK.parent)}")
    if "--strict" in argv and (c.get("مخفقة") or c.get("للقارئ")):
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
