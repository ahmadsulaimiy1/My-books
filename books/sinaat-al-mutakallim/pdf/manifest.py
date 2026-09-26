#!/usr/bin/env python3
"""The delivery manifest of the series: what is delivered, volume by volume, with checksums.

The interior is digital-first (Bible ch. 22 §6): its deliverable is the final PDF of each volume, on a white page
field and with no bleed; print masters are made only when the printer, paper, binding and trim are confirmed.
Reads what is on disk (never a list kept by hand): the final PDFs, the cover plates of the three editions in
covers/<edition>/, the spines in covers/spines.json, and the shared files (printer-spec.json, isbn.json). Checks as it
goes that every volume has its final PDF and every edition its full set of plates, and that the PDF's page count is
the one its spine was built on; and stops if not.

    python3 pdf/manifest.py      writes book/_production/الإخراج/ملف-التسليم.md and ملف-التسليم.sha256
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
OUT = ROOT / "book" / "_production" / "الإخراج"
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
        pm = sorted(ROOT.glob(f"Volume-{n:02d}_*_Final-Proof.pdf"))
        if not pm:
            problems.append(f"volume {n}: no final PDF")
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
    for extra in ("spines.json", "printer-spec.json", "isbn.json"):
        sums.append((sha(COVERS / extra), f"covers/{extra}"))
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        sys.exit(1)

    md = ["# صناعة المتكلّم العربي — ملفّ التسليم", "",
          "أحد عشر مجلدًا، ١٧×٢٤ سم. **المتن رقميٌّ أولًا** (الدليل ٢٢ §٦): لكل مجلد نسخته النهائية PDF على أرضيةٍ بيضاء، "
          "بلا نزف؛ ونسخ الطباعة تُصنع حين يُؤكَّد المطبعيّ والورق والتجليد ومقاس القصّ. ولكل مجلد **ألواح الغلاف في الطبعات "
          "الثلاث المعتمدة**، كلُّ لوحٍ ملفٌّ مستقل. والمجاميع في `ملف-التسليم.sha256`.", "",
          "| المجلد | النسخة النهائية | الصفحات | الصفحة (مم) | الكعب (مم) | الغلاف المبسوط (مم) | ألواح الطبعات الثلاث |",
          "|---|---|---|---|---|---|---|"]
    for n, name, pages, trim, spine, wrap, eds, size in rows:
        tw, th = trim.width * 25.4 / 72, trim.height * 25.4 / 72
        md.append(f"| {ar(n)}: {VOLUMES[n - 1]['name']} | `{name}` | {ar(pages)} "
                  f"| {ar(round(tw))}×{ar(round(th))} | {ar(spine)} | {ar(wrap[0])}×{ar(wrap[1])} "
                  f"| {'، '.join(f'{f}: {ar(k)}' for f, k in eds)} |")
    md += ["", "## الملفات المشتركة", "",
           "- `covers/printer-spec.json`: ورق المتن (أبيض ناصع فاخر غير مطلي، محايدٌ لا مصفرّ ولا مزرقّ، عالي العتامة، ببروفة مطبوعة)، "
           "والمتن رقميٌّ أولًا بلا نزف، ومواصفة ألواح الغلاف والرقائق والكبس والورنيش والطبعات الثلاث.",
           "- `covers/spines.json`: عرض الكعب من عدد الصفحات وسُمك الورقة المفترض في `printer-spec.json` — مؤقتٌ حتى يؤكّد المطبعيّ الورق.",
           "- `covers/isbn.json`: فارغٌ عمدًا حتى يصدر الردمك.", "",
           "## ما ينتظر من خارج الإنتاج", "",
           "لا يُطبع بدلها نصٌّ مؤقت (الدليل، الجزء ١٤):", "",
           "1. **الردمك** لكل مجلد وللمجموعة، و**رقم الإيداع**، و**مكان النشر**، و**صاحب الحقوق**: من الناشر؛ ومنطقة الردمك في ظهر الغلاف فارغةٌ محفوظة.",
           "2. **المطبعيّ والورق والتجليد**: الورق الأبيض المختار وسُمكه (يعاد به حساب الكعب)، ومقاس القصّ والنزف إن طُلب، وملفّ ألوانه وشهادة PDF/X؛ "
           "ثم تُصنع نسخ الطباعة من النسخ النهائية، و**بروفة مطبوعة معتمدة** للمتن على الورق نفسه وللغلاف (الدليل ٢٢ §٦).",
           "3. **الرقائق والكبس والورنيش**: أرقام الرقائق من مورّد المطبعة، ومطابقة الألواح بعضها على بعض في بروفة التشطيب.",
           "4. **علامة صفحة العنوان الداخلية** (الدليل ٢٥ §١٤ د): قرارٌ للمؤلف والناشر.", ""]
    (OUT / "ملف-التسليم.md").write_text("\n".join(md), encoding="utf-8")
    (OUT / "ملف-التسليم.sha256").write_text("".join(f"{h}  {p}\n" for h, p in sums), encoding="utf-8")
    print(f"ملف-التسليم.md: {len(rows)} volumes; ملف-التسليم.sha256: {len(sums)} files")


if __name__ == "__main__":
    main()
