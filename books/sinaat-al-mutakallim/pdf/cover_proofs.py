#!/usr/bin/env python3
"""Material proofs and the presentation of the covers: what the plates of covers.py look like once printed,
foiled, pressed and varnished, and how the eleven stand together.

Every image is made from the plates themselves (nothing is painted for the picture): PRINT and SPOT-SAPPHIRE give
the ink on the sheet (through a print model of ink on coated paper, artwork.inks_to_linear); EMBOSS and DEBOSS
give the surface its relief; the foils are metals that mirror a studio (a softbox from the upper left, a strip
from the right, a dark room), the hot foils polished, the cold foil satin under the soft-touch laminate, the pearl
with a faint play of colour; the gloss varnish is a clear coat that catches the softbox where the matte does not.
No glow, no smoke, no light the object would not make (Bible, ch. 25 §9).

    python3 pdf/cover_proofs.py            everything below
    python3 pdf/cover_proofs.py 5          one volume's wrap proof
    python3 pdf/cover_proofs.py --edition heritage    one edition (all three by default)

Writes into covers/<edition>/ (1-Heritage, 2-Matn, 3-Contemporary):
  Cover-NN_<Latin>_Proof.jpg    the flat wrap, lit
  Series_Fronts.jpg             the eleven fronts
  Series_Shelf.jpg              the eleven on a shelf, straight on
  Series_Shelf-Angled.jpg       the same, from the side
  Series_Spines-Closeup.jpg     four spines near
  Volume-NN_Front-Hero.jpg      each volume standing, its front in raking light
  Volume-10_Wrap.jpg            the tenth's wrap, front, spine and back
  Volume-10_Finish-Closeup.jpg  the finishes near: foil, emboss, engraving, gloss
The proofs simulate; the printer's wet proof and a finished sample decide.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import artwork as AW  # noqa: E402

OUT = HERE.parent / "covers"
EDITIONS = {"heritage": "1-Heritage", "matn": "2-Matn", "contemporary": "3-Contemporary"}
DIR = OUT / EDITIONS["matn"]               # the edition being proofed (main sets it)
LATIN = {1: "Al-Usul", 2: "Al-Lisan", 3: "Al-Ibara", 4: "Al-Bayan", 5: "Al-Maqam", 6: "Al-Adab", 7: "Al-Hiwar",
         8: "Al-Majalis-wal-Minbar", 9: "Al-Muassasa", 10: "Al-Tamkin", 11: "Marji-al-Mutakallim"}


def spines():
    return json.loads((OUT / "spines.json").read_text())


def plate(n, name, dpi, clip=None, cmyk=False):
    doc = pymupdf.open(str(DIR / f"Cover-{n:02d}_{LATIN[n]}_{name}.pdf"))
    page = doc[0]
    kw = dict(dpi=dpi, colorspace=pymupdf.csCMYK if cmyk else pymupdf.csGRAY, alpha=False)
    if clip is not None:
        kw["clip"] = pymupdf.Rect(*[v * 72 / 25.4 for v in clip])
    pm = page.get_pixmap(**kw)
    a = np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n).astype(np.float32) / 255.0
    return a if cmyk else 1.0 - a[..., 0]


def _norm(v):
    return v / np.linalg.norm(v)


class Light:
    """The studio: a softbox, a strip, a dark room; and the camera's distance (mm) for the views across the object."""

    def __init__(self, key=(-0.36, -0.46, 0.81), strip=(0.62, -0.12, 0.78), key_size=0.34, strip_size=0.16,
                 key_power=1.0, strip_power=0.42, ambient=0.05, camera=650.0, dome=0.42):
        self.key, self.strip = _norm(np.array(key)), _norm(np.array(strip))
        self.key_size, self.strip_size = key_size, strip_size
        self.key_power, self.strip_power, self.ambient = key_power, strip_power, ambient
        self.camera = camera
        self.dome = dome

    def env(self, R, rough):
        """Radiance seen along the reflected direction R (..., 3) for a surface of the given roughness: a large
        diffusion dome behind the camera (what a flat foil mirrors when it faces us), brighter toward the top,
        and on it the softbox and the strip."""
        facing = np.clip(R[..., 2], 0, 1)
        dome = self.dome * (0.62 + 0.38 * np.clip(-R[..., 1] * 0.8 + 0.5, 0, 1)) * (0.35 + 0.65 * facing ** 2)
        out = (self.ambient + dome)[..., None] * np.ones(3)
        for d, size, power, tint in ((self.key, self.key_size, self.key_power, (1.0, 0.97, 0.92)),
                                     (self.strip, self.strip_size, self.strip_power, (0.92, 0.95, 1.0))):
            c = np.clip(R @ d, -1, 1)
            ang = np.arccos(c)
            soft = size + rough * 0.9
            v = np.clip((soft - ang) / max(1e-3, rough * 0.9 + 0.06), 0, 1)
            v = v * v * (3 - 2 * v)
            out = out + power * v[..., None] * np.array(tint)
        return out


def render(n, dpi=150, clip=None, light=None, spine_round=None):
    """The lit image of volume n's wrap (or of clip, in mm on the wrap), as linear RGB (rows × cols × 3)."""
    light = light or Light()
    k = dpi / 25.4
    cm = plate(n, "PRINT", dpi, clip, cmyk=True)
    sp = plate(n, "SPOT-SAPPHIRE", dpi, clip)
    inks = np.concatenate([cm, sp[..., None]], axis=-1)
    base = AW.inks_to_linear(inks)
    cold = plate(n, "COLD-FOIL", dpi, clip)
    gold = plate(n, "FOIL-GOLD", dpi, clip)
    pearl = plate(n, "FOIL-PEARL", dpi, clip)
    ruby = plate(n, "FOIL-RUBY", dpi, clip)
    emb = plate(n, "EMBOSS", dpi, clip)
    deb = plate(n, "DEBOSS", dpi, clip)
    uv = plate(n, "SPOT-UV", dpi, clip)
    Hh, Ww = base.shape[:2]
    # the surface: emboss raised, deboss pressed, hot foil pressed a little into what it lands on
    hot = np.clip(gold + pearl + ruby, 0, 1)
    height = (0.34 * ndimage.gaussian_filter(emb, 0.22 * k) - 0.20 * ndimage.gaussian_filter(deb, 0.20 * k)
              - 0.025 * ndimage.gaussian_filter(hot, 0.05 * k))
    gy, gx = np.gradient(height, 1.0 / k)
    nrm = np.dstack([-gx * 1.6, -gy * 1.6, np.ones_like(height)])
    if spine_round is not None:
        # a rounded spine: the surface turns away toward both edges of the spine's band of columns
        x0, x1 = spine_round
        cols = (np.arange(Ww) + 0.5) / k + (clip[0] if clip else 0)
        u = np.clip((cols - (x0 + x1) / 2) / ((x1 - x0) / 2), -1, 1)
        th = u * 0.62
        nrm[..., 0] += np.sin(th)[None, :] * 1.0
        nrm[..., 2] *= np.cos(th)[None, :]
    nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
    # the view: a camera at a finite distance, so a flat foil runs through the studio's light across the cover
    ys = (np.arange(Hh) + 0.5) / k + (clip[1] if clip else 0)
    xs = (np.arange(Ww) + 0.5) / k + (clip[0] if clip else 0)
    X, Y = np.meshgrid(xs, ys)
    cx, cy = (xs[0] + xs[-1]) / 2, (ys[0] + ys[-1]) / 2
    V = np.dstack([cx - X, cy - Y, np.full_like(X, light.camera)])
    V /= np.linalg.norm(V, axis=-1, keepdims=True)
    ndv = np.clip(np.sum(nrm * V, axis=-1), 0, 1)
    R = 2 * ndv[..., None] * nrm - V
    # the printed sheet under soft-touch laminate: diffuse, with a faint velvet haze
    diff = (light.ambient * 2.2 + light.key_power * 0.95 * np.clip(nrm @ light.key, 0, 1)
            + light.strip_power * 0.6 * np.clip(nrm @ light.strip, 0, 1))
    img = base * diff[..., None] * 0.92 + 0.003
    # gloss varnish: a clear coat that mirrors the studio sharply (and the matte does not)
    fres = 0.04 + 0.96 * (1 - ndv) ** 5
    gloss = light.env(R, 0.05) * (fres * 0.75)[..., None]
    img = img * (1 - 0.04 * uv[..., None]) + gloss * uv[..., None]
    # cold foil, satin under the laminate
    satin = np.array([0.72, 0.53, 0.24]) * (0.30 + 0.62 * light.env(R, 0.55))
    img = img * (1 - cold[..., None]) + satin * cold[..., None]
    # hot foils, polished
    env_sharp = light.env(R, 0.10)
    goldc = np.array([1.00, 0.74, 0.30]) * (0.06 + 1.05 * env_sharp)
    rubyc = np.array([0.50, 0.03, 0.07]) * (0.16 + 1.20 * env_sharp)
    hue = 0.035 * np.dstack([np.sin(6 * R[..., 0]), np.sin(6 * R[..., 0] + 2.1), np.sin(6 * R[..., 0] + 4.2)])
    pearlc = np.array([0.86, 0.84, 0.79]) * (0.62 + 0.55 * light.env(R, 0.30)) + hue
    for m, col in ((gold, goldc), (pearl, pearlc), (ruby, rubyc)):
        img = img * (1 - m[..., None]) + col * m[..., None]
    return np.clip(img, 0, None)


def to_image(lin, exposure=1.0):
    """Linear light to an sRGB image: a shoulder on the brightness only, so the metal keeps its hue."""
    x = lin * exposure
    lum = np.max(x, axis=-1, keepdims=True)
    mapped = lum * 1.12 / (1 + 0.12 * lum)
    x = x * np.where(lum > 1e-6, mapped / np.maximum(lum, 1e-6), 0)
    return Image.fromarray((AW._srgb(np.clip(x, 0, 1)) * 255 + 0.5).astype(np.uint8))


# ------------------------------------------------------------------------------------------------ the views
def wrap_proof(n, dpi=110):
    sp = spines()[str(n)]
    lin = render(n, dpi)
    im = to_image(lin)
    im.save(DIR / f"Cover-{n:02d}_{LATIN[n]}_Proof.jpg", quality=90)
    return im


def front_image(n, dpi=110, light=None):
    sp = spines()[str(n)]
    f = sp["front"]
    lin = render(n, dpi, clip=(f[0], f[1], f[2], f[3]), light=light)
    return to_image(lin)


def spine_image(n, dpi=120, light=None):
    sp = spines()[str(n)]
    s = sp["spine"]
    lin = render(n, dpi, clip=(s[0], s[1], s[2], s[3]), light=light, spine_round=(s[0], s[2]))
    return lin


def series_fronts(dpi=60):
    ims = [front_image(n, dpi) for n in range(1, 12)]
    w, h = ims[0].size
    gap = 18
    cols = 6
    rows = 2
    sheet = Image.new("RGB", (cols * w + (cols + 1) * gap, rows * h + (rows + 1) * gap), (18, 18, 20))
    # the Arabic order: the first volume at the right
    for i, im in enumerate(ims):
        r, c = divmod(i, cols)
        x = sheet.width - gap - (c + 1) * (w + gap) + (0 if r == 0 else 0)
        sheet.paste(im, (x, gap + r * (h + gap)))
    sheet.save(DIR / "Series_Fronts.jpg", quality=90)


# ------------------------------------------------------------------------------------------------ a small 3-D studio
class Camera:
    """A pinhole camera in mm: position, target, focal length (pixels) and the image size."""

    def __init__(self, pos, target, f, size):
        self.C = np.array(pos, float)
        self.w, self.h = size
        self.f = f
        F = np.array(target, float) - self.C
        self.F = F / np.linalg.norm(F)
        R = np.cross(self.F, np.array([0.0, 1.0, 0.0]))
        self.R = R / np.linalg.norm(R)
        self.U = np.cross(self.R, self.F)

    def project(self, P):
        d = np.asarray(P, float) - self.C
        x, y, z = d @ self.R, d @ self.U, d @ self.F
        return (self.w / 2 + self.f * x / z, self.h / 2 - self.f * y / z), z


def _coeffs(dst, src):
    A, B = [], []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y])
        A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y])
        B += [X, Y]
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def paste_quad(canvas, tex, corners2d, shade=1.0):
    """Warp the texture (PIL RGB) onto the projected quad (tl, tr, br, bl) of the canvas (PIL RGB)."""
    xs = [p[0] for p in corners2d]
    ys = [p[1] for p in corners2d]
    x0, y0 = int(max(0, math.floor(min(xs)))), int(max(0, math.floor(min(ys))))
    x1, y1 = int(min(canvas.width, math.ceil(max(xs)))), int(min(canvas.height, math.ceil(max(ys))))
    if x1 - x0 < 2 or y1 - y0 < 2:
        return
    local = [(x - x0, y - y0) for (x, y) in corners2d]
    tw, th = tex.size
    warped = tex.transform((x1 - x0, y1 - y0), Image.PERSPECTIVE, _coeffs(local, [(0, 0), (tw, 0), (tw, th), (0, th)]),
                           Image.BICUBIC)
    if shade != 1.0:
        warped = Image.eval(warped, lambda v: int(min(255, v * shade)))
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    ImageDraw.Draw(mask).polygon(local, fill=255)
    canvas.paste(warped, (x0, y0), mask)


def head_texture(sw, depth, k=4.0):
    """The head of a bound volume seen from above: the boards' edges in sapphire, the headband, and the gilt
    edge of the page block (printer-spec: extras.top_edge)."""
    w, h = max(8, int(sw * k)), max(8, int(depth * k))
    a = np.zeros((h, w, 3), np.float32)
    board = int(2.5 * k)
    a[:, :] = (0.72, 0.56, 0.26)                                   # gilt
    rng = np.random.default_rng(3)
    a *= (0.88 + 0.12 * np.sin(np.arange(w) * 1.7)[None, :, None]) * (0.95 + 0.05 * rng.random((1, w, 1)))
    a[:, :board] = (0.04, 0.07, 0.20)
    a[:, -board:] = (0.04, 0.07, 0.20)
    a[:int(3.0 * k)] = (0.06, 0.09, 0.24)                          # the spine's covering, turned over the head
    a[int(3.0 * k):int(4.6 * k), board:-board] = (0.55, 0.42, 0.18)  # the headband, gold and sapphire
    a[int(3.0 * k):int(4.6 * k):2, board:-board] = (0.08, 0.12, 0.34)
    return Image.fromarray((AW._srgb(np.clip(a, 0, 1)) * 255).astype(np.uint8))


def studio(w, h, floor_y, cam, x_range, depth):
    """The gallery: a dark wall with a warm pool of light, a walnut shelf in perspective."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    pool = np.exp(-(((xx - w * 0.5) / (w * 0.62)) ** 2 + ((yy - h * 0.30) / (h * 0.62)) ** 2))
    wall = np.dstack([0.012 + 0.050 * pool, 0.010 + 0.040 * pool, 0.010 + 0.032 * pool])
    img = Image.fromarray((AW._srgb(np.clip(wall, 0, 1)) * 255).astype(np.uint8))
    # the shelf: its top from the wall to its front edge, and the front edge
    xa, xb = x_range
    top = [cam.project(P)[0] for P in ((xa, 0, -depth - 60), (xb, 0, -depth - 60), (xb, 0, 90), (xa, 0, 90))]
    front = [cam.project(P)[0] for P in ((xa, 0, 90), (xb, 0, 90), (xb, -34, 90), (xa, -34, 90))]
    d = ImageDraw.Draw(img)
    d.polygon(top, fill=(46, 30, 20))
    d.polygon(front, fill=(26, 17, 12))
    # grain and falloff on the shelf's top
    return img


def book_faces(x0, sw, H_, D, spine_tex, front_tex=None, back_tex=None):
    faces = [("spine", spine_tex, [(x0, H_, 0), (x0 + sw, H_, 0), (x0 + sw, 0, 0), (x0, 0, 0)], 1.0),
             ("head", head_texture(sw, D), [(x0, H_, -D), (x0 + sw, H_, -D), (x0 + sw, H_, 0), (x0, H_, 0)], 0.92)]
    if front_tex is not None:        # the front board faces left on an Arabic shelf: its spine side at the front
        faces.append(("front", front_tex, [(x0, H_, -D), (x0, H_, 0), (x0, 0, 0), (x0, 0, -D)], 0.80))
    if back_tex is not None:
        faces.append(("back", back_tex, [(x0 + sw, H_, 0), (x0 + sw, H_, -D), (x0 + sw, 0, -D), (x0 + sw, 0, 0)], 0.70))
    return faces


def render_scene(cam, faces, size, x_range, depth, shadow_rect=None):
    img = studio(size[0], size[1], 0, cam, x_range, depth)
    # contact shadow of the row on the shelf
    if shadow_rect is not None:
        xa, xb = shadow_rect
        sh = Image.new("L", size, 0)
        poly = [cam.project(P)[0] for P in ((xa - 6, 0, -depth - 4), (xb + 6, 0, -depth - 4), (xb + 6, 0, 14), (xa - 6, 0, 14))]
        ImageDraw.Draw(sh).polygon(poly, fill=235)
        sh = sh.filter(ImageFilter.GaussianBlur(max(4, size[0] // 180)))
        img.paste((2, 2, 2), (0, 0), sh)
    # the faces, far to near
    order = sorted(faces, key=lambda f: -np.linalg.norm(np.mean(np.array(f[2]), axis=0) - cam.C))
    for (name, tex, corners, shade) in order:
        pts = [cam.project(P) for P in corners]
        # back-face culling: the projected quad must turn the right way
        (a, b, c) = (pts[0][0], pts[1][0], pts[2][0])
        cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
        if cross <= 0:
            continue
        paste_quad(img, tex, [p[0] for p in pts], shade)
    return img


def shelf_scene(angled=False, dpi=95, width=2600):
    sps = spines()
    light = Light(key=(-0.30, -0.42, 0.86), strip=(0.55, -0.2, 0.81), dome=0.34)
    H_ = 246.0
    D = 172.0
    gap = 1.2
    xs, x = {}, 0.0
    for n in range(11, 0, -1):          # left to right on the shelf: the reference first, the first volume last
        xs[n] = x
        x += sps[str(n)]["spine_mm"] + gap
    total = x - gap
    faces = []
    for n in range(1, 12):
        tex = to_image(spine_image(n, dpi, light))
        ft = front_image(11, 70, light) if (angled and n == 11) else None
        faces += book_faces(xs[n], sps[str(n)]["spine_mm"], H_, D, tex, front_tex=ft)
    h = int(width * (0.62 if not angled else 0.58))
    if angled:
        cam = Camera((-230.0, 330.0, 620.0), (total * 0.52, 100.0, -80.0), width * 0.95, (width, h))
    else:
        cam = Camera((total / 2, 225.0, 960.0), (total / 2, 118.0, -60.0), width * 1.62, (width, h))
    img = render_scene(cam, faces, (width, h), (-400, total + 400), D, shadow_rect=(0, total))
    # a light vignette, as a lens sees a lit room
    a = np.asarray(img).astype(np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:width].astype(np.float32)
    v = 1 - 0.28 * (((xx - width / 2) / (width * 0.62)) ** 2 + ((yy - h / 2) / (h * 0.75)) ** 2)
    img = Image.fromarray((np.clip(a * v[..., None], 0, 1) * 255).astype(np.uint8))
    name = "Series_Shelf-Angled.jpg" if angled else "Series_Shelf.jpg"
    img.save(DIR / name, quality=92)
    return img


def shelf(**kw):
    return shelf_scene(False)


def shelf_angled(**kw):
    return shelf_scene(True)


def spines_closeup(vols=(11, 10, 9, 8), dpi=260, out="Series_Spines-Closeup.jpg"):
    light = Light(key=(-0.62, -0.30, 0.73), strip=(0.66, -0.05, 0.75), key_size=0.28)
    strips = [spine_image(n, dpi, light) for n in vols]
    k = dpi / 25.4
    gap = int(1.2 * k)
    hgt = max(s.shape[0] for s in strips)
    total = sum(s.shape[1] for s in strips) + gap * (len(strips) - 1)
    img = np.zeros((hgt, total, 3), np.float32) + 0.02
    x = 0
    for s in strips:              # left to right as they stand: eleven, ten, nine, eight
        img[:s.shape[0], x:x + s.shape[1]] = s
        x += s.shape[1] + gap
    # crop to the upper two thirds, where the title, the medallion and the band are
    img = img[: int(hgt * 0.62)]
    to_image(img, 1.08).save(DIR / out, quality=92)


def hero_head(wb, sw, k=4.0):
    """The head of the standing volume: back board along the far edge, front board along the near one, the spine's
    covering at the right, the gilt page block between."""
    w, h = int(wb * k), max(8, int(sw * k))
    a = np.zeros((h, w, 3), np.float32)
    a[:, :] = (0.72, 0.56, 0.26)
    a *= (0.88 + 0.12 * np.sin(np.arange(h) * 1.7)[:, None, None])
    board = int(2.5 * k)
    a[:board] = (0.04, 0.07, 0.20)
    a[-board:] = (0.04, 0.07, 0.20)
    a[:, -int(3.0 * k):] = (0.06, 0.09, 0.24)
    a[board:-board, -int(4.6 * k):-int(3.0 * k)] = (0.55, 0.42, 0.18)
    return Image.fromarray((AW._srgb(np.clip(a, 0, 1)) * 255).astype(np.uint8))


def front_hero(n=10, dpi=150, out=None, width=2000):
    """One volume standing, turned a little: its front board, its spine at the right (an Arabic book), its head."""
    sps = spines()
    sw = sps[str(n)]["spine_mm"]
    light = Light(key=(-0.55, -0.50, 0.67), strip=(0.7, 0.1, 0.7), key_size=0.30, strip_power=0.30, camera=520)
    front = front_image(n, dpi, light)
    spine = to_image(spine_image(n, int(dpi * 0.8), light))
    H_, Wb = 246.0, 169.0
    # the book in its own frame: the front board in the plane z = 0 facing the camera, the spine at its right
    # edge running back
    faces = [("front", front, [(0, H_, 0), (Wb, H_, 0), (Wb, 0, 0), (0, 0, 0)], 1.0),
             ("spine", spine, [(Wb, H_, 0), (Wb, H_, -sw), (Wb, 0, -sw), (Wb, 0, 0)], 0.78),
             ("head", hero_head(Wb, sw), [(0, H_, -sw), (Wb, H_, -sw), (Wb, H_, 0), (0, H_, 0)], 0.9)]
    h = int(width * 1.18)
    cam = Camera((Wb * 1.55, 330.0, 520.0), (Wb * 0.52, 112.0, -18.0), width * 1.58, (width, h))
    img = render_scene(cam, faces, (width, h), (-300, 500), sw, shadow_rect=(0, Wb))
    img.save(DIR / (out or f"Volume-{n:02d}_Front-Hero.jpg"), quality=92)


def finish_closeup(n=10, dpi=520, out=None):
    """The finishes near, where the matn meets its glosses: the sculpted seam and its jewel, the matn's rules, the
    glosses' gold dots and ruby vowels over their latent letters, the rulings; in raking light."""
    sp = spines()[str(n)]
    fx, fy = sp["front"][0], sp["front"][1]
    sq = 3.0
    clip = (fx + sq + 16, fy + sq + 26, fx + sq + 86, fy + sq + 82)
    light = Light(key=(-0.80, -0.30, 0.52), strip=(0.6, 0.3, 0.74), key_size=0.26, strip_power=0.35, camera=300)
    lin = render(n, dpi, clip=clip, light=light)
    to_image(lin, 1.1).save(DIR / (out or f"Volume-{n:02d}_Finish-Closeup.jpg"), quality=93)


def wrap_view(n=10, dpi=130):
    im = to_image(render(n, dpi), 1.03)
    im.save(DIR / f"Volume-{n:02d}_Wrap.jpg", quality=91)


def main(argv):
    global DIR
    vols = [int(a) for a in argv if a.isdigit()]
    eds = [argv[i + 1] for i, a in enumerate(argv) if a == "--edition"] or list(EDITIONS)
    for ed in eds:
        DIR = OUT / EDITIONS[ed]
        if vols:
            for n in vols:
                wrap_proof(n)
            continue
        from multiprocessing import Pool
        with Pool(4) as p:
            p.map(wrap_proof, range(1, 12))
        series_fronts()
        shelf()
        shelf_angled()
        spines_closeup()
        for n in range(1, 12):               # every volume standing, for the publisher's presentation
            front_hero(n)
        wrap_view(10)
        finish_closeup(10)


if __name__ == "__main__":
    main(sys.argv[1:])
