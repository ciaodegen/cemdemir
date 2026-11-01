"""Bölüm 7 (Boyanmayan Kalp) detay çekimleri: sarı-lacivert kalp, stetoskop, boya kutusu, Deniz'in göğsü."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
YELLOW = (246, 200, 30)
NAVY = (22, 34, 86)


def heart_pts(cx, cy, s, n=200):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    return pts


def striped_heart(scale=1.0, glow=0.0):
    """Yellow-navy striped heart with soft 3D shading; glow 0..1 makes the stripes shine."""
    s = 34 * scale
    cx, cy = 720, 1200
    m = Image.new("L", (BW, BH), 0); ImageDraw.Draw(m).polygon(heart_pts(cx, cy, s), fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.5))
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    band = (((x - cx) * 0.35 + (y - cy)) / (64 * scale)) % 2.0 < 1.0
    col = np.where(band[..., None], np.array(YELLOW, np.float32), np.array(NAVY, np.float32))
    r = np.sqrt(((x - cx + 120 * scale) / (420 * scale)) ** 2 + ((y - cy + 160 * scale) / (420 * scale)) ** 2)
    col *= (1.25 - 0.55 * np.clip(r, 0, 1.4))[..., None]
    col += glow * 80 * band[..., None]
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    img.putalpha(m)
    hl = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse([cx - 300 * scale, cy - 380 * scale, cx - 90 * scale, cy - 230 * scale], fill=(255, 255, 255, 90))
    img.alpha_composite(hl.filter(ImageFilter.GaussianBlur(30 * scale)))
    if glow > 0:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).polygon(heart_pts(cx, cy, s * 1.08), fill=(255, 220, 90, int(110 * glow)))
        img = Image.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)), img)
    return img


def stethoscope(obj, end=(720, 1250), from_top=True):
    d = ImageDraw.Draw(obj)
    ex, ey = end
    pts = [(ex + 260, -40), (ex + 300, 300), (ex + 180, ey - 420), (ex + 60, ey - 160), (ex, ey - 40)]
    d.line(pts, fill=(40, 40, 44, 255), width=26, joint="curve")
    d.ellipse([ex - 95, ey - 95, ex + 95, ey + 95], fill=(170, 172, 178, 255))
    d.ellipse([ex - 70, ey - 70, ex + 70, ey + 70], fill=(210, 212, 218, 255))
    d.ellipse([ex - 40, ey - 60, ex + 10, ey - 25], fill=(255, 255, 255, 120))


@functools.lru_cache(maxsize=48)
def heart_plate(pulse_q=0, glow_q=0, steth=True, paint=True):
    """pulse_q 0..10 scales the heart (beat), glow_q 0..10 lights it up."""
    img = ins.wood_top(67).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    if paint:
        d = ImageDraw.Draw(obj)
        d.rounded_rectangle([1010, 1780, 1330, 2120], radius=20, fill=(150, 154, 160, 255))
        d.ellipse([1010, 1740, 1330, 1820], fill=(176, 180, 186, 255))
        d.ellipse([1035, 1752, 1305, 1808], fill=(200, 30, 36, 255))
        d.ellipse([1110, 1762, 1230, 1798], fill=(246, 200, 30, 255))
        d.rectangle([1040, 1880, 1300, 2020], fill=(240, 236, 226, 255))
        f = font(FONT_BOLD, 44)
        for t, yy, c in (("SARI", 1890, (200, 160, 0, 255)), ("KIRMIZI", 1945, (190, 24, 30, 255))):
            tw = d.textlength(t, font=f); d.text((1170 - tw / 2, yy), t, font=f, fill=c)
    obj.alpha_composite(striped_heart(1.0 + 0.06 * pulse_q / 10, glow_q / 10))
    if steth:
        stethoscope(obj, (760, 1180))
    ins.shadowed(img, obj, blur=34, off=(22, 36), alpha=175)
    return img


@functools.lru_cache(maxsize=16)
def deniz_chest(pulse_q=0):
    img = Image.new("RGBA", (BW, BH), (28, 76, 86, 255))
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(3)
    for _ in range(700):
        x, y = rng.uniform(0, BW), rng.uniform(0, BH)
        d.line([(x, y), (x + 6, y + 2)], fill=(34, 86, 96, 255), width=3)
    d.polygon([(250, 2560), (420, 600), (560, 600), (430, 2560)], fill=(64, 92, 140, 255))
    d.polygon([(1190, 2560), (1020, 600), (880, 600), (1010, 2560)], fill=(64, 92, 140, 255))
    d.ellipse([440, 640, 520, 720], fill=(190, 180, 150, 255))
    d.ellipse([920, 640, 1000, 720], fill=(190, 180, 150, 255))
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    k = 1.0 + 0.05 * pulse_q / 10
    stethoscope(obj, (720, int(1250 + (k - 1) * -200)))
    if pulse_q:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([720 - 300 * k, 1250 - 300 * k, 720 + 300 * k, 1250 + 300 * k], fill=(250, 60, 50, int(60 * pulse_q / 10)))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))
    ins.shadowed(img, obj, blur=26, off=(16, 26), alpha=150)
    return img


if __name__ == "__main__":
    ims = [heart_plate(0, 0, False, True), heart_plate(0, 0, True, True), heart_plate(10, 10, True, True), deniz_chest(10)]
    sheet = Image.new("RGB", (300 * len(ims), 533))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((300, 533)), (i * 300, 0))
    sheet.save(sys.argv[1])
