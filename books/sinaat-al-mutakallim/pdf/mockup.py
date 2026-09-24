#!/usr/bin/env python3
"""Studio mockup of the four-volume hardcover set (presentation only; not part of the book).

The four case wraps from cover.py are cut into their front and spine panels and mounted on 3-D
boxes in Chromium: the set stands in a row, spines to the light, with volume one turned forward to
show its face. Soft light from the upper right, a warm stone surface, contact shadows; no glow, no
reflections, no particles (Bible, Part Six, ch. 25 §9 and §10).

    python3 mockup.py        writes ../Sinaat-al-Mutakallim-al-Arabi_Mockup.png
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pypdfium2 as pdfium

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cover as CVR  # noqa: E402

CACHE = HERE / ".cache" / "mockup"
OUT = HERE.parent / "Sinaat-al-Mutakallim-al-Arabi_Mockup.png"
PX = 3.0                      # css px per mm in the scene


def panels(wraps_pdf: Path, spines: dict):
    """Cut every volume wrap into front and spine PNGs (trim only, bleed removed)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument(str(wraps_pdf))
    out = {}
    scale = 300 / 72
    for i, (v, sp) in enumerate(sorted(spines.items())):
        im = doc[i].render(scale=scale).to_pil().convert("RGB")
        k = scale * 72 / 25.4
        b = CVR.BLEED
        front = im.crop((int(b * k), int(b * k), int((b + CVR.W) * k), int((b + CVR.H) * k)))
        spine = im.crop((int((b + CVR.W) * k), int(b * k), int((b + CVR.W + sp) * k), int((b + CVR.H) * k)))
        fp, sp_ = CACHE / f"front-v{v}.jpg", CACHE / f"spine-v{v}.jpg"
        front.save(fp, quality=92)
        spine.save(sp_, quality=92)
        out[v] = (fp, sp_, sp)
    return out


BOOK_CSS = """
html, body { margin: 0; }
body { width: 2400px; height: 1500px; overflow: hidden;
  background: radial-gradient(ellipse 120% 90% at 70% 20%, #F1ECE3 0%, #E4DDD1 45%, #CFC6B7 100%); }
.floor { position: absolute; left: 0; right: 0; top: 1130px; bottom: 0;
  background: linear-gradient(180deg, #D6CEC1 0%, #C9C0B1 100%); }
.floor::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 2px; background: rgba(255,255,255,.35); }
.scene { position: absolute; inset: 0; perspective: 3400px; perspective-origin: 55% 30%; }
.book { position: absolute; transform-style: preserve-3d; }
.face { position: absolute; backface-visibility: hidden; overflow: hidden; }
.face img { display: block; width: 100%; height: 100%; }
.face .light { position: absolute; inset: 0; }
.pages { background: repeating-linear-gradient(90deg, #F4EFE3 0 1px, #E9E2D3 1px 2px); }
.shadow { position: absolute; border-radius: 50%; filter: blur(18px); background: rgba(40, 32, 20, .42); }
"""


def box(v, front, spine, sp_mm, x, y, rot, lift=0.0, front_light=0.0, spine_light=0.0):
    """A standing hardcover: face (front board), spine, top (boards and page block), back."""
    W, H, S = CVR.W * PX, CVR.H * PX, sp_mm * PX
    # an Arabic book: the spine is on the right of its face
    faces = [
        # front
        (f'width:{W}px;height:{H}px;transform: translateZ({S / 2}px);',
         f'<img src="{front.as_uri()}"><div class="light" style="background:linear-gradient(115deg, rgba(255,255,255,{0.10 + front_light}) 0%, rgba(255,255,255,0) 38%, rgba(0,0,0,{0.10 - front_light / 2}) 100%)"></div>'),
        # spine (right side)
        (f'width:{S}px;height:{H}px;left:{W - S / 2}px;transform: rotateY(90deg);',
         f'<img src="{spine.as_uri()}"><div class="light" style="background:linear-gradient(90deg, rgba(0,0,0,{0.18 - spine_light}) 0%, rgba(255,255,255,{0.07 + spine_light}) 45%, rgba(0,0,0,{0.22 - spine_light}) 100%)"></div>'),
        # top: page block between the boards
        (f'width:{W - 8}px;height:{S - 5}px;left:4px;top:{-(S - 5) / 2 + 3}px;transform: rotateX(90deg);',
         '<div class="pages" style="width:100%;height:100%"></div><div class="light" style="background:linear-gradient(180deg, rgba(0,0,0,.18), rgba(0,0,0,0) 30%, rgba(0,0,0,0) 70%, rgba(0,0,0,.18))"></div>'),
        # back
        (f'width:{W}px;height:{H}px;transform: rotateY(180deg) translateZ({S / 2}px);', '<div style="width:100%;height:100%;background:#0B2461"></div>'),
    ]
    html = "".join(f'<div class="face" style="{st}">{inner}</div>' for st, inner in faces)
    return (f'<div class="book" style="left:{x}px; top:{y - lift}px; width:{W}px; height:{H}px; '
            f'transform: {rot};">{html}</div>')


def scene(p):
    W, H = CVR.W * PX, CVR.H * PX
    books, shadows = [], []
    # the set, spines out as on a shelf (volume one at the right, as an Arabic set stands); each book
    # is turned a quarter so its face presses against its neighbour, and the whole row is angled
    spines_total = sum(p[v][2] * PX for v in p) + 3 * 6
    x = 0.0
    row = []
    for v in (4, 3, 2, 1):
        front, spine, sp = p[v]
        S = sp * PX
        # after a quarter turn the spine lies in the plane of the row; place its centre at x + S/2
        row.append(box(v, front, spine, sp, x + S / 2 - W + S / 2, 0, "rotateY(-90deg)", spine_light=0.05))
        x += S + 6
    books.append(f'<div class="book" style="left:1320px; top:{1130 - H}px; width:{spines_total}px; height:{H}px; '
                 f'transform: rotateY(-16deg); transform-origin: 0 50%;">{"".join(row)}</div>')
    shadows.append(f'<div class="shadow" style="left:1290px; top:1116px; width:{spines_total + 140}px; height:40px"></div>')
    # volume one turned forward
    front, spine, sp = p[1]
    books.append(box(1, front, spine, sp, 360, 1130 - H + 10, "rotateY(-24deg)", front_light=0.04))
    shadows.append(f'<div class="shadow" style="left:310px; top:1110px; width:{W + 60}px; height:48px"></div>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BOOK_CSS}</style></head><body>'
            f'<div class="floor"></div><div class="scene">{"".join(shadows)}{"".join(books)}</div></body></html>')


def shoot(html: str, out: Path):
    CACHE.mkdir(parents=True, exist_ok=True)
    src = CACHE / "scene.html"
    src.write_text(html, encoding="utf-8")
    js = CACHE / "shot.js"
    js.write_text("""const { chromium } = require('playwright');
(async () => {
  const [inp, out] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2400, height: 1500 }, deviceScaleFactor: 1 });
  await p.goto('file://' + inp, { waitUntil: 'load' });
  await p.waitForTimeout(500);
  await p.screenshot({ path: out });
  await b.close();
})();""")
    env = dict(os.environ)
    gnm = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    env["NODE_PATH"] = os.pathsep.join(filter(None, [env.get("NODE_PATH", ""), gnm]))
    subprocess.run(["node", str(js), str(src), str(out)], check=True, env=env)
    return out


def main():
    spines = json.loads((HERE / ".cache" / "cover" / "spines.json").read_text()) if (HERE / ".cache" / "cover" / "spines.json").exists() else None
    if spines is None:
        raise SystemExit("run cover.py (volume wraps) first")
    spines = {int(k): v for k, v in spines.items()}
    p = panels(HERE / ".cache" / "cover" / "wraps.pdf", spines)
    print(shoot(scene(p), OUT))


if __name__ == "__main__":
    main()
