#!/usr/bin/env python3
"""What the covers share (Bible, ch. 25 §13): the title as the covers set it, the house's seal, the words of the
back, the page as layers of material (artwork.Layers) on the page (170 × 240 mm, y downward), and the move of a
page onto the wrap. The composition itself, front, spine and back, is «المتن والحاشية» in matn.py; the
illuminated binding that came before it («الشمسة وأثر القلم», §12) is kept in book/_production/الأرشيف.
"""
from __future__ import annotations

import math
from functools import lru_cache

from shapely import affinity
from shapely.geometry import box
from shapely.ops import unary_union

import artwork as AW
import illumination as IL
import typeset as T

W, H = 170.0, 240.0


TAU = 2 * math.pi


AR = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")


@lru_cache(maxsize=1)
def faces():
    return T.Faces()


def translate(L, dx, dy):
    out = AW.Layers()
    for k in L.__dataclass_fields__:
        items = getattr(L, k)
        moved = []
        for it in items:
            if k == "glow":
                moved.append((it[0] + dx, it[1] + dy) + tuple(it[2:]))
            elif isinstance(it, tuple):
                moved.append((affinity.translate(it[0], dx, dy),) + it[1:])
            else:
                moved.append(affinity.translate(it, dx, dy))
        setattr(out, k, moved)
    return out


class Page:
    """A surface being composed: its layers, and the areas of its architecture (what the gloss stroke and
    the ground pass behind)."""

    def __init__(self):
        self.L = AW.Layers()
        self.arch = []

    def gold(self, g):
        if g is not None and not g.is_empty:
            self.L.gold.append(AW.valid(g))

    def pearl(self, g):
        if g is not None and not g.is_empty:
            self.L.pearl.append(AW.valid(g))

    def champagne(self, g):
        if g is not None and not g.is_empty:
            self.L.champagne.append(AW.valid(g))

    def ruby(self, g):
        self.L.ruby.append(AW.valid(g))

    def cold(self, g, t):
        if g is not None and not g.is_empty:
            self.L.cold.append((AW.valid(g), AW.tint(t)))

    def panel(self, g, depth=0.02):
        self.L.body.append((AW.valid(g), ("depth", depth, 1.0)))

    def ink(self, g, inks):
        self.L.ink.append((AW.valid(g), inks))

    def emboss(self, g, level=1.0):
        self.L.emboss.append((AW.valid(g), level))


def title_parts(cx, lines):
    """The title in Kufam as (letters, dots, ascenders): lines = [(text, size, baseline)]. The font's square dots
    are found and returned apart, to be redrawn as the nib's dots."""
    F = faces()
    letters, dots, asc = [], [], []
    for (txt, sz, base) in lines:
        g, w = T.text(txt, F.kufi6, sz, cx=cx, base=base, features=T.KF)
        side = 0.137 * sz
        for c in AW.poly_list(g):
            x0, y0, x1, y1 = c.bounds
            cw, ch = x1 - x0, y1 - y0
            if abs(cw - side) < 0.25 * side and abs(ch - side) < 0.25 * side:
                dots.append(((x0 + x1) / 2, (y0 + y1) / 2, side, base))
            else:
                letters.append(c)
                if ch > 0.7 * sz and cw < 0.3 * sz:
                    asc.append(((x0 + x1) / 2, y0, cw, sz))
    return AW.valid(unary_union(letters)), dots, asc


def floriate(x, top, stem_w, size, side=1):
    """A tendril from the head of an ascender: it leans, curls and ends in a split leaf (floriated Kufic)."""
    g, end = IL.tendril(x, top + 0.4, -math.pi / 2, size * 0.62, -0.03 * side * 12 / size, -0.75 * side * 12 / size,
                        stem_w * 0.62, stem_w * 0.26, nib=70)
    lf = IL.split_leaf(end[0], end[1], end[2] - 0.5 * side, size * 0.26, size * 0.13)
    return AW.valid(unary_union([g, lf]))


def set_title(P, cx, lines, floriation=False, emboss=True, dot_scale=1.5):
    """The title as the covers set it: letters in pearl foil over a registered emboss, the dots redrawn as the
    nib's dots in gold, the nūn's dot (the lone dot of «صناعة») in ruby, and tendrils from the ascenders."""
    letters, dots, asc = title_parts(cx, lines)
    P.pearl(letters)
    if emboss:
        P.emboss(letters, 1.0)
    first_base = lines[0][2]
    for (x, y, s, base) in dots:
        nq = AW.nuqta(x, y, s * dot_scale, 70)
        lone = all(math.hypot(x - x2, y - y2) > 2.2 * s for (x2, y2, s2, b2) in dots if (x2, y2) != (x, y))
        if lone and base == first_base and y < base:
            P.ruby(nq)
        else:
            P.gold(nq)
    if floriation:
        for i, (x, top, w, sz) in enumerate(asc):
            if sz > 15 or i % 2 == 0:
                P.gold(floriate(x, top, w, sz * 0.9))
    return letters


def seal(cx, base, small=False):
    """The house's device (Bible, ch. 98): «الإحسان» in Kufam in a frame of two rules, broken at the top by the
    nib's dot. Returns geometries (for gold)."""
    F = faces()
    size = 2.7 if small else 3.9
    g, w = T.text("الإحسان", F.kufi6, size, cx=cx, base=base, features=T.KF)
    out = [g]
    pad_x, pad_top, pad_bot = size * 0.9, size * 1.0, size * 0.8
    x0, x1 = cx - w / 2 - pad_x, cx + w / 2 + pad_x
    y0, y1 = base - size * 0.95 - pad_top, base + pad_bot
    t_out, t_in, gap = (0.22, 0.12, 0.7) if small else (0.28, 0.14, 0.9)
    dot = size * 0.34
    for (t, d) in ((t_out, 0.0), (t_in, gap)):
        a0, a1, b0, b1 = x0 + d, x1 - d, y0 + d, y1 - d
        hole = dot * 0.9 + 0.5 + d * 0.6
        out.append(unary_union([box(a0, b1 - t, a1, b1), box(a0, b0, a0 + t, b1), box(a1 - t, b0, a1, b1),
                                box(a0, b0, cx - hole, b0 + t), box(cx + hole, b0, a1, b0 + t)]))
    out.append(AW.nuqta(cx, y0 + t_out / 2, dot * 2.2, 70))
    return out


LEAD = ("لا يريد هذا الكتاب أن يُخرج متكلّمًا يُبهر الناس بألفاظه،",
        "ولا خطيبًا يُعجب السامعين بنفسه؛",
        "بل يريد متكلّمًا يُفهِم ويُحسن ويؤثّر.")


SERIES = ("كتابٌ في أحد عشر مجلدًا في صناعة الكلام بالعربية الفصحى المعاصرة، لمن يعرف العربية ثم لا يجدها على لسانه "
          "حين يحتاج إليها. يبدأ من سؤالٍ لا بدّ منه: أيّ عربيةٍ نتكلّم؟ ثم يمضي من صحة الصوت واستقامة الجملة إلى "
          "مراعاة المقام وحسن البيان، جامعًا بين أصول البيان العربي وما انتهى إليه الدرس الحديث في التواصل، ومقيمًا "
          "ذلك كله على النماذج المتدرّجة والحوار والتدريب والتقويم.")


ISBN_ZONE = (21.0, 186.0, 46.0, 26.0)      # on the back, from its spine side and its head (mm), inside the frame
