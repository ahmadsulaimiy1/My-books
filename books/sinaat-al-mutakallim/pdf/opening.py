#!/usr/bin/env python3
"""The opening of Volume I, typeset in the edition-1.2 system (Bible, part seven).

Flowing pages (Chromium pagination), with the page types of ch. 36 placed where the argument turns:
title page, the verse of Surat al-Rahman, the author's word, a sapphire threshold for the مقدمة,
a sapphire band opening every chapter, heritage pages for the scholars, poster interludes,
Qur'an in Amiri Quran, poetry in hemistichs, tables in IBM Plex Sans Arabic, notes at chapter end.

Type: Scheherazade New for reading; Changa Bold / Light as the principal display Kufi; Kufam
(the book's cut) for the logotype and poster words; Amiri for heritage; Plex for navigation.

    python3 opening.py          writes ../Volume-I_Opening.pdf
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
import proto2 as P2  # noqa: E402
import frontmatter as FM  # noqa: E402
import heads as H  # noqa: E402

BOOK = HERE.parent / "book"
from paths import AUTHOR_WORD, OPENING  # noqa: E402
import ids as IDS  # noqa: E402
OUT = HERE.parent / "Volume-I_Opening.pdf"
AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
ORD = ["", "الأول", "الثاني", "الثالث", "الرابع", "الخامس", "السادس", "السابع", "الثامن", "التاسع", "العاشر",
       "الحادي عشر", "الثاني عشر", "الثالث عشر", "الرابع عشر", "الخامس عشر", "السادس عشر", "السابع عشر",
       "الثامن عشر", "التاسع عشر", "العشرون"]

CSS = r"""
/* the running heads and folios are not drawn here: heads.py lays them over the assembled pages, where each page
   knows whether it is a left-hand or a right-hand page (Bible, ch. 117b) */
@page { size: 200mm 260mm; margin: 25mm 39mm 30mm 39mm; }
@page :first { margin-top: 104mm; }
:root { --ink: #1C1915; --ink-2: #4A443C; --ink-3: #7C7467; --paper: #F8F6F1; --paper-2: #EFECE5;
  --sapphire: #0C2766; --sapphire-2: #2B4A8F; --gold: #C9A95C; --gold-l: #E4CB8C; --gold-ink: #8A6A1F; --crimson: #A8172E;
  --ruby: #7B1730; --ruby-2: #9A4A58; --charcoal: #232A3A; }
html, body { margin: 0; background: var(--paper); }
body { direction: rtl; color: var(--ink); font: 400 13.2pt/1.85 "Scheherazade New", serif; }
.full { position: relative; width: 200mm; height: 260mm; overflow: hidden; break-before: page; break-after: page; }
.wrap-pg { page: wrap; break-after: page; }
.dark { background: var(--sapphire); color: #EFE7D6; }
.chap { break-before: page; }
.chap-band { position: absolute; top: 0; left: 0; right: 0; height: 92mm; background: var(--sapphire); color: #EFE7D6; }
.chap-band .k { position: absolute; top: 36mm; right: 39mm; font: 300 11pt/1 "Changa"; color: var(--gold-l); display: flex; gap: 3mm; align-items: center; }
.chap-band .k i { width: 10mm; border-top: .5pt solid var(--gold); display: inline-block; }
.chap-band h2 { position: absolute; top: 46mm; right: 39mm; left: 39mm; margin: 0; font: 700 29pt/1.25 "Changa"; color: #F4ECD9; string-set: chap content(); text-wrap: balance; }
.chap-band .sub { position: absolute; top: 62mm; right: 39mm; left: 39mm; font: 300 12.5pt/1.5 "Changa"; color: var(--gold-l); }
.chap-band .dot { position: absolute; bottom: -1.3mm; right: 39mm; width: 2.4mm; height: 2.4mm; transform: rotate(45deg); background: var(--gold); }
.chap-open { position: relative; }
p { margin: 0; text-align: justify; }
p + p { text-indent: 6mm; }
.chap-open > p:first-child, .chap-open > .keep:first-child > p { font-size: 14.4pt; line-height: 1.8; text-indent: 0; }
h3 { font: 700 15pt/1.45 "Changa"; color: var(--sapphire); margin: 7mm 0 2.4mm; break-after: avoid; }
h3::after { content: ""; display: block; width: 12mm; border-top: .8pt solid var(--gold); margin-top: 1.6mm; }
h3 + p { text-indent: 0; }
strong { font-weight: 700; }
.q { font: 400 14.6pt/1.9 "Amiri Quran", "Amiri"; color: var(--ruby); }
.qref { font: 400 8.2pt/1 "Changa"; color: var(--ruby-2); margin-right: 1.4mm; white-space: nowrap; }
p.ayah { text-align: center; text-indent: 0; margin: 7mm 0 7.5mm; padding: 6.2mm 5mm 5.4mm; break-inside: avoid; text-wrap: balance;
  background: url("data:image/svg+xml;utf8,%%3Csvg%%20xmlns%%3D%%22http%%3A//www.w3.org/2000/svg%%22%%20width%%3D%%2244mm%%22%%20height%%3D%%222.4mm%%22%%20viewBox%%3D%%220%%200%%20440%%2024.0%%22%%3E%%3Cg%%20fill%%3D%%22none%%22%%20stroke%%3D%%22%%23C9A95C%%22%%20stroke-width%%3D%%222%%22%%3E%%3Cline%%20x1%%3D%%220%%22%%20y1%%3D%%2212%%22%%20x2%%3D%%22200%%22%%20y2%%3D%%2212%%22/%%3E%%3Cline%%20x1%%3D%%22240%%22%%20y1%%3D%%2212%%22%%20x2%%3D%%22440%%22%%20y2%%3D%%2212%%22/%%3E%%3C/g%%3E%%3Cpath%%20d%%3D%%22M220%%202%%20L230%%2012%%20L220%%2022%%20L210%%2012%%20Z%%22%%20fill%%3D%%22%%237B1730%%22/%%3E%%3Cg%%20fill%%3D%%22%%23C9A95C%%22%%3E%%3Cpath%%20d%%3D%%22M200%%209%%20l3%%203%%20-3%%203%%20-3%%20-3z%%22/%%3E%%3Cpath%%20d%%3D%%22M240%%209%%20l3%%203%%20-3%%203%%20-3%%20-3z%%22/%%3E%%3C/g%%3E%%3C/svg%%3E") no-repeat center top / 44mm 2.4mm, linear-gradient(#C9A95C, #C9A95C) no-repeat center bottom / 16mm .45pt; }
p.ayah .q { font-size: 17.4pt; line-height: 2.1; }
p.ayah .qref { display: block; margin: 1.6mm 0 0; font: 300 8.6pt/1.4 "Changa"; letter-spacing: .3pt; color: var(--ruby-2); }
blockquote { margin: 4mm 0; padding: 0; break-inside: avoid; }
blockquote.quote { border-right: 1.4pt solid var(--gold); padding: 1mm 5mm 1mm 0; }
blockquote.hadith { margin: 6.5mm 5mm; text-align: center; }
blockquote.hadith::before, blockquote.hadith::after { content: ""; display: block; height: 2mm; background: url("data:image/svg+xml;utf8,%%3Csvg%%20xmlns%%3D%%22http%%3A//www.w3.org/2000/svg%%22%%20width%%3D%%2228mm%%22%%20height%%3D%%222mm%%22%%20viewBox%%3D%%220%%200%%20280%%2020%%22%%3E%%3Cg%%20fill%%3D%%22none%%22%%20stroke%%3D%%22%%23C9A95C%%22%%20stroke-width%%3D%%222%%22%%3E%%3Cline%%20x1%%3D%%220%%22%%20y1%%3D%%2210%%22%%20x2%%3D%%22125%%22%%20y2%%3D%%2210%%22/%%3E%%3Cline%%20x1%%3D%%22155%%22%%20y1%%3D%%2210%%22%%20x2%%3D%%22280%%22%%20y2%%3D%%2210%%22/%%3E%%3Cpath%%20d%%3D%%22M140%%202%%20L148%%2010%%20L140%%2018%%20L132%%2010%%20Z%%22/%%3E%%3C/g%%3E%%3C/svg%%3E") no-repeat center / 28mm 2mm; }
blockquote.hadith p { font: 400 14.8pt/1.95 "Amiri"; color: var(--charcoal); text-align: center; text-indent: 0; padding: 2.6mm 0; text-wrap: balance; }
blockquote.quote p { font: 400 14pt/1.9 "Amiri"; color: var(--sapphire); text-indent: 0; }
blockquote.lesson { background: var(--paper-2); border-top: .8pt solid var(--gold); padding: 3mm 5mm 3.4mm; margin: 5mm 0 5.5mm; }
blockquote.lesson p { font: 400 12.4pt/1.75 "Scheherazade New"; color: var(--ink-2); text-indent: 0; text-align: justify; }
blockquote.lesson p > strong:first-child { display: block; font: 600 10.4pt/1.5 "Changa"; color: var(--gold-ink); margin-bottom: .8mm; }
blockquote.litany { margin: 6mm 0; padding: 4mm 0; border-top: .5pt solid var(--gold); border-bottom: .5pt solid var(--gold); text-align: center; }
blockquote.litany .ln { font: 400 14.2pt/2 "Scheherazade New"; color: var(--sapphire); }
blockquote.litany .ln:first-child { font-weight: 700; }
blockquote.title-line { margin: 7mm 0 2mm; text-align: center; }
blockquote.title-line p { font: 600 25pt/1.6 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--sapphire); text-align: center; text-indent: 0; }
blockquote.title-line p strong { font-weight: 600; }
blockquote.def p { font: 400 13.6pt/1.8 "Scheherazade New"; color: var(--sapphire); text-align: center; text-indent: 0; }
.bayt { display: grid; grid-template-columns: 1fr 7mm 1fr; padding: 0 3mm; font: 400 13.8pt/2.1 "Amiri"; color: var(--ink); }
.bayt span { text-align: center; white-space: nowrap; }
blockquote.poem { background: var(--paper-2); padding: 4.5mm 0; margin: 6mm 0; border-top: .5pt solid var(--gold); border-bottom: .5pt solid var(--gold); }
ol, ul { margin: 1mm 0 2mm; padding: 0 6.5mm 0 0; }
li { text-align: justify; margin: .4mm 0; }
ul { list-style: none; } ul > li { position: relative; }
ul > li::before { content: ""; position: absolute; right: -4.8mm; top: 3.9mm; width: 1.4mm; height: 1.4mm; transform: rotate(45deg); background: var(--gold); }
.keep { break-inside: avoid; }
.keep > h3 + p { text-indent: 0; }
ul.cols { columns: 2; column-gap: 9mm; } ul.cols > li { break-inside: avoid; }
.sig { margin: 9mm 0 0 0; text-align: left; break-inside: avoid; }
.sig-name { display: block; font: 700 14pt "Changa"; color: var(--sapphire); }
.sig-du { display: block; font: 400 11pt/1.6 "Amiri"; color: var(--gold-ink); margin-top: 1mm; }
ol { list-style: arabic-indic; } ol > li { padding-right: 1.6mm; } ol > li::marker { font: 600 11pt "Changa"; color: var(--gold-ink); }
table { width: 100%%; border-collapse: collapse; font: 400 8.8pt/1.55 "IBM Plex Sans Arabic"; margin: 4mm 0; break-inside: avoid; }
th { font: 600 9.2pt/1.4 "Changa"; text-align: right; color: #F3ECDC; background: var(--sapphire); padding: 1.6mm 2mm; }
td { border-bottom: .4pt solid #D8D0C0; padding: 1.4mm 2mm; vertical-align: top; color: var(--ink-2); }
tr:nth-child(even) td { background: #F6F1E6; }
td:first-child { font-weight: 600; color: var(--ink); }
/* notes at the foot of the page where they are called (Bible, chs. 45 and 82): a short gold rule from the
   right, then the notes in a smaller Scheherazade, each hanging on its chapter number */
.fn-note { float: footnote; footnote-policy: line; }
.pagedjs_page_content, .pagedjs_footnote_inner_content { direction: ltr; }
/* Paged.js builds the margin boxes as a grid that follows the writing direction: kept LTR, so @top-right stays right */
.pagedjs_margin-top, .pagedjs_margin-bottom { direction: ltr; }
.pagedjs_margin-content { direction: rtl; }
.pagedjs_page_content > div, .fn-note { direction: rtl; }
.pagedjs_footnote_content { margin-top: 4mm; padding-top: 2.8mm; position: relative; }
.pagedjs_footnote_content::before { content: ""; position: absolute; top: .8mm; right: 0; width: 22mm; border-top: .5pt solid var(--gold); }
.pagedjs_footnote_content::after { content: ""; position: absolute; top: .1mm; right: 21.3mm; width: 1.4mm; height: 1.4mm;
  background: var(--gold); transform: rotate(45deg); }
.fn-note[data-footnote-marker] { display: block; position: relative; padding-right: 6.4mm; margin-bottom: 1.3mm;
  font: 400 10.6pt/1.62 "Scheherazade New"; color: var(--ink-2); text-align: justify; text-indent: 0; letter-spacing: 0; }
.fn-note[data-footnote-marker]::before { content: attr(data-n); position: absolute; right: 0; top: .05em;
  font: 700 11pt/1.6 "Amiri"; color: var(--sapphire); }
.fn-tag { font: 300 8pt "Changa"; color: var(--gold-ink); margin-left: .8mm; }
.fn-note[data-split-from]::before { content: none; }
.fn-note .q { font-size: 11.2pt; line-height: 1.55; }
.fn-note .qref { font-size: 7.6pt; }
.fn-note i, .fn-note em { font-style: normal; color: var(--sapphire); }
.fn-note .lat em { font-style: italic; color: inherit; }
.fn-note[data-footnote-call]::after { vertical-align: .44em; font: 700 11pt/0 "Amiri"; font-variant-position: normal;
  color: var(--sapphire); margin: 0 .45mm 0 .15mm; }
%(calls)s
.lat { direction: ltr; unicode-bidi: isolate; font-family: "Source Serif 4"; font-size: .86em; }
/* heritage and poster interludes */
.her { position: absolute; top: 40mm; bottom: 40mm; right: 24mm; left: 24mm; border: .6pt solid var(--gold); padding: 3mm; }
.her-in { border: .3pt solid var(--gold); height: 100%%; box-sizing: border-box; padding: 16mm 12mm; display: flex; flex-direction: column; justify-content: center; background: var(--paper-2); text-align: center; }
.her .who { font: 300 12pt/1.4 "Changa"; color: var(--gold-ink); margin-bottom: 7mm; }
.her .qt { font: 400 18pt/2 "Amiri"; color: var(--sapphire); }
.her .src { font: 400 8.4pt/1.5 "IBM Plex Sans Arabic"; color: var(--ink-3); margin-top: 6mm; }
.poster { position: absolute; inset: 0; display: flex; flex-direction: column; justify-content: center; padding: 0 30mm; }
.poster .kick { font: 300 12pt/1 "Changa"; color: var(--gold-l); margin-bottom: 9mm; display: flex; gap: 3mm; align-items: center; }
.poster .kick i { width: 12mm; border-top: .5pt solid var(--gold); }
.poster .big { font: 700 60pt/1.2 "Changa"; color: var(--gold-l); text-wrap: balance; }
.poster .big.mid { font-size: 36pt; line-height: 1.45; }
.poster .big.kufam { font-family: "Kufam SMA"; font-feature-settings: "liga" 0; font-weight: 600; }
.poster .line { font: 400 16pt/1.8 "Scheherazade New"; color: #E7DFCE; max-width: 120mm; margin-top: 9mm; }
/* the measure page: four questions turned, on pearl within a double gold rule */
.mz { position: absolute; top: 24mm; bottom: 24mm; right: 22mm; left: 22mm; border: .6pt solid var(--gold); padding: 3mm; }
.mz-in { border: .3pt solid var(--gold); height: 100%%; box-sizing: border-box; background: var(--paper-2); display: flex; flex-direction: column; justify-content: center; padding: 12mm 13mm; text-align: center; }
.mz .kick { font: 300 12pt/1 "Changa"; color: var(--gold-ink); margin-bottom: 11mm; display: flex; gap: 3mm; align-items: center; justify-content: center; }
.mz .kick i { width: 10mm; border-top: .5pt solid var(--gold); }
.mz-pair { padding: 5.2mm 0; }
.mz-pair + .mz-pair { border-top: .4pt solid #D9CBA6; }
.mz .no { font: 300 13pt/1.5 "Changa"; color: var(--ink-3); }
.mz .yes { font: 700 17.5pt/1.5 "Changa"; color: var(--sapphire); margin-top: 1.4mm; text-wrap: balance; }
.mz .coda { font: 600 16pt/1.7 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--gold-ink); margin-top: 11mm; text-wrap: balance; }
/* the map of formation: a chain of growing rings on pearl, within the double gold rule of the measure page */
.mp { position: absolute; top: 18mm; bottom: 18mm; right: 16mm; left: 16mm; border: .6pt solid var(--gold); padding: 3mm; }
.mp-in { border: .3pt solid var(--gold); height: 100%%; box-sizing: border-box; background: var(--paper-2); display: flex; flex-direction: column; justify-content: center; align-items: center; padding: 8mm 0; }
.mp .kick { font: 600 13pt/1 "Changa"; color: var(--sapphire); margin-bottom: 6mm; display: flex; gap: 3mm; align-items: center; }
.mp .kick i { width: 10mm; border-top: .5pt solid var(--gold); }
.mp-draw { position: relative; width: 160mm; }
.mp-svg { position: absolute; top: 0; left: 0; width: 160mm; }
.mp-n { position: absolute; transform: translate(-50%%, -52%%); font: 600 10.5pt/1 "Changa"; color: var(--gold-ink); }
.mp-l { position: absolute; transform: translateY(-50%%); font: 500 12.4pt/1.2 "Changa"; color: var(--sapphire); white-space: nowrap; }
.mp-right { text-align: right; } .mp-left { text-align: left; }
.mp-band { position: absolute; right: 0; width: 7mm; border-right: .5pt solid var(--gold); }
.mp-band span { position: absolute; top: 50%%; right: 1.6mm; transform: translateY(-50%%); writing-mode: vertical-rl; font: 400 9.4pt "Changa"; color: var(--gold-ink); letter-spacing: .3pt; }
.mp-band.b2 { border-right-color: var(--sapphire-2); }
.mp-note { font: 300 10.4pt/1.6 "Changa"; color: var(--ink-3); margin-top: 6mm; }
.mp-coda { font: 600 14pt/1.6 "Kufam SMA"; font-feature-settings: "liga" 0; color: var(--gold-ink); margin-top: 3mm; }
.vp { align-items: center; text-align: center; } .vp .kick { justify-content: center; }
.vp-a { font: 400 30pt/2 "Amiri Quran"; color: var(--gold-l); text-wrap: balance; }
.vp-r { font: 300 11pt/1.4 "Changa"; color: #E7DFCE; margin-top: 7mm; }
.arw { display: inline-block; width: 1.05em; height: .66em; vertical-align: .05em; margin: 0 1.4mm; color: var(--gold-ink); }
h3 .hn { font: 700 14pt/1 "Amiri"; color: var(--gold-ink); margin-left: 2.4mm; }
.sc-draw { position: relative; width: 160mm; }
.sc-core { position: absolute; transform: translate(-50%%, -50%%); width: 27mm; text-align: center; }
.sc-core b { display: block; font: 600 12.2pt/1.25 "Changa"; color: var(--sapphire); }
.sc-core span { display: block; font: 400 8.3pt/1.4 "Scheherazade New"; color: var(--ink-2); margin-top: .8mm; }
.sc-mid { position: absolute; transform: translate(-50%%, -50%%); font: 500 8.6pt/1.25 "Changa"; color: var(--gold-l); text-align: center; }
.sc-sup { position: absolute; transform: translate(-50%%, -50%%); font: 400 9.2pt/1 "Changa"; color: var(--ink-2); background: var(--paper-2); padding: 1.2mm 2mm; white-space: nowrap; display: flex; gap: 1.6mm; align-items: center; }
.sc-sup i { width: 1.2mm; height: 1.2mm; background: var(--gold); transform: rotate(45deg); }
.sc-leg { display: flex; gap: 8mm; font: 300 8.6pt/1 "Changa"; color: var(--ink-3); margin-top: 1mm; }
.sc-leg span { display: flex; gap: 2mm; align-items: center; }
.sc-leg i.c { width: 3.4mm; height: 3.4mm; border-radius: 50%%; background: rgba(201,169,92,.25); border: .35pt solid #0C2766; }
.sc-leg i.s { width: 1.4mm; height: 1.4mm; background: var(--gold); transform: rotate(45deg); }
.sc-arrow { font: 300 9.6pt/1 "Changa"; color: var(--gold-ink); margin-top: 7mm; }
.sc-band { margin-top: 3mm; background: var(--sapphire); padding: 3.4mm 4mm; display: flex; flex-wrap: wrap; justify-content: center; gap: 1.4mm 3.2mm; max-width: 146mm; box-sizing: border-box; }
.sc-band span { font: 500 9.8pt/1.3 "Changa"; color: #F1EADB; white-space: nowrap; }
.sc-band span + span::before { content: ""; display: inline-block; width: 1.2mm; height: 1.2mm; background: var(--gold); transform: rotate(45deg); margin-left: 3.2mm; vertical-align: middle; }
/* ثبت المصادر: hanging entries, no bullets */
.app-91 ul { list-style: none; padding: 0; }
.app-91 ul > li { padding-right: 6mm; text-indent: -6mm; margin: 0 0 1.6mm; font-size: 11.6pt; line-height: 1.7; text-align: right; }
.app-91 ul > li::before { content: none; }
.app-91 ul > li strong { color: var(--sapphire); }
.app-91 ul:last-of-type { direction: ltr; }
.app-91 ul:last-of-type > li { padding: 0 0 0 6mm; text-indent: -6mm; text-align: left; font: 400 10.6pt/1.6 "Source Serif 4"; }
.app-91 ul:last-of-type .lat { font-size: 1em; }
.app-91 .deg { font: 400 7.6pt/1 "Changa"; color: var(--gold-ink); white-space: nowrap; margin-right: 1.2mm; }
.app-91 ul:last-of-type .deg { font-family: "Changa"; direction: rtl; unicode-bidi: isolate; }
.toc-p { font: 400 12pt/1.9 "Scheherazade New"; }
.toc-row { display: flex; gap: 3mm; align-items: baseline; border-bottom: .4pt dotted #CFC5B1; padding: 1.2mm 0; }
.toc-row b { font: 600 10pt "Changa"; color: var(--gold-ink); min-width: 22mm; }
.toc-row span { font: 400 13pt "Scheherazade New"; }

/* «فإن قيل… قلنا»: the objection in its own block, the answer after it (Bible, ch. 100) */
p.obj { background: var(--paper-2); border-right: 1.3pt solid var(--sapphire-2); padding: 2.6mm 4.5mm 2.8mm 3mm; margin: 5mm 0 0; text-indent: 0; }
p.ans { border-right: 1.3pt solid var(--gold); padding: 2.4mm 4.5mm 2.6mm 3mm; margin: 0 0 5mm; text-indent: 0; }
p.obj + p.ans { margin-top: 0; }
/* a line that introduces a verse, a hadith or a quotation never stays behind at the foot of a page */
p:has(+ p.ayah), p:has(+ blockquote), p:has(+ .keep > blockquote) { break-after: avoid; }
/* the close of a chapter (خلاصة، ما يترتّب): its own quieter panel, so the chapter ends on a different rhythm */
.summary { background: var(--paper-2); border-top: .8pt solid var(--gold); border-bottom: .4pt solid var(--gold); padding: 1mm 5.5mm 4.2mm; margin: 7mm 0 2mm; }
.summary > h3 { margin-top: 3.4mm; }
.summary p, .summary li { font-size: 12.8pt; }
.summary table { margin-bottom: 1mm; }
"""
CSS += FM.CSS


def ayat(html):
    """﴿…﴾ (ref) → Amiri Quran span + reference; a paragraph that is only an ayah becomes a display ayah."""
    html = re.sub(r"﴿([^﴾]+)﴾\s*\(([^)]+)\)", r'<span class="q">﴿\1﴾</span><span class="qref">(\2)</span>', html)
    html = re.sub(r'(?<!<span class="q">)﴿([^﴾]+)﴾', r'<span class="q">﴿\1﴾</span>', html)
    return html


def is_hadith(bq, notes):
    """A quotation whose note is a takhrij of a marfu' report (رواه/متفق عليه/أخرجه, not موقوف)."""
    m = re.search(r"⟦(\d+)⟧", bq.get_text())
    if not m:
        return False
    note = notes.get(m.group(1), "")
    return note.startswith(("رواه", "متفق", "أخرجه")) and "موقوف" not in note


TAGS = {"تحقيق": "tahqiq", "لغة": "lugha", "انظر": "ihala", "تعقيب": "taqib", "تنبيه": "tanbih"}


def note_kind(text):
    """The kind of a note (Bible, chs. 44 and 82). A note that opens with its label (تحقيق: لغة: انظر: تعقيب: تنبيه:)
    is of that kind; a takhrij opens with أخرجه; every other note documents a source and carries no label."""
    head = re.match(r"(\S+?)[:\s]", text)
    if head and head.group(1) in TAGS:
        return TAGS[head.group(1)]
    if text.startswith(("أخرجه", "رواه", "متفق")):
        return "takhrij"
    return "tawthiq"


ARROW = ('<svg class="arw" viewBox="0 0 16 10" aria-hidden="true"><path d="M15 5 H2.2 M6 1.4 L2 5 L6 8.6" fill="none" '
         'stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def latinize(soup):
    """A Latin run inside Arabic is isolated left-to-right in Source Serif, so its word order holds."""
    for t in soup.find_all(string=re.compile(r"[A-Za-z]{3,}")):
        if t.parent.name not in ("style",) and not t.find_parent(class_="lat"):
            t.replace_with(BeautifulSoup(re.sub(r"([A-Za-z][^؀-ۿ]*[A-Za-z.)\"”’'])", r'<span class="lat">\1</span>', str(t)), "html.parser"))


def note_span(n, text):
    """A note as the page carries it: an inline element at its call, which the paginator floats to the foot
    of the page where the call falls (float: footnote). Its number is the chapter's, never the page's."""
    # a whole Latin reference (title in italics and all) is one left-to-right isolate, not a run per word group
    text = re.sub(r"([A-Za-z][^؀-ۿ]*[A-Za-z.)\"”’'])", r'<span class="lat">\1</span>', text)
    body = markdown.markdown(text).removeprefix("<p>").removesuffix("</p>")
    body = re.sub(r"^(%s):" % "|".join(TAGS), r'<span class="fn-tag">\1:</span>', body)
    body = re.sub(r"(?<![*\w])\*([^*]+)\*", r"<i>\1</i>", ayat(body))
    num = n.translate(AR)
    return f'<span class="fn-note fn-n{n} fn-{note_kind(text)}" data-n="{num}">{body}</span>'


def md_to_html(md):
    md = IDS.printed(md)          # production IDs never reach the page (Bible, ch. 112d §٥)
    notes = dict(re.findall(r"^\[\^(\d+)\]:\s*(.+)$", md, re.M))
    md = re.sub(r"^\[\^\d+\]:.*$", "", md, flags=re.M)
    md = re.sub(r"\[\^(\d+)\]", lambda m: f"⟦{m.group(1)}⟧", md)
    # the call hugs the word or quotation it documents; the full stop, comma or colon follows it
    md = re.sub(r"([.،؛:])((?:⟦\d+⟧)+)", r"\2\1", md)
    md = re.sub(r"^\*\*(أحمد بن إبراهيم السليمي)\*\*\n(.+)$",
                r'<div class="sig"><span class="sig-name">\1</span><span class="sig-du">\2</span></div>', md, flags=re.M)
    html = markdown.markdown(md, extensions=["tables"])
    html = ayat(html)
    soup = BeautifulSoup(html, "html.parser")
    for p in soup.find_all("p"):
        t = p.get_text().strip()
        if t.startswith("﴿") and p.find(class_="q") and len(p.find_all(class_="q")) == 1 and t.endswith(")"):
            p["class"] = ["ayah"]
    for bq in soup.find_all("blockquote"):
        txt = bq.get_text("\n").strip()
        if " ... " in txt:
            lines = [l.strip() for l in txt.split("\n") if " ... " in l]
            bq.clear()
            bq["class"] = ["poem"]
            for l in lines:
                a, b = l.split(" ... ")
                bq.append(BeautifulSoup(f'<div class="bayt"><span>{a}</span><span></span><span>{b}</span></div>', "html.parser"))
        elif txt.startswith("ما علّم"):
            bq["class"] = ["lesson"]
        elif txt.startswith("رأيتُ"):
            lines = [l.strip() for l in txt.split("\n") if l.strip()]
            bq.clear()
            bq["class"] = ["litany"]
            for l in lines:
                bq.append(BeautifulSoup(f'<div class="ln">{l}</div>', "html.parser"))
        elif txt == "«صناعة المتكلّم العربي»":
            bq["class"] = ["title-line"]
            bq.find("p").string = txt.strip("«»")
        elif txt.startswith("«") and is_hadith(bq, notes):
            bq["class"] = ["hadith"]
        elif txt.startswith("«"):
            bq["class"] = ["quote"]
        else:
            bq["class"] = ["def"]
    for p in soup.find_all("p"):
        t = p.get_text().lstrip()
        if t.startswith("فإن قيل"):
            p["class"] = (p.get("class") or []) + ["obj"]
        elif t.startswith(("قلنا", "قلتُ:")) and (prev := p.find_previous_sibling()) is not None and "obj" in (prev.get("class") or []):
            p["class"] = (p.get("class") or []) + ["ans"]
    # a heading never ends a page: it travels with the paragraph or display that follows it
    for h in soup.find_all("h3"):
        m = re.match(r"^([٠-٩]+)\.\s*", h.get_text())
        if m and h.string:
            h.string = h.string[m.end():]
            num = soup.new_tag("span", attrs={"class": "hn"}); num.string = m.group(1)
            h.insert(0, num)
    for h in soup.find_all("h3"):
        nxt = h.find_next_sibling()
        if nxt is not None and nxt.name in ("p", "blockquote"):
            keep = soup.new_tag("div", attrs={"class": "keep"})
            h.insert_before(keep)
            keep.append(h.extract())
            keep.append(nxt.extract())
    # the close of a chapter (its summary, or what follows from it) is set in its own panel, down to the next heading
    for h in soup.find_all("h3"):
        if not re.search(r"خلاصة|^ما يترتّب|^ما يُستخرج|^موقع هذا الكتاب", h.get_text().lstrip("٠١٢٣٤٥٦٧٨٩. ")):
            continue
        start = h.parent if h.parent is not None and "keep" in (h.parent.get("class") or []) else h
        panel = soup.new_tag("div", attrs={"class": "summary"})
        start.insert_before(panel)
        node = start
        while node is not None and node.name not in ("h2",) and not (node is not start and (node.name == "h3" or (node.name == "div" and node.find("h3", recursive=False)))):
            nxt = node.find_next_sibling()
            panel.append(node.extract())
            node = nxt
    # a run of short items (a list of acts, sounds, places) reads better in two columns
    for ul in soup.find_all("ul"):
        items = ul.find_all("li", recursive=False)
        if len(items) >= 5 and all(len(li.get_text()) <= 32 and not li.find("ul") for li in items):
            ul["class"] = ["cols"]
    latinize(soup)
    # «←» is in none of the book's faces: it is drawn, so no system font enters the page
    html = str(soup).replace("←", ARROW)
    html = re.sub(r"⟦(\d+)⟧", lambda m: note_span(m.group(1), notes[m.group(1)]), html)
    missing = set(notes) - set(re.findall(r'class="fn-note fn-n(\d+) ', html))
    if missing:
        raise SystemExit(f"notes defined but never called: {sorted(missing, key=int)}")
    return html, ""


def chapter(md, kicker):
    m = re.search(r"^##\s+(.+)$", md, re.M)
    title = m.group(1)
    title = re.sub(r"^الفصل [^:]+:\s*", "", title)
    body = md[m.end():]
    sub = re.search(r"<!--\s*sub:\s*(.+?)\s*-->", body)
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    html, notes = md_to_html(body)
    return f'<section class="chap"><div class="chap-open">{html}{notes}</div></section>', band(kicker, title, sub.group(1) if sub else "")


def band(kicker, title, sub=""):
    return (f'<section class="full"><div class="chap-band"><div class="k"><span>{kicker}</span><i></i></div>'
            f'<h2>{title}</h2>{f"<div class=sub>{sub}</div>" if sub else ""}<div class="dot"></div></div></section>')


def verse_poster(kick, ayah, ref):
    """A sapphire page that carries one verse in the mushaf face (never Changa or Kufam), with its reference."""
    return full(f'<div class="poster vp"><div class="kick"><span>{kick}</span><i></i></div><div class="vp-a">﴿{ayah}﴾</div>'
                f'<div class="vp-r">{ref}</div></div>', "dark")


def full(inner, cls=""):
    return f'<section class="full {cls}">{inner}</section>'


def heritage(who, quote, src):
    return full(f'<div class="her"><div class="her-in"><div class="who">{who}</div><div class="qt">{quote}</div><div class="src">{src}</div></div></div>')


def poster(kick, big, line, kufam=False, mid=False):
    return full(f'<div class="poster"><div class="kick"><span>{kick}</span><i></i></div><div class="big{" kufam" if kufam else ""}{" mid" if mid else ""}">{big}</div>'
                f'<div class="line">{line}</div></div>', "dark")


MEASURE = [("كم درستَ؟", "ماذا ملكتَ مما درست؟"),
           ("هل تعرف القاعدة؟", "هل تجري على لسانك حين تحتاج إليها؟"),
           ("هل تستطيع أن تكتب المعنى؟", "هل تستطيع أن تحمله إلى مخاطبك في وقته ومقامه؟"),
           ("هل تحفظ الفصيح؟", "هل تعرف متى تستعمله، وكيف، وبأيّ قدر؟")]


def measure_page():
    pairs = "".join(f'<div class="mz-pair"><div class="no">ليس السؤال: {a}</div><div class="yes">بل: {b}</div></div>' for a, b in MEASURE)
    return full(f'<div class="mz"><div class="mz-in"><div class="kick"><i></i><span>ميزان الملكة</span><i></i></div>{pairs}'
                f'<div class="coda">فالعبرة ليست بكم تعلّم الإنسان، وإنما بكيف تملّك ما تعلّم</div></div></div>')


CORE = [("النحو", "أبوابه ومسائله"), ("الصرف", "أبنيته وأحواله"), ("البلاغة", "المعاني · البيان · البديع"),
        ("الأدب العربي", "فنونه ونصوصه وعصوره"), ("فقه اللغة", "خصائص العربية وأصولها")]
SUPPORT = ["العروض والقافية", "علم اللغة", "علم الأصوات", "علم الدلالة", "تاريخ اللغة العربية", "اللهجات العربية", "تحقيق النصوص"]
SHARIA = ["علوم القرآن", "التفسير", "علوم الحديث", "العقيدة والتوحيد", "أصول الفقه", "الفقه"]


def sciences_page():
    """خريطة العلوم: the sciences themselves, not their chapters or the skills built from them (Bible, ch. 92).
    Five core sciences as petals round «علوم العربية», each with what falls under it in small type; the supporting
    sciences on an outer ring; the Sharia sciences, which Arabic serves, on a band beneath."""
    import math
    cx, cy, R, r, ring = 80.0, 66.0, 33.5, 15.5, 60.0
    svg, html = [], []
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="{ring}" fill="none" stroke="#C9A95C" stroke-width=".35" stroke-dasharray="1 1.6"/>')
    for k, (name, sub) in enumerate(CORE):
        ang = math.radians(-90 + k * 72)
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="rgba(201,169,92,.15)" stroke="#0C2766" stroke-width=".35"/>')
        html.append(f'<div class="sc-core" style="left:{x:.2f}mm;top:{y:.2f}mm"><b>{name}</b><span>{sub}</span></div>')
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="#0C2766"/>')
    html.append(f'<div class="sc-mid" style="left:{cx}mm;top:{cy}mm">علوم<br>العربية</div>')
    for k, name in enumerate(SUPPORT):
        ang = math.radians(-90 + 36 + k * (360 / len(SUPPORT)))
        x, y = cx + ring * math.cos(ang), cy + ring * math.sin(ang)
        html.append(f'<div class="sc-sup" style="left:{x:.2f}mm;top:{y:.2f}mm"><i></i>{name}</div>')
    h = cy + ring + 8
    draw = (f'<div class="sc-draw" style="height:{h:.1f}mm"><svg viewBox="0 0 160 {h:.1f}" style="position:absolute;inset:0;width:160mm;height:{h:.1f}mm">'
            f'{"".join(svg)}</svg>{"".join(html)}</div>')
    legend = ('<div class="sc-leg"><span><i class="c"></i>العلوم الأساسية</span><span><i class="s"></i>العلوم المساندة والتخصّصية</span></div>')
    band = "".join(f'<span>{x}</span>' for x in SHARIA)
    return full(f'<div class="mp"><div class="mp-in"><div class="kick"><i></i><span>خريطة علوم العربية وعلوم الشريعة</span><i></i></div>'
                f'{draw}{legend}<div class="sc-arrow">والعربية آلةٌ لعلوم الشريعة</div><div class="sc-band">{band}</div>'
                f'<div class="mp-note">في الخريطة العلوم وحدها؛ وأبوابها ومسائلها تحتها، والمهارات تتكوّن منها ومن الممارسة</div></div></div>')


FIXED_PAGES = {"ميزان الملكة": measure_page, "خريطة العلوم": sciences_page}
CONT_CSS = 'html, body { background: transparent !important; } @page :first { margin-top: 25mm; }'


def chapter_parts(md, kicker):
    """A chapter may carry <!-- page: name --> markers: the flow stops there for a full page, then runs on.
    Each part carries the notes it calls, so every note sits at the foot of the page of its call."""
    defs = dict(re.findall(r"^\[\^(\d+)\]:(.*)$", md, re.M))
    body = re.sub(r"^\[\^\d+\]:.*$", "", md, flags=re.M)
    chunks = re.split(r"<!--\s*page:\s*(.+?)\s*-->", body)
    called = set(re.findall(r"\[\^(\d+)\]", body))
    if set(defs) != called:
        raise SystemExit(f"notes and calls differ: {sorted(set(defs) ^ called, key=int)}")

    def with_notes(t, i):
        return t + "\n\n" + "\n".join(f"[^{n}]:{defs[n]}" for n in dict.fromkeys(re.findall(r"\[\^(\d+)\]", t)))

    parts = [("flow", chapter(with_notes(chunks[0], 0), kicker))]
    for k, (name, text) in enumerate(zip(chunks[1::2], chunks[2::2])):
        parts.append(("fixed", FIXED_PAGES[name]()))
        html, notes = md_to_html(with_notes(text, 2 * k + 2))
        parts.append(("cont", f'<section class="chap-cont">{html}{notes}</section>'))
    return parts


def author_word():
    md = AUTHOR_WORD.read_text(encoding="utf-8").replace("# كلمة المؤلف", "## كلمة المؤلف")
    return chapter(md, "الافتتاحية")


def contents(files):
    rows = []
    for f in files:
        m = re.search(r"^##\s+(.+)$", f.read_text(encoding="utf-8"), re.M)
        t = m.group(1)
        k, _, name = t.partition(":")
        rows.append(f'<div class="toc-row"><b>{k if name else ""}</b><span>{name.strip() or t}</span></div>')
    return (f'<section class="chap"><div class="chap-open"><p class="toc-p" style="text-indent:0">فصول المقدمة:</p>{"".join(rows)}</div></section>',
            band("المقدمة", "في صناعة الكلام"))


FIXED_CSS = "@page { size: %(w)smm %(h)smm; margin: 0; } html, body { margin: 0; }"
# the heads: the larger unit on a right-hand page, the chapter on a left-hand page (heads.py)
MUQ = [("label", "المقدمة"), ("title", "في صناعة الكلام")]


def same(title):
    return ([("title", title)], [("title", title)])
TP_MARK = '<div style="position:absolute;bottom:13mm;left:0;right:0">' + FM.mark() + '</div></section>'


PAGED = HERE / "vendor" / "paged.polyfill.min.js"   # Paged.js 0.4.3, MIT (vendor/paged.LICENSE.md)
CALLS = "\n".join(f'.fn-n{n}[data-footnote-call]::after {{ content: "{str(n).translate(AR)}"; }}' for n in range(1, 100))
# Paged.js lays the text out once every face is loaded, and says when it has finished (render.js waits for it)
PAGED_CONFIG = ("<script>window.PagedConfig = { auto: true, before: async () => { "
                "await Promise.all([...document.fonts].map(f => f.load().catch(() => null))); await document.fonts.ready; }, "
                "after: () => { window.__pagedDone = true; } };</script>")


def doc(css, body, page_css, paged=False):
    # a page that carries notes is paginated by Paged.js, which alone places a note at the foot of its page
    script = f'{PAGED_CONFIG}<script src="{PAGED.as_uri()}"></script>' if paged else ""
    return (f'<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>صناعة المتكلّم العربي</title>'
            f'<style>{css}</style><style>{CSS % dict(wrapw=0, wraph=0, calls=CALLS)}{C2.TEXT_CSS}{extra_css()}</style>'
            f'<style>{page_css}</style>{script}</head><body>{IDS.check(body)}</body></html>')


def flow(css, piece):
    body, bandhtml = piece
    # the text flows on a transparent page laid over a full-bleed paper (or band) underlay,
    # so the paper colour reaches the trim instead of stopping at the text block
    return (doc(css, body, "html, body { background: transparent !important; }", paged="fn-note" in body),
            doc(css, bandhtml, FIXED_CSS % dict(w=200, h=260)))


ABJAD = "أ ب ج د هـ و ز ح ط ي ك ل م ن س ع ف ص ق ر ش ت ث خ ذ ض ظ غ".split()


def folios(css, pages):
    """The overlay of heads and folios (heads.py): one page per page of the book after the case wrap."""
    measure = H.Measure(css)
    return doc(css, H.overlay(pages, measure),
               FIXED_CSS % dict(w=200, h=260) + " html, body { background: transparent !important; }" + H.CSS)


def head_of(md, n):
    """The chapter's head on a left-hand page: its number and its title, or the short form the chapter gives beside
    its title (<!-- head: … -->) when the title would reach the mark."""
    t = re.search(r"^##\s+(.+)$", md, re.M).group(1)
    short = re.search(r"<!--\s*head:\s*(.+?)\s*-->", md)
    title = short.group(1) if short else re.sub(r"^الفصل [^:]+:\s*", "", t)
    return [("label", "الفصل"), ("num", str(n).translate(AR)), ("title", title)]


def sections(md):
    """The numbered sections of a chapter (### ١. …), for the contents."""
    return [(m.group(1), m.group(2).strip()) for m in re.finditer(r"^###\s+([٠-٩]+)\.\s+(.+)$", md, re.M)]


def main():
    from pypdf import PdfReader
    css = C2.fonts()
    wrap, wmm, hmm = C2.wrap(css, 1, 48.2, dpi=300)
    everything = sorted(OPENING.glob("*.md"))
    files = [f for f in everything if f.name[:2] < "90"]          # the Muqaddima
    appendices = [f for f in everything if f.name[:2] >= "90"]    # ملحق التحقيق، ثبت المصادر
    fixed = FIXED_CSS % dict(w=200, h=260)
    R = {"recto": True}
    # (kind, html, meta): meta may ask the piece to open on a recto, and name it as a target of the contents
    pieces = [("wrap", doc(css, wrap, FIXED_CSS % dict(w=wmm, h=hmm)), {}),
              ("fixed", doc(css, FM.half_title(), fixed), R),
              ("fixed", doc(css, FM.volumes_map(), fixed), {}),
              ("fixed", doc(css, P2.title_page(css).replace('class="pg', 'class="full').replace("</section>", "") + TP_MARK, fixed), R),
              ("fixed", doc(css, FM.imprint(), fixed), {}),
              ("fixed", doc(css, FM.rights(), fixed), R),
              ("fixed", doc(css, FM.dedication(), fixed), {}),
              ("fixed", doc(css, P2.verse_page().replace('class="pg', 'class="full'), fixed), R),
              ("cont", doc(css, FM.publisher_word(), CONT_CSS), {"recto": True, "anchor": "publisher", "head": same("كلمة الناشر"), "opens": True}),
              ("flow", flow(css, author_word()), {"recto": True, "anchor": "author", "head": same("كلمة المؤلف")}),
              ("toc", None, {"recto": True, "head": same("المحتويات"), "opens": True}),
              ("cont", doc(css, FM.symbols(), CONT_CSS), {"recto": True, "anchor": "symbols", "head": same("الرموز والاصطلاحات"), "opens": True}),
              ("fixed", doc(css, poster("الافتتاحية", "المقدمة", "في صناعة الكلام: البيان في خلق الإنسان وفي الكتاب والسنة وعند علماء العربية، ومنزلة العربية وعلومها، والفرق بين أن تعرف اللغة وأن تملكها، وأيّ عربيةٍ نتكلّم.", kufam=True), fixed), {"recto": True, "anchor": "main"})]
    tamhid = files[0].read_text(encoding="utf-8").replace("# المقدمة: في صناعة الكلام\n", "")
    pieces.append(("flow", flow(css, chapter(tamhid, "المقدمة")), {"anchor": "01", "head": (MUQ, [("title", "تمهيد")])}))
    toc_rows = [("part", "", "المقدّمات"), ("e", "", "كلمة الناشر", "publisher", []), ("e", "", "كلمة المؤلف", "author", []), ("e", "", "الرموز والاصطلاحات", "symbols", []),
                ("part", "", "المقدمة: في صناعة الكلام"), ("e", "", "تمهيد", "01", [])]
    for n, f in enumerate(files[1:], 1):
        md = f.read_text(encoding="utf-8")
        if f.name.startswith("05-"):
            pieces.append(("fixed", doc(css, heritage("سيبويه", "«فمنه مستقيمٌ حسن، ومُحال، ومستقيمٌ كذب، ومستقيمٌ قبيح، وما هو مُحالٌ كذب»",
                                                     "الكتاب، باب الاستقامة من الكلام والإحالة"), fixed), {}))
        if f.name.startswith("07-"):
            pieces.append(("fixed", doc(css, verse_poster("العربية والوحي", "إِنَّا نَحْنُ نَزَّلْنَا ٱلذِّكْرَ وَإِنَّا لَهُۥ لَحَٰفِظُونَ", "(الحجر: ٩)"), fixed), {}))
        if f.name.startswith("10-"):
            pieces.append(("fixed", doc(css, poster("السؤال الذي وُلد منه الكتاب", "كيف نصنع المتكلّم العربي؟",
                                                    "لا: كيف نعلّم الطالب مزيدًا من العربية؛ بل: كيف نجعل العربية التي تعلّمها تظهر على لسانه حين يحتاج إليها، ثم يُحسن وضعها في موضعها.",
                                                    kufam=True, mid=True), fixed), {}))
        if f.name.startswith("11-"):
            pieces.append(("fixed", doc(css, poster("المقدمة", "فأين الخلل؟", "ليس في علم المتعلّم، ولا في عقله، ولا في دينه؛ بل في صناعةٍ لم تُعلَّم تعليمًا مقصودًا: أن يصير ما يعرفه كلامًا يُقال، لمن يُقال له، حين يُقال."), fixed), {}))
        if f.name.startswith("14-"):
            pieces.append(("fixed", doc(css, heritage("من الصحيفة المنسوبة إلى بشر بن المعتمر",
                                                     "«فيجعل لكلّ طبقةٍ من ذلك كلامًا، ولكلّ حالةٍ من ذلك مقامًا»", "رواها الجاحظ في البيان والتبيين"), fixed), {}))
        title = re.sub(r"^الفصل [^:]+:\s*", "", re.search(r"^##\s+(.+)$", md, re.M).group(1))
        key = f.name[:2]
        toc_rows.append(("e", f"الفصل {ORD[n]}", title, key, sections(md)))
        heads = (MUQ, head_of(md, n))
        for kind, part in chapter_parts(md, f"الفصل {ORD[n]}"):
            if kind == "flow":
                pieces.append(("flow", flow(css, part), {"anchor": key, "head": heads}))
            elif kind == "fixed":
                pieces.append(("fixed", doc(css, part, fixed), {}))
            else:
                pieces.append(("cont", doc(css, part, CONT_CSS, paged="fn-note" in part), {"head": heads}))
    toc_rows.append(("part", "", "الملاحق"))
    for f in appendices:
        md = f.read_text(encoding="utf-8")
        title = re.search(r"^##\s+(.+)$", md, re.M).group(1).strip()
        key = f.name[:2]
        toc_rows.append(("e", "", title, key, sections(md)))
        for kind, part in chapter_parts(md, "الملاحق"):
            if kind == "flow":
                body, bandhtml = part
                part = (body.replace('<section class="chap">', f'<section class="chap app-{key}">', 1), bandhtml)
                pieces.append(("flow", flow(css, part), {"recto": True, "anchor": key, "head": ([("title", "الملاحق")], [("title", title)])}))
    pieces.append(("fixed", doc(css, FM.colophon(), fixed), {"recto": True}))

    def toc_html(numbers):
        rows = []
        for r in toc_rows:
            if r[0] == "part":
                rows.append(r)
            else:
                rows.append(("e", r[1], r[2], numbers.get(r[3], "٠٠٠"), r[4]))
        return doc(css, FM.contents(rows), CONT_CSS, paged=True)

    paper = B.render(doc(css, '<div style="width:200mm;height:260mm;background:var(--paper)"></div>', fixed), "opening-paper")
    blank = PdfReader(str(paper)).pages[0]
    out, anchors, toc_slot = [], {}, None   # out: [(page, kind, heads)]; the first entry is the case wrap
    for i, (kind, html, meta) in enumerate(pieces):
        hd = meta.get("head")
        if meta.get("recto") and len(out) >= 1 and len(out) % 2 == 0:
            out.append((PdfReader(str(paper)).pages[0], "blank", None))   # the next page would be a verso: leave it white
        if meta.get("anchor"):
            anchors[meta["anchor"]] = len(out)
        if kind == "toc":
            r = PdfReader(str(B.render(toc_html({}), "opening-toc")))
            toc_slot = (len(out), len(r.pages[:body_pages(r)]))
            for pg in r.pages[:toc_slot[1]]:
                out.append((pg, "toc", hd))
            continue
        if kind == "flow":
            body, bandhtml = html
            r = PdfReader(str(B.render(body, f"opening-{i:02d}")))
            band = B.render(bandhtml, f"opening-{i:02d}-band")
            for j, pg in enumerate(r.pages[:body_pages(r)]):
                under = PdfReader(str(band if j == 0 else paper)).pages[0]
                under.merge_page(pg)
                out.append((under, "open" if j == 0 else "flow", hd))
            continue
        r = PdfReader(str(B.render(html, f"opening-{i:02d}")))
        for j, pg in enumerate(r.pages[:body_pages(r)] if kind == "cont" else r.pages):
            if kind == "cont":
                under = PdfReader(str(paper)).pages[0]
                under.merge_page(pg)
                pg = under
            # a piece that opens under its own title (كلمة الناشر، الرموز) has no head on that page, as a chapter has none
            out.append((pg, ("open" if meta.get("opens") and j == 0 else "flow") if kind == "cont" else kind, hd))
    # the preliminaries are counted in abjad letters from the half-title; the text is counted from ١ at the Muqaddima
    main_at = anchors["main"]
    label = [""] + [ABJAD[i - 1] if i < main_at else str(i - main_at + 1).translate(AR) for i in range(1, len(out))]
    numbers = {a: label[ix] for a, ix in anchors.items()}
    r = PdfReader(str(B.render(toc_html(numbers), "opening-toc")))
    if len(r.pages[:body_pages(r)]) != toc_slot[1]:
        raise SystemExit("the contents changed length when its page numbers were filled in")
    for k in range(toc_slot[1]):
        under = PdfReader(str(paper)).pages[0]
        under.merge_page(r.pages[k])
        out[toc_slot[0] + k] = (under, "open" if k == 0 else "flow", out[toc_slot[0] + k][2])
    # the heads and folios, drawn last: page i (after the wrap) is a left-hand page when i is odd
    style = {"flow": "run", "open": "open"}
    measure = H.Measure(css)
    marks = []
    for i in range(1, len(out)):
        st, hd = style.get(out[i][1], ""), out[i][2]
        parts = None
        if st == "run" and hd:
            parts = hd[1] if i % 2 else hd[0]
            if not measure.fits(parts):
                raise SystemExit(f"the head reaches the mark ({measure.head(parts):.1f} mm of {H.REACH:.1f}): {parts}"
                                 " — give the chapter a short head: <!-- head: … -->")
        marks.append((label[i], st, parts, "odd" if i % 2 else "even"))
    fr = PdfReader(str(B.render(folios(css, marks), "opening-folios")))
    from pypdf import PdfWriter
    w = PdfWriter()
    for i, (pg, _, _) in enumerate(out):
        if i and marks[i - 1][1]:
            pg.merge_page(fr.pages[i - 1])
        w.add_page(pg)
    w.add_metadata({"/Title": "صناعة المتكلّم العربي — المجلد الأول: الافتتاحية", "/Author": "أحمد بن إبراهيم السليمي",
                    "/Publisher": FM.PUBLISHER_EN})
    w.write(str(OUT))
    guard_fonts(OUT)
    print(OUT, len(w.pages), "pages")


def body_pages(reader):
    """Paged.js may close a flow with a page that holds nothing but the running heads: it is not a page of the book."""
    n = len(reader.pages)
    while n > 1 and len("".join((reader.pages[n - 1].extract_text() or "").split())) < 60:
        n -= 1
    return n


def guard_fonts(pdf):
    """Stop if any glyph fell back to a system font: every face in the book is one we chose."""
    from pypdf import PdfReader
    bad = set()
    for pg in PdfReader(str(pdf)).pages:
        for f in ((pg.get("/Resources") or {}).get("/Font") or {}).values():
            name = str(f.get_object().get("/BaseFont"))
            if any(x in name for x in ("DejaVu", "Liberation", "FreeSerif", "FreeSans", "Noto")):
                bad.add(name.split("+")[-1])
    if bad:
        raise SystemExit(f"system fonts in the PDF: {sorted(bad)}")


def extra_css():
    """Styles the borrowed title and verse pages need (from proto2), scoped to .full pages."""
    keep = []
    for sel in (".tp-band", ".tp-sub", ".tp-desc", ".tp-vol", ".tp-auth", ".verse", ".kufi", ".gold-foil", ".qref"):
        for m in re.finditer(r"(?m)^" + re.escape(sel) + r"[^{]*\{[^}]*\}", P2.CSS.replace("%%", "%")):
            keep.append(m.group(0))
    return "\n".join(keep).replace("var(--read)", '"Scheherazade New"').replace("var(--sans)", '"IBM Plex Sans Arabic"').replace("var(--quran)", '"Amiri Quran"')


if __name__ == "__main__":
    main()
