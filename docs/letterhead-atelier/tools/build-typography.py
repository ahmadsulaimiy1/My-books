#!/usr/bin/env python3
"""
Build assets/letterhead-typography.css — every face subset and embedded.

Why the faces are INSTANCED to static weights: Chrome's print-to-PDF pipeline
does not embed variable fonts. It silently substitutes a system serif, so a PDF
that looked perfect on screen reaches the printer set in Liberation Serif. Each
weight we actually use is therefore pinned to a static instance first.

Why the Arabic is NOT subset to the masthead wording: the letterhead is a
template. It has to set any correspondence written on it, so Amiri and Reem Kufi
keep the whole Arabic block. Only the Latin faces are cut to a repertoire.

    pip install fonttools brotli
    python3 tools/build-typography.py
"""
import base64, io, os, re, subprocess, sys, tempfile

HERE   = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), "assets")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/120.0.0.0 Safari/537.36")

# Latin repertoire: enough for any letter body, the names, and the contact block
LATIN = ("U+0020-007E,U+00A0,U+00A9,U+00AB,U+00BB,U+00B7,U+00C0-00FF,U+0100-0101,"
         "U+012A-012B,U+014C-014D,U+016A-016B,U+2010-2011,U+2013-2014,U+2018-2019,"
         "U+201C-201D,U+2020,U+2022,U+2026,U+2030,U+20AC,U+2122")
ARABIC = ("U+0020,U+00A0,U+0600-06FF,U+0750-077F,U+08A0-08FF,U+200C-200F,U+2010-2011,"
          "U+FB50-FDFF,U+FE70-FEFC")
AR_FEATURES = "ccmp,locl,isol,init,medi,fina,rlig,calt,rclt,liga,kern,mark,mkmk,curs"
LA_FEATURES = "ccmp,locl,liga,calt,kern,mark,mkmk,onum,lnum,tnum"

# unicode-ranges declared in the CSS
UR_AR  = ARABIC
UR_LAT = ("U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,"
          "U+2000-206F,U+2074,U+20AC,U+2122,U+2212")
UR_EXT = ("U+0100-024F,U+0259,U+1E00-1EFF,U+2020,U+20A0-20AB,U+20AD-20CF,U+2113,"
          "U+2C60-2C7F,U+A720-A7FF")

# family, google query, subset label, weight, pinned axes (None = already static)
FACES = [
    # ── Arabic ──────────────────────────────────────────────────────────────
    # SCHEHERAZADE NEW for the document voice. Amiri was here and has been
    # replaced outright. Set against it at matched optical size, Amiri reads
    # as a competent screen Naskh: even colour, shallow modulation, shallow
    # descenders — the look of a document produced in an office. Scheherazade
    # is a classical Naskh in the tradition of the great Cairo and Beirut
    # book founts: pronounced thick/thin modulation, deep generous bowls,
    # long confident descenders, and a rhythm that wants air around it. It is
    # the fount of Qur'anic and scholarly Arabic publishing, and it is what a
    # letter from a scholar's office should be set in.
    #
    # It carries a large body for its point size, so it is set at 13.4pt where
    # Amiri was at 11.2pt — the same apparent size, more presence.
    ("Scheherazade New","family=Scheherazade+New:wght@400","arabic", 400, {"wght":400}),
    ("Scheherazade New","family=Scheherazade+New:wght@400","latin",  400, {"wght":400}),
    ("Scheherazade New","family=Scheherazade+New:wght@700","arabic", 700, {"wght":700}),
    ("Scheherazade New","family=Scheherazade+New:wght@700","latin",  700, {"wght":700}),
    # REEM KUFI for display. A contemporary Kufi drawn from the Jazm tradition
    # by the same hand that drew Amiri, so the pairing is a designed one rather
    # than an assembled one. Monumental without being a calligraphic pastiche,
    # geometric without being a geometry exercise.
    ("Reem Kufi",       "family=Reem+Kufi:wght@400",    "arabic",    400, {"wght":400}),
    ("Reem Kufi",       "family=Reem+Kufi:wght@400",    "latin",     400, {"wght":400}),
    ("Reem Kufi",       "family=Reem+Kufi:wght@600",    "arabic",    600, {"wght":600}),
    ("Reem Kufi",       "family=Reem+Kufi:wght@600",    "latin",     600, {"wght":600}),

    # ── Latin ───────────────────────────────────────────────────────────────
    # EB GARAMOND, for display AND body. A Garamond is the European counterpart
    # to what Amiri is: a humanist book face with calligraphic roots, cut for
    # reading at length. Setting the identity in its capitals and the letter in
    # its lowercase gives one voice across the whole Latin side.
    ("EB Garamond",     "family=EB+Garamond:wght@400",  "latin",     400, {"wght":400}),
    ("EB Garamond",     "family=EB+Garamond:wght@400",  "latin-ext", 400, {"wght":400}),
    ("EB Garamond",     "family=EB+Garamond:wght@600",  "latin",     600, {"wght":600}),
    ("EB Garamond",     "family=EB+Garamond:wght@600",  "latin-ext", 600, {"wght":600}),
    # PLAYFAIR DISPLAY 700 carries the Latin WORDMARK. EB Garamond's capitals
    # are a book face's capitals: narrow, old-style, and they read as reticent
    # at identity size. Playfair at 700 is wide, high-contrast and genuinely
    # bold — the difference between a name set in a book and a name on a door.
    ("Playfair Display","family=Playfair+Display:wght@700","latin",     700, {"wght":700}),
    ("Playfair Display","family=Playfair+Display:wght@700","latin-ext", 700, {"wght":700}),
    # INTER for the instrument layer only — references, serials, microtext.
    # Deliberately impersonal: this part of the page is machinery, not voice.
    ("Inter",           "family=Inter:wght@400",        "latin",     400, {"wght":400,"opsz":14}),
    ("Inter",           "family=Inter:wght@400",        "latin-ext", 400, {"wght":400,"opsz":14}),
    ("Inter",           "family=Inter:wght@600",        "latin",     600, {"wght":600,"opsz":14}),
    ("Inter",           "family=Inter:wght@600",        "latin-ext", 600, {"wght":600,"opsz":14}),
]

def google_css(query):
    r = subprocess.run(["curl", "-sS", "-L", "-A", UA,
                        f"https://fonts.googleapis.com/css2?{query}&display=block"],
                       check=True, capture_output=True)
    return r.stdout.decode()

def face_url(css, label):
    for lbl, block in re.findall(r"/\*\s*([a-z0-9\-]+)\s*\*/\s*(@font-face\s*\{.*?\})", css, re.S):
        if lbl == label:
            return re.search(r"url\((https://[^)]+\.woff2)\)", block).group(1)
    raise SystemExit(f"subset {label!r} not offered for this family")

def main():
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    os.makedirs(ASSETS, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="lh-fonts-")
    blocks, total = [], 0

    for i, (fam, query, label, weight, pin) in enumerate(FACES):
        url = face_url(google_css(query), label)
        raw = os.path.join(tmp, f"{i}.woff2")
        subprocess.run(["curl", "-sS", "-L", "-A", UA, "-o", raw, url], check=True)

        src = raw
        if pin:
            f = TTFont(raw)
            if "fvar" in f:
                # Google may already have instanced some axes away, so pin only
                # what this file still carries. Every REMAINING axis must be
                # pinned: a partially-instanced font is still variable, and
                # Chrome declines to embed it in the PDF just the same.
                have = {a.axisTag for a in f["fvar"].axes}
                limits = {k: v for k, v in pin.items() if k in have}
                missing = have - set(limits)
                if missing:
                    raise SystemExit(f"{fam} {weight} {label}: unpinned axes {sorted(missing)}")
                f = instancer.instantiateVariableFont(f, limits, inplace=True,
                                                      updateFontNames=False)
                src = os.path.join(tmp, f"{i}-static.ttf")
                f.save(src)

        arabic = label == "arabic"
        out = os.path.join(tmp, f"{i}-sub.woff2")
        subprocess.run([
            "pyftsubset", src, f"--output-file={out}", "--flavor=woff2",
            f"--unicodes={ARABIC if arabic else LATIN}",
            f"--layout-features={AR_FEATURES if arabic else LA_FEATURES}",
            "--ignore-missing-unicodes", "--ignore-missing-glyphs",
            "--no-hinting", "--desubroutinize", "--name-IDs=1,2,3,4,6",
        ], check=True)

        size = os.path.getsize(out); total += size
        b64 = base64.b64encode(open(out, "rb").read()).decode()
        urange = UR_AR if arabic else (UR_LAT if label == "latin" else UR_EXT)
        blocks.append(
            f"/* {fam} {weight} · {label} · {size/1024:.1f} KB */\n"
            f"@font-face{{\n  font-family:'{fam}';\n  font-style:normal;\n"
            f"  font-weight:{weight};\n  font-display:block;\n"
            f"  src:url(data:font/woff2;base64,{b64}) format('woff2');\n"
            f"  unicode-range:{urange};\n}}\n")
        print(f"{fam:16s} {weight} {label:10s} {size/1024:7.1f} KB"
              f"{'  [instanced]' if pin else ''}")

    header = """/* ══════════════════════════════════════════════════════════════════════════════
   THE PERSONAL OFFICE — ATELIER TYPOGRAPHY
   المكتب الخاص · الإمام أحمد بن إبراهيم السليمي (آل سلام)

   GENERATED FILE — do not edit. Rebuild with tools/build-typography.py.

   Every face is subset and embedded as WOFF2, so the stationery renders
   identically offline, at a print shop, and inside an exported PDF, with no
   font to install and no network request.

   FOUR VOICES, AND A RULE FOR EACH. Every line on the sheet belongs to one
   of three layers, and each layer has exactly one fount per script:

                   ARABIC                LATIN
     IDENTITY      Reem Kufi             Playfair Display 700
     DOCUMENT      Scheherazade New      EB Garamond
     INSTRUMENT    Reem Kufi (small)     Inter

   Nothing crosses. The office name, the personal name, the house and the
   scope are IDENTITY and are set only in the first row. The letter, the
   Bismillah, the addressee and the subject are DOCUMENT. References,
   serials, glosses, microtext and the folio are INSTRUMENT — deliberately
   impersonal, because that part of the page is machinery, not voice.

   Two decisions worth keeping:
   · Faces are pinned to STATIC instances. Chrome's print-to-PDF will not embed
     a variable font; it substitutes a system serif without warning, so a PDF
     that looked right on screen reaches the printer in the wrong typeface.
   · Arabic coverage is the FULL Arabic block, not merely the masthead wording,
     so the template sets whatever correspondence is written on it.
   ══════════════════════════════════════════════════════════════════════════ */

"""
    dest = os.path.join(ASSETS, "letterhead-typography.css")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(blocks))
    print(f"\n{total/1024:.0f} KB of font → {os.path.getsize(dest)/1024:.0f} KB of CSS")
    print(dest)

if __name__ == "__main__":
    main()
