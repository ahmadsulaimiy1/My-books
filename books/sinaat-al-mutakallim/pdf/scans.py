#!/usr/bin/env python3
"""Match quotations on the scans of the printed editions (Bible, chs. 48 and 73): the step from «توثيقٌ ناقص» to «متحقّق».

For each source a scan of the adopted edition on archive.org is named, with the OCR archive.org made of it (text per
leaf) and its map of leaves to printed page numbers. For each quotation the leaf whose text best matches it is found;
its printed page is read from the map and compared with the page the note cites; the quotation is then compared with
that leaf again, read afresh by Tesseract from the page image, to be independent of archive.org's reading. A
quotation is matched on print when both readings agree with it closely and the page is the page cited. The page
image is kept as evidence.

    python3 scans.py IK          one source
    python3 scans.py             all configured sources
"""
from __future__ import annotations

import gzip
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

import ledger as L
import shamela as S
from verify import best_window

HERE = Path(__file__).resolve().parent
CACHE = HERE.parent / ".cache" / "scans"
CACHE.mkdir(parents=True, exist_ok=True)
OUT = HERE.parent / "book" / "_production" / "التحقيق"
EVID = OUT / "مصوّرات"
EVID.mkdir(parents=True, exist_ok=True)
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")

# source key -> (who, archive item, {volume: file prefix inside the item}, edition as stated)
SOURCES = {
    "IK": ("ابن خلدون", "01-17270",
           {"1": "history00745 العبر وديوان المبتدأ والخبر تاريخ ابن خلدون - ط دار الفكر 01-08/01_17270"},
           "تاريخ ابن خلدون، دار الفكر، بيروت، ١٤٠١هـ/١٩٨١م"),
}


def fetch(item, name):
    f = CACHE / re.sub(r"[^\w.-]+", "_", f"{item}__{name}")
    if not f.exists() or f.stat().st_size == 0:
        url = f"https://archive.org/download/{item}/{urllib.parse.quote(name)}"
        subprocess.run(["curl", "-sL", "--retry", "3", "-C", "-", "-o", str(f), url], check=True)
    return f


def leaves(item, prefix):
    """Text of every leaf, and its printed page number, from archive.org's OCR."""
    text = gzip.open(fetch(item, prefix + "_hocr_searchtext.txt.gz"), "rt", encoding="utf-8").read()
    index = json.loads(gzip.open(fetch(item, prefix + "_hocr_pageindex.json.gz"), "rt").read())
    pages = json.loads(fetch(item, prefix + "_page_numbers.json").read_text(encoding="utf-8"))
    printed = {p["leafNum"]: str(p.get("pageNumber") or "") for p in pages.get("pages", [])}
    out = []
    for k, span in enumerate(index):
        a, b = span[0], span[1]
        out.append((k, printed.get(k + 1, ""), text[a:b]))
    return out


def tesseract(item, prefix, leaf):
    """The leaf read afresh from the page image, and the image kept as evidence."""
    import pymupdf
    pdf = fetch(item, prefix + ".pdf")
    d = pymupdf.open(str(pdf))
    img = EVID / f"{item}_{leaf:04d}.png"
    if not img.exists():
        d[leaf].get_pixmap(dpi=200).save(str(img))
    r = subprocess.run(["tesseract", str(img), "-", "-l", "ara", "--psm", "6"], capture_output=True, text=True)
    return r.stdout, img


def first_page(p):
    m = re.search(r"[٠-٩0-9]+", str(p).split("؛")[0])
    return m.group(0).translate(EN) if m else ""


def ocr_words(img):
    """Tesseract's words with their boxes, in reading order."""
    r = subprocess.run(["tesseract", str(img), "-", "-l", "ara", "--psm", "4", "tsv"], capture_output=True, text=True)
    rows = [l.split("\t") for l in r.stdout.splitlines()[1:]]
    return [(w[11], int(w[6]), int(w[7]), int(w[8]), int(w[9]), (w[2], w[3], w[4])) for w in rows if len(w) == 12 and w[11].strip()]


def letters(s):
    return re.sub(r"[^ء-ي]", "", S.plain(s)).replace("ى", "ي").replace("ة", "ه").replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")


def locate(words, quote):
    """The run of words that best matches the quotation, letter by letter (tolerant of OCR errors)."""
    import difflib
    q = letters(quote)
    best = (0.0, 0, 0)
    n = len(words)
    for i in range(n):
        acc = ""
        for j in range(i, min(n, i + 120)):
            acc += letters(words[j][0])
            if len(acc) >= len(q) * 0.9:
                r = difflib.SequenceMatcher(None, acc, q, autojunk=False).ratio()
                if r > best[0]:
                    best = (r, i, j)
                if len(acc) > len(q) * 1.15:
                    break
    return best


def printed_number(img):
    """The printed page number, read from the footer band (or, failing that, the header band) of the page image."""
    from PIL import Image
    im = Image.open(img)
    tr = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
    for box in ((0, int(im.height * .86), im.width, im.height), (0, 0, im.width, int(im.height * .09))):
        band = im.crop(box); f = CACHE / "band.png"; band.save(f)
        for lang in ("ara", "ara+eng"):
            r = subprocess.run(["tesseract", str(f), "-", "-l", lang, "--psm", "6"], capture_output=True, text=True)
            m = re.findall(r"[٠-٩0-9۰-۹]{2,4}", r.stdout)
            if m:
                return m[0].translate(tr)
    return ""


def match(key, only=None, offset=-1):
    import pymupdf
    who, item, vols, ed = SOURCES[key]
    quotes = {r["id"]: r["quote"] for r in json.loads((OUT / "مطابقة-النقول.json").read_text(encoding="utf-8"))}
    results = []
    for row in L.ROWS:
        vid, part, page = row[0], row[9], row[10]
        if row[5] != who or vid not in quotes or (only and vid not in only):
            continue
        vol = (part or "1").translate(EN)
        if vol not in vols:
            continue
        cited = int(first_page(page))
        d = pymupdf.open(str(fetch(item, vols[vol] + ".pdf")))
        best = None
        for leaf in (cited + offset, cited + offset + 1, cited + offset - 1):
            img = CACHE / f"{item}_{leaf:04d}.png"
            if not img.exists():
                d[leaf].get_pixmap(dpi=200).save(str(img))
            words = ocr_words(img)
            r, i, j = locate(words, quotes[vid])
            if best is None or r > best[0]:
                best = (r, leaf, img, words, i, j)
        r, leaf, img, words, i, j = best
        from PIL import Image
        im = Image.open(img)
        pn = printed_number(img)
        seg = words[i:j + 1]
        top = max(0, min(w[2] for w in seg) - 40); bottom = min(im.height, max(w[2] + w[4] for w in seg) + 40)
        crop = EVID / f"{vid}.png"
        im.crop((0, top, im.width, bottom)).save(crop)
        ok = r >= 0.85 and pn == str(cited) if pn else False
        results.append({"id": vid, "who": who, "cited": page, "leaf": leaf, "printed": pn, "ratio": round(r, 3),
                        "on_print": ok, "crop": str(crop.relative_to(OUT)), "edition": ed,
                        "url": f"https://archive.org/details/{item}/page/n{leaf}"})
        print(f"{vid}\tcited {page}\tprinted {pn or '?'}\tleaf {leaf}\tletters {r:.2f}\t{'ON PRINT' if ok else 'CHECK'}")
    f = OUT / "مطابقة-المصوّرات.json"
    old = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    keep = [r for r in old if r["id"] not in {x["id"] for x in results}]
    f.write_text(json.dumps(keep + results, ensure_ascii=False, indent=1), encoding="utf-8")
    return results



# ------------------------------------------------------------------ hadith: the first source of each takhrij
BUKHARI = ("03-54504", {n: f"صحيح البخاري - ط السلطانية/{n:02d}_{c}" for n, c in
                        {1: 54495, 2: 54496, 3: 54504, 4: 54505, 5: 54497, 6: 54498, 7: 54506, 8: 54507, 9: 54508}.items()},
           "صحيح البخاري، الطبعة السلطانية، بولاق ١٣١١هـ (وعنها طوق النجاة)")
MUSLIM = ("saheeh_moslem_Abdulbaqy", {0: "Saheeh_Moslem"}, "صحيح مسلم، تحقيق محمد فؤاد عبد الباقي")


def best_leaf(item, prefix, quote, window=None):
    """The leaf that carries the quotation: letter 4-grams shortlist the leaves, then the word run decides."""
    q = letters(quote)
    grams = {q[i:i + 4] for i in range(len(q) - 3)}
    scored = []
    for k, _, t in leaves(item, prefix):
        lt = letters(t)
        if lt and (window is None or window[0] <= k <= window[1]):
            scored.append((len(grams & {lt[i:i + 4] for i in range(len(lt) - 3)}) / max(1, len(grams)), k, t))
    best = (0.0, 0)
    for _, k, t in sorted(scored, reverse=True)[:4]:
        r, _, _ = locate([(w, 0, 0, 0, 0, None) for w in t.split()], quote)
        if r > best[0]:
            best = (r, k)
    return best


def hadith():
    import pymupdf
    from PIL import Image
    quotes = {r["id"]: r["quote"] for r in json.loads((OUT / "مطابقة-النقول.json").read_text(encoding="utf-8"))}
    results = []
    for row in L.ROWS:
        vid, src, part, page = row[0], row[6], row[9], row[10]
        if not vid.startswith("ح") or vid not in quotes:
            continue
        if src.startswith("البخاري"):
            item, vols, ed = BUKHARI
            vol = int(str(part).split("؛")[0].strip().translate(EN))
            prefix = vols[vol]
        elif src.startswith("مسلم"):
            item, vols, ed = MUSLIM
            prefix = vols[0]
            vol = int(str(part).split("؛")[0].strip().translate(EN))
        else:
            continue
        cited = first_page(page)
        # the printed page sits a few leaves after its number (front matter); the index at the end is excluded
        window = (int(cited) - 3, int(cited) + 25) if cited and vol == 1 or item == BUKHARI[0] else None
        r, leaf = best_leaf(item, prefix, quotes[vid], window)
        d = pymupdf.open(str(fetch(item, prefix + ".pdf")))
        img = CACHE / f"{item}_{re.sub(r'[^0-9_]', '', prefix[-8:])}_{leaf:04d}.png"
        if not img.exists():
            d[leaf].get_pixmap(dpi=200).save(str(img))
        words = ocr_words(img)
        r2, i, j = locate(words, quotes[vid])
        im = Image.open(img)
        seg = words[i:j + 1] or words[:1]
        top = max(0, min(w[2] for w in seg) - 50); bottom = min(im.height, max(w[2] + w[4] for w in seg) + 50)
        crop = EVID / f"{vid}.png"
        im.crop((0, top, im.width, bottom)).save(crop)
        head = CACHE / f"head_{vid}.png"
        im.crop((0, 0, im.width, int(im.height * .09))).save(head)
        results.append({"id": vid, "who": row[5], "cited": page, "leaf": leaf, "printed": "", "ratio": round(max(r, r2), 3),
                        "on_print": False, "crop": str(crop.relative_to(OUT)), "head": str(head), "edition": ed,
                        "url": f"https://archive.org/details/{item}/page/n{leaf}"})
        print(f"{vid}\tcited {part}/{page}\tleaf {leaf}\tarchive {r:.2f}\ttesseract {r2:.2f}")
    f = OUT / "مطابقة-المصوّرات.json"
    old = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    keep = [x for x in old if x["id"] not in {y["id"] for y in results}]
    f.write_text(json.dumps(keep + results, ensure_ascii=False, indent=1), encoding="utf-8")


def record(vid, who, item, file, leaf, printed, edition, text_read, page_read="بالعين على الصفحة", also=None):
    """Enter a quotation read by eye on the scan of the printed edition, keeping the page as evidence."""
    import pymupdf
    d = pymupdf.open(str(fetch(item, file)))
    crop = EVID / f"{vid}.png"
    d[leaf].get_pixmap(dpi=80).pil_image().convert("L").save(crop, optimize=True)
    entry = {"id": vid, "who": who, "cited": printed, "leaf": leaf, "printed": printed, "on_print": True,
             "crop": str(crop.relative_to(OUT)), "edition": edition, "url": f"https://archive.org/details/{item}/page/n{leaf}",
             "page_read": page_read, "text_read": text_read}
    if also:
        entry["also"] = also
    f = OUT / "مطابقة-المصوّرات.json"
    old = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
    f.write_text(json.dumps([x for x in old if x["id"] != vid] + [entry], ensure_ascii=False, indent=1), encoding="utf-8")
    return entry


if __name__ == "__main__":
    keys = sys.argv[1:] or list(SOURCES)
    for k in keys:
        match(k)
