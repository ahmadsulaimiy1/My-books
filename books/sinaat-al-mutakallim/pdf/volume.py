#!/usr/bin/env python3
"""A volume of the series, typeset whole in the edition-1.2 system, from the authoritative map (volumes.py).

Every volume is built by one system: the front matter of Bible ch. 99 with the series map as a spread, then the
volume's units in the order of the map (the first volume's Muqaddima and introduction; a bab or the reference by
one builder, as threshold, opener and chapters; the programme of the second bab; the book's closing; the reference's
appendices and closing lists), and the colophon that hands the reader to the next volume. The page types and the machinery of the notes are the
opening's (opening.py); the lesson elements are set as the Bible sets them (part eight, §٣):

    the example         a line in the text, its code small in the margin
    the models          the graded speeches in one frame, each under its grade's mark, not in stacked boxes
    the rule            a thin gold rule at the start, no ground
    the situation card  Plex lines above the example or the dialogue, not a coloured table
    the dialogue        a play text: the speaker in Plex in a side column, the speech in Amiri, the line number faint
    the voice drill     a frame on a deeper pearl
    the exercises       numbered cards at the chapter's end
    the mastery         its own panel on the assessment page
    the review tags     visible in the proof, and counted; none may reach the edition

The glyphs of the lessons (✔ ✘ ◐ ▣ ① ② ③ ④) are in none of the book's faces: they are drawn, as «←» is, so no system
font enters the page; ↑ and ↓ are set in Plex.

    python3 volume.py N             writes ../Volume-NN_<name>_Final-Proof.pdf: no slug, no proof line, the edition's metadata
    python3 volume.py N --review    writes ../Volume-NN_<name>_Proof.pdf, slugged «نسخة المراجعة» on every page
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402
import cover2 as C2  # noqa: E402
import frontmatter as FM  # noqa: E402
import geometry as G  # noqa: E402
import heads as H  # noqa: E402
import ids as IDS  # noqa: E402
import opening as O  # noqa: E402
import proto2 as P2  # noqa: E402
from paths import AUTHOR_WORD, INTRO, OPENING  # noqa: E402
from volumes import APPENDIX, BOOK, PROGRAM, VOL_OF_BAB, VOLUMES, unit_files  # noqa: E402

AR = O.AR
ORD = O.ORD
PROOF_DATE = "٢٥ سبتمبر ٢٠٢٦م"


def out_path(n, review=False):
    """The volume's file: the final proof by default; the review proof (slugged «نسخة المراجعة») on request."""
    base = f"Volume-{n:02d}_{LATIN[n]}"
    return HERE.parent / (base + ("_Proof.pdf" if review else "_Final-Proof.pdf"))


LATIN = {1: "Al-Usul", 2: "Al-Lisan", 3: "Al-Ibara", 4: "Al-Bayan", 5: "Al-Maqam", 6: "Al-Adab", 7: "Al-Hiwar",
         8: "Al-Majalis-wal-Minbar", 9: "Al-Muassasa", 10: "Al-Tamkin", 11: "Marji-al-Mutakallim"}

# ------------------------------------------------------------------------------------------------ the drawn glyphs

def _svg(body, cls):
    return f'<svg class="gl {cls}" viewBox="0 0 10 10" aria-hidden="true">{body}</svg>'


GLYPHS = {
    "✔": _svg('<path d="M1.7 5.4 L4.1 7.8 L8.5 2.4" fill="none" stroke="currentColor" stroke-width="1.4" '
              'stroke-linecap="round" stroke-linejoin="round"/>', "ok"),
    "✘": _svg('<path d="M2.4 2.4 L7.6 7.6 M7.6 2.4 L2.4 7.6" fill="none" stroke="currentColor" stroke-width="1.4" '
              'stroke-linecap="round"/>', "no"),
    "◐": _svg('<circle cx="5" cy="5" r="3.6" fill="none" stroke="currentColor" stroke-width=".9"/>'
              '<path d="M5 1.4 A3.6 3.6 0 0 0 5 8.6 Z" fill="currentColor"/>', "mid"),
    "▣": _svg('<rect x="1.3" y="1.3" width="7.4" height="7.4" fill="none" stroke="currentColor" stroke-width=".9"/>'
              '<rect x="3.5" y="3.5" width="3" height="3" fill="currentColor"/>', "sq"),
    "ﷺ": '<span class="salla">ﷺ</span>',
    "●": _svg('<circle cx="5" cy="5" r="3.6" fill="currentColor"/>', "sev s1"),
    "◔": _svg('<circle cx="5" cy="5" r="3.6" fill="none" stroke="currentColor" stroke-width=".9"/>'
              '<path d="M5 5 V1.4 A3.6 3.6 0 0 1 8.6 5 Z" fill="currentColor"/>', "sev s3"),
    "○": _svg('<circle cx="5" cy="5" r="3.6" fill="none" stroke="currentColor" stroke-width=".9"/>', "sev s4"),
    "≠": _svg('<path d="M1.8 3.8 H8.2 M1.8 6.4 H8.2 M6.6 1.6 L3.4 8.6" fill="none" stroke="currentColor" stroke-width=".9" '
              'stroke-linecap="round"/>', "ne"),
    "↑": '<span class="gp">↑</span>',
    "↓": '<span class="gp">↓</span>',
}
for _k, (_c, _n) in enumerate(zip("①②③④", "١٢٣٤"), 1):
    GLYPHS[_c] = f'<span class="gm g{_k}">{_n}</span>'
_GLYPH_RE = re.compile("[" + "".join(GLYPHS) + "]")


def glyphs(html):
    return _GLYPH_RE.sub(lambda m: GLYPHS[m.group(0)], html)


# ------------------------------------------------------------------------------------------------ the lesson styles

LESSON_CSS = r"""
/* a heading never ends a page: it travels with the first grade of the models (the frame runs on unbroken after it),
   and a panel's title with the panel's first block (keep_headings) */
/* a short table is never broken, so its head never stays alone at the foot of a page; a long one breaks with its head repeated */
div.tblk { break-inside: avoid; }
.grades.gfirst { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.grades.gcont { margin-top: 0; padding-top: 0; border-top: .35pt solid #E2DACB; }
.gl { display: inline-block; width: .8em; height: .8em; vertical-align: -.06em; margin: 0 .4mm; overflow: visible; }
.gl.ok { color: var(--sapphire-2); } .gl.no { color: var(--crimson); } .gl.mid { color: var(--gold-ink); } .gl.sq { color: var(--sapphire); }
.gl.s1 { color: var(--crimson); } .gl.s3 { color: var(--gold-ink); } .gl.s4 { color: var(--ink-3); } .gl.ne { color: var(--ink-2); }
/* code spans of the manuscript (the marks of the voice drills) are set in Plex, never in a system face */
code { font: 500 .92em "IBM Plex Sans Arabic"; color: var(--gold-ink); background: none; }
/* the glossary and the bibliography of the reference */
dl.gloss { margin: 3mm 0; } dl.gloss > div { padding: 1.8mm 0; border-bottom: .35pt solid #E2DACB; break-inside: avoid; }
dl.gloss dt { font: 600 12pt/1.5 "Changa"; color: var(--sapphire); }
dl.gloss dt .en { font: 400 9pt "Source Serif 4"; color: var(--ink-3); margin-right: 3mm; direction: ltr; unicode-bidi: isolate; }
dl.gloss dd { margin: .6mm 0 0; font: 400 12pt/1.75 "Scheherazade New"; color: var(--ink-2); }
ul.biblio { list-style: none; padding: 0; } ul.biblio > li { padding-right: 6mm; text-indent: -6mm; margin: 0 0 1.4mm; font-size: 11.8pt; line-height: 1.7; }
ul.biblio > li::before { content: none; } ul.biblio b { color: var(--sapphire); }
.gm { display: inline-flex; align-items: center; justify-content: center; width: 1.32em; height: 1.32em; box-sizing: border-box;
  border-radius: 50%; border: .6pt solid currentColor; font: 700 max(.74em, 8.2pt)/1 "Amiri"; padding-top: .14em; min-width: 11.5pt; min-height: 11.5pt; vertical-align: .06em; margin: 0 .5mm; }
.gm.g1 { color: var(--ruby); } .gm.g2 { color: var(--gold-ink); } .gm.g3 { color: var(--sapphire); }
.gm.g4 { color: #F4ECD9; background: var(--sapphire); border-color: var(--sapphire); }
.gp { font-family: "IBM Plex Sans Arabic"; font-weight: 500; color: var(--gold-ink); }
/* ﷺ in a line set in Changa (headings, bands, the contents, the posters): Changa has no glyph for it */
h1 .salla, h2 .salla, h3 .salla, h4 .salla, .chap-band .salla, .toc2 .salla, .poster .salla, .sm .salla, .k .salla, .t .salla,
.card .ch .salla, .pl .who .salla { font-family: "Amiri"; font-weight: 400; }
/* the review tags of the proof: visible, never mistaken for the text */
.rv { font: 400 8pt/1.5 "IBM Plex Sans Arabic"; color: var(--crimson); background: #F6E7E4; padding: .2mm 1.2mm; border-radius: .6mm;
  -webkit-box-decoration-break: clone; box-decoration-break: clone; }
/* the chapter of a bab: its scope under the band, its sections, its headings */
p.scope { font: 400 9pt/1.7 "IBM Plex Sans Arabic"; color: var(--ink-3); text-align: right; text-indent: 0; margin: 0 0 3mm;
  padding-bottom: 2.4mm; border-bottom: .4pt solid #DCD6CA; }
.chap-open > p.scope:first-child { font-size: 9pt; line-height: 1.7; }
h2.sec { margin: 0 0 6mm; padding-top: 1mm; break-after: avoid; }
h2.sec.brk { break-before: page; }
h2.sec .k { display: flex; gap: 3mm; align-items: center; font: 300 10pt/1 "Changa"; color: var(--gold-ink); letter-spacing: .3pt; margin-bottom: 2.4mm; }
h2.sec .k i { flex: 1; border-top: .45pt solid var(--gold); }
h2.sec .t { display: block; font: 700 18pt/1.4 "Changa"; color: var(--sapphire); text-wrap: pretty; }
h2.sec.lite { margin: 2mm 0 3.4mm; }
h2.sec.lite .t { font-size: 15pt; }
h4 { font: 600 12.6pt/1.45 "Changa"; color: var(--sapphire-2); margin: 5mm 0 1.6mm; break-after: avoid; }
h4 + p, h4 + ol, h4 + ul { text-indent: 0; }
.chap-open h3 + p, .chap-open h4 + p { text-indent: 0; }
/* the panels of the lesson: objectives, the opening question, the summary, the mastery, the trainer */
.panel { margin: 5mm 0; padding: 3.2mm 5mm 3.6mm; break-inside: avoid; }
.panel > h3, .panel > h4, .panel > .phk > h3 { margin: 0 0 1.6mm; font: 600 10.6pt/1.4 "Changa"; color: var(--gold-ink); letter-spacing: .2pt; }
.panel > h3::after, .panel > .phk > h3::after { content: none; }
.panel.obj { background: var(--paper-2); border-top: .8pt solid var(--gold); break-inside: auto; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
.panel.obj ol > li, .panel.obj p { font-size: 12.2pt; line-height: 1.75; }
.panel.oq { border-right: 1.4pt solid var(--sapphire-2); background: #F1F2F6; }
.panel.oq p { color: var(--ink); }
.panel.mastery { border: .6pt solid var(--gold); background: var(--paper); padding: 4mm 6mm 4.4mm; }
.panel.mastery > h3, .panel.mastery > .phk > h3 { font: 700 12pt/1.4 "Changa"; color: var(--sapphire); }
.panel.mastery ul { list-style: none; padding: 0; margin: 1mm 0 0; counter-reset: m; }
.panel.mastery ul > li { counter-increment: m; display: grid; grid-template-columns: 7mm 1fr; padding: 1.8mm 0; border-top: .35pt solid #E2DACB; margin: 0; }
.panel.mastery ul > li::before { content: counter(m, arabic-indic); position: static; width: auto; height: auto; transform: none; background: none;
  font: 700 11pt/1.6 "Amiri"; color: var(--gold-ink); }
.trainer { margin: 7mm 0 2mm; padding: 4mm 5.5mm 4mm; background: var(--paper-2); border-right: 1.4pt solid var(--gold); }
.trainer > h3, .trainer > .phk > h3 { margin-top: 0; font: 600 12pt/1.4 "Changa"; color: var(--gold-ink); }
.trainer > h3::after, .trainer > .phk > h3::after { content: none; }
.trainer p, .trainer li { font-size: 11.8pt; line-height: 1.75; }
.trainer table { margin-top: 2mm; }
/* the example: a line in the text, its code small in the margin (Bible, part eight, §٣) */
.exm { position: relative; margin: 3.2mm 0 3.6mm; break-inside: avoid; }
.exm .exh { display: flex; justify-content: space-between; align-items: baseline; gap: 4mm; margin-bottom: .4mm; }
.exm .exid { font: 400 7.8pt/1.3 "IBM Plex Sans Arabic"; color: #9A9282; letter-spacing: .15pt; white-space: nowrap; flex: none; }
.exm .exg { font: 400 9.4pt/1.6 "IBM Plex Sans Arabic"; color: var(--ink-3); }
.exl { display: grid; grid-template-columns: 5.2mm 1fr; align-items: baseline; margin: .5mm 0; }
.exl .mk .gl { width: .92em; height: .92em; }
.exl .tx { font: 400 13pt/1.8 "Scheherazade New"; text-align: right; }
.exl.no .tx { color: var(--ink-2); }
.ctx { font: 400 9.4pt/1.6 "IBM Plex Sans Arabic"; color: var(--ink-3); }
.sd { font-size: .86em; color: var(--ink-3); }
/* the graded models: one frame, each speech under the mark of its grade */
.grades { margin: 5mm 0 6mm; border-top: .8pt solid var(--gold); border-bottom: .4pt solid var(--gold); padding: 1mm 0; }
.grade { display: grid; grid-template-columns: 11mm 1fr; column-gap: 2mm; padding: 3mm 0 3.2mm; }
.grade + .grade { border-top: .35pt solid #E2DACB; }
.grade > .gmk { padding-top: 1.2mm; text-align: center; }
.grade > .gmk .gm { font-size: 16pt; width: 1.36em; height: 1.36em; }
.grade > .gbd > p:first-child { text-indent: 0; }
.grade > .gbd > p:first-child strong { font: 600 11.2pt/1.5 "Changa"; color: var(--sapphire); }
.grade.g1 > .gbd > p:first-child strong { color: var(--ruby); }
.grade.g2 > .gbd > p:first-child strong { color: var(--gold-ink); }
.grade blockquote { margin: 1.6mm 0 2mm; padding: 0 4mm 0 0; border-right: 1.2pt solid var(--gold); break-inside: auto; }
.grade.g1 blockquote { border-right-color: var(--ruby-2); }
.grade.g3 blockquote, .grade.g4 blockquote { border-right-color: var(--sapphire); }
.grade blockquote p { font: 400 13.4pt/1.85 "Amiri"; color: var(--ink); text-indent: 0; }
.grade ul > li { font-size: 12.4pt; }
/* the rule, the warning, the definition, the note to the trainer: a long one may run on to the next page */
blockquote.rule, blockquote.warn, blockquote.defn, blockquote.tr, blockquote.note { break-inside: auto; orphans: 2; widows: 2; }
.chap-open h3, .lesson-t h4 { break-after: avoid; }
blockquote.rule { border-right: 1pt solid var(--gold); padding: .6mm 5mm .8mm 0; margin: 5mm 0; }
blockquote.rule p { font: 400 13.2pt/1.85 "Scheherazade New"; color: var(--ink); text-indent: 0; }
blockquote.rule p > strong:first-child { font: 600 10.6pt/1.5 "Changa"; color: var(--gold-ink); margin-left: 1.4mm; }
blockquote.warn { border-right: 1pt solid var(--crimson); padding: .6mm 5mm .8mm 0; margin: 5mm 0; }
blockquote.warn p { font: 400 12.6pt/1.8 "Scheherazade New"; color: var(--ink-2); text-indent: 0; }
blockquote.warn p > strong:first-child { font: 600 10.4pt/1.5 "Changa"; color: var(--crimson); margin-left: 1.4mm; }
blockquote.defn { border-top: .6pt solid var(--gold); border-bottom: .4pt solid var(--gold); padding: 2.6mm 2mm 2.8mm; margin: 5mm 0; }
blockquote.defn p { font: 400 13.4pt/1.85 "Scheherazade New"; color: var(--sapphire); text-indent: 0; text-align: center; text-wrap: balance; }
blockquote.defn p > strong:first-child { display: block; font: 600 10.4pt/1.5 "Changa"; color: var(--gold-ink); margin-bottom: .6mm; }
blockquote.tr { background: var(--paper-2); padding: 2.6mm 5mm 2.8mm; margin: 5mm 0; }
blockquote.tr p { font: 400 11.2pt/1.75 "IBM Plex Sans Arabic"; color: var(--ink-2); text-indent: 0; text-align: right; }
blockquote.tr p > strong:first-child { font: 600 10pt/1.5 "Changa"; color: var(--gold-ink); margin-left: 1.4mm; }
blockquote.speech p { font: 400 13.4pt/1.85 "Amiri"; color: var(--ink); text-indent: 0; }
blockquote.speech { border-right: 1.2pt solid var(--gold); padding: 0 4.5mm 0 0; break-inside: auto; }
blockquote.lead { margin: 2mm 0 6mm; text-align: center; }
blockquote.lead p { font: 400 14.6pt/1.8 "Scheherazade New"; color: var(--ink-2); text-align: center; text-indent: 0; }
blockquote.lead p strong { display: block; font: 700 19pt/1.5 "Changa"; color: var(--sapphire); margin-top: 1mm; }
blockquote.note p { font: 400 12.4pt/1.8 "Scheherazade New"; color: var(--ink-2); text-indent: 0; }
blockquote.note { border-right: .6pt solid #CFC5B1; padding: 0 4.5mm 0 0; }
/* the situation card: Plex lines, not a coloured table */
.card { margin: 4mm 0 4.6mm; padding: 2.2mm 0 2.4mm; border-top: .6pt solid var(--gold); border-bottom: .35pt solid var(--gold); break-inside: avoid; }
.card .ch { font: 600 9.2pt/1.4 "Changa"; color: var(--sapphire); margin-bottom: 1mm; display: flex; gap: 1.6mm; align-items: center; }
.card .ch .gl { width: 1em; height: 1em; }
.card .cf { font: 400 9pt/1.75 "IBM Plex Sans Arabic"; color: var(--ink-2); text-align: right; }
.card .cf b { font-weight: 600; color: var(--ink); margin-left: 1mm; }
.card .cf + .cf { margin-top: .2mm; }
.card .n { font: 700 10pt/1 "Amiri"; color: var(--sapphire); }
/* the dialogue: a play text */
.play { margin: 4mm 0 5mm; border-top: .6pt solid var(--gold); border-bottom: .35pt solid var(--gold); padding: 1.6mm 0; }
.pl { display: grid; grid-template-columns: 7mm 21mm 1fr; column-gap: 2.4mm; align-items: baseline; padding: .9mm 0; break-inside: avoid; }
.pl .ln { font: 400 7.8pt/1 "IBM Plex Sans Arabic"; color: #978E7E; text-align: right; }
.pl .who { font: 600 8.8pt/1.5 "IBM Plex Sans Arabic"; color: var(--sapphire); }
.pl .say { font: 400 13.2pt/1.8 "Amiri"; color: var(--ink); text-align: right; }
.pl .say .sd { font: 400 9.4pt/1.6 "IBM Plex Sans Arabic"; color: var(--ink-3); }
/* the voice drill: a frame on a deeper pearl */
.voice { background: #EAE5DA; border: .5pt solid #D9CBA6; padding: 4mm 6mm; margin: 4mm 0 5mm; break-inside: avoid; }
.voice .vl { font: 400 14pt/2.05 "Scheherazade New"; color: var(--ink); text-align: right; }
.voice .vl strong { color: var(--sapphire); text-decoration: underline; text-decoration-color: var(--gold); text-underline-offset: 1.4mm; }
.voice .ps { color: var(--gold-ink); font-family: "IBM Plex Sans Arabic"; font-weight: 500; margin: 0 .8mm; }
.voice .br { font: 400 8.4pt "IBM Plex Sans Arabic"; color: var(--sapphire-2); }
/* the chapter's exercises: numbered cards */
.ex-card { border: .45pt solid #D9CBA6; background: var(--paper); margin: 3.2mm 0; padding: 2.6mm 5mm 3mm; break-inside: auto; }
.ex-card > h4 { break-after: avoid; }
.ex-card > h4 { margin: 0 0 1.4mm; display: flex; gap: 2.6mm; align-items: baseline; color: var(--sapphire); font-size: 11.8pt; }
.ex-card > h4 .no { font: 700 13pt/1 "Amiri"; color: var(--gold-ink); }
.ex-card ol > li, .ex-card p, .ex-card ul > li { font-size: 12.2pt; line-height: 1.75; }
ul.runon, ol.runon { margin-top: 0; }
/* the self-check */
ul.check { list-style: none; padding: 0 1mm 0 0; }
ul.check > li { position: relative; padding-right: 6.4mm; }
ul.check > li::before { content: ""; position: absolute; right: 0; top: 2.6mm; width: 3mm; height: 3mm; transform: none;
  border: .6pt solid var(--gold-ink); background: none; box-sizing: border-box; }
/* the tables of the lessons: Plex, a quieter head than the opening's; a long one runs on, its head repeated */
.lesson-t table { break-inside: auto; }
.lesson-t thead { display: table-header-group; }
.lesson-t tr { break-inside: avoid; }
.lesson-t table th { background: var(--paper-2); color: var(--sapphire); border-bottom: .8pt solid var(--gold); font-weight: 600; }
.lesson-t table td { font-size: 8.8pt; }
.lesson-t table tr:nth-child(even) td { background: none; }
/* the figure */
.fig { margin: 6mm 0 6.4mm; break-inside: avoid; }
.fig .ft { font: 600 11pt/1.4 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--sapphire); text-align: center; margin-bottom: 3mm; }
.fig .fc { font: 400 10.2pt/1.6 "Scheherazade New"; color: var(--ink-3); text-align: center; margin-top: 2.6mm; text-wrap: balance; }
.fig .fc b { font: 400 8.6pt "Changa"; color: var(--gold-ink); margin-left: 1.4mm; }
"""


# ------------------------------------------------------------------------------------------------ the figure of the introduction

def spectrum():
    """The spectrum of Arabic (Bible, part eight, §٤: المدخل، ف١): from the heritage tongue to the colloquial, the
    situations placed on it; the professional styles are colours of the modern fuṣḥā, not a level of their own.
    Sapphire and sand only; labels in Plex, the title in Kufam; no shadow, no gradient."""
    zones = [("العربية التراثية", "نقرؤها ونحفظها ونستشهد بها", "#0C2766", "#F4ECD9"),
             ("الفصحى المعاصرة المكتوبة", "الكتاب والصحيفة والمراسلة", "#2B4A8F", "#F4ECD9"),
             ("الفصحى المنطوقة", "المحاضرة والندوة والمقابلة والخطبة", "#C9A95C", "#1C1915"),
             ("العاميات", "البيت والسوق", "#EFECE5", "#4A443C")]
    w, x = 122.0, 122.0
    cells, under = [], []
    for name, where, fill, ink in zones:
        cw = w / 4
        x -= cw
        stroke = ' stroke="#C9A95C" stroke-width=".4"' if fill == "#EFECE5" else ""
        cells.append(f'<rect x="{x:.2f}" y="15" width="{cw:.2f}" height="14"{stroke} fill="{fill}"/>')
        under.append(f'<div class="fz" style="right:{w - x - cw:.2f}mm;width:{cw:.2f}mm"><b style="color:{ink}">{name}</b></div>'
                     f'<div class="fw" style="right:{w - x - cw:.2f}mm;width:{cw:.2f}mm">{where}</div>')
    field = w / 4 * 2, w / 4 * 3          # the book's field: the spoken fuṣḥā (third zone from the right)
    lx0, lx1 = w - field[1], w - field[0]
    svg = (f'<svg viewBox="0 0 {w} 55" style="position:absolute;top:0;left:0;width:{w}mm;height:55mm">'
           f'{"".join(cells)}'
           f'<path d="M{lx0 + 1.5:.2f} 12.2 V10 H{lx1 - 1.5:.2f} V12.2" fill="none" stroke="#8A6A1F" stroke-width=".45"/>'
           f'<line x1="{w - 1:.2f}" y1="4" x2="1" y2="4" stroke="#C9A95C" stroke-width=".35"/>'
           f'<path d="M3.2 2.4 L1 4 L3.2 5.6" fill="none" stroke="#C9A95C" stroke-width=".35"/>'
           f'<rect x="{w / 4:.2f}" y="42.5" width="{w / 2:.2f}" height="10.5" fill="none" stroke="#2B4A8F" stroke-width=".4" stroke-dasharray="1.2 .9"/>'
           f'</svg>')
    labels = (f'<div class="fe" style="right:0">من لسان التراث</div><div class="fe" style="left:0">إلى لسان البيت والسوق</div>'
              f'<div class="ff" style="right:{w - lx1:.2f}mm;width:{lx1 - lx0:.2f}mm">ميدان هذا الكتاب</div>'
              f'<div class="fp" style="right:{w / 4:.2f}mm;width:{w / 2:.2f}mm">الأساليب المهنية: ألوانٌ للفصحى المعاصرة في الجامعة والإعلام والإدارة والمنبر</div>')
    css = ('<style>.fsp { position: relative; width: 122mm; height: 55mm; margin: 0 auto; }'
           '.fsp .fz { position: absolute; top: 15mm; height: 14mm; display: flex; align-items: center; justify-content: center; text-align: center; }'
           '.fsp .fz b { font: 600 8.4pt/1.25 "IBM Plex Sans Arabic"; padding: 0 1.4mm; }'
           '.fsp .fw { position: absolute; top: 30.6mm; font: 400 8pt/1.35 "IBM Plex Sans Arabic"; color: var(--ink-3); text-align: center; padding: 0 1mm; box-sizing: border-box; }'
           '.fsp .fe { position: absolute; top: 0; font: 300 8pt/1 "Changa"; color: var(--gold-ink); background: var(--paper); padding: 0 1.6mm; }'
           '.fsp .ff { position: absolute; top: 6.4mm; text-align: center; font: 500 8.2pt/1 "Changa"; color: var(--gold-ink); }'
           '.fsp .fp { position: absolute; top: 42.5mm; height: 10.5mm; display: flex; align-items: center; justify-content: center; text-align: center; '
           'font: 400 8pt/1.4 "IBM Plex Sans Arabic"; color: var(--sapphire-2); padding: 0 3mm; box-sizing: border-box; }</style>')
    return (f'<div class="fig">{css}<div class="ft">طيف مستويات العربية</div><div class="fsp">{svg}{"".join(under)}{labels}</div>'
            f'<div class="fc"><b>الرسم ١</b>الطيف متصلٌ لا غرفٌ منفصلة: يتنقّل المتكلّم الواحد بين مواضعه في الحديث الواحد؛ '
            f'وميدان هذا الكتاب الفصحى المنطوقة.</div></div>')


FIGURES = {"طيف المستويات": spectrum}


def with_figures(md):
    return re.sub(r"<!--\s*figure:\s*(.+?)\s*-->", lambda m: "\n\n" + FIGURES[m.group(1)]() + "\n\n", md)


# ------------------------------------------------------------------------------------------------ the lessons, from markdown

REVIEW = re.compile(r"\*\[([^\]]+)\]\*")
EXID = re.compile(r"^(\[(?:ب|ر)[٠-٩]+-ف[٠-٩]+-مث[٠-٩]+[أ-ي]?\])\s*(.*)$")
MARKS = ("✔", "✘", "◐")


def inline(text):
    """A line's inline markdown (bold, italics), as HTML without its paragraph."""
    return markdown.markdown(text).removeprefix("<p>").removesuffix("</p>")


def speech_marks(html):
    """Stage directions [..] and a leading context (..) are quieter than the speech."""
    html = re.sub(r"\[([^\]\[]{1,160})\]", r'<span class="sd">[\1]</span>', html)
    return re.sub(r"^\(([^()]{1,200})\)", r'<span class="ctx">(\1)</span>', html)


def examples(md):
    """An example block (its code, then the lines marked ✔ ✘ ◐) becomes the example of the Bible: lines in the text,
    the code small at the head's far end (Chromium keeps nothing in the page's margin). Lines after the marked ones
    are the example's comment, set as a paragraph under it."""
    out = []
    for block in re.split(r"\n{2,}", md):
        lines = block.split("\n")
        m = EXID.match(lines[0].strip())
        rest = lines[1:] if m else lines
        k = 0
        while k < len(rest) and rest[k].strip().startswith(MARKS):
            k += 1
        rows, after = rest[:k], rest[k:]
        if not m and not rows:
            out.append(block)
            continue
        head = ""
        if m:
            gloss = f'<span class="exg">{inline(m.group(2))}</span>' if m.group(2).strip() else "<span></span>"
            head = f'<div class="exh">{gloss}<span class="exid">{m.group(1)}</span></div>'
        body = []
        for l in rows:
            l = l.strip()
            kind = {"✔": "ok", "✘": "no", "◐": "mid"}[l[0]]
            body.append(f'<div class="exl {kind}"><span class="mk">{l[0]}</span><div class="tx">{speech_marks(inline(l[1:].strip()))}</div></div>')
        out.append(f'<div class="exm">{head}{"".join(body)}</div>')
        if after:
            out.append("\n".join(after))
    return "\n\n".join(out)


def voice(bq):
    """A voice drill keeps its lines; its marks of pause and breath are set apart from the words."""
    lines = [l for l in bq.decode_contents().replace("<p>", "").replace("</p>", "\n").split("\n") if l.strip()]
    rows = []
    for l in lines:
        l = re.sub(r"(//|(?<![/<])/(?![/>]))", r'<span class="ps">\1</span>', l)
        l = l.replace("(ت)", '<span class="br">(ت)</span>')
        rows.append(f'<div class="vl">{l.strip()}</div>')
    new = BeautifulSoup(f'<div class="voice">{"".join(rows)}</div>', "html.parser")
    bq.replace_with(new)


def card(p, table):
    """بطاقة المقام: the table's rows as Plex lines under the card's mark."""
    fields = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) < 2:
            continue
        k, v = tds[0].get_text(" ", strip=True), tds[1].decode_contents().strip()
        v = re.sub(r"([٠-٩]+(?:–[٠-٩]+)?)", r'<span class="n">\1</span>', v)
        fields.append(f'<div class="cf"><b>{k}:</b> {v}</div>')
    head = f'<div class="ch">▣<span>{p.get_text(" ", strip=True).lstrip("▣").strip()}</span></div>' if p is not None else ""
    new = BeautifulSoup(f'<div class="card{"" if p is not None else " bare"}">{head}{"".join(fields)}</div>', "html.parser")
    table.replace_with(new)
    if p is not None:
        p.decompose()


def play(table):
    rows = []
    for tr in table.find_all("tr")[1:]:
        tds = tr.find_all("td")
        if len(tds) != 3:
            return
        ln, who, say = tds[0].get_text(strip=True), tds[1].decode_contents().strip(), tds[2].decode_contents().strip()
        say = re.sub(r"\[([^\]\[]{1,160})\]", r'<span class="sd">[\1]</span>', say)
        rows.append(f'<div class="pl"><span class="ln">{ln}</span><span class="who">{who}</span><span class="say">{say}</span></div>')
    table.replace_with(BeautifulSoup(f'<div class="play">{"".join(rows)}</div>', "html.parser"))


def wrap_until(soup, start, cls, stop):
    """Wrap `start` and its following siblings until one satisfies `stop`, in a div of class `cls`."""
    box = soup.new_tag("div", attrs={"class": cls})
    start.insert_before(box)
    node = start
    while node is not None:
        nxt = node.find_next_sibling()
        box.append(node.extract())
        node = nxt
        if node is None or stop(node):
            break
    return box


def heading_level(node):
    return node.name if node.name in ("h2", "h3", "h4") else None


def loosen_lists(md):
    """Python-Markdown opens a list only after a blank line; the manuscript often sets one straight under its lead
    line («**تحليل الأخطاء:**» then «- …»). A blank line is put there, never inside a list or a table."""
    out, prev = [], ""
    for line in md.split("\n"):
        item = re.match(r"^\s*(?:[-*]\s|[0-9]+\.\s)", line)
        if item and prev.strip() and not re.match(r"^\s*(?:[-*]\s|[0-9]+\.\s|\|)", prev) and not prev.startswith((" ", "\t")):
            out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)


def keep_headings(soup):
    """A heading never ends a page: it travels with the headings right under it and with the start of what follows
    (a short block whole; a long list by its first two items; a long table or block after it is left to break)."""
    for h in soup.find_all(["h3", "h4"]):
        if h.parent is None or any(c in (h.parent.get("class") or []) for c in ("keep",)):
            continue
        if h.parent.name == "div" and h.find_previous_sibling() is None \
                and any(c in (h.parent.get("class") or []) for c in ("panel", "summary", "trainer", "ex-card")):
            nxt = h.find_next_sibling()                     # a panel's own title stays with the panel's first block
            if "ex-card" in (h.parent.get("class") or []) or nxt is None:
                continue
            items = nxt.find_all("li", recursive=False) if nxt.name in ("ul", "ol") else []
            if nxt.name in ("p", "ul", "ol", "blockquote") and len(nxt.get_text(" ", strip=True)) < 600:
                keep = soup.new_tag("div", attrs={"class": "keep phk"})
                h.insert_before(keep)
                keep.append(h.extract())
                keep.append(nxt.extract())
            elif len(items) > 2:                            # a long list: the title with its first two items
                keep = soup.new_tag("div", attrs={"class": "keep phk"})
                h.insert_before(keep)
                keep.append(h.extract())
                head = soup.new_tag(nxt.name, attrs={k: v for k, v in nxt.attrs.items()})
                for li in items[:2]:
                    head.append(li.extract())
                keep.append(head)
                if nxt.name == "ol":
                    nxt["start"] = str(int(nxt.get("start", 1)) + 2)
                nxt["class"] = (nxt.get("class") or []) + ["runon"]
            continue
        run = [h]
        nxt = h.find_next_sibling()
        while nxt is not None and nxt.name in ("h3", "h4"):
            run.append(nxt)
            nxt = nxt.find_next_sibling()
        if nxt is None or nxt.name == "h2":
            continue
        keep = soup.new_tag("div", attrs={"class": "keep"})
        h.insert_before(keep)
        for x in run:
            keep.append(x.extract())
        cls = nxt.get("class") or []
        text = len(nxt.get_text(" ", strip=True))
        first = nxt.find("div", class_="grade", recursive=False) if "grades" in cls else None
        if first is not None and len(first.get_text(" ", strip=True)) < 900 and len(nxt.find_all("div", class_="grade", recursive=False)) > 1:
            frame = soup.new_tag("div", attrs={"class": "grades gfirst"})
            frame.append(first.extract())
            keep.append(frame)
            nxt["class"] = cls + ["gcont"]
            continue
        if text < 360 and (nxt.name in ("p", "blockquote", "ul", "ol") or "card" in cls or "exm" in cls) \
                or "ex-card" in cls and text < 900:
            keep.append(nxt.extract())
        elif nxt.name in ("ul", "ol") and len(nxt.find_all("li", recursive=False)) > 2:
            head = soup.new_tag(nxt.name, attrs={k: v for k, v in nxt.attrs.items()})
            for li in nxt.find_all("li", recursive=False)[:2]:
                head.append(li.extract())
            keep.append(head)
            if nxt.name == "ol":
                nxt["start"] = str(int(nxt.get("start", 1)) + 2)
            nxt["class"] = (nxt.get("class") or []) + ["runon"]
        elif nxt.name == "p" and text < 900:
            keep.append(nxt.extract())


def lesson_html(md, breaks=True):
    """A bab's chapter (or its opener) as the page carries it. breaks: a lesson opens its page."""
    md = re.sub(r"<!--\s*head:.*?-->\s*", "", md)          # the short head is the running head's, never the page's
    # the notes, as the Muqaddima sets them: the call hugs what it documents, the punctuation follows, and each note
    # floats to the foot of the page of its call (Paged.js)
    notes = dict(re.findall(r"^\[\^(\d+)\]:\s*(.+)$", md, re.M))
    md = re.sub(r"^\[\^\d+\]:.*$", "", md, flags=re.M)
    md = re.sub(r"\[\^(\d+)\]", lambda m: f"⟦{m.group(1)}⟧", md)
    md = re.sub(r"([.،؛:])((?:⟦\d+⟧)+)", r"\2\1", md)
    md = loosen_lists(IDS.printed(md))
    md = re.sub(r"^---+\s*$", "", md, flags=re.M)
    md = REVIEW.sub(lambda m: f'<span class="rv">{m.group(1)}</span>', md)
    md = re.sub(r"^\*\((الباب [^)]*)\)\*\s*$", r'<p class="scope">\1</p>', md, flags=re.M)
    md = examples(md)
    md = re.sub(r"^- \[ \] ", "- ⊡", md, flags=re.M)
    soup = BeautifulSoup(markdown.markdown(md, extensions=["tables"]), "html.parser")
    O.latinize(soup)
    # sections: a lesson or the chapter's application opens a page, under its kicker
    first = True
    for h in soup.find_all("h2"):
        t = h.get_text(" ", strip=True)
        prev = h.find_previous_sibling()
        lite = t == "مدخل الفصل" or first or (prev is not None and prev.name == "h2")   # a heading right under another keeps its page
        m = re.match(r"^((?:الدرس|اليوم) [^:]+):\s*(.+)$", t)
        k, title = (m.group(1), m.group(2)) if m else ("", t)
        h["class"] = ["sec"] + (["lite"] if lite or not breaks else ["brk"])
        h.clear()
        if k:
            h.append(BeautifulSoup(f'<span class="k"><span>{k}</span><i></i></span>', "html.parser"))
        h.append(BeautifulSoup(f'<span class="t">{title}</span>', "html.parser"))
        first = False
    # the lead question of a bab's opener
    for bq in soup.find_all("blockquote"):
        t = bq.get_text(" ", strip=True)
        if t.startswith("السؤال الذي يجيب عنه"):
            bq["class"] = ["lead"]
    # the graded models: from a paragraph opening with ①–④ to the next grade, heading or table
    grades = [p for p in soup.find_all("p") if p.find("strong") and re.match(r"^\s*[①②③④]", p.get_text())]
    for p in grades:
        if p.parent is None or "gbd" in (p.parent.get("class") or []):
            continue
        g = "①②③④".index(p.get_text().strip()[0]) + 1
        box = wrap_until(soup, p, f"grade g{g}", lambda n: heading_level(n) or n.name == "table"
                         or (n.name == "p" and re.match(r"^\s*[①②③④]", n.get_text()) and n.find("strong"))
                         or "exm" in (n.get("class") or []))
        body = soup.new_tag("div", attrs={"class": "gbd"})
        for c in list(box.children):
            body.append(c.extract())
        mk = BeautifulSoup(f'<div class="gmk">{"①②③④"[g - 1]}</div>', "html.parser")
        box.append(mk)
        box.append(body)
        lead = body.find("p")
        if lead is not None and lead.find("strong"):
            s = lead.find("strong")
            s.string = re.sub(r"^\s*[①②③④]\s*", "", s.get_text())
    for box in soup.find_all("div", class_="grade"):
        if box.parent is not None and "grades" in (box.parent.get("class") or []):
            continue
        prev = box.find_previous_sibling()
        if prev is not None and "grades" in (prev.get("class") or []):
            prev.append(box.extract())
        else:
            frame = soup.new_tag("div", attrs={"class": "grades"})
            box.insert_before(frame)
            frame.append(box.extract())
    # blockquotes by their lead word
    for bq in soup.find_all("blockquote"):
        if bq.get("class"):
            continue
        t = bq.get_text(" ", strip=True)
        lead = bq.find("strong")
        lw = lead.get_text(strip=True) if lead is not None and bq.get_text().strip().startswith(lead.get_text().strip()) else ""
        if re.search(r"(//|\(ت\))", t) and len(bq.find_all("p")) <= 2:
            voice(bq)
        elif re.match(r"^(ال)?قاعدة", lw):
            bq["class"] = ["rule"]
        elif lw.startswith("للمدرب") or lw.startswith("للمدرّب"):
            bq["class"] = ["tr"]
        elif lw.startswith(("تنبيه", "انتبه", "تحذير")):
            bq["class"] = ["warn"]
        elif lw.startswith("تعريف"):
            bq["class"] = ["defn"]
        elif t.startswith("«") or (bq.parent is not None and "gbd" in (bq.parent.get("class") or [])):
            bq["class"] = ["speech"]
        else:
            bq["class"] = ["note"]
    # tables: the card, the dialogue, and the rest in the lesson's quieter style
    for table in soup.find_all("table"):
        if len(table.find_all("tr")) <= 9 and not (table.parent is not None and "tblk" in (table.parent.get("class") or [])):
            box = soup.new_tag("div", attrs={"class": "tblk"})       # Paged.js keeps a block whole, not a table
            table.insert_before(box)
            box.append(table.extract())
        head = [th.get_text(" ", strip=True) for th in table.find_all("th")]
        prev = table.find_previous_sibling()
        if head[:2] == ["البند", "البيان"]:
            card(prev if prev is not None and prev.name == "p" and prev.get_text().strip().startswith("▣") else None, table)
        elif head and head[0] == "السطر" and len(head) == 3:
            play(table)
    # panels
    for h in soup.find_all("h3"):
        t = h.get_text(" ", strip=True)
        stop = lambda n: heading_level(n) in ("h2", "h3")   # noqa: E731
        if t.startswith("أهداف"):
            wrap_until(soup, h, "panel obj", stop)
        elif t.startswith("سؤال افتتاحي"):
            wrap_until(soup, h, "panel oq", stop)
        elif t == "الخلاصة":
            wrap_until(soup, h, "summary", stop)
        elif t == "معيار الإتقان":
            wrap_until(soup, h, "panel mastery", stop)
        elif t.startswith("للمدرب") or t.startswith("للمدرّب"):
            wrap_until(soup, h, "trainer", lambda n: heading_level(n) == "h2")
    # the exercises: each numbered h4 under «تدريبات الفصل» is a card
    for h in soup.find_all("h3"):
        if not h.get_text(strip=True).startswith("تدريبات"):
            continue
        node = h.find_next_sibling()
        while node is not None and heading_level(node) not in ("h2", "h3"):
            nxt = node.find_next_sibling()
            if node.name == "h4":
                m = re.match(r"^([٠-٩]+)\.\s*(.+)$", node.get_text(" ", strip=True))
                if m:
                    node.clear()
                    node.append(BeautifulSoup(f'<span class="no">{m.group(1)}</span><span>{m.group(2)}</span>', "html.parser"))
                box = wrap_until(soup, node, "ex-card", lambda n: heading_level(n) is not None)
                nxt = box.find_next_sibling()
            node = nxt
    # the self-check
    for ul in soup.find_all("ul"):
        items = ul.find_all("li", recursive=False)
        if items and all(li.get_text().lstrip().startswith("⊡") for li in items):
            ul["class"] = ["check"]
            for li in items:
                for s in li.find_all(string=re.compile("⊡")):
                    s.replace_with(s.replace("⊡", "", 1))
    # the numbered headings of the opening's kind (### ١. …)
    for h in soup.find_all("h3"):
        m = re.match(r"^([٠-٩]+)\.\s*", h.get_text())
        if m and h.string:
            h.string = h.string[m.end():]
            num = soup.new_tag("span", attrs={"class": "hn"}); num.string = m.group(1)
            h.insert(0, num)
    keep_headings(soup)
    html = O.ayat(str(soup).replace("←", O.ARROW))
    soup = BeautifulSoup(html, "html.parser")
    for p in soup.find_all("p"):                             # a paragraph that is only an ayah is displayed
        t = p.get_text().strip()
        if t.startswith("﴿") and len(p.find_all(class_="q")) == 1 and t.endswith(")"):
            p["class"] = ["ayah"]
    html = re.sub(r"⟦(\d+)⟧", lambda m: O.note_span(m.group(1), notes[m.group(1)]), str(soup))
    missing = set(notes) - set(re.findall(r'class="fn-note fn-n(\d+) ', html))
    if missing:
        raise SystemExit(f"notes defined but never called: {sorted(missing, key=int)}")
    return f'<div class="lesson-t">{html}</div>'


# ------------------------------------------------------------------------------------------------ pieces

def doc(css, body, page_css, paged=False):
    return O.doc(css, glyphs(body), LESSON_CSS + page_css, paged)


def flow(css, piece):
    body, bandhtml = piece
    return (doc(css, body, "html, body { background: transparent !important; }", paged="fn-note" in body),
            doc(css, bandhtml, O.FIXED_CSS % dict(w=G.W, h=G.H)))


def title_of(md):
    """The chapter's title and its question: «# الفصل الأول: الكلام وأركانه» then «## لماذا ينجح كلام…»."""
    t = re.search(r"^#\s+(.+)$", md, re.M).group(1)
    t = re.sub(r"\s*\(تابع\)\s*$", "", t)
    title = re.sub(r"^الفصل [^:]+:\s*", "", t)
    sub = re.search(r"^##\s+(.+)$", md, re.M)
    return title, (sub.group(1).strip() if sub else "")


def bab_chapters(n, files=None):
    """{chapter number: [files]} for the bab's chapter files (ف01-أ، ف01-ب …); files: another unit's (the reference)."""
    files = files if files is not None else unit_files(VOL_OF_BAB[n], ("bab", n))
    out = {}
    for f in files:
        m = re.match(r"ف([0-9]+)", f.name)
        if m:
            out.setdefault(int(m.group(1)), []).append(f)
    return files[0] if files and files[0].name.startswith("00-") else None, out


def chapter_md(files):
    """The chapter's files joined: the first gives the title and question; the others continue it. A chapter's notes
    are numbered through all its files, from ١ (Bible, ch. 34 §٣), in the order of their calls."""
    parts, n = [], 0
    for i, f in enumerate(files):
        md = f.read_text(encoding="utf-8")
        md = re.sub(r"^#\s+.+$", "", md, count=1, flags=re.M)
        if i == 0:
            md = re.sub(r"^##\s+.+$", "", md, count=1, flags=re.M)
        body = re.sub(r"^\[\^\d+\]:.*$", "", md, flags=re.M)
        order = list(dict.fromkeys(re.findall(r"\[\^(\d+)\]", body)))
        new = {k: str(n + j + 1) for j, k in enumerate(order)}
        n += len(order)
        md = re.sub(r"\[\^(\d+)\](:?)", lambda m: f"[^{new[m.group(1)]}]{m.group(2)}" if m.group(1) in new else m.group(0), md)
        parts.append(md.strip())
    return "\n\n".join(parts)


def lesson_sections(md):
    """The contents line of a bab chapter: its lessons and its application."""
    out = []
    for m in re.finditer(r"^##\s+(.+)$", md, re.M):
        t = m.group(1).strip()
        if t == "مدخل الفصل":
            continue
        t = re.sub(r"^الدرس [^:]+:\s*", "", t)
        out.append((str(len(out) + 1).translate(AR), t))
    return out


def threshold(kick, big, line):
    """A unit's threshold: a long name («الدبلوماسية والتواصل الرسمي») in the middle size, never squeezed."""
    return O.poster(kick, big, line, kufam=True, mid=len(big) > 14)


def opener_of(files):
    """A bab's opener (or the reference's): its title, label and name, its subtitle, its question, and its body."""
    omd = files[0].read_text(encoding="utf-8")
    title = re.search(r"^#\s+(.+)$", omd, re.M).group(1).strip()
    label, name = [x.strip() for x in title.split(":", 1)]
    lead = re.search(r"^>\s*(السؤال الذي يجيب عنه [^:]+):.*$", omd, re.M)
    question = re.search(r"\*\*(.+?)\*\*", lead.group(0)).group(1)
    sub = re.search(r"^##\s+(.+)$", omd, re.M).group(1)
    body = re.sub(r"^#\s+.+$", "", omd, count=1, flags=re.M)
    body = re.sub(r"^##\s+.+$", "", body, count=1, flags=re.M)
    return title, label, name, sub, f"{lead.group(1)}: {question}", body


def babs_line(n):
    """The title page's line of the volume's units, the babs by their numbers («البابان الثامن والتاسع»)."""
    if n == 1:
        return None
    units = VOLUMES[n - 1]["units"]
    babs = [u[1] for u in units if u[0] == "bab"]
    names = [opener_of(unit_files(n, ("bab", b)))[2] for b in babs]
    if len(babs) == 1:
        line = f"الباب {O.ORD[babs[0]]}: {names[0]}"
    elif len(babs) == 2:
        line = f"البابان {O.ORD[babs[0]]} و{O.ORD[babs[1]]}: {names[0]}، و{names[1]}"
    elif babs:
        line = "الأبواب " + " و".join(O.ORD[b] for b in babs)
    else:
        line = "المرجع الأول: بنك الأخطاء، والملاحق الأربعة، ومسرد المصطلحات، والمصادر والمراجع"
    if ("program",) in units:
        line += "، وملحقه: برنامج النطق اليومي"
    if ("closing",) in units:
        line += "، وخاتمة الكتاب"
    return line


def flat(md):
    """A file whose sections are h2 under its h1: the h1 goes to the band, the sections stay."""
    return re.sub(r"^#\s+.+$", "", md, count=1, flags=re.M).strip()


def numbered(md):
    """The numbered sections (## ٧. الشكر) of an appendix, for its contents line."""
    return [(m.group(1), m.group(2).strip()) for m in re.finditer(r"^##\s+([٠-٩]+)\.\s+(.+)$", md, re.M)]


def unit(css, n, u, pieces, toc, outline, fixed, first=False):
    """One unit of the volume's map (volumes.py) as pieces: a bab or the reference (threshold, opener, chapters), the
    programme of the second bab, the book's closing, an appendix of the reference, or a closing list (the glossary,
    the bibliography). first: the unit that opens the text, numbered from ١."""
    if u[0] in ("bab", "reference"):
        files = unit_files(n, u)
        b = u[1] if u[0] == "bab" else 0
        tag = f"b{b}" if b else "r"
        opener, chapters = bab_chapters(b, files)
        title, label, name, sub, lead, obody = opener_of(files)
        pieces.append(("fixed", doc(css, threshold(label, name, lead), fixed),
                       {"recto": True, "anchor": "main" if first else tag }))
        outline.append((title, "main" if first else tag, 0))
        if first:
            pieces[-1][2]["alias"] = tag
        short = re.search(r"<!--\s*head:\s*(.+?)\s*-->", files[0].read_text(encoding="utf-8"))
        head = [("label", label), ("title", short.group(1) if short else name)]
        ohtml = (f'<section class="chap chap-open"><div class="opener-k"><span>{title}</span><i></i></div>'
                 f'<h2 class="op-t">{"فاتحة الباب" if b else "فاتحة المرجع"}</h2><p class="op-s">{sub}</p>{lesson_html(obody)}</section>')
        oname = "فاتحة الباب" if b else "فاتحة المرجع"
        pieces.append(("cont", doc(css, ohtml, O.CONT_CSS + OPENER_CSS), {"anchor": f"{tag}o", "head": (head, [("title", oname)]), "opens": True}))
        toc.append(("part", "", title))
        toc.append(("e", "", oname, f"{tag}o", []))
        outline.append((oname, f"{tag}o", 1))
        for c, cf in sorted(chapters.items()):
            md = chapter_md(cf)
            first_md = cf[0].read_text(encoding="utf-8")
            ctitle, question = title_of(first_md)
            key = f"{tag}c{c}"
            toc.append(("e", f"الفصل {ORD[c]}", ctitle, key, lesson_sections(md) if b else []))
            outline.append((f"الفصل {ORD[c]}: {ctitle}", key, 1))
            short = re.search(r"<!--\s*head:\s*(.+?)\s*-->", first_md)
            heads = (head, [("label", "الفصل"), ("num", str(c).translate(AR)), ("title", short.group(1) if short else ctitle)])
            body = f'<section class="chap"><div class="chap-open">{lesson_html(md)}</div></section>'
            band = O.band(f"{label}: {name} · الفصل {ORD[c]}", ctitle, question)
            pieces.append(("flow", flow(css, (body, band)), {"anchor": key, "head": heads}))
        return

    if u[0] == "program":
        files = unit_files(n, u)
        md = "\n\n".join(flat(f.read_text(encoding="utf-8")) for f in files)
        kick, title = [x.strip() for x in PROGRAM.split(":", 1)]
        body = f'<section class="chap"><div class="chap-open">{lesson_html(md, breaks=False)}</div></section>'
        pieces.append(("flow", flow(css, (body, O.band(kick, title, ""))),
                       {"recto": True, "anchor": "prog", "head": ([("title", kick)], [("title", "برنامج النطق اليومي")])}))
        toc.append(("part", "", kick))
        toc.append(("e", "", title, "prog", []))
        outline.append((PROGRAM, "prog", 0))
        return

    if u[0] == "closing":
        md = unit_files(n, u)[0].read_text(encoding="utf-8")
        md = re.sub(r"^## ", "### ", md, flags=re.M)
        md = re.sub(r"^# ", "## ", md, count=1, flags=re.M)
        # the book's close opens once, on its band: no threshold repeats its title
        outline.append(("خاتمة الكتاب", "closing-t", 0))
        heads = ([("title", "خاتمة الكتاب")], [("title", "خاتمة الكتاب")])
        for kind, part in O.chapter_parts(md, "خاتمة الكتاب"):
            if kind == "flow":
                pieces.append(("flow", flow(css, part), {"recto": True, "anchor": "closing-t", "head": heads}))
            else:
                pieces.append((kind, doc(css, part, fixed if kind == "fixed" else O.CONT_CSS), {"head": heads}))
        toc.append(("part", "", "خاتمة الكتاب"))
        toc.append(("e", "", "خاتمة الكتاب", "closing-t", O.sections(md)))
        return

    if u[0] in ("app", "back"):
        files = unit_files(n, u)
        raw = "\n\n".join(f.read_text(encoding="utf-8") for f in files)
        h1 = re.search(r"^#\s+(.+)$", raw, re.M).group(1).strip()
        md = "\n\n".join(flat(f.read_text(encoding="utf-8")) if i == 0 else f.read_text(encoding="utf-8") for i, f in enumerate(files))
        if u[0] == "app":
            kick, title = [x.strip() for x in h1.split(":", 1)]
            key, group = f"app-{u[1]}", "الملاحق"
        else:
            kick, title = "الخواتيم", h1
            key, group = f"back-{u[1]}", "الخواتيم"
        if not any(r[0] == "part" and r[2] == group for r in toc):
            toc.append(("part", "", group))
            outline.append((group, key, 0))
        toc.append(("e", kick if u[0] == "app" else "", title, key, numbered(md)))
        outline.append((h1, key, 1))
        body = f'<section class="chap"><div class="chap-open">{lesson_html(md, breaks=False)}</div></section>'
        pieces.append(("flow", flow(css, (body, O.band(kick, title, ""))),
                       {"recto": True, "anchor": key, "head": ([("title", group)], [("title", title if len(title) < 22 else kick)])}))
        return
    raise SystemExit(f"no builder for the unit {u}")


def folios(css, pages, slug=None):
    """The heads and folios (heads.py); the review proof also carries its slug on every page, the final never."""
    measure = H.Measure(css)
    body = H.overlay(pages, measure)
    if slug:
        body = body.replace('<section class="hd-page">', f'<section class="hd-page"><div class="slug">{slug}</div>')
    return doc(css, body, O.FIXED_CSS % dict(w=G.W, h=G.H) + " html, body { background: transparent !important; }" + H.CSS
               + '.slug { position: absolute; bottom: 5.2mm; left: 0; right: 0; text-align: center; font: 400 6.2pt/1 "IBM Plex Sans Arabic"; '
                 'color: #A39A8A; letter-spacing: .4pt; }')


# ------------------------------------------------------------------------------------------------ the volume

def main(n=1, review=False):
    from pypdf import PdfReader, PdfWriter
    css = C2.fonts()
    fixed = O.FIXED_CSS % dict(w=G.W, h=G.H)
    R = {"recto": True}
    vol = VOLUMES[n - 1]
    everything = sorted(OPENING.glob("*.md"))
    muq = [f for f in everything if f.name[:2] < "90"]
    appendices = [f for f in everything if f.name[:2] >= "90"]

    # (kind, html, meta); meta: recto (open on a recto page), spread (open on an even page), anchor, head, toc
    title_page = P2.title_page(css, FM.title_volume(n, babs_line(n))).replace('class="pg', 'class="full').replace("</section>", "") + O.TP_MARK
    pieces = [("fixed", doc(css, FM.half_title(n), fixed), R),
              ("fixed", doc(css, FM.volumes_map(n), fixed), {"spread": True}),
              ("fixed", doc(css, title_page, fixed), R),
              ("fixed", doc(css, FM.imprint(n), fixed), {"anchor": "imprint"}),
              ("fixed", doc(css, FM.rights(), fixed), R)]
    if n > 1:
        # the book's dedication, its author's word and its publisher's word are in the first volume; each volume
        # has its verse, its contents and its symbols (Bible, chs. 99 and 112d §٤)
        pieces += [("fixed", doc(css, P2.verse_page().replace('class="pg', 'class="full'), fixed), R),
                   ("toc", None, {"recto": True, "head": O.same("المحتويات"), "opens": True}),
                   ("cont", doc(css, FM.symbols(), O.CONT_CSS), {"recto": True, "anchor": "symbols", "head": O.same("الرموز والاصطلاحات"), "opens": True})]
        toc = [("part", "", "المقدّمات"), ("e", "", "الرموز والاصطلاحات", "symbols", [])]
        outline = [("المقدّمات", "toc", 0), ("المحتويات", "toc", 1), ("الرموز والاصطلاحات", "symbols", 1)]
        for u in vol["units"]:
            unit(css, n, u, pieces, toc, outline, fixed, first=u is vol["units"][0])
        return assemble(css, n, review, pieces, toc, outline, fixed)
    pieces += [("fixed", doc(css, FM.dedication(), fixed), {}),
              ("fixed", doc(css, P2.verse_page().replace('class="pg', 'class="full'), fixed), R),
              ("cont", doc(css, FM.publisher_word(), O.CONT_CSS), {"recto": True, "anchor": "publisher", "head": O.same("كلمة الناشر"), "opens": True}),
              ("flow", flow(css, O.chapter(AUTHOR_WORD.read_text(encoding="utf-8").replace("# كلمة المؤلف", "## كلمة المؤلف"), FM.volume_line(n))),
               {"recto": True, "anchor": "author", "head": O.same("كلمة المؤلف")}),
              ("toc", None, {"recto": True, "head": O.same("المحتويات"), "opens": True}),
              ("cont", doc(css, FM.symbols(), O.CONT_CSS), {"recto": True, "anchor": "symbols", "head": O.same("الرموز والاصطلاحات"), "opens": True}),
              ("fixed", doc(css, O.poster("المجلد الأول", "المقدمة", "في صناعة الكلام: البيان في خلق الإنسان وفي الكتاب والسنة وعند علماء العربية، ومنزلة العربية وعلومها، والفرق بين أن تعرف اللغة وأن تملكها، وأيّ عربيةٍ نتكلّم.", kufam=True), fixed),
               {"recto": True, "anchor": "main"})]
    toc = [("part", "", "المقدّمات"), ("e", "", "كلمة الناشر", "publisher", []), ("e", "", "كلمة المؤلف", "author", []),
           ("e", "", "الرموز والاصطلاحات", "symbols", []), ("part", "", "المقدمة: في صناعة الكلام"), ("e", "", "تمهيد", "01", [])]
    outline = [("المقدّمات", "publisher", 0), ("كلمة الناشر", "publisher", 1), ("كلمة المؤلف", "author", 1),
               ("المحتويات", "toc", 1), ("الرموز والاصطلاحات", "symbols", 1), ("المقدمة: في صناعة الكلام", "main", 0), ("تمهيد", "01", 1)]

    # the Muqaddima, as the opening sets it
    tamhid = muq[0].read_text(encoding="utf-8").replace("# المقدمة: في صناعة الكلام\n", "")
    pieces.append(("flow", flow(css, O.chapter(tamhid, "المقدمة")), {"anchor": "01", "head": (O.MUQ, [("title", "تمهيد")])}))
    interludes = {
        "05-": ("fixed", lambda: O.heritage("سيبويه", "«فمنه مستقيمٌ حسن، ومُحال، ومستقيمٌ كذب، ومستقيمٌ قبيح، وما هو مُحالٌ كذب»", "الكتاب، باب الاستقامة من الكلام والإحالة")),
        "07-": ("fixed", lambda: O.verse_poster("العربية والوحي", "إِنَّا نَحْنُ نَزَّلْنَا ٱلذِّكْرَ وَإِنَّا لَهُۥ لَحَٰفِظُونَ", "(الحجر: ٩)")),
        "10-": ("fixed", lambda: O.poster("السؤال الذي وُلد منه الكتاب", "كيف نصنع المتكلّم العربي؟",
                                          "لا: كيف نعلّم الطالب مزيدًا من العربية؛ بل: كيف نجعل العربية التي تعلّمها تظهر على لسانه حين يحتاج إليها، ثم يُحسن وضعها في موضعها.", kufam=True, mid=True)),
        "11-": ("fixed", lambda: O.poster("المقدمة", "فأين الخلل؟", "ليس في علم المتعلّم، ولا في عقله، ولا في دينه؛ بل في صناعةٍ لم تُعلَّم تعليمًا مقصودًا: أن يصير ما يعرفه كلامًا يُقال، لمن يُقال له، حين يُقال.")),
        "14-": ("fixed", lambda: O.heritage("من الصحيفة المنسوبة إلى بشر بن المعتمر", "«فيجعل لكلّ طبقةٍ من ذلك كلامًا، ولكلّ حالةٍ من ذلك مقامًا»", "رواها الجاحظ في البيان والتبيين")),
    }
    for k, f in enumerate(muq[1:], 1):
        md = f.read_text(encoding="utf-8")
        if f.name[:3] in interludes:
            pieces.append(("fixed", doc(css, interludes[f.name[:3]][1](), fixed), {}))
        title = re.sub(r"^الفصل [^:]+:\s*", "", re.search(r"^##\s+(.+)$", md, re.M).group(1))
        key = f.name[:2]
        toc.append(("e", f"الفصل {ORD[k]}", title, key, O.sections(md)))
        outline.append((f"الفصل {ORD[k]}: {title}", key, 1))
        heads = (O.MUQ, O.head_of(md, k))
        for kind, part in O.chapter_parts(md, f"الفصل {ORD[k]}"):
            if kind == "flow":
                pieces.append(("flow", flow(css, part), {"anchor": key, "head": heads}))
            elif kind == "fixed":
                pieces.append(("fixed", doc(css, part, fixed), {}))
            else:
                pieces.append(("cont", doc(css, part, O.CONT_CSS, paged="fn-note" in part), {"head": heads}))

    # the introduction: a threshold, then its chapter, with the spectrum where the text announces it
    pieces.append(("fixed", doc(css, threshold("المجلد الأول", "المدخل", "العربية التي نتكلّمها: لغةٌ واحدة لها مستويات، ولكل مستوًى مقامه؛ وأين يقف المتكلّم منها، وإلى أين يريد أن يصل."), fixed),
                   {"recto": True, "anchor": "intro"}))
    toc.append(("part", "", "المدخل"))
    outline.append(("المدخل", "intro", 0))
    for k, f in enumerate(sorted(INTRO.glob("ف*.md")), 1):
        raw = f.read_text(encoding="utf-8")
        raw = re.sub(r"^## ", "### ", raw, flags=re.M)                   # its sections under its title
        md = with_figures(re.sub(r"^# ", "## ", raw, count=1, flags=re.M))
        title = re.sub(r"^الفصل [^:]+:\s*", "", re.search(r"^##\s+(.+)$", md, re.M).group(1))
        key = f"i{k}"
        toc.append(("e", f"الفصل {ORD[k]}", title, key, [("", t) for t in re.findall(r"^###\s+(.+)$", md, re.M)]))
        outline.append((f"الفصل {ORD[k]}: {title}", key, 1))
        heads = ([("title", "المدخل")], O.head_of(md, k))
        for kind, part in O.chapter_parts(md, f"المدخل · الفصل {ORD[k]}"):
            if kind == "flow":
                pieces.append(("flow", flow(css, part), {"anchor": key, "head": heads}))
            else:
                pieces.append((kind, doc(css, part, fixed if kind == "fixed" else O.CONT_CSS, paged="fn-note" in part), {"head": heads}))

    unit(css, n, ("bab", 1), pieces, toc, outline, fixed)

    # the appendices: the verification appendix and the volume's thabat
    toc.append(("part", "", "الملاحق"))
    first_app = True
    for f in appendices:
        md = f.read_text(encoding="utf-8")
        title = re.search(r"^##\s+(.+)$", md, re.M).group(1).strip()
        key = f.name[:2]
        toc.append(("e", "", title, key, O.sections(md)))
        outline.append((title, key, 0 if first_app else 1))
        if first_app:
            outline[-1] = ("الملاحق", key, 0)
            outline.append((title, key, 1))
        first_app = False
        for kind, part in O.chapter_parts(md, "الملاحق"):
            if kind == "flow":
                body, bandhtml = part
                part = (body.replace('<section class="chap">', f'<section class="chap app-{key}">', 1), bandhtml)
                pieces.append(("flow", flow(css, part), {"recto": True, "anchor": key, "head": ([("title", "الملاحق")], [("title", title)])}))
    return assemble(css, n, review, pieces, toc, outline, fixed)


def assemble(css, n, review, pieces, toc, outline, fixed):
    """The pieces set, paged, numbered, headed, bookmarked, compacted and guarded; the colophon closes the volume."""
    from pypdf import PdfReader, PdfWriter
    proof = f"نسخة المراجعة (<span class='lat'>Proof</span>)، أُخرجت في {PROOF_DATE} لفحصها قبل الطبع؛ وليست الطبعة المعتمدة." if review else None
    pieces.append(("fixed", doc(css, FM.colophon(n, proof=proof), fixed), {"recto": True}))

    def toc_html(numbers):
        rows = [r if r[0] == "part" else ("e", r[1], r[2], numbers.get(r[3], "٠٠٠"), r[4]) for r in toc]
        return doc(css, FM.contents(rows, n), O.CONT_CSS, paged=True)

    tag = f"vol{n:02d}"
    paper = B.render(doc(css, '<div style="width:170mm;height:240mm;background:var(--paper)"></div>', fixed), f"{tag}-paper")
    out, anchors, toc_slot = [], {"toc": None}, None       # out: [(page, kind, heads)]; page 1 is out[0]
    for i, (kind, html, meta) in enumerate(pieces):
        hd = meta.get("head")
        # page p = len(out) + 1; a recto is odd, a spread opens on an even page
        if meta.get("recto") and (len(out) + 1) % 2 == 0:
            out.append((PdfReader(str(paper)).pages[0], "blank", None))
        if meta.get("spread") and (len(out) + 1) % 2 == 1:
            out.append((PdfReader(str(paper)).pages[0], "blank", None))
        if meta.get("anchor"):
            anchors[meta["anchor"]] = len(out)
        if meta.get("alias"):
            anchors[meta["alias"]] = len(out)
        if kind == "toc":
            anchors["toc"] = len(out)
            r = PdfReader(str(B.render(toc_html({}), f"{tag}-toc")))
            toc_slot = (len(out), len(r.pages[:O.body_pages(r)]))
            for pg in r.pages[:toc_slot[1]]:
                out.append((pg, "toc", hd))
            continue
        if kind == "flow":
            body, bandhtml = html
            r = PdfReader(str(B.render(body, f"{tag}-{i:02d}")))
            band = B.render(bandhtml, f"{tag}-{i:02d}-band")
            for j, pg in enumerate(r.pages[:O.body_pages(r)]):
                under = PdfReader(str(band if j == 0 else paper)).pages[0]
                under.merge_page(pg)
                out.append((under, "open" if j == 0 else "flow", hd))
            continue
        r = PdfReader(str(B.render(html, f"{tag}-{i:02d}")))
        for j, pg in enumerate(r.pages[:O.body_pages(r)] if kind == "cont" else r.pages):
            if kind == "cont":
                under = PdfReader(str(paper)).pages[0]
                under.merge_page(pg)
                pg = under
            out.append((pg, ("open" if meta.get("opens") and j == 0 else "flow") if kind == "cont" else kind, hd))
    # the preliminaries in abjad letters from the half-title; the text from ١ at the Muqaddima
    main_at = anchors["main"]
    label = [O.ABJAD[i] if i < main_at else str(i - main_at + 1).translate(AR) for i in range(len(out))]
    numbers = {a: label[ix] for a, ix in anchors.items() if ix is not None}
    r = PdfReader(str(B.render(toc_html(numbers), f"{tag}-toc")))
    if len(r.pages[:O.body_pages(r)]) != toc_slot[1]:
        raise SystemExit("the contents changed length when its page numbers were filled in")
    for k in range(toc_slot[1]):
        under = PdfReader(str(paper)).pages[0]
        under.merge_page(r.pages[k])
        out[toc_slot[0] + k] = (under, "open" if k == 0 else "flow", out[toc_slot[0] + k][2])
    # the heads and folios, drawn last: page p is a left-hand page when p is odd
    style = {"flow": "run", "open": "open"}
    measure = H.Measure(css)
    marks = []
    for i in range(len(out)):
        p = i + 1
        st, hd = style.get(out[i][1], ""), out[i][2]
        parts = None
        if st == "run" and hd:
            parts = hd[1] if p % 2 else hd[0]
            if not measure.fits(parts):
                raise SystemExit(f"the head reaches the mark ({measure.head(parts):.1f} mm of {H.REACH:.1f}): {parts}"
                                 " — give the chapter a short head: <!-- head: … -->")
        marks.append((label[i], st, parts, "odd" if p % 2 else "even"))
    slug = f"نسخة المراجعة · {FM.volume_line(n)} · ليست للنشر" if review else None
    fr = PdfReader(str(B.render(folios(css, marks, slug), f"{tag}-folios")))
    w = PdfWriter()
    for i, (pg, _, _) in enumerate(out):
        pg.merge_page(fr.pages[i])
        w.add_page(pg)
    parents = {}
    for title, key, level in outline:
        ix = anchors.get(key)
        if ix is None:
            continue
        parent = parents.get(level - 1) if level else None
        parents[level] = w.add_outline_item(title, ix, parent=parent)
    meta = {"/Title": f"{FM.TITLE} — {FM.volume_line(n)}" + (" (نسخة المراجعة)" if review else ""), "/Author": FM.AUTHOR_SHORT,
            "/Publisher": FM.PUBLISHER_EN, "/Subject": "Proof — not for publication" if review else FM.volume_line(n)}
    if FM.ISBN.get(n):
        meta["/ISBN"] = FM.ISBN[n]
    w.add_metadata(meta)
    w.page_mode = "/UseOutlines"
    dest = out_path(n, review)
    w.write(str(dest))
    import pymupdf
    # every piece carries its own copy of the faces and pypdf writes them uncompressed: one lossless pass merges
    # the duplicates and compresses the streams (a 35 MB file becomes a fifth of it, page for page the same)
    tmp = dest.with_suffix(".tmp.pdf")
    pymupdf.open(str(dest)).save(str(tmp), garbage=4, deflate=True, deflate_fonts=True)
    tmp.replace(dest)
    O.guard_fonts(dest)
    t3 = sorted({label[pg.number] for pg in pymupdf.open(str(dest)) for f in pg.get_fonts() if f[2] == "Type3"})
    if t3:
        raise SystemExit(f"Type 3 glyphs (a glyph none of the book's faces holds) on pages: {t3}")
    anchors_page = {a: label[ix] for a, ix in anchors.items() if ix is not None}
    (HERE / ".cache" / f"{tag}-anchors.json").write_text(__import__("json").dumps(
        {"anchors": anchors_page, "labels": label, "kinds": [k for _, k, _ in out]}, ensure_ascii=False), encoding="utf-8")
    print(dest, len(w.pages), "pages")


OPENER_CSS = """
.opener-k { display: flex; gap: 3mm; align-items: center; font: 300 10.4pt/1 "Changa"; color: var(--gold-ink); margin-bottom: 3mm; }
.opener-k i { flex: 1; border-top: .45pt solid var(--gold); }
h2.op-t { font: 700 26pt/1.3 "Changa"; color: var(--sapphire); margin: 0; }
p.op-s { font: 300 12.6pt/1.5 "Changa"; color: var(--gold-ink); text-indent: 0; margin: 1mm 0 5mm; text-align: right; }
"""

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    main(int(args[0]) if args else 1, review="--review" in sys.argv)
