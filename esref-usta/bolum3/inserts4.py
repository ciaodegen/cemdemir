"""Bölüm 3 (Söküm) detay çekimleri: çarklı pirinç kalp, BURAK / ZEYNEP çarkı, yeni çark."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B
import inserts as ins

BW, BH = 1440, 2560
BRASS = (196, 150, 72)
BRASS_D = (120, 84, 34)
BRASS_L = (240, 206, 130)
COPPER = (176, 104, 60)


def heart_pts(cx, cy, s, n=200):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    return pts


def gear_img(r, teeth, color, angle=0.0, label=None, label_size=None, hub=True, shine=True):
    size = int(r * 2.5)
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = size / 2
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4) + math.radians(angle)
        rr = r * 1.12 if (i % 4) in (1, 2) else r * 0.97
        pts.append((c + math.cos(a) * rr, c + math.sin(a) * rr))
    d.polygon(pts, fill=color + (255,))
    d.ellipse([c - r * 0.9, c - r * 0.9, c + r * 0.9, c + r * 0.9], fill=tuple(min(255, int(v * 1.06)) for v in color) + (255,))
    d.ellipse([c - r * 0.78, c - r * 0.78, c + r * 0.78, c + r * 0.78], outline=tuple(int(v * 0.7) for v in color) + (255,), width=max(2, int(r * 0.03)))
    if hub:
        hr_ = 0.09 if label else 0.16
        d.ellipse([c - r * hr_, c - r * hr_ + (r * 0.32 if label and "\n" in label else r * 0.2 if label else 0), c + r * hr_, c + r * hr_ + (r * 0.32 if label and "\n" in label else r * 0.2 if label else 0)], fill=tuple(int(v * 0.55) for v in color) + (255,))
    if label:
        f = font(FONT_SERIF_B, label_size or int(r * 0.32))
        tx = Image.new("RGBA", (size, size), (0, 0, 0, 0)); td = ImageDraw.Draw(tx)
        lines = label.split("\n")
        y = c - (len(lines) * f.size * 1.1) / 2
        for ln in lines:
            tw = td.textlength(ln, font=f)
            td.text((c - tw / 2, y - r * (0.3 if len(lines) == 1 else 0.12)), ln, font=f, fill=tuple(int(v * 0.45) for v in color) + (235,))
            y += f.size * 1.1
        tx = tx.rotate(-angle, center=(c, c), resample=Image.BICUBIC)
        im.alpha_composite(tx)
    if shine:
        g = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([c - r * 0.7, c - r * 0.85, c + r * 0.1, c - r * 0.2], fill=(255, 245, 210, 70))
        im.alpha_composite(g.filter(ImageFilter.GaussianBlur(r * 0.12)))
    return im


def _brass_fill(mask, top=BRASS_L, bot=BRASS_D):
    w, h = mask.size
    y = np.linspace(0, 1, h)[:, None, None]
    col = np.array(top)[None, None, :] * (1 - y) + np.array(bot)[None, None, :] * y
    arr = np.broadcast_to(col, (h, w, 3)).astype(np.uint8)
    im = Image.fromarray(arr).convert("RGBA"); im.putalpha(mask)
    return im


@functools.lru_cache(maxsize=64)
def heart(step=0, dark_bg=True):
    """The clockwork heart; `step` ticks the gears round (6 degrees per tick)."""
    base = Image.new("RGBA", (BW, BH), (14, 9, 6, 255)) if dark_bg else ins.wood_top(31).copy()
    if dark_bg:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([120, 600, 1320, 2000], fill=(120, 70, 30, 90))
        base.alpha_composite(g.filter(ImageFilter.GaussianBlur(200)))
    cx, cy, s = 720, 1240, 41
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    outer = Image.new("L", (BW, BH), 0); ImageDraw.Draw(outer).polygon(heart_pts(cx, cy, s), fill=255)
    inner = Image.new("L", (BW, BH), 0); ImageDraw.Draw(inner).polygon(heart_pts(cx, cy + 20, s * 0.78), fill=255)
    obj.alpha_composite(_brass_fill(outer))
    win = Image.new("RGBA", (BW, BH), (30, 18, 10, 255)); win.putalpha(inner)
    obj.alpha_composite(win)
    a = step * 6
    gears = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    for (gx, gy, r, n, col, sp) in ((420, 1010, 150, 12, COPPER, -1.6), (1040, 1030, 130, 11, BRASS, -1.8),
                                    (580, 1520, 120, 10, BRASS, 1.9), (900, 1510, 135, 12, COPPER, 1.5)):
        gi = gear_img(r, n, col, a * sp)
        gears.alpha_composite(gi, (int(gx - gi.size[0] / 2), int(gy - gi.size[1] / 2)))
    big = gear_img(235, 18, BRASS, a, "BURAK", 80)
    gears.alpha_composite(big, (int(730 - big.size[0] / 2), int(1230 - big.size[1] / 2)))
    gm = Image.fromarray(np.minimum(np.asarray(gears.split()[3]), np.asarray(inner)))
    gears.putalpha(gm)
    obj.alpha_composite(gears)
    # glass glint + rivets
    gl = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    gd.polygon([(360, 800), (520, 750), (320, 1450), (260, 1300)], fill=(255, 255, 255, 40))
    for p in heart_pts(cx, cy + 6, s * 0.89, 26):
        gd.ellipse([p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11], fill=BRASS_D + (255,))
        gd.ellipse([p[0] - 6, p[1] - 8, p[0] + 3, p[1] - 1], fill=BRASS_L + (255,))
    obj.alpha_composite(gl)
    ins.shadowed(base, obj, blur=40, off=(26, 44), alpha=190)
    return base


@functools.lru_cache(maxsize=64)
def loupe_gear(step=0):
    src = heart(step, False)
    zoom = 2.4
    w, h = BW / zoom, BH / zoom
    cx, cy = 730, 1230
    crop = src.crop((int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))).resize((BW, BH), Image.LANCZOS)
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).ellipse([BW / 2 - 640, 1280 - 640, BW / 2 + 640, 1280 + 640], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    out = Image.new("RGBA", (BW, BH), (8, 5, 3, 255)); out.paste(crop, (0, 0), m)
    ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([BW / 2 - 650, 1280 - 650, BW / 2 + 650, 1280 + 650], outline=(20, 16, 12, 255), width=60)
    out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
    return out


@functools.lru_cache(maxsize=64)
def flip_gear(f=0.0):
    """Single gear on the counter turning over: f 0 -> front (BURAK), 1 -> back (ZEYNEP · 22)."""
    img = ins.wood_top(37).copy()
    front = f < 0.5
    g = gear_img(330, 22, BRASS, 8, "BURAK" if front else "ZEYNEP\n22 yaş", 110 if front else 96)
    sx = max(0.04, abs(math.cos(math.pi * f)))
    g = g.resize((max(2, int(g.size[0] * sx)), g.size[1]), Image.LANCZOS)
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    obj.alpha_composite(g, (int(720 - g.size[0] / 2), int(1260 - g.size[1] / 2)))
    ins.shadowed(img, obj, blur=34, off=(22, 36), alpha=180)
    return img


@functools.lru_cache(None)
def new_gear():
    img = ins.wood_top(41).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    old = gear_img(230, 18, BRASS, 8, "ZEYNEP\n22 yaş", 70)
    new = gear_img(230, 18, (226, 196, 120), 0, None)
    obj.alpha_composite(old, (int(450 - old.size[0] / 2), int(1150 - old.size[1] / 2)))
    obj.alpha_composite(new, (int(990 - new.size[0] / 2), int(1430 - new.size[1] / 2)))
    sp = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sp)
    for (x, y, r) in ((1080, 1290, 26), (900, 1350, 14), (1110, 1520, 12)):
        sd.polygon([(x, y - r * 2), (x + r * 0.4, y - r * 0.4), (x + r * 2, y), (x + r * 0.4, y + r * 0.4), (x, y + r * 2),
                    (x - r * 0.4, y + r * 0.4), (x - r * 2, y), (x - r * 0.4, y - r * 0.4)], fill=(255, 250, 225, 230))
    obj.alpha_composite(sp.filter(ImageFilter.GaussianBlur(1.5)))
    ins.shadowed(img, obj, blur=30, off=(20, 32), alpha=170)
    return img


if __name__ == "__main__":
    ims = [heart(0), heart(3), loupe_gear(0), flip_gear(0.0), flip_gear(0.4), flip_gear(1.0), new_gear()]
    sheet = Image.new("RGB", (300 * len(ims), 533))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((300, 533)), (i * 300, 0))
    sheet.save(sys.argv[1])
