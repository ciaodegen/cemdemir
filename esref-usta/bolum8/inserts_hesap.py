"""Bölüm 8 (Hesabı Kim Öder) detay çekimleri: lokanta fişi, makas, kendiliğinden birleşme, fişin arkası."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_BOLD, FONT_HAND
import inserts as ins
import inserts_m1 as im

BW, BH = 1440, 2560
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
RW, RH = 760, 1560
INK_BACK = (34, 52, 140, 255)
BACK = ["Sınav gecen sabaha kadar", "seninle uyanık kaldı.", "",
        "Annen hastayken her gün", "yemek götürdü.", "",
        "Kötü gününde 3 saat dinledi,", "bir kere saate bakmadı."]
BACK_SEG = [(0, 1), (3, 4), (6, 7)]          # which lines belong to which spoken sentence


def _torn(p, top=True, bottom=True):
    d = ImageDraw.Draw(p)
    w, h = p.size
    for x in range(0, w, 22):
        if top:
            d.polygon([(x, 0), (x + 11, 12), (x + 22, 0)], fill=(0, 0, 0, 0))
        if bottom:
            d.polygon([(x, h), (x + 11, h - 12), (x + 22, h)], fill=(0, 0, 0, 0))
    return p


@functools.lru_cache(None)
def receipt_front():
    p = im.paper(RW, RH, seed=81, lined=False, tint=(250, 249, 244))
    d = ImageDraw.Draw(p)
    fb, f, fs = font(MONO_B, 58), font(MONO, 40), font(MONO, 32)
    def c(y, t, fnt, col=(30, 30, 34, 255)):
        d.text(((RW - d.textlength(t, font=fnt)) / 2, y), t, font=fnt, fill=col)
    c(70, "KÖŞE LOKANTA", fb)
    c(150, "Masa: 4   Kişi: 2", fs, (90, 90, 96, 255))
    c(195, "14.11  20:47", fs, (90, 90, 96, 255))
    def dash(y):
        for x in range(40, RW - 40, 24):
            d.line([(x, y), (x + 12, y)], fill=(120, 120, 126, 255), width=3)
    dash(260)
    y = 300
    for item, price in (("Mantı x2", "780,00"), ("Çay x2", "70,00"), ("Künefe x1", "350,00"),
                        ("Ayran x2", "120,00"), ("Salata x1", "530,00")):
        d.text((50, y), item, font=f, fill=(30, 30, 34, 255))
        d.text((RW - 50 - d.textlength(price, font=f), y), price, font=f, fill=(30, 30, 34, 255))
        y += 70
    dash(y + 20)
    y += 60
    d.text((50, y), "TOPLAM", font=fb, fill=(20, 20, 24, 255))
    t = "1.850 TL"
    d.text((RW - 50 - d.textlength(t, font=fb), y), t, font=fb, fill=(20, 20, 24, 255))
    dash(y + 110)
    c(y + 150, "Teşekkür ederiz", fs, (90, 90, 96, 255))
    c(y + 200, "Yine bekleriz :)", fs, (90, 90, 96, 255))
    return _torn(p)


def receipt_back(reveal, total=False):
    """reveal: tuple of chars shown per BACK line."""
    p = im.paper(RW, RH, seed=82, lined=False, tint=(248, 247, 241))
    d = ImageDraw.Draw(p)
    # faint mirror of the printing showing through
    ghost = receipt_front().transpose(Image.FLIP_LEFT_RIGHT)
    g = Image.eval(ghost.convert("L"), lambda v: 255 - (255 - v) // 9).convert("RGBA")
    g.putalpha(ghost.split()[3])
    p = Image.alpha_composite(p, g)
    d = ImageDraw.Draw(p)
    fh = font(FONT_HAND, 54)
    y = 140
    for i, line in enumerate(BACK):
        n = reveal[i] if i < len(reveal) else 0
        if line and n > 0:
            d.text((50, y), line[:n], font=fh, fill=INK_BACK)
        y += 78 if line else 50
    if total:
        y += 50
        for x in range(40, RW - 40, 24):
            d.line([(x, y), (x + 12, y)], fill=(120, 120, 126, 255), width=3)
        d.text((50, y + 30), "TOPLAM:", font=font(MONO_B, 50), fill=(20, 20, 24, 255))
        d.text((50, y + 100), "Hesaplanamadı.", font=font(FONT_HAND, 76), fill=(178, 30, 34, 255))
    return _torn(p)


def scissors(open_k):
    """Simple scissors pointing up; open_k 0 closed .. 1 open."""
    im_ = Image.new("RGBA", (420, 900), (0, 0, 0, 0))
    for sgn in (-1, 1):
        blade = Image.new("RGBA", (420, 900), (0, 0, 0, 0))
        d = ImageDraw.Draw(blade)
        d.polygon([(210, 40), (226, 470), (194, 470)], fill=(196, 200, 208, 255))
        d.line([(210, 50), (210, 460)], fill=(150, 154, 162, 255), width=4)
        d.ellipse([210 - 22 + sgn * 70, 560, 210 + 22 + sgn * 70 + 0, 840], fill=(30, 30, 34, 255))
        d.ellipse([210 - 8 + sgn * 70, 600, 210 + 8 + sgn * 70, 800], fill=(0, 0, 0, 0))
        d.polygon([(196, 470), (224, 470), (210 + sgn * 70, 600)], fill=(30, 30, 34, 255))
        blade = blade.rotate(sgn * 9 * open_k, center=(210, 500), resample=Image.BICUBIC)
        im_.alpha_composite(blade)
    ImageDraw.Draw(im_).ellipse([196, 486, 224, 514], fill=(120, 120, 128, 255))
    return im_


@functools.lru_cache(maxsize=128)
def bill_plate(drop_q=20, cut_q=0, gap_q=0, glow_q=0, sc_q=0, sc_open_q=0):
    """Front side on the counter.
    drop_q: 0..20 slap-in; cut_q: 0..20 how far the cut line runs; gap_q: 0..20 halves apart;
    glow_q: rejoin shimmer; sc_q: 0 none, 1..20 scissors y-progress; sc_open_q blade opening."""
    img = ins.wood_top(91).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    r = receipt_front()
    k = drop_q / 20
    scale = 1.0 + 0.12 * (1 - k)
    rr = r.resize((int(RW * scale), int(RH * scale)), Image.LANCZOS).rotate(-3 + 6 * (1 - k), expand=True, resample=Image.BICUBIC)
    cx, cy = BW // 2, 1240
    gap = gap_q / 20 * 90
    if cut_q > 0 and gap > 0:
        w = rr.size[0]
        left = rr.crop((0, 0, w // 2, rr.size[1])); right = rr.crop((w // 2, 0, w, rr.size[1]))
        obj.alpha_composite(left.rotate(2 * gap_q / 20, expand=False, resample=Image.BICUBIC), (int(cx - w / 2 - gap / 2), int(cy - rr.size[1] / 2)))
        obj.alpha_composite(right.rotate(-2 * gap_q / 20, expand=False, resample=Image.BICUBIC), (int(cx + gap / 2), int(cy - rr.size[1] / 2)))
    else:
        obj.alpha_composite(rr, (int(cx - rr.size[0] / 2), int(cy - rr.size[1] / 2)))
        if cut_q > 0:
            d = ImageDraw.Draw(obj)
            y0 = cy + rr.size[1] / 2; y1 = y0 - rr.size[1] * cut_q / 20
            d.line([(cx, y0), (cx, y1)], fill=(60, 60, 64, 200), width=4)
    ins.shadowed(img, obj, blur=26, off=(16, 28), alpha=150 if k >= 1 else int(150 * k))
    if glow_q:
        g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        a = int(150 * glow_q / 20)
        gd.rectangle([cx - 30, cy - RH / 2, cx + 30, cy + RH / 2], fill=(255, 226, 150, a))
        rng = np.random.default_rng(glow_q)
        for _ in range(26):
            sx = cx + rng.uniform(-60, 60); sy = cy + rng.uniform(-RH / 2, RH / 2); rs = rng.uniform(4, 14)
            gd.ellipse([sx - rs, sy - rs, sx + rs, sy + rs], fill=(255, 240, 190, a))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(22)))
    if sc_q:
        s = scissors(sc_open_q / 20)
        y = cy + RH / 2 + 120 - (RH + 160) * sc_q / 20
        img.alpha_composite(s, (int(cx - 210), int(y - 40)))
    return img


@functools.lru_cache(maxsize=128)
def back_plate(flip_q=20, reveal=(), total=False):
    """flip_q 0..20: 0..10 front squashes away, 10..20 back grows in."""
    img = ins.wood_top(91).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    k = flip_q / 20
    side = receipt_front().rotate(-3, expand=True, resample=Image.BICUBIC) if k < 0.5 else receipt_back(reveal, total).rotate(-3, expand=True, resample=Image.BICUBIC)
    sx = abs(1 - 2 * k) if k < 1 else 1.0
    if sx < 0.02:
        sx = 0.02
    w = max(2, int(side.size[0] * sx))
    side = side.resize((w, side.size[1]), Image.LANCZOS)
    cx, cy = BW // 2, 1240
    obj.alpha_composite(side, (int(cx - w / 2), int(cy - side.size[1] / 2)))
    ins.shadowed(img, obj, blur=26, off=(16, 28), alpha=150)
    return img


if __name__ == "__main__":
    full = tuple(len(l) for l in BACK)
    ims = [bill_plate(20), bill_plate(20, 20, 0, 0, 14, 10), bill_plate(20, 20, 20), bill_plate(20, 20, 6, 16),
           back_plate(14, (), False), back_plate(20, full, True)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((270, 480)), (i * 270, 0))
    sheet.save(sys.argv[1])
