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
    # the pages preflight rejected (its report gives folios; the PDF text gives their digits in either order)
    tsv = BOOK / "_production" / "الإخراج" / f"فحص-المجلد-{ORD[n - 1]}.tsv"
    bad = {r.split("\t")[0] for r in tsv.read_text(encoding="utf-8").splitlines() if "عنوانٌ في أسفل الصفحة" in r} if tsv.exists() else set()
    toc = doc.get_toc()
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
        folio = p.get_text().split()[-1] if p.get_text().split() else ""
        if folio not in bad and folio[::-1] not in bad:
            continue
        lines.sort(key=lambda x: x[0])
        y, font, size, l = lines[-1]
        if "Changa" in font and size >= 11.5:
            mark = [t[1] for t in toc if t[2] <= p.number + 1]
            found.append((mark[-1] if mark else "", " ".join(s["text"] for s in l["spans"]).strip()))
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    have = {e for e in data.get(str(n), []) if " ▸ " in e}     # entries are «bookmark ▸ heading»
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
        byk.setdefault(key(re.sub(r"^[٠-٩]+\.\s*", "", h)), re.sub(r"^[٠-٩]+\.\s*", "", h))
    added = []
    for mark, t in found:
        h = byk.get(key(t))
        if h and f"{mark} ▸ {h}" not in have:
            have.add(f"{mark} ▸ {h}"); added.append(f"{mark} ▸ {h}")
    data[str(n)] = sorted(have)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"volume {n}: {len(found)} stranded; added {added}")


if __name__ == "__main__":
    for a in sys.argv[1:]:
        main(int(a))
