"""Bölüm 13 (Severek Ayrılınır mı?) detay çekimleri: kurdeleyle bağlı iki cep saati, ayrışan zamanlar, kapak içindeki yazılar."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_HAND
import inserts as ins

BW, BH = 1440, 2560
R = 230
WATCH = {"A": (420, 1560), "B": (1020, 1560)}          # A = hers (gold), B = his (silver)
METAL = {"A": ((214, 168, 70), (246, 214, 130), (150, 110, 40)),
         "B": ((176, 180, 188), (226, 230, 236), (120, 124, 132))}
LID_DY = 520
LINES = {"A": [("Berlin'de iş", "teklifi aldım."), ("Hemen evlenmek", "istiyorum.")],
         "B": [("Annem hasta,", "onu bırakamam."), ("Önce kendimi", "bulmalıyım.")]}


def _disc(d, cx, cy, r, w):
    base, light, dark = METAL[w]
    d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], fill=dark + (255,))
    d.ellipse([cx - r - 12, cy - r - 12, cx + r + 8, cy + r + 8], fill=base + (255,))
    d.ellipse([cx - r - 8, cy - r - 10, cx + r - 30, cy + r - 40], fill=light + (90,))


def _face(d, cx, cy, mins, w):
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(246, 240, 226, 255))
    for i in range(60):
        a = math.radians(i * 6)
        r0 = R - (34 if i % 5 == 0 else 16)
        d.line([(cx + r0 * math.sin(a), cy - r0 * math.cos(a)), (cx + (R - 8) * math.sin(a), cy - (R - 8) * math.cos(a))],
               fill=(50, 40, 32, 255), width=8 if i % 5 == 0 else 3)
    f = font(FONT_SERIF_B, 46)
    for n in (12, 3, 6, 9):
        a = math.radians(n * 30); r0 = R - 74
        t = str(n); tw = d.textlength(t, font=f)
        d.text((cx + r0 * math.sin(a) - tw / 2, cy - r0 * math.cos(a) - 28), t, font=f, fill=(50, 40, 32, 255))
    hd = (mins / 60 % 12) * 30; md = (mins % 60) * 6
    for ang, ln, wd in ((hd, R * 0.5, 14), (md, R * 0.78, 9)):
        a = math.radians(ang)
        d.line([(cx, cy), (cx + ln * math.sin(a), cy - ln * math.cos(a))], fill=(30, 26, 22, 255), width=wd)
    d.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=METAL[w][2] + (255,))


def _lid(d, cx, cy, w, lines_shown, chars_last):
    base, light, dark = METAL[w]
    ly = cy - LID_DY
    d.ellipse([cx - R - 18, ly - R - 18, cx + R + 18, ly + R + 18], fill=dark + (255,))
    d.ellipse([cx - R - 6, ly - R - 6, cx + R + 6, ly + R + 6], fill=base + (255,))
    d.ellipse([cx - R + 22, ly - R + 22, cx + R - 22, ly + R - 22], fill=tuple(int(c * 0.92) for c in base) + (255,))
    d.rectangle([cx - 30, ly + R + 4, cx + 30, cy - R - 4], fill=dark + (255,))   # hinge
    f = font(FONT_HAND, 54)
    y = ly - 120
    for i, (l1, l2) in enumerate(LINES[w][:lines_shown]):
        n = len(l1) + len(l2) if i < lines_shown - 1 else chars_last
        for line in (l1, l2):
            if n <= 0:
                break
            s = line[:n]; n -= len(line)
            tw = d.textlength(line, font=f)
            d.text((cx - tw / 2 + 2, y + 2), s, font=f, fill=light + (200,))
            d.text((cx - tw / 2, y), s, font=f, fill=(70, 46, 16, 255) if w == "A" else (54, 56, 64, 255))
            y += 60
        y += 14


@functools.lru_cache(maxsize=256)
def watches_plate(minA, minB, ribbon=1.0, shownA=0, charsA=0, shownB=0, charsB=0, apart_q=0):
    """minA/minB: displayed minutes (int, tenths ok via rounding); ribbon 1 tied, 0 untied;
    shown*/chars*: lid writing; apart_q 0..20 slides the watches apart after the ribbon is untied."""
    img = ins.wood_top(151).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    off = apart_q / 20 * 90
    pos = {"A": (WATCH["A"][0] - off, WATCH["A"][1]), "B": (WATCH["B"][0] + off, WATCH["B"][1])}
    # chains from each crown toward the middle
    mid = (720, 1880)
    for w, s in (("A", 1), ("B", -1)):
        cx, cy = pos[w]
        crown = (cx + s * (R + 30), cy + 40)
        d.ellipse([crown[0] - 22, crown[1] - 22, crown[0] + 22, crown[1] + 22], fill=METAL[w][2] + (255,))
        end = mid if ribbon > 0.5 else (crown[0] + s * 120, crown[1] + 260)
        n = 16
        for k in range(n):
            t = k / n
            px = crown[0] + (end[0] - crown[0]) * t; py = crown[1] + (end[1] - crown[1]) * t + 90 * math.sin(math.pi * t)
            d.ellipse([px - 11, py - 7, px + 11, py + 7], outline=METAL[w][1] + (255,), width=5)
    for w in ("A", "B"):
        cx, cy = pos[w]
        _disc(d, cx, cy, R, w)
        _face(d, cx, cy, (minA if w == "A" else minB) / 10, w)
        _lid(d, cx, cy, w, shownA if w == "A" else shownB, charsA if w == "A" else charsB)
    # red ribbon bow tying the chains
    if ribbon > 0:
        r = (196, 30, 40, int(255 * ribbon))
        if ribbon > 0.5:
            d.polygon([mid, (mid[0] - 110, mid[1] - 60), (mid[0] - 110, mid[1] + 60)], fill=r)
            d.polygon([mid, (mid[0] + 110, mid[1] - 60), (mid[0] + 110, mid[1] + 60)], fill=r)
            d.polygon([mid, (mid[0] - 50, mid[1] + 200), (mid[0] - 10, mid[1] + 210)], fill=r)
            d.polygon([mid, (mid[0] + 60, mid[1] + 190), (mid[0] + 20, mid[1] + 210)], fill=r)
            d.ellipse([mid[0] - 30, mid[1] - 30, mid[0] + 30, mid[1] + 30], fill=(170, 20, 30, 255))
        else:   # loose ribbon lying on the wood
            pts = [(mid[0] - 260 + i * 26, mid[1] + 140 + 30 * math.sin(i / 2.2)) for i in range(21)]
            d.line(pts, fill=(196, 30, 40, 255), width=30, joint="curve")
    ins.shadowed(img, obj, blur=26, off=(16, 28), alpha=150)
    return img


if __name__ == "__main__":
    ims = [watches_plate(6100, 6100), watches_plate(6100, 5200, 1, 1, 30, 1, 30),
           watches_plate(6150, 4900, 1, 2, 40, 2, 40), watches_plate(6150, 4900, 0, 2, 40, 2, 40, 20)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((270, 480)), (i * 270, 0))
    sheet.save(sys.argv[1])
