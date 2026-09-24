#!/usr/bin/env python3
"""Renumber a chapter's notes in the order of their first call (Bible, ch. 82 §6).

A note may be written with any label ([^new], [^x2]) where it is born in the text; this gives every note its
chapter number by the order of its call, rewrites the definitions in that order, and stops if a call has no
definition or a definition no call.

    python3 renumber.py ../book/الافتتاحية/05-….md
"""
import re
import sys
from pathlib import Path

DEF = re.compile(r"^\[\^([^\]]+)\]:\s*(.*)$", re.M)


def renumber(md: str) -> str:
    defs = dict(DEF.findall(md))
    body = DEF.sub("", md).rstrip() + "\n"
    order = list(dict.fromkeys(re.findall(r"\[\^([^\]]+)\]", body)))
    if set(order) != set(defs):
        raise SystemExit(f"calls and notes differ: {sorted(set(order) ^ set(defs))}")
    new = {old: str(i) for i, old in enumerate(order, 1)}
    body = re.sub(r"\[\^([^\]]+)\]", lambda m: f"[^{new[m.group(1)]}]", body)
    return body + "\n" + "\n".join(f"[^{new[o]}]: {defs[o]}" for o in order) + "\n"


if __name__ == "__main__":
    for f in sys.argv[1:]:
        p = Path(f)
        p.write_text(renumber(p.read_text(encoding="utf-8")), encoding="utf-8")
        print(p.name, "renumbered")
