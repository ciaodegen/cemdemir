"""Bölüm 9 (Uzak Mesafe) detay çekimleri: İstanbul→İzmir otobüs biletleri, şerit metre, göğüste 0 cm."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_BOLD, FONT_HAND, FONT_SERIF_B
import inserts as ins
import inserts_m1 as im

BW, BH = 1440, 2560
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
INK = (34, 52, 140, 255)
TICKETS = [("12.01", ("Doğum gününde", "gittiğin bilet.")),
           ("03.02", ("Sınavından önce, sadece", "elini tutmaya gittiğin.")),
           ("17.03", ("3 saat kalmıştın,", "ama değmişti."))]
SPOTS = [(700, 560, -3), (840, 1260, 2), (700, 1960, -2)]


def ticket(date, note, note_n):
    """note: tuple of lines; note_n: total chars revealed across the lines."""
    w, h = 900, 440
    p = im.paper(w, h, seed=int(date.replace(".", "")), lined=False, tint=(250, 246, 236))
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 74], fill=(170, 40, 46, 255))
    d.text((28, 16), "EGE YOLU  ·  OTOBÜS BİLETİ", font=font(MONO_B, 36), fill=(250, 240, 236, 255))
    d.text((28, 98), "İSTANBUL", font=font(FONT_BOLD, 56), fill=(30, 30, 36, 255))
    d.text((330, 104), "→", font=font(FONT_BOLD, 52), fill=(170, 40, 46, 255))
    d.text((410, 98), "İZMİR", font=font(FONT_BOLD, 56), fill=(30, 30, 36, 255))
    d.text((28, 178), f"Tarih: {date}   Kalkış: 23:30   Koltuk: 21", font=font(MONO, 28), fill=(90, 90, 96, 255))
    for x in range(w - 170, w - 30, 9):   # barcode
        d.rectangle([x, 100, x + (3 if (x // 9) % 3 else 6), 200], fill=(30, 30, 36, 255))
    for x in range(20, w - 20, 24):
        d.line([(x, 232), (x + 12, 232)], fill=(150, 150, 156, 255), width=3)
    y = 250
    for line in note:
        if note_n <= 0:
            break
        d.text((40, y), line[:note_n], font=font(FONT_HAND, 66), fill=INK)
        note_n -= len(line); y += 84
    return p


@functools.lru_cache(maxsize=128)
def tickets_plate(n, notes=(0, 0, 0), tape=0.0, counter=""):
    """n tickets on the counter; notes = chars revealed per note; tape 0..1 stretches a tape measure."""
    img = ins.wood_top(101).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    for i in range(min(n, len(TICKETS))):
        date, note = TICKETS[i]
        t = ticket(date, note, notes[i] if i < len(notes) else 0).rotate(SPOTS[i][2], expand=True, resample=Image.BICUBIC)
        x, y, _ = SPOTS[i]
        obj.alpha_composite(t, (int(x - t.size[0] / 2), int(y - t.size[1] / 2)))
    ins.shadowed(img, obj, blur=24, off=(16, 26), alpha=160)
    if tape > 0:
        top = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        _tape(top, (150, 2330), (150, 300), tape, counter, 320)
        ins.shadowed(img, top, blur=14, off=(10, 16), alpha=150)
    return img


def _casing(counter, size=300):
    c = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=(236, 186, 34, 255))
    d.rounded_rectangle([size * 0.08, size * 0.08, size * 0.92, size * 0.92], radius=int(size * 0.18), outline=(196, 146, 20, 255), width=6)
    d.rounded_rectangle([size * 0.14, size * 0.3, size * 0.86, size * 0.62], radius=14, fill=(250, 250, 246, 255), outline=(40, 40, 44, 255), width=5)
    f = font(MONO_B, int(size * 0.17))
    tw = d.textlength(counter, font=f)
    d.text(((size - tw) / 2, size * 0.355), counter, font=f, fill=(20, 20, 24, 255))
    d.rectangle([size * 0.35, size * 0.72, size * 0.65, size * 0.8], fill=(60, 60, 64, 255))
    return c


def _tape(layer, start, end, k, counter, csize=300):
    """Yellow blade from the casing at `start` toward `end` (fraction k), casing drawn at start."""
    d = ImageDraw.Draw(layer)
    sx, sy = start; ex, ey = end
    tx, ty = sx + (ex - sx) * k, sy + (ey - sy) * k
    ang = math.atan2(ty - sy, tx - sx)
    nx, ny = -math.sin(ang) * 26, math.cos(ang) * 26
    d.polygon([(sx + nx, sy + ny), (tx + nx, ty + ny), (tx - nx, ty - ny), (sx - nx, sy - ny)], fill=(246, 206, 46, 255))
    L = math.hypot(tx - sx, ty - sy)
    for i in range(0, int(L), 22):
        px, py = sx + math.cos(ang) * i, sy + math.sin(ang) * i
        m = 20 if i % 110 == 0 else 10
        d.line([(px + nx * 0.95, py + ny * 0.95), (px + nx * (0.95 - m / 26), py + ny * (0.95 - m / 26))], fill=(30, 30, 30, 255), width=3)
    d.polygon([(tx + nx, ty + ny), (tx - nx, ty - ny), (tx - nx + math.cos(ang) * 14, ty - ny + math.sin(ang) * 14),
               (tx + nx + math.cos(ang) * 14, ty + ny + math.sin(ang) * 14)], fill=(150, 152, 160, 255))
    c = _casing(counter, csize)
    layer.alpha_composite(c, (int(sx - c.size[0] / 2), int(sy - c.size[1] / 2)))


@functools.lru_cache(None)
def _knit():
    """Burak's camel knit sweater filling the frame."""
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    k = (np.sin(x * 2 * math.pi / 26 + 2.0 * np.sin(y / 60)) > 0).astype(np.float32)
    base = np.array((154, 110, 66), np.float32); dark = np.array((138, 98, 58), np.float32)
    col = base * (1 - k[..., None]) + dark * k[..., None]
    shade = 1.0 - 0.25 * (((x - 720) / 900) ** 2 + ((y - 1300) / 1400) ** 2)
    col *= shade[..., None]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")


@functools.lru_cache(maxsize=64)
def chest_plate(counter, heart_q=0):
    img = _knit().copy()
    top = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    if heart_q:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        a = int(120 * heart_q / 20)
        ImageDraw.Draw(g).ellipse([480, 520, 920, 960], fill=(255, 90, 80, a))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(80)))
    _tape(top, (1000, 1380), (700, 760), 1.0, counter, 460)
    ins.shadowed(img, top, blur=16, off=(12, 20), alpha=150)
    return img


def km_counter(k):
    return f"{int(round(480 * k))} km"


if __name__ == "__main__":
    ims = [tickets_plate(3), tickets_plate(5, (10, 15, 24)), tickets_plate(5, (10, 15, 24), 1.0, "480 km"),
           chest_plate("480 km"), chest_plate("0 cm", 20)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((270, 480)), (i * 270, 0))
    sheet.save(sys.argv[1])


def tape_to_point(frame, start, end, reach, counter, glow):
    """Draw the tape measure on a finished frame: blade from the casing (start) to the heart (end)."""
    W_, H_ = frame.size
    s = W_ / 1440
    if glow > 0:
        g = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        r = 150 * s
        ImageDraw.Draw(g).ellipse([end[0] - r, end[1] - r, end[0] + r, end[1] + r], fill=(255, 70, 60, int(170 * glow)))
        frame.alpha_composite(g.filter(ImageFilter.GaussianBlur(60 * s)))
        # small heart drawn right where the tape touches
        hh = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        pts = []
        for i in range(60):
            t = 2 * math.pi * i / 60
            pts.append((end[0] + 3.2 * s * 16 * math.sin(t) ** 3,
                        end[1] - 3.2 * s * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))))
        ImageDraw.Draw(hh).polygon(pts, fill=(226, 40, 46, int(230 * glow)))
        frame.alpha_composite(hh)
    layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    _tape(layer, start, end, max(0.02, reach), counter, int(420 * s))
    ins.shadowed(frame, layer, blur=int(10 * s), off=(int(8 * s), int(12 * s)), alpha=140)
    return frame
