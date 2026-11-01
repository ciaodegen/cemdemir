"""Mektup 1 (KPSS) detay çekimleri: kısalmış kurşun kalem, sınav belgeleri, kalemtıraş."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
sys.path.insert(0, "/home/user/cemdemir/esref-usta/mektup1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B, FONT_BOLD, FONT_HAND
import inserts as ins
import inserts_m1 as im

BW, BH = 1440, 2560
YEL = (236, 186, 40, 255)


@functools.lru_cache(maxsize=32)
def pencil(length=420, sharp=0.0, scale=1.0):
    """Horizontal stub pencil, tip on the left. sharp 0 = blunt worn tip, 1 = fresh point."""
    s = scale
    L, Wd = int(length * s), int(64 * s)
    cone = int((70 + 40 * sharp) * s)
    im_ = Image.new("RGBA", (L + 20, Wd + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(im_)
    y0, y1, cy = 10, 10 + Wd, 10 + Wd / 2
    x_tip = 10
    x_body = x_tip + cone
    eras = int(70 * s); fer = int(46 * s)
    x_fer = 10 + L - eras - fer
    # wood cone
    tipw = (1 - sharp) * 16 * s + 2
    d.polygon([(x_tip + 6 * s, cy - tipw), (x_body, y0 + 4 * s), (x_body, y1 - 4 * s), (x_tip + 6 * s, cy + tipw)], fill=(226, 190, 146, 255))
    # graphite
    gl = int((20 + 26 * sharp) * s)
    d.polygon([(x_tip, cy - (1 - sharp) * 10 * s - 1), (x_tip + gl, cy - (tipw + 7 * s)), (x_tip + gl, cy + tipw + 7 * s), (x_tip, cy + (1 - sharp) * 10 * s + 1)], fill=(64, 64, 70, 255))
    if sharp < 0.5:
        d.ellipse([x_tip - 4 * s, cy - 10 * s, x_tip + 14 * s, cy + 10 * s], fill=(64, 64, 70, 255))
    # painted hex body
    d.rectangle([x_body, y0, x_fer, y1], fill=YEL)
    d.rectangle([x_body, y0 + Wd * 0.3, x_fer, y0 + Wd * 0.42], fill=(252, 218, 100, 255))
    d.rectangle([x_body, y0 + Wd * 0.72, x_fer, y1], fill=(206, 152, 22, 255))
    # scalloped paint edge at the cone
    for k in range(4):
        yy = y0 + Wd * (k + 0.5) / 4
        d.ellipse([x_body - 8 * s, yy - Wd / 8, x_body + 8 * s, yy + Wd / 8], fill=YEL)
    # ferrule + eraser
    d.rectangle([x_fer, y0 - 2, x_fer + fer, y1 + 2], fill=(186, 188, 194, 255))
    for k in range(3):
        xx = x_fer + fer * (k + 1) / 4
        d.line([(xx, y0 - 2), (xx, y1 + 2)], fill=(140, 142, 150, 255), width=max(2, int(3 * s)))
    d.rounded_rectangle([x_fer + fer, y0, x_fer + fer + eras, y1], radius=int(14 * s), fill=(232, 140, 150, 255))
    # tiny print on the body
    d.text((x_body + 30 * s, y0 + 16 * s), "2B", font=font(FONT_BOLD, int(26 * s)), fill=(40, 30, 10, 255))
    # bite marks / wear near the eraser end
    for k in range(3):
        xx = x_fer - (20 + k * 16) * s
        d.line([(xx, y0 + 4), (xx + 6 * s, y0 + 14 * s)], fill=(196, 140, 20, 255), width=max(2, int(3 * s)))
    return im_


def _place(obj, img, cx, cy, angle):
    r = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    obj.alpha_composite(r, (int(cx - r.size[0] / 2), int(cy - r.size[1] / 2)))


@functools.lru_cache(maxsize=64)
def envelope_plate(kq=20, pq=20):
    """Envelope slides in; pencil stub rolls out of it (pq 0..20)."""
    img = im.envelope_plate(kq, "4 yıldır atanamamak.").copy()
    if kq < 20 or pq <= 0:
        return img
    k = pq / 20
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    x = 560 + 300 * k; y = 1560 + 200 * k
    _place(obj, pencil(300, 0.0, 1.5), x, y, -20 + 380 * (1 - k) if k < 1 else -20)
    ins.shadowed(img, obj, blur=12, off=(10, 16), alpha=150)
    return img


def slip(year):
    w, h = 820, 520
    p = im.paper(w, h, seed=year, lined=False, tint=(250, 250, 246))
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 86], fill=(56, 72, 104, 255))
    d.text((30, 22), "KPSS SONUÇ BELGESİ", font=font(FONT_BOLD, 40), fill=(240, 240, 245, 255))
    d.text((30, 120), "Sınav yılı:", font=font(FONT_SERIF_B, 36), fill=(80, 80, 90, 255))
    d.text((30, 160), str(year), font=font(FONT_SERIF_B, 120), fill=(30, 30, 40, 255))
    d.text((30, 320), "Puan: ......   Durum:", font=font(FONT_SERIF_B, 34), fill=(80, 80, 90, 255))
    st = Image.new("RGBA", (420, 120), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([5, 5, 415, 115], radius=12, outline=(176, 36, 36, 230), width=7)
    f = font(FONT_SERIF_B, 58); t = "ATANAMADI"
    sd.text(((420 - sd.textlength(t, font=f)) / 2, 26), t, font=f, fill=(176, 36, 36, 230))
    a = np.array(st); rng = np.random.default_rng(year)
    a[..., 3] = (a[..., 3] * (rng.random(a.shape[:2]) > 0.2)).astype(np.uint8)
    st = Image.fromarray(a).rotate(8, expand=True, resample=Image.BICUBIC)
    p.alpha_composite(st, (w - st.size[0] - 20, h - st.size[1] - 20))
    return p


@functools.lru_cache(maxsize=16)
def slips_plate(n):
    img = ins.wood_top(47).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    spots = [(590, 600, 5), (740, 1130, -4), (590, 1660, 3), (740, 2160, -5)]
    for i, year in enumerate((2022, 2023, 2024, 2025)):
        if i >= n:
            break
        x, y, a = spots[i]
        _place(obj, slip(year), x, y, a)
    _place(obj, pencil(300, 0.0, 1.0), 1200, 1400, 75)
    ins.shadowed(img, obj, blur=24, off=(16, 26), alpha=160)
    return img


@functools.lru_cache(maxsize=64)
def pencil_plate(sharp_q=0, shave_q=0, sharpener=False, insert_q=0, compare=False):
    """Pencil close-up. insert_q 0..20 pushes the tip into the sharpener; shave_q 0..20 grows shavings."""
    img = ins.wood_top(53).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    cx, cy, ang = 820, 1360, 28
    a = math.radians(ang)
    if compare:   # a brand new pencil for scale
        _place(obj, pencil(1180, 1.0, 1.1), 720, 900, ang)
    p = pencil(300, sharp_q / 20, 2.2)
    half = p.size[0] / 2 - 10
    push = insert_q / 20 * 120
    pcx = cx - push * math.cos(a); pcy = cy + push * math.sin(a)
    _place(obj, p, pcx, pcy, ang)
    tx = cx - 120 * math.cos(a) - half * math.cos(a) + 60 * math.cos(a)
    ty = cy + 120 * math.sin(a) + half * math.sin(a) - 60 * math.sin(a)
    if shave_q:
        rng = np.random.default_rng(9)
        d = ImageDraw.Draw(obj)
        for k in range(int(shave_q / 20 * 9)):
            sx, sy = tx - 40 + rng.uniform(-120, 120), ty + 170 + rng.uniform(-30, 160)
            r = rng.uniform(40, 80)
            d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(222, 190, 146, 255))
            d.ellipse([sx - r * 0.55, sy - r * 0.55, sx + r * 0.55, sy + r * 0.55], fill=(238, 214, 176, 255))
            for a0 in range(0, 360, 40):
                d.arc([sx - r, sy - r, sx + r, sy + r], a0, a0 + 20, fill=YEL, width=8)
    if sharpener:
        sh = Image.new("RGBA", (230, 300), (0, 0, 0, 0))
        sd = ImageDraw.Draw(sh)
        sd.rounded_rectangle([20, 0, 230, 300], radius=26, fill=(150, 154, 162, 255))
        sd.rounded_rectangle([30, 12, 120, 288], radius=20, fill=(184, 188, 196, 255))
        sd.rectangle([0, 60, 40, 250], fill=(120, 124, 132, 255))
        sd.ellipse([180, 96, 230, 204], fill=(70, 72, 80, 255))
        _place(obj, sh, tx, ty, ang)
    ins.shadowed(img, obj, blur=20, off=(14, 22), alpha=160)
    return img


if __name__ == "__main__":
    ims = [envelope_plate(20, 20), slips_plate(4), pencil_plate(0, 0, False, 0, True), pencil_plate(0, 12, True, 20), pencil_plate(20, 20, True, 0)]
    sheet = Image.new("RGB", (300 * len(ims), 533))
    for i, im_ in enumerate(ims):
        sheet.paste(im_.convert("RGB").resize((300, 533)), (i * 300, 0))
    sheet.save(sys.argv[1])
