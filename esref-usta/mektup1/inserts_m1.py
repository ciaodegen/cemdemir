"""Mektup 1 detay çekimleri: zarf, takipçinin mektubu, Usta'nın cevabı."""
import sys, functools, math
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_HAND, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
INK = (28, 40, 110, 255)
INK_U = (40, 30, 24, 255)       # Usta's ink: dark brown-black
RED_INK = (178, 30, 34, 255)


def paper(w, h, seed=1, lined=True, tint=(246, 241, 228)):
    rng = np.random.default_rng(seed)
    a = np.ones((h, w, 3), np.float32) * np.array(tint, np.float32)
    n = rng.normal(0, 3.0, (h // 4, w // 4)).astype(np.float32)
    n = np.asarray(Image.fromarray(n).resize((w, h), Image.BICUBIC))
    a += n[..., None]
    yy = np.linspace(-1, 1, h)[:, None]; xx = np.linspace(-1, 1, w)[None, :]
    a *= (1 - 0.06 * (xx ** 2 + yy ** 2))[..., None]
    p = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(p)
    if lined:
        for y in range(260, h - 80, 118):
            d.line([(70, y), (w - 70, y)], fill=(170, 190, 215, 255), width=3)
        d.line([(150, 0), (150, h)], fill=(220, 150, 150, 255), width=3)
    # soft fold line in the middle
    d.line([(0, h // 2), (w, h // 2)], fill=(222, 214, 196, 255), width=4)
    return p


@functools.lru_cache(None)
def envelope_img(ariza="Hâlâ özlüyorum."):
    w, h = 1060, 660
    e = paper(w, h, seed=4, lined=False, tint=(244, 236, 218))
    d = ImageDraw.Draw(e)
    # airmail border
    k = 0
    for x in range(0, w, 46):
        c = (186, 36, 40, 255) if k % 2 == 0 else (32, 60, 130, 255)
        d.polygon([(x, 0), (x + 30, 0), (x + 14, 22), (x - 16, 22)], fill=c)
        d.polygon([(x, h), (x + 30, h), (x + 46, h - 22), (x + 16, h - 22)], fill=c)
        k += 1
    # stamp
    d.rectangle([w - 210, 60, w - 70, 230], fill=(250, 246, 236, 255), outline=(170, 40, 40, 255), width=6)
    d.rectangle([w - 190, 80, w - 90, 210], fill=(196, 70, 60, 255))
    cx, cy = w - 140, 145
    pts = []
    for i in range(60):
        t = 2 * math.pi * i / 60
        pts.append((cx + 2.6 * 16 * math.sin(t) ** 3, cy - 2.6 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))))
    d.polygon(pts, fill=(250, 236, 220, 255))
    for r in (70, 82):
        d.arc([w - 330 - r, 140 - r, w - 330 + r, 140 + r], 0, 360, fill=(90, 90, 100, 150), width=4)
    fh = font(FONT_HAND, 104)
    d.text((140, 230), "Eşref Usta'ya", font=fh, fill=INK)
    d.text((170, 360), "Tamir Atölyesi", font=font(FONT_HAND, 60), fill=INK)
    d.text((140, 470), "Arıza: " + ariza, font=font(FONT_HAND, 70), fill=RED_INK)
    return e.rotate(-4, expand=True, resample=Image.BICUBIC)


@functools.lru_cache(maxsize=64)
def envelope_plate(kq=20, ariza="Hâlâ özlüyorum."):
    """kq 0..20: envelope slides in from the top and settles."""
    k = kq / 20
    img = ins.wood_top(23).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    e = envelope_img(ariza)
    e2 = e.rotate(-14 * (1 - k), expand=True, resample=Image.BICUBIC) if k < 1 else e
    y = int(860 - 1900 * (1 - k) ** 3)
    obj.alpha_composite(e2, ((BW - e2.size[0]) // 2, y))
    ins.shadowed(img, obj, blur=28, off=(18, 30), alpha=160)
    return img


LETTER = [("Eşref Usta,", 0), ("9 senelik evliliğimi", 1), ("bitireli 3 sene oldu.", 1),
          ("Hâlâ özlüyorum.", 2), ("Çocuk da var,", 3), ("10 yaşında.", 4), ("— Bir takipçin", 5)]
REPLY = [("Özlemek arıza değil evlat.", 0), ("Dokuz yıl kolay sökülmez.", 0),
         ("Bir parçası hâlâ çalışıyor:", 1), ("on yaşında bir çocuk.", 2),
         ("Evlilik biter.", 3), ("Anne babalık bitmez.", 4)]


def _sheet(lines, reveal, ink, title=None, seed=1, size=96, pen=False, pencil=False):
    w, h = 1240, 1820
    p = paper(w, h, seed=seed)
    d = ImageDraw.Draw(p)
    f = font(FONT_HAND, size)
    row0 = 0
    if title:
        d.text((190, 260 - 0.8 * 78), title, font=font(FONT_HAND, 78), fill=ink)
        row0 = 1
    tip = None
    for i, (txt, _) in enumerate(lines):
        n = reveal[i] if i < len(reveal) else 0
        if n <= 0:
            continue
        s = txt[:n]
        sig = txt.startswith("—")
        x = 190 + (80 if sig else 0)
        base = 260 + 118 * (i + row0 + (1 if sig else 0))
        y = base - 0.8 * size
        d.text((x, y), s, font=f, fill=ink)
        if n < len(txt):
            tip = (x + d.textlength(s, font=f), base - 8)
    if pen and tip:
        a = math.radians(58)
        dx, dy = math.cos(a), math.sin(a)
        nx, ny = -dy, dx
        tx, ty = tip
        def pt(u, v):
            return (tx + dx * u + nx * v, ty + dy * u + ny * v)
        if pencil:   # the short, freshly sharpened yellow pencil stub
            d.polygon([pt(0, 0), pt(26, -6), pt(26, 6)], fill=(60, 60, 64, 255))
            d.polygon([pt(26, -6), pt(80, -20), pt(80, 20), pt(26, 6)], fill=(222, 186, 140, 255))
            d.polygon([pt(80, -20), pt(230, -20), pt(230, 20), pt(80, 20)], fill=(236, 186, 40, 255))
            d.line([pt(82, -7), pt(228, -7)], fill=(250, 214, 90, 255), width=5)
            d.line([pt(82, 9), pt(228, 9)], fill=(200, 150, 20, 255), width=4)
            d.polygon([pt(230, -21), pt(262, -21), pt(262, 21), pt(230, 21)], fill=(186, 188, 194, 255))
            d.polygon([pt(262, -20), pt(300, -20), pt(300, 20), pt(262, 20)], fill=(236, 150, 160, 255))
        else:
            d.polygon([pt(0, 0), pt(90, -14), pt(90, 14)], fill=(200, 170, 90, 255))
            d.polygon([pt(88, -16), pt(560, -18), pt(560, 18), pt(88, 16)], fill=(30, 30, 34, 255))
            d.polygon([pt(150, -17), pt(180, -17), pt(180, 17), pt(150, 17)], fill=(196, 160, 80, 255))
            d.line([pt(200, -8), pt(540, -9)], fill=(90, 90, 100, 255), width=4)
    return p


@functools.lru_cache(maxsize=256)
def letter_plate(reveal, lines=None):
    img = ins.wood_top(31).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    s = _sheet(lines or LETTER, reveal, INK, seed=2).rotate(2, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(s, ((BW - s.size[0]) // 2, 360))
    ins.shadowed(img, obj, blur=28, off=(18, 30), alpha=160)
    return img


@functools.lru_cache(maxsize=256)
def reply_plate(reveal, pen=True, lines=None, ink=None, pencil=False):
    img = ins.wood_top(37).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    s = _sheet(lines or REPLY, reveal, ink or INK_U, title="Cevap —", seed=5, size=88, pen=pen, pencil=pencil).rotate(-2, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(s, ((BW - s.size[0]) // 2, 360))
    ins.shadowed(img, obj, blur=28, off=(18, 30), alpha=160)
    return img


if __name__ == "__main__":
    full = tuple(len(t) for t, _ in LETTER)
    ims = [envelope_plate(10), envelope_plate(20), letter_plate(full),
           reply_plate((26, 25, 27, 10, 0, 0))]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
