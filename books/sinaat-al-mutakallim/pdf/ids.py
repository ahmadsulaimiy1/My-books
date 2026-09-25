#!/usr/bin/env python3
"""The identifiers of the examples (Bible, ch. 112d §٥): a production ID in the source, a teaching ID on the page.

The manuscript keeps every example's full production ID, written under the four parts of the earlier edition:
[م٢-ب٦-ف٤-مث١] = part 2, bab 6, chapter 4, example 1. It is kept for traceability and is never printed. The printed
ID drops the part, whose «م» would read as a level, and numbers the bab across the series: [ب٦-ف٤-مث١]. The Malaka
(the fourteenth bab of that edition) is the thirteenth; the error bank (its thirteenth) is the first reference and
takes its own prefix: [ر١-ف٤-مث١].

    printed(text)    the text as it is set: every production ID converted; stops on one that does not convert
    check(html)      stops the build if a production ID reached the page
    python3 ids.py   writes the register production ID → printed ID → file, and checks every file of the series
"""
import csv
import re
import sys

from volumes import BOOK

AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
EN = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
PROD = re.compile(r"\[م([٠-٩]+)-ب([٠-٩]+)-ف([٠-٩]+)-مث([٠-٩]+[أ-ي]?)\]")   # an example may carry a letter: مث١٦أ
PART_OF = {b: (1 if b <= 3 else 2 if b <= 6 else 3 if b <= 10 else 4) for b in range(1, 15)}
REGISTER = BOOK / "_production" / "هندسة-السلسلة" / "سجل-المعرفات.tsv"


def teaching_id(m):
    part, bab = int(m.group(1).translate(EN)), int(m.group(2).translate(EN))
    if PART_OF.get(bab) != part:
        raise ValueError(f"{m.group(0)}: part {part} does not hold bab {bab}")
    tail = f"-ف{m.group(3)}-مث{m.group(4)}]"
    if bab == 13:
        return "[ر١" + tail
    return "[ب" + str(14 - 1 if bab == 14 else bab).translate(AR) + tail


def printed(text):
    return PROD.sub(teaching_id, text)


def check(html):
    left = re.findall(r"\[م[٠-٩]+-ب[٠-٩]+", html)
    if left:
        raise SystemExit(f"production IDs reached the page: {left[:5]}")
    return html


def main():
    rows, errors = [], []
    for f in sorted(BOOK.glob("المجلد-*/**/*.md")) + sorted(BOOK.glob("_المرافقة/**/*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in PROD.finditer(line):
                try:
                    rows.append([m.group(0), teaching_id(m), str(f.relative_to(BOOK)), str(n)])
                except ValueError as e:
                    errors.append(f"{f.relative_to(BOOK)}:{n}: {e}")
    with open(REGISTER, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["المعرّف الإنتاجي", "المعرّف المطبوع", "الملف", "السطر"])
        w.writerows(rows)
    printed_ids = [r[1] for r in rows]
    dup = {x for x in printed_ids if printed_ids.count(x) > 1} if len(printed_ids) < 20000 else set()
    print(len(rows), "IDs;", len(set(printed_ids)), "distinct printed;", len(errors), "errors")
    for e in errors:
        print("  ", e)
    if dup:
        print("  printed IDs used more than once (a cross-reference or a duplicate):", len(dup))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
