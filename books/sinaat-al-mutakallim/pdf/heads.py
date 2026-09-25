#!/usr/bin/env python3
"""The running head and the folio of every volume (Bible, part sixteen, ch. 117b): one geometry, drawn last, over the
assembled pages, where each page knows at last whether it is a left-hand or a right-hand page.

    the lintel   at the outer edge, the unit the reader is in (the larger unit on the right-hand page, the chapter on
                 the left-hand page); at the inner edge, the series' name, smaller and quieter; beneath them one gold
                 rule the width of the text, heavy under the title and light under the name, meeting at the mark
    the mark     a rhombic dot within a rhombus three dots wide: the dot of the pen, by which the proportioned script
                 measured its letters; it stands in the page's axis, the same on every page of every volume
    the folio    the rule in little, heavy outward and light inward, with the number in the mark's place; on a page
                 that opens a chapter, and so has no head, the mark comes down to the foot and stands over the number
    parity       the book is bound on the right: page 1 is a left-hand page, so an odd page has its outer edge on the
                 left and an even page on the right, and the head is mirrored between them

A head is a list of parts: ("label", "الفصل"), ("num", "١٤"), ("title", "…"), set «الفصل ١٤: …». The builder measures every head
(fits()) and stops if one would reach the mark; a chapter whose title is too long carries its short form beside its
title in the manuscript: <!-- head: … -->.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lettering as L  # noqa: E402

PT = 0.3528                       # mm in a point
PAGE_W, PAGE_H = 200.0, 260.0
MARGIN = 39.0                     # the text block: 122 mm, centred
TEXT_W = PAGE_W - 2 * MARGIN
RULE_Y = 18.2                     # the rule's centre line, 6.8 mm above the text block
MARK_R = 1.8                      # half the rhombus' diagonal: three dots of 1.2 mm
GAP = 0.8                         # between the rhombus and the rule
HEAVY, LIGHT = 0.8, 0.35          # the rule's two weights, in points
REACH = TEXT_W / 2 - MARK_R - 6.0  # how far a head may run from its edge: 6 mm of paper stay round the mark
FOLIO_ARM = 9.0                   # each arm of the folio's rule
SERIES = "صناعة المتكلّم العربي"
SALUTATIONS = "ﷺ"                  # set in Amiri: Changa has no glyph for them

GOLD, GOLD_INK, PAPER = "#C9A95C", "#8A6A1F", "#F8F6F1"
SAPPHIRE, SAPPHIRE_2, QUIET, INK = "#0C2766", "#2B4A8F", "#6B7390", "#1C1915"

CSS = f"""
.hd-page {{ position: relative; width: {PAGE_W}mm; height: {PAGE_H}mm; break-after: page; }}
.hd {{ position: absolute; top: 12.15mm; left: {MARGIN}mm; right: {MARGIN}mm; direction: rtl; display: flex;
  justify-content: space-between; align-items: baseline; white-space: nowrap; }}
.hd-o {{ font: 500 8.3pt/1 "Changa"; color: {SAPPHIRE}; }}
.hd-o .l {{ font-weight: 300; color: {SAPPHIRE_2}; }}
.hd-o .n {{ font: 400 9pt/1 "Amiri"; }}
.hd-o .s {{ font: 400 8.6pt/1 "Amiri"; }}
.hd-i {{ font: 300 7.3pt/1 "Changa"; color: {QUIET}; }}
.hd-rule, .fo-rule, .fo-mark {{ position: absolute; overflow: visible; }}
.fo-n {{ position: absolute; left: 0; right: 0; text-align: center; font: 400 10.5pt/1 "Amiri"; color: {INK}; }}
.fo-n.open {{ font-size: 9.2pt; color: {GOLD_INK}; }}
"""


def rhombus(cx, cy, r):
    return f"{cx - r:.3f},{cy:.3f} {cx:.3f},{cy - r:.3f} {cx + r:.3f},{cy:.3f} {cx:.3f},{cy + r:.3f}"


def mark(cx, cy, r=MARK_R, stroke=0.45):
    """The rhombic dot within its rhombus."""
    return (f'<polygon points="{rhombus(cx, cy, r)}" fill="none" stroke="{GOLD}" stroke-width="{stroke * PT:.3f}"/>'
            f'<polygon points="{rhombus(cx, cy, r / 3)}" fill="{GOLD}"/>')


def rule(x0, x1, cy, weight):
    return (f'<line x1="{x0:.3f}" y1="{cy:.3f}" x2="{x1:.3f}" y2="{cy:.3f}" stroke="{GOLD}" '
            f'stroke-width="{weight * PT:.3f}"/>')


def outer_edge_left(parity):
    return parity == "odd"


def mirrored(width, parity, inner):
    """Drawings are made with the outer edge at x = 0; a right-hand page turns them over."""
    return inner if outer_edge_left(parity) else f'<g transform="translate({width},0) scale(-1,1)">{inner}</g>'


def head_parts_html(parts):
    """label and number in the light weight, then a colon, as the book writes its own headings («الفصل ١٤: …»);
    no dot beside the number, which an Eastern reader takes for a zero (Bible, ch. 23, rule 9)."""
    out, lead = [], []
    for kind, text in parts:
        if kind == "label":
            lead.append(text)
        elif kind == "num":
            lead.append(f'<span class="n">{text}</span>')
        elif kind == "title":
            for s in SALUTATIONS:
                text = text.replace(s, f'<span class="s">{s}</span>')
            out.append(text)
    if lead and out:
        return f'<span class="l">{" ".join(lead)}:</span> {out[0]}'
    return out[0] if out else f'<span class="l">{" ".join(lead)}</span>'


def head(parts, parity):
    """The lintel: the title outward, the series' name inward, and the rule of two weights with the mark between."""
    c = TEXT_W / 2
    drawing = rule(0, c - MARK_R - GAP, 1.8, HEAVY) + rule(c + MARK_R + GAP, TEXT_W, 1.8, LIGHT) + mark(c, 1.8)
    svg = (f'<svg class="hd-rule" viewBox="0 0 {TEXT_W} 3.6" style="left:{MARGIN}mm;top:{RULE_Y - 1.8}mm;'
           f'width:{TEXT_W}mm;height:3.6mm">{mirrored(TEXT_W, parity, drawing)}</svg>')
    title = f'<div class="hd-o">{head_parts_html(parts)}</div>'
    series = f'<div class="hd-i">{SERIES}</div>'
    # the row runs right to left: its first child stands at the right-hand edge
    row = series + title if outer_edge_left(parity) else title + series
    return svg + f'<div class="hd">{row}</div>'


def folio(text, style, parity, width):
    """style "run": the number on the rule in little; "open": the mark over the number; "": counted, not shown.
    width: the number's measured width in mm, so the arms keep the same distance from any number."""
    if style == "run":
        box, c, cy = 2 * (FOLIO_ARM + 8), FOLIO_ARM + 8, 1.0
        near = width / 2 + 2.4
        drawing = rule(c - near - FOLIO_ARM, c - near, cy, HEAVY) + rule(c + near, c + near + FOLIO_ARM, cy, LIGHT)
        svg = (f'<svg class="fo-rule" viewBox="0 0 {box} 2" style="left:{PAGE_W / 2 - c}mm;top:{PAGE_H - 17.15}mm;'
               f'width:{box}mm;height:2mm">{mirrored(box, parity, drawing)}</svg>')
        return svg + f'<div class="fo-n" style="top:{PAGE_H - 17.8}mm">{text}</div>'
    if style == "open":
        svg = (f'<svg class="fo-mark" viewBox="0 0 6 4" style="left:{PAGE_W / 2 - 3}mm;top:{PAGE_H - 21.7}mm;'
               f'width:6mm;height:4mm">{mark(3, 2, 1.4, 0.4)}</svg>')
        return svg + f'<div class="fo-n open" style="top:{PAGE_H - 16.8}mm">{text}</div>'
    return ""


class Measure:
    """Widths of heads and numbers, shaped with HarfBuzz in the book's own faces."""

    def __init__(self, font_css):
        self.changa3 = L.arabic_face(font_css, "Changa", 300)
        self.changa5 = L.arabic_face(font_css, "Changa", 500)
        self.amiri = L.arabic_face(font_css, "Amiri", 400)

    def number(self, text):
        return L.Line(text, self.amiri, 10.5 * PT).width if text else 0.0

    def head(self, parts):
        lead = [t for k, t in parts if k in ("label", "num")]
        titles = [t for k, t in parts if k == "title"]
        w = 0.0
        for kind, text in parts:
            if kind == "label":
                w += L.Line(text, self.changa3, 8.3 * PT).width
            elif kind == "num":
                w += L.Line(" " + text, self.amiri, 9 * PT).width
            elif kind == "title":
                plain = text
                for s in SALUTATIONS:
                    plain = plain.replace(s, "")
                w += L.Line(plain, self.changa5, 8.3 * PT).width + 3.2 * sum(text.count(s) for s in SALUTATIONS)
        if lead and titles:
            w += L.Line(": ", self.changa3, 8.3 * PT).width
        return w

    def fits(self, parts):
        return self.head(parts) <= REACH


def overlay(pages, measure):
    """pages: one (text, style, head, parity) per page. Returns the body of the overlay document."""
    out = []
    for text, style, parts, parity in pages:
        inner = folio(text, style, parity, measure.number(text))
        if style == "run" and parts:
            inner = head(parts, parity) + inner
        out.append(f'<section class="hd-page">{inner}</section>')
    return "".join(out)
