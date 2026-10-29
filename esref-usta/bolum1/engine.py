import math, random, subprocess, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = "/home/user/cemdemir/esref-usta"
import os
W = int(os.environ.get("RES_W", "720")); H = W * 16 // 9
UI = W / 720.0  # scale for screen-space sizes
FPS = 24

FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
FONT_HAND = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


def smooth(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------- sprites ----------
MOUTHS = {  # cx, my (mustache/lip line), x0, x1, chin
    "esref_1": (197, 122, 150, 245, 168),
    "esref_8": (140, 125, 95, 200, 185),
    "esref_2": (185, 122, 130, 240, 175),
    "deniz_1": (165, 133, 135, 195, 158),
    "deniz_2": (170, 132, 140, 200, 156),
    "deniz_8": (160, 130, 130, 190, 155),
}


@functools.lru_cache(None)
def sprite(name, warm=(1.0, 0.86, 0.70), dark=0.86):
    im = np.asarray(Image.open(f"{ROOT}/karakterler/{name}.png").convert("RGBA")).astype(np.float32)
    h = im.shape[0]
    grad = (1.0 - 0.28 * np.linspace(0, 1, h) ** 1.3)[:, None, None]
    rgb = im[..., :3] * np.array(warm)[None, None, :] * dark * grad
    out = np.concatenate([np.clip(rgb, 0, 255), im[..., 3:]], 2).astype(np.uint8)
    return out


def talk_sprite(name, amp):
    arr = sprite(name)
    if amp <= 0.02 or name not in MOUTHS:
        return Image.fromarray(arr)
    cx, my, x0, x1, chin = MOUTHS[name]
    a = arr.astype(np.float32)
    h, w = a.shape[:2]
    D = amp * (5.0 if name.startswith("esref") else 3.2)
    ys = np.arange(h, dtype=np.float32)[:, None]
    xs = np.arange(w, dtype=np.float32)[None, :]
    vy = np.clip((ys - my) / 6.0, 0, 1) * (1 - np.clip((ys - chin) / 22.0, 0, 1))
    hx = np.clip(1 - np.abs(xs - cx) / ((x1 - x0) / 2.0 + 1e-6), 0, 1)
    hx = hx * hx * (3 - 2 * hx)
    d = D * vy * hx
    sy = np.clip(ys - d, 0, h - 1)
    y0 = np.floor(sy).astype(int); y1 = np.clip(y0 + 1, 0, h - 1); f = (sy - y0)[..., None]
    xi = np.broadcast_to(np.arange(w)[None, :], (h, w))
    warped = a[y0, xi] * (1 - f) + a[y1, xi] * f
    img = Image.fromarray(np.clip(warped, 0, 255).astype(np.uint8))
    # dark mouth opening under the mustache / between lips
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    mw = (x1 - x0) * (0.26 if name.startswith("esref") else 0.42)
    mh = max(1.0, D * 0.9)
    dd.ellipse([cx - mw / 2, my + 0.5, cx + mw / 2, my + 0.5 + mh], fill=(52, 22, 18, 235))
    ov = ov.filter(ImageFilter.GaussianBlur(0.8))
    img.alpha_composite(ov)
    return img


# ---------- world layers (1440x2560) ----------
@functools.lru_cache(None)
def layer(name, blur=0):
    im = Image.open(f"{ROOT}/dukkan/src/{name}.png").convert("RGBA")
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return im


@functools.lru_cache(None)
def emre_silhouette(blur=26):
    """Guest seen from behind: dark hair + navy coat, foreground, out of focus."""
    im = Image.new("RGBA", (1100, 1100), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([60, 560, 1040, 1300], radius=330, fill=(26, 31, 44, 255))  # shoulders/coat
    d.polygon([(470, 560), (630, 560), (600, 700), (500, 700)], fill=(20, 22, 30, 255))  # collar shadow
    d.ellipse([360, 340, 470, 470], fill=(170, 120, 92, 255))   # ear hint
    d.ellipse([370, 120, 740, 600], fill=(30, 22, 18, 255))     # head/hair
    d.ellipse([430, 150, 650, 330], fill=(58, 42, 32, 255))     # hair sheen
    rim = Image.new("RGBA", im.size, (0, 0, 0, 0)); rd = ImageDraw.Draw(rim)
    rd.arc([370, 120, 740, 600], 200, 330, fill=(210, 150, 95, 255), width=16)
    rd.arc([60, 560, 1040, 1300], 205, 335, fill=(150, 120, 100, 255), width=14)
    im.alpha_composite(rim.filter(ImageFilter.GaussianBlur(6)))
    return im.filter(ImageFilter.GaussianBlur(blur))


# ---------- rope ----------
def _resample(pts, step=2.0):
    out = [pts[0]]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        n = max(1, int(L / step))
        for i in range(1, n + 1):
            out.append((x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n))
    return out


def _ell(cx, cy, a, b, ang, n=18):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + a * math.cos(t) * ca - b * math.sin(t) * sa, cy + a * math.cos(t) * sa + b * math.sin(t) * ca)
            for t in (2 * math.pi * i / n for i in range(n))]


def draw_rope(img, pts, width, end_a="flat", end_b="flat", color=(196, 160, 112), seed=1):
    """Twisted 3-strand rope along polyline pts, drawn onto an RGBA image."""
    rnd = random.Random(seed)
    w = float(width)
    dark = tuple(int(c * 0.45) for c in color)
    mid = tuple(int(c * 0.78) for c in color)
    light = tuple(min(255, int(c * 1.22)) for c in color)
    dense = _resample(pts, 2.0)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).line([(x + w * 0.15, y + w * 0.3) for x, y in dense[::3]], fill=(0, 0, 0, 150), width=int(w * 1.05), joint="curve")
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(max(1, w * 0.22))))
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line(dense[::2], fill=dark + (255,), width=int(w * 0.98), joint="curve")
    step = max(2, int(w * 0.36 / 2.0))
    for i in range(0, len(dense) - 1, step):
        x, y = dense[i]
        j = min(i + 2, len(dense) - 1); k = max(i - 2, 0)
        tx, ty = dense[j][0] - dense[k][0], dense[j][1] - dense[k][1]
        L = math.hypot(tx, ty) or 1; tx, ty = tx / L, ty / L
        ang = math.atan2(ty, tx) + math.radians(52)
        d.polygon(_ell(x, y, w * 0.5, w * 0.2, ang), fill=mid + (255,))
        d.polygon(_ell(x - ty * w * 0.04, y + tx * w * 0.04, w * 0.42, w * 0.14, ang), fill=color + (255,))
        d.polygon(_ell(x + ty * w * 0.12 - tx * w * 0.02, y - tx * w * 0.12 - ty * w * 0.02, w * 0.2, w * 0.05, ang), fill=light + (200,))
    # cylinder shading along the edges
    nrm = []
    for i in range(0, len(dense) - 1, 2):
        j = min(i + 2, len(dense) - 1); k = max(i - 2, 0)
        tx, ty = dense[j][0] - dense[k][0], dense[j][1] - dense[k][1]
        L = math.hypot(tx, ty) or 1
        nrm.append((dense[i], (-ty / L, tx / L)))
    edge = Image.new("RGBA", img.size, (0, 0, 0, 0)); ed = ImageDraw.Draw(edge)
    ed.line([(p[0] + n[0] * w * 0.4, p[1] + n[1] * w * 0.4) for p, n in nrm], fill=(30, 18, 8, 120), width=max(1, int(w * 0.2)))
    ed.line([(p[0] - n[0] * w * 0.36, p[1] - n[1] * w * 0.36) for p, n in nrm], fill=(255, 235, 200, 60), width=max(1, int(w * 0.1)))
    lay.alpha_composite(edge.filter(ImageFilter.GaussianBlur(max(0.5, w * 0.06))))
    # clip to the rope body
    body = Image.new("L", img.size, 0)
    ImageDraw.Draw(body).line(dense[::2], fill=255, width=int(w), joint="curve")
    a = ImageChops.multiply(lay.split()[3], body)
    lay.putalpha(a)
    img.alpha_composite(lay)
    d = ImageDraw.Draw(img)
    for kind, p, q in ((end_a, dense[0], dense[min(6, len(dense) - 1)]), (end_b, dense[-1], dense[max(-7, -len(dense))])):
        x, y = p; L = math.hypot(p[0] - q[0], p[1] - q[1]) or 1
        tx, ty = (p[0] - q[0]) / L, (p[1] - q[1]) / L
        nx, ny = -ty, tx
        if kind == "fray":
            for _ in range(int(w * 0.9)):
                o = (rnd.random() - 0.5) * w * 0.9
                ln = w * (0.5 + rnd.random() * 1.1)
                ang = (rnd.random() - 0.5) * 1.1
                ca, sa = math.cos(ang), math.sin(ang)
                fx, fy = tx * ca - ty * sa, tx * sa + ty * ca
                sx, sy = x + nx * o, y + ny * o
                c = color if rnd.random() > 0.4 else light
                d.line([(sx, sy), (sx + fx * ln, sy + fy * ln)], fill=c + (230,), width=max(1, int(w * 0.05)))
        elif kind == "flat":
            ang = math.atan2(ty, tx)
            d.polygon(_ell(x, y, w * 0.16, w * 0.5, ang, 28), fill=(214, 186, 140, 255), outline=dark + (255,))
            for s_ in range(3):
                th = ang + 2 * math.pi * s_ / 3 + 0.5
                d.polygon(_ell(x + math.cos(th) * w * 0.0 + nx * w * 0.2 * math.cos(2 * math.pi * s_ / 3),
                                y + ny * w * 0.2 * math.cos(2 * math.pi * s_ / 3) + tx * 0,
                                w * 0.06, w * 0.15, ang, 14), fill=(186, 154, 108, 200))


# ---------- finishing ----------
@functools.lru_cache(None)
def vignette(strength=0.62):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W * 0.5) / (W * 0.62)) ** 2 + ((y - H * 0.42) / (H * 0.6)) ** 2)
    v = 1 - strength * np.clip((r - 0.45) / 0.75, 0, 1) ** 1.6
    return v[..., None]


rng = np.random.default_rng(5)
DUST = [(rng.random() * W, rng.random() * H, 0.6 + rng.random() * 1.8, rng.random() * 6.28, 0.2 + rng.random() * 0.8) for _ in range(46)]


def finish(img, t, dust=True, grain=True):
    """Warm grade, vignette, floating dust, grain."""
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    arr = arr * vignette()
    arr[..., 0] *= 1.03; arr[..., 2] *= 0.93
    if grain:
        g = np.random.default_rng(int(t * FPS)).normal(0, 4.0, (H // 2, W // 2, 1)).astype(np.float32)
        g = np.repeat(np.repeat(g, 2, 0), 2, 1)
        arr += g
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    if dust:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        for x0, y0, r, ph, sp in DUST:
            x = (x0 + math.sin(t * 0.3 * sp + ph) * 30 + t * 4 * sp) % W
            y = (y0 - t * 9 * sp) % H
            a = int(70 + 60 * math.sin(t * 1.3 + ph))
            d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 220, 160, max(0, a)))
        ov = ov.filter(ImageFilter.GaussianBlur(0.9))
        out = out.convert("RGBA"); out.alpha_composite(ov); out = out.convert("RGB")
    return out


def subtitle(img, text):
    if not text:
        return img
    img = img.convert("RGBA")
    f = font(FONT_BOLD, int(30 * UI))
    d = ImageDraw.Draw(img)
    lines = wrap(text, f, W - int(120 * UI), d)
    y = int(H * 0.705) - (len(lines) - 1) * int(20 * UI)
    for ln in lines:
        tw = d.textlength(ln, font=f)
        x = (W - tw) / 2
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((x, y + 2 * UI), ln, font=f, fill=(0, 0, 0, 230), stroke_width=int(3 * UI), stroke_fill=(0, 0, 0, 200))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(2.2 * UI)))
        d = ImageDraw.Draw(img)
        d.text((x, y), ln, font=f, fill=(255, 255, 255, 255))
        y += int(40 * UI)
    return img.convert("RGB")


def wrap(text, f, maxw, d):
    words = text.split(); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines


# ---------- audio envelopes ----------
@functools.lru_cache(None)
def envelope(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "9600", "-f", "s16le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop = 9600 // FPS
    n = len(x) // hop
    rms = np.array([np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2)) for i in range(n)])
    p = np.percentile(rms, 92) if n else 1
    e = np.clip((rms / (p + 1e-6) - 0.18) / 0.8, 0, 1)
    # light smoothing + flutter so the jaw doesn't freeze open
    e2 = np.convolve(e, [0.25, 0.5, 0.25], mode="same")
    return e2


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())
