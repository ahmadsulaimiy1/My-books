#!/usr/bin/env python3
"""The indexes of a volume (Bible, ch. 111 §4): the verses, the hadith and athar, the poetry, the people, the terms, and the
sources cited, each with the pages where it stands.

An entry is marked where the page is made: its words are wrapped in a link to https://idx.invalid/<kind>/<key>. The link
changes nothing on the page (it takes the colour and the line of the text round it), and Chromium keeps its rectangle on
every page the words reach. When the volume is laid out, the pages of every entry are read from those links, the index
pages are set after the last page of the text and before the colophon, and the links are taken out of the file.

What is marked, and where the entry's wording comes from:
- the verses: every ayah that carries its reference, «﴿…﴾ (السورة: الآية)», keyed by the reference; the index follows the
  order of the mushaf;
- the hadith, the athar and the poetry: the quotations of the verification ledger (verify.py ITEMS, ledger.py ROWS), found
  in their file by the words the ledger finds them by; the index gives the opening words (الطرف), in the order of the
  letters, and the poetry by its rhyme;
- the people: the names of «سجل-الأعلام.tsv» (the people the book cites or tells of: scholars, Companions, poets,
  modern authors; never a character of the book's scenes), in the order of the letters, the article set aside;
- the terms: a term of the glossary where the book sets it in bold, that is, where it defines or explains it;
- the sources: in the notes, the title of every source of the volume's thabat.
"""
from __future__ import annotations

import csv
import re
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parent / "book"
OUT = BOOK / "_production" / "التحقيق"
PREFIX = "https://idx.invalid/"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
KINDS = [("q", "فهرس الآيات"), ("h", "فهرس الأحاديث والآثار"), ("s", "فهرس الأشعار"), ("n", "فهرس الأعلام"),
         ("t", "فهرس المصطلحات"), ("m", "فهرس المصادر")]
TITLE = dict(KINDS)
CSS = "a.ix { color: inherit; text-decoration: none; }"

# what the pages being made have marked: (kind, key) -> the entry as the index prints it
SEEN: dict[tuple[str, str], dict] = {}
# set by use_volume(): marking is on only while a volume is being built
ACTIVE = False
QUOTES: list = []          # [(kind, key, words that find it, entry)]
NAMES: list = []
GLOSSARY: dict = {}
TITLES: dict = {}          # the words of a cited title -> the thabat's entry


def reset():
    global ACTIVE
    SEEN.clear()
    ACTIVE = False


def use_volume(n: int):
    """Loads what the indexes of volume n are made of, and turns the marking on."""
    global ACTIVE, QUOTES, NAMES, GLOSSARY, TITLES
    import ledger as L
    import thabat as T
    import verify as V
    words = {iid: key for iid, _prefix, key, *_ in V.ITEMS}
    QUOTES = []
    for row in L.ROWS:
        vid, _loc, kind, text, _form, who = row[:6]
        k = "h" if kind.startswith(("حديث", "أثر")) else "s" if kind.startswith("شعر") and "موضع" not in kind else None
        if not vid or not k:
            continue
        find = words.get(vid) or re.split(r"[…/]", text)[0].strip()
        shown = re.split(r"\s*/\s*", text)[0].strip() if k == "s" else text
        QUOTES.append((k, vid, find, {"text": shown.strip("«» "), "who": who}))
    NAMES = people()
    GLOSSARY = terms()
    TITLES = {}
    for r in T.cited(n):
        author, title = r["المؤلف"].strip(), r["العنوان"].strip()
        short = T.short(title)
        for w in {title, short}:
            if len(w) >= 4:
                TITLES[w] = f"{author}، {short}" if author else short
    SEEN.clear()
    ACTIVE = True


def link(kind: str, key: str, inner: str, **entry) -> str:
    """The words `inner` (HTML) marked as an entry of the index `kind`."""
    SEEN.setdefault((kind, key), {"kind": kind, "key": key, **entry})
    return f'<a class="ix" href="{PREFIX}{kind}/{urllib.parse.quote(key, safe="")}">{inner}</a>'


# ------------------------------------------------------------------------------------------------------------- reading

DIAC = re.compile(r"[ً-ٰٟـۡ]")


FOLD = str.maketrans({"إ": "ا", "أ": "ا", "آ": "ا", "ٱ": "ا", "ى": "ي", "ة": "ه"})


def plain(s: str) -> str:
    return plain_map(s)[0].strip()


def plain_map(s: str) -> tuple[str, list[int]]:
    """`s` without its vowels, its alef forms folded and its spaces single, with, for every character kept, its place
    in `s`, so that a match in the plain text can be found again in the original."""
    out, where, space = [], [], False
    for i, ch in enumerate(s):
        if DIAC.match(ch):
            continue
        if ch.isspace():
            if space:
                continue
            space, ch = True, " "
        else:
            space = False
        out.append(ch.translate(FOLD))
        where.append(i)
    return "".join(out), where


def sort_key(s: str) -> str:
    """The order of the letters, the vowels and the article set aside (العلم under ع), and ابن/أبو read as written."""
    s = plain(re.sub(r"[«»﴿﴾\"'()\[\]…:،.؟!]", "", s))
    s = re.sub(r"^(ال)(?=\S{2,})", "", s)
    return s


# -------------------------------------------------------------------------------------------------------------- people

def people() -> list[dict]:
    """The names to index: «سجل-الأعلام.tsv» (الاسم، الصيغ، الصفة). A form is a regular expression; the first form that
    matches at a place is the one marked."""
    f = OUT / "سجل-الأعلام.tsv"
    if not f.exists():
        return []
    rows = []
    with open(f, encoding="utf-8") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            forms = [x.strip() for x in r["الصيغ"].split("|") if x.strip()]
            if forms:
                rows.append({"name": r["الاسم"].strip(), "forms": forms, "what": r.get("الصفة", "").strip()})
    return rows


def terms() -> dict[str, str]:
    """The glossary's terms: their plain form (as a bold word is matched) -> the approved spelling (as the index prints it)."""
    f = OUT / "سجل-المصطلحات.tsv"
    if not f.exists():
        return {}
    with open(f, encoding="utf-8") as fh:
        return {plain(t): t for t in (r["الرسم المعتمد"] or r["المصطلح"] for r in csv.DictReader(fh, delimiter="\t")) if t}


# ------------------------------------------------------------------------------------------------------------- marking

def ayah(html: str, ref: str, words: str = "") -> str:
    """A verse with its reference, marked (called by opening.ayat); `words` is the verse itself, for the index."""
    return link("q", ref.strip(), html, ref=ref.strip(), text=words or re.sub(r"<[^>]+>", "", html))


def listing(md: str) -> bool:
    """A closing list (the thabat, the bibliography, the glossary) is not a place the indexes point to."""
    return bool(re.search(r"^#{1,3}\s+(?:ثبت المصادر|المصادر والمراجع|المسرد)", md, re.M))


def mark(soup, quotes=(), names=None, glossary=None):
    """Marks, in a page's HTML (a BeautifulSoup), the quotations `quotes` [(kind, key, phrase, entry)], the people and the
    bold terms. The Qur'an (span.q), the example codes and the titles of the page are left alone."""
    from bs4 import BeautifulSoup, NavigableString
    names = people() if names is None else names
    glossary = terms() if glossary is None else glossary

    def text_nodes():
        for t in list(soup.find_all(string=True)):
            if isinstance(t, NavigableString) and t.parent is not None and t.parent.name not in ("style", "script") \
                    and not t.find_parent("a") and not t.find_parent(class_=("q", "qref", "exid")) \
                    and not t.find_parent(["h1", "h2"]):
                yield t

    # the quotations of the ledger: the first place in the page where their words stand
    for kind, key, phrase, entry in quotes:
        p = plain(phrase)
        if not p:
            continue
        for t in text_nodes():
            s = str(t)
            ps, where = plain_map(s)
            k = ps.find(p)
            if k < 0:
                continue
            a, b = where[k], where[k + len(p) - 1] + 1
            html = escape(s[:a]) + link(kind, key, escape(s[a:b]), **entry) + escape(s[b:])
            t.replace_with(BeautifulSoup(html, "html.parser"))
            break
    # the people
    if names:
        pat = re.compile("|".join(f"(?P<g{k}>{'|'.join(r['forms'])})" for k, r in enumerate(names)))
        for t in text_nodes():
            s = str(t)
            if not pat.search(s):
                continue
            out, last = "", 0
            for m in pat.finditer(s):
                k = int(next(g for g, v in m.groupdict().items() if v is not None)[1:])
                r = names[k]
                out += escape(s[last:m.start()]) + link("n", r["name"], escape(m.group(0)), name=r["name"], what=r["what"])
                last = m.end()
            t.replace_with(BeautifulSoup(out + escape(s[last:]), "html.parser"))
    # the terms, where the book sets them in bold
    if glossary:
        for b in soup.find_all(["strong", "b"]):
            w = plain(b.get_text())
            if w in glossary and not b.find_parent("a") and not b.find("a"):
                inner = b.decode_contents()
                b.clear()
                b.append(BeautifulSoup(link("t", w, inner, term=glossary[w]), "html.parser"))
    return soup


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def mark_sources(note_html: str, titles: dict[str, str]) -> str:
    """In a note: the first title of a source of the thabat, marked (titles: the words to find -> the thabat's entry).
    The longest titles are tried first, so that «الإيضاح في علوم البلاغة» is not taken for «الإيضاح»."""
    for words in sorted(titles, key=len, reverse=True):
        k = note_html.find(words)
        if words and k >= 0 and PREFIX not in note_html[max(0, k - 200):k + len(words)]:
            entry = titles[words]
            note_html = note_html[:k] + link("m", entry, words, source=entry) + note_html[k + len(words):]
    return note_html


# ---------------------------------------------------------------------------------------------------------- collecting

def collect(pages) -> dict[tuple[str, str], list[int]]:
    """The pages (their places in `pages`, pypdf page objects) of every marked entry."""
    hits: dict[tuple[str, str], list[int]] = {}
    for i, pg in enumerate(pages):
        for a in pg.get("/Annots") or []:
            a = a.get_object()
            uri = (a.get("/A") or {}).get("/URI", "")
            if isinstance(uri, str) and uri.startswith(PREFIX):
                kind, _, key = uri[len(PREFIX):].partition("/")
                seen = hits.setdefault((kind, urllib.parse.unquote(key)), [])
                if i not in seen:
                    seen.append(i)
    return hits


def strip(pdf: Path):
    """Takes the index links out of the file (they served only to find the pages)."""
    import pymupdf
    doc = pymupdf.open(str(pdf))
    n = 0
    for page in doc:
        for l in page.get_links():
            if (l.get("uri") or "").startswith(PREFIX):
                page.delete_link(l)
                n += 1
    tmp = pdf.with_suffix(".ix.pdf")
    doc.save(str(tmp), garbage=4, deflate=True, deflate_fonts=True)
    doc.close()
    tmp.replace(pdf)
    return n


# ----------------------------------------------------------------------------------------------------------- the pages

def pages_text(ixs: list[int], label) -> str:
    """«١٢، ١٤–١٦»: the pages, runs of consecutive pages joined."""
    ixs = sorted(set(ixs))
    runs, start, prev = [], None, None
    for i in ixs:
        if start is None:
            start = prev = i
        elif i == prev + 1:
            prev = i
        else:
            runs.append((start, prev))
            start = prev = i
    if start is not None:
        runs.append((start, prev))
    return "، ".join(label(a) if a == b else f"{label(a)}–{label(b)}" for a, b in runs)


def verse_order():
    try:
        from quran import chapters, name_key
        names = chapters()
    except Exception:  # without the sura table the verses keep the order of the book
        return lambda ref: (0, 0)

    def key(ref):
        sura, _, v = ref.partition(":")
        first = re.split(r"[–-]", v.strip())[0].translate(EN)
        return names.get(name_key(sura.strip()), 999), int(first) if first.isdigit() else 0
    return key


def rhyme(line: str) -> str:
    """The rhyme letter of a verse: the last letter of its last hemistich that is not a vowel of length or a ha of silence."""
    last = plain(line.split("...")[-1]).rstrip(" .،»")
    letters = re.sub(r"[^ء-ي]", "", last)
    for ch in reversed(letters):
        if ch not in "اوي":
            return ch
    return letters[-1:] or ""


def latin(s: str) -> bool:
    return bool(re.match(r"[A-Za-z]", s.strip()))


def show(s: str) -> str:
    """An entry's words as the page sets them: a Latin title isolated left to right."""
    return f'<span class="lat">{escape(s)}</span>' if latin(s) else escape(s)


def html(hits: dict, label) -> list[tuple[str, str, str]]:
    """The index pieces [(anchor, title, html)], one per kind that has entries, in the order of the Bible."""
    out = []
    order_q = None
    for kind, title in KINDS:
        entries = [(SEEN.get((kind, key), {"key": key}), ixs) for (k, key), ixs in hits.items() if k == kind]
        if not entries:
            continue
        text = {"q": lambda e: e.get("text", ""), "h": lambda e: e.get("text", e["key"]), "s": lambda e: e.get("text", e["key"]),
                "n": lambda e: e.get("name", e["key"]), "t": lambda e: e.get("term", e["key"]), "m": lambda e: e.get("source", e["key"])}[kind]
        # one entry for one text: the same hadith kept by two rows of the ledger is one line of the index
        if kind in "hsnmt":
            merged = {}
            for e, ixs in entries:
                k = plain(re.sub(r"[«»…]", "", text(e)))
                if k in merged:
                    merged[k][1].extend(ixs)
                    if not merged[k][0].get("who") and e.get("who"):
                        merged[k][0]["who"] = e["who"]
                else:
                    merged[k] = (dict(e), list(ixs))
            entries = list(merged.values())
        rows = []
        if kind == "q":
            order_q = order_q or verse_order()
            entries.sort(key=lambda e: order_q(e[0]["key"]))
            for e, ixs in entries:
                words = e.get("text", "").strip("﴿﴾ ").split()
                short = " ".join(words[:5]) + ("…" if len(words) > 5 else "")
                rows.append(f'<li><span class="ix-r">{e["key"]}</span> <span class="ix-q">﴿{short}﴾</span>'
                            f' <span class="ix-p">{pages_text(ixs, label)}</span></li>')
        else:
            if kind == "s":
                entries.sort(key=lambda e: (sort_key(rhyme(text(e[0]))), sort_key(text(e[0]))))
            else:
                entries.sort(key=lambda e: (latin(text(e[0])), sort_key(text(e[0])).lower()))
            for e, ixs in entries:
                who = f' <span class="ix-w">{escape(e["who"])}</span>' if kind in "hs" and e.get("who") else ""
                rows.append(f'<li><span class="ix-e">{show(text(e))}</span>{who} <span class="ix-p">{pages_text(ixs, label)}</span></li>')
        body = f'<section class="ix"><h2 class="ix-t">{title}</h2><ul class="ix-l ix-{kind}">{"".join(rows)}</ul></section>'
        out.append((f"ix-{kind}", title, body))
    return out


PAGE_CSS = """
section.ix { padding-top: 2mm; }
h2.ix-t { font: 700 17pt/1.3 "Changa"; color: var(--sapphire); margin: 0 0 5mm; }
ul.ix-l { list-style: none; margin: 0; padding: 0; columns: 2; column-gap: 8mm; column-rule: .4pt solid #D8D0C0; }
ul.ix-l li { break-inside: avoid; font: 400 10.6pt/1.55 "Scheherazade New"; color: var(--ink); text-align: right;
  padding: .5mm 4.5mm .5mm 0; text-indent: -4.5mm; border-bottom: .3pt dotted #D8D0C0; }
ul.ix-l li .ix-q { font: 400 10.4pt/1.6 "Amiri Quran"; color: #8A1C2B; }
ul.ix-l li .ix-r, ul.ix-l li .ix-w { font: 300 8.2pt/1.4 "Changa"; color: var(--gold-ink); }
ul.ix-l li .ix-p { font: 400 10.4pt/1.4 "Amiri"; color: var(--sapphire); }
ul.ix-l li .lat { font-family: "Source Serif 4"; font-size: 9.4pt; direction: ltr; unicode-bidi: isolate; }
"""
