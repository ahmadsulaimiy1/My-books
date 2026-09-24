#!/usr/bin/env python3
"""A small client for the public pages of al-Maktaba al-Shamila (shamela.ws), used to find and match citations.

Shamela is a means of finding and comparing (Bible, part nine, ch. 48): a page on Shamela gives the
printed edition's volume and page when the book is marked as matching the print, and the final check is
still made on the adopted edition itself. Every request is cached on disk, so a run can be repeated
without asking the site again, and requests are spaced out.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import time
from pathlib import Path

BASE = "https://shamela.ws"
CACHE = Path(__file__).resolve().parent.parent / ".cache" / "shamela"
CACHE.mkdir(parents=True, exist_ok=True)
DIAC = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")


def _get(url: str, data: dict | None = None) -> str:
    key = hashlib.sha1((url + json.dumps(data, sort_keys=True, ensure_ascii=False)).encode()).hexdigest()
    f = CACHE / key
    if f.exists():
        return f.read_text(encoding="utf-8")
    cmd = ["curl", "-s", "--max-time", "60", url]
    if data is not None:
        cmd[1:1] = ["-X", "POST"]
        for k, v in data.items():
            for item in (v if isinstance(v, list) else [v]):
                cmd += ["--data-urlencode", f"{k}={item}"]
    for attempt in range(4):
        out = subprocess.run(cmd, capture_output=True, text=True).stdout
        if out.strip():
            break
        time.sleep(2 ** (attempt + 1))
    time.sleep(0.6)
    f.write_text(out, encoding="utf-8")
    return out


def plain(s: str) -> str:
    """Arabic without vowels, marks, tatweel; alef forms and ya/alef-maqsura unified; spaces normalised."""
    s = DIAC.sub("", html.unescape(s))
    s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    s = re.sub(r"[^ء-ي\s]", " ", s)
    # the salutation is written out in some editions and as a ligature (ﷺ) in others: neither counts in a comparison
    s = re.sub(r"صلي\s+الله\s+عليه\s+وسلم", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def search(term: str, books: list[str] | None = None) -> list[dict]:
    """Full-library (or per-book) search. Returns [{book, page, title, author, snippet}] in the site's order."""
    data = {"term": term}
    if books:
        data["books[]"] = books
    t = _get(f"{BASE}/ajax/search", data)
    out = []
    pat = re.compile(r'<a target="_blank" href="https://shamela\.ws/book/(\d+)/(\d+)[^"]*"><b><span class="text-primaryy">(.*?)</span></b>'
                     r'\s*<span class="text-gray">\[(.*?)\]</span></a></div><p class="srch-snippet">(.*?)(?:<button|</p>)', re.S)
    for m in pat.finditer(t):
        snip = html.unescape(re.sub(r"<[^>]+>", "", m.group(5)))
        out.append({"book": m.group(1), "page": m.group(2), "title": html.unescape(m.group(3)).strip(),
                    "author": html.unescape(m.group(4)).strip(), "snippet": re.sub(r"\s+", " ", snip).strip()})
    return out


def page(book: str, pid: str) -> dict:
    """The text of one page, with the part and page labels Shamela shows (those of the printed edition)."""
    t = _get(f"{BASE}/book/{book}/{pid}")
    title = html.unescape(re.search(r"<title>(.*?)</title>", t, re.S).group(1)) if "<title>" in t else ""
    m = re.search(r'<div class="nass[^"]*"[^>]*>(.*?)</div>\s*<div id="appended_pages"', t, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r"<br\s*/?>", "\n", body)
    text = html.unescape(re.sub(r"<[^>]+>", "", body))
    text = re.sub(r"[ \t]+", " ", text).strip()
    part = re.search(r'id="fld_part_top" value="([^"]*)"', t) or re.search(r'id="fld_part_bottom" value="([^"]*)"', t)
    num = re.search(r'data-page-num="([^"]*)"', t)
    return {"book": book, "pid": pid, "title": title.strip(), "part": part.group(1) if part else "",
            "printed_page": num.group(1) if num else "", "text": text}


def book_card(book: str) -> dict:
    """Title, author and the edition data Shamela records for a book (محقق، ناشر، طبعة، عدد الأجزاء)."""
    t = _get(f"{BASE}/book/{book}")
    title = html.unescape(re.search(r"<title>(.*?)</title>", t, re.S).group(1)).strip() if "<title>" in t else ""
    txt = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    info = {}
    for key in ["المؤلف", "المحقق", "الناشر", "الطبعة", "عدد الأجزاء", "ترقيم الكتاب", "أعده للشاملة"]:
        m = re.search(key + r"\s*:\s*([^\n]+)", txt)
        if m:
            info[key] = m.group(1).strip()
    return {"book": book, "title": title, **info}


if __name__ == "__main__":
    import sys
    for r in search(sys.argv[1], sys.argv[2:] or None)[:10]:
        print(r["book"], r["page"], r["title"], "|", r["author"], "|", r["snippet"][:160])
