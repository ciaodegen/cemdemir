"""Bölüm 12 (Emeğim Boşa mı?) detay çekimleri: pirinç terazi, slime kavanozu ve altınlar, delik iş eldivenleri, emek etiketleri."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_BOLD, FONT_HAND, FONT_SERIF_B
import inserts as ins
import inserts_m1 as im

BW, BH = 1440, 2560
BRASS = (196, 150, 62, 255)
BRASS_D = (150, 108, 40, 255)
BRASS_L = (236, 200, 110, 255)
TAGS = ["Kardeşinin okul servisi", "Annenin kirası", "Babanın ilacı", "Kardeşin üniversitede"]
PIV = (720, 1120)
ARM = 400
HANG = 560


@functools.lru_cache(None)
def _backdrop():
    img = Image.new("RGBA", (BW, BH), (0, 0, 0, 255))
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    g = np.clip(1 - ((x - 720) / 1100) ** 2 - ((y - 1000) / 1600) ** 2, 0.15, 1)
    wall = np.stack([70 * g, 46 * g, 30 * g], -1)
    img = Image.fromarray(wall.astype(np.uint8)).convert("RGBA")
    wood = ins.wood_top(141).crop((0, 0, BW, BH - 2120)).resize((BW, BH - 2120))
    img.alpha_composite(wood, (0, 2120))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 2112, BW, 2126], fill=(40, 24, 14, 255))
    return img


def _jar(coins=True):
    w, h = 300, 360
    j = Image.new("RGBA", (w, h + 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(j)
    # slime: swirled pink / teal
    sl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sw = np.sin(xx / 30 + yy / 45 + np.sin(yy / 25) * 2)
    col = np.where((sw > 0)[..., None], np.array((236, 120, 190), np.float32), np.array((80, 210, 200), np.float32))
    col *= (0.85 + 0.15 * np.cos(xx / w * math.pi - math.pi / 2))[..., None]
    sli = Image.fromarray(col.astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([18, 70, w - 18, h - 6], radius=40, fill=255)
    sl.paste(sli, (0, 0), m)
    j.alpha_composite(sl, (0, 120))
    # glass
    d.rounded_rectangle([8, 150, w - 8, h + 116], radius=46, outline=(220, 236, 240, 200), width=10)
    d.rounded_rectangle([30, 120, w - 30, 160], radius=10, fill=(200, 200, 206, 255))
    d.line([(40, 200), (40, h + 60)], fill=(255, 255, 255, 140), width=10)
    if coins:
        rng = np.random.default_rng(5)
        for _ in range(14):
            cx, cy = rng.uniform(40, w - 40), rng.uniform(10, 120)
            d.ellipse([cx - 34, cy - 18, cx + 34, cy + 18], fill=(232, 186, 50, 255), outline=(170, 120, 20, 255), width=4)
            d.ellipse([cx - 16, cy - 7, cx + 16, cy + 3], fill=(250, 220, 110, 255))
    return j


def _gloves():
    w, h = 360, 170
    g = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    for k, x0 in enumerate((10, 170)):
        c = (116, 78, 46, 255) if k == 0 else (104, 70, 42, 255)
        d.rounded_rectangle([x0, 60, x0 + 170, 160], radius=36, fill=c)
        for f in range(4):
            fx = x0 + 20 + f * 36
            d.rounded_rectangle([fx, 10 + (f % 2) * 8, fx + 30, 90], radius=14, fill=c)
        # holes and wear
        d.ellipse([x0 + 40, 100, x0 + 70, 124], fill=(220, 168, 132, 255))
        d.ellipse([x0 + 104, 24, x0 + 124, 40], fill=(220, 168, 132, 255))
        d.line([(x0 + 30, 140), (x0 + 150, 136)], fill=(80, 52, 30, 255), width=5)
    return g


def _tag(text):
    f = font(FONT_HAND, 50)
    tmp = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tw = tmp.textlength(text, font=f)
    w, h = int(tw + 90), 112
    t = im.paper(w, h, seed=len(text), lined=False, tint=(246, 236, 210))
    d = ImageDraw.Draw(t)
    d.ellipse([18, h / 2 - 12, 42, h / 2 + 12], fill=(120, 90, 60, 255))
    d.text((60, 22), text, font=f, fill=(34, 52, 140, 255))
    return t


def _pan(layer, cx, top, content, dx=0):
    d = ImageDraw.Draw(layer)
    bowl_y = top + HANG
    for ch in (-150, 0, 150):
        d.line([(cx, top), (cx + ch, bowl_y)], fill=(120, 90, 40, 255), width=6)
    layer.alpha_composite(content, (int(cx - content.size[0] / 2 + dx), int(bowl_y - content.size[1] + 10)))
    d.chord([cx - 200, bowl_y - 50, cx + 200, bowl_y + 70], 0, 180, fill=BRASS)
    d.ellipse([cx - 200, bowl_y - 30, cx + 200, bowl_y + 20], fill=BRASS_L)
    d.ellipse([cx - 186, bowl_y - 22, cx + 186, bowl_y + 12], fill=BRASS_D)


@functools.lru_cache(maxsize=128)
def scale_plate(angle_q=0, jar=True, gloves=True, ntags=0, glow_q=0):
    """angle_q: beam tilt in tenths of degrees (+ = left pan down)."""
    img = _backdrop().copy()
    lay = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # base + pillar
    d.polygon([(520, 2110), (920, 2110), (840, 2040), (600, 2040)], fill=BRASS_D)
    d.rounded_rectangle([700, PIV[1], 740, 2050], radius=14, fill=BRASS)
    d.rectangle([706, PIV[1], 716, 2040], fill=BRASS_L)
    a = math.radians(angle_q / 10)
    lx, ly = PIV[0] - ARM * math.cos(a), PIV[1] + ARM * math.sin(a)
    rx, ry = PIV[0] + ARM * math.cos(a), PIV[1] - ARM * math.sin(a)
    # pans (behind beam)
    content_l = _jar() if jar else Image.new("RGBA", (10, 10))
    stack = Image.new("RGBA", (520, 700), (0, 0, 0, 0))
    if gloves:
        gl = _gloves(); stack.alpha_composite(gl, ((520 - gl.size[0]) // 2, 700 - gl.size[1]))
    y = 700 - 180
    for i in range(ntags):
        t = _tag(TAGS[i]).rotate((-1) ** i * 3, expand=True, resample=Image.BICUBIC)
        if t.size[0] > 480:
            t = t.resize((480, int(t.size[1] * 480 / t.size[0])), Image.LANCZOS)
        y -= t.size[1] - 6
        stack.alpha_composite(t, ((520 - t.size[0]) // 2, y))
    _pan(lay, lx, ly, content_l)
    _pan(lay, rx, ry, stack, -40)
    # beam
    d = ImageDraw.Draw(lay)
    d.line([(lx, ly), (rx, ry)], fill=BRASS, width=30)
    d.line([(lx, ly - 8), (rx, ry - 8)], fill=BRASS_L, width=8)
    d.ellipse([PIV[0] - 40, PIV[1] - 40, PIV[0] + 40, PIV[1] + 40], fill=BRASS_D)
    d.polygon([(PIV[0] - 12, PIV[1] - 30), (PIV[0] + 12, PIV[1] - 30), (PIV[0], PIV[1] - 150)], fill=BRASS)
    for p in ((lx, ly), (rx, ry)):
        d.ellipse([p[0] - 16, p[1] - 16, p[0] + 16, p[1] + 16], fill=BRASS_D)
    if glow_q:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([rx - 360, ry + 120, rx + 360, ry + 760], fill=(255, 230, 150, int(110 * glow_q / 20)))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))
    ins.shadowed(img, lay, blur=22, off=(14, 22), alpha=140)
    return img


if __name__ == "__main__":
    ims = [scale_plate(0, True, True, 0), scale_plate(140, True, True, 0), scale_plate(30, True, True, 2), scale_plate(-140, True, True, 4, 14)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((270, 480)), (i * 270, 0))
    sheet.save(sys.argv[1])
