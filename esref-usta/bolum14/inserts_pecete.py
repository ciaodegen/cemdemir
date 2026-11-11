"""Bölüm 14 (Borç) detay çekimleri: arkadaşın peçeteye yazdığı borç notu, büyüteç altında parlayan "SÖZ!"."""
import sys, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_HAND
import inserts as ins
import inserts_m1 as im

BW, BH = 1440, 2560
NW = 940                                  # napkin size
CX, CY = 720, 1300                        # napkin centre on the plate
ROT = -4
INK = (30, 48, 136, 255)
LINES = [("Kanka,", 92, 150), ("5.000 TL aldım.", 92, 290), ("Ay sonu veririm.", 92, 430)]
SOZ = ("SÖZ!", 170, 560)
SIGN = ("— Kerem   12.03", 70, 790)


@functools.lru_cache(None)
def _napkin():
    n = im.paper(NW, NW, seed=14, lined=False, tint=(252, 251, 246))
    d = ImageDraw.Draw(n)
    # embossed border pattern
    for k in range(0, NW - 120, 22):
        for x, y in ((60 + k, 50), (60 + k, NW - 50), (50, 60 + k), (NW - 50, 60 + k)):
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(232, 230, 222, 255))
    d.rectangle([34, 34, NW - 34, NW - 34], outline=(236, 234, 226, 255), width=3)
    # fold creases
    d.line([(NW // 2, 0), (NW // 2, NW)], fill=(236, 233, 224, 255), width=4)
    d.line([(0, NW // 2), (NW, NW // 2)], fill=(238, 235, 226, 255), width=4)
    d.line([(NW // 2 + 4, 0), (NW // 2 + 4, NW)], fill=(255, 255, 252, 255), width=2)
    return n


def _text_x(d, s, f):
    return (NW - d.textlength(s, font=f)) / 2


def napkin(glow=0.0):
    n = _napkin().copy()
    d = ImageDraw.Draw(n)
    for s, size, y in LINES:
        f = font(FONT_HAND, size)
        d.text((_text_x(d, s, f), y), s, font=f, fill=INK)
    s, size, y = SOZ
    f = font(FONT_HAND, size)
    x0 = _text_x(d, s, f); tw = d.textlength(s, font=f)
    if glow > 0:
        g = Image.new("RGBA", n.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([x0 - 90, y - 30, x0 + tw + 90, y + size + 50], fill=(255, 214, 90, int(200 * glow)))
        n.alpha_composite(g.filter(ImageFilter.GaussianBlur(50)))
    for dx in (0, 2, 4):     # pressed hard: thick strokes
        d.text((x0 + dx, y), s, font=f, fill=INK)
    for k in (0, 1):
        d.line([(x0 - 10, y + size + 18 + k * 22), (x0 + tw + 14, y + size + 10 + k * 22)], fill=INK, width=7)
    if glow > 0:   # warm gold tint on the word itself
        m = Image.new("L", n.size, 0)
        md = ImageDraw.Draw(m)
        for dx in (0, 2, 4):
            md.text((x0 + dx, y), s, font=f, fill=int(255 * glow))
        n.paste(Image.new("RGBA", n.size, (214, 150, 30, 255)), (0, 0), m)
    s, size, y = SIGN
    f = font(FONT_HAND, size)
    d.text((NW - 90 - d.textlength(s, font=f), y), s, font=f, fill=INK)
    return n


@functools.lru_cache(maxsize=64)
def napkin_plate(glow_q=0):
    img = ins.wood_top(171).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    n = napkin(glow_q / 20).rotate(ROT, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(n, (CX - n.size[0] // 2, CY - n.size[1] // 2))
    ins.shadowed(img, obj, blur=20, off=(12, 20), alpha=120)
    return img


def napkin_point(x, y):
    """Plate coordinates of a napkin-local point (rotation ignored)."""
    return CX - NW / 2 + x, CY - NW / 2 + y


if __name__ == "__main__":
    ims = [napkin_plate(), napkin_plate(20)]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
