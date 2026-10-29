"""Bölüm 2 (Ağır Çanta) detay çekimleri: deri çanta ve içinden çıkanlar."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_HAND, FONT_BOLD
import inserts as ins

BW, BH = 1440, 2560
LEATHER = (96, 52, 26, 255)
LEATHER_D = (66, 34, 16, 255)
BRASS = (196, 156, 78, 255)


@functools.lru_cache(None)
def briefcase(opened=False):
    img = ins.wood_top(17).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    cx, cy = 720, 1420
    if opened:
        d.rounded_rectangle([cx - 520, cy - 820, cx + 520, cy - 170], radius=50, fill=LEATHER_D)
        d.rounded_rectangle([cx - 480, cy - 780, cx + 480, cy - 210], radius=36, fill=(120, 70, 36, 255))
        d.rectangle([cx - 520, cy - 190, cx + 520, cy - 160], fill=(50, 26, 12, 255))
    d.rounded_rectangle([cx - 540, cy - 170, cx + 540, cy + 420], radius=56, fill=LEATHER)
    for k in range(6):  # stitching
        d.line([(cx - 500, cy - 130 + k * 0), (cx + 500, cy - 130)], fill=(140, 90, 50, 255), width=4)
    d.rounded_rectangle([cx - 500, cy - 130, cx + 500, cy + 380], radius=40, outline=(130, 82, 44, 255), width=5)
    if opened:
        d.rounded_rectangle([cx - 470, cy - 140, cx + 470, cy + 260], radius=24, fill=(40, 20, 10, 255))
        # papers peeking out
        d.polygon([(cx - 380, cy - 60), (cx + 120, cy - 110), (cx + 150, cy + 120), (cx - 350, cy + 170)], fill=(232, 226, 210, 255))
        d.rectangle([cx + 160, cy - 80, cx + 400, cy + 140], fill=(176, 36, 40, 255))
        d.rectangle([cx + 265, cy - 80, cx + 295, cy + 140], fill=(232, 196, 90, 255))
    else:
        # handle and clasps
        d.rounded_rectangle([cx - 170, cy - 300, cx + 170, cy - 150], radius=60, outline=LEATHER_D, width=46)
        for sx in (-1, 1):
            d.rounded_rectangle([cx + sx * 330 - 50, cy - 190, cx + sx * 330 + 50, cy - 90], radius=12, fill=BRASS)
    ins.shadowed(img, obj, blur=34, off=(24, 38), alpha=175)
    return img


def _paper(obj, box, rot, draw_fn):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    p = Image.new("RGBA", (w, h), (238, 232, 216, 255))
    draw_fn(ImageDraw.Draw(p), w, h)
    p = p.rotate(rot, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(p, (int((x0 + x1) / 2 - p.size[0] / 2), int((y0 + y1) / 2 - p.size[1] / 2)))


def _hand(d, xy, text, size=64, color=(40, 44, 92, 255)):
    d.text(xy, text, font=font(FONT_HAND, size), fill=color)


@functools.lru_cache(None)
def receipt():
    img = ins.wood_top(19).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    def draw(d, w, h):
        d.text((60, 60), "OKUL TAKSİT MAKBUZU", font=font(FONT_SERIF_B, 64), fill=(50, 40, 34, 255))
        d.line([(60, 150), (w - 60, 150)], fill=(120, 100, 80, 255), width=3)
        lab = font(FONT_SERIF_B, 46)
        for i, (k, v) in enumerate((("Öğrenci:", "Efe"), ("Sınıf:", "4-B"), ("Taksit:", "3 / 9"), ("Durum:", "Ödendi"))):
            y = 210 + i * 120
            d.text((60, y), k, font=lab, fill=(90, 74, 60, 255))
            _hand(d, (330, y - 14), v, 72)
            d.line([(320, y + 70), (w - 60, y + 70)], fill=(200, 186, 160, 255), width=2)
        d.ellipse([w - 330, h - 300, w - 80, h - 50], outline=(60, 90, 160, 200), width=10)
        f = font(FONT_SERIF_B, 40); t = "ÖDENDİ"; tw = d.textlength(t, font=f)
        d.text((w - 205 - tw / 2, h - 200), t, font=f, fill=(60, 90, 160, 220))
    _paper(obj, (250, 760, 1190, 1820), -4, draw)
    ins.shadowed(img, obj, blur=26, off=(18, 28), alpha=150)
    return img


@functools.lru_cache(None)
def gift():
    img = ins.wood_top(23).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(obj)
    cx, cy = 720, 1300
    d.rounded_rectangle([cx - 380, cy - 300, cx + 380, cy + 300], radius=20, fill=(176, 36, 40, 255))
    for k in range(-360, 380, 90):  # paper pattern
        d.ellipse([cx + k - 14, cy - 220 - 14, cx + k + 14, cy - 220 + 14], fill=(200, 70, 70, 255))
        d.ellipse([cx + k + 30, cy + 200 - 14, cx + k + 58, cy + 200 + 14], fill=(200, 70, 70, 255))
    d.rectangle([cx - 40, cy - 300, cx + 40, cy + 300], fill=(232, 196, 90, 255))
    d.rectangle([cx - 380, cy - 40, cx + 380, cy + 40], fill=(232, 196, 90, 255))
    d.ellipse([cx - 170, cy - 110, cx - 10, cy + 10], outline=(232, 196, 90, 255), width=34)
    d.ellipse([cx + 10, cy - 110, cx + 170, cy + 10], outline=(232, 196, 90, 255), width=34)
    # tag
    tag = Image.new("RGBA", (620, 300), (0, 0, 0, 0)); td = ImageDraw.Draw(tag)
    td.polygon([(60, 0), (620, 0), (620, 300), (60, 300), (0, 150)], fill=(240, 228, 196, 255))
    td.ellipse([36, 128, 80, 172], fill=(120, 90, 60, 255))
    _hand(td, (110, 50), "Efe'ye", 96)
    _hand(td, (110, 170), "10. yaşın kutlu olsun", 50, (120, 50, 50, 255))
    tag = tag.rotate(-10, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(tag, (cx - 120, cy + 300))
    d.line([(cx - 60, cy + 330), (cx, cy + 40)], fill=(232, 196, 90, 255), width=8)
    ins.shadowed(img, obj, blur=30, off=(20, 32), alpha=165)
    return img


@functools.lru_cache(None)
def rent():
    img = ins.wood_top(29).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    def draw(d, w, h):
        d.rectangle([0, 0, w, 120], fill=(70, 90, 120, 255))
        d.text((50, 26), "KİRA ÖDEME BİLDİRİMİ", font=font(FONT_SERIF_B, 58), fill=(240, 240, 240, 255))
        lab = font(FONT_SERIF_B, 46)
        for i, (k, v) in enumerate((("Dönem:", "Ekim"), ("Daire:", "No 7"), ("Son ödeme:", "Bu hafta"))):
            y = 200 + i * 120
            d.text((50, y), k, font=lab, fill=(80, 70, 60, 255))
            d.text((380, y), v, font=lab, fill=(40, 34, 30, 255))
            d.line([(370, y + 66), (w - 50, y + 66)], fill=(200, 186, 160, 255), width=2)
    _paper(obj, (220, 860, 1220, 1700), 5, draw)
    ins.shadowed(img, obj, blur=26, off=(18, 28), alpha=150)
    return img


if __name__ == "__main__":
    ims = [briefcase(False), briefcase(True), receipt(), gift(), rent()]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
