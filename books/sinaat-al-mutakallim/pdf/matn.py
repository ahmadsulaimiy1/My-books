#!/usr/bin/env python3
"""«المتن والحاشية» — the master of the covers (Bible, ch. 25 §13): the architecture of the scholar's page.

The front is a page as the Arabic scholarly book builds one: the matn (the text) raised at its heart, ruled round
in gold and pearl, and carrying the title; round it the margins, where the volume's own words run as the
scholar's glosses (الحواشي), set on gold rulings, the head and foot level and the sides slanting as a commentator
slants them; the seams where the glosses turn are gold beams, jewelled at both ends. The words are the volume's
own opening, set in the three layers of Arabic writing: the rasm (the letters' bodies) is left latent, pressed as
a gloss whisper into the sapphire; the dots (the i'jam, which tell one letter's sound from another's) are lit in
gold; the vowels (the shakl, first marked, in the account attributed to Abu al-Aswad, as red dots, to keep the
tongue from error) are ruby. The title is the one line fully voiced.

الصوت → اللفظ → العبارة → البيان → الأثر: the dots are the sound; the silent rasm the utterance not yet spoken;
the ruled lines the phrase; the matn and its title the clarity at the centre; the glosses the trace a text leaves
in those who comment on it. Across the series the voice spreads: on the first volume only a halo of dots round the
matn is lit, and each volume lights more of its page, until the tenth is lit to its edges; the reference sets its
margins as an index. On the spines the glosses run at one height from volume to volume, so the shelf is one page.
"""
from __future__ import annotations

import math
import re
from functools import lru_cache

import numpy as np
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import unary_union

import artwork as AW
import frontmatter as FM
import illumination as IL
import typeset as T
from marks import bevel, device, margins

W, H = 170.0, 240.0
HARAKAT = re.compile(r"[ً-ْٰ]")
GLOSS_SIZE, GLOSS_LEAD = 2.9, 4.25
MATN = (42.0, 42.0, W - 36.0, 166.0)          # the front's text block: toward the spine, the wide margin outside
FIELD_INSET = 9.5 + 3.6


@lru_cache(maxsize=1)
def faces():
    return T.Faces()


# ------------------------------------------------------------------------------------------------ the words
@lru_cache(maxsize=None)
def paragraphs(n):
    """The volume's own opening, as paragraphs; the reference sets the index of the series instead."""
    from volumes import VOLUMES, unit_files
    if n == 11:
        return index_paragraphs()
    t = unit_files(n, VOLUMES[n - 1]["units"][0])[0].read_text(encoding="utf-8")
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"﴿[^﴾]*﴾", "", t)                 # the Qur'an is never set as texture
    t = re.sub(r"\[[^\]]*\]", "", t)
    t = re.sub(r"[#>*`_«»]", "", t)
    paras = [clean(p) for p in t.split("\n") if len(p.strip()) > 80 and "السؤال الذي يجيب" not in p]
    return tuple(p for p in paras if len(p) > 60)


def clean(text):
    """Keep what the Arabic face sets: its letters, marks, digits and punctuation; drop the rest (rules of tables,
    brackets, Latin), and close up the spaces."""
    cmap = faces().amiri4.cmaps[0]
    kept = "".join(ch if (ord(ch) in cmap and ch not in "|()[]{}<>/\\") or ch == " " else " " for ch in text)
    return re.sub(r"\s+", " ", kept).strip()


def index_paragraphs():
    """The reference's margins: the ten volumes, each with its number, its name and what it holds."""
    from volumes import VOLUMES
    ar = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")
    return tuple(clean(f"{str(v['n']).translate(ar)} {v['name']}، {v['sentence']}") for v in VOLUMES[:10])


class Words:
    """The words in order, paragraph by paragraph, round and round."""

    def __init__(self, paras):
        self.paras, self.p, self.w = list(paras), 0, 0
        self.cur = self.paras[0].split()
        self.opening = True

    def take(self):
        if self.w >= len(self.cur):
            self.p = (self.p + 1) % len(self.paras)
            self.cur, self.w, self.opening = self.paras[self.p].split(), 0, True
            return None
        w = self.cur[self.w]
        self.w += 1
        return w

    def back(self):
        self.w -= 1


def shaped(text, size, x_right, base):
    """A line in its three layers: the rasm, the dots (centre and count of each group), the vowels; and its width."""
    F = faces()
    path = F.amiri4.files[0]
    plain = HARAKAT.sub("", text)
    runs, w = T.glyph_runs(plain, path, size, features=T.KF)
    body = [T.segs_to_geom(s) for (c, s) in runs]
    body = [g for g in body if not g.is_empty]
    if not body:
        return None, [], None, w
    allp = affinity.translate(AW.valid(unary_union(body)), x_right - w, base)
    rasm, dots = [], []
    for p in AW.poly_list(allp):
        bx0, by0, bx1, by1 = p.bounds
        if (by1 - by0) < 0.17 * size and (bx1 - bx0) < 0.30 * size and p.area < 0.028 * size * size:
            k = len(AW.poly_list(p.buffer(-0.035 * size)))
            dots.append(((bx0 + bx1) / 2, (by0 + by1) / 2, max(1, min(3, k))))
        else:
            rasm.append(p)
    har = None
    if HARAKAT.search(text):
        runs2, w2 = T.glyph_runs(text, path, size, features=T.KF)
        g2 = [T.segs_to_geom(s) for (c, s) in runs2]
        full = affinity.translate(AW.valid(unary_union([g for g in g2 if not g.is_empty])), x_right - w2, base)
        keep = []
        for p in AW.poly_list(AW.valid(full.difference(allp.buffer(0.06)))):
            bx0, by0, bx1, by1 = p.bounds
            if 0.003 * size * size < p.area < 0.03 * size * size and (bx1 - bx0) < 0.45 * size and (by1 - by0) < 0.4 * size:
                keep.append(p)
        har = AW.valid(unary_union(keep)) if keep else None
    return (AW.valid(unary_union(rasm)) if rasm else None), dots, har, w


def dot_group(dx, dy, k, size):
    """The dots of one group as the nib makes them, at the pen's angle."""
    s = 0.32 * size
    if k == 1:
        pts = [(dx, dy)]
    elif k == 2:
        pts = [(dx - 0.14 * size, dy), (dx + 0.14 * size, dy)]
    else:
        pts = [(dx - 0.14 * size, dy + 0.06 * size), (dx + 0.14 * size, dy + 0.06 * size), (dx, dy - 0.13 * size)]
    return [AW.nuqta(px, py, s, 70) for (px, py) in pts]


@lru_cache(maxsize=None)
def word_width(word, size):
    return T.line(HARAKAT.sub("", word), faces().amiri4, size).width


@lru_cache(maxsize=None)
def space_width(size):
    return T.line("ب ب", faces().amiri4, size).width - 2 * T.line("ب", faces().amiri4, size).width


def plain_width(text, size):
    """The width of a line of glosses, from its words measured once each (the fitting asks it word by word)."""
    ws = text.split()
    return sum(word_width(w, size) for w in ws) + space_width(size) * max(0, len(ws) - 1)


# ------------------------------------------------------------------------------------------------ the glosses
class Acc:
    def __init__(self):
        self.rules, self.rasm, self.dots, self.vowels, self.marks, self.digits = [], [], [], [], [], []


def gloss(region, angle, words, acc, size=GLOSS_SIZE, lead=GLOSS_LEAD, numerals=False):
    """Fill region with lines of the words at angle (degrees), each on its ruling, right to left, top to bottom."""
    cx, cy = region.centroid.x, region.centroid.y
    rr = affinity.rotate(region, -angle, origin=(cx, cy))
    x0, y0, x1, y1 = rr.bounds
    rot = (lambda q: affinity.rotate(q, angle, origin=(cx, cy))) if angle else (lambda q: q)
    y = y0 + lead * 0.9
    off = 0.55
    while y < y1 - 0.2:
        chord = rr.intersection(LineString([(x0 - 1, y + off), (x1 + 1, y + off)]))
        if chord.is_empty:
            y += lead
            continue
        cs = list(chord.geoms) if hasattr(chord, "geoms") else [chord]
        c = max(cs, key=lambda c: c.length)
        a, b = c.bounds[0] + 0.3, c.bounds[2] - 0.3
        if b - a < 3.5:
            y += lead
            continue
        acc.rules.append(rot(box(a, y + off - 0.05, b, y + off + 0.05)))
        head = words.opening
        indent = 1.5 if head else 0.0
        lw = []
        while True:
            w_ = words.take()
            if w_ is None:
                break
            words.opening = False
            if plain_width(" ".join(lw + [w_]), size) > (b - a - indent):
                words.back()
                break
            lw.append(w_)
        if lw:
            if head:
                acc.marks.append(rot(AW.nuqta(b - 0.55, y - 0.28 * size, 0.95, 70)))
            ras, dots, har, _ = shaped(" ".join(lw), size, b - indent, y)
            if ras is not None:
                acc.rasm.append(rot(ras))
            for (dx, dy, k) in dots:
                acc.dots += [rot(q) for q in dot_group(dx, dy, k, size)]
            if har is not None:
                acc.vowels.append(rot(har))
            if numerals:
                for m in re.finditer(r"^[0-9٠-٩]+", " ".join(lw)):
                    g, _ = T.text(m.group(0), faces().amiri7, size * 1.15, x_right=b - indent, base=y, digits=True)
                    acc.digits.append(rot(g))
        y += lead


def voice_reach(n):
    """How far from the matn the voice has spread on volume n (mm): a halo on the first, the whole page on the
    tenth and on the reference."""
    return 6.0 + (min(n, 10) - 1) * (70.0 / 9.0)


def lay_gloss(P, acc, clip, halo=None):
    """The glosses' materials: rulings in satin gold; the rasm a gloss whisper in the sapphire's own tone; the dots
    gold where the voice has reached and a whisper where not; the vowels ruby where it has reached."""
    def u(gs):
        gs = [g for g in gs if g is not None and not g.is_empty]
        return AW.valid(unary_union(gs)).intersection(clip) if gs else None
    rules, rasm, dots, vowels, marks = u(acc.rules), u(acc.rasm), u(acc.dots), u(acc.vowels), u(acc.marks)
    if rules is not None:
        P.cold(rules, 0.85)
    if rasm is not None:
        P.L.uv.append(rasm)
        P.L.body.append((rasm, ("lift", 0.06)))
    if dots is not None:
        lit = dots if halo is None else dots.intersection(halo)
        if not lit.is_empty:
            P.gold(lit)
            P.emboss(lit, 0.8)
        if halo is not None:
            P.L.uv.append(AW.valid(dots.difference(halo)))
    if vowels is not None:
        v = vowels if halo is None else vowels.intersection(halo)
        if not v.is_empty:
            P.ruby(v)
    if marks is not None:
        P.gold(marks)
    if acc.digits:
        d = u(acc.digits)
        if d is not None:
            P.gold(d)


# ------------------------------------------------------------------------------------------------ the parts of the page
def jewel(P, x, y, size, phi=70.0, material="gold"):
    """The nib's dot cut as a jewel: the rhombus, its four facets parted by fine lines, pressed up."""
    d = AW.nuqta(x, y, size, phi)
    a = math.radians(phi)
    ux, uy = math.cos(a) * size / 2, -math.sin(a) * size / 2
    vx, vy = math.sin(a) * size * 0.36, math.cos(a) * size * 0.36
    cuts = unary_union([LineString([(x + ux, y + uy), (x - ux, y - uy)]).buffer(0.05),
                        LineString([(x + vx, y + vy), (x - vx, y - vy)]).buffer(0.05)])
    {"gold": P.gold, "pearl": P.pearl, "ruby": P.ruby}[material](d.difference(cuts))
    bevel(P, d, depth=min(1.0, size * 0.22), steps=3)
    return d


def tajdwil(P, rect, w=0.8):
    """The page's ruled frame: gold, pearl, and a satin rule within (the ruby is kept for what it means)."""
    P.gold(IL.band(rect, 0, -w, join=2))
    P.pearl(IL.band(rect, -w - 0.9, -w - 1.06, join=2))
    P.cold(IL.band(rect, -w - 1.7, -w - 1.82, join=2), 0.8)


def matn_block(P, rect, pad=3.4, rulings=None):
    """The matn raised, ruled round in gold (sculpted), pearl, satin and a gold hairline; its own rulings pressed
    blind behind what is written in it. Returns the block and its margin (what the glosses keep clear of)."""
    mb = box(*rect)
    m = mb.buffer(pad, join_style=2)
    P.panel(mb, 0.14)
    bevel(P, mb, top=0.55, base=0.15, depth=3.4, steps=7)
    jad = IL.band(mb, 0.0, -1.0, join=2)
    P.gold(jad)
    bevel(P, jad, top=1.0, base=0.6, depth=0.4, steps=2)
    P.pearl(IL.band(mb, -1.8, -1.96, join=2))
    P.cold(IL.band(mb, -2.6, -2.72, join=2), 0.8)
    P.gold(IL.band(mb, -3.3, -3.45, join=2))
    P.gold(IL.band(m, 0.0, -0.3, join=2))
    if rulings:
        inner = mb.buffer(-5.0, join_style=2)
        x0, y0, x1, y1 = inner.bounds
        rl = [box(x0, y - 0.06, x1, y + 0.06) for y in rulings if y0 < y < y1]
        if rl:
            R = AW.valid(unary_union(rl))
            P.L.deboss.append(R)
            P.L.body.append((R, ("lift", 0.05)))
    return mb, m


def seams(P, field, m, beam=0.6):
    """The seams where the glosses turn: gold beams from the corners of the page to the corners of the matn."""
    fx0, fy0, fx1, fy1 = field.bounds
    mx0, my0, mx1, my1 = m.bounds
    for (a, b) in (((fx0, fy0), (mx0, my0)), ((fx1, fy0), (mx1, my0)), ((fx0, fy1), (mx0, my1)), ((fx1, fy1), (mx1, my1))):
        ln = LineString([a, b])
        bm = ln.buffer(beam, cap_style=2)
        P.gold(bm.difference(ln.buffer(0.07)))
        bevel(P, bm, depth=beam, steps=3)
        jewel(P, b[0], b[1], 3.6)
        jewel(P, a[0] + (2.2 if a[0] < W / 2 else -2.2), a[1] + (2.2 if a[1] < H / 2 else -2.2), 4.4)


# ------------------------------------------------------------------------------------------------ the front
def front(n):
    """The front of volume n. Returns the page and its field."""
    F = faces()
    P = _page()
    outer = box(9.5, 9.5, W - 9.5, H - 9.5)
    tajdwil(P, outer)
    field = outer.buffer(-3.6, join_style=2)
    mb, m = matn_block(P, MATN, rulings=[93.0, 114.0, 126.5, 143.0, 156.0])
    angles = (0, 0, 0, 0) if n == 11 else (0, 45, 0, 45)
    words = Words(paragraphs(n))
    acc = Acc()
    for reg, ang in margins(field, m, angles):
        gloss(reg, ang, words, acc, numerals=(n == 11))
    halo = None if n >= 10 else m.buffer(voice_reach(n), join_style=2)
    lay_gloss(P, acc, AW.valid(field.difference(m)), halo)
    seams(P, field, m)
    cx = (MATN[0] + MATN[2]) / 2
    ordinal, name = FM.VOLUMES[n - 1][:2]
    label = "مرجع المتكلّم العربي" if n == 11 else name
    rub, _ = T.text(f"المجلد {ordinal}", F.changa4, 3.0, cx=cx, base=63.0)
    P.ink(rub, AW.CHAMPAGNE_INK)
    import coverart as CA
    CA.set_title(P, cx, [("صناعة", 18.5, 93.0), ("المتكـلّم العربي", 11.2, 114.0)])
    sub, _ = T.text(FM.SUBTITLE, F.sch4, 3.9, cx=cx, base=126.5)
    P.ink(sub, AW.PEARL_SOFT)
    size = 4.8 * min(1.0, 80.0 / T.line(label, F.changa5, 4.8).width)
    nm, _ = T.text(label, F.changa5, size, cx=cx, base=143.0)
    P.champagne(nm)
    au, _ = T.text(FM.AUTHOR_SHORT, F.sch6, 3.8, cx=cx, base=156.0)
    P.ink(au, AW.PEARL_INK)
    P.L.glow.append((cx, 104.0, 64.0, 0.95))
    P.arch.append(field.buffer(0))
    return P, field


def _page():
    import coverart as CA
    return CA.Page()


# ------------------------------------------------------------------------------------------------ the spine
SPINE_BANDS = (6.6, 8.0)
SPINE_COMPS = [(11.5, 51.0), (54.0, 102.0), (105.0, 118.0), (121.0, 197.0), (200.0, 229.5)]
SHELF_RULES = np.arange(124.0, 195.0, GLOSS_LEAD)


def spine(n, sw):
    """The spine of volume n, sw wide (x from its front edge, y from the page's head): the title; the page device
    with the volume's numeral; the name; the glosses, whose rulings run at one height along the shelf; the author
    and the house."""
    import coverart as CA
    F = faces()
    P = _page()
    cx = sw / 2
    mwid = sw - 2 * 3.0
    for yb in SPINE_BANDS + (H - SPINE_BANDS[1], H - SPINE_BANDS[0]):
        P.gold(box(-0.2, yb - 0.16, sw + 0.2, yb + 0.16))
    for (a, b) in SPINE_COMPS:
        r = box(1.9, a, sw - 1.9, b)
        P.pearl(IL.band(r, 0.0, -0.16))
        P.gold(box(0.8, a - 1.05, sw - 0.8, a - 0.75))
        P.gold(box(0.8, b + 0.75, sw - 0.8, b + 1.05))
    fit = min(1.0, (mwid - 1.0) / 26.0)
    CA.set_title(P, cx, [("صناعة", 7.6 * fit, 26.5), ("المتكلّم", 5.0 * fit, 37.0), ("العربي", 5.0 * fit, 46.0)],
                 floriation=False, emboss=True, dot_scale=1.5)
    dw = min(sw - 6.0, 30.0)
    device(P, cx, 78.0, dw, min(44.0, dw * 1.4), n=n, lit=min(n, 10) / 10.0, numeral=n)
    ordinal, name = FM.VOLUMES[n - 1][:2]
    label = {8: "المجالس والمنبر", 11: "المرجع"}.get(n, name)
    ln = T.line(label, F.kufi6, 5.0, features=T.KF)
    size = 5.0 * min(1.0, (mwid - 1.0) / ln.width)
    ng, _ = T.text(label, F.kufi6, size, cx=cx, base=113.8, features=T.KF)
    P.pearl(ng)
    # the glosses of the shelf: the rulings at one height on every spine; on them the volume's own words, their
    # dots lit as far as its voice has reached
    comp = box(2.6, SPINE_COMPS[3][0] + 1.2, sw - 2.6, SPINE_COMPS[3][1] - 1.2)
    words = Words(paragraphs(n)[1:] or paragraphs(n))
    acc = Acc()
    x0, x1 = comp.bounds[0], comp.bounds[2]
    for yy in SHELF_RULES:
        acc.rules.append(box(-0.2, yy + 0.55 - 0.05, sw + 0.2, yy + 0.55 + 0.05))
        lw = []
        while True:
            w_ = words.take()
            if w_ is None:
                break
            if plain_width(" ".join(lw + [w_]), GLOSS_SIZE) > (x1 - x0):
                words.back()
                break
            lw.append(w_)
        if lw:
            ras, dots, har, _ = shaped(" ".join(lw), GLOSS_SIZE, x1, yy)
            if ras is not None:
                acc.rasm.append(ras)
            for (dx, dy, k) in dots:
                acc.dots += dot_group(dx, dy, k, GLOSS_SIZE)
            if har is not None:
                acc.vowels.append(har)
    # the voice on the spine: the share of its lines lit grows with the volume
    share = min(n, 10) / 10.0
    lit_to = SPINE_COMPS[3][1] - (SPINE_COMPS[3][1] - SPINE_COMPS[3][0]) * share
    halo = box(-1, lit_to, sw + 1, SPINE_COMPS[3][1])
    rules_only = box(-0.2, SPINE_COMPS[3][0], sw + 0.2, SPINE_COMPS[3][1])
    lay_gloss(P, acc, rules_only, None if n >= 10 else halo)
    y = 207.5
    for part in ("أحمد بن", "إبراهيم", "السليمي"):
        g, w = T.text(part, F.sch6, 3.3, cx=cx, base=y)
        P.ink(g, AW.PEARL_INK)
        y += 4.6
    for g in CA.seal(cx, 225.4, small=True):
        P.gold(g)
    return P


# ------------------------------------------------------------------------------------------------ the back
BACK_MATN = (30.0, 28.0, W - 30.0, 166.0)


def back(n):
    """The back: the same page. Its matn carries what the book says of itself and of this volume; its glosses
    continue the volume's words, their voice quieter; the eleven volumes stand in a row as eleven small pages; the
    house, the edition, and the ISBN zone kept clear."""
    import coverart as CA
    F = faces()
    P = _page()
    outer = box(9.5, 9.5, W - 9.5, H - 9.5)
    tajdwil(P, outer)
    field = outer.buffer(-3.6, join_style=2)
    mb, m = matn_block(P, BACK_MATN)
    fx0, fy0, fx1, fy1 = field.bounds
    mx0, my0, mx1, my1 = m.bounds
    # glosses on the head and the two sides only; the foot holds the row of the series and the colophon
    foot = my1 + 3.0
    head = Polygon([(fx0, fy0), (fx1, fy0), (mx1, my0), (mx0, my0)])
    side_r = Polygon([(fx1, fy0), (fx1, foot), (mx1, foot), (mx1, my0)])
    side_l = Polygon([(fx0, fy0), (mx0, my0), (mx0, foot), (fx0, foot)])
    words = Words(paragraphs(n)[2:] or paragraphs(n))
    acc = Acc()
    for reg, ang in ((head, 0), (side_r, 45), (side_l, 45)):
        gloss(AW.valid(reg), ang, words, acc, numerals=(n == 11))
    halo = m.buffer(voice_reach(max(1, n // 2)), join_style=2)
    lay_gloss(P, acc, AW.valid(field.difference(m)).intersection(box(0, 0, W, foot)), halo)
    for (a, b) in (((fx0, fy0), (mx0, my0)), ((fx1, fy0), (mx1, my0))):
        ln = LineString([a, b])
        P.gold(ln.buffer(0.45, cap_style=2).difference(ln.buffer(0.06)))
        jewel(P, b[0], b[1], 3.0)
    P.gold(box(fx0, foot - 0.2, fx1, foot + 0.2))
    # what the book says
    right, measure = BACK_MATN[2] - 8.0, (BACK_MATN[2] - BACK_MATN[0]) - 16.0
    y = 42.0
    for t in CA.LEAD:
        g, _ = T.text(t, F.sch6, 4.7, x_right=right, base=y)
        P.ink(g, AW.PEARL_INK)
        y += 7.9
    y += 1.0
    P.gold(box(right - 16, y - 0.18, right, y + 0.18))
    P.gold(AW.nuqta(right - 17.6, y, 2.0, 70))
    y += 9.0
    for ln in T.paragraph(CA.SERIES, F.sch4, 3.45, measure):
        P.ink(T.segs_to_geom(T.set_right(ln, right, y)), AW.PEARL_SOFT)
        y += 6.0
    y += 4.5
    kick, _ = T.text("في هذا المجلد", F.changa4, 2.6, x_right=right, base=y)
    P.ink(kick, AW.CHAMPAGNE_INK)
    y += 7.2
    headl = "مرجع المتكلّم العربي" if n == 11 else FM.volume_line(n)
    hg, _ = T.text(headl, F.changa5, 4.2, x_right=right, base=y)
    P.pearl(hg)
    y += 7.0
    what = FM.VOLUMES[n - 1][2]
    if n == 11:
        what = f"{FM.REFERENCE_SUB}: {what}"
    for ln in T.paragraph(what + ".", F.sch4, 3.45, measure):
        P.ink(T.segs_to_geom(T.set_right(ln, right, y)), AW.PEARL_SOFT)
        y += 5.9
    stage = FM.VOLUMES[n - 1][3]
    if stage:
        y += 1.8
        babs = re.sub(r"<[^>]+>", "", FM.VOLUMES[n - 1][4])
        lab, _ = T.text(f"{FM.STAGES[stage]}: {stage} · {babs}", F.changa4, 2.6, x_right=right, base=y)
        P.ink(lab, AW.CHAMPAGNE_INK)
    if y > BACK_MATN[3] - 4:
        raise SystemExit(f"back {n}: the words overrun the matn ({y:.1f} mm)")
    # the series: eleven small pages in a row, this volume's lit
    row_y = 178.5
    slot = 12.2
    for v in range(1, 12):
        x = 146.0 - (v - 1) * slot
        if v == n:
            device(P, x, row_y, 9.6, 12.4, n=v, lit=1.0, numeral=v)
        else:
            r = box(x - 4.8, row_y - 6.2, x + 4.8, row_y + 6.2)
            P.cold(IL.band(r, 0.0, -0.18, join=2), 0.55)
            P.cold(IL.band(r.buffer(-2.2, join_style=2), 0.0, -0.12, join=2), 0.45)
            ng, _ = T.text(str(v), F.amiri4, 3.0, cx=x, base=row_y + 1.1, digits=True)
            P.ink(ng, AW.CHAMPAGNE_INK)
    for g in CA.seal(126.0, 205.0):
        P.gold(g)
    pub, _ = T.text(FM.PUBLISHER_AR, F.sch4, 3.2, cx=126.0, base=214.0)
    P.ink(pub, AW.PEARL_SOFT)
    ed, _ = T.text(f"{FM.EDITION}، {FM.YEAR}", F.sch4, 2.9, cx=126.0, base=219.5)
    P.ink(ed, AW.PEARL_SOFT)
    zx, zy, zw, zh = CA.ISBN_ZONE
    P.arch.append(box(zx - 1, zy - 1, zx + zw + 1, zy + zh + 1))
    P.L.glow.append((85.0, 90.0, 70.0, 0.55))
    return P, field
