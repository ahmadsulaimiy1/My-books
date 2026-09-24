#!/usr/bin/env python3
"""The Qur'an in the manuscript, set in the Uthmani script of the Madinah mushaf (Bible, part nine, ch. 42 §1).

Every ﴿…﴾ with its reference (سورة: آية[–آية]) is read from the manuscript. The cited verses are fetched in the
Uthmani Hafs text from two independent services (quran.com and alquran.cloud); both must agree. Our words are
then aligned with the Uthmani text on the consonantal skeleton (so that spelling conventions such as «يا أيها»
against «يَـٰٓأَيُّهَا» do not break the match), the reference is checked, and our wording is replaced by the exact
Uthmani words, with a numbered verse-end mark (۝ and the number) between the verses of a multi-verse citation.
Anything that does not align exactly is reported and left untouched.

    python3 quran.py            report only
    python3 quran.py --apply    rewrite the manuscript files
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
CACHE = HERE.parent / ".cache" / "quran"
CACHE.mkdir(parents=True, exist_ok=True)
OUT = BOOK / "_production" / "التحقيق"
FILES = sorted((BOOK / "الافتتاحية").glob("*.md")) + [BOOK / "00-كلمة-المؤلف.md", BOOK / "الخواتيم" / "00-خاتمة-الكتاب.md"]
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
CITE = re.compile(r"﴿([^﴾]+)﴾\s*\(([^:()]+):\s*([٠-٩]+)(?:\s*[–-]\s*([٠-٩]+))?\)")


def get(url: str):
    f = CACHE / re.sub(r"[^A-Za-z0-9]+", "_", url)
    if not f.exists():
        out = subprocess.run(["curl", "-s", "--max-time", "60", url], capture_output=True, text=True).stdout
        f.write_text(out, encoding="utf-8")
    return json.loads(f.read_text(encoding="utf-8"))


def skeleton(s: str) -> str:
    """Letters only: no vowels, Qur'anic marks, verse marks, digits, alefs, hamzas or spaces; ya/ta forms unified."""
    s = re.sub(r"[ؐ-ًؚ-ٰٟۖ-ࣰۭ-ࣿـ]", "", s)
    s = re.sub(r"[٠-٩0-9\s۝]", "", s)
    s = re.sub("[ٱأإآاءئؤ]", "", s).replace("ى", "ي").replace("ة", "ه")
    return s


def name_key(s: str) -> str:
    """Sura names: vowels removed and alef forms unified, nothing more (النساء and الناس must stay apart)."""
    s = re.sub(r"[\u064B-\u065F\u0670\u0640]", "", s)
    return re.sub("[إأآٱ]", "ا", s).strip()


def chapters() -> dict:
    d = get("https://api.quran.com/api/v4/chapters?language=ar")["chapters"]
    return {name_key(c["name_arabic"]): c["id"] for c in d}


def verses(n: int) -> dict:
    # a tatweel before the dagger alif is a convention of the digital text, not of the mushaf; where the
    # tatweel carries a hamza (مَسْـُٔولًا) it is the mushaf's own and stays
    a = {int(v["verse_key"].split(":")[1]): v["text_uthmani"].strip().replace("\u0640\u0670", "\u0670")
         for v in get(f"https://api.quran.com/api/v4/quran/verses/uthmani?chapter_number={n}")["verses"]}
    b = {x["numberInSurah"]: x["text"] for x in get(f"https://api.alquran.cloud/v1/surah/{n}/quran-uthmani")["data"]["ayahs"]}
    if n not in (1, 9) and 1 in b:  # this service prefixes the basmala to the first verse of a sura
        w = b[1].replace("\ufeff", "").split()
        if skeleton(" ".join(w[:4])) == skeleton("بسم الله الرحمن الرحيم"):
            b[1] = " ".join(w[4:])
    return {k: (a[k], b.get(k, "")) for k in a}


def rebuild(ours: str, sura: int, v1: int, v2: int, vv: dict) -> tuple[str | None, str]:
    """Our citation re-set in the Uthmani words it corresponds to, or None with the reason."""
    words = []  # (verse, word)
    for v in range(v1, v2 + 1):
        qc, ac = vv[v]
        if ac and skeleton(qc) != skeleton(ac):
            return None, f"المصدران يختلفان في الآية {v}"
        # the first verse of a sura in the alquran.cloud text may carry the basmala; quran.com's does not
        words += [(v, w) for w in qc.split()]
    sk = "".join(skeleton(w) for _, w in words)
    starts, pos = [], 0
    for _, w in words:
        starts.append(pos)
        pos += len(skeleton(w))
    q = skeleton(ours)
    at = sk.find(q)
    if at < 0:
        return None, "لم تنطبق الألفاظ على نص الآيات المحال إليها"
    end = at + len(q)
    try:
        i = starts.index(at)
    except ValueError:
        return None, "الاقتباس يبدأ في وسط كلمة"
    j = i
    while j < len(words) and starts[j] + len(skeleton(words[j][1])) <= end:
        j += 1
    while j < len(words) and not skeleton(words[j][1]) and starts[j] < end:
        j += 1  # a pause mark inside the span
    span = words[i:j]
    while span and not skeleton(span[-1][1]):
        span = span[:-1]  # no pause mark at the end of a quotation
    while span and span[0][1] == "۞":
        span = span[1:]  # the hizb sign is a division of the mushaf, not part of the verse
    if "".join(skeleton(w) for _, w in span) != q:
        return None, "حدود الاقتباس لا تنطبق على حدود الكلمات"
    out = []
    for k, (v, w) in enumerate(span):
        if not skeleton(w) and re.fullmatch(r"[\u06D6-\u06DC]+", w) and out:
            out[-1] += w  # a pause sign sits on the end of its word, as in the mushaf
            continue
        out.append(w)
        last_of_verse = k + 1 == len(span) or span[k + 1][0] != v
        verse_complete = last_of_verse and (words.index((v, w)) + 1 == len(words) or words[words.index((v, w)) + 1][0] != v
                                            or all(not skeleton(x) for vx, x in words[words.index((v, w)) + 1:] if vx == v))
        if last_of_verse and k + 1 < len(span) and verse_complete:
            out.append("۝" + str(v).translate(AR))
    return " ".join(out), ""


def main(apply: bool):
    names = chapters()
    report, changed = [], {}
    for f in FILES:
        text = f.read_text(encoding="utf-8")
        new = text
        for m in CITE.finditer(text):
            ours, sname, a, b = m.group(1), m.group(2).strip(), m.group(3), m.group(4)
            v1 = int(a.translate(EN)); v2 = int((b or a).translate(EN))
            n = names.get(name_key(sname))
            row = {"file": f.name, "ref": f"{sname}: {a}" + (f"–{b}" if b else ""), "ours": ours}
            if not n:
                row["result"] = "اسم السورة غير معروف"; report.append(row); continue
            vv = verses(n)
            uth, why = rebuild(ours, n, v1, v2, vv)
            if uth is None:
                row["result"] = why
            else:
                row["result"] = "مطابق" if skeleton(uth) == skeleton(ours) else "مطابق بعد المحاذاة"
                row["uthmani"] = uth
                new = new.replace("﴿" + ours + "﴾", "﴿" + uth + "﴾", 1)
            report.append(row)
        if new != text:
            changed[f] = new
    for r in report:
        print(r["result"], "|", r["file"], "|", r["ref"], "|", r.get("uthmani", r["ours"])[:90])
    (OUT / "مطابقة-القرآن.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    if apply:
        for f, t in changed.items():
            f.write_text(t, encoding="utf-8")
        print("rewrote", len(changed), "files")


if __name__ == "__main__":
    main("--apply" in sys.argv)
