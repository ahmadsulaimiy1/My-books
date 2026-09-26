#!/usr/bin/env python3
"""The typesetter's last pass: headings preflight still finds alone at the foot of a page are recorded in
book/_production/الإخراج/فواصل-الصفحات.json so that volume.py opens a new page before them.

    python3 pdf/fixbreaks.py N      read the volume's preflight report and add its stranded headings
"""
import json
import re
import sys
from pathlib import Path

BOOK = Path(__file__).resolve().parent.parent / "book"
OUT = BOOK / "_production" / "الإخراج" / "فواصل-الصفحات.json"
ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي-عشر"]


def main(n):
    import pymupdf
    import glob
    pdf = glob.glob(str(BOOK.parent / f"Volume-{n:02d}_*_Final-Proof.pdf"))[0]
    doc = pymupdf.open(pdf)
    found = []
    for p in doc:
        lines = []
        for b in p.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                if l["spans"] and l["bbox"][3] < p.rect.height * 0.92:
                    s = max(l["spans"], key=lambda s: len(s["text"].strip()))
                    if s["text"].strip():
                        lines.append((l["bbox"][3], s["font"], s["size"], l))
        if not lines:
            continue
        lines.sort(key=lambda x: x[0])
        y, font, size, l = lines[-1]
        if "Changa" in font and size >= 11.5:
            # the heading's text in logical order: from the words of the source that match its letters
            found.append(" ".join(s["text"] for s in l["spans"]).strip())
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    have = set(data.get(str(n), []))
    # match against the source headings (the PDF gives visual order)
    import unicodedata
    def key(t):
        return "".join(sorted(re.sub(r"\s+", "", unicodedata.normalize("NFKC", t))))
    sys.path.insert(0, str(Path(__file__).parent))
    from volumes import VOLUMES, unit_files
    heads = []
    for u in VOLUMES[n - 1]["units"]:
        for f in unit_files(n, u):
            if f.exists():
                heads += [re.sub(r"[*`#]", "", h).strip() for h in re.findall(r"^#{2,4}\s+(.+)$", f.read_text(encoding="utf-8"), re.M)]
    byk = {}
    for h in heads:
        byk.setdefault(key(re.sub(r"^[٠-٩]+\.\s*", "", h)), h)
    added = []
    for t in found:
        h = byk.get(key(t))
        if h and h not in have:
            have.add(re.sub(r"^[٠-٩]+\.\s*", "", h)); added.append(h)
    data[str(n)] = sorted(have)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"volume {n}: {len(found)} stranded; added {added}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(int(a))
