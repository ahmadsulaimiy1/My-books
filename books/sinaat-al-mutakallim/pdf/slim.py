#!/usr/bin/env python3
"""Write a light digital copy of a Chromium PDF (text and vectors kept, nothing rasterised).

Chromium places every Arabic glyph with its own `Td … Tj`, at a position rounded to the pixel, and
wraps ligatures in ActualText spans. This rewrites each text run as one `TJ` string that follows the
fonts' own advances, adding a kerning number only where a glyph sits more than TOL from where the
advance puts it (justified word gaps, marks), and drops the per-glyph spans and the structure tree.
Positions stay within TOL of the original; the visible page does not change.

    python3 slim.py in.pdf out.pdf [first last]      (1-based page range, inclusive)

Volume one of the digital edition (pages 1–845 of the complete book):

    python3 slim.py ../Sinaat-al-Mutakallim-al-Arabi_Complete-Book.pdf \
        ../delivery/Sinaat-al-Mutakallim-al-Arabi_Volume-1_Digital.pdf 1 845

pikepdf (optional) packs the remaining objects into object streams.
"""
from __future__ import annotations

import sys
import re

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ArrayObject, ContentStream, FloatObject, NameObject, NumberObject,
                           TextStringObject, ByteStringObject, DictionaryObject, BooleanObject,
                           DecodedStreamObject)

TOL = 0.5          # text-space units (CSS px at the page scale Chromium uses)


def spaces(font):
    """CIDs whose ToUnicode is a space (they draw nothing; the gap they leave is kept)."""
    font = font.get_object()
    tu = font.get("/ToUnicode")
    if tu is None:
        return set()
    cm = tu.get_object().get_data()
    out = set()
    for blk in re.findall(rb"beginbfchar(.*?)endbfchar", cm, re.S):
        for a, b in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            if b.upper() in (b"0020", b"00A0"):
                out.add(int(a, 16))
    for blk in re.findall(rb"beginbfrange(.*?)endbfrange", cm, re.S):
        for a, b, c in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            lo, hi, u = int(a, 16), int(b, 16), int(c, 16)
            if lo <= hi and u <= 0x20 <= u + (hi - lo):
                out.add(lo + 0x20 - u)
    return out


def widths(font):
    """CID -> width (1/1000 em) for a Type0 font; default /DW."""
    font = font.get_object()
    d = font["/DescendantFonts"][0].get_object() if "/DescendantFonts" in font else font
    dw = float(d.get("/DW", 1000))
    table = {}
    w = d.get("/W")
    if w is not None:
        w = w.get_object()
        i = 0
        while i < len(w):
            a = int(w[i])
            nxt = w[i + 1]
            if isinstance(nxt, ArrayObject) or hasattr(nxt, "__iter__") and not isinstance(nxt, (int, float)):
                for k, v in enumerate(nxt.get_object() if hasattr(nxt, "get_object") else nxt):
                    table[a + k] = float(v)
                i += 2
            else:
                b = int(nxt)
                v = float(w[i + 2])
                for c in range(a, b + 1):
                    table[c] = v
                i += 3
    return table, dw


TOK = re.compile(rb"<<|>>|<[0-9A-Fa-f\s]*>|\((?:\\.|[^\\)])*\)|/[^\s/<>\[\]()%]*|\[|\]|[-+]?(?:\d+\.?\d*|\.\d+)|[A-Za-z'\"*][A-Za-z0-9'\"*]*")


def fmt(x):
    x = round(x, 2)
    return (b"%d" % x) if x == int(x) else (b"%.2f" % x).rstrip(b"0").rstrip(b".")


def ops(data):
    """(operand tokens, operator, raw bytes) for each operation in a content stream."""
    operands, start, depth = [], None, 0
    for m in TOK.finditer(data):
        t = m.group()
        if start is None:
            start = m.start()
        if t in (b"<<", b"["):
            depth += 1
        elif t in (b">>", b"]"):
            depth -= 1
        c = t[:1]
        if depth == 0 and (c.isalpha() or c in (b"'", b'"')) :
            yield operands, t, data[start:m.end()]
            operands, start = [], None
        else:
            operands.append(t)


INSIDE_OK = {b"rg", b"RG", b"g", b"G", b"k", b"K", b"sc", b"SC", b"scn", b"SCN", b"cs", b"CS", b"gs",
             b"w", b"J", b"j", b"M", b"d", b"ri", b"i"}


def rewrite(page, cache):
    """One text object per stretch of text: runs continue across words, colour and ExtGState
    changes; a new Tm only where the baseline, font or matrix changes."""
    fonts = page["/Resources"].get_object().get("/Font", {})
    data = page.get_contents().get_data()
    out = []
    in_bt = False            # inside the source BT … ET
    open_ = False            # a BT is open in the output
    cur_font = None          # (name, size) set in the output
    want_font = None
    size = 1.0
    wt = ({}, 1000.0)
    sp = set()
    lx = ly = 0.0
    tm_ab = b"1 0 0 -1"
    run = None
    run_key = None
    pen = 0.0

    def flush():
        nonlocal run
        if run:
            out.append(b"[" + b"".join(run) + b"]TJ")
        run = None

    def close():
        nonlocal open_
        flush()
        if open_:
            out.append(b"ET")
            open_ = False

    for operands, op, raw in ops(data):
        if op in (b"BDC", b"BMC", b"EMC"):
            continue                       # marked content: the structure tree is not kept
        if op == b"BT":
            in_bt = True
            continue
        if op == b"ET":
            in_bt = False
            continue
        if not in_bt:
            if op in INSIDE_OK:
                flush()
                out.append(raw)
            else:
                close()
                out.append(raw)
            continue
        if op == b"Tf":
            name = operands[0].decode("latin-1")
            size = float(operands[1])
            if name not in cache:
                cache[name] = (widths(fonts[name]), spaces(fonts[name]))
            wt, sp = cache[name]
            want_font = (name, operands[1])
            continue
        if op == b"Tm":
            tm_ab = b" ".join(operands[:4])
            lx, ly = float(operands[4]), float(operands[5])
            continue
        if op == b"Td":
            lx += float(operands[0]); ly += float(operands[1]); continue
        if op == b"Tj" and operands and operands[0].startswith(b"<"):
            hexs = re.sub(rb"\s", b"", operands[0][1:-1])
            cids = [int(hexs[i:i + 4], 16) for i in range(0, len(hexs), 4)]
            if all(c in sp for c in cids):
                continue                   # a space glyph: nothing to draw
            table, dw = wt
            key = (want_font, tm_ab, ly)
            if not open_:
                out.append(b"BT")
                open_ = True
                cur_font = None
            if run is None or key != run_key or cur_font != want_font:
                flush()
                if cur_font != want_font:
                    out.append(want_font[0].encode("latin-1") + b" " + want_font[1] + b" Tf")
                    cur_font = want_font
                out.append(tm_ab + b" " + fmt(lx) + b" " + fmt(ly) + b" Tm")
                run, pen, run_key = [], lx, key
            gap = lx - pen
            if abs(gap) > TOL:
                run.append(b"%d" % round(-gap * 1000.0 / size))
                pen = lx
            if run and run[-1].startswith(b"<"):
                run[-1] = run[-1][:-1] + hexs + b">"
            else:
                run.append(b"<" + hexs + b">")
            pen += sum(table.get(c, dw) for c in cids) * size / 1000.0
            continue
        # any other text-object operator: keep it, in its own text object
        flush()
        if not open_:
            out.append(b"BT"); open_ = True; cur_font = None
        if want_font and cur_font != want_font:
            out.append(want_font[0].encode("latin-1") + b" " + want_font[1] + b" Tf"); cur_font = want_font
        if op in (b"TJ", b"Tj", b"'", b'"'):
            out.append(tm_ab + b" " + fmt(lx) + b" " + fmt(ly) + b" Tm")
        out.append(raw)
    close()
    new = DecodedStreamObject()
    new.set_data(b"\n".join(out))
    return new


def main():
    src, dst = sys.argv[1], sys.argv[2]
    r = PdfReader(src)
    first, last = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1, len(r.pages))
    w = PdfWriter()
    w.append(r, pages=(first - 1, last))
    root = w._root_object
    for k in ("/StructTreeRoot", "/MarkInfo"):
        if k in root:
            del root[k]
    root[NameObject("/Lang")] = TextStringObject("ar")
    root[NameObject("/ViewerPreferences")] = DictionaryObject({NameObject("/Direction"): NameObject("/R2L"),
                                                                NameObject("/DisplayDocTitle"): BooleanObject(True)})
    root[NameObject("/PageMode")] = NameObject("/UseOutlines")
    if r.metadata:
        w.add_metadata({k: v for k, v in r.metadata.items()})
    cache = {}
    for i, p in enumerate(w.pages):
        if "/StructParents" in p:
            del p["/StructParents"]
        new = rewrite(p, cache)
        p[NameObject("/Contents")] = w._add_object(new)
        p.compress_content_streams(level=9)
        if i % 100 == 0:
            print("page", i + 1, file=sys.stderr)
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    w.write(dst)
    try:                       # pack the remaining objects (fonts' width tables, page dicts) into object streams
        import pikepdf
    except ImportError:
        return
    tmp = dst + ".tmp"
    with pikepdf.open(dst) as pdf:
        pdf.remove_unreferenced_resources()
        pdf.save(tmp, object_stream_mode=pikepdf.ObjectStreamMode.generate, recompress_flate=True)
    import os
    os.replace(tmp, dst)


if __name__ == "__main__":
    main()
