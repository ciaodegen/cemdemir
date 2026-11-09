"""Bölüm 13 (Severek Ayrılınır mı?) fotoğraf çekimleri: Boğaz kıyısında birbirinden uzak iki kişi, ikisi de giderken dönüp birbirine bakıyor."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_HAND
import inserts as ins

BW, BH = 1440, 2560
PW, PH = 1200, 780                  # photo (inside the white border)
PX, PY = (BW - PW) // 2, 1280 - PH // 2
GROUND = 620                         # promenade line inside the photo
HER = (270, GROUND)                  # feet positions inside the photo
HIM = (930, GROUND)


def _scene():
    y, x = np.mgrid[0:PH, 0:PW].astype(np.float32)
    v = y / GROUND
    sky = np.stack([250 - 90 * v, 170 - 70 * v, 120 + 20 * v], -1)
    sun = np.exp(-(((x - 600) / 140) ** 2 + ((y - 430) / 140) ** 2))
    sky += sun[..., None] * np.array((60, 50, 20))
    img = Image.fromarray(np.clip(sky, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # sea
    d.rectangle([0, 470, PW, GROUND], fill=(90, 92, 128, 255))
    for k in range(12):
        yy = 480 + k * 10
        d.line([(570 - k * 10, yy), (630 + k * 10, yy)], fill=(250, 200, 140, 150), width=3)
    # far skyline with a tower
    sk = [(0, 470), (0, 440), (90, 440), (90, 420), (180, 420), (180, 445), (300, 445), (300, 430), (420, 430), (420, 450),
          (760, 450), (760, 410), (800, 410), (800, 360), (812, 330), (824, 360), (824, 410), (860, 410), (860, 440),
          (1000, 440), (1000, 425), (1110, 425), (1110, 445), (PW, 445), (PW, 470)]
    d.polygon(sk, fill=(70, 58, 86, 255))
    # promenade and railing
    d.rectangle([0, GROUND, PW, PH], fill=(118, 102, 94, 255))
    for k in range(6):   # paving lines
        yy = GROUND + 18 + k * k * 9
        d.line([(0, yy), (PW, yy)], fill=(108, 93, 86, 255), width=3)
    d.line([(0, 548), (PW, 548)], fill=(60, 50, 50, 255), width=6)
    for x0 in range(20, PW, 80):
        d.line([(x0, 548), (x0, GROUND)], fill=(60, 50, 50, 255), width=5)
    return img


SKIN = {"A": (232, 186, 154, 255), "B": (222, 176, 144, 255)}
SKIN_D = {"A": (212, 162, 132, 255), "B": (200, 152, 122, 255)}


def _person(d, fx, fy, s, who):
    """s = walking direction (-1 left, +1 right). Body strides that way, the head is turned back (-s)."""
    X = lambda dx: fx + s * dx
    coat = (196, 170, 124, 255) if who == "A" else (46, 58, 86, 255)
    coat_d = (170, 144, 102, 255) if who == "A" else (34, 44, 66, 255)
    leg = (60, 50, 50, 255) if who == "A" else (40, 40, 46, 255)
    hair = (78, 44, 26, 255) if who == "A" else (36, 28, 24, 255)
    # long shadow on the promenade
    d.polygon([(X(-60), fy), (X(60), fy), (X(30), fy + 40), (X(-120), fy + 40)], fill=(96, 82, 76, 255))
    # back props: suitcase (her) / backpack (him), both behind, on the -s side
    if who == "A":
        sx0, sx1 = sorted((X(-110), X(-200)))
        d.line([(X(-96), fy - 236), (X(-130), fy - 150)], fill=(50, 40, 40, 255), width=8)   # handle
        d.rounded_rectangle([sx0, fy - 160, sx1, fy - 14], radius=14, fill=(150, 46, 52, 255))
        d.line([((sx0 + sx1) / 2, fy - 150), ((sx0 + sx1) / 2, fy - 24)], fill=(120, 34, 40, 255), width=6)
        for wx in (sx0 + 16, sx1 - 16):
            d.ellipse([wx - 10, fy - 18, wx + 10, fy + 2], fill=(30, 26, 26, 255))
    else:
        bx0, bx1 = sorted((X(-36), X(-96)))
        d.rounded_rectangle([bx0, fy - 400, bx1, fy - 236], radius=22, fill=(110, 120, 70, 255))
        d.rounded_rectangle([min(X(-50), X(-100)), fy - 340, max(X(-50), X(-100)), fy - 270], radius=12, fill=(92, 100, 58, 255))
    # legs: front leg toward s, back leg toward -s
    d.line([(X(10), fy - 170), (X(62), fy - 8)], fill=leg, width=22)
    d.line([(X(-10), fy - 170), (X(-44), fy - 6)], fill=leg, width=22)
    for footx, lift in ((X(62), 0), (X(-44), 4)):
        d.ellipse([min(footx, footx + s * 40) - 4, fy - 14 - lift, max(footx, footx + s * 40) + 4, fy + 6 - lift], fill=(34, 28, 28, 255))
    # back arm (behind the body) swinging toward -s
    d.line([(X(-26), fy - 380), (X(-96), fy - 240)], fill=coat_d, width=30)
    d.ellipse([X(-96) - 14, fy - 254, X(-96) + 14, fy - 226], fill=SKIN_D[who])
    # torso / coat, leaning slightly forward, tail flaring back
    if who == "A":
        body = [(X(-40), fy - 400), (X(44), fy - 400), (X(66), fy - 150), (X(-56), fy - 150), (X(-86), fy - 166)]
    else:
        body = [(X(-48), fy - 410), (X(50), fy - 410), (X(56), fy - 170), (X(-50), fy - 170)]
    d.polygon(body, fill=coat)
    if who == "A":   # red scarf, end flying back
        d.rounded_rectangle([min(X(-40), X(44)), fy - 412, max(X(-40), X(44)), fy - 380], radius=12, fill=(190, 44, 52, 255))
        d.polygon([(X(-30), fy - 400), (X(-110), fy - 380), (X(-96), fy - 356), (X(-20), fy - 380)], fill=(190, 44, 52, 255))
    # front arm swinging toward s
    d.line([(X(28), fy - 384), (X(84), fy - 250)], fill=coat, width=30)
    d.ellipse([X(84) - 14, fy - 264, X(84) + 14, fy - 236], fill=SKIN[who])
    # neck + head, face turned back toward -s
    hx, hy = X(2), fy - 470
    d.rectangle([hx - 14, hy + 30, hx + 14, hy + 70], fill=SKIN_D[who])
    if who == "A":   # long hair falling behind (s side)
        d.polygon([(X(-6), hy - 40), (X(52), hy - 20), (X(64), hy + 120), (X(4), hy + 128)], fill=hair)
    d.ellipse([hx - 48, hy - 52, hx + 48, hy + 48], fill=SKIN[who])
    if who == "A":
        d.chord([hx - 54, hy - 64, hx + 54, hy + 30], 180, 360, fill=hair)
        d.polygon([(X(10), hy - 40), (X(54), hy - 20), (X(52), hy + 40), (X(16), hy + 14)], fill=hair)
    else:
        d.chord([hx - 52, hy - 66, hx + 52, hy + 6], 180, 360, fill=hair)
        d.polygon([(X(4), hy - 34), (X(52), hy - 26), (X(48), hy + 22), (X(20), hy + 8)], fill=hair)
    # face on the -s side: eye, brow, nose, mouth, cheek
    ex = X(-22)
    d.ellipse([ex - 7, hy - 10, ex + 7, hy + 6], fill=(40, 30, 26, 255))
    d.line([(ex - 12, hy - 22), (ex + 10, hy - 26)], fill=hair, width=5)
    d.polygon([(X(-44), hy + 2), (X(-58), hy + 16), (X(-42), hy + 20)], fill=SKIN_D[who])
    d.line([(X(-34), hy + 32), (X(-20), hy + 30)], fill=(150, 80, 70, 255), width=4)
    if who == "A":
        d.ellipse([X(-14) - 12, hy + 8, X(-14) + 12, hy + 24], fill=(236, 150, 140, 200))


def _woman(d, fx, fy):
    _person(d, fx, fy, -1, "A")


def _man(d, fx, fy):
    _person(d, fx, fy, +1, "B")


@functools.lru_cache(None)
def _photo_base():
    ph = _scene()
    d = ImageDraw.Draw(ph)
    _woman(d, *HER)
    _man(d, *HIM)
    # warm film look
    ph = Image.blend(ph, Image.new("RGBA", ph.size, (255, 200, 140, 255)), 0.08)
    return ph


def photo(gaze=0.0):
    ph = _photo_base().copy()
    if gaze > 0:   # a soft golden line between the two gazes
        g = Image.new("RGBA", ph.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        a = (HER[0] + 22, HER[1] - 472); b = (HIM[0] - 22, HIM[1] - 472)
        n = int(30 * gaze)
        for k in range(n):
            t = k / 30
            p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t - 60 * math.sin(math.pi * t))
            gd.ellipse([p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8], fill=(255, 228, 140, 245))
        ph.alpha_composite(g.filter(ImageFilter.GaussianBlur(2)))
        ph.alpha_composite(g.filter(ImageFilter.GaussianBlur(10)))
    # white border
    out = Image.new("RGBA", (PW + 60, PH + 60), (246, 242, 234, 255))
    out.alpha_composite(ph, (30, 30))
    return out


@functools.lru_cache(maxsize=128)
def photo_plate(gaze_q=0):
    img = ins.wood_top(161).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    p = photo(gaze_q / 20).rotate(-2, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(p, ((BW - p.size[0]) // 2, 1280 - p.size[1] // 2))
    ins.shadowed(img, obj, blur=26, off=(16, 28), alpha=160)
    return img


def photo_point(px, py):
    """Plate coordinates of a point given in photo coordinates (rotation ignored, close enough for camera framing)."""
    return (BW - (PW + 60)) / 2 + 30 + px, 1280 - (PH + 60) / 2 + 30 + py


if __name__ == "__main__":
    ims = [photo_plate(), photo_plate(20)]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
