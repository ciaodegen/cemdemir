"""Dükkânın duvar saati yakın planı: ileri koşan akrep/yelkovan, yıl penceresi."""
import sys, math, functools
sys.path.insert(0, "/home/user/cemdemir/esref-usta/bolum1")
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from engine import font, FONT_SERIF_B
import inserts as ins

BW, BH = 1440, 2560
CX, CY, R = 720, 1180, 560


@functools.lru_cache(None)
def _base():
    img = ins.wood_top(41).copy()
    img = Image.eval(img.convert("RGB"), lambda v: int(v * 0.55)).convert("RGBA")
    d = ImageDraw.Draw(img)
    # shadow
    sh = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([CX - R + 30, CY - R + 50, CX + R + 30, CY + R + 50], fill=(0, 0, 0, 170))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(40)))
    d = ImageDraw.Draw(img)
    d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=(96, 60, 34, 255))
    d.ellipse([CX - R + 14, CY - R + 10, CX + R - 30, CY + R - 34], fill=(122, 80, 46, 255))
    rf = R - 70
    # face with soft radial shading
    y, x = np.mgrid[0:BH, 0:BW].astype(np.float32)
    rr = np.sqrt((x - CX) ** 2 + (y - CY) ** 2) / rf
    face = np.stack([240 - 30 * rr ** 2, 232 - 32 * rr ** 2, 210 - 34 * rr ** 2], -1)
    m = Image.new("L", (BW, BH), 0); ImageDraw.Draw(m).ellipse([CX - rf, CY - rf, CX + rf, CY + rf], fill=255)
    fimg = Image.fromarray(np.clip(face, 0, 255).astype(np.uint8)).convert("RGBA"); fimg.putalpha(m)
    img.alpha_composite(fimg)
    d = ImageDraw.Draw(img)
    for i in range(60):
        a = math.radians(i * 6)
        r0 = rf - (52 if i % 5 == 0 else 26)
        w = 14 if i % 5 == 0 else 5
        d.line([(CX + r0 * math.sin(a), CY - r0 * math.cos(a)), (CX + (rf - 14) * math.sin(a), CY - (rf - 14) * math.cos(a))], fill=(50, 36, 26, 255), width=w)
    f = font(FONT_SERIF_B, 64)
    for n in range(1, 13):
        a = math.radians(n * 30); r0 = rf - 110
        t = str(n); tw = d.textlength(t, font=f)
        d.text((CX + r0 * math.sin(a) - tw / 2, CY - r0 * math.cos(a) - 38), t, font=f, fill=(50, 36, 26, 255))
    d.text((CX - d.textlength("EŞREF USTA", font=font(FONT_SERIF_B, 34)) / 2, CY - 230), "EŞREF USTA", font=font(FONT_SERIF_B, 34), fill=(110, 80, 50, 255))
    return img


def _hand(d, ang, length, width, col, tail=40):
    a = math.radians(ang)
    sx, sy = math.sin(a), -math.cos(a)
    d.line([(CX - tail * sx, CY - tail * sy), (CX + length * sx, CY + length * sy)], fill=col, width=width)


def clock(minute_deg, hour_deg, sec_deg, year_text, spin=0.0):
    """spin 0..1 adds motion trails to the hands."""
    img = _base().copy()
    # year window
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([CX - 120, CY + 150, CX + 120, CY + 240], radius=10, fill=(40, 30, 24, 255))
    f = font(FONT_SERIF_B, 58)
    tw = d.textlength(year_text, font=f)
    d.text((CX - tw / 2, CY + 160), year_text, font=f, fill=(246, 214, 120, 255))
    hands = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    if spin > 0:
        trail = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
        td = ImageDraw.Draw(trail)
        for k in range(1, 10):
            _hand(td, minute_deg - k * 9 * spin, R - 140, 16, (40, 30, 24, int(110 * (1 - k / 10))))
        hands.alpha_composite(trail.filter(ImageFilter.GaussianBlur(6)))
    hd = ImageDraw.Draw(hands)
    _hand(hd, hour_deg, R - 300, 28, (36, 26, 20, 255))
    _hand(hd, minute_deg, R - 140, 18, (36, 26, 20, 255))
    _hand(hd, sec_deg, R - 120, 6, (180, 30, 30, 255), tail=70)
    hd.ellipse([CX - 30, CY - 30, CX + 30, CY + 30], fill=(36, 26, 20, 255))
    hd.ellipse([CX - 12, CY - 12, CX + 12, CY + 12], fill=(180, 30, 30, 255))
    sh = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    sh.alpha_composite(hands)
    sh = Image.eval(sh, lambda v: v)
    a = sh.split()[3].point(lambda v: v * 90 // 255)
    shadow = Image.new("RGBA", (BW, BH), (0, 0, 0, 255)); shadow.putalpha(a)
    img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)), (10, 16))
    img.alpha_composite(hands)
    # glass glare
    g = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([CX - 380, CY - 420, CX - 40, CY - 220], fill=(255, 255, 255, 40))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(30)))
    return img


if __name__ == "__main__":
    ims = [clock(60, 10 * 30 + 5, 120, "2026"), clock(200, 130, 300, "2041", 1.0), clock(66, 10 * 30 + 5.5, 0, "BUGÜN")]
    sheet = Image.new("RGB", (360 * len(ims), 640))
    for i, im in enumerate(ims):
        sheet.paste(im.convert("RGB").resize((360, 640)), (i * 360, 0))
    sheet.save(sys.argv[1])
