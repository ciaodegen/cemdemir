"""Bölüm 7 (Atkı) tezgâh nesneleri: sarı-lacivert atkı + boya kutusu + fırça.

Tek bir yüksek çözünürlüklü çizim hem geniş planda hem yakın planda kullanılır,
böylece nesneler her açıda birebir aynı görünür. Koordinatlar dünya pikseli (shop/door dünyası).
"""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import W, H, font, FONT_BOLD

F = 4                       # hi-res factor
X0, Y0 = 440, 1860          # world box origin
BWW, BWH = 450, 500         # world box size
TOP = 1992                  # counter top line (world)
YELLOW = np.array((246, 200, 30), np.float32)
NAVY = np.array((22, 34, 86), np.float32)
RED = np.array((206, 28, 36), np.float32)

# hanging piece (world)
HX0, HX1 = 548, 698
HY0, HY1 = TOP - 4, TOP + 316
STRIPE = 40


def _w2h(x, y):
    return (x - X0) * F, (y - Y0) * F


def stripe_index(yw):
    return int((yw - HY0) // STRIPE)


@functools.lru_cache(None)
def _hang_base():
    """Returns (rgb float array, alpha, navy-mask) of the hanging piece in hi-res box coords."""
    w, h = BWW * F, BWH * F
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    xw = x / F + X0; yw = y / F + Y0
    wave = 3.0 * np.sin((yw - HY0) / 38.0)
    inside = (xw >= HX0 + wave) & (xw <= HX1 + wave) & (yw >= HY0) & (yw <= HY1)
    band = ((yw - HY0) // STRIPE).astype(int)
    navy = (band % 2 == 1)
    col = np.where(navy[..., None], NAVY, YELLOW)
    u = np.clip((xw - HX0 - wave) / (HX1 - HX0), 0, 1)
    shade = 0.78 + 0.32 * np.sin(u * math.pi) - 0.08 * ((yw - HY0) / (HY1 - HY0))
    rib = 0.93 + 0.07 * np.cos((xw - HX0 - wave) * 2 * math.pi / 3.0)
    col = col * (shade * rib)[..., None]
    a = inside.astype(np.float32)
    # fringe
    fr = np.zeros_like(a)
    for k in range(10):
        fx = HX0 + 6 + k * (HX1 - HX0 - 12) / 9
        fr = np.maximum(fr, ((np.abs(xw - fx - wave - 1.5 * np.sin(k)) < 2.4) & (yw > HY1) & (yw < HY1 + 26 + 4 * math.sin(k * 1.7))).astype(np.float32))
    col = np.where((fr > 0)[..., None], YELLOW * 0.9, col)
    a = np.maximum(a, fr)
    return col, a, navy & inside


@functools.lru_cache(None)
def _noise(seed=7):
    rng = np.random.default_rng(seed)
    n = rng.random((BWH * F // 40, BWW * F // 40)).astype(np.float32)
    im = Image.fromarray((n * 255).astype(np.uint8)).resize((BWW * F, BWH * F), Image.BICUBIC).filter(ImageFilter.GaussianBlur(24))
    v = np.asarray(im).astype(np.float32) / 255
    return (v - v.min()) / (v.max() - v.min())


@functools.lru_cache(None)
def _streaks():
    rng = np.random.default_rng(3)
    s = rng.random((BWH * F, 1)).astype(np.float32)
    s = np.repeat(s, BWW * F, axis=1)
    im = Image.fromarray((s * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur((12, 2)))
    return np.asarray(im).astype(np.float32) / 255


def paint_mask(coat, p):
    """Mask (hi-res) of paint applied. coat 1: Deniz's single swipe; coat 2: all navy stripes; p 0..1 progress."""
    h, w = BWH * F, BWW * F
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    xw = x / F + X0; yw = y / F + Y0
    col, a, navy = _hang_base()
    if coat == 1:
        yc = HY0 + STRIPE * 1.5
        edge = HX0 - 6 + p * (HX1 - HX0 + 12)
        m = (np.abs(yw - yc - (xw - HX0) * 0.08) < STRIPE * 0.62) & (xw < edge)
    else:
        rows = int(HY1 - HY0) // STRIPE
        navies = [r for r in range(rows + 1) if r % 2 == 1]
        k = p * len(navies)
        m = np.zeros((h, w), bool)
        for i, r in enumerate(navies):
            fill = min(1.0, max(0.0, k - i))
            if fill <= 0:
                break
            edge = HX0 - 6 + fill * (HX1 - HX0 + 12)
            m |= (yw >= HY0 + r * STRIPE - 3) & (yw < HY0 + (r + 1) * STRIPE + 3) & (xw < edge)
    return m & (a > 0)


@functools.lru_cache(maxsize=96)
def scarf_layer(coat=0, pq=0, rq=0, glow=0):
    """Hi-res RGBA of the scarf (lying fold + hanging piece). pq/rq: paint/revert progress 0..20."""
    w, h = BWW * F, BWH * F
    col, a, navy = _hang_base()
    col = col.copy()
    if coat and pq:
        m = paint_mask(coat, pq / 20).astype(np.float32)
        if rq:
            r = rq / 20
            n = _noise()
            m = m * np.clip((n - r * 1.15) / 0.12 + 1.0, 0, 1) * (1 - max(0, r - 0.9) * 10)
        st = _streaks()
        paint = RED * (0.85 + 0.25 * st)[..., None]
        col = col * (1 - m[..., None]) + paint * m[..., None]
        if rq:
            # sparkles at the reverting edge, only where paint was
            r = rq / 20
            n = _noise()
            pm = paint_mask(coat, pq / 20)
            edge = np.exp(-((n - r * 1.15) / 0.03) ** 2) * pm * (r < 0.95)
            col = col + edge[..., None] * np.array((255, 225, 140), np.float32) * 0.55
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    img.putalpha(Image.fromarray((a * 255).astype(np.uint8)))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    # shadow on the counter face behind the hanging piece
    sh = Image.new("L", (w, h), 0)
    sx0, sy0 = _w2h(HX0 + 8, HY0 + 6); sx1, sy1 = _w2h(HX1 + 14, HY1 + 24)
    ImageDraw.Draw(sh).rectangle([sx0, sy0, sx1, sy1], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    out.paste(Image.new("RGBA", (w, h), (10, 6, 3, 255)), (0, 0), sh)
    # lying fold on the counter (front view): soft roll with vertical stripes
    fold = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fm = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(fm)
    x0, y0 = _w2h(492, TOP - 46); x1, y1 = _w2h(728, TOP + 2)
    dm.rounded_rectangle([x0, y0, x1, y1], radius=int(22 * F), fill=255)
    x0, y0 = _w2h(520, TOP - 76); x1, y1 = _w2h(700, TOP - 34)
    dm.rounded_rectangle([x0, y0, x1, y1], radius=int(20 * F), fill=255)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xw = xx / F + X0; yw = yy / F + Y0
    vb = (((xw - 492) // 32).astype(int) % 2 == 1)
    fc = np.where(vb[..., None], NAVY, YELLOW)
    up = yw < TOP - 40
    v = np.where(up, np.clip((yw - (TOP - 76)) / 42, 0, 1), np.clip((yw - (TOP - 46)) / 48, 0, 1))
    fc = fc * (0.68 + 0.45 * np.sin(v * math.pi * 0.9 + 0.2))[..., None]
    fimg = Image.fromarray(np.clip(fc, 0, 255).astype(np.uint8)).convert("RGBA"); fimg.putalpha(fm)
    fold.alpha_composite(fimg)
    d = ImageDraw.Draw(fold)
    x0, y0 = _w2h(522, TOP - 40); x1, y1 = _w2h(700, TOP - 30)
    d.line([x0, y0, x1, y0], fill=(0, 0, 0, 90), width=10)
    for k in range(9):   # fringe poking out of the left end
        fx, fy = _w2h(492 - 4, TOP - 40 + k * 4.6)
        d.line([fx, fy, fx - 22 * F, fy + 3 * F], fill=(236, 190, 28, 255), width=int(2.4 * F))
    cs = Image.new("L", (w, h), 0)
    a0, b0 = _w2h(470, TOP - 6); a1, b1 = _w2h(736, TOP + 8)
    ImageDraw.Draw(cs).ellipse([a0, b0, a1, b1], fill=150)
    out.paste(Image.new("RGBA", (w, h), (10, 6, 3, 255)), (0, 0), cs.filter(ImageFilter.GaussianBlur(14)))
    out.alpha_composite(fold)
    out.alpha_composite(img)
    if glow:
        g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        gx0, gy0 = _w2h(HX0 - 30, HY0 - 30); gx1, gy1 = _w2h(HX1 + 30, HY1 + 40)
        ImageDraw.Draw(g).rounded_rectangle([gx0, gy0, gx1, gy1], radius=80, fill=(255, 220, 120, int(70 * glow / 10)))
        out = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)), out)
    return out


@functools.lru_cache(maxsize=4)
def can_layer(brush_on=True):
    w, h = BWW * F, BWH * F
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    cx0, cx1 = 772, 856
    ctop, cbot = TOP - 104, TOP + 1
    # contact shadow
    cs = Image.new("L", (w, h), 0)
    a0, b0 = _w2h(cx0 - 10, cbot - 8); a1, b1 = _w2h(cx1 + 18, cbot + 10)
    ImageDraw.Draw(cs).ellipse([a0, b0, a1, b1], fill=170)
    out.paste(Image.new("RGBA", (w, h), (10, 6, 3, 255)), (0, 0), cs.filter(ImageFilter.GaussianBlur(14)))
    # cylinder body with metallic shading
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xw = xx / F + X0; yw = yy / F + Y0
    u = np.clip((xw - cx0) / (cx1 - cx0), 0, 1)
    metal = (150 + 70 * np.sin(u * math.pi) ** 2 + 40 * np.exp(-((u - 0.3) / 0.06) ** 2))
    body = np.stack([metal, metal * 1.01, metal * 1.04], -1)
    # label: red top half, yellow bottom half
    lab = (yw > ctop + 22) & (yw < cbot - 12)
    redh = lab & (yw < (ctop + cbot) / 2 + 4)
    yelh = lab & ~redh
    sh = (0.7 + 0.42 * np.sin(u * math.pi))[..., None]
    body = np.where(redh[..., None], RED * sh, body)
    body = np.where(yelh[..., None], YELLOW * sh, body)
    m = Image.new("L", (w, h), 0)
    x0, y0 = _w2h(cx0, ctop); x1, y1 = _w2h(cx1, cbot)
    ImageDraw.Draw(m).rounded_rectangle([x0, y0, x1, y1], radius=3 * F, fill=255)
    bimg = Image.fromarray(np.clip(body, 0, 255).astype(np.uint8)).convert("RGBA"); bimg.putalpha(m)
    out.alpha_composite(bimg)
    d = ImageDraw.Draw(out)
    # rims + lid with a red drip
    for yr in (ctop + 20, cbot - 12):
        a0, b0 = _w2h(cx0, yr - 2); a1, b1 = _w2h(cx1, yr + 2)
        d.rectangle([a0, b0, a1, b1], fill=(110, 112, 118, 255))
    a0, b0 = _w2h(cx0, ctop - 9); a1, b1 = _w2h(cx1, ctop + 9)
    d.ellipse([a0, b0, a1, b1], fill=(186, 190, 196, 255))
    a0, b0 = _w2h(cx0 + 6, ctop - 6); a1, b1 = _w2h(cx1 - 6, ctop + 6)
    d.ellipse([a0, b0, a1, b1], fill=(196, 30, 36, 255))
    a0, b0 = _w2h(cx0 + 18, ctop); a1, b1 = _w2h(cx0 + 26, ctop + 24)
    d.rounded_rectangle([a0, b0, a1, b1], radius=4 * F, fill=(196, 30, 36, 255))
    # label text
    f = font(FONT_BOLD, 13 * F)
    for t, yy_, c in (("BOYA", ctop + 32, (250, 236, 220, 255)), ("SARI-KIRMIZI", (ctop + cbot) / 2 + 12, (150, 30, 24, 255))):
        ff = f if t == "BOYA" else font(FONT_BOLD, 9 * F)
        tw = d.textlength(t, font=ff); xx_, yy2 = _w2h((cx0 + cx1) / 2, yy_)
        d.text((xx_ - tw / 2, yy2), t, font=ff, fill=c)
    if brush_on:
        b = brush_img()
        b = b.rotate(-78, expand=True, resample=Image.BICUBIC)
        bx, by = _w2h(cx0 - 26, ctop - 40)
        out.alpha_composite(b, (int(bx), int(by)))
    return out


@functools.lru_cache(None)
def brush_img(wet=True):
    """Brush pointing down (tip at bottom centre), hi-res; world length ~190."""
    L, Wd = 190 * F, 34 * F
    im = Image.new("RGBA", (Wd, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = Wd // 2
    d.rounded_rectangle([cx - 7 * F, 0, cx + 7 * F, 115 * F], radius=7 * F, fill=(150, 92, 48, 255))
    d.rounded_rectangle([cx - 3 * F, 4 * F, cx - 1 * F, 110 * F], radius=F, fill=(196, 140, 90, 255))
    d.rectangle([cx - 12 * F, 112 * F, cx + 12 * F, 140 * F], fill=(180, 182, 188, 255))
    d.rectangle([cx - 12 * F, 116 * F, cx + 12 * F, 119 * F], fill=(130, 132, 138, 255))
    d.polygon([(cx - 13 * F, 140 * F), (cx + 13 * F, 140 * F), (cx + 9 * F, 186 * F), (cx - 9 * F, 186 * F)], fill=(232, 210, 160, 255))
    if wet:
        d.polygon([(cx - 11 * F, 162 * F), (cx + 11 * F, 162 * F), (cx + 9 * F, 188 * F), (cx - 9 * F, 188 * F)], fill=(200, 28, 34, 255))
    return im


@functools.lru_cache(maxsize=64)
def _brush_rot(angle_q, wet=True):
    return brush_img(wet).rotate(angle_q, expand=True, resample=Image.BICUBIC)


def _paste_scaled(frame, img, wx, wy, cam):
    """Composite a hi-res layer whose top-left sits at world (wx, wy)."""
    cx, cy, cw = cam
    s = W / cw
    ch = cw * H / W
    sx = (wx - (cx - cw / 2)) * s; sy = (wy - (cy - ch / 2)) * s
    k = s / F
    im = img.resize((max(1, int(img.size[0] * k)), max(1, int(img.size[1] * k))), Image.LANCZOS)
    frame.alpha_composite(im, (int(round(sx)), int(round(sy))))


def overlay(scarf=True, can=True, brush_on=True, coat=0, p=0.0, r=0.0, glow=0.0,
            scarf_drop=1.0, can_slide=1.0, brush=None):
    """Returns an overlay(frame, cam) callable. brush = (tip_world_x, tip_world_y, angle_deg)."""
    def f(frame, cam):
        if scarf and scarf_drop > 0:
            k = scarf_drop
            dy = -120 * (1 - k) ** 2
            lay = scarf_layer(coat, int(round(p * 20)), int(round(r * 20)), int(round(glow * 10)))
            if k < 1:
                lay = lay.copy(); lay.putalpha(Image.eval(lay.split()[3], lambda v: int(v * min(1, k * 2.5))))
            _paste_scaled(frame, lay, X0, Y0 + dy, cam)
        if can and can_slide > 0:
            dx = -260 * (1 - can_slide) ** 2
            lay = can_layer(brush_on)
            if can_slide < 1:
                lay = lay.copy(); lay.putalpha(Image.eval(lay.split()[3], lambda v: int(v * min(1, can_slide * 3))))
            _paste_scaled(frame, lay, X0 + dx, Y0, cam)
        if brush:
            tx, ty, ang = brush
            b = _brush_rot(int(round(ang)))
            # tip of the unrotated brush is at bottom centre; find it after rotation
            bw, bh = brush_img().size
            a = math.radians(ang)
            vx, vy = 0, bh / 2
            rx = vx * math.cos(a) + vy * math.sin(a); ry = -vx * math.sin(a) + vy * math.cos(a)
            tipx = b.size[0] / 2 + rx; tipy = b.size[1] / 2 + ry
            _paste_scaled(frame, b, tx - tipx / F, ty - tipy / F, cam)
    return f


if __name__ == "__main__":
    import scenes3d as s3
    out = sys.argv[1]
    ims = [s3.shop(0, s3.WIDE, rope="none", overlay=overlay()),
           s3.shop(0, (623, 2090, 420), rope="none", usta_blur=6, deniz_blur=8, bg_blur=8,
                   overlay=overlay(brush_on=False, coat=2, p=1.0, brush=(650, 2160, 35))),
           s3.shop(0, (623, 2090, 420), rope="none", usta_blur=6, deniz_blur=8, bg_blur=8,
                   overlay=overlay(brush_on=False, coat=2, p=1.0, r=0.5))]
    sheet = Image.new("RGB", (400 * len(ims), 711))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((400, 711)), (i * 400, 0))
    sheet.save(out)
