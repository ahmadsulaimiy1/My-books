#!/usr/bin/env python3
"""Where each hadith and athar of the opening sits in the adopted editions (Bible, part nine, ch. 42 §2 and ch. 43).

For every item, every place in an edition where the quoted words occur is listed with the hadith number of
that edition, the book (كتاب) and chapter (باب) as the edition heads them, the volume and printed page where
the hadith begins, and the edition's own words around the quotation. The takhrij in the manuscript is written
from this list, never from memory.

    python3 hadith.py      writes book/_production/التحقيق/مواضع-الأحاديث.json and .md
"""
from __future__ import annotations

import html
import json
import re

import shamela as S
from verify import ITEMS, OUT, best_window, quote_from_manuscript

EDITIONS = {
    "1681": "صحيح البخاري، ط. السلطانية (ترقيم عبد الباقي = طوق النجاة)",
    "1284": "صحيح البخاري، ط. دار التأصيل",
    "1727": "صحيح مسلم، ت. محمد فؤاد عبد الباقي",
    "711": "صحيح مسلم، الطبعة التركية",
    "1726": "سنن أبي داود، ت. محمد محيي الدين عبد الحميد",
    "117359": "سنن أبي داود، ت. شعيب الأرنؤوط ومحمد كامل قره بللي",
}
# how each edition writes the number that opens a hadith
NUMBER = {
    "1681": re.compile(r"(?<![٠-٩(\[⦗])([٠-٩]{1,4})\s*-\s+(?=[^\s٠-٩(])"),
    "1726": re.compile(r"(?<![٠-٩(\[⦗])([٠-٩]{1,4})\s*-\s+(?=[^\s٠-٩(])"),
    "117359": re.compile(r"(?<![٠-٩(\[⦗])([٠-٩]{1,4})\s*-\s+(?=[^\s٠-٩(])"),
    "1727": re.compile(r"[٠-٩]{1,4}\s*-\s*\(([٠-٩]{1,4})\)"),
    "711": re.compile(r"[٠-٩]{1,4}\s*-\s*\(([٠-٩]{1,4})\)"),
    "1284": re.compile(r"\[([٠-٩]{1,4})\]"),
}
MARK = re.compile(r"⦗([٠-٩]+)⦘")
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
_toc = {}


def toc(book: str, pid: int) -> list[tuple[int, int, str]]:
    """(depth, page id, title) of the edition's table of contents as Shamela shows it beside a page."""
    t = S._get(f"{S.BASE}/book/{book}/{pid}")
    blk = t[t.find('class="s-nav"'):]
    depth, out = 0, []
    for m in re.finditer(r'<ul>|</ul>|<a href="https://shamela\.ws/book/%s/(\d+)[^"]*">([^<]+)</a>' % book, blk):
        s = m.group(0)
        if s == "<ul>":
            depth += 1
        elif s == "</ul>":
            depth -= 1
            if depth <= 0:
                break
        else:
            out.append((depth, int(m.group(1)), html.unescape(m.group(2)).strip()))
    return out


def heads(book: str, pid: int) -> tuple[str, str]:
    """The book (top level) and chapter (deepest level) that contain a page."""
    t = toc(book, pid)
    top = [x for x in t if x[0] == 1 and x[1] <= pid]
    sub = [x for x in t if x[0] > 1 and x[1] <= pid]
    kitab = top[-1][2] if top else ""
    bab = sub[-1][2] if sub and (not top or sub[-1][1] >= top[-1][1]) else ""
    return kitab, bab


def segments(book: str, pid: int) -> list[tuple[str, int, str]]:
    """The page cut at every hadith number: (number, position of the number, text of the hadith on this page)."""
    pg = S.page(book, str(pid))
    t = pg["text"]
    cuts = [(m.group(1), m.start()) for m in NUMBER[book].finditer(t)]
    out = []
    if not cuts or cuts[0][1] > 0:
        out.append(("", 0, t[: cuts[0][1] if cuts else len(t)]))
    for k, (n, at) in enumerate(cuts):
        end = cuts[k + 1][1] if k + 1 < len(cuts) else len(t)
        out.append((n, at, t[at:end]))
    return out


def start_of(book: str, pid: int) -> tuple[str, int, str, str]:
    """For text that opens a page before any number: the number, page id, part and printed page where it began."""
    for back in range(1, 6):
        p = pid - back
        segs = [s for s in segments(book, p) if s[0]]
        if segs:
            n, at, _ = segs[-1]
            pg = S.page(book, str(p))
            marks = [m.group(1) for m in MARK.finditer(pg["text"][:at])]
            return n, p, pg["part"], (marks[-1] if marks else pg["printed_page"])
    return "", pid, "", ""


def places(book: str, phrase: str, quote: str) -> list[dict]:
    seen, out = set(), []
    key = S.plain(phrase)
    for h in S.search(f'"{phrase}"', [book]):
        for pid in (int(h["page"]), int(h["page"]) + 1):
            pg = S.page(book, str(pid))
            for n, at, seg in segments(book, pid):
                if key not in S.plain(seg):
                    continue
                if n:
                    marks = [m.group(1) for m in MARK.finditer(pg["text"][:at])]
                    p0, part, page = pid, pg["part"], (marks[-1] if marks else pg["printed_page"])
                else:
                    n, p0, part, page = start_of(book, pid)
                if not n or (n, p0) in seen:
                    continue
                seen.add((n, p0))
                kitab, bab = heads(book, p0)
                ratio, span, diffs = best_window(seg, quote)
                out.append({"book": book, "edition": EDITIONS[book], "number": n, "n": int(n.translate(EN)),
                            "part": part, "page": page, "kitab": kitab, "bab": bab, "ratio": round(ratio, 3),
                            "span": span, "diffs": diffs, "url": f"{S.BASE}/book/{book}/{p0}"})
            if any(key in S.plain(s[2]) for s in segments(book, pid)):
                break
    return sorted(out, key=lambda x: x["n"])


def main():
    results = []
    for iid, prefix, mkey, phrase, books, kind in ITEMS:
        if not iid.startswith("ح"):
            continue
        quote = quote_from_manuscript(prefix, mkey)
        rec = {"id": iid, "kind": kind, "quote": quote, "places": []}
        for b in books + (["1284"] if "1681" in books and "1284" not in books else []):
            rec["places"] += places(b, phrase, quote)
        results.append(rec)
        print(iid, "|", quote[:50])
        for p in rec["places"]:
            print(f"   {p['book']:>6} {p['number']:>6}  ج{p['part']} ص{p['page']}  {p['kitab']} / {p['bab'][:60]}  r={p['ratio']}")
    (OUT / "مواضع-الأحاديث.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    md = ["# مواضع الأحاديث والآثار في الطبعات المعتمدة: افتتاحية المجلد الأول", "",
          "كل موضعٍ وقعت فيه ألفاظ النص في الطبعة، برقم الحديث فيها وكتابه وبابه كما تعنونه الطبعة، والجزء والصفحة "
          "التي يبدأ فيها الحديث. يُولَّد من `pdf/hadith.py`، وتُكتب حواشي التخريج منه لا من الذاكرة.", ""]
    for rec in results:
        md += [f"## {rec['id']} — {rec['kind']}", f"**نصّنا:** «{rec['quote']}»", "",
               "| الطبعة | الرقم | الجزء/الصفحة | الكتاب | الباب | التطابق |", "|---|---|---|---|---|---|"]
        for p in rec["places"]:
            md.append(f"| {p['edition']} | [{p['number']}]({p['url']}) | {p['part']}/{p['page']} | {p['kitab']} | {p['bab']} | "
                      f"{round(p['ratio'] * 100)}٪ |")
        md.append("")
    (OUT / "مواضع-الأحاديث.md").write_text("\n".join(md) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
