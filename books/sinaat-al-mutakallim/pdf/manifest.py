#!/usr/bin/env python3
"""The delivery manifest of the series: what goes to the printer, volume by volume, with checksums.

Reads what is on disk (never a list kept by hand): the press masters in print/, the cover plates of the three
editions in covers/<edition>/, the spines in covers/spines.json, and the shared files (printer-spec.json, isbn.json,
colour-map.tsv). Checks as it goes that every volume has its master and every edition its full set of plates, and
that the master's page count is the one its spine was built on; and stops if not.

    python3 pdf/manifest.py      writes print/MANIFEST.md and print/MANIFEST.sha256
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRINT = ROOT / "print"
COVERS = ROOT / "covers"
sys.path.insert(0, str(HERE))
from covers import EDITIONS  # noqa: E402
from volumes import VOLUMES  # noqa: E402

PLATES = ["PRINT", "SPOT-SAPPHIRE", "FOIL-GOLD", "FOIL-CHAMPAGNE", "FOIL-PEARL", "FOIL-RUBY", "COLD-FOIL",
          "EMBOSS", "DEBOSS", "SPOT-UV", "PRINT-FLAT", "GUIDES"]
AR = "٠١٢٣٤٥٦٧٨٩"


def ar(x):
    return str(x).translate(str.maketrans("0123456789.", AR + "٫"))


def sha(p: Path):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    spines = json.loads((COVERS / "spines.json").read_text(encoding="utf-8"))
    sums, rows, problems = [], [], []
    for n in range(1, len(VOLUMES) + 1):
        pm = sorted(PRINT.glob(f"Volume-{n:02d}_*_Press-Master.pdf"))
        if not pm:
            problems.append(f"volume {n}: no press master")
            continue
        pm = pm[0]
        d = pymupdf.open(str(pm))
        pages = len(d)
        trim = d[0].trimbox
        if spines[str(n)]["pages"] != pages:
            problems.append(f"volume {n}: master has {pages} pages, its spine was built on {spines[str(n)]['pages']}")
        sums.append((sha(pm), pm.relative_to(ROOT).as_posix()))
        eds = []
        for ed in EDITIONS.values():
            folder = ed["folder"]
            have = []
            for plate in PLATES:
                f = sorted((COVERS / folder).glob(f"Cover-{n:02d}_*_{plate}.pdf"))
                if f:
                    have.append(plate)
                    sums.append((sha(f[0]), f[0].relative_to(ROOT).as_posix()))
            missing = [p for p in PLATES if p not in have]
            if "PRINT" in missing or "GUIDES" in missing:
                problems.append(f"volume {n}, {folder}: missing {', '.join(missing)}")
            eds.append((folder, len(have)))
        rows.append((n, pm.name, pages, trim, spines[str(n)]["spine_mm"], spines[str(n)]["wrap_mm"], eds,
                     pm.stat().st_size))
    for extra in ("colour-map.tsv",):
        sums.append((sha(PRINT / extra), f"print/{extra}"))
    for extra in ("spines.json", "printer-spec.json", "isbn.json"):
        sums.append((sha(COVERS / extra), f"covers/{extra}"))
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        sys.exit(1)

    md = ["# صناعة المتكلّم العربي — ملفّ التسليم إلى المطبعة", "",
          "أحد عشر مجلدًا، ١٧×٢٤ سم، تجليدٌ فنّي (case). لكل مجلد: **نسخة المطبعة للمتن** (CMYK بخريطة الألوان، ونزف ٣ مم، "
          "وصندوقا القصّ والنزف) و**ألواح الغلاف في الطبعات الثلاث المعتمدة**، كلُّ لوحٍ ملفٌّ مستقل. والمجاميع في `MANIFEST.sha256`.", "",
          "| المجلد | نسخة المطبعة | الصفحات | القصّ (مم) | الكعب (مم) | الغلاف المبسوط (مم) | ألواح الطبعات الثلاث |",
          "|---|---|---|---|---|---|---|"]
    for n, name, pages, trim, spine, wrap, eds, size in rows:
        tw, th = trim.width * 25.4 / 72, trim.height * 25.4 / 72
        md.append(f"| {ar(n)}: {VOLUMES[n - 1]['name']} | `{name}` | {ar(pages)} "
                  f"| {ar(round(tw))}×{ar(round(th))} | {ar(spine)} | {ar(wrap[0])}×{ar(wrap[1])} "
                  f"| {'، '.join(f'{f}: {ar(k)}' for f, k in eds)} |")
    md += ["", "## الملفات المشتركة", "",
           "- `print/colour-map.tsv`: كل لونٍ في الكتاب وما يُطبع به (يؤكّده المطبعيّ على ملفّ ألوانه).",
           "- `covers/printer-spec.json`: مواصفة الألواح والرقائق والكبس والورنيش والطبعات الثلاث.",
           "- `covers/spines.json`: عرض الكعب من عدد الصفحات وسُمك الورقة المفترض في `printer-spec.json` — مؤقتٌ حتى يؤكّد المطبعيّ الورق.",
           "- `covers/isbn.json`: فارغٌ عمدًا حتى يصدر الردمك.", "",
           "## ما ينتظر من خارج الإنتاج", "",
           "لا يُطبع بدلها نصٌّ مؤقت (الدليل، الجزء ١٤):", "",
           "1. **الردمك** لكل مجلد وللمجموعة، و**رقم الإيداع**، و**مكان النشر**، و**صاحب الحقوق**: من الناشر؛ ومنطقة الردمك في ظهر الغلاف فارغةٌ محفوظة.",
           "2. **ورق المتن وسُمكه** من المطبعة: يعاد به حساب الكعب (`covers.py` من `spines.json`) قبل تجهيز الألواح.",
           "3. **ملفّ ألوان المطبعة** (FOGRA أو غيره) وشهادة PDF/X؛ و**بروفة مطبوعة معتمدة** للمتن والغلاف (الدليل ٢٢ §٦)، "
           "وفيها يُختبر النصّ الصغير بالياقوتي والذهبي، والأسود فوق الأرضيات (overprint) على إعداد المطبعة.",
           "4. **الرقائق والكبس والورنيش**: أرقام الرقائق من مورّد المطبعة، ومطابقة الألواح بعضها على بعض في بروفة التشطيب.",
           "5. **علامة صفحة العنوان الداخلية** (الدليل ٢٥ §١٤ د): قرارٌ للمؤلف والناشر.", ""]
    (PRINT / "MANIFEST.md").write_text("\n".join(md), encoding="utf-8")
    (PRINT / "MANIFEST.sha256").write_text("".join(f"{h}  {p}\n" for h, p in sums), encoding="utf-8")
    print(f"MANIFEST.md: {len(rows)} volumes; MANIFEST.sha256: {len(sums)} files")


if __name__ == "__main__":
    main()
