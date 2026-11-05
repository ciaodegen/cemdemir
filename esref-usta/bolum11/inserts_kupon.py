"""Bölüm 11 (Bir Kupon Daha) detay çekimleri: kaybedilenlerin yazdığı kuponlar, KAYBETTİ damgaları, boş son kupon, arkasına 115."""
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
RED = (178, 30, 34)
COUPONS = [("KIZININ DOĞUM", "GÜNÜ HEDİYESİ", "1.500 TL"),
           ("ANNENİN İLAÇ", "PARASI", "2.300 TL"),
           ("EŞİNİN", "BİLEZİĞİ", "18.000 TL"),
           ("EŞİNİN", "GÜVENİ", "—")]
SPOTS = [(700, 420, -4), (840, 960, 3), (690, 1500, -2), (850, 2040, 4)]


def _stamp(text, w=430, h=130, seed=1):
    st = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([5, 5, w - 5, h - 5], radius=14, outline=RED + (230,), width=8)
    f = font(FONT_SERIF_B, 64)
    sd.text(((w - sd.textlength(text, font=f)) / 2, (h - 70) / 2), text, font=f, fill=RED + (235,))
    a = np.array(st); rng = np.random.default_rng(seed)
    a[..., 3] = (a[..., 3] * (rng.random(a.shape[:2]) > 0.2)).astype(np.uint8)
    return Image.fromarray(a)


def coupon(i, nchars, stamp_k):
    w, h = 820, 470
    p = im.paper(w, h, seed=300 + i, lined=False, tint=(248, 248, 244))
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 70], fill=(40, 44, 52, 255))
    d.text((26, 14), "BAHİS KUPONU", font=font(MONO_B, 38), fill=(240, 240, 244, 255))
    d.text((w - 220, 20), f"No: 00{i + 1}4{7 - i}", font=font(MONO, 30), fill=(200, 200, 206, 255))
    for x in range(20, w - 20, 24):
        d.line([(x, 92), (x + 12, 92)], fill=(150, 150, 156, 255), width=3)
    l1, l2, amt = COUPONS[i]
    f = font(MONO_B, 52)
    d.text((30, 112), "MAÇ:", font=font(MONO, 34), fill=(90, 90, 96, 255))
    n = nchars
    for k, line in enumerate((l1, l2)):
        if n <= 0:
            break
        d.text((30, 160 + k * 66), line[:n], font=f, fill=(24, 24, 28, 255))
        n -= len(line)
    if nchars >= len(l1) + len(l2):
        d.text((30, 318), "TUTAR:", font=font(MONO, 34), fill=(90, 90, 96, 255))
        d.text((180, 312), amt, font=font(MONO_B, 44), fill=(24, 24, 28, 255))
    for x in range(20, w - 20, 24):
        d.line([(x, 392), (x + 12, 392)], fill=(150, 150, 156, 255), width=3)
    if stamp_k > 0:
        st = _stamp("KAYBETTİ", seed=i).rotate(-9, expand=True, resample=Image.BICUBIC)
        s = 1.35 - 0.35 * min(1.0, stamp_k)
        st = st.resize((int(st.size[0] * s), int(st.size[1] * s)), Image.LANCZOS)
        if stamp_k < 1:
            st.putalpha(st.split()[3].point(lambda v: int(v * stamp_k)))
        p.alpha_composite(st, (w - st.size[0] - 14, 100))
    return p


@functools.lru_cache(maxsize=128)
def coupons_plate(n, chars=(0, 0, 0, 0), stamps=(0, 0, 0, 0)):
    img = ins.wood_top(131).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    for i in range(min(n, len(COUPONS))):
        c = coupon(i, chars[i], stamps[i] / 10).rotate(SPOTS[i][2], expand=True, resample=Image.BICUBIC)
        x, y, _ = SPOTS[i]
        obj.alpha_composite(c, (int(x - c.size[0] / 2), int(y - c.size[1] / 2)))
    ins.shadowed(img, obj, blur=24, off=(16, 26), alpha=160)
    return img


def last_front(reveal):
    """The blank last coupon: 'MAÇ: KENDİN  ·  SONUÇ: ?' (reveal 0..2 lines)."""
    w, h = 1060, 600
    p = im.paper(w, h, seed=399, lined=False, tint=(248, 248, 244))
    d = ImageDraw.Draw(p)
    d.rectangle([0, 0, w, 90], fill=(40, 44, 52, 255))
    d.text((34, 20), "BAHİS KUPONU", font=font(MONO_B, 48), fill=(240, 240, 244, 255))
    d.text((40, 140), "MAÇ:", font=font(MONO, 44), fill=(90, 90, 96, 255))
    if reveal >= 1:
        d.text((40, 200), "KENDİN", font=font(MONO_B, 96), fill=(24, 24, 28, 255))
    d.text((40, 360), "SONUÇ:", font=font(MONO, 44), fill=(90, 90, 96, 255))
    if reveal >= 2:
        d.text((240, 340), "?", font=font(MONO_B, 110), fill=RED + (255,))
    return p


def last_back(nchars, pen):
    w, h = 1060, 600
    p = im.paper(w, h, seed=398, lined=False, tint=(246, 245, 238))
    d = ImageDraw.Draw(p)
    text = "115"
    sub = "Yeşilay · ücretsiz ve gizli"
    f = font(FONT_HAND, 300)
    shown = text[:min(nchars, 3)]
    tw = d.textlength(text, font=f)
    x0 = (w - tw) / 2
    d.text((x0, 40), shown, font=f, fill=(34, 52, 140, 255))
    if nchars > 3:
        fs = font(FONT_HAND, 64)
        sw = d.textlength(sub, font=fs)
        d.text(((w - sw) / 2, 430), sub[:nchars - 3], font=fs, fill=(34, 52, 140, 255))
    if pen and nchars < 3 + len(sub):
        tip = (x0 + d.textlength(shown, font=f), 290) if nchars <= 3 else ((w - d.textlength(sub, font=font(FONT_HAND, 64))) / 2 + d.textlength(sub[:nchars - 3], font=font(FONT_HAND, 64)), 500)
        a = math.radians(58); dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
        def pt(u, v):
            return (tip[0] + dx * u + nx * v, tip[1] + dy * u + ny * v)
        d.polygon([pt(0, 0), pt(90, -14), pt(90, 14)], fill=(200, 170, 90, 255))
        d.polygon([pt(88, -16), pt(560, -18), pt(560, 18), pt(88, 16)], fill=(30, 30, 34, 255))
    return p


@functools.lru_cache(maxsize=96)
def last_plate(side="front", reveal=2, flip_q=20, nchars=0, pen=False):
    """side front/back; flip_q 0..20 squashes the coupon over (0..10 front, 10..20 back)."""
    img = ins.wood_top(133).copy()
    obj = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    k = flip_q / 20
    if side == "flip":
        c = last_front(2) if k < 0.5 else last_back(0, False)
        sx = max(0.02, abs(1 - 2 * k))
    else:
        c = last_front(reveal) if side == "front" else last_back(nchars, pen)
        sx = 1.0
    c = c.rotate(-2, expand=True, resample=Image.BICUBIC)
    c = c.resize((max(2, int(c.size[0] * sx)), c.size[1]), Image.LANCZOS)
    obj.alpha_composite(c, (int((BW - c.size[0]) / 2), 960))
    ins.shadowed(img, obj, blur=26, off=(16, 28), alpha=160)
    return img


if __name__ == "__main__":
    full = tuple(len(a) + len(b) for a, b, _ in COUPONS)
    ims = [coupons_plate(2, (full[0], 6, 0, 0), (10, 0, 0, 0)), coupons_plate(4, full, (10, 10, 10, 10)),
           last_plate("front", 2), last_plate("flip", 2, 12), last_plate("back", 2, 20, 12, True)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for i, x in enumerate(ims):
        sheet.paste(x.convert("RGB").resize((270, 480)), (i * 270, 0))
    sheet.save(sys.argv[1])
