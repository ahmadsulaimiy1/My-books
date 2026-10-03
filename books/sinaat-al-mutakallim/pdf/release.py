#!/usr/bin/env python3
"""The release: the eleven digital editions, issued from the final files once they pass their preflight.

Each final (Volume-NN_<name>_Final-Proof.pdf) is checked before it is issued: 170×240 mm, its outline, no review
slug or proof line on any page or in its metadata, the publication data in its imprint (the city, and the volume's
ISBN where one is printed), and a clean preflight report. Then it is copied unchanged, byte for byte, to
release/Volume-NN_<name>.pdf, and release/SHA256SUMS and release/README.md are written. Digital-first, no bleed
(Bible 22 §6): the printer's masters are a separate package, made once the printer confirms the paper.

    python3 pdf/release.py
"""
from __future__ import annotations

import glob
import hashlib
import re
import shutil
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "release"
sys.path.insert(0, str(HERE))
import frontmatter as FM  # noqa: E402

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
ORD = ["الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر", "الحادي-عشر"]


def check(n, path):
    doc = pymupdf.open(str(path))
    bad = []
    r = doc[0].rect
    if (round(r.width / 72 * 25.4), round(r.height / 72 * 25.4)) != (170, 240):
        bad.append("trim")
    if not doc.get_toc():
        bad.append("outline")
    meta = " ".join(str(v) for v in doc.metadata.values())
    if re.search(r"Proof|نسخة المراجعة", meta):
        bad.append("proof in metadata")
    text = "\n".join(p.get_text() for p in doc)
    if "نسخة المراجعة" in text:
        bad.append("review slug on a page")
    flat = re.sub(r"\s+", "", text)
    if FM.CITY and re.sub(r"\s+", "", FM.CITY) not in flat:
        bad.append("city")
    if FM.ISBN.get(n) and FM.ISBN[n] not in text:
        bad.append("ISBN")
    report = ROOT / "book" / "_production" / "الإخراج" / f"فحص-المجلد-{ORD[n - 1]}.md"
    if not report.exists() or any(l.startswith("|") and "| لا يجتاز |" in l for l in report.read_text(encoding="utf-8").splitlines()):
        bad.append("preflight")
    pages = len(doc)
    doc.close()
    return pages, bad


def main():
    OUT.mkdir(exist_ok=True)
    rows, sums, failed = [], [], []
    for n in range(1, 12):
        src = Path(sorted(glob.glob(str(ROOT / f"Volume-{n:02d}_*_Final-Proof.pdf")))[0])
        pages, bad = check(n, src)
        if bad:
            failed.append((n, bad))
            continue
        dst = OUT / src.name.replace("_Final-Proof", "")
        shutil.copyfile(src, dst)
        h = hashlib.sha256(dst.read_bytes()).hexdigest()
        sums.append(f"{h}  {dst.name}\n")
        rows.append((n, dst.name, pages, FM.ISBN.get(n), h))
    if failed:
        for n, bad in failed:
            print(f"volume {n}: NOT released: {', '.join(bad)}")
        sys.exit(1)
    (OUT / "SHA256SUMS").write_text("".join(sums), encoding="utf-8")
    md = [f"# {FM.TITLE}: {FM.SUBTITLE}", "",
          f"الإصدار الرقمي، {FM.EDITION}، {FM.YEAR}. {FM.PUBLISHER_AR} ({FM.PUBLISHER_EN})، {FM.CITY}.", "",
          "أحد عشر مجلدًا، ١٧×٢٤ سم، رقميةٌ أولًا بلا نزف (الدليل ٢٢ §٦)؛ ونسخ المطبعة حزمةٌ مستقلة تُصنع حين يؤكّد المطبعيّ الورق.", "",
          "| المجلد | الملف | الصفحات | ردمك | SHA-256 |", "|---|---|---|---|---|"]
    for n, name, pages, isbn, h in rows:
        md.append(f"| {str(n).translate(AR)}: {FM.VOLUMES[n - 1][1]} | `{name}` | {str(pages).translate(AR)} "
                  f"| {'ISBN ' + isbn if isbn else 'ينتظر تأكيد الناشر'} | `{h}` |")
    md += ["", f"ردمك المجموعة: {'ISBN ' + FM.ISBN_SET if FM.ISBN_SET else 'ينتظر تأكيد الناشر'}. "
           f"رقم الإيداع القانوني: ينتظر الجهة المختصّة.", "",
           "التحقق: `sha256sum -c SHA256SUMS` في هذا المجلد.", ""]
    (OUT / "README.md").write_text("\n".join(md), encoding="utf-8")
    print(f"released {len(rows)} volumes, {sum(r[2] for r in rows)} pages -> {OUT}")


if __name__ == "__main__":
    main()
