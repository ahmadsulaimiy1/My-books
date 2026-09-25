"""Manuscript QA: completeness, banned phrases, separators, terminology, required dialogues."""
import re, sys, collections
from pathlib import Path
BOOK = Path(__file__).resolve().parent.parent / "book"
# chapter counts per bab, from the Bible book map
COUNT = {1: 6, 2: 12, 3: 9, 4: 10, 5: 9, 6: 9, 7: 7, 8: 5, 9: 5, 10: 5, 11: 4, 12: 3, 13: 8, 14: 3}
BANNED = ["في عالمنا المتسارع", "لا شك أن", "مما لا ريب فيه", "يلعب دور", "مفتاح النجاح", "في هذا الفصل سوف نستعرض", r"(?<![\u0621-\u064A])رحلة", r"(?<![\u0621-\u064A])بوابة"]
files = sorted(p for p in BOOK.rglob("*.md") if "_production" not in p.parts)
bab_dirs = {}
for d in BOOK.glob("الجزء-*/الباب-*"):
    bab_dirs[d.name] = d
issues = collections.defaultdict(list)
words = 0
for f in files:
    t = f.read_text(encoding="utf-8")
    words += len(re.findall(r"\S+", t))
    rel = f.relative_to(BOOK)
    for b in BANNED:
        for m in re.finditer(b, t):
            line = t[:m.start()].count("\n") + 1
            ctx = t[max(0, m.start()-30):m.end()+30].replace("\n", " ")
            if "رحلة" in b or "بوابة" in b and ("✘" in ctx or "①" in ctx):
                continue
            issues["banned"].append(f"{rel}:{line} «{b}» … {ctx}")
    for m in re.finditer(r"[٠-٩]\s?·|·\s?[٠-٩]", t):
        issues["middot"].append(f"{rel}:{t[:m.start()].count(chr(10))+1}")
    for m in re.finditer(r"المتكلم المتقن|المتكلم الفاشل|المتكلمُ الفاشل", t):
        issues["term"].append(f"{rel}:{t[:m.start()].count(chr(10))+1} {m.group(0)}")
    if re.search(r"^#####", t, re.M):
        issues["h5"].append(str(rel))
    if "سجل اعتماد الفصل" in t:
        issues["audit-log"].append(str(rel))
    for i, ln in enumerate(t.split("\n"), 1):
        s2 = re.sub(r"^\s*\d+\.\s", "", ln)
        s2 = re.sub(r"\[[^\]]*\]\([^)]*\)|`[^`]*`|<[^>]+>|[A-Za-z][A-Za-z0-9 .,'\-]*", "", s2)
        if re.search(r"[0-9]", s2) and re.search(r"[\u0621-\u064A]", s2):
            issues["latin-digit"].append(f"{rel}:{i} {ln[:90]}")
# completeness
status = {}
for name, d in sorted(bab_dirs.items()):
    chs = collections.defaultdict(str)
    for f in d.glob("ف*.md"):
        m = re.match(r"ف(\d\d)", f.name)
        chs[int(m.group(1))] += f.read_text(encoding="utf-8")
    status[name] = chs
print(f"files {len(files)}, words {words:,}")
for name, chs in status.items():
    row = []
    for n in sorted(chs):
        t = chs[n]
        done = bool(re.search(r"^#+\s*الخلاصة", t, re.M)) and bool(re.search(r"^#+\s*معيار الإتقان", t, re.M))
        row.append(f"{n}{'✔' if done else 'P'}({len(t.split())//100/10}k)")
    op = "op" if list(BOOK.glob(f"*/{name}/00-*.md")) else "NO-OPENER"
    print(name, op, " ".join(row))
for k, v in issues.items():
    print(f"\n[{k}] {len(v)}")
    for x in v[:15]:
        print("  ", x)
