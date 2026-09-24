"""Arabic display lettering as vector outlines.

Shapes a line with HarfBuzz (script arab, direction rtl), draws every glyph outline with
fontTools and returns one SVG path in millimetres. Working from outlines lets a title be
engineered like commissioned lettering: words stacked and overlapped, kashida (مدّ)
lengths chosen per word, marks placed, optical spacing corrected; and the result needs no
font embedding in the PDF.
"""
from __future__ import annotations

import io
import re
from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
TTF_CACHE = HERE / ".cache" / "ttf"


@lru_cache(maxsize=None)
def load(path: str, wght: float | None = None) -> tuple[bytes, TTFont]:
    """TTF bytes (for HarfBuzz) and a TTFont (for outlines); variable fonts are pinned to wght."""
    TTF_CACHE.mkdir(parents=True, exist_ok=True)
    key = TTF_CACHE / f"{Path(path).stem}-{int(wght or 0)}.ttf"
    if not key.exists():
        f = TTFont(path)
        if "fvar" in f and wght is not None:
            from fontTools.varLib import instancer
            axes = {a.axisTag: a.defaultValue for a in f["fvar"].axes}
            axes["wght"] = wght
            f = instancer.instantiateVariableFont(f, axes)
        f.flavor = None
        buf = io.BytesIO()
        f.save(buf)
        key.write_bytes(buf.getvalue())
    data = key.read_bytes()
    return data, TTFont(io.BytesIO(data))


def arabic_face(font_css: str, family: str, weight: int) -> str:
    """Path of the face serving Arabic for family/weight in a resolved @font-face stylesheet."""
    for block in re.findall(r"@font-face\s*{(.*?)}", font_css, flags=re.S):
        fam = re.search(r"font-family:\s*'?\"?([^;'\"]+)", block).group(1).strip()
        wt = re.search(r"font-weight:\s*(\d+)", block)
        rng = re.search(r"unicode-range:\s*([^;]+);", block)
        if fam != family or (wt and int(wt.group(1)) != weight):
            continue
        if rng and "U+0600" not in rng.group(1) and "U+600" not in rng.group(1):
            continue
        url = re.search(r"url\(file://([^)]+)\)", block).group(1)
        from urllib.request import url2pathname
        return url2pathname(url)
    raise KeyError(f"{family} {weight} (arabic) not in stylesheet")


class Line:
    """A shaped line: SVG path data in mm with the origin at the left end of the baseline."""

    def __init__(self, text, path, size_mm, wght=None, features=None, tracking_mm=0.0):
        data, font = load(path, wght)
        face = hb.Face(data)
        hbfont = hb.Font(face)
        upem = face.upem
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        buf.direction, buf.script, buf.language = "rtl", "Arab", "ar"
        hb.shape(hbfont, buf, features or {"kern": True, "liga": True, "calt": True})
        gs = font.getGlyphSet()
        order = font.getGlyphOrder()
        k = size_mm / upem
        x = 0.0
        pen = SVGPathPen(gs)
        bp = BoundsPen(gs)
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            name = order[info.codepoint]
            gx = x + pos.x_offset * k
            gy = -pos.y_offset * k
            tp = TransformPen(pen, (k, 0, 0, -k, gx, gy))
            gs[name].draw(tp)
            gs[name].draw(TransformPen(bp, (k, 0, 0, -k, gx, gy)))
            x += pos.x_advance * k + tracking_mm
        self.d = pen.getCommands()
        self.width = x - tracking_mm
        self.bounds = bp.bounds or (0, 0, self.width, 0)   # xmin, ymin (top, negative), xmax, ymax (descent)
        self.size = size_mm

    def placed(self, x_right, baseline):
        """(dx, dy) that puts the line's right end at x_right on the given baseline."""
        return x_right - self.width, baseline


def svg_path(line: Line, dx: float, dy: float, **attrs) -> str:
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path transform="translate({dx:.3f} {dy:.3f})" d="{line.d}" {a}/>'
