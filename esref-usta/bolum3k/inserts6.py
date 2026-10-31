"""Bölüm 3 (Susan Kedi) detay çekimleri: tüylerin içindeki tasma künyesi, Deniz'in araması."""
import sys, math, random, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B
import inserts as ins

BW, BH = 1440, 2560


@functools.lru_cache(None)
def fur_plate():
    rnd = random.Random(7)
    img = Image.new("RGBA", (BW, BH), (226, 222, 214, 255))
    d = ImageDraw.Draw(img)
    for _ in range(9000):
        x = rnd.uniform(-50, BW + 50); y = rnd.uniform(-50, BH + 50)
        ln = rnd.uniform(40, 120); a = math.radians(rnd.uniform(70, 110))
        c = int(rnd.uniform(205, 252))
        d.line([(x, y), (x + math.cos(a) * ln * 0.3, y + math.sin(a) * ln)], fill=(c, c - 3, c - 8, 255), width=rnd.choice((2, 3, 4)))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    # collar band crossing the frame, half buried in fur
    band = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    bd.polygon([(-100, 1060), (1540, 1180), (1540, 1340), (-100, 1220)], fill=(92, 124, 150, 255))
    for k in range(0, 1640, 40):
        bd.line([(k - 100, 1062 + k * 0.073), (k - 100, 1218 + k * 0.073)], fill=(80, 108, 132, 255), width=3)
    img.alpha_composite(band)
    # fur strands falling over the collar
    over = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); od = ImageDraw.Draw(over)
    for _ in range(1400):
        x = rnd.uniform(-50, BW + 50); y = rnd.uniform(950, 1180)
        ln = rnd.uniform(60, 160); c = int(rnd.uniform(215, 252))
        od.line([(x, y), (x + rnd.uniform(-15, 15), y + ln)], fill=(c, c - 3, c - 8, 230), width=rnd.choice((2, 3)))
    img.alpha_composite(over.filter(ImageFilter.GaussianBlur(1.0)))
    # metal tag hanging from the collar
    tag = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
    cx, cy, r = 720, 1500, 230
    td.line([(cx, 1250), (cx, cy - r)], fill=(150, 150, 156, 255), width=14)
    td.ellipse([cx - 40, 1215, cx + 40, 1295], outline=(160, 160, 166, 255), width=14)
    td.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(178, 180, 186, 255))
    td.ellipse([cx - r + 18, cy - r + 18, cx + r - 18, cy + r - 18], outline=(140, 142, 148, 255), width=6)
    f1 = font(FONT_SERIF_B, 84); f2 = font(FONT_SERIF_B, 46)
    for t, f_, y in (("PAMUK", f1, cy - 90), ("0532 418 27 63", f2, cy + 30)):
        tw = td.textlength(t, font=f_); td.text((cx - tw / 2, y), t, font=f_, fill=(88, 90, 96, 255))
    sc = [(cx - r * 0.5, cy - r * 0.6), (cx + r * 0.1, cy - r * 0.75)]
    td.line(sc, fill=(230, 232, 236, 200), width=10)
    sh = Image.new("RGBA", (BW, BH), (0, 0, 0, 0)); sh.putalpha(tag.split()[3].point(lambda v: v * 110 // 255))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)), (14, 24))
    img.alpha_composite(tag)
    return img


@functools.lru_cache(None)
def loupe_tag():
    src = fur_plate()
    m = Image.new("L", (BW, BH), 0)
    ImageDraw.Draw(m).ellipse([BW / 2 - 640, 1280 - 640, BW / 2 + 640, 1280 + 640], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(26))
    out = Image.new("RGBA", (BW, BH), (8, 5, 3, 255)); out.paste(src, (0, 0), m)
    ring = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([BW / 2 - 650, 1280 - 650, BW / 2 + 650, 1280 + 650], outline=(20, 16, 12, 255), width=60)
    out.alpha_composite(ring.filter(ImageFilter.GaussianBlur(14)))
    return out


@functools.lru_cache(None)
def deniz_dials():
    return ins.phone(True, "0532 418 27 63", "Pamuk", "aranıyor…", True)


if __name__ == "__main__":
    ims = [loupe_tag(), deniz_dials()]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
