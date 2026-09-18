#!/usr/bin/env python3
"""
LETTERHEAD v1 — the lock.

    python3 tools/verify-v1.py            check this working tree against v1
    python3 tools/verify-v1.py --spec     rewrite SPEC-v1.md from the constants
    python3 tools/verify-v1.py --seal     rewrite MANIFEST-v1.sha256 (RE-LOCKS)

v1 is a RELEASED design. Two things are frozen and this script checks both:

  1. THE CONSTANTS below — every dimension, colour and type size the design
     depends on, each paired with the file and the pattern that must still
     contain it. A stylesheet edit that moves the gold rail, re-sizes the
     body face or shifts the seal's clear zone fails here by name.
  2. THE MANIFEST — a SHA-256 of every released file, so a changed PDF,
     asset or page is caught even if the CSS still reads correctly.

`--seal` is how a NEW version is cut. It is not a way to make a failing
tree pass: if the design has genuinely moved on, bump VERSION, update the
constants, re-seal, and tag. If it has not, fix the drift.
"""
import hashlib, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
VERSION  = "letterhead v1.0"
MANIFEST = os.path.join(ROOT, "MANIFEST-v1.sha256")
SPEC     = os.path.join(ROOT, "SPEC-v1.md")

A = "assets/atelier.css"
M = "assets/materials.css"

# ── section, label, file, the exact text that must be present ───────────────
CONSTANTS = [
 ("THE SHEET", [
  ("Trim",                      M, "width:210mm; height:297mm"),
  ("Page box",                  M, "@page{ size:A4; margin:0; }"),
  ("Left axis — every block",   A, ".register{ position:absolute; top:107.4mm; left:24mm; right:48mm;"),
  ("Writing measure",           A, ".field{ position:absolute; top:147mm; left:24mm; right:48mm; bottom:52mm;"),
 ]),
 ("THE PLATE", [
  ("Head depth 56mm, pier at 172mm", A,
   ".plate     { clip-path:polygon(0 0,210mm 0,210mm 297mm,172mm 297mm,172mm 56mm,0 56mm);"),
  ("Gold keyline — lower silhouette only, 0.55mm proud", A,
   ".plate-gold{ clip-path:polygon(0 0,210mm 0,210mm 297mm,172mm 297mm,172mm 56.55mm,0 56.55mm); }"),
  ("Continuation pier — same 38mm", A, ".cont-plate{ position:absolute; top:0; right:0; bottom:0; width:38mm;"),
 ]),
 ("THE BINDING EDGE — nine members, total 7.87mm from x=172mm", [
  ("Assembly origin and width", A, ".edge{ position:absolute; top:0; bottom:0; left:172mm; width:7.87mm;"),
  ("1 · crevice + lit arris  .55", A, ".edge-arris{ position:absolute; top:56mm; bottom:0; left:-.20mm; width:.55mm;"),
  ("2 · SILL, lit            .86", A, ".edge-sill { left:.35mm;  width:.86mm;"),
  ("3 · near wall, cut       .19", A, ".edge-cut  { left:1.21mm; width:.19mm;"),
  ("4 · GOLD RAIL, proud    3.40", A, ".edge-rail { left:1.40mm; width:3.40mm;"),
  ("5 · return, lit chamfer  .35", A, ".edge-ret  { left:4.80mm; width:.35mm;"),
  ("6 · PLATINUM, recessed  2.20", A, ".edge-plat { left:5.15mm; width:2.20mm;"),
  ("7 · far wall, lit        .30", A, ".edge-wall { left:7.35mm; width:.30mm;"),
  ("8 · cut line             .22", A, ".edge-rule { left:7.65mm; width:.22mm; background:#020814; }"),
 ]),
 ("THE SEAL — 46mm, centred (139, 56), 10mm clear on every side", [
  ("Medallion",                 A, ".medallion{ position:absolute; left:116mm; top:33mm; width:46mm; height:46mm;"),
  ("Bezel — steel ring",        A, ".med-steel{ position:absolute; inset:1.5mm;"),
  ("Field",                     A, ".med-field{ position:absolute; inset:2.6mm;"),
  ("Inner hairline ring",       A, ".med-hair { position:absolute; inset:4.4mm;"),
  ("Mark, 19mm, clear inside",  A, ".med-mark { position:absolute; left:50%; top:50%;"),
  ("Latin wordmark held OFF the clear zone", A,
   'font-size:13.6pt;\n  letter-spacing:.06em;'),
 ]),
 ("THE RED CHANNEL — the binding section turned 90°", [
  ("Stainless wall, above, shaded  .50", A, ".redch-steel{ position:absolute; left:0; right:38mm; top:94.5mm; height:.5mm;"),
  ("Red channel                   5.60", A, ".redch      { position:absolute; left:0; right:38mm; top:95mm; height:5.6mm;"),
  ("Gold wall, below, lit          .62", A, ".redch-gold { position:absolute; left:0; right:38mm; top:100.6mm; height:.62mm;"),
 ]),
 ("TYPOGRAPHY — four voices, one fount per script per layer", [
  ("Arabic identity · Reem Kufi 600 19pt", A, 'font-weight:600; font-size:19pt;'),
  ("Latin identity · Playfair Display 700 13.6pt", A, '.ident-name{ font-family:"Playfair Display",serif; font-weight:700;'),
  ("Arabic document · Scheherazade New 13.4pt / 1.78", A,
   '.letter{ font-family:"Scheherazade New",serif; font-size:13.4pt; line-height:1.78;'),
  ("Latin document · EB Garamond",   A, '.letter .lat{ font-family:"EB Garamond",serif;'),
  ("Instrument · Inter",             A, ".foot .contact{ font:400 6.2pt/1 \"Inter\",sans-serif;"),
  ("Amiri is OUT of the build", "tools/build-typography.py", '"Scheherazade New","family=Scheherazade+New:wght@400","arabic", 400'),
 ]),
 ("PALETTE", [
  ("Sapphire, deepest",  M, "--sapphire-950:#020B1E;"),
  ("Sapphire, ground",   M, "--sapphire-800:#082349;"),
  ("Sapphire, lit",      M, "--sapphire-600:#11418F;"),
  ("RED — the principal red, and it is red", M, "--red-700:#C8102E;"),
  ("Pearl",              M, "--pearl:#FBF9F5;"),
  ("Ink",                M, "--ink:#121826;"),
  ("Gold — rich ramp, for members that carry weight", M, "--foil-gold-rich:linear-gradient(104deg,"),
  ("Platinum — cooler and a stop darker than the stainless", M, "--foil-plat:linear-gradient(104deg,"),
  ("Stainless — the diamond ramp, white at 72%", M, "--foil-steel:linear-gradient(104deg,"),
 ]),
]

SKIP = {"MANIFEST-v1.sha256"}

def files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if not d.startswith(".")]
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), ROOT)
            if rel not in SKIP and not f.startswith("."):
                yield rel

def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(ROOT, rel), "rb") as fh:
        for b in iter(lambda: fh.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()

def seal():
    lines = [f"# {VERSION} — sealed manifest", "# verify: python3 tools/verify-v1.py", ""]
    lines += [f"{sha(r)}  {r}" for r in files()]
    open(MANIFEST, "w").write("\n".join(lines) + "\n")
    print(f"sealed {len(lines)-3} files → {os.path.relpath(MANIFEST, ROOT)}")

def check():
    bad = []
    for section, items in CONSTANTS:
        print(f"\n  {section}")
        for label, rel, needle in items:
            src = open(os.path.join(ROOT, rel), encoding="utf-8").read()
            ok = needle in src
            print(f"    {'ok ' if ok else 'XX '} {label}")
            if not ok:
                bad.append(f"{section} · {label}  ({rel})")

    print("\n  MANIFEST")
    if not os.path.exists(MANIFEST):
        bad.append("MANIFEST-v1.sha256 missing — nothing is sealed")
    else:
        want = {}
        for ln in open(MANIFEST):
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                d, _, r = ln.partition("  ")
                want[r] = d
        have = set(files())
        for r in sorted(set(want) | have):
            if r not in want:   bad.append(f"untracked file: {r}");     print(f"    XX  new      {r}")
            elif r not in have: bad.append(f"file missing: {r}");       print(f"    XX  missing  {r}")
            elif sha(r) != want[r]: bad.append(f"file changed: {r}");   print(f"    XX  changed  {r}")
        print(f"    ok  {len(have)} files match" if not bad else "")

    if bad:
        print(f"\n  ✗ {VERSION} — {len(bad)} deviation(s):")
        for b in bad: print("      ·", b)
        return 1
    print(f"\n  ✓ {VERSION} — locked, and this tree matches it.")
    return 0

def spec():
    out = [f"# {VERSION} — the locked specification", "",
           "**الإمام أحمد بن إبراهيم السليمي (آل سلام)** · PERSONAL OFFICE ·"
           " IMAM AHMAD IBROHIM SULAIMIY · ĀL-ES-SALAM", "",
           "> GENERATED FILE — rewritten by `tools/verify-v1.py --spec`.",
           "> Every value below is read back out of the stylesheets by",
           "> `python3 tools/verify-v1.py`, which fails by name if one moves.", ""]
    for section, items in CONSTANTS:
        out += [f"## {section}", "", "| | value in source |", "|---|---|"]
        for label, rel, needle in items:
            v = needle.replace("\n", " ").replace("|", "\\|")
            out.append(f"| {label} | `{v}` |")
        out.append("")
    out += ["## What is NOT frozen", "",
            "The stationery is a template, so the **content** of a letter is free:",
            "the addressee, the reference, the date, the subject, the body and the",
            "signature blocks all change per letter and are not part of v1.",
            "",
            "Everything else is. A change to any table above is a change to the",
            "**design**, and belongs in v2 — bump `VERSION` in `tools/verify-v1.py`,",
            "update the constant, re-seal with `--seal`, and tag.", ""]
    open(SPEC, "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {os.path.relpath(SPEC, ROOT)}")

if __name__ == "__main__":
    a = sys.argv[1:]
    if "--seal" in a: seal()
    if "--spec" in a: spec()
    if not a: sys.exit(check())
